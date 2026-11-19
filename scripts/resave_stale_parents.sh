#!/bin/bash
#
# Re-save Magic cells whose recorded child timestamps are stale.
#
# WHY.  scripts/check_timestamps.py lists the cells whose `use' lines record a
# child timestamp that disagrees with the child file.  Editing the number in
# the text would hide a real inconsistency:  a `use' also records the child's
# bounding box, and if the child changed after the parent was saved, that box
# is wrong too.  Magic knows how to repair both:  when it reads the child it
# notices the mismatch (the children are read first, then the parent), and
# `save' of the parent rewrites the
# `timestamp' AND the `box' of that use from the real child.  That is all
# this script does, one parent at a time.
#
# What it does NOT do.  It does not touch the parent's own header timestamp
# (so it does not cascade into the parents of the parent;  `drc catchup'
# would change that stamp, so it is not used).  Magic may append a
# `<< checkpaint >>' section to a re-saved cell:  that only marks the cell as
# needing a DRC re-check, and 27 cells in the harness already carry one.
#
# Usage (inside the container, at the top level of the repository):
#
#	scripts/resave_stale_parents.sh [--dry-run] [DIR ...]
#
#	DIR ...	directories whose .mag files may be rewritten.
#		Default:  magic/   (the harness's own cells).
#		Give a clone of another library's magic/ directory to repair
#		that one (for a pull request upstream).  The PDK tree and
#		dependencies/ are never rewritten unless you name them.
#	--dry-run	only list what would be re-saved
#
#	PDK_ROOT, PDK	as for the other scripts (default /usr/share/pdk, gf180mcuD)
#
# Afterwards it re-runs the checker on the same directories and prints what
# is left.  What is left is somebody else's file:  report it to its owner.
#
# Review before committing:  `git diff --stat' (the changes should be a
# handful of `timestamp'/`box' lines per file, nothing else).

export PDK_ROOT=${PDK_ROOT:-/usr/share/pdk}
export PDK=${PDK:-gf180mcuD}

ROOT=$(cd "$(dirname "$0")/.." && pwd)
CHECK="$ROOT/scripts/check_timestamps.py"
RC="$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc"

DRY=0
if [ "$1" = "--dry-run" ]; then DRY=1; shift; fi
DIRS=("$@")
[ ${#DIRS[@]} -eq 0 ] && DIRS=("$ROOT/magic")

for d in "${DIRS[@]}"; do
    [ -d "$d" ] || { echo "not a directory: $d" >&2; exit 2; }
    case $(cd "$d" && pwd) in
        "$PDK_ROOT"/*) echo "refusing to rewrite inside PDK_ROOT: $d" >&2; exit 2 ;;
    esac
done
[ -r "$RC" ] || { echo "no magic rc file: $RC" >&2; exit 2; }

SCRATCH=$(mktemp -d)
TSV="$SCRATCH/mismatches.tsv"

# The directories to repair are searched first, then the usual set
# (dependencies, PDK libraries), so every child can be found.
python3 -I "$CHECK" --quiet --defaults --tsv "$TSV" "${DIRS[@]}"
if [ $(($(wc -l < "$TSV") - 1)) -le 0 ]; then
    echo "no timestamp mismatches in the scanned directories; nothing to do"
    rm -rf "$SCRATCH"; exit 0
fi

for d in "${DIRS[@]}"; do
    d=$(cd "$d" && pwd)
    # One line per parent:  <parent cell> <stale child> <stale child> ...
    python3 -I - "$TSV" "$d" > "$SCRATCH/todo.txt" <<'EOF'
import sys, csv, os
tsv, d = sys.argv[1], os.path.realpath(sys.argv[2])
todo = {}
for r in csv.DictReader(open(tsv), delimiter="\t"):
    p = os.path.realpath(r["parent_file"])
    if os.path.dirname(p) == d:
        todo.setdefault(r["parent"], set()).add(r["child"])
for k in sorted(todo):
    print(k, *sorted(todo[k]))
EOF
    n=$(wc -l < "$SCRATCH/todo.txt")
    echo
    echo "== $d: $n cell(s) to re-save"
    sed 's/^/   /' "$SCRATCH/todo.txt"
    [ "$n" -eq 0 ] && continue
    [ $DRY -eq 1 ] && continue

    # Run in the directory itself, so that Magic finds (and `save' writes)
    # the file there.
    ( cd "$d" && magic -dnull -noconsole -rcfile "$RC" <<EOF
drc off
# Magic writes a library path on a use line in portable form (variable name
# PDKPATH plus a relative part) only if the Tcl variable PDKPATH is set.
# The PDK magicrc sets PDK_ROOT only, so set PDKPATH here, otherwise a
# re-save would bake a machine path into the file.
if {![info exists PDKPATH]} { set PDKPATH $PDK_ROOT/$PDK }
addpath $ROOT/magic
foreach dep [glob -nocomplain $ROOT/dependencies/*/magic $ROOT/dependencies/*/magic/paramcells] {
    addpath \$dep
}
foreach lib {gf180mcu_ocd_io gf180mcu_as_sc_mcu7t3v3 gf180mcu_ocd_alpha_small gf180mcu_ocd_alpha_large gf180mcu_ocd_alpha_misc gf180mcu_ocd_ip_sram} {
    addpath $PDK_ROOT/$PDK/libs.ref/\$lib/mag
}
set fd [open $SCRATCH/todo.txt r]
while {[gets \$fd line] >= 0} {
    set parent [lindex \$line 0]
    set kids [lrange \$line 1 end]
    # Read the stale children first:  a parent that is read afterwards is
    # checked against the children already in memory, and Magic marks its
    # recorded stamps for rewriting.
    foreach kid \$kids { catch {load \$kid -silent} }
    load \$parent -silent
    set h0 [lindex [exec md5sum \$parent.mag] 0]
    save \$parent
    # Magic reports a failed write only as a message;  check the file itself.
    if {[lindex [exec md5sum \$parent.mag] 0] ne \$h0} {
        puts "RESAVED \$parent"
    } else {
        puts "NOT WRITTEN \$parent  (read-only file or directory?)"
    }
}
close \$fd
quit -noprompt
EOF
    )
done

[ $DRY -eq 1 ] && { echo; echo "(dry run: nothing written)"; rm -rf "$SCRATCH"; exit 0; }

echo
echo "== re-check"
python3 -I "$CHECK" --defaults "${DIRS[@]}"
rc=$?
rm -rf "$SCRATCH"
exit $rc
