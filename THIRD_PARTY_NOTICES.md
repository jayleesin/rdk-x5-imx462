# Third-party notices

## Included GPL-derived sensor material

The register sequences are adapted from the Raspberry Pi Linux IMX290/462 driver:

- [Pinned source](https://github.com/raspberrypi/linux/blob/359f37f0faefb712add32a39f98751aea67d5c1f/drivers/media/i2c/imx290.c)
- Original notice: Copyright (C) 2019 FRAMOS GmbH.
- Original notice: Copyright (C) 2019 Linaro Ltd.
- Original author: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>
- Original SPDX identifier: `GPL-2.0`, meaning version 2 only in the Linux licensing convention; this project uses the explicit identifier `GPL-2.0-only`.

Adaptation: 2026-10-19, single-mode RDK X5 IMX462 evaluation integration. Publication notices were updated on 2026-10-21 without changing sensor logic or register values. This is a modified integration, not an upstream-endorsed driver. The CM4 kernel module is not distributed.

GPL-2.0-only applies to the included sensor integration, register tables, ABI helper, project-authored scripts, settings, and documentation. The full license is supplied in `LICENSE`; the upstream Linux license identification text is also retained under `LICENSES/`.

## External materials not distributed

The D-Robotics SDK headers, `libcam`, ISP runtime, tuning databases, multimedia examples, and locally generated artifacts are not part of this public release. Their authors retain their rights. This repository's GPL notice grants no rights over those materials.

Several official packaging repositories carry Apache-2.0. Separate repositories containing the exact libcam headers, tuning data, and multimedia example examined in this review do not state an applicable license. SDK headers also contain a Horizon Robotics rights-reservation notice. These observations are recorded with pinned references in `docs/LICENSE_REVIEW.md` and `validation/license-review.json`.

No project affiliation, endorsement, or trademark license is implied by the names RDK, D-Robotics, Horizon Robotics, Raspberry Pi, or Sony IMX462.
