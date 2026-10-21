#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# Local build only. Generated objects are excluded from the public release.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
INC=${INC:-"$ROOT/deps/x5-libcam-inc"}
OUT=${OUT:-"$ROOT/build"}
CC=${CC:-gcc}
case "$(uname -m)" in aarch64) ;; *) echo 'Run natively on the tested RDK X5 / aarch64 environment.' >&2; exit 1 ;; esac
test -f "$INC/legacy/utility/hb_cam_utility.h" || { echo 'Provide your separately obtained SDK headers through INC; see docs/BUILD.md.' >&2; exit 1; }
INC=$(CDPATH= cd -- "$INC" && pwd)
mkdir -p "$OUT"
OUT=$(CDPATH= cd -- "$OUT" && pwd)
cd "$ROOT/sensor"
set -- -DCAMERA_FRAMEWORK_HBN "-I$INC" "-I$INC/legacy" "-I$INC/legacy/inc" "-I$INC/legacy/utility" "-I$INC/legacy/utility/sensor" "-I$INC/develop" "-I$INC/private"
"$CC" -std=gnu11 -Wall -Wextra -Wno-old-style-declaration -O2 -fPIC "$@" \
  -shared imx462_utility.c -o "$OUT/libimx462.so" -L/usr/hobot/lib -lcam \
  -Wl,-z,defs -Wl,-soname,libimx462.so
"$CC" -std=gnu11 -Wall -Wextra -Wno-old-style-declaration "$@" abi_probe.c -o "$OUT/abi_probe" -ldl
"$OUT/abi_probe" "$OUT/libimx462.so" imx462
sha256sum "$OUT/libimx462.so"
echo 'Local build complete. The generated binary is not cleared for public redistribution by this release.'
