import sys,re
p=sys.argv[1]; ids=sys.argv[2].split(','); keys=sys.argv[3].split(',') if len(sys.argv)>3 else None
for l in open(p,encoding='utf-8'):
    m=re.match(r'^([A-Z_]+)\|id=([0-9]{3})\|',l)
    if not m or m.group(2) not in ids: continue
    if keys is None: print(l.rstrip()); print(); continue
    d={}
    for w in l.rstrip().split('|'):
        if '=' in w:
            k,v=w.split('=',1); d.setdefault(k,v)
    print(m.group(1),m.group(2),' || '.join('%s=%s'%(k,d.get(k,'-')) for k in keys))
