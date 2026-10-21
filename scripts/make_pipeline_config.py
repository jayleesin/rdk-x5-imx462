#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Apply numeric/name changes to a user-supplied SDK example; no vendor template is bundled."""
import argparse
import hashlib
import json
import re
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
if hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() != reference['local_reproduction']['pipeline_baseline_LF_sha256']:
    parser.error('SDK example does not match the tested baseline.')
text = raw.decode('utf-8').replace('\r\n', '\n')
text = text.replace('imx219', 'imx462').replace('RAW10', 'RAW12').replace('raw10', 'raw12').replace('30fps', '20fps')
text, count = re.subn(r'(#define SENSOE_FPS\s+)30\b', r'\g<1>20', text)
if count != 1:
    parser.error('Unexpected FPS declaration.')
text, count = re.subn(r'(#define RAW12\s+)0x2B\b', r'\g<1>0x2C', text)
if count != 1:
    parser.error('Unexpected pixel format declaration.')
changes = {
    'mclk': ('24', '0'), 'mipiclk': ('1728', '1782'),
    'linelenth': ('3448', '2200'), 'framelenth': ('1166', '3375'),
    'addr': ('0x10', '0x1a'), 'gpio_enable_bit': ('0x01', '0x00'),
    'mipi_rx': ('2', '0'), 'mclk_freq': ('24000000', '37125000'),
    'bit_width': ('10', '12'), 'chip_id_reg': ('0x0000', '0x319a'),
    'chip_id': ('0x0219', '0xd007'), 'sensor_i2c_addr_list': ('{0x10}', '{0x1a}'),
}
for field, (old, new) in changes.items():
    pattern = r'(\.' + re.escape(field) + r'\s*=\s*)' + re.escape(old) + r'(?=\s*,)'
    text, count = re.subn(pattern, lambda m: m.group(1) + new, text)
    if count != 1:
        parser.error('Unexpected occurrence count for ' + field)
text = text.replace('imx462_1920x1080_tuning.json', 'imx462_tuning.json')
preamble = '''/* Evaluation application template; validation results are in provenance.json.
 * mclk=0 disables host sensor clock; this setup relies on the module oscillator.
 * vin_attr_ex_mask=0: this file does not enable a host MCLK.
 * 0xd007 is the observed 16-bit big-endian read at 0x319a; NOT proven unique to IMX462.
 * GPIO power/reset and IR-CUT control are outside this evaluation. */
'''
data = (preamble + text).replace('\n', '\r\n').encode('utf-8')
if hashlib.sha256(data).hexdigest() != reference['reference_artifacts']['pipeline_configuration']['sha256']:
    parser.error('Generated configuration does not match the tested snapshot.')
with args.output.open('xb') as f:
    f.write(data)
print('Reproduced the pipeline configuration locally. The vendor-derived output is excluded from the public release.')
