#!/bin/bash
# usage: write_logo.sh <harness checkout> <out.gds.gz> <PDK_ROOT with gf180mcu_ocd_alpha_misc>
# runs in <checkout>/magic, as the harness scripts do; the logo cell open_source comes from the PDK overlay
export PDK_ROOT="$3"
cd "$1/magic" || exit 1
magic -dnull -noconsole -rcfile "$PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc" <<EOT
drc off
crashbackups stop
locking disable
source ../scripts/layout_setup.tcl
load gf180mcu_padframe
gds compress 9
gds write $2
quit -noprompt
EOT
