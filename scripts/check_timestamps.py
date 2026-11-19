#!/usr/bin/env python3
"""Find Magic cells whose recorded child timestamps disagree with the children.

WHY THIS EXISTS.  On 2026-11-18 `make padframe' died with

    can't use empty string as operand of "-"

and its log still ended in "Done!".  The generator (gen_padframe.tcl) calls
`instance list abutment <name>' right after `getcell'.  In Magic 8.3 the
first such call returns an empty string whenever reading the cell's
children triggers a "Timestamp mismatches found in these cells" message:
the result string is lost.  The mismatch itself is a data problem.  Every
`use' in a .mag file records the child's timestamp as it was when the
parent was saved;  if the child file's own header timestamp differs, Magic
flags the pair.  In gf180mcu_ocd_io, gf180mcu_ocd_io__cor.mag records
GF_NI_COR_BASE with timestamp 1764351143 while GF_NI_COR_BASE.mag says
1766072706.

This script applies Magic's own rule (database/DBio.c, the test
`childStamp != subCellDef->cd_timestamp || childStamp == 0') to the files,
without starting Magic:

    for every `use CHILD ID' in a parent .mag file
        recorded = the `timestamp N' line that follows the `use' line
        actual   = the `timestamp N' in CHILD's header
                   (the first line before the first `<< layer >>' section)
        mismatch if recorded != actual, or if actual is 0 / missing

A child is looked up the way Magic does it:  if the `use' line names a
directory ("use CELL ID $PDKPATH/libs.ref/LIB/mag") that wins;  otherwise the
directories given on the command line, in order, first match wins.  Only the file that
wins for a name is checked as a parent, since a shadowed copy is never read.

    scripts/check_timestamps.py DIR [DIR ...]   scan these directories
    scripts/check_timestamps.py                 scan the harness default set:
                                                  magic/, dependencies/*/magic*,
                                                  and the PDK libs that
                                                  layout_setup.tcl puts on
                                                  the path, under $PDK_ROOT/$PDK
    scripts/check_timestamps.py --defaults DIR  DIR first, then the default set
    scripts/check_timestamps.py --tsv FILE ...  also write the full list as TSV
    scripts/check_timestamps.py --quiet ...     exit status only (1 = mismatches)

Children that are in none of the directories are counted, not reported as
mismatches:  a cell from a library you did not list is simply not checkable.

Reading the result.  recorded < actual means the child was changed after the
parent was last saved, so the parent's recorded `box' for that use may be
wrong too;  this script does not check boxes.  Do not just edit the number:
re-save the parent in Magic (it rewrites the stamp and the box together),
or ask the library's owner to.
"""

import os
import sys
import glob
import time
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# PDK libraries that scripts/layout_setup.tcl and gen_padframe.tcl add to the
# search path, relative to $PDK_ROOT/$PDK/libs.ref.
PDK_LIBS = ["gf180mcu_ocd_io", "gf180mcu_as_sc_mcu7t3v3",
            "gf180mcu_ocd_alpha_small", "gf180mcu_ocd_alpha_large",
            "gf180mcu_ocd_alpha_misc", "gf180mcu_ocd_ip_sram"]


def default_dirs():
    dirs = [os.path.join(ROOT, "magic")]
    for d in sorted(glob.glob(os.path.join(ROOT, "dependencies", "*", "magic*"))):
        if os.path.isdir(d):
            dirs.append(d)
            if os.path.isdir(os.path.join(d, "paramcells")):
                dirs.append(os.path.join(d, "paramcells"))
    pdk_root = os.environ.get("PDK_ROOT", "")
    pdk = os.environ.get("PDK", "gf180mcuD")
    for lib in PDK_LIBS:
        d = os.path.join(pdk_root, pdk, "libs.ref", lib, "mag")
        if pdk_root and os.path.isdir(d):
            dirs.append(d)
    return dirs


