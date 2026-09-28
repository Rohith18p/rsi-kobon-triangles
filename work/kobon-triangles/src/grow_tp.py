"""Add lines passing EXACTLY through an existing intersection point (creates a
triple point), with a small rational direction. Scored with the incremental
float scorer, verified exactly.

Usage: uv run python src/grow_tp.py base.json --add 1 --angles 360 --out added --tag X
"""

import argparse
import json
import math
import os
from fractions import Fraction
from itertools import combinations

import numpy as np
from numba import njit, prange

from count import _meet, triangles, validate
from lns import add_score, base_state, insert_best, int_line
from polish import to_td


@njit(parallel=True, cache=True)
def anchored_scores(t, d, T, px, py, ok, vx, vy, angles):
    nv, na = vx.shape[0], angles.shape[0]
    out = np.zeros((nv, na), dtype=np.int64)
    for iv in prange(nv):
        for ia in range(na):
            th = angles[ia]
            off = math.cos(th) * vx[iv] + math.sin(th) * vy[iv]
            out[iv, ia] = add_score(t, d, T, px, py, ok, th, off)
    return out


def rational_dir(th, max_den=2000):
    """Small integer direction (p, q) approximating (cos th, sin th) up to scale."""
    c, s = math.cos(th), math.sin(th)
    if abs(c) >= abs(s):
        r = Fraction(s / c).limit_denominator(max_den)
        return r.denominator, r.numerator  # (1, s/c)
    r = Fraction(c / s).limit_denominator(max_den)
    return r.numerator, r.denominator  # (c/s, 1)


def line_through(X, Y, W, th):
    """Integer line through the point (X/W, Y/W) with normal direction ~ (cos th, sin th)."""
    p, q = rational_dir(th)  # normal vector (p, q)
    a, b, c = p * W, q * W, -(p * X + q * Y)
    if W < 0:
        a, b, c = -a, -b, -c
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c)) or 1
    return [a // g, b // g, c // g]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--add", type=int, default=1)
    ap.add_argument("--angles", type=int, default=360)
    ap.add_argument("--top", type=int, default=40, help="exactly verify this many best float candidates")
    ap.add_argument("--out", default="added")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    L = json.load(open(args.base))["lines"]
    rng = np.random.default_rng(0)
    os.makedirs(args.out, exist_ok=True)
    for _ in range(args.add):
        n = len(L)
        t, d = to_td(L)
        T, px, py, ok = base_state(t, d)
        verts = []
        for i, j in combinations(range(n), 2):
            X, Y, W = _meet(L[i], L[j])
            if W != 0:
                verts.append((X, Y, W))
        # dedupe points already shared by several lines
        uniq = {}
        for X, Y, W in verts:
            f = (Fraction(X, W), Fraction(Y, W))
            uniq.setdefault(f, (X, Y, W))
        verts = list(uniq.values())
        vx = np.array([X / W for X, Y, W in verts])
        vy = np.array([Y / W for X, Y, W in verts])
        angles = np.linspace(0, math.pi, args.angles, endpoint=False) + rng.uniform(0, math.pi / args.angles)
        S = anchored_scores(t, d, T, px, py, ok, vx, vy, angles)
        # also the best free (non-anchored) insertion, for comparison
        fth, foff, fsc = insert_best(t, d, 540, rng)
        flat = np.argsort(S, axis=None)[::-1][: args.top]
        best = (-1, None, None)
        for idx in flat:
            iv, ia = np.unravel_index(idx, S.shape)
            X, Y, W = verts[iv]
            new = line_through(X, Y, W, angles[ia])
            cand = L + [new]
            try:
                validate(cand)
            except ValueError:
                continue
            ex = len(triangles(cand))
            if ex > best[0]:
                best = (ex, cand, int(S[iv, ia]))
        free = L + [int_line(fth, foff)]
        free_ex = len(triangles(free)) if not _dup(free) else -1
        print(f"n={n + 1}: anchored best exact={best[0]} (float {best[2]}), free exact={free_ex} (float {fsc})", flush=True)
        if free_ex >= best[0]:
            best = (free_ex, free, fsc)
        L = best[1]
        p = f"{args.out}/n{len(L)}_{best[0]}_{args.tag}tp.json"
        json.dump({"lines": L}, open(p, "w"))
        print(f"  saved {p}", flush=True)


def _dup(L):
    try:
        validate(L)
        return False
    except ValueError:
        return True


if __name__ == "__main__":
    main()
