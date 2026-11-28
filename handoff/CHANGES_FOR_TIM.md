# Branch `custom_padframe`: what changed against `main`, for Tim Edwards

Fork `tatzelbrumm/gf180mcu_ocd_chipalooza`, branch `custom_padframe`, started from `main` at `2f18cd4` (Tim's commits
plus a merge). Purpose: let slot 16 (`config.txt:132`, project `tatzelbrumm/gf180_cm_ip__single2diff2single`) use
**custom pads** in its two dedicated pad positions, and fix what the harness scripts got wrong on the way. The pads
themselves are placeholders for now (copies of PDK digital pads with new core-side pins); the slot 16 designer
designs the real ones later under the same names.

Marks: **[V]** verified, **[I]** inferred, **[U]** unverified. "Regenerated" means `make clean-config config padframe
wrappers symbols gds-slots` with PDK `gf180mcuD` (open_pdks `1.0.588-128-ge7a6777`), Magic 8.3.706, netgen 1.5.332,
xschem from the cloud environment, IP submodules at `c21d8c0`, `96a93f8`, `a6f16be`.

## 1. Commits, oldest first

| Commit | What | Kind |
| --- | --- | --- |
| `c66429b` | the fork's own fixes from branch `chipalooza_artifacts_run1`, `fixes/pad_pins/`: padframe verilog pad pins `iovdd/iovss/vdd/vss` → `DVDD/DVSS/VDD/VSS`; LVS scripts without the IHP `flatten gf180mcu_SecondaryProtection`, PDK pad netlist as fallback | fix (pre-existing bug) |
| `ebcdd77`, `e1fb916`, `276643a` | first trial: slot 16 placeholders as renamed copies of `asig_5p0`; `analog_pad_types` in `parse_config.py`; Magic search path; LVS reads the custom spice | superseded by the next rows, except the search path and LVS lines |
| `4401f24` | `parse_config.py` stops with exit code 1 on an unknown pad type (it printed "Bad pad type", wrote broken files and exited 0); the Tcl SIGNALS branch got its missing `else` (it re-emitted the previous line) | fix (pre-existing bug) |
| `843dc36` | `custom_pads/gf180_cm_io/`: placeholders `gf180_cm_io__asig_in` (copy of `in_c`) and `gf180_cm_io__asig_out` (copy of `bi_24t`) with the pins of the designer's IHP pads; generator and checks in `custom_pads/tools/` | new |
| `a85894b` | `parse_config.py`: **custom pad class** (below); the stale `spaces`/`signal_name` in the PAD branch fixed | new + fix |
| `f836915` | `magic/chipalooza_frame.mag`: slot 16's two analog straps removed (they would short the new pins) | change for slot 16 |
| `d910034` | regenerated views | generated |
| `87a1500` | symbols keep their pins: padframe template core-signal ports moved to the end of the port list; `gen_xschem_sym.py` sizes the slot body from the widest label pair on one row | fix (found through slot 16) |
| `a8a5c1b` | regenerated views | generated |
| `692e3b0` | slot 16 in the hand-maintained harness core: RTL, schematics, frame symbol, gate-level top; regenerated schematic netlists, LVS views, frame extraction, frame LVS report | change for slot 16 |

## 2. The custom pad class (`scripts/parse_config.py`, `a85894b`)

- A custom pad is a module in `custom_pads/<lib>/verilog/*.v` (`*__blackbox*` skipped) with supply pins
  `DVDD DVSS VDD VSS`, one bond pad pin `pad` (or `PAD`), and core-side pins with declared directions. Its layout
  (`custom_pads/<lib>/mag/`) has the gf180mcu_ocd_io pad size and edge rails and labels each core-side pin on Metal2 at
  the core edge.
- For `s<N>_an[k]` of that type: the bond pad connects to `s<N>_an[k]`; core-side pin `<p>` becomes the core signal
  `<signal name>_<p>` (e.g. `s16_an_0_outp`): a port of `gf180mcu_padframe`, a `label_<side>_signal` in
  `gen_padframe.tcl`, hence a slot wrapper pin. **[V]** (generated files, section 4).
- Magic finds the cells through `addpath ../custom_pads/gf180_cm_io/mag` in `gen_padframe_template.tcl` and
  `layout_setup.tcl` (`e1fb916`); LVS reads `custom_pads/gf180_cm_io/spice/gf180_cm_io.spice` (`e1fb916`, on top of
  `lvs_scripts.patch`). The path is per library, hard-coded; a loop over `custom_pads/*/mag` would be cleaner **[I]**.

## 3. Changes to hand-drawn harness files for slot 16 (`f836915`, `692e3b0`)

