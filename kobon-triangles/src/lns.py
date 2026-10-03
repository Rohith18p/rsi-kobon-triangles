"""Large-neighbourhood search: repeatedly remove one line and re-insert the best
possible line (grid over angle x offset, scored incrementally), accepting
non-worsening moves. Existing lines stay exact integers; only re-inserted lines
are rounded. Every accepted state is re-counted exactly before saving.

Usage: uv run python src/lns.py seed.json --minutes 30 --out lns [--angles 540]
"""

import argparse
import json
import math
import os
import time

import numpy as np
from numba import njit, prange

from count import triangles, validate
from polish import to_td

EPS = 1e-9


@njit(cache=True)
def base_state(t, d):
    """Vertices of all bounded triangles of the arrangement, and pair intersections."""
    n = t.shape[0]
    a, b = np.cos(t), np.sin(t)
    px = np.zeros((n, n)); py = np.zeros((n, n)); ok = np.zeros((n, n), dtype=np.bool_)
    for i in range(n):
        for j in range(i + 1, n):
            det = a[i] * b[j] - a[j] * b[i]
            if abs(det) > 1e-12:
                px[i, j] = px[j, i] = (d[i] * b[j] - d[j] * b[i]) / det
                py[i, j] = py[j, i] = (a[i] * d[j] - a[j] * d[i]) / det
                ok[i, j] = ok[j, i] = True
    tri = []
    for i in range(n):
        for j in range(i + 1, n):
            if not ok[i, j]:
                continue
            for k in range(j + 1, n):
                if not (ok[i, k] and ok[j, k]):
                    continue
                x1, y1, x2, y2, x3, y3 = px[i, j], py[i, j], px[i, k], py[i, k], px[j, k], py[j, k]
                if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-12:
                    continue
                good = True
                for m in range(n):
                    if m == i or m == j or m == k:
                        continue
                    s1 = a[m] * x1 + b[m] * y1 - d[m]
                    s2 = a[m] * x2 + b[m] * y2 - d[m]
                    s3 = a[m] * x3 + b[m] * y3 - d[m]
                    if ((s1 > EPS) or (s2 > EPS) or (s3 > EPS)) and ((s1 < -EPS) or (s2 < -EPS) or (s3 < -EPS)):
                        good = False
                        break
                if good:
                    tri.append((x1, y1, x2, y2, x3, y3))
    T = np.zeros((len(tri), 6))
    for q in range(len(tri)):
        for r in range(6):
            T[q, r] = tri[q][r]
    return T, px, py, ok


@njit(cache=True)
def add_score(t, d, T, px, py, ok, tn, dn):
    """Triangle count after adding line (tn, dn) to the arrangement (t, d)."""
    n = t.shape[0]
    a, b = np.cos(t), np.sin(t)
    an, bn = math.cos(tn), math.sin(tn)
    cnt = 0
    for q in range(T.shape[0]):  # surviving triangles
        s1 = an * T[q, 0] + bn * T[q, 1] - dn
        s2 = an * T[q, 2] + bn * T[q, 3] - dn
        s3 = an * T[q, 4] + bn * T[q, 5] - dn
        if not (((s1 > EPS) or (s2 > EPS) or (s3 > EPS)) and ((s1 < -EPS) or (s2 < -EPS) or (s3 < -EPS))):
            cnt += 1
    qx = np.zeros(n); qy = np.zeros(n); qok = np.zeros(n, dtype=np.bool_)
    for i in range(n):
        det = a[i] * bn - an * b[i]
        if abs(det) > 1e-12:
            qx[i] = (d[i] * bn - dn * b[i]) / det
            qy[i] = (a[i] * dn - an * d[i]) / det
            qok[i] = True
    for i in range(n):  # new triangles using the new line
        if not qok[i]:
            continue
        for j in range(i + 1, n):
            if not (qok[j] and ok[i, j]):
                continue
            x1, y1, x2, y2, x3, y3 = px[i, j], py[i, j], qx[i], qy[i], qx[j], qy[j]
            if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-12:
                continue
            good = True
            for m in range(n):
                if m == i or m == j:
                    continue
                s1 = a[m] * x1 + b[m] * y1 - d[m]
                s2 = a[m] * x2 + b[m] * y2 - d[m]
                s3 = a[m] * x3 + b[m] * y3 - d[m]
                if ((s1 > EPS) or (s2 > EPS) or (s3 > EPS)) and ((s1 < -EPS) or (s2 < -EPS) or (s3 < -EPS)):
                    good = False
                    break
            if good:
                cnt += 1
    return cnt


