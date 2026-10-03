#!/usr/bin/env python3
"""Prioritised job list: k2 with poor lines, k3/k4 around poor+hot lines, k+1 on 38 bases, rest of k2."""
import json, glob, os, sys, random
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hotlines import hot
P = os.path.dirname(HERE) + '/'  # the kobon-triangles folder
seeds = sorted(glob.glob(P + 'added/g38/n39_470_*.json')) + [P + 'added/n39_469_u38-grow.json']
done = set()
for f in glob.glob(HERE + '/logs/*.jsonl'):
    for x in open(f):
        r = json.loads(x); done.add((r['seed'], tuple(r['R']), r['m']))
H = {s: hot(json.load(open(s))['lines']) for s in seeds}
def order(s):
    h = H[s]; return sorted(range(39), key=lambda i: (h['deg'][i], -h['score'][i]))
A, B3, C4, REST = [], [], [], []
for s in seeds:
    o = order(s); p1, p2 = o[0], o[1]; hotl = [i for i in o[2:12]]
    for x in range(39):
        for p in (p1, p2):
            if x != p: A.append(dict(seed=s, R=sorted({p, x}), m=2, tag='k2'))
    for x in range(39):
        if x not in (p1, p2): B3.append(dict(seed=s, R=sorted([p1, p2, x]), m=3, tag='k3'))
    for x, y in combinations(hotl, 2):
        B3.append(dict(seed=s, R=sorted([p1, x, y]), m=3, tag='k3'))
        C4.append(dict(seed=s, R=sorted([p1, p2, x, y]), m=4, tag='k4'))
    for x, y in combinations(range(39), 2):
        REST.append(dict(seed=s, R=[x, y], m=2, tag='k2'))
# k+1: 38/450 bases, remove 1 of the 3 lowest-degree lines + 3 random, insert 2
D = []
random.seed(1)
bases = sorted(glob.glob(P + 'derived/g38/*.json'))
for b in bases:
    h = hot(json.load(open(b))['lines'])
    o = sorted(range(38), key=lambda i: (h['deg'][i], -h['score'][i]))
    for x in o[:3] + random.sample(o[3:], 3):
        D.append(dict(seed=b, R=[x], m=2, tag='k1p1'))
random.shuffle(REST)
def uniq(js):
    out, seen = [], set()
    for j in js:
        k = (j['seed'], tuple(j['R']), j['m'])
        if k in seen or k in done: continue
        seen.add(k); out.append(j)
    return out
jobs = uniq(A + B3 + C4 + D + REST)
json.dump({'A': len(uniq(A)), 'B3': len(uniq(B3)), 'C4': len(uniq(C4)), 'D': len(uniq(D))}, sys.stdout); print()
with open(HERE + '/jobs_main.jsonl', 'w') as f:
    for j in jobs: f.write(json.dumps(j) + '\n')
print(len(jobs))
