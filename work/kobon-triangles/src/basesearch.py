"""Search for doubling bases: Y0 (y = 0) plus n lines y = m_i (x - a_i) with FIXED
intercepts a = tan(k pi / n) (k = ±1..±(n/2-1)) and two tiny ones ±eps, optimizing
only the slopes so that (a) Y0 touches n-1 triangles (every Y0 segment used) and
(b) the base has as many triangles as possible. Then apply Prop 3.1 exactly:
the result has 2n+1 lines and T(base) + n^2 triangles.

Usage: uv run python src/basesearch.py --n 30 --minutes 10 --workers 10
"""

import argparse
import json
import math
import os
import time
from fractions import Fraction as F
from multiprocessing import Pool

import numpy as np
from numba import njit

import doubling
from count import triangles, validate

EPS = 1e-12


@njit(cache=True)
def score(ms, avals):
    """Return (triangles, unused Y0 segments) for Y0 + lines y = m (x - a)."""
    n = ms.shape[0] + 1
    A = np.zeros(n); B = np.zeros(n); C = np.zeros(n)  # A x + B y + C = 0, normalized
    A[0], B[0], C[0] = 0.0, 1.0, 0.0
    for i in range(1, n):
        m = ms[i - 1]; a = avals[i - 1]
        r = math.sqrt(m * m + 1.0)
        A[i], B[i], C[i] = m / r, -1.0 / r, -m * a / r
    px = np.zeros((n, n)); py = np.zeros((n, n)); ok = np.zeros((n, n), dtype=np.bool_)
    for i in range(n):
        for j in range(i + 1, n):
            det = A[i] * B[j] - A[j] * B[i]
            if abs(det) > 1e-14:
                px[i, j] = (B[i] * C[j] - B[j] * C[i]) / det
                py[i, j] = (C[i] * A[j] - C[j] * A[i]) / det
                ok[i, j] = True
    # Y0 segments: sorted intercepts
    order = np.argsort(avals)
    used = np.zeros(n - 2, dtype=np.bool_)
    cnt = 0
    for i in range(n):
        for j in range(i + 1, n):
            if not ok[i, j]:
                continue
            for k in range(j + 1, n):
                if not (ok[i, k] and ok[j, k]):
                    continue
                x1, y1, x2, y2, x3, y3 = px[i, j], py[i, j], px[i, k], py[i, k], px[j, k], py[j, k]
                if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-18:
                    continue
                good = True
                for q in range(n):
                    if q == i or q == j or q == k:
                        continue
                    s1 = A[q] * x1 + B[q] * y1 + C[q]
                    s2 = A[q] * x2 + B[q] * y2 + C[q]
                    s3 = A[q] * x3 + B[q] * y3 + C[q]
                    if ((s1 > EPS) or (s2 > EPS) or (s3 > EPS)) and ((s1 < -EPS) or (s2 < -EPS) or (s3 < -EPS)):
                        good = False
                        break
                if good:
                    cnt += 1
                    if i == 0:  # triangle with a side on Y0 between intercepts of lines j, k
                        lo = min(avals[j - 1], avals[k - 1])
                        for s in range(n - 2):
                            if avals[order[s]] == lo:
                                used[s] = True
                                break
    unused = 0
    for s in range(n - 2):
        if not used[s]:
            unused += 1
    return cnt, unused


def intercepts(n, eps_frac):
    ks = [k for k in range(-(n // 2 - 1), n // 2) if k != 0]
    a = [math.tan(k * math.pi / n) for k in ks]
    eps = eps_frac / n
    return np.array(a + [-eps, eps])


def objective(ms, avals, w):
    c, u = score(ms, avals)
    return c - w * u, c, u


def anneal(args):
    seed, n, minutes, eps_frac, init = args
    rng = np.random.default_rng(seed)
    avals = intercepts(n, eps_frac)
    if init is None:
        # alternating-sign slopes of random magnitude, as in the published bases
        ms = rng.choice([-1.0, 1.0], n) * np.exp(rng.normal(1.0, 1.2, n))
    else:
        ms = np.array(init)
    w = 3.0
    cur, c, u = objective(ms, avals, w)
    best = (cur, c, u, ms.copy())
    deadline = time.time() + minutes * 60
    it = 0
    while time.time() < deadline:
        it += 1
        frac = (deadline - time.time()) / (minutes * 60)
        T = 2.0 * frac + 0.05
        i = rng.integers(n)
        cand = ms.copy()
        if rng.random() < 0.05:
            cand[i] = -cand[i]
        else:
            cand[i] *= math.exp(rng.normal(0, 0.5 * frac + 0.01))
            cand[i] = math.copysign(min(max(abs(cand[i]), 1e-3), 1e3), cand[i])
        v, cc, uu = objective(cand, avals, w)
        if v >= cur or rng.random() < math.exp((v - cur) / T):
            ms, cur = cand, v
            if uu == 0 and (best[2] != 0 or cc > best[1]):
                best = (v, cc, uu, ms.copy())
            elif best[2] != 0 and v > best[0]:
                best = (v, cc, uu, ms.copy())
    return best[1], best[2], best[3].tolist(), seed, it


def build(n, ms, eps_frac, delta_exp=4, eps2_exp=2):
    avals = intercepts(n, eps_frac)
    L = [(F(m).limit_denominator(10**12), F(a).limit_denominator(10**15)) for m, a in zip(ms, avals)]
    doubling.EPS2 = eps2_exp
    base_int = doubling.to_int_lines(L)
    B = doubling.double(L, delta_exp)
    return base_int, doubling.to_int_lines(B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True, help="number of non-Y0 lines (even)")
    ap.add_argument("--minutes", type=float, default=10)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--eps-frac", type=float, default=0.3)
    ap.add_argument("--out", default="bases")
    args = ap.parse_args()
    n = args.n
    assert n % 2 == 0
    score(np.ones(4), intercepts(4, 0.3))
    jobs = [(s + 1000 * n, n, args.minutes, args.eps_frac, None) for s in range(args.workers)]
    with Pool(args.workers) as pool:
        res = pool.map(anneal, jobs)
    res.sort(key=lambda r: (r[1] == 0, r[0]), reverse=True)
    os.makedirs(args.out, exist_ok=True)
    for c, u, ms, seed, it in res[:3]:
        print(f"base n+1={n + 1}: float triangles={c} unusedY0={u} seed={seed} iters={it}", flush=True)
        if u != 0:
            continue
        if ms[-1] == ms[-2]:
            print("  special lines parallel; skipping")
            continue
        json.dump({"slopes": ms, "n": n, "eps_frac": args.eps_frac}, open(f"{args.out}/slopes{n + 1}_{c}_s{seed}.json", "w"))
        base, big = build(n, ms, args.eps_frac)
        cb = len(triangles(base))
        try:
            validate(big)
            cB = len(triangles(big))
        except ValueError as e:
            print("  doubled invalid:", e)
            continue
        print(f"  exact base={cb}  doubled n={len(big)} triangles={cB} (expected {cb + n * n})", flush=True)
        json.dump({"lines": base, "slopes": ms}, open(f"{args.out}/base{n + 1}_{cb}_s{seed}.json", "w"))
        json.dump({"lines": big}, open(f"{args.out}/n{len(big)}_{cB}_base{n + 1}.json", "w"))


if __name__ == "__main__":
    main()
