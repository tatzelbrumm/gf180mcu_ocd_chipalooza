# Chipalooza cloud build report (final, 2026-11-23)
Model claude-sonnet-5-5, effort medium. PDK gf180mcuD, Magic 8.3.706, 4 cores, 15 GB. `make setup` does not exist in the repo (scripts/setup.sh missing); skipped on user's instruction.

| step | rc | s | result judged by log / output files |
|---|---|---|---|
| check | 0 | 0 | 0 stale, 1 not built |
| submodules | 0 | 2 | 3 dependencies filled |
| pad abutment | - | - | ABUT_SUMMARY pads 17 empty 0 (OK). addpath: fd_io (line 47) before ocd_io (line 50) |
| clean-config .. user-id (7 steps) | 0 | 0-5 | ran; logs not grepped |
| projects-gds | 0 | 7 | 0 projects placed (all slots empty) |
| gds-prefill | 0 | 159 | file written; SRAM "placed on top of itself" warnings |
| gds-final (1st run) | 0 | 68 | file written, top cell NOT renamed (bug) |
| drc-final (1st) | 0 | 3 | FAILED: top cell gf180mcu_ocd_chipalooza_final not found |
| extract-sch-top | 0 | 0 | ok |
| extract-top | 0 | 1621 | ok, 3 port-short warnings |
| lvs-top (1st) | 0 | 1 | FAILED: netlist/schematic/gf180mcu_ocd_io.spice missing |
| gds-final (patched) | 0 | 72 | renamed top cell gf180mcu_ocd_chipalooza_final, 1030 cells |
| drc-final (first rerun) | killed | - | killed by my own poller time limit at rule DN.3; partial result kept in artifacts results/ |
| drc-final (full) | 0 | 11534 | COMPLETE: 228 violations (V2.2a 148, V2.1 80), all in cell gf180mcu_padframe |
| lvs-top (IO spice copied, SRAM .spice path) | 0 | 3 | netgen aborted: 452 iovdd/iovss pin errors |
| lvs-top (pad pin patch + lvs scripts patch) | 0 | 36 | ran to end: pin errors 0, "Netlists do not match", 28 mismatches (vdd/avdd, vss/avss, shld2/shld3 nets, net count 44/45 and 79/80); SRAM, constant_block, fill5, brk5 black boxes |

Causes and fixes (all in artifacts branch fixes/): top cell name (fix_final_top_cell.patch, regression of bf1d19b); LVS inputs (ISSUE_lvs_inputs.md, lvs_sram_spice_path.patch); pad pin names (fixes/pad_pins, from the planning session). Applied tracked-file changes: fixes/ALL_TRACKED_CHANGES_applied_in_tree.patch.
Not examined: whether the 228 DRC violations are real or caused by the unfinished padframe corner/pad work; README ground-domain LVS issue untouched; gen_padframe_template.tcl lines 1076-1077 label two dvss pads vdd5v0 (reported by planning session, unverified).
Sizes: final GDS 33.1 MB gz, 23.7 MB xz in 1 chunk; pre-fill 22.8 MB; cells.tsv 1030 cells. The chat log check failed (reasoning not in the log text), so no new chat log; the earlier one stays.
