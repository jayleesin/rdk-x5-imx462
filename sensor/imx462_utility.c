// SPDX-License-Identifier: GPL-2.0-only
// Adapted 2026-10-19; publication notice updated 2026-10-21 (no logic change).
// Single-mode evaluation port of the Raspberry Pi IMX290/462 register sequence.
// Requires a powered module with a 37.125MHz input clock. No GPIO/IR-CUT changes.
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "hb_i2c.h"
#include "hb_cam_utility.h"
#include "hb_camera_data_config.h"
#include "imx462_setting.h"

#define COUNT(a) (sizeof(a) / sizeof((a)[0]))
#define IMX462_VMAX 3375U
#define TRY(x) do { int r_ = (x); if (r_ < 0) return r_; } while (0)
static unsigned gain_calls, exposure_calls, last_gain, last_line;

static int wr(int bus, int addr, uint16_t reg, unsigned width, uint32_t val)
{
    for (unsigned i = 0; i < width; ++i) {
        int r = hb_vin_i2c_write_reg16_data8(bus, addr, reg + i, (val >> (8*i)) & 255);
        if (r < 0) { fprintf(stderr, "imx462 write %04x failed: %d\n", reg+i, r); return r; }
    }
    return 0;
}
static int table(sensor_info_t *s, const struct imx462_reg *a, size_t n)
{
    for (size_t i = 0; i < n; ++i) TRY(wr(s->bus_num, s->sensor_addr, a[i].addr, a[i].width, a[i].value));
    usleep(10000);
    return 0;
}
static int sensor_stop(sensor_info_t *s)
{
    int r = wr(s->bus_num, s->sensor_addr, 0x3000, 1, 1);
    usleep(30000);
    int r2 = wr(s->bus_num, s->sensor_addr, 0x3002, 1, 1);
    return r < 0 ? r : r2;
}
static int sensor_start(sensor_info_t *s)
{
    TRY(wr(s->bus_num, s->sensor_addr, 0x3000, 1, 0));
    usleep(30000);
    int r = wr(s->bus_num, s->sensor_addr, 0x3002, 1, 0);
    if (r < 0) sensor_stop(s);
    return r;
}
static int tuning(sensor_info_t *s)
{
    sensor_turning_data_t t = {0};
    t.bus_num = s->bus_num; t.bus_type = s->bus_type; t.port = s->port;
    t.reg_width = s->reg_width; t.mode = s->sensor_mode; t.sensor_addr = s->sensor_addr;
    snprintf(t.sensor_name, sizeof(t.sensor_name), "%s", s->sensor_name);
    t.sensor_data.active_width = 1920; t.sensor_data.active_height = 1080;
    t.sensor_data.turning_type = 1; t.sensor_data.conversion = 1;
    t.sensor_data.VMAX = IMX462_VMAX; t.sensor_data.HMAX = 2200;
    t.sensor_data.lines_per_second = IMX462_VMAX * 20;
    t.sensor_data.analog_gain_max = 156; t.sensor_data.analog_gain_init = 32;
    t.sensor_data.digital_gain_max = 0;
    t.sensor_data.exposure_time_min = 1; t.sensor_data.exposure_time_max = IMX462_VMAX-2;
    t.sensor_data.exposure_time_long_max = IMX462_VMAX-2; t.sensor_data.exposure_time_init = 2024;
    sensor_data_bayer_fill(&t.sensor_data, 12, BAYER_START_R, BAYER_PATTERN_RGGB);
    sensor_data_bits_fill(&t.sensor_data, 12);
    // Streaming uses the callbacks, which preserve the required 30ms delay.
    // Kernel-only stress-test stream control is outside this prototype's scope.
    t.stream_ctrl.data_length = 1;
    uint32_t lut[256]; memcpy(lut, imx462_gain_lut, sizeof(lut));
    t.normal.again_lut = lut;
    int r = ioctl(s->sen_devfd, SENSOR_TURNING_PARAM, &t);
    if (r < 0) { int e=errno; perror("imx462 SENSOR_TURNING_PARAM"); return -e; }
    return 0;
}
static int configure(sensor_info_t *s)
{
    static const struct imx462_reg clock_lanes_csi[] = {
        {0x305c,1,0x18},{0x305d,1,3},{0x305e,1,0x20},{0x305f,1,1},
        {0x315e,1,0x1a},{0x3164,1,0x1a},
        {0x3407,1,1},{0x3443,1,1},{0x3009,1,1},
        {0x3405,1,0},{0x3446,2,119},{0x3448,2,103},{0x344a,2,71},
        {0x344c,2,55},{0x344e,2,63},{0x3450,2,255},{0x3452,2,63},{0x3454,2,55},
    };
    static const struct imx462_reg controls[] = {
        {0x300a,2,240},{0x301c,2,2200},{0x3018,3,IMX462_VMAX},
        {0x3020,3,IMX462_VMAX-2024-1},{0x3014,1,20},{0x3007,1,0},{0x308c,1,0},
    };
    TRY(sensor_stop(s));
    TRY(wr(s->bus_num,s->sensor_addr,0x3001,1,0));
    TRY(table(s,imx290_global_init_settings,COUNT(imx290_global_init_settings)));
    TRY(table(s,imx290_global_init_settings_462,COUNT(imx290_global_init_settings_462)));
    TRY(table(s,xclk_regs,COUNT(xclk_regs)));
    TRY(table(s,clock_lanes_csi,COUNT(clock_lanes_csi)));
    TRY(table(s,imx290_12bit_settings,COUNT(imx290_12bit_settings)));
    TRY(table(s,imx290_1080p_settings,COUNT(imx290_1080p_settings)));
    TRY(table(s,controls,COUNT(controls)));
    return tuning(s);
}
static int sensor_init(sensor_info_t *s)
{
    gain_calls=exposure_calls=last_gain=last_line=0;
    if (!s || s->sensor_mode != NORMAL_M || s->width != 1920 || s->height != 1080 ||
        s->fps != 20 || s->format != 0x2c || s->sensor_addr != 0x1a || s->gpio_num > 0) {
        fprintf(stderr,"imx462 requires 1920x1080 RAW12 20fps linear, address 0x1a, GPIO disabled\n");
        return -EINVAL;
    }
    fprintf(stderr,"imx462 evaluation init: bus=%d port=%d fd=%d\n",s->bus_num,s->port,s->sen_devfd);
    int r = configure(s);
    if (r < 0) sensor_stop(s);
    return r;
}
static int gain(hal_control_info_t *i, uint32_t mode, uint32_t *a, uint32_t *d, uint32_t n)
{
    (void)d;
    if (!i || !a || n != 1 || mode != NORMAL_M) return -EINVAL;
    unsigned idx = a[0] > 156 ? 156 : a[0];
    gain_calls++; last_gain=imx462_gain_lut[idx];
    return wr(i->bus_num,i->sensor_addr,0x3014,1,imx462_gain_lut[idx]);
}
static int exposure(hal_control_info_t *i, uint32_t mode, uint32_t *line, uint32_t n)
{
    if (!i || !line || n != 1 || mode != NORMAL_M) return -EINVAL;
    uint32_t l = line[0] < 1 ? 1 : line[0] > IMX462_VMAX-2 ? IMX462_VMAX-2 : line[0];
    exposure_calls++; last_line=l;
    TRY(wr(i->bus_num,i->sensor_addr,0x3001,1,1));
    int r = wr(i->bus_num,i->sensor_addr,0x3020,3,IMX462_VMAX-l-1);
    int end = wr(i->bus_num,i->sensor_addr,0x3001,1,0);
    return r < 0 ? r : end;
}
static int userspace(uint32_t port, uint32_t *enable)
{
    (void)port; if (!enable) return -EINVAL;
    *enable = HAL_GAIN_CONTROL | HAL_LINE_CONTROL; return 0;
}
static int sensor_deinit(sensor_info_t *s)
{
    fprintf(stderr,"imx462 AE callbacks: gain=%u exposure=%u last_gain_code=%u last_lines=%u\n",
      gain_calls,exposure_calls,last_gain,last_line);
    return sensor_stop(s);
}
SENSOR_MODULE_F(imx462, CAM_MODULE_FLAG_A16D8);
sensor_module_t imx462 = {
    .module = SENSOR_MNAME(imx462), .init = sensor_init, .start = sensor_start,
    .stop = sensor_stop, .deinit = sensor_deinit,
    .aexp_gain_control = gain, .aexp_line_control = exposure, .userspace_control = userspace,
};
