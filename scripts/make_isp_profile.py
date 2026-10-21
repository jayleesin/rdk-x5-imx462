#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Apply project-authored metadata changes to a separately obtained local ISP baseline."""
import argparse
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('baseline', type=Path)
parser.add_argument('output', type=Path, help='New local output file, normally under build/')
args = parser.parse_args()
if args.output.exists():
    parser.error('Output already exists; choose a new file.')
reference = json.loads((root / 'provenance.json').read_text(encoding='utf-8'))
raw = args.baseline.read_bytes()
if hashlib.sha256(raw).hexdigest() != reference['local_reproduction']['isp_baseline_sha256']:
    parser.error('Baseline hash differs from the tested IMX219 file.')
profile = json.loads(raw)
header = profile['header']
header.update({
    'creation_date': '19-Oct-2026',
    'creator': 'CM4 to X5 feasibility investigation; not calibrated',
    'sensor_name': 'imx462',
    'sample_name': 'UNVALIDATED_X5_IMX219_BASELINE_FOR_IMX462',
})
header['resolution'][0]['framerate'] = [{'name': 'FPS_20', 'fps': 20.0}]
# Preserve the deployed snapshot's CRLF representation independently of host OS.
data = (json.dumps(profile, indent=2) + '\n').replace('\n', '\r\n').encode('utf-8')
if hashlib.sha256(data).hexdigest() != reference['reference_artifacts']['isp_profile']['sha256']:
    parser.error('Generated profile does not match the tested device snapshot.')
with args.output.open('xb') as f:
    f.write(data)
print('Reproduced the uncalibrated device profile locally. Vendor data rights remain separate; do not publish the output.')
