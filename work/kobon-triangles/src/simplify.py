"""Resolve multiple points (and parallels) of an arrangement into a SIMPLE one,
greedily choosing, for each multiple point, the tiny shift of one of its lines
that keeps the most triangles (exact). Tries several shift sizes.

Usage: uv run python src/simplify.py in.json out.json
"""
import json
import sys
from fractions import Fraction as F
from itertools import combinations

from count import _meet, triangles, validate


def multipoints(L):
    pts = {}
    for i, j in combinations(range(len(L)), 2):
        X, Y, W = _meet(L[i], L[j])
        if W == 0:
            continue
        pts.setdefault((F(X, W), F(Y, W)), set()).update((i, j))
    return [sorted(s) for s in pts.values() if len(s) >= 3]


def parallels(L):
    return [(i, j) for i, j in combinations(range(len(L)), 2) if _meet(L[i], L[j])[2] == 0]


def shifted(L, i, dc):
    M = [list(l) for l in L]
    M[i] = [M[i][0], M[i][1], M[i][2] + dc]
    return M


def main():
    L = json.load(open(sys.argv[1]))["lines"]
    cur = len(triangles(L))
    print(f"start: {cur} triangles, {len(multipoints(L))} multiple points, {len(parallels(L))} parallel pairs")
    scale = max(abs(v) for l in L for v in l)
    while True:
        mps = multipoints(L)
        if not mps:
            break
        pt = mps[0]
        best = None
        for i in pt:
            for k in (10**-6, 10**-9, 10**-12):
                dc = max(1, int(scale * k))
                for sgn in (1, -1):
                    M = shifted(L, i, sgn * dc)
                    if len(multipoints(M)) >= len(mps):
                        continue
                    c = len(triangles(M))
                    if best is None or c > best[0]:
                        best = (c, M, i, sgn * dc)
        L = best[1]
        print(f"  resolved point on lines {pt} by shifting line {best[2]} by {best[3]}: {best[0]} triangles")
    for i, j in parallels(L):
        L[j] = [L[j][0] + 1, L[j][1], L[j][2]]
    validate(L)
    c = len(triangles(L))
    print(f"simple: {c} triangles, {len(multipoints(L))} multiple points, {len(parallels(L))} parallel pairs")
    json.dump({"lines": L}, open(sys.argv[2], "w"))


if __name__ == "__main__":
    main()
