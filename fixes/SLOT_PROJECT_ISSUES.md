# Slot projects: what `make projects-gds` found (run 2, config.txt of main 2f18cd4 + slot 8 URL fix)
Convention (scripts/get_project_gds.sh): a file `slot_<N>.gds` or `.gds.gz` with a top cell named `slot_<N>`, hierarchical, covering the slot (1274.3 x 412.7 um, origin at the slot's lower left).

| slot | project | state | sandbox fix |
|---|---|---|---|
| 2, 4, 6 | Weiser, Saunders, Rodovalho | found in `gds/slot_N.gds[.gz]`, top `slot_N`, 1274.3 x 412.7 | none needed |
| 7 | Ananth and Yu | `final/gds/sar_adc_slot.gds`, top `sar_adc_r4_slot`, 1193.0 x 402.7 (smaller than the slot, origin 0,0) | copy `final/gds/slot_7.gds` with top cell renamed (slot_gds_fixes.sh). Not checked: that its pins line up with the wrapper. |
| 15 | Munaut | `final/gds/slot15_wrapper.gds`, top `slot15_wrapper`, slot-sized | copy `final/gds/slot_15.gds` with top cell renamed. Its top cell name equals the harness's own slot15_wrapper cell. |
| 1 | Sands and Araujo | only bare core layouts (e.g. Layout/LNA/output/LNAMkV__TOP/magic_RC/TOP.gds, 130.9 x 79.8), no slot-sized GDS | NOT placed: a core cell has no wrapper pins and would sit at the wrong position |
| 5 | Moya | `bandgap/gds/bandgap.gds` has top cell TOP and is EMPTY (no geometry) | NOT placed |
| 18 | Novatska | only core layouts (ldo_v2.gds 184.1 x 121.4, ldo_v2_place_snug.gds 180.2 x 96.6) plus device pieces | NOT placed |
| 8, 14, 16, 17 | Hill/Hoshino, Dexter, Maier, Bhagwat | no GDS at all (slot 17 has only .mag files, 8/14/16 no layout files) | NOT placed |
| 3, 9, 10, 11, 12, 13 | | no project assigned in config.txt | - |

To tell Tim / the authors: slot 8 URL in config.txt was `github.cm` (fixed in sandbox, fix_config_slot8_url.patch); slots 1, 5, 18 need a slot_N.gds with the wrapper pins; slots 8, 14, 16, 17 need a GDS; slots 7 and 15 need the slot_N name (file and top cell).
The two renamed files are untracked files inside the cloned project repositories (dependencies/slot_7, dependencies/slot_15); the originals are untouched.
