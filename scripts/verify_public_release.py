#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify this reviewed source snapshot and its local Git object database.

This is a release-integrity check, not a general secret scanner or legal review.
Ignored local build/dependency directories are never part of the public export.
"""
import hashlib
import ipaddress
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCAL_DIRS = {'.git', 'build', 'deps', 'vendor', 'private', 'backups', 'generated', '__pycache__'}
FORBIDDEN_SUFFIXES = {'.a', '.o', '.bin', '.ko', '.zip', '.tar', '.gz', '.pem', '.key', '.log'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_path(name):
    p = pathlib.PurePosixPath(name)
    require(name == p.as_posix() and not p.is_absolute() and
            all(part not in ('..', '.') for part in p.parts) and
            '\\' not in name and ':' not in name, 'Unsafe path: ' + name)
    require(not any(part in LOCAL_DIRS for part in p.parts), 'Local-only path: ' + name)
    require(p.suffix.lower() not in FORBIDDEN_SUFFIXES and
            not re.search(r'\.so(?:\.|$)', name, re.I), 'Excluded binary/archive path: ' + name)
    require(p.name not in {'.env', 'imx462_tuning.json', 'imx219_1920x1080_tuning.json',
                           'linear_1920x1080_raw12_20fps_2lane.c',
                           'linear_1920x1080_raw10_30fps_2lane.c'}, 'Excluded payload: ' + name)
    require(p.suffix.lower() != '.h' or name == 'sensor/imx462_setting.h',
            'Unreviewed header: ' + name)


def inspect_bytes(data, label, excluded):
    require(not data.startswith((b'\x7fELF', b'MZ', b'PK\x03\x04', b'\x1f\x8b')),
            'Binary/archive signature: ' + label)
    require(digest(data) not in excluded and digest(data.replace(b'\r\n', b'\n')) not in excluded,
            'Known excluded vendor/binary content: ' + label)
    text = data.decode('utf-8')
    require(not re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----', text), 'Private key: ' + label)
    for candidate in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text):
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        require(not address.is_private and not address.is_loopback, 'Private IP address: ' + label)
    require(not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})', text),
            'Possible GitHub token: ' + label)


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def verify():
    provenance = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
    excluded = {v['sha256'] for v in provenance['reference_artifacts'].values()}
    excluded.update(v for k, v in provenance['local_reproduction'].items() if k.endswith('sha256'))
    excluded.add(provenance['sensor_register_source']['cm4_module_sha256'])
    manifest = {}
    for line in (ROOT / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        require(match is not None, 'Malformed SHA256SUMS line')
        checksum, name = match.groups()
        public_path(name)
        require(name != 'SHA256SUMS' and name not in manifest, 'Duplicate/self manifest entry: ' + name)
        manifest[name] = checksum
    require(bool(manifest), 'Empty manifest')
    expected = set(manifest) | {'SHA256SUMS'}
    actual = set()
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in LOCAL_DIRS for part in relative.parts):
            continue
        require(not path.is_symlink(), 'Symlink in public tree: ' + relative.as_posix())
        if path.is_file():
            actual.add(relative.as_posix())
    require(actual == expected, 'Public file list differs from manifest: ' + repr(sorted(actual ^ expected)))
    for name in sorted(expected):
        public_path(name)
        data = (ROOT / name).read_bytes()
        inspect_bytes(data, name, excluded)
        if name in manifest:
            require(digest(data) == manifest[name], 'Hash mismatch: ' + name)

    git_blobs = 0
    has_git = (ROOT / '.git').exists()
    has_index = False
    if has_git:
        require(git('rev-parse', '--show-toplevel').decode().strip().replace('\\', '/').lower() ==
                ROOT.as_posix().lower(), 'Git root is outside release directory')
        index = git('ls-files', '--stage', '-z').split(b'\0')
        entries = {}
        for entry in filter(None, index):
            metadata, raw_name = entry.split(b'\t', 1)
            mode, oid, stage = metadata.decode().split()
            name = raw_name.decode('utf-8')
            public_path(name)
            require(mode in ('100644', '100755') and stage == '0', 'Unexpected Git index entry: ' + name)
            entries[name] = oid
        has_index = bool(entries)
        if has_index:
            require(set(entries) == expected, 'Git index file list differs from release manifest')
            for name, oid in entries.items():
                require(git('cat-file', 'blob', oid) == (ROOT / name).read_bytes(), 'Stale Git index: ' + name)
        # --batch-all-objects includes objects unreachable from a branch or index.
        objects = git('cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)')
        for line in objects.decode().splitlines():
            oid, kind = line.split()
            if kind == 'blob':
                inspect_bytes(git('cat-file', 'blob', oid), 'Git blob ' + oid, excluded)
                git_blobs += 1
    print(json.dumps({'status': 'PASS', 'public_files': len(expected), 'git_present': has_git,
                      'git_index_checked': has_index, 'git_blobs_checked': git_blobs,
                      'scope': 'Reviewed manifest/files and all local Git blobs; ignored local directories are excluded'}, indent=2))


if __name__ == '__main__':
    try:
        verify()
    except (ValueError, OSError, UnicodeError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
