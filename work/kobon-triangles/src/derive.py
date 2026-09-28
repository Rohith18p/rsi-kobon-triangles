"""Derive arrangements for new n by deleting lines from a known arrangement (exact).

For each non-degenerate triple we record the set of lines crossing its interior.
After deleting a set S, triple (i,j,k) is a triangle iff i,j,k not in S and its
blockers are a subset of S. One exact O(n^4) pass then scores every deletion set.

Usage: uv run python src/derive.py <lines.csv|solution.json> --delete 1 2 --out DIR
"""

import argparse
import csv
import json
import os
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import gcd

from count import _meet, _side, triangles, validate


def load(path):
    if path.endswith(".json"):
        return [list(map(int, t)) for t in json.load(open(path))["lines"]]
    lines = []
    with open(path) as f:
        for row in csv.DictReader(f):
            m, b = Fraction(row["m"]), Fraction(row["b"])  # y = m x + b  ->  m x - y + b = 0
            den = m.denominator * b.denominator // gcd(m.denominator, b.denominator)
            a, bb, c = m * den, Fraction(-den), b * den
            t = [int(a), int(bb), int(c)]
            g = gcd(gcd(abs(t[0]), abs(t[1])), abs(t[2]))
            lines.append([v // g for v in t])
    return lines


def blocker_table(lines, cap=3):
    """Map triple -> tuple of blockers (only kept when fewer than `cap` blockers)."""
    n = len(lines)
    meet = {p: _meet(lines[p[0]], lines[p[1]]) for p in combinations(range(n), 2)}
    table = {}
    for i, j, k in combinations(range(n), 3):
        p, q, r = meet[i, j], meet[i, k], meet[j, k]
        if p[2] == 0 or q[2] == 0 or r[2] == 0 or _side(lines[k], p) == 0:
            continue
        bl = []
        for m in range(n):
            if m in (i, j, k):
                continue
            s = {_side(lines[m], p), _side(lines[m], q), _side(lines[m], r)}
            if 1 in s and -1 in s:
                bl.append(m)
                if len(bl) >= cap:
                    break
        if len(bl) < cap:
            table[i, j, k] = tuple(bl)
    return table


def score_deletions(table, n, k):
    base_loss = defaultdict(int)  # triangles lost because a deleted line is a side
    results = []
    by_blockers = defaultdict(int)
    for tri, bl in table.items():
        by_blockers[bl] += 1
    for S in combinations(range(n), k):
        s = set(S)
        cnt = 0
        for tri, bl in table.items():
            if s.isdisjoint(tri) and s.issuperset(bl):
                cnt += 1
        results.append((cnt, S))
    results.sort(reverse=True)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--delete", type=int, nargs="+", default=[1])
    ap.add_argument("--out", default="derived")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    lines = load(args.src)
    validate(lines)
    n = len(lines)
    table = blocker_table(lines, cap=max(args.delete) + 1)
    base = sum(1 for bl in table.values() if not bl)
    print(f"source n={n} triangles={base} (exact)")
    os.makedirs(args.out, exist_ok=True)
    for k in args.delete:
        res = score_deletions(table, n, k)
        best, S = res[0]
        sub = [l for idx, l in enumerate(lines) if idx not in S]
        exact = len(triangles(sub))  # independent re-count of the winner
        assert exact == best, (exact, best)
        path = f"{args.out}/n{n - k}_{best}_{args.tag}del{'-'.join(map(str, S))}.json"
        json.dump({"lines": sub}, open(path, "w"))
        top = ", ".join(f"{c}" for c, _ in res[:5])
        print(f"delete {k}: n={n - k} best={best} lines={S} (top5: {top}) -> {path}")


if __name__ == "__main__":
    main()
