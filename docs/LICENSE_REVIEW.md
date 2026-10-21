# License and redistribution review

Review date: **2026-10-21**. Decision: **publish the included source-and-recipes edition; withhold the prebuilt plugin and vendor payloads**.

This is an evidence-based release-scope decision. It is not a blanket determination that every SDK component may be redistributed, or that every possible linked binary is legally prohibited. No vendor permission request was sent and no additional permission was obtained.

## Findings

| Component | Evidence | Public release treatment |
|---|---|---|
| Raspberry Pi IMX290/462 register source | Pinned file has SPDX `GPL-2.0`; upstream licensing text maps this to version 2 only | Adapted register tables retained with GPL-2.0-only and attribution |
| Project sensor integration and tools | Project-authored integration around the GPL-derived tables; vendor headers are referenced, not copied | Source retained; modification notices and full GPL text supplied |
| IMX219 ISP baseline and derived IMX462 JSON | No applicable license in the inspected `x5-tuning-json` tree; installed package copyright file has no License field | Complete JSON excluded; only a local metadata transformation recipe retained |
| VIN/ISP C example and derived IMX462 configuration | No applicable license for `vp_sensors` in `x5-multimedia-samples`; unrelated subdirectories have their own licenses | Complete C template excluded; numeric/name transformation recipe retained |
| libcam SDK headers | No repository-wide license in `x5-libcam-inc`; headers reserve Horizon Robotics' rights and include inline functions | Headers excluded; supplied separately for local use |
| Prebuilt `libimx462.so` | Linked against `libcam.so.1` and compiled with SDK inline helpers/macros; source uses GPL-2.0-only | Binary excluded pending resolution of SDK rights and linked-work compatibility |
| Runtime/packaging repositories | Apache-2.0 found in the official repositories below | Recorded as positive evidence, but not extended automatically to separately sourced material |

The previous package's statement that no vendor licenses were found was incomplete. **Apache-2.0 licenses do exist in the packaging/runtime repositories.** The revised assessment distinguishes them from the separate source repositories and the files actually used.

## Pinned vendor evidence

Packaging/runtime licenses:

- [x5-hobot-camera LICENSE](https://github.com/D-Robotics/x5-hobot-camera/blob/c223d45a40deff1c6f9547a38882b0a13cd4f80c/LICENSE)
- [x5-hobot-multimedia LICENSE](https://github.com/D-Robotics/x5-hobot-multimedia/blob/0f297df905511c3429567202813359acee26dbb3/LICENSE)
- [x5-hobot-multimedia-dev LICENSE](https://github.com/D-Robotics/x5-hobot-multimedia-dev/blob/f625c7fd28a3553f57524c2bc3721a42078af2b7/LICENSE)
- [x5-hobot-multimedia-samples LICENSE](https://github.com/D-Robotics/x5-hobot-multimedia-samples/blob/db9ccff4d1207aafe067f2a3a771863df7b582d0/LICENSE)

The camera packaging tree does not contain the tested tuning JSON; its [gitignore](https://github.com/D-Robotics/x5-hobot-camera/blob/c223d45a40deff1c6f9547a38882b0a13cd4f80c/.gitignore) excludes the sensor payload directory. The samples packaging tree does not contain the tested `vp_sensors` C file. The development packaging tree does not contain the reviewed `camera_sensor_dev.h`. No text explicitly extending those root licenses to the separate repositories below was found.

Separately inspected source repositories and files:

- [x5-tuning-json](https://github.com/D-Robotics/x5-tuning-json/tree/96cdd39ecb485ee725d5d40601a8d3b834674b4b)
- [x5-multimedia-samples](https://github.com/D-Robotics/x5-multimedia-samples/tree/0d9925cef6c41056525ae27383d2d3604f9e4690)
- [x5-libcam-inc camera_sensor_dev.h](https://github.com/D-Robotics/x5-libcam-inc/blob/52bbff4cc77ccdff1182c710590ba17dddd6ee73/develop/camera_sensor_dev.h)

The installed `hobot-camera`, `hobot-multimedia`, and `hobot-multimedia-samples` copyright files identify D-Robotics as copyright holder but contain no License field or redistribution terms. This absence is not proof of an absolute prohibition; it means these files do not fill the permission gap. The ARM Control Tool notice found in the camera package applies to that tool, not automatically to all sensor files. Likewise, the licenses of CoreMark, a websocket component, or a video player do not license the unrelated `vp_sensors` example.

GitHub explains that making a repository public does not replace a software license. Its viewing/forking provisions should not be treated as a general permission to repackage unlicensed material in a different project. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

## Conditions for the included GPL source

The [pinned GPL version 2 text](https://raw.githubusercontent.com/raspberrypi/linux/359f37f0faefb712add32a39f98751aea67d5c1f/LICENSES/preferred/GPL-2.0) allows covered source redistribution subject to its terms. In this release:

- Copyright, attribution, license, and warranty notices are retained.
- Adaptation and notice-update dates are stated in the source.
- The complete GPL-2.0 text accompanies the covered source.
- Changes to covered source remain under GPL-2.0-only; no invented SDK linking exception or conversion to GPLv3 is applied.

Binary distribution adds corresponding-source requirements and requires compatible rights for the combined work. Supplying this project's C source alone does not settle all SDK/header or linking questions.

## Why the prebuilt plugin is withheld

The [Apache Software Foundation](https://apache.org/licenses/GPL-compatibility.html) and [GNU license list](https://www.gnu.org/licenses/license-list.en.html#apache2) describe Apache-2.0 as incompatible with GPL version 2. The plugin's existing GPL-2.0-only status cannot simply be changed to GPLv3. There is also no confirmed broad redistribution grant for the separately sourced header implementations.

This does not decide whether a specific interface use, system-library exception, or other legal theory applies. No such exception has been established for this plugin. The practical publication decision is to omit the binary, SDK contents, and vendor-derived data while making the independently distributable source and factual integration instructions available.

## What would enable a broader release

Before adding the `.so`, full tuning JSON, or vendor-derived C example, obtain authoritative terms tied to the exact files/versions. For a binary release, also resolve the applicable GPL/SDK combination, including any necessary permission or exception from the relevant rightsholders. The fact that a local build works or matches a device hash is not sufficient.

If an exact vendor work is confirmed to be Apache-2.0, its redistribution conditions include supplying the license, marking modifications, preserving relevant notices, and carrying applicable NOTICE attributions. This review does not apply Apache-2.0 to the currently unresolved files merely because a related packaging repository uses it. See [Apache-2.0, section 4](https://www.apache.org/licenses/LICENSE-2.0).

Until then, locally generated files remain excluded from this public release. This is a packaging boundary, not an additional restriction on the rights granted by the GPL over the included covered source.
