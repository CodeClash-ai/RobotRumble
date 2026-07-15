import glob,re,statistics,collections,os

def parse(fn):
    txt=open(fn,errors='ignore').read()
    w=re.search(r'Done! (\w+) won',txt)
    winner=w.group(1) if w else 'Tie'
    states=[]
    # Game start has no turn; after turn N health units
    chunks=re.split(r'(?:Game start:|After turn (\d+):)',txt)
    # easier find all Health lines preceded by marker
    cur=None
    for line in txt.splitlines():
        m=re.match(r'After turn (\d+):', line)
        if m: cur=int(m.group(1))
        elif line.startswith('Game start:'): cur=0
        m=re.match(r'Health (\d+) (\d+) Units (\d+) (\d+)', line)
        if m and cur is not None:
            h1,h2,u1,u2=map(int,m.groups()); states.append((cur,h1,h2,u1,u2))
    return winner,states

rows=[]
for fn in sorted(glob.glob('/logs/rounds/0/sim_*.txt'), key=lambda x:int(re.search(r'sim_(\d+)',x).group(1))):
    w,st=parse(fn); d={t:(h1,h2,u1,u2) for t,h1,h2,u1,u2 in st}
    final=st[-1]
    row={'sim':int(re.search(r'sim_(\d+)',fn).group(1)),'winner':w,'states':d,'final':final}
    rows.append(row)

print(collections.Counter(r['winner'] for r in rows))
for t in [80,85,89,90,91,94,97,100]:
    vals=[]; trans=collections.Counter()
    by=collections.defaultdict(list)
    for r in rows:
        if t in r['states']:
            h1,h2,u1,u2=r['states'][t]; vals.append((u1-u2,h1-h2,r['winner'],r['sim']))
            trans[(u1-u2>0)-(u1-u2<0),r['winner']]+=1
            by[r['winner']].append(u1-u2)
    print('\nTurn',t,'avg unit diff',statistics.mean(v[0] for v in vals),'avg hp diff',statistics.mean(v[1] for v in vals))
    for w,ds in by.items(): print(' ',w, len(ds), 'ud avg/min/max', round(statistics.mean(ds),2), min(ds), max(ds))
    print(' sign->winner', trans)

print('\nNon-win samples: sim winner t90/t95/t100 h/u')
for r in rows:
    if r['winner']!='Blue':
        def fmt(t):
            if t not in r['states']: return ''
            h1,h2,u1,u2=r['states'][t]; return f'T{t} U{u1}-{u2} H{h1}-{h2}'
        print(r['sim'],r['winner'],fmt(85),fmt(90),fmt(95),fmt(100))
