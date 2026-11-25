# Pending for Tim (summary written by the cloud build session, 2026-11-25)
Nothing here has been sent to Tim; no issue or pull request was opened. Drafts and patches are in the repository tatzelbrumm/gf180mcu_ocd_chipalooza (the fork).
Base: harness main 2f18cd4 (Tim's config.txt update on top of 78edf00), PDK gf180mcuD (open_pdks e7a6777), Magic 8.3.706.

## 1. Configuration and project slots
- Slot 8 URL typo in config.txt: `https://github.cm/...` (should be github.com). Sandbox fix: `fix_config_slot8_url.patch` (this directory).
- Slots 7 and 15: GDS exists, but not named `slot_N.gds` with top cell `slot_N`. Sandbox: renamed copies made by `slot_gds_fixes.sh` (this directory). Not checked: that the slot 7 pins line up with the wrapper.
- Slots 1, 5, 18: need a slot-sized `slot_N.gds` with the wrapper pins. Slots 1 and 18 have only bare core layouts; slot 5's bandgap/gds/bandgap.gds is an empty cell.
- Slots 8, 14, 16, 17: no GDS at all (slot 17 has only .mag files).
- Details: `SLOT_PROJECT_ISSUES.md` (this directory).

## 2. Harness script bugs
- `scripts/run_gen_filled_final_gds.sh` leaves the top cell as gf180mcu_ocd_chipalooza, so `make drc-final` fails (cell gf180mcu_ocd_chipalooza_final not found). Regression from commit bf1d19b. Fix: `fix_final_top_cell.patch`.
- The same script's `gzip` has no `-f`: a rerun does not overwrite an existing gds/..._final.gds.gz. No patch yet.
- `make setup` calls `./scripts/setup.sh`, which is not in the repository. No draft.

## 3. LVS inputs and padframe
- `netlist/schematic/gf180mcu_ocd_io.spice` is in no commit; the SRAM netlist path ends in `.cdl` but the PDK has only `.spice`. Patch for the second: `lvs_sram_spice_path.patch`; both in `ISSUE_lvs_inputs.md`.
- Padframe verilog uses the IHP pad pins iovdd/iovss/vdd/vss; the GF pads have DVDD/DVSS/VDD/VSS. `fixes/pad_pins/` (pad_pins.patch, lvs_scripts.patch), written by the planning session's agent.
- `gen_padframe_template.tcl` lines 1076-1077 label two dvss pads `vdd5v0` (looks like a bug, unverified).
- Still failing: LVS "Netlists do not match", 28 mismatches, including the ground-domain problem the README expects. The LVS only sees the empty slot wrappers, not the project GDS.

## 4. DRC results (run 2)
- Padframe: the same 228 violations as run 1 (V2.2a 148, V2.1 80), at the top-left padframe corner that Tim's own commit calls unfinished.
- Projects: 3159 violations in total with 5 projects placed. Most in slot 6, then DPF.1 (336) in the polysilicon fill, then slot 4. Not checked: whether they are real.
- DRC database: `results/gf180mcu_ocd_chipalooza_final.lyrdb` (this branch).

## Where the drafts are (repository tatzelbrumm/gf180mcu_ocd_chipalooza)
- Branches chipalooza_artifacts and chipalooza_artifacts_run1, directory fixes/: ISSUE.md, PR.md, fix_final_top_cell.patch, ISSUE_lvs_inputs.md, PR_lvs_inputs.md, lvs_sram_spice_path.patch, pad_pins/, ALL_TRACKED_CHANGES_applied_in_tree.patch.
- Branch chipalooza_artifacts_run2, directory fixes/: this summary, SLOT_PROJECT_ISSUES.md, slot_gds_fixes.sh, fix_config_slot8_url.patch.
