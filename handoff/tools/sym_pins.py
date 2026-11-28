# Compare pin positions of xschem symbols between a git revision and the working tree.
import re, subprocess, sys, glob, os
rev = sys.argv[1]
def pins(text):
    return {m.group(5): (float(m.group(1)), float(m.group(2))) for m in re.finditer(r'^B 5 (\S+) (\S+) (\S+) (\S+) \{name=([^ ]+)', text, re.M)}
for f in sorted(glob.glob('xschem/*.sym')):
    try: old = subprocess.run(['git', 'show', f'{rev}:{f}'], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError: print(f'{f}: new'); continue
    a, b = pins(old), pins(open(f).read())
    moved = [n for n in a if n in b and a[n] != b[n]]
    gone = [n for n in a if n not in b]
    new = [n for n in b if n not in a]
    if moved or gone or new:
        print(f'{f}: moved {moved} removed {gone} added {new}')
