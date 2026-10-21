# Publishing this edition

Publish only the verified source-and-recipes edition. The previous mixed snapshot and its archive were preserved outside the public output directory. They are not part of this release. The current local Git repository is fresh, so its object database does not carry the removed vendor payloads from the earlier staging index.

Before committing or uploading:

```sh
python3 scripts/verify_public_release.py
git status --short
git diff --cached --stat
```

The verifier checks the release manifest and, when a Git index exists, checks the indexed bytes and file list. It also rejects binary/vendor payload paths and scans all Git blobs, including unreachable ones, for excluded binary signatures and known excluded content hashes. Do not disable these checks to add vendor material. `.gitignore` is a convenience, not a license or sufficient protection on its own.

The public repository is [jayleesin/rdk-x5-imx462](https://github.com/jayleesin/rdk-x5-imx462), with `main` as its default branch. Publish only the reviewed source files, retaining the GPL license and attribution notices. The matching ZIP contains the same public files and omits `.git/`, build products, dependencies, and private archives.

## Files deliberately excluded

- Prebuilt or locally rebuilt sensor `.so`, object files, and libraries
- Complete IMX219/IMX462 ISP tuning JSON and derived profiles
- Complete vendor/derived VIN/ISP C templates and SDK headers
- Vendor runtime and ISP binaries, kernel modules, proprietary tools
- Credentials, LAN addresses, captures, and private operational logs

`build/`, `deps/`, and generated artifacts may exist on your development machine, but must not enter a public export. The source release does not grant rights over those contents.

## Adding binaries or vendor-derived files later

First obtain terms that apply to the exact vendor inputs and address the linked plugin's GPL/SDK compatibility. Preserve any required notices and corresponding-source obligations. The current public-edition assessment does not cover such an expanded release. Do not relabel GPL-2.0-only code as GPLv3 or Apache-2.0 to bypass this review.

After changing legitimate public source or documentation, review the changes and regenerate `SHA256SUMS` for the new release. The current manifest intentionally detects edits to this reviewed snapshot.