def parse(path):
    """Return (header_stamp, [(use_name, use_id, recorded_stamp)])."""
    header = 0
    uses = []
    in_header = True
    cur = None
    with open(path, errors="replace") as fh:
        for line in fh:
            tok = line.split()
            if not tok:
                continue
            if line.startswith("<<"):
                in_header = False
                cur = None
                continue
            if in_header:
                if tok[0] == "timestamp" and len(tok) > 1 and tok[1].lstrip("-").isdigit():
                    header = int(tok[1])
                continue
            if tok[0] == "use" and len(tok) >= 3:
                cur = [tok[1], tok[2], None, tok[3] if len(tok) > 3 else None]
                uses.append(cur)
            elif tok[0] == "timestamp" and cur is not None and cur[2] is None:
                if len(tok) > 1 and tok[1].lstrip("-").isdigit():
                    cur[2] = int(tok[1])
            elif tok[0] in ("transform", "box", "array"):
                pass
    return header, [(n, i, s, d) for n, i, s, d in uses]


def explicit_dir(parent_path, path):
    """Directory named by the optional path token of a `use' line, or None.

    Magic expands environment variables in it.  PDKPATH is set by the PDK's
    magicrc to $PDK_ROOT/$PDK, so it is derived from those here.
    """
    if not path:
        return None
    env = dict(os.environ)
    env.setdefault("PDKPATH", os.path.join(os.environ.get("PDK_ROOT", ""),
                                           os.environ.get("PDK", "gf180mcuD")))
    p = os.path.expandvars(path.replace("$PDKPATH", env["PDKPATH"])
                               .replace("${PDKPATH}", env["PDKPATH"]))
    if not os.path.isabs(p):
        p = os.path.join(os.path.dirname(os.path.abspath(parent_path)), p)
    return os.path.normpath(p) if os.path.isdir(p) else None


def utc(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t)) if t else "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="*")
    ap.add_argument("--tsv")
    ap.add_argument("--defaults", action="store_true",
                    help="append the default directories after the ones given")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    dirs = list(a.dirs)
    if not dirs or a.defaults:
        dirs += default_dirs()
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        print("check_timestamps: no directories to scan", file=sys.stderr)
        return 2

    index = {}                       # cell name -> (path, header stamp)
    parents = []                     # (path, name) files that win for their name
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "*.mag"))):
            name = os.path.basename(p)[:-4]
            if name in index:
                continue             # shadowed: Magic never reads this one
            index[name] = (p, None)
            parents.append((p, name))
    for name, (p, _) in list(index.items()):
        index[name] = (p, parse(p)[0])

    rows = []
    unresolved = set()
    nuses = 0
    for p, name in parents:
        _, uses = parse(p)
        for child, uid, rec, where in uses:
            nuses += 1
            key = os.path.basename(child)
            if key.endswith(".mag"):
                key = key[:-4]
            # An explicit path on the use line wins over the search path.
            xdir = explicit_dir(p, where)
            xfile = os.path.join(xdir, key + ".mag") if xdir else None
            if xfile and os.path.isfile(xfile):
                cpath, actual = xfile, parse(xfile)[0]
            elif key in index:
                cpath, actual = index[key]
            else:
                unresolved.add(key)
                continue
            if rec is None:
                rec = 0
            if rec != actual or actual == 0:
                rows.append((p, name, uid, key, rec, actual, cpath))

    if a.tsv:
        with open(a.tsv, "w") as fh:
            fh.write("parent_file\tparent\tuse_id\tchild\trecorded\trecorded_utc"
                     "\tactual\tactual_utc\tactual_minus_recorded_s\tchild_file\n")
            for p, name, uid, key, rec, actual, cpath in rows:
                fh.write(f"{p}\t{name}\t{uid}\t{key}\t{rec}\t{utc(rec)}\t"
                         f"{actual}\t{utc(actual)}\t{actual - rec}\t{cpath}\n")

    if not a.quiet:
        print(f"scanned {len(parents)} cell files in {len(dirs)} directories, "
              f"{nuses} uses; {len(unresolved)} children not in these directories")
        if not rows:
            print("no timestamp mismatches")
        else:
            bychild = {}
            for r in rows:
                bychild.setdefault(r[3], []).append(r)
            print(f"{len(rows)} mismatching uses of {len(bychild)} cells:\n")
            for key in sorted(bychild):
                rs = bychild[key]
                print(f"{key}   [{rs[0][6]}]")
                print(f"    its own timestamp: {rs[0][5]}  ({utc(rs[0][5])} UTC)")
                for p, name, uid, _, rec, actual, _c in rs:
                    side = ("child newer than the parent's record" if actual > rec
                            else "child older than the parent's record")
                    print(f"    {name}  (use {uid}) records {rec}  ({utc(rec)} UTC)"
                          f"  {side}")
                print()
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