@njit(parallel=True, cache=True)
def best_insert(t, d, T, px, py, ok, angles, xs, ys):
    na = angles.shape[0]
    best_c = np.zeros(na, dtype=np.int64)
    best_o = np.zeros(na)
    for ia in prange(na):
        th = angles[ia]
        proj = np.sort(math.cos(th) * xs + math.sin(th) * ys)
        bc, bo = -1, 0.0
        for k in range(proj.shape[0] - 1):
            if proj[k + 1] - proj[k] < 1e-10:
                continue
            o = 0.5 * (proj[k] + proj[k + 1])
            c = add_score(t, d, T, px, py, ok, th, o)
            if c > bc:
                bc, bo = c, o
        best_c[ia] = bc
        best_o[ia] = bo
    return best_c, best_o


def insert_best(t, d, n_angles, rng):
    T, px, py, ok = base_state(t, d)
    iu = np.triu_indices(len(t), 1)
    m = ok[iu]
    xs, ys = px[iu][m], py[iu][m]
    angles = np.linspace(0, math.pi, n_angles, endpoint=False) + rng.uniform(0, math.pi / n_angles)
    bc, bo = best_insert(t, d, T, px, py, ok, angles, xs, ys)
    ia = int(np.argmax(bc))
    return angles[ia], bo[ia], int(bc[ia])


def int_line(th, off, S=10**12):
    v = [round(math.cos(th) * S), round(math.sin(th) * S), -round(off * S)]
    g = math.gcd(math.gcd(abs(v[0]), abs(v[1])), abs(v[2])) or 1
    return [x // g for x in v]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--minutes", type=float, default=30)
    ap.add_argument("--angles", type=int, default=540)
    ap.add_argument("--out", default="lns")
    ap.add_argument("--tag", default="")
    ap.add_argument("--rseed", type=int, default=0)
    ap.add_argument("--k", type=int, default=1, help="lines removed and re-inserted per move")
    args = ap.parse_args()
    rng = np.random.default_rng(args.rseed)
    L = json.load(open(args.seed))["lines"]
    n = len(L)
    cur = len(triangles(L))
    print(f"seed n={n} exact={cur}", flush=True)
    os.makedirs(args.out, exist_ok=True)
    deadline = time.time() + args.minutes * 60
    order = list(rng.permutation(n))
    tries = 0
    while time.time() < deadline:
        if not order:
            order = list(rng.permutation(n))
        i = order.pop()
        tries += 1
        drop = {i}
        while len(drop) < args.k:
            drop.add(int(rng.integers(n)))
        rest = [l for k, l in enumerate(L) if k not in drop]
        for _ in range(args.k):
            t, d = to_td(rest)
            th, off, fc = insert_best(t, d, args.angles, rng)
            rest = rest + [int_line(th, off)]
        if fc < cur:
            continue
        cand = rest
        try:
            validate(cand)
        except ValueError:
            continue
        ex = len(triangles(cand)) if fc > cur else fc  # exact check on every improvement
        if ex >= cur:
            improved = ex > cur
            L, cur = cand, ex
            if improved:
                path = f"{args.out}/n{n}_{cur}_{args.tag}lns.json"
                json.dump({"lines": L}, open(path, "w"))
                print(f"  [{time.strftime('%H:%M:%S')}] try {tries}: replaced line {i} -> exact {cur}  saved {path}", flush=True)
    cur = len(triangles(L))
    json.dump({"lines": L}, open(f"{args.out}/n{n}_{cur}_{args.tag}lns_final.json", "w"))
    print(f"done n={n} exact={cur} tries={tries}", flush=True)


if __name__ == "__main__":
    main()
