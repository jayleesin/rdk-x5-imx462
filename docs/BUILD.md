# Local build and reproduction

Use the tested AArch64 X5 environment listed in the README. Obtain the SDK through the vendor's authorized channels and use it subject to the applicable terms. This repository does not download, include, or grant rights over SDK headers, libraries, or tuning data.

The reference header revision is [x5-libcam-inc commit 52bbff4](https://github.com/D-Robotics/x5-libcam-inc/tree/52bbff4cc77ccdff1182c710590ba17dddd6ee73). This link identifies the version; public availability is not a redistribution license.

```sh
python3 scripts/verify_public_release.py
INC=/absolute/path/to/x5-libcam-inc sh scripts/build.sh
```

The script compiles the sensor plugin and ABI helper into `build/`. It performs no installation or service control. The ABI helper uses `dlopen`/`dlsym` to check module metadata; it does not call sensor initialization or streaming callbacks. An ABI-size match alone does not prove hardware or image-quality compatibility.

Reference ABI output:

```text
imx462 module=304/304 info=384/384 data=0 version=00010000 flags=00000021
```

The tested private plugin's SHA-256 is:

```text
38e3e8ffcfc0ac376e5e30b6223fddaac29047eada49a963b7edfb5dfaad372d
```

This digest identifies a technical reference; no binary accompanies this public edition. Different compilers or SDK versions can produce different outputs. The source's publication-notice changes do not change sensor behavior.

## Reproduce local settings

The tools require the exact tested baseline, allowing LF/CRLF normalization only for the SDK C example. Existing outputs are never overwritten.

```sh
mkdir -p build
python3 scripts/make_isp_profile.py \
  /usr/hobot/lib/sensor/imx219_1920x1080_tuning.json \
  build/imx462_tuning.json
python3 scripts/make_pipeline_config.py \
  /app/multimedia_samples/vp_sensors/imx219/linear_1920x1080_raw10_30fps_2lane.c \
  build/linear_1920x1080_raw12_20fps_2lane.c
gcc -std=gnu11 -Wall -Wextra -Werror \
  -I/app/multimedia_samples/vp_sensors \
  -c build/linear_1920x1080_raw12_20fps_2lane.c \
  -o build/imx462_pipeline_config.o
```

The ISP tool changes project-authored header metadata only. The C configuration tool changes sensor names and mode parameters in a user-supplied example. Neither tool supplies calibration coefficients or a vendor template. Generated files remain subject to the input materials' terms and are excluded from public exports.

The pipeline object must be linked into an application that selects this configuration and creates the sensor on the appropriate bus/port. It is not a standalone capture or RTSP program.
