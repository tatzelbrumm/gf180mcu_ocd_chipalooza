# custom_pads: custom analog pads for the dedicated slot pads

Pad cells that are not in the PDK but can be chosen for an `s<N>_an[k]` position in `config.txt`. They must have the
form factor of `gf180mcu_ocd_io__asig_5p0` (75 x 350 um, the same edge rails, `ASIG5V` on Metal2 at the core edge
within x 15.34-59.66 um, pins `ASIG5V DVDD DVSS VDD VSS`), and their names must be listed in `analog_pad_types` in
`scripts/parse_config.py`. Plan and measurements: `docs/CUSTOM_PADS_PLAN.md` on branch `custom_pads_exploration` of
`tatzelbrumm/gf180_cm_ip__single2diff2single`.

## gf180_cm_io (slot 16)

| Cell | Slot position | State |
| --- | --- | --- |
| `gf180_cm_io__asig_in` | `s16_an[0]` (input) | placeholder: a renamed copy of `gf180mcu_ocd_io__asig_5p0` |
| `gf180_cm_io__asig_out` | `s16_an[1]` (output) | placeholder: a renamed copy of `gf180mcu_ocd_io__asig_5p0` |

Views: `mag/` (Magic; the PDK pad's file with its `GDS_FILE`/`GDS_START`/`GDS_END` properties, so Magic writes the PDK
pad's GDS under the new name, and explicit `$PDKPATH` paths for its two subcells), `gds/`, `lef/`, `spice/`, `verilog/`,
`xschem/`. Made by `tools/make_placeholder_pads.sh custom_pads/gf180_cm_io` (needs `PDK_ROOT`, `PDK`, KLayout's
Python module).

Where the flow reads them: `scripts/gen_padframe_template.tcl` and `scripts/layout_setup.tcl` (Magic search path),
`validate/run_lvs_ocd_chipalooza.sh` and `validate/run_lvs_padframe.sh` (spice).

## Checks

The make steps exit 0 even when something is wrong, so after `make clean-config config padframe wrappers symbols`:

- the `make config` output must not contain `Bad pad type` (with the stop patch in `parse_config.py` it exits 1);
- the `make padframe` output must not contain `couldn't be read` for a pad cell (`open_source` is the only expected
  one) nor `Bad cell path`;
- `CUSTOM_PAD_DIRS=$PWD/custom_pads/gf180_cm_io/mag magic -dnull -noconsole -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc custom_pads/tools/pad_abutment_check_custom.tcl`
  must end with `custom_bad 0`;
- `python3 -I custom_pads/tools/pad_edge_check.py custom_pads/gf180_cm_io/gds/gf180_cm_io.gds <cell>` must print
  `EDGE_SUMMARY <cell> ok`.

## Next

The input pad is to get its CDM network (series resistor and secondary diodes) inside the pad. Then the bond pad and
the core-side terminal are two nets, which the harness's analog pad class does not support yet.
