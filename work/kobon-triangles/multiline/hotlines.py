#!/usr/bin/env python3
"""Per-line 'hotness' for choosing removal sets: unused bounded edges (owner line
and the two lines crossing at its endpoints), triple points, few triangles."""
import json, os, sys
from itertools import combinations
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'research', 'tools'))
from autolab_hill_eval import count_triangles, _normalize


def meet(l1, l2):
    a, b, c = l1; d, e, f = l2
    w = a * e - b * d
    if w == 0:
        return None
    return (Fraction(b * f - c * e, w), Fraction(c * d - a * f, w))


def hot(lines):
    L = [_normalize(tuple(l)) for l in lines]; n = len(L)
    P = {}
    on = [dict() for _ in range(n)]
    for i, j in combinations(range(n), 2):
        p = meet(L[i], L[j])
        if p is None:
            continue
        P.setdefault(p, set()).update((i, j))
    for p, s in P.items():
        for i in s:
            on[i][p] = s
    tris = count_triangles(L)
    used = set()
    deg = [0] * n
    for i, j, k in tris:
        for a in (i, j, k):
            deg[a] += 1
        pij, pik, pjk = meet(L[i], L[j]), meet(L[i], L[k]), meet(L[j], L[k])
        used.add((i, frozenset((pij, pik)))); used.add((j, frozenset((pij, pjk)))); used.add((k, frozenset((pik, pjk))))
    score = [0.0] * n
    unused = []
    for i in range(n):
        key = (lambda q: (q[0], q[1])) if L[i][1] else (lambda q: (q[1], q[0]))
        pts = sorted(on[i], key=key)
        for u, v in zip(pts, pts[1:]):
            if (i, frozenset((u, v))) not in used:
                ends = (on[i][u] | on[i][v]) - {i}
                unused.append((i, sorted(ends)))
                score[i] += 2
                for e in ends:
                    score[e] += 1
    for p, s in P.items():
        if len(s) > 2:
            for i in s:
                score[i] += 1
    for i in range(n):
        score[i] += max(0, (n - 2) - deg[i]) * 0.5
    return dict(score=score, deg=deg, unused=unused, T=len(tris))


if __name__ == '__main__':
    h = hot(json.load(open(sys.argv[1]))['lines'])
    order = sorted(range(len(h['score'])), key=lambda i: -h['score'][i])
    print('T', h['T'], 'unused', len(h['unused']))
    print([(i, h['score'][i], h['deg'][i]) for i in order])
