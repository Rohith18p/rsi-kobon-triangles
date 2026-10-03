"""Simulated-annealing search for Kobon arrangements (dev tool).

Lines are parametrized as x*cos(t) + y*sin(t) = d. The float counter is only a
guide; every candidate is converted to exact integers and re-counted exactly
before it is saved.

Usage:
  uv run python src/search.py --n 18 --workers 10 --minutes 20 [--sym 3] [--init file.json]
"""

import argparse
import json
import math
import os
import time
from fractions import Fraction
from multiprocessing import Pool

import numpy as np
from numba import njit

from count import triangles, validate

EPS = 1e-9


@njit(cache=True)
def count_float(t, d):
    n = t.shape[0]
    a = np.cos(t)
    b = np.sin(t)
    # intersection points of every pair
    px = np.zeros((n, n))
    py = np.zeros((n, n))
    ok = np.zeros((n, n), dtype=np.bool_)
    for i in range(n):
        for j in range(i + 1, n):
            det = a[i] * b[j] - a[j] * b[i]
            if abs(det) > 1e-12:
                x = (d[i] * b[j] - d[j] * b[i]) / det
                y = (a[i] * d[j] - a[j] * d[i]) / det
                px[i, j] = x
                py[i, j] = y
                ok[i, j] = True
    cnt = 0
    for i in range(n):
        for j in range(i + 1, n):
            if not ok[i, j]:
                continue
            for k in range(j + 1, n):
                if not (ok[i, k] and ok[j, k]):
                    continue
                x1, y1 = px[i, j], py[i, j]
                x2, y2 = px[i, k], py[i, k]
                x3, y3 = px[j, k], py[j, k]
                area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
                if abs(area) < 1e-12:
                    continue
                good = True
                for m in range(n):
                    if m == i or m == j or m == k:
                        continue
                    s1 = a[m] * x1 + b[m] * y1 - d[m]
                    s2 = a[m] * x2 + b[m] * y2 - d[m]
                    s3 = a[m] * x3 + b[m] * y3 - d[m]
                    pos = (s1 > EPS) or (s2 > EPS) or (s3 > EPS)
                    neg = (s1 < -EPS) or (s2 < -EPS) or (s3 < -EPS)
                    if pos and neg:
                        good = False
                        break
                if good:
                    cnt += 1
    return cnt


def expand(params, n, sym):
    """Map free parameters to n lines, applying `sym`-fold rotational symmetry."""
    if sym == 1:
        return params[:n], params[n:]
    k = n // sym
    t0, d0 = params[:k], params[k:]
    t = np.concatenate([t0 + 2 * math.pi * r / sym for r in range(sym)])
    d = np.tile(d0, sym)
    return t, d


def to_integer_lines(t, d, scale):
    lines = []
    for ti, di in zip(t, d):
        a = round(math.cos(ti) * scale)
        b = round(math.sin(ti) * scale)
        c = -round(di * scale)
        g = math.gcd(math.gcd(abs(a), abs(b)), abs(c)) or 1
        lines.append([a // g, b // g, c // g])
    return lines


def exact_count(t, d):
    """Return (count, lines) for the best exact rounding we can find."""
    best = (-1, None)
    for scale in (10**6, 10**9, 10**12, 10**15):
        lines = to_integer_lines(t, d, scale)
        try:
            validate(lines)
        except ValueError:
            continue
        c = len(triangles(lines))
        if c > best[0]:
            best = (c, lines)
    return best


def anneal(args):
    seed, n, sym, minutes, init, T0 = args
    rng = np.random.default_rng(seed)
    k = n // sym
    if init is not None:
        params = np.array(init, dtype=float)
    else:
        params = np.concatenate([rng.uniform(0, math.pi if sym == 1 else 2 * math.pi, k),
                                 rng.normal(0, 1, k)])
    cur = count_float(*expand(params, n, sym))
    best, best_params = cur, params.copy()
    deadline = time.time() + minutes * 60
    it = 0
    while time.time() < deadline:
        it += 1
        frac = min(1.0, (deadline - time.time()) / (minutes * 60))
        T = T0 * frac + 1e-3
        step = 0.3 * frac + 1e-3
        cand = params.copy()
        idx = rng.integers(0, 2 * k)
        cand[idx] += rng.normal(0, step)
        if rng.random() < 0.1:  # occasionally move a whole line
            j = rng.integers(0, k)
            cand[j] += rng.normal(0, step)
            cand[k + j] += rng.normal(0, step)
        c = count_float(*expand(cand, n, sym))
        if c >= cur or rng.random() < math.exp((c - cur) / T):
            params, cur = cand, c
            if c > best:
                best, best_params = c, cand.copy()
        # periodic restart from best to intensify
        if it % 200000 == 0:
            params, cur = best_params.copy(), best
    return best, best_params.tolist(), seed, it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--sym", type=int, default=1)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--minutes", type=float, default=10)
    ap.add_argument("--T0", type=float, default=1.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="candidates")
    args = ap.parse_args()
    assert args.n % args.sym == 0
    count_float(np.zeros(3), np.zeros(3))  # compile once before forking
    jobs = [(args.seed + w, args.n, args.sym, args.minutes, None, args.T0) for w in range(args.workers)]
    os.makedirs(args.out, exist_ok=True)
    with Pool(args.workers) as pool:
        results = pool.map(anneal, jobs)
    results.sort(key=lambda r: -r[0])
    for fl, params, seed, it in results:
        t, d = expand(np.array(params), args.n, args.sym)
        ex, lines = exact_count(t, d)
        print(f"seed={seed} iters={it} float={fl} exact={ex}", flush=True)
        if lines is not None:
            path = f"{args.out}/n{args.n}_s{args.sym}_seed{seed}_{ex}.json"
            json.dump({"lines": lines}, open(path, "w"))


if __name__ == "__main__":
    main()
