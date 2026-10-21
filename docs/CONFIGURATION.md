# Tested mode and integration settings

```text
IMX462 → MIPI RX0 → VIN RAW12 → ISP in DDR mode → NV12 → application/encoder
           libcam + sensor plugin       cam-service + local tuning profile
```

| Item | Tested setting |
|---|---|
| Mode | 1920 × 1080, 20 fps, linear, HDR disabled |
| Sensor interface | I²C bus 6, 7-bit address 0x1a |
| Pixel format | RAW12, CSI datatype 0x2c, Bayer RGGB |
| MIPI | RX0, VC0, IPI1, two lanes |
| Receiver fields | mipiclk 1782, settle 30, stop_check_instart 1 |
| Timing | HMAX 2200, VMAX 3375, AE lines_per_second 67500 |
| Clock | Nominal module clock 37.125 MHz; host mclk 0, vin_attr_ex_mask 0 |
| VIN memory | DDR enabled, RAW12 in 16-bit storage, stride 3840 bytes |
| ISP | DDR_MODE, crop (0, 0, 1920, 1080), RAW12 input, 8-bit NV12 output |
| AE | User-space gain/exposure callbacks; exposure 1…3373 lines |
| Gain | LUT indices 0…156, maximum register code 98; no digital gain |
| GPIO / IR-cut | No power/reset switching or IR-cut control |

`mipiclk=1782` is a tested SDK configuration value, not an electrical measurement. The module clock was not measured electrically. Gain-table indices are not dB values.

The observed read at register 0x319a was 0xd007. It has not been established as a unique IMX462 identification value.

The plugin accepts the stated RAW12/1080p/20fps/linear/address/GPIO conditions. The application supplies the I²C bus and sensor port. Other connectors require their board mapping to be checked independently.

The locally generated configuration exports `imx462_linear_1920x1080_raw12_20fps_2lane`. The application must compile/select it and connect the VIN/ISP nodes. Its sensor name is `imx462` and its profile path is `/usr/hobot/lib/sensor/imx462_tuning.json`.

`config/imx462-mode.json` is a factual reference for these settings; it is not directly loaded by the vendor runtime. The existing SDK provides the kernel drivers, `libcam`, and `cam-service`. This project does not replace them or include their binaries.

## Image-quality limitations

The tested local tuning profile retains the baseline IMX219 `sensor`, `system`, and `tuning` sections unchanged. Only header metadata was changed. It must not be described as an IMX462-calibrated profile.

Lens, lighting, IR filtering, exposure, AWB, CCM, and noise calibration require separate testing. The purple tint investigation and bright-/low-light color validation are deferred. Direct viewing of a fluorescent lamp is a hypothesis, not an established cause.
