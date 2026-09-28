#!/usr/bin/env python3
"""Independent exact Kobon counter (does not share code with the hill evaluator).

A triple of lines {i,j,k} is counted iff the three lines pairwise intersect in three
distinct points (non-degenerate triangle) and no other line meets the OPEN triangle,
i.e. no other line has vertices strictly on both sides. O(n^4), exact integers.

Usage: python3 verify_independent.py solution.json   (hill format, a*x+b*y+c=0)
"""
import json
import sys
from itertools import combinations


def _meet(l1, l2):
    a, b, c = l1
    d, e, f = l2
    w = a * e - b * d
    if w == 0:
        return None
    return (b * f - c * e, c * d - a * f, w)  # homogeneous (X, Y, W), point = (X/W, Y/W)


def _side(line, p):
    a, b, c = line
    X, Y, W = p
    v = a * X + b * Y + c * W
    s = (v > 0) - (v < 0)
    return s if W > 0 else -s


def count_interior(lines, return_list=False):
    lines = [tuple(l) for l in lines]
    n = len(lines)
    tris = []
    for i, j, k in combinations(range(n), 3):
        p, q, r = _meet(lines[i], lines[j]), _meet(lines[i], lines[k]), _meet(lines[j], lines[k])
        if p is None or q is None or r is None:
            continue
        # concurrent => degenerate
        if _side(lines[k], p) == 0:
            continue
        ok = True
        for m in range(n):
            if m in (i, j, k):
                continue
            s = {_side(lines[m], p), _side(lines[m], q), _side(lines[m], r)}
            if 1 in s and -1 in s:
                ok = False
                break
        if ok:
            tris.append((i, j, k))
    return tris if return_list else len(tris)


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    print(count_interior(data["lines"]))
