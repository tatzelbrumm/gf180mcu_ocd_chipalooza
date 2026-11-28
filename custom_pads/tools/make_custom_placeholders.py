#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""make_custom_placeholders.py --- placeholder custom pads made from PDK digital pads.

Each placeholder is a copy of a gf180mcu_ocd_io digital pad (all its circuitry kept, to be gutted later) with
  - its digital core-side pins (PU, PD, Y, A, OE, ...) no longer labelled: they stay in the layout as unconnected
    nets, the pad's driver and input path are therefore NOT tied off (placeholder only, not for tapeout as is);
  - the bond pad label renamed PAD -> pad;
  - new core-side pins: Metal2 stubs at the core edge (pad-local y 348.4-350, 0.38 um wide, 5 um pitch from
    x = 20 um), labelled with the pin names of the IHP custom pads of sg13cmos5l_cm_ip__single2diff2single
    (branch claude/c3-s2d-pad-layout, symbols sg13cmos5l_IOPadSingle2Diff.sym / sg13cmos5l_IOPadDiff2Single.sym);
    the stubs connect to nothing inside the pad;
  - the rails DVDD DVSS VDD VSS as in the PDK pad.
Views written to <outdir>: mag/ (no GDS_* properties: Magic writes the top cell from the .mag; the PDK subcells are
still copied from the PDK GDS), gds/ (gzipped) and lef/ (both written by Magic from the .mag), spice/ (the PDK pad as a
subcircuit plus the unconnected new pins), verilog/ (module with directions: read by scripts/parse_config.py).

usage: PDK_ROOT=... PDK=gf180mcuD python3 -I make_custom_placeholders.py <outdir>   (outdir e.g. custom_pads/gf180_cm_io)
"""
import os
import re
import subprocess
import sys

LIB = 'gf180_cm_io'
RAILS = ['DVDD', 'DVSS', 'VDD', 'VSS']
# cell: (PDK base pad, [(pin, direction as seen from the pad), ...]).  Directions: IHP symbols; iref is inout there.
CELLS = {
    'gf180_cm_io__asig_in': ('gf180mcu_ocd_io__in_c', [
        ('outp', 'output'), ('outn', 'output'), ('vcm', 'input'), ('vref', 'input'),
        ('iref', 'inout'), ('en_3v3', 'input'), ('en_3v3_b', 'input')]),
    'gf180_cm_io__asig_out': ('gf180mcu_ocd_io__bi_24t', [
        ('vinp', 'input'), ('vinn', 'input'), ('vref', 'input'),
        ('iref', 'inout'), ('en_3v3', 'input'), ('en_3v3_b', 'input')]),
}
UNIT = 200                      # Magic units per um (magscale 1 10, 5 nm)
X0, PITCH, W = 20.0, 5.0, 0.38  # stub placement, um
Y1, Y2 = 348.4, 350.0
MAGUSE = {'input': 'input', 'output': 'output', 'inout': 'bidirectional'}


def die(msg):
    print('make_custom_placeholders.py: ' + msg, file=sys.stderr)
    sys.exit(1)


def pdk_lib():
    root, pdk = os.environ.get('PDK_ROOT'), os.environ.get('PDK')
    if not root or not pdk:
        die('set PDK_ROOT and PDK')
    return os.path.join(root, pdk, 'libs.ref', 'gf180mcu_ocd_io')


def make_mag(base_text, pins):
    """Return the placeholder .mag text from the PDK pad's .mag text."""
    lines = base_text.splitlines()
    out, i, drop = [], 0, set()
    # labels to drop: every metal2 signal label of the base pad (its digital core-side pins)
    for k, l in enumerate(lines):
        if re.match(r'^[fr]label metal2 ', l):
            drop.add(l.split()[-1])
    while i < len(lines):
        l = lines[i]
        if re.match(r'^[fr]label ', l) and l.split()[-1] in drop:
            i += 2 if i + 1 < len(lines) and lines[i + 1].startswith('port ') else 1
            continue
        if re.match(r'^string GDS_(FILE|START|END) ', l):
            i += 1
            continue
        m = re.match(r'^use (\S+) +(\S+)$', l)
        if m:
            l = l + ' $PDKPATH/libs.ref/gf180mcu_ocd_io/mag'
        if re.match(r'^[fr]label metal5 .* PAD$', l):
            l = l[:-3] + 'pad'
            if i + 1 < len(lines) and lines[i + 1].startswith('port '):
                out.append(l)
                f = lines[i + 1].split()
                out.append(' '.join(f[:3] + ['signal', 'bidirectional']))
                i += 2
                continue
        if l == 'string LEFclass PAD INPUT':
            l = 'string LEFclass PAD INOUT'
        out.append(l)
        i += 1
    # port numbering: rails and pad keep their order, then the new pins
    names = []
    for k, l in enumerate(out):
        if re.match(r'^[fr]label ', l) and k + 1 < len(out) and out[k + 1].startswith('port '):
            n = l.split()[-1]
            if n not in names:
                names.append(n)
    order = [n for n in sorted(names, key=lambda n: (n != 'pad', RAILS.index(n) if n in RAILS else -1))]
    if sorted(order) != sorted(RAILS + ['pad']):
        die('unexpected ports left in base pad: ' + ' '.join(order))
    index = {n: k + 1 for k, n in enumerate(order)}
    for k, l in enumerate(out):
        if re.match(r'^[fr]label ', l) and k + 1 < len(out) and out[k + 1].startswith('port '):
            f = out[k + 1].split()
            f[1] = str(index[l.split()[-1]])
            out[k + 1] = ' '.join(f)
    rects, labels = [], []
    for j, (pin, pdir) in enumerate(pins):
        x1 = round((X0 + PITCH * j) * UNIT)
        x2 = x1 + round(W * UNIT)
        y1, y2 = round(Y1 * UNIT), round(Y2 * UNIT)
        rects.append('rect %d %d %d %d' % (x1, y1, x2, y2))
        labels.append('flabel metal2 s %d %d %d %d 0 FreeSans 700 90 0 0 %s' % (x1, y1, x2, y2, pin))
        labels.append('port %d nsew signal %s' % (len(order) + j + 1, MAGUSE[pdir]))
    k = out.index('<< metal2 >>') + 1
    out[k:k] = rects
    k = out.index('<< labels >>') + 1
    out[k:k] = labels
    return '\n'.join(out) + '\n'


