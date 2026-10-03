"""Structural statistics of an arrangement (exact).

crossing points (distinct), multiplicities (triple points ...), parallel pairs,
bounded segments E, segments used by 0 / 1 / 2 triangles, and the identity
3T = (segments used once) + 2*(segments used twice).
"""
import json
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import combinations

from count import _meet, triangles


def stats(L):
    n = len(L)
    pts = {}
    par = 0
    on_line = {i: set() for i in range(n)}
    for i, j in combinations(range(n), 2):
        X, Y, W = _meet(L[i], L[j])
        if W == 0:
            par += 1
            continue
        p = (F(X, W), F(Y, W))
        pts.setdefault(p, set()).update((i, j))
        on_line[i].add(p)
        on_line[j].add(p)
    mult = Counter(len(s) for s in pts.values())
    tris = triangles(L)
    # bounded segments: consecutive distinct points along each line
    seg_use = Counter()
    segs = []
    for i in range(n):
        a, b, _ = L[i]
        key = (lambda p: p[0]) if b != 0 else (lambda p: p[1])
        ps = sorted(on_line[i], key=key)
        for u, v in zip(ps, ps[1:]):
            segs.append((i, u, v))
    seg_index = {}
    for i, u, v in segs:
        seg_index[(i, u, v)] = 0
    for t in tris:
        i, j, k = t
        verts = {}
        for (x, y) in ((i, j), (i, k), (j, k)):
            X, Y, W = _meet(L[x], L[y])
            verts[(x, y)] = (F(X, W), F(Y, W))
        for line, (e1, e2) in ((i, ((i, j), (i, k))), (j, ((i, j), (j, k))), (k, ((i, k), (j, k)))):
            u, v = verts[e1], verts[e2]
            a, b, _ = L[line]
            key = (lambda p: p[0]) if b != 0 else (lambda p: p[1])
            u, v = sorted((u, v), key=key)
            if (line, u, v) in seg_index:
                seg_index[(line, u, v)] += 1
    use = Counter(seg_index.values())
    return {
        "lines": n,
        "triangles": len(tris),
        "crossing_points": len(pts),
        "triple_points": mult.get(3, 0),
        "higher_multiplicity_points": sum(v for k, v in mult.items() if k > 3),
        "parallel_pairs": par,
        "bounded_segments": len(segs),
        "unused_segments": use.get(0, 0),
        "segments_used_once": use.get(1, 0),
        "segments_shared_by_2": use.get(2, 0),
        "tamura_bound": n * (n - 2) // 3,
        "max_coef_digits": max(len(str(abs(v))) for l in L for v in l),
        "identity_ok": 3 * len(tris) == use.get(1, 0) + 2 * use.get(2, 0),
    }


if __name__ == "__main__":
    for f in sys.argv[1:]:
        L = json.load(open(f))["lines"]
        print(f, json.dumps(stats(L)))
