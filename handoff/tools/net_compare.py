# Compare the connectivity of two xschem spice netlists, subcircuit by subcircuit, independent of automatic net
# names: each net is the set of (instance, pin position) points plus the subcircuit port of that name.
# usage: python3 -I net_compare.py <old.spice> <new.spice> [ignore-instance:cell ...]
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from spice_inst import parse
import os, re
old, new = parse(sys.argv[1]), parse(sys.argv[2])
ignore = set(a for a in sys.argv[3:] if not a.startswith('--symdirs='))
symdirs = [a.split('=', 1)[1].split(',') for a in sys.argv[3:] if a.startswith('--symdirs=')]
symdirs = symdirs[0] if symdirs else []
def pinnames(symdir, cell):
    f = os.path.join(symdir, cell + '.sym')
    if not os.path.exists(f): return None
    out = []
    for m in re.finditer(r'^B 5 .*?\{name=(\S+) dir', open(f).read(), re.M):
        b = re.match(r'^(.*)\[(\d+):(\d+)\]$', m.group(1))
        if b:
            a, c = int(b.group(2)), int(b.group(3))
            step = 1 if c >= a else -1
            out += ['%s[%d]' % (b.group(1), i) for i in range(a, c + step, step)]
        else:
            out.append(m.group(1))
    return out
def nets(sub, symdir=None):
    d = {}
    for p in sub['ports']: d.setdefault(p, set()).add(('PORT', p))
    for inst, (cell, ns) in sub['inst'].items():
        if inst in ignore: continue
        names = pinnames(symdir, cell) if symdir else None
        for k, n in enumerate(ns):
            pin = names[k] if names and len(names) == len(ns) else k
            d.setdefault(n, set()).add((inst, cell, pin))
    return d
total = 0
for name in sorted(set(old) | set(new)):
    if name not in old or name not in new: print('subckt only in', 'new' if name in new else 'old', name); continue
    a = {frozenset(v) for v in nets(old[name], symdirs[0] if symdirs else None).values()}
    b = {frozenset(v) for v in nets(new[name], symdirs[1] if symdirs else None).values()}
    only_a, only_b = a - b, b - a
    if only_a or only_b:
        total += 1
        print(f'== {name}: {len(only_a)} nets only in old, {len(only_b)} only in new')
        for s in sorted(only_a, key=lambda s: sorted(map(str, s))): print('   old:', sorted(map(str, s))[:8])
        for s in sorted(only_b, key=lambda s: sorted(map(str, s))): print('   new:', sorted(map(str, s))[:8])
print('SUBCKTS_DIFFERING', total)
