#!/usr/bin/env python3
"""Edge ledger for an arrangement (hill format): n, #triple+ points k (by multiplicity),
#parallel pairs, bounded edges E, used edges, shared edges a2 (edge on 2 triangles),
unused bounded edges M, triangles T.  Identity: 3T = (E - M) + a2."""
import json, sys
from itertools import combinations
from fractions import Fraction
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from verify_independent import count_interior, _meet

def ledger(lines):
    lines = [tuple(l) for l in lines]; n = len(lines)
    pts = {}
    par = 0
    for i, j in combinations(range(n), 2):
        p = _meet(lines[i], lines[j])
        if p is None: par += 1; continue
        key = (Fraction(p[0], p[2]), Fraction(p[1], p[2]))
        pts.setdefault(key, set()).update((i, j))
    mult = {}
    for s in pts.values(): mult[len(s)] = mult.get(len(s), 0) + 1
    E = 0; edges = set()
    for L in range(n):
        on = sorted([k for k, s in pts.items() if L in s], key=lambda q: (q[0], q[1]) if lines[L][1] else (q[1], q[0]))
        E += max(len(on) - 1, 0)
        for a, b in zip(on, on[1:]): edges.add((L, a, b))
    tris = count_interior(lines, return_list=True)
    use = {}
    for i, j, k in tris:
        P = {}
        for a, b in ((i, j), (i, k), (j, k)):
            p = _meet(lines[a], lines[b]); P[(a, b)] = (Fraction(p[0], p[2]), Fraction(p[1], p[2]))
        for L, (u, v) in ((i, (P[(i, j)], P[(i, k)])), (j, (P[(i, j)], P[(j, k)])), (k, (P[(i, k)], P[(j, k)]))):
            key = (L,) + tuple(sorted([u, v], key=lambda q: (q[0], q[1]) if lines[L][1] else (q[1], q[0])))
            use[key] = use.get(key, 0) + 1
    a2 = sum(1 for v in use.values() if v == 2)
    used = len(use)
    return dict(n=n, T=len(tris), mult={m: c for m, c in sorted(mult.items()) if m > 2}, parallel_pairs=par,
                E=E, used=used, M=E - used, a2=a2)

if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f.rsplit('/', 1)[-1], json.dumps(ledger(json.load(open(f))["lines"])))
