"""Greedy exact deletion: repeatedly remove the line whose removal keeps the most
triangles, saving the arrangement at every size down to --min-n.

Usage: uv run python src/peel.py source.json --min-n 51 --out peeled --tag X
"""

import argparse
import json
import os
from collections import Counter

from count import triangles, validate
from derive import blocker_table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--min-n", type=int, required=True)
    ap.add_argument("--out", default="peeled")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    L = json.load(open(args.src))["lines"]
    os.makedirs(args.out, exist_ok=True)
    while len(L) > args.min_n:
        n = len(L)
        table = blocker_table(L, cap=2)
        base = sum(1 for bl in table.values() if not bl)
        lost = Counter()
        gain = Counter()
        for tri, bl in table.items():
            if not bl:
                for v in tri:
                    lost[v] += 1
            elif len(bl) == 1:
                gain[bl[0]] += 1
        # a triangle blocked only by line r becomes a triangle unless r is one of its sides (impossible)
        scores = {r: base - lost[r] + gain[r] for r in range(n)}
        r = max(scores, key=scores.get)
        L = [l for k, l in enumerate(L) if k != r]
        validate(L)
        c = len(triangles(L))
        assert c == scores[r], (c, scores[r])
        p = f"{args.out}/n{len(L)}_{c}_{args.tag}peel.json"
        json.dump({"lines": L}, open(p, "w"))
        print(f"n={len(L)} triangles={c} (removed line {r}) -> {p}", flush=True)


if __name__ == "__main__":
    main()
