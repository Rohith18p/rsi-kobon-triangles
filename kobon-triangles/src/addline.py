"""Greedily add lines to an arrangement: grid-search (angle, offset) for the new
line that maximizes the triangle count, refine locally, repeat (dev tool).

Usage: uv run python src/addline.py base.json --add 2 --out added
"""

import argparse
import json
import math
import os

import numpy as np
from numba import njit, prange

from count import triangles, validate
from polish import to_td, exact
from search import count_float


@njit(cache=True)
def _points(t, d):
    n = t.shape[0]
    a, b = np.cos(t), np.sin(t)
    xs, ys = [], []
    for i in range(n):
        for j in range(i + 1, n):
            det = a[i] * b[j] - a[j] * b[i]
            if abs(det) > 1e-12:
                xs.append((d[i] * b[j] - d[j] * b[i]) / det)
                ys.append((a[i] * d[j] - a[j] * d[i]) / det)
    return np.array(xs), np.array(ys)


@njit(parallel=True, cache=True)
def grid_scores(t, d, angles, offsets_per_angle):
    na = angles.shape[0]
    no = offsets_per_angle.shape[1]
    out = np.zeros((na, no), dtype=np.int64)
    n = t.shape[0]
    for ia in prange(na):
        tt = np.empty(n + 1)
        dd = np.empty(n + 1)
        tt[:n] = t
        dd[:n] = d
        tt[n] = angles[ia]
        for io in range(no):
            dd[n] = offsets_per_angle[ia, io]
            out[ia, io] = count_float(tt, dd)
    return out


def best_new_line(t, d, n_angles=360, n_offsets=None):
    xs, ys = _points(t, d)
    angles = np.linspace(0, math.pi, n_angles, endpoint=False) + np.random.uniform(0, math.pi / n_angles)
    offs = []
    for th in angles:
        proj = np.sort(np.cos(th) * xs + np.sin(th) * ys)
        # candidate offsets: midpoints between consecutive projected vertices
        mids = (proj[1:] + proj[:-1]) / 2
        if n_offsets is not None and len(mids) > n_offsets:
            mids = mids[np.linspace(0, len(mids) - 1, n_offsets).astype(int)]
        offs.append(mids)
    width = max(len(o) for o in offs)
    grid = np.array([np.pad(o, (0, width - len(o)), mode="edge") for o in offs])
    scores = grid_scores(t, d, angles, grid)
    ia, io = np.unravel_index(np.argmax(scores), scores.shape)
    return angles[ia], grid[ia, io], scores[ia, io]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--add", type=int, default=1)
    ap.add_argument("--angles", type=int, default=720)
    ap.add_argument("--out", default="added")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    lines = json.load(open(args.base))["lines"]
    t, d = to_td(lines)
    print(f"base n={len(t)} float={count_float(t, d)}", flush=True)
    os.makedirs(args.out, exist_ok=True)
    L = [list(l) for l in lines]  # keep existing lines exact (preserves triple points)
    for step in range(args.add):
        th, off, sc = best_new_line(t, d, args.angles)
        t, d = np.append(t, th), np.append(d, off)
        S = 10**12
        new = [round(math.cos(th) * S), round(math.sin(th) * S), -round(off * S)]
        g = math.gcd(math.gcd(abs(new[0]), abs(new[1])), abs(new[2])) or 1
        L.append([v // g for v in new])
        validate(L)
        ex = len(triangles(L))
        print(f"  +1 -> n={len(t)} float={sc} exact={ex}", flush=True)
        json.dump({"lines": L}, open(f"{args.out}/n{len(t)}_{ex}_{args.tag}add.json", "w"))


if __name__ == "__main__":
    main()
