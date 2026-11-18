#!/bin/bash
# make_pdk_overlay.sh -- build a writable overlay PDK_ROOT that adds the
# gf180mcu_ocd_io pad layouts to the read-only /foss/pdks/gf180mcuD.
#
# What it writes: only symbolic links (and the directories holding them)
# below $OV. It never writes into /foss/pdks, into the pad repo or into
# the Chipalooza repo. Running it again only replaces links.
#
# Output goes to make_pdk_overlay.out / .err beside this script.
# Run it inside the container as:  bash <path>/make_pdk_overlay.sh

D=$(cd "$(dirname "$0")" && pwd)
OUT="$D/make_pdk_overlay.out"; ERR="$D/make_pdk_overlay.err"
exec >"$OUT" 2>"$ERR"; set +e

SRC_PDK=${SRC_PDK:-/foss/pdks/gf180mcuD}              # read-only PDK variant dir
IO_MAG=${IO_MAG:-/foss/designs/gf180mcu_ocd_io/magic}  # pad repo, Magic views (flat)
OV=${OV:-/foss/designs/pdk_overlay}                    # overlay PDK_ROOT to create
DESIGNS=${DESIGNS:-/foss/designs}                      # where the library clones live
# extra libraries, each a clone $DESIGNS/<lib> laid out as <lib>/pdk/libs.ref/<lib>
EXTRA_LIBS=${EXTRA_LIBS:-gf180mcu_as_sc_mcu7t3v3}
PDK=gf180mcuD
export OV PDK

sec() { echo; echo "##### $*"; }
run() { echo "\$ $*"; "$@"; local rc=$?; [ $rc -ne 0 ] && echo "(exit status $rc)"; return 0; }

sec "0. settings"
echo "SRC_PDK=$SRC_PDK"; echo "IO_MAG=$IO_MAG"; echo "OV=$OV"
echo "DESIGNS=$DESIGNS"; echo "EXTRA_LIBS=$EXTRA_LIBS"
date -u +%Y-%m-%dT%H:%M:%SZ

sec "1. preconditions"
if [ ! -d "$SRC_PDK/libs.ref" ]; then echo "STOP: $SRC_PDK/libs.ref missing"; exit 1; fi
if [ ! -f "$IO_MAG/gf180mcu_ocd_io__asig_5p0.mag" ]; then
  echo "STOP: $IO_MAG/gf180mcu_ocd_io__asig_5p0.mag missing"; exit 1; fi
echo "ok: both exist"

sec "2. which Magic layers does asig_5p0 use (flat vs 3lm vs 4lm)?"
echo "(each line: number of 'rect' lines per '<< layer >>' section header;"
echo " this shows which metal levels each copy draws in)"
for v in "" 3lm 4lm 5lm; do
  f="$IO_MAG/${v:+$v/}gf180mcu_ocd_io__asig_5p0.mag"
  echo "--- ${v:-flat (magic/)}: $f"
  if [ -f "$f" ]; then
    awk '/^<< .* >>$/ {l=$2; next} /^rect / {n[l]++} END {for (k in n) print "  " k, n[k]}' "$f" | sort
  else
    echo "  (file does not exist)"
  fi
done

sec "3. build the overlay (links only)"
run mkdir -p "$OV/$PDK/libs.ref/gf180mcu_ocd_io"
# every top-level entry of the PDK variant except libs.ref
for e in "$SRC_PDK"/* "$SRC_PDK"/.[!.]*; do
  [ -e "$e" ] || continue
  b=$(basename "$e"); [ "$b" = libs.ref ] && continue
  ln -sfn "$e" "$OV/$PDK/$b"
done
# every library of libs.ref
for e in "$SRC_PDK"/libs.ref/*; do
  [ -e "$e" ] || continue
  ln -sfn "$e" "$OV/$PDK/libs.ref/$(basename "$e")"
done
# the addition: the pad library, Magic views from the pad repo (flat folder)
ln -sfn "$IO_MAG" "$OV/$PDK/libs.ref/gf180mcu_ocd_io/mag"
# the extra libraries, taken from their own clones
for lib in $EXTRA_LIBS; do
  src="$DESIGNS/$lib/pdk/libs.ref/$lib"
  if [ -d "$src" ]; then
    ln -sfn "$src" "$OV/$PDK/libs.ref/$lib"; echo "linked    $lib -> $src"
  else
    echo "NOT FOUND $lib: $src does not exist"
  fi
done
# gf180mcu_ocd_alpha: one clone holding three libraries, <clone>/{small,large,misc}/magic
for sz in small large misc; do
  src="$DESIGNS/gf180mcu_ocd_alpha/$sz/magic"
  dst="$OV/$PDK/libs.ref/gf180mcu_ocd_alpha_$sz"
  if [ -d "$src" ]; then
    mkdir -p "$dst"; ln -sfn "$src" "$dst/mag"; echo "linked    gf180mcu_ocd_alpha_$sz/mag -> $src"
  else
    echo "NOT FOUND gf180mcu_ocd_alpha_$sz: $src does not exist"
  fi
done
# gf180mcu_ocd_ip_sram: the clone keeps one folder per macro, <clone>/cells/<macro>/magic/*.mag;
# Magic wants one flat folder, so this one is made of one link per .mag file
SRAM="$DESIGNS/gf180mcu_ocd_ip_sram"
dst="$OV/$PDK/libs.ref/gf180mcu_ocd_ip_sram/mag"
if [ -d "$SRAM/cells" ]; then
  mkdir -p "$dst"
  declare -A seen; n=0; dup=0
  for f in "$SRAM"/cells/*/magic/*.mag; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    if [ -n "${seen[$b]}" ]; then dup=$((dup+1)); echo "DUPLICATE name $b: kept ${seen[$b]}, skipped $f"; continue; fi
    seen[$b]="$f"; ln -sfn "$f" "$dst/$b"; n=$((n+1))
  done
  echo "linked    gf180mcu_ocd_ip_sram/mag: $n .mag files from $SRAM/cells/*/magic ($dup duplicate names skipped)"
