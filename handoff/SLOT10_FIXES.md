# Slot 10: problems in the harness, and what the slot 10 designer should know

For Tim Edwards (harness) and the slot 10 designer (`config.txt:133` `slot_10: Al Sabagh`; `config.txt:89`
`s10_source: -`, so no repository is known). Found on 2026-11-28 by a Claude Code session working for the slot 16
designer, while checking slot 16 changes against `main`. **None of this is caused by the slot 16 changes:** every
item is reproduced on the fork's `main` at `2f18cd4` (= Tim's commits), either as committed or after running
`main`'s own scripts (`make clean-config config padframe wrappers symbols`).

Marks: **[V]** verified (file and line, or command and output), **[I]** inferred (from what), **[U]** unverified.
Coordinates in µm: chip coordinates as in `magic/gf180mcu_padframe.mag` and `magic/chipalooza_frame.mag` (both placed
with the same transform in `gf180mcu_ocd_chipalooza.mag`), slot coordinates relative to the slot 10 wrapper. Slot 10's
box in chip coordinates: x 349.76-1624.01, y 4207.65-4620.36 (`scripts/run_gen_user_wrappers.sh:56-66`: slot 18 at
y 903.65, +413 per slot) **[V]**.

## Where slot 10's pads are

| Pad | Placement (`scripts/gen_padframe.tcl`) | Bond pad label (`gf180mcu_padframe.mag`) | Core-side strap |
| --- | --- | --- | --- |
| `pad_s10_an_0` | **top row**, `place_pad_top` (line 595) | x 697.5-757.5, y 5008-5068 | see problem 1 |
| `pad_s10_an_1` | left side, `place_pad_left` (line 582) | x 2-62, y 4544.5-4604.5 | x 351-353, y 4552.34-4596.66 |
| `pad_s10_an_2` | left side, `place_pad_left` (line 578) | x 2-62, y 4204.5-4264.5 | x 351-353, y 4212.34-4256.66 |
| `pad_vss3v3_3` (ground) | left side, between them | Metal5 `vss3v3` x 351.35-354.35, y 4368.36-4440.64 (`label_power_pad_left`, `gen_padframe_template.tcl:1089`) | |

**[V]** (instance transforms `gf180mcu_padframe.mag` lines 1225-1235; labels from the same file.)

## Problem 1: the top-row pad `s10_an[0]` is labelled as if it were on the left side

- `scripts/parse_config.py` decides the side from the slot number: slots 1-9 right, 10-18 left (`parse_config.py`, Tcl
  part, `if slot_num >= 0 and slot_num <= 9: side = 'right' else: side = 'left'`) **[V]**. So `gen_padframe.tcl:878` is
  `label_left_analog pad_s10_an_0  pad s10_an\[0\]`, for a pad on the top row **[V]**.
- `label_left_analog` paints, at the abutment box's east side, a 1 µm wide Metal2 + Metal3 strip with Via2 over the
  full box height minus 15.34 µm at each end, plus a Metal3 label (`gen_padframe_template.tcl:169-187`) **[V]**. On the
  rotated top pad that is a strip along the pad's side edge: Metal2/Via2/Metal3 at x 765-766 (Metal3 to 769),
  y 4735.34-5054.66, labelled `s10_an[0]` (`gf180mcu_padframe.mag`, Metal2/Metal3/Via2 rects at those coordinates)
  **[V]**.
- That strip runs across the padframe's ring rails, which cross every pad and filler on Metal3 (and Metal2 for VSS)
  **[V]** for the rail geometry of the pad cells (`gf180mcu_ocd_io__fill10` and `__asig_5p0` edge spans); that this
  shorts `s10_an[0]` to DVDD, DVSS, VDD and VSS is **[I]** from that geometry (no padframe extraction was run).
- The core-side terminal of a top pad is its bottom edge (y = 4720); nothing connects it to slot 10 **[I]**: the
  generated `chipalooza_frame_wrapper` has no `s10_an[0]` label (its labels come from the inner area of the padframe,
  `gen_padframe_template.tcl` "Create the user project wrapper", and the strip is outside it) **[V]**, and the frame
  layout has none at the top edge (problem 2) **[V]**.

