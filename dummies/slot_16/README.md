# Dummy slot 16 layout (first shot, 2026-11-28)

`gds/slot_16.gds`, top cell `slot_16`, 1274.27 x 412.71 um (the bbox of `slot16_wrapper`). Contents: for each of the
63 labelled pins of `gds/slot16_wrapper.gds` (59 on Metal3 42/0 + label 42/10, 4 supplies on Metal5 81/0 + label
81/10), a rectangle on the same layer covering the wrapper's pin and reaching 2 um further into the slot, with the
same label; plus the DIEAREA 0/0. No devices. Made by
`python3 -I dummies/slot_16/make_slot16_dummy.py gds/slot16_wrapper.gds dummies/slot_16/gds/slot_16.gds`.

Before / after in KLayout: `gds/slot16_wrapper.gds` (the empty slot) and `gds/slot_16.gds` on top of it.

## Checks (logs in `logs/`)

| check | result |
| --- | --- |
| KLayout DRC, `gf180mcu.drc`, options of `validate/run_klayout_drc.sh` (`decks=all,-density`), on `slot_16` | 0 violations |
| the same on `slot16_wrapper` alone, and on both overlaid at the origin | 0 violations each |
| Magic extraction of `slot_16` vs `slot_16_ref.spice` (the 63 ports of `verilog/rtl/slot16_wrapper.v`, no devices), netgen | "Cell pin lists are equivalent"; no devices, so netgen reports "Not checked" for the rest |
| `make projects-gds SLOTS=16` + `make gds-prefill`, scratch copy with this file in `dependencies/slot_16/gds/` | rc 0; in `gf180mcu_ocd_chipalooza.gds.gz` the `slot_16` instance has the same box as `slot16_wrapper`, (375.76, 1755.65)-(1650.03, 2168.36) um |

Not run: `make drc` / `drc-final` on the chip, `extract-top`, `lvs-top`.

## Where the harness looks for it

`scripts/get_project_gds.sh` reads `slot_16.gds` from `dependencies/slot_16/` (the slot 16 project, `s16_source` in
`config.txt`, cloned by `make projects`), not from here. For a run with the dummy, copy `gds/slot_16.gds` to
`dependencies/slot_16/gds/` (as in the check above).
