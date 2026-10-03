"""Local-search polish of an existing arrangement (dev tool, float guide + exact check).

Perturbs one line at a time (angle/offset, log-uniform step sizes), accepting
non-worsening moves. Each worker starts from the same seed arrangement.
Winners are rounded to integers and re-counted exactly before saving.

Usage: uv run python src/polish.py seed.json --workers 10 --minutes 10 --out polished
"""

import argparse
import json
import math
import os
import time
from multiprocessing import Pool

import numpy as np

from count import triangles, validate
from search import count_float, to_integer_lines


def to_td(lines):
    t, d = [], []
    for a, b, c in lines:
        r = math.hypot(a, b)
        t.append(math.atan2(b / r, a / r))
        d.append(-c / r)
    t, d = np.array(t), np.array(d)
    # recentre and rescale so intersection points are O(1)
    return t, d


def exact(t, d):
    best = (-1, None)
    for scale in (10**9, 10**12, 10**15, 10**18):
        lines = to_integer_lines(t, d, scale)
        try:
            validate(lines)
        except ValueError:
            continue
        c = len(triangles(lines))
        if c > best[0]:
            best = (c, lines)
        if best[0] >= 0 and scale >= 10**12:
            break
    return best


def work(args):
    seed, t, d, minutes, temp = args
    rng = np.random.default_rng(seed)
    n = len(t)
    scale = np.median(np.abs(d)) + 1.0
    cur = count_float(t, d)
    best, bt, bd = cur, t.copy(), d.copy()
    deadline = time.time() + minutes * 60
    it = 0
    while time.time() < deadline:
        it += 1
        i = rng.integers(n)
        nt, nd = t.copy(), d.copy()
        step = 10 ** rng.uniform(-7, -1.5)
        if rng.random() < 0.5:
            nt[i] += rng.normal(0, step)
        if rng.random() < 0.7:
            nd[i] += rng.normal(0, step * scale)
        c = count_float(nt, nd)
        if c >= cur or (temp > 0 and rng.random() < math.exp((c - cur) / temp)):
            t, d, cur = nt, nd, c
            if c > best:
                best, bt, bd = c, t.copy(), d.copy()
        if it % 5000 == 0 and cur < best:
            t, d, cur = bt.copy(), bd.copy(), best
    return best, bt, bd, seed, it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--minutes", type=float, default=10)
    ap.add_argument("--temp", type=float, default=0.3)
    ap.add_argument("--out", default="polished")
    args = ap.parse_args()
    lines = json.load(open(args.seed))["lines"]
    t, d = to_td(lines)
    start = count_float(t, d)
    n = len(lines)
    print(f"seed {args.seed}: n={n} float={start} exact={len(triangles(lines))}", flush=True)
    jobs = [(s, t, d, args.minutes, args.temp) for s in range(args.workers)]
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs)
    res.sort(key=lambda r: -r[0])
    os.makedirs(args.out, exist_ok=True)
    seen = set()
    for fl, bt, bd, s, it in res[:3]:
        if fl in seen:
            continue
        seen.add(fl)
        ex, L = exact(bt, bd)
        print(f"  worker={s} iters={it} float={fl} exact={ex}", flush=True)
        if L is not None:
            json.dump({"lines": L}, open(f"{args.out}/n{n}_{ex}_polish_w{s}.json", "w"))


if __name__ == "__main__":
    main()
