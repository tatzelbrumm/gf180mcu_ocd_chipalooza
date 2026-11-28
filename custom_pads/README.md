# custom_pads: custom pads for the dedicated slot pads

Pad cells that are not in the PDK but can be chosen for an `s<N>_an[k]` position in `config.txt`. Plan and
measurements: `docs/CUSTOM_PADS_PLAN.md` on branch `custom_pads_exploration` of
`tatzelbrumm/gf180_cm_ip__single2diff2single`.

## The custom pad class (`scripts/parse_config.py`)

A custom pad is any module in `custom_pads/<lib>/verilog/*.v` (files named `*__blackbox*` are skipped). It must have:

- the size of the `gf180mcu_ocd_io` pads: abutment box 75 x 350 um, the same rails on both side edges;
- supply pins `DVDD DVSS VDD VSS`, connected by the padframe template (5 V ring, 3.3 V ring);
- one bond pad pin `pad` (or `PAD`), connected to the chip pin `s<N>_an[k]`;
- any number of core-side pins, each labelled on Metal2 reaching the core edge (y = 350 um, pad-local) and with its
  direction (as seen from the pad) declared in the verilog module. Pin `<p>` of the pad at `s<N>_an[k]` becomes the
  core signal `<signal name>_<p>` (signal name from `config.txt`, e.g. `s16_an_0_outp`): a port of
  `gf180mcu_padframe`, a Metal3 label at the core edge (`label_<side>_signal` of `gen_padframe_template.tcl`) and so a
  pin of the slot wrapper.

## gf180_cm_io (slot 16)

| Cell | Slot position | Copy of | Core-side pins (direction seen from the pad) |
| --- | --- | --- | --- |
| `gf180_cm_io__asig_in` | `s16_an[0]` | `gf180mcu_ocd_io__in_c` | `outp outn` out, `vcm vref` in, `iref` inout, `en_3v3 en_3v3_b` in |
| `gf180_cm_io__asig_out` | `s16_an[1]` | `gf180mcu_ocd_io__bi_24t` | `vinp vinn vref` in, `iref` inout, `en_3v3 en_3v3_b` in |

The pin names and directions are those of the IHP custom pads of `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`
(branch `claude/c3-s2d-pad-layout`, `c913388`: `sg13cmos5l_IOPadSingle2Diff.sym`, `sg13cmos5l_IOPadDiff2Single.sym`),
with the IHP rings `iovdd iovss vdd vss` mapped to `DVDD DVSS VDD VSS`. Unlike the IHP pads, these include the bond
pad (the `gf180mcu_ocd_io` cells all do, through `5LM_METAL_RAIL_PAD_60` / `Bondpad_5LM`).

**These are placeholders, not for tapeout as they are.** Each is the PDK digital pad with all its circuitry, its
digital pins (`PU PD Y`, resp. `A CS IE OE PD PU SL Y`) no longer labelled, so its driver and input path are not tied
off, and the new pins are Metal2 stubs (0.38 um wide, pad-local y 348.4-350, x = 20, 25, ... um) that connect to
nothing inside the pad. Gutting the pads and connecting the pins is the next step.

Views: `mag/` (no `GDS_*` properties: Magic writes the top cell from the `.mag`; the PDK subcells, named with
`$PDKPATH`, are copied from the PDK GDS), `gds/` (`.gds.gz`) and `lef/` (written by Magic), `spice/` (the PDK pad as a
subcircuit, the new pins unconnected), `verilog/` (read by `parse_config.py`). Made by
`python3 -I tools/make_custom_placeholders.py custom_pads/gf180_cm_io` (needs `PDK_ROOT`, `PDK`, Magic).

Where the flow reads them: `scripts/parse_config.py` (verilog), `scripts/gen_padframe_template.tcl` and
`scripts/layout_setup.tcl` (Magic search path), `validate/run_lvs_ocd_chipalooza.sh` and `validate/run_lvs_padframe.sh`
(spice).

## Changes outside the generated files

`magic/chipalooza_frame.mag` (hand-drawn, not generated) carried a Metal3 strap and a label `s16_an[0]` / `s16_an[1]`
at x 350-354 um in front of each slot 16 pad, for the analog pad's core terminal. They are removed: they overlapped
the new pin labels and would have shorted all pins of a pad together. The other slots are unchanged.

Not yet updated, hand-maintained, still with `s16_an[0:1]` as the slot 16 pins: `verilog/rtl/chipalooza_frame.v`,
`verilog/rtl/slot16_wrapper.v`, `xschem/chipalooza_frame.sch`, `xschem/gf180mcu_ocd_chipalooza.sch`,
`netlist/*/chipalooza_frame.spice`, `netlist/schematic/gf180mcu_ocd_chipalooza.spice`, `verilog/gl/gf180mcu_ocd_chipalooza.v`.
LVS of the frame and of the chip will not match until they are.

## Checks

The make steps exit 0 even when something is wrong, so after `make clean-config config padframe wrappers symbols gds-slots`:

- the `make config` output must not contain `Bad pad type` (with the stop patch, `make config` exits 1);
- the `make padframe` output must not contain `couldn't be read` for a pad cell (`open_source` is expected) nor
  `Bad cell path`;
- `CUSTOM_PAD_DIRS=$PWD/custom_pads/gf180_cm_io/mag magic -dnull -noconsole -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc custom_pads/tools/pad_abutment_check_custom.tcl`
  must end with `custom_bad 0`;
- `python3 -I custom_pads/tools/pad_edge_check.py --pins custom_pads/gf180_cm_io/gds/<cell>.gds.gz <cell>` must print
  `EDGE_SUMMARY <cell> ok` (warnings about the Metal2 VSS rails shifted by 0.15 / 0.24 um come from the PDK pads).
