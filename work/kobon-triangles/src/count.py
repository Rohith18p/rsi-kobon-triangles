"""Exact Kobon triangle counter (dev numbers only; official scores come from `hills eval`).

A triple of lines forms a counted triangle iff the three lines are pairwise
non-parallel, not concurrent, and no other line has triangle vertices strictly
on both of its sides (i.e. no line crosses the triangle's interior).

Usage: uv run python src/count.py path/to/solution.json
"""

import json
import sys
from itertools import combinations


def _meet(l1, l2):
    """Intersection of two lines as homogeneous integers (X, Y, W), W != 0 unless parallel."""
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    w = a1 * b2 - a2 * b1
    x = b1 * c2 - b2 * c1
    y = c1 * a2 - c2 * a1
    return x, y, w


def _side(line, p):
    """Sign of the line evaluated at homogeneous point p, normalized so W > 0."""
    a, b, c = line
    x, y, w = p
    v = a * x + b * y + c * w
    if w < 0:
        v = -v
    return (v > 0) - (v < 0)


def triangles(lines):
    """Return the list of index triples forming bounded triangular faces."""
    n = len(lines)
    meet = {}
    for i, j in combinations(range(n), 2):
        meet[i, j] = _meet(lines[i], lines[j])
    found = []
    for i, j, k in combinations(range(n), 3):
        p, q, r = meet[i, j], meet[i, k], meet[j, k]
        if p[2] == 0 or q[2] == 0 or r[2] == 0:
            continue  # a parallel pair: no bounded triangle
        if _side(lines[k], p) == 0:
            continue  # concurrent: degenerate
        ok = True
        for m in range(n):
            if m in (i, j, k):
                continue
            s = {_side(lines[m], p), _side(lines[m], q), _side(lines[m], r)}
            if 1 in s and -1 in s:
                ok = False
                break
        if ok:
            found.append((i, j, k))
    return found


def validate(lines):
    for t in lines:
        if len(t) != 3 or not all(isinstance(v, int) and not isinstance(v, bool) for v in t):
            raise ValueError(f"not an integer triple: {t}")
        if max(abs(v) for v in t) > 10**30:
            raise ValueError(f"coefficient magnitude exceeds 10^30: {t}")
        if t[0] == 0 and t[1] == 0:
            raise ValueError(f"degenerate line: {t}")
    for (i, s), (j, t) in combinations(enumerate(lines), 2):
        if all(s[a] * t[b] == s[b] * t[a] for a, b in ((0, 1), (0, 2), (1, 2))):
            raise ValueError(f"lines {i} and {j} are the same line")


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    lines = data["lines"]
    validate(lines)
    print(f"n={len(lines)} triangles={len(triangles(lines))}")
