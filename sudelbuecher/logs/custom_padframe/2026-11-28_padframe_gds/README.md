# Padframe GDS for viewing in KLayout (2026-11-28)

Written by Magic 8.3.706 (`write_logo.sh`, run in `<checkout>/magic` with `scripts/layout_setup.tcl`, `load gf180mcu_padframe`,
`gds write`), top cell `gf180mcu_padframe` in both files:

| file | source |
|---|---|
| `gf180mcu_padframe_main_2f18cd4.gds.gz` | `tatzelbrumm/gf180mcu_ocd_chipalooza`, branch `main` at `2f18cd4` (the base of `custom_padframe`) |
| `gf180mcu_padframe_custom_padframe_bcbef3b.gds.gz` | `tatzelbrumm/gf180mcu_ocd_chipalooza`, branch `custom_padframe` at `bcbef3b` (slot 16 with the placeholder pads `gf180_cm_io__asig_in` / `__asig_out`) |

The PDK install in the cloud container (`/foss/pdks/gf180mcuD`, open_pdks `1.0.588-128-ge7a6777`) lacks the library
`gf180mcu_ocd_alpha_misc`, which holds the logo cell `open_source`. Both files were written with `PDK_ROOT` pointing to
a symlink overlay of that PDK whose `libs.ref/gf180mcu_ocd_alpha_misc/mag` is `misc/magic` of
`RTimothyEdwards/gf180mcu_ocd_alpha` at `0597ebd`; the PDK itself was not changed. Checked with KLayout 0.30.12: both
files contain `caravel_motto` and `open_source` (bbox 3.3,22.9 ; 129,72.15 µm). The write logs (`*.write.log`) have no
"couldn't be read" and no error lines. Scratch paths in the logs and the script are replaced by `<scratch>`.

Not the chip GDS: no slot projects, no fill, no seal ring (`make gds-prefill` / `gds-final` were not run).
