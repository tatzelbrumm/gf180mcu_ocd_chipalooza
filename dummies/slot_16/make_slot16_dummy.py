#!/usr/bin/env python3
# make_slot16_dummy.py --- write dummies/slot_16/gds/slot_16.gds, a dummy slot 16 layout.
#
# Usage (repository top level of tatzelbrumm/gf180mcu_ocd_chipalooza):
#	python3 -I dummies/slot_16/make_slot16_dummy.py gds/slot16_wrapper.gds dummies/slot_16/gds/slot_16.gds
#
# The harness places a slot's layout, top cell slot_<N>, exactly over its wrapper (scripts/get_project_gds.sh).
# This dummy has, for each labelled pin of slot16_wrapper (Metal3 42/0 + label 42/10, Metal5 81/0 + label 81/10),
# a rectangle on the same layer that covers the wrapper's pin shape and reaches STUB um further into the slot, and the
# same label at the same place; plus the wrapper's DIEAREA (0/0). No devices, no other shapes. Pins at the west edge
# (x = 0) grow to +x, pins at the east edge grow to -x.
import sys
import klayout.db as db

STUB = 2.0  # um, how far each pin reaches into the slot beyond the wrapper's pin shape

src, dst = sys.argv[1], sys.argv[2]
w = db.Layout(); w.read(src)
wc = w.cell('slot16_wrapper')
if wc is None:
    sys.exit('no cell slot16_wrapper in ' + src)
bbox = wc.dbbox()

o = db.Layout(); o.dbu = w.dbu
top = o.create_cell('slot_16')
npins = 0
for (ml, md), (ll, ld) in [((42, 0), (42, 10)), ((81, 0), (81, 10))]:
    wm, wl = w.find_layer(ml, md), w.find_layer(ll, ld)
    om, ol = o.layer(ml, md), o.layer(ll, ld)
    rects = [it.shape().dbox for it in wc.begin_shapes_rec(wm).each() if it.shape().is_box()]
    for it in wc.begin_shapes_rec(wl).each():
        s = it.shape()
        if not s.is_text():
            continue
        t = s.dtext
        hit = [r for r in rects if r.contains(t.position())]
        if len(hit) != 1:
            sys.exit(f'label {t.string} at {t.position()}: {len(hit)} pin shapes on {ml}/{md}')
        r = hit[0]
        if r.left <= bbox.left + 1e-6:
            r = db.DBox(r.left, r.bottom, r.right + STUB, r.top)
        elif r.right >= bbox.right - 0.05:
            r = db.DBox(r.left - STUB, r.bottom, r.right, r.top)
        else:
            sys.exit(f'label {t.string}: pin shape {r} is at neither the west nor the east edge')
        top.shapes(om).insert(r)
        top.shapes(ol).insert(db.DText(t.string, db.DTrans(t.position())))
        npins += 1
d0 = w.find_layer(0, 0)
for it in wc.begin_shapes_rec(d0).each():
    top.shapes(o.layer(0, 0)).insert(it.shape().dbox)
o.write(dst)
print(f'slot_16: {npins} pins, bbox {top.dbbox()}, written to {dst}')
