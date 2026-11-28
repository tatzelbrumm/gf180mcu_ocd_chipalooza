import sys
def parse(f):
    txt=open(f).read().replace('\n+',' ')
    subs={}; cur=None
    for l in txt.splitlines():
        t=l.split()
        if not t or t[0].startswith('*'): continue
        if t[0].lower()=='.subckt': cur=t[1]; subs[cur]={'ports':t[2:], 'inst':{}}; continue
        if t[0].lower()=='.ends': cur=None; continue
        if cur and t[0][0] in 'xX':
            args=[a for a in t[1:] if '=' not in a]
            subs[cur]['inst'][t[0]]=(args[-1], args[:-1])
    return subs
if __name__=='__main__':
    s=parse(sys.argv[1]); key=sys.argv[2]
    for sub,d in s.items():
        if any(key in p for p in d['ports']): print('SUBCKT', sub, 'ports:', [p for p in d['ports'] if key in p])
        for i,(cell,nets) in d['inst'].items():
            if any(key in n for n in nets): print(' ', sub, i, cell, [n for n in nets if key in n])