else
  echo "NOT FOUND gf180mcu_ocd_ip_sram: $SRAM/cells does not exist"
fi
echo "done"
run ls -la "$OV" "$OV/$PDK" "$OV/$PDK/libs.ref" "$OV/$PDK/libs.ref/gf180mcu_ocd_io"

sec "4. do the pad cells that gen_padframe.tcl places resolve?"
for c in asig_5p0 bi_24t in_c vdd vss dvdd dvss cor brk5 fill1 fill5 fill10; do
  f="$OV/$PDK/libs.ref/gf180mcu_ocd_io/mag/gf180mcu_ocd_io__$c.mag"
  if [ -f "$f" ]; then echo "found    $c"; else echo "MISSING  $c"; fi
done

echo "--- extra libraries: Magic technology named in each .mag file (first 'tech' line)"
for lib in $EXTRA_LIBS; do
  m="$OV/$PDK/libs.ref/$lib/mag"
  if [ -d "$m" ]; then
    echo "$lib: $(ls "$m"/*.mag 2>/dev/null | wc -l) .mag files"
    grep -h -m1 '^tech ' "$m"/*.mag 2>/dev/null | sort | uniq -c
  else
    echo "$lib: no mag/ folder in the overlay"
  fi
done
t="$OV/$PDK/libs.ref/gf180mcu_as_sc_mcu7t3v3/mag/gf180mcu_as_sc_mcu7t3v3__tap_2.mag"
if [ -f "$t" ]; then echo "found    as_sc tap_2"; else echo "MISSING  as_sc tap_2"; fi
for x in gf180mcu_ocd_alpha_small/mag/font_76 gf180mcu_ocd_alpha_large/mag/alpha_0 gf180mcu_ocd_alpha_misc/mag/open_source gf180mcu_ocd_ip_sram/mag/gf180mcu_ocd_ip_sram__sram1024x8m8wm1; do
  if [ -f "$OV/$PDK/libs.ref/$x.mag" ]; then echo "found    $x"; else echo "MISSING  $x"; fi
done
echo "--- technology named in the alpha and sram .mag files (first 'tech' line of each file)"
for l in gf180mcu_ocd_alpha_small gf180mcu_ocd_alpha_large gf180mcu_ocd_alpha_misc gf180mcu_ocd_ip_sram; do
  echo "$l: $(ls "$OV/$PDK/libs.ref/$l/mag/"*.mag 2>/dev/null | wc -l) .mag files"
  grep -h -m1 '^tech ' "$OV/$PDK/libs.ref/$l/mag/"*.mag 2>/dev/null | sort | uniq -c
done

sec "5. Magic test: load those cells through the overlay (reads only, never saves)"
if ! command -v magic >/dev/null 2>&1; then echo "magic not found"; exit 0; fi
export PDK_ROOT="$OV"
RC="$OV/$PDK/libs.tech/magic/$PDK.magicrc"
echo "PDK_ROOT=$PDK_ROOT  rcfile=$RC"
[ -f "$RC" ] || { echo "rcfile missing"; exit 0; }
SCR=$(mktemp -d)   # scratch working directory, so Magic writes nothing near your repos
cd "$SCR" || exit 0
timeout 120 magic -dnull -noconsole -rcfile "$RC" <<'EOF'
addpath $::env(PDK_ROOT)/gf180mcuD/libs.ref/gf180mcu_ocd_io/mag
addpath $::env(PDK_ROOT)/gf180mcuD/libs.ref/gf180mcu_as_sc_mcu7t3v3/mag
foreach l {gf180mcu_ocd_alpha_small gf180mcu_ocd_alpha_large gf180mcu_ocd_alpha_misc gf180mcu_ocd_ip_sram} {
    addpath $::env(PDK_ROOT)/gf180mcuD/libs.ref/$l/mag
}
foreach n {gf180mcu_as_sc_mcu7t3v3__tap_2 font_76 alpha_0 open_source gf180mcu_ocd_ip_sram__sram1024x8m8wm1} {
    load $n
    puts "LOADED $n: [llength [cellname list children $n]] subcell(s)"
}
foreach c {asig_5p0 bi_24t in_c vdd vss dvdd dvss cor brk5 fill1 fill5 fill10} {
    set n gf180mcu_ocd_io__$c
    load $n
    puts "LOADED $n: [llength [cellname list children $n]] subcell(s)"
}
quit -noprompt
EOF
echo "(magic exit status $?)"
cd / && rmdir "$SCR" 2>/dev/null

sec "end"
echo "finished normally"
