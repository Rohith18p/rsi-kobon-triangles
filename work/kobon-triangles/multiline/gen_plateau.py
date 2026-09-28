#!/usr/bin/env python3
"""Jobs for plateau walk: for each plateau 470 not yet expanded, k2 pairs with its 2 poorest lines
and k3 {p1,p2,x}."""
import json, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hotlines import hot
done = set()
for f in glob.glob(HERE + '/logs/*.jsonl'):
    for x in open(f):
        r = json.loads(x); done.add(r['seed'])
jobs = []
for s in sorted(glob.glob(HERE + '/plateau/*.json')):
    if s in done: continue
    h = hot(json.load(open(s))['lines'])
    o = sorted(range(39), key=lambda i: (h['deg'][i], -h['score'][i])); p1, p2 = o[0], o[1]
    for x in range(39):
        for p in (p1, p2):
            if x != p: jobs.append(dict(seed=s, R=sorted({p, x}), m=2, tag='k2plat'))
    for x in range(39):
        if x not in (p1, p2): jobs.append(dict(seed=s, R=sorted([p1, p2, x]), m=3, tag='k3plat'))
seen = set(); out = []
for j in jobs:
    k = (j['seed'], tuple(j['R']), j['m'])
    if k not in seen: seen.add(k); out.append(j)
with open(sys.argv[1], 'w') as f:
    for j in out: f.write(json.dumps(j) + '\n')
print(len(out))
