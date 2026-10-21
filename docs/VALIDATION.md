# Technical validation and limits

## Public edition preparation

The sensor's publication changes add attribution/modification notices and normalize line endings. Logic and register values remain unchanged. A native X5 build is checked against the reference private plugin hash; generated binary and vendor-derived configuration files are kept outside this public release.

Both local reproduction tools validate their inputs and check generated SHA-256 values against the tested device snapshots. They refuse an unexpected baseline or an existing output. See `validation/public-preparation.json` for the checks performed on this edition.

No live camera configuration was installed or changed, and no production service was restarted. The manual installation/rollback instructions were not executed during this preparation.

## Prior full-system 12-hour test

The following is a summary of a single continuous test on 2026-10-20 UTC using the sensor implementation and the private full RTSP configuration. The encoder, server, custom SEI instrumentation, and LAN receiver are not included in this source release.

| Measurement | Result |
|---|---|
| Decoded frames | 864,021 |
| Sensor-time observation | 43,201.084034808 seconds |
| PC observation | 43,201.15604710003 seconds |
| Geometry / measured rate | 1920 × 1080 / 19.99996109597 fps |
| Raw RTP packets | 23,793,235 |
| Detected sensor/frame/packet loss | 0 |
| Initial excluded frames | 0, starting at the first complete IDR |
| Decoder PTS intervals | Matched original RTP timestamp intervals throughout |
| RTP timestamp wraps | 1, accounted for in continuity checks |
| Service restarts / health recoveries | 0 |
| Device telemetry samples | 1,442; maximum interval 30.113 seconds |
| CPU temperature | 72.895–77.926 °C |
| DDR temperature | 73.969–78.171 °C |

No sustained service-memory-leak signature was observed during the finite 12-hour window. Small process-memory increases and changes in overall system available memory were assessed separately. This is not proof that every possible leak is absent.

Scope: one LAN PC, RTSP/TCP, the tested full server configuration, and FFmpeg `2026-04-09-git-d3d0b7a5ee-full_build-www.gyan.dev`. This does not establish compatibility with all clients, multiple tracks, different SDKs, or physical power cycling. It does not claim decoding of reference-less P frames preceding the first complete IDR. The cancelled 24-hour request was not counted.

Only aggregate results are distributed. Original captures, private device identifiers, and detailed operational logs are excluded.

## Unvalidated items

- IMX462-specific color/lens/IR/AWB/CCM/noise calibration
- Bright-light and low-light color accuracy; the purple tint's cause and correction
- Other modules, wiring, reference clocks, board variants, and SDK versions
- HDR, other modes/frame rates, digital gain, GPIO power/reset, and IR-cut control

The stream-stability result is not an image-quality or general compatibility result. Build reproducibility is not a legal clearance of the generated binary.