def main():
    if len(sys.argv) != 2:
        die('usage: make_custom_placeholders.py <outdir>')
    outdir = os.path.abspath(sys.argv[1])
    src = pdk_lib()
    for d in ['mag', 'gds', 'lef', 'spice', 'verilog']:
        os.makedirs(os.path.join(outdir, d), exist_ok=True)
    spice = ['* ' + LIB + ': placeholder custom pads (copies of PDK digital pads, new core-side pins unconnected)',
             '* needs ' + os.path.join('$PDK_ROOT/$PDK/libs.ref/gf180mcu_ocd_io/spice/gf180mcu_ocd_io.spice'), '']
    verilog = ['// ' + LIB + ': placeholder custom pads; port directions as seen from the pad.',
               '// scripts/parse_config.py reads this file for the core-side pins of each pad type.', '']
    for cell, (base, pins) in CELLS.items():
        with open(os.path.join(src, 'mag', base + '.mag')) as f:
            text = make_mag(f.read(), pins)
        with open(os.path.join(outdir, 'mag', cell + '.mag'), 'w') as f:
            f.write(text)
        # spice: the base pad's own subcircuit, its digital pins on internal nets
        with open(os.path.join(src, 'spice', 'gf180mcu_ocd_io.spice')) as f:
            m = re.search(r'^\.subckt ' + base + r' (.*)$', f.read(), re.M)
        basepins = m.group(1).split()
        conn = [p if p in RAILS else ('pad' if p == 'PAD' else 'nc_' + p) for p in basepins]
        newpins = [p for p, _ in pins]
        spice += ['.subckt %s %s pad %s' % (cell, ' '.join(RAILS), ' '.join(newpins)),
                  'X0 %s %s' % (' '.join(conn), base),
                  '* noconn ' + ' '.join(newpins), '.ends', '']
        decl = ['    inout %s;' % r for r in RAILS] + ['    inout pad;'] + ['    %s %s;' % (d, p) for p, d in pins]
        verilog += ['module %s (%s);' % (cell, ', '.join(RAILS + ['pad'] + newpins))] + decl + ['endmodule', '']
    with open(os.path.join(outdir, 'spice', LIB + '.spice'), 'w') as f:
        f.write('\n'.join(spice))
    with open(os.path.join(outdir, 'verilog', LIB + '.v'), 'w') as f:
        f.write('\n'.join(verilog))
    # gds and lef from Magic
    tcl = ['drc off', 'crashbackups stop', 'locking disable', 'gds compress 9', 'addpath ' + os.path.join(outdir, 'mag')]
    for cell in CELLS:
        tcl += ['load %s -silent' % cell,
                'gds write %s' % os.path.join(outdir, 'gds', cell + '.gds.gz'),
                'lef write %s -hide' % os.path.join(outdir, 'lef', cell + '.lef')]
    tcl += ['quit -noprompt']
    rc = os.path.join(os.environ['PDK_ROOT'], os.environ['PDK'], 'libs.tech', 'magic', os.environ['PDK'] + '.magicrc')
    r = subprocess.run(['magic', '-dnull', '-noconsole', '-rcfile', rc], input='\n'.join(tcl) + '\n',
                       text=True, capture_output=True, cwd=outdir)
    bad = [l for l in (r.stdout + r.stderr).splitlines() if "couldn't be read" in l or 'Error' in l]
    if r.returncode != 0 or bad:
        die('magic failed:\n' + '\n'.join(bad or [r.stdout[-2000:], r.stderr[-2000:]]))
    print('placeholder library %s written to %s: %s' % (LIB, outdir, ' '.join(CELLS)))


if __name__ == '__main__':
    main()
