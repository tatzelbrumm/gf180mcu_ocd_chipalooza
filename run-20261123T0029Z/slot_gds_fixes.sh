#!/bin/bash
# Sandbox fixes so that get_project_gds.sh finds a project's GDS: write dependencies/slot_N/final/gds/slot_N.gds
# as a copy of the project's own GDS with the top cell renamed to slot_N (the naming convention in get_project_gds.sh).
# Run from the repository top level.  The projects' original files are not changed.
set -e
fix() {  # slot, source gds, source top cell
  out=dependencies/slot_$1/final/gds/slot_$1.gds
  klayout -zz -r scripts/rename_top_cell.rb -rd input=$2 -rd output=$out -rd newname=slot_$1
  echo "slot_$1: $2 (top $3) -> $out"
}
fix 7  dependencies/slot_7/final/gds/sar_adc_slot.gds       sar_adc_r4_slot
fix 15 dependencies/slot_15/final/gds/slot15_wrapper.gds    slot15_wrapper