**Fix (harness):** take the side of each `s<N>_an[k]` pad from its `place_pad_<side>` line in the template, not from the
slot number, so that `pad_s10_an_0` gets `label_top_analog`. Then route `s10_an[0]` from the top pad's core edge
(y 4720, strap x 705.34-749.66) to slot 10 in the frame layout (the slot's top edge is at y 4620.36).

## Problem 2: the frame layout's slot 10 straps follow an older pad order

`magic/chipalooza_frame.mag` (hand-drawn) has three Metal3 strap labels for slot 10 at x 351-353 **[V]**
(lines 5302-5306 on `main`):

| Frame label | y | What the padframe has there |
| --- | --- | --- |
| `s10_an[0]` | 4552.35-4596.66 | the strap of **`s10_an[1]`** |
| `s10_an[1]` | 4382.35-4426.66 | the ground pad `pad_vss3v3_3` and its `vss3v3` power connection |
| `s10_an[2]` | 4212.35-4256.66 | the strap of `s10_an[2]` (correct) |

Consequences:

- The slot 10 wrapper cut from the frame carries `s10_an[0]` and `s10_an[1]` on the same Metal3 shape (slot
  coordinates x 1.24-3.24, y 344.69-389.01) **[V]** (`magic/slot10_wrapper.mag` after `make wrappers` on `main`).
- `make extract-frame` reports `Warning:  Ports "s10_an[1]" and "s10_an[0]" are electrically shorted.`, on `main` as
  committed and after regeneration **[V]** (logs in `logs/`).
- The frame strap `s10_an[1]` (Metal3, x 351-353) overlaps the `vert_power_connect` cell of `pad_vss3v3_3` (Metal2 to
  Metal5, x 350-351.35, y 4368.36-4440.64) by 0.35 µm in x: probably `s10_an[1]` shorted to `vss3v3` at chip level
  **[I]** from the geometry; not extracted.

**Fix (harness):** redraw slot 10's straps in `chipalooza_frame.mag` for the present pad order: no strap at
y 4382-4427 (ground pad), `s10_an[1]` at y 4552-4597, `s10_an[2]` at y 4212-4257, `s10_an[0]` from the top row
(problem 1). Then `make wrappers symbols gds-slots`.

## Problem 3: a ground pin `vss3v3` appears in the slot 10 wrapper, but the harness core does not know it

- Running `main`'s `make wrappers` puts the Metal5 label `vss3v3` of `pad_vss3v3_3` into the slot 10 wrapper: slot
  coordinates x 1.59-4.59, y 160.72-233.00, layer Metal5 **[V]**. `run_gen_user_wrappers.sh` renames a `vss3v3`
  label to `vss_3v3` only if it is on Metal2 (`if {\$result == "metal2"}`), so this one stays `vss3v3` and becomes a
  port **[V]**.
- The slot 10 wrapper committed on `main` does not have it, although the padframe committed on `main` has the label
  at the same place **[V]**: the committed slot wrappers were not regenerated after the padframe changed **[I]**.
- Slots 11 and 17 have the same kind of pin by design: `inout wire vss3v3, // ground pad routed through this slot
  (vss3v3_slot11 on the frame)` in `verilog/rtl/slot11_wrapper.v:53`, frame ports `vss3v3_slot11` / `vss3v3_slot17`
  (`verilog/rtl/chipalooza_frame.v:38-39, 1287, 1432`; `xschem/chipalooza_frame.sch`, `xschem/chipalooza_frame.sym`)
  **[V]**. Slot 10 has none of these.
- Result: `make lvs-verilog` passes on `main` as committed (`Circuits match uniquely`) and fails after
  `make clean-config config padframe wrappers symbols extract-sch`: `The following subcells failed to match:
  slot10_wrapper(0) slot10_wrapper(1)` **[V]** (logs).

**Fix (harness), either:** add `vss3v3` to slot 10 as for slots 11 and 17 (`verilog/rtl/slot10_wrapper.v` port,
`chipalooza_frame.v` port `vss3v3_slot10` and `.vss3v3(vss3v3_slot10)`, an iopin on the slot 10 wrapper's new pin in
`xschem/chipalooza_frame.sch` (symbol row at local y -320), a pin on `xschem/chipalooza_frame.sym`, regenerate
`validate/lvs/blackboxes.v`); **or** decide that the label should not reach into the slot and keep it out of the
wrapper. Then commit the regenerated wrapper views.

## For the slot 10 designer

Until the harness is fixed, as the harness's own scripts generate the slot 10 wrapper today **[V]** unless marked:

- `s10_an[2]`: Metal3 pin at the west edge, x 1.24-3.24, y 4.70-49.02. Correct.
- `s10_an[1]`: the correct place is the west edge at y 344.69-389.01, but that shape is also labelled `s10_an[0]`.
  A second `s10_an[1]` label sits at y 174.69-219.01, in front of a ground pad. Do not rely on either label yet.
- `s10_an[0]`: its pad is on the **top row** of the chip; there is no connection from it into slot 10 yet **[I]**.
  Ask the harness maintainer where it will arrive (probably the slot's top edge).
- New pin `vss3v3` (Metal5, west edge, x 1.59-4.59, y 160.72-233.00): a 3.3 V ground strap of a padframe ground pad
  that reaches into the slot. Keep Metal5 clear there unless you connect to it; it is the chip's 3.3 V ground,
  not a switched supply **[I]** from the pad type (`gf180mcu_ocd_io__vss`).
- The wrapper size is unchanged: 1274.27 x 412.71 µm **[V]** (`run_gen_user_wrappers.sh:145`).

## Related harness issues seen on the way (not slot 10 specific)

- `magic/run_extract_chipalooza_frame.sh` sets every slot wrapper's `FIXED_BBOX` to `0 0 537.15 273` (an IHP slot size)
  before extracting the frame; the GF180 slot is 1274.27 x 412.71 **[V]**. Pins above y = 273 lie outside that box
  **[I]**; whether the extraction is affected was not isolated **[U]**.
- `make extract-frame` on `main` as committed: `chipalooza_frame: 719 errors`, `gf180mcu_ocd_ip__biasgen: 16 errors`;
  after regeneration only the 16 `biasgen` errors **[V]** (logs). Not investigated.

## Logs

In `logs/` next to this file: `main_committed_extract-frame.log`, `main_regenerated_extract-frame.log`,
`main_lvs-verilog_committed.log`, `main_lvs-verilog_regenerated.log`.