| File | Change |
| --- | --- |
| `magic/chipalooza_frame.mag` | the two Metal3 straps + labels `s16_an[0]`, `s16_an[1]` at x 350-354 removed |
| `verilog/rtl/slot16_wrapper.v` | `inout wire [1:0] s16_an` → 13 ports (directions from the slot: `outp outn` in; `vcm vref vinp vinn en_3v3 en_3v3_b` out; `iref` inout) |
| `verilog/rtl/chipalooza_frame.v` | port `s16_an` → the 13 ports; slot16 instance connections |
| `verilog/rtl/digital_tb.v` | the 13 ports left unconnected |
| `verilog/gl/gf180mcu_ocd_chipalooza.v` | slot 16 only: 13 wires to padframe and harness core; slot 16's `_esd` wires removed. The rest of the file is still IHP-era (slot 4 has 1 pin, slot 5 has 3, `_esd` wires for all slots) and is read by no flow **[V]** (grep) |
| `xschem/chipalooza_frame.sym` | pin `s16_an[0:1]` → 13 pins at the bottom of the right side; body extended to y 820 |
| `xschem/chipalooza_frame.sch` | iopin `s16_an[0:1]` → 13 iopins at the slot16 wrapper's new pins; wires `#net62`, `#net63`, `#net64` rerouted (they crossed the taller slot16 symbol's pin column at y 4510, 4690, 4710 and would have joined pins) |
| `xschem/gf180mcu_ocd_chipalooza.sch` | frame pins and padframe pins of the 13 nets joined by labels; the chip pin `s16_an[1:0]` still on the padframe |

## 4. Checks run (no DRC, no chip-level extraction or LVS)

- Quick steps: all exit 0; only `Cell open_source couldn't be read` (as on `main`) **[V]**.
- Abutment/port check (`custom_pads/tools/pad_abutment_check_custom.tcl`): 19 pads, 0 empty, `custom_bad 0`; edge
  check (`pad_edge_check.py --pins`) ok for both placeholders **[V]**.
- Symbols: compared with `main`, no pin of any generated symbol moves; added pins only **[V]**
  (`logs/symbol_pins_vs_main.txt`).
- Schematic netlists: xschem netlists of the branch and of `main` (same xschem), compared net by net with pins by
  name: identical except slot 16's ports and the `vss3v3` pin of slot 10 **[V]** (`logs/schematic_net_compare_*.txt`).
- `make lvs-verilog`: `slot16_wrapper` matches; only `slot10_wrapper` fails, as it does on `main` after regeneration
  **[V]** (`SLOT10_FIXES.md`, problem 3).
- `make extract-frame` + `make lvs-frame`: same summary as `main` as committed (83 subcircuits match uniquely, 4 with
  port errors, 3 do not match); `Device classes slot16_wrapper and slot16_wrapper are equivalent` **[V]**
  (`validate/comp_chipalooza_frame.out`, `logs/`).
- Extraction of the slot 16 wrapper: 13 separate slot 16 ports **[V]**.

## 5. Open, for slot 16

- The frame layout has no frame-level labels for the 13 nets (lvs-frame: `(no pin, node is slot16_wrapper_0/...)`).
  Adding Metal3 labels with ports in `chipalooza_frame.mag` gave port-number collisions in the cut slot wrapper
  (`port 190 has two names`, from `port makeall`), and after renumbering, netgen flattened `slot16_wrapper` **[V]**;
  reverted. Needs a decision on how frame ports and wrapper ports should be numbered **[U]**.
- `label_left_signal` paints Via2 on a 0.38 µm wide pin; not DRC-checked. Digital pads were never placed on the left
  or right side of this padframe before **[V]** (template).
- The placeholders are not for tapeout: driver and input path of the copied digital pads are not tied off, and the new
  pins connect to nothing inside the pad.

## 6. Pre-existing issues found (also on `main`), not fixed here

1. `make padframe` exits 0 when a pad cell cannot be read; the failed `getcell` leaves the previous spacer selected,
   `identify` renames it, and the pads after it shift **[V]** (seen with a missing search path).
2. Slot 10: see `SLOT10_FIXES.md` (top-row pad labelled as left; stale frame straps, short `s10_an[0]`/`s10_an[1]`;
   unknown `vss3v3` pin).
3. The committed views on `main` are not what `main`'s scripts produce (e.g. `magic/slot16_wrapper.mag`,
   `slot10_wrapper`) **[V]**: regenerating `main` without changes modifies them.
4. `magic/run_extract_chipalooza_frame.sh`: `FIXED_BBOX 0 0 537.15 273` for the slot wrappers (IHP size) **[V]**.
5. `make extract-frame` on `main` as committed: `chipalooza_frame: 719 errors`, `gf180mcu_ocd_ip__biasgen: 16 errors`
   **[V]**; not investigated.
6. Earlier findings of the fork, not repeated here: `fixes/TIM_SUMMARY.md` on branch `chipalooza_artifacts_run2`
   (final top cell name, `gzip` without `-f`, `make setup` without `scripts/setup.sh`, slot 8 URL typo, LVS inputs,
   ground domain).
