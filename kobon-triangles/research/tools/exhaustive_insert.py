#!/usr/bin/env python3
"""Exhaustive single-line insertion (dual-vertex enumeration).

For a base arrangement B (hill format), every combinatorial way of adding one
straight line is represented by a cell / edge / vertex of the dual arrangement of
B's vertices.  Every such face is incident to a dual vertex, i.e. to the line
through two base vertices v, w.  For every pair (v, w) we therefore score
  * the line vw itself                           (passes through v and w),
  * vw rotated slightly about v (w above/below)  (passes through v only), same about w,
  * the 4 generic perturbations (signs of v, w in {+,-}^2),
so the maximum over all candidates is the exact optimum of "B + one line"
(up to floating-point tolerance; the winners are re-verified exactly).

Modes:
  insert  base.json              best line to add to base (n -> n+1)
  lns     arr.json               for each line i: remove it, best re-insertion
Usage: uv run python research/tools/exhaustive_insert.py insert base.json [--top 5] [--out dir]
"""
import argparse, json, math, os, sys, time
import numpy as np
from numba import njit, prange

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from autolab_hill_eval import count_triangles, _normalize  # exact counter

EPS = 1e-14


def to_abd(lines):
    L = np.array([[float(a), float(b), float(c)] for a, b, c in lines])
    nr = np.hypot(L[:, 0], L[:, 1])
    return L[:, 0] / nr, L[:, 1] / nr, -L[:, 2] / nr  # a x + b y = d


@njit(cache=True)
def base_state(a, b, d, eps):
    n = a.shape[0]
    px = np.zeros((n, n)); py = np.zeros((n, n)); ok = np.zeros((n, n), dtype=np.bool_)
    for i in range(n):
        for j in range(i + 1, n):
            det = a[i] * b[j] - a[j] * b[i]
            if abs(det) > 1e-14:
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
                if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-30:
                    continue
                good = True
                for m in range(n):
                    if m == i or m == j or m == k:
                        continue
                    s1 = a[m] * x1 + b[m] * y1 - d[m]
                    s2 = a[m] * x2 + b[m] * y2 - d[m]
                    s3 = a[m] * x3 + b[m] * y3 - d[m]
                    if ((s1 > eps) or (s2 > eps) or (s3 > eps)) and ((s1 < -eps) or (s2 < -eps) or (s3 < -eps)):
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
def score(a, b, d, T, px, py, ok, an, bn, dn, eps):
    n = a.shape[0]
    cnt = 0
    for q in range(T.shape[0]):
        s1 = an * T[q, 0] + bn * T[q, 1] - dn
        s2 = an * T[q, 2] + bn * T[q, 3] - dn
        s3 = an * T[q, 4] + bn * T[q, 5] - dn
        if not (((s1 > eps) or (s2 > eps) or (s3 > eps)) and ((s1 < -eps) or (s2 < -eps) or (s3 < -eps))):
            cnt += 1
    # crossings of new line with base lines, parametrised along direction (-bn, an)
    qx = np.zeros(n); qy = np.zeros(n); qs = np.full(n, np.inf)
    for i in range(n):
        det = a[i] * bn - an * b[i]
        if abs(det) > 1e-14:
            qx[i] = (d[i] * bn - dn * b[i]) / det
            qy[i] = (a[i] * dn - an * d[i]) / det
            qs[i] = -bn * qx[i] + an * qy[i]
    order = np.argsort(qs)
    # distinct points along the new line
    m_valid = 0
    for i in range(n):
        if qs[order[i]] < np.inf:
            m_valid += 1
    # groups
    gstart = np.zeros(n + 1, dtype=np.int64)
    ng = 0
    k = 0
    while k < m_valid:
        gstart[ng] = k
        ng += 1
        k2 = k + 1
        while k2 < m_valid and qs[order[k2]] - qs[order[k]] < eps:
            k2 += 1
        k = k2
    gstart[ng] = m_valid
    for g in range(ng - 1):
        for u in range(gstart[g], gstart[g + 1]):
            i = order[u]
            for v in range(gstart[g + 1], gstart[g + 2]):
                j = order[v]
                if not ok[i, j]:
                    continue
                x1, y1, x2, y2, x3, y3 = px[i, j], py[i, j], qx[i], qy[i], qx[j], qy[j]
                if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-30:
                    continue
                good = True
                for m in range(n):
                    if m == i or m == j:
                        continue
                    s1 = a[m] * x1 + b[m] * y1 - d[m]
                    s2 = a[m] * x2 + b[m] * y2 - d[m]
                    s3 = a[m] * x3 + b[m] * y3 - d[m]
                    if ((s1 > eps) or (s2 > eps) or (s3 > eps)) and ((s1 < -eps) or (s2 < -eps) or (s3 < -eps)):
                        good = False
                        break
                if good:
                    cnt += 1
    return cnt


@njit(parallel=True, cache=True)
def sweep(a, b, d, T, px, py, ok, VX, VY, eps):
    V = VX.shape[0]
    npairs = V * (V - 1) // 2
    best = np.zeros((V, 4))  # per v: best count, w, kind, (unused)
    for v in prange(V):
        bc = -1; bw = -1; bk = -1
        for w in range(v + 1, V):
            dx = VX[w] - VX[v]; dy = VY[w] - VY[v]
            L = math.hypot(dx, dy)
            if L < 1e-12:
                continue
            an = -dy / L; bn = dx / L
            dn = an * VX[v] + bn * VY[v]
            # gap: min distance of other vertices to line vw; and extent
            g = 1e300; R = 0.0
            for u in range(V):
                if u == v or u == w:
                    continue
                s = abs(an * VX[u] + bn * VY[u] - dn)
                if s > 1e-13 and s < g:
                    g = s
                r = math.hypot(VX[u] - VX[v], VY[u] - VY[v])
                if r > R:
                    R = r
            if g > 1e299:
                g = 1.0
            mx = 0.5 * (VX[v] + VX[w]); my = 0.5 * (VY[v] + VY[w])
            dth = min(g / (4.0 * (R + L + 1.0)), 1e-3)
            for i2 in range(a.shape[0]):
                sn = abs(an * b[i2] - bn * a[i2])
                if sn > 1e-13 and sn / 4.0 < dth:
                    dth = sn / 4.0
            dup = False
            for i in range(a.shape[0]):
                if abs(a[i] * VX[v] + b[i] * VY[v] - d[i]) < 1e-12 and abs(a[i] * VX[w] + b[i] * VY[w] - d[i]) < 1e-12:
                    dup = True
                    break
            for kind in range(9):
                if dup:
                    break  # v, w on a common base line: all perturbations ~coincide with it (skipped)
                if kind == 0:
                    cx, cy, th, sh = VX[v], VY[v], 0.0, 0.0
                elif kind == 1:
                    cx, cy, th, sh = VX[v], VY[v], dth, 0.0
                elif kind == 2:
                    cx, cy, th, sh = VX[v], VY[v], -dth, 0.0
                elif kind == 3:
                    cx, cy, th, sh = VX[w], VY[w], dth, 0.0
                elif kind == 4:
                    cx, cy, th, sh = VX[w], VY[w], -dth, 0.0
                elif kind == 5:
                    cx, cy, th, sh = mx, my, 0.0, g / 4.0
                elif kind == 6:
                    cx, cy, th, sh = mx, my, 0.0, -g / 4.0
                elif kind == 7:
                    cx, cy, th, sh = mx, my, dth * 0.5, 0.0
                else:
                    cx, cy, th, sh = mx, my, -dth * 0.5, 0.0
                ca = math.cos(th); sa = math.sin(th)
                a2 = an * ca - bn * sa; b2 = an * sa + bn * ca
                d2 = a2 * cx + b2 * cy + sh
                c = score(a, b, d, T, px, py, ok, a2, b2, d2, eps)
                if c > bc:
                    bc = c; bw = w; bk = kind
        # lines through v parallel to base line i (dual vertices at infinity)
        for i in range(a.shape[0]):
            an = a[i]; bn = b[i]
            dn = an * VX[v] + bn * VY[v]
            if abs(dn - d[i]) < 1e-12:
                continue  # v on line i
            g = 1e300; R = 0.0
            for u in range(V):
                if u == v:
                    continue
                s = abs(an * VX[u] + bn * VY[u] - dn)
                if s > 1e-13 and s < g:
                    g = s
                r = math.hypot(VX[u] - VX[v], VY[u] - VY[v])
                if r > R:
                    R = r
            if g > 1e299:
                g = 1.0
            dth = min(g / (4.0 * (R + 1.0)), 1e-3)
            for i2 in range(a.shape[0]):
                sn = abs(an * b[i2] - bn * a[i2])
                if sn > 1e-13 and sn / 4.0 < dth:
                    dth = sn / 4.0
            for kind in range(10, 16):
                if kind == 10:
                    th, sh = dth, 0.0
                elif kind == 11:
                    th, sh = -dth, 0.0
                elif kind == 12:
                    th, sh = dth, g / 4.0
                elif kind == 13:
                    th, sh = -dth, g / 4.0
                elif kind == 14:
                    th, sh = dth, -g / 4.0
                else:
                    th, sh = -dth, -g / 4.0
                ca = math.cos(th); sa = math.sin(th)
                a2 = an * ca - bn * sa; b2 = an * sa + bn * ca
                d2 = a2 * VX[v] + b2 * VY[v] + sh
                c = score(a, b, d, T, px, py, ok, a2, b2, d2, eps)
                if c > bc:
                    bc = c; bw = -(i + 1); bk = kind
        best[v, 0] = bc; best[v, 1] = bw; best[v, 2] = bk
    return best


def vertices(a, b, d, with_pairs=False):
    n = len(a); pts = []; prs = []
    for i in range(n):
        for j in range(i + 1, n):
            det = a[i] * b[j] - a[j] * b[i]
            if abs(det) > 1e-14:
                pts.append(((d[i] * b[j] - d[j] * b[i]) / det, (a[i] * d[j] - a[j] * d[i]) / det)); prs.append((i, j))
    pts = np.array(pts)
    key = np.round(pts / (1e-9 * (1 + np.abs(pts))), 0)
    _, idx = np.unique(key, axis=0, return_index=True)
    idx = np.sort(idx)
    if with_pairs:
        return pts[idx, 0].copy(), pts[idx, 1].copy(), [prs[k] for k in idx]
    return pts[idx, 0].copy(), pts[idx, 1].copy()


def candidate_line(VX, VY, v, w, kind, a, b, d, T, px, py, ok):
    """Recompute the float line for (v,w,kind) exactly as in sweep."""
    if w < 0:
        i = -w - 1; an, bn = a[i], b[i]; dn = an * VX[v] + bn * VY[v]
        s = np.abs(an * VX + bn * VY - dn); s[v] = np.inf; s[s <= 1e-13] = np.inf
        g = s.min() if np.isfinite(s.min()) else 1.0
        R = np.hypot(VX - VX[v], VY - VY[v]).max()
        dth = min(g / (4.0 * (R + 1.0)), 1e-3)
        sn = np.abs(an * b - bn * a); sn = sn[sn > 1e-13]
        if len(sn): dth = min(dth, sn.min() / 4.0)
        th, sh = {10: (dth, 0), 11: (-dth, 0), 12: (dth, g / 4), 13: (-dth, g / 4), 14: (dth, -g / 4), 15: (-dth, -g / 4)}[kind]
        a2 = an * math.cos(th) - bn * math.sin(th); b2 = an * math.sin(th) + bn * math.cos(th)
        return a2, b2, a2 * VX[v] + b2 * VY[v] + sh
    dx = VX[w] - VX[v]; dy = VY[w] - VY[v]; L = math.hypot(dx, dy)
    an = -dy / L; bn = dx / L; dn = an * VX[v] + bn * VY[v]
    s = np.abs(an * VX + bn * VY - dn); s[[v, w]] = np.inf; s[s <= 1e-13] = np.inf
    g = s.min() if np.isfinite(s.min()) else 1.0
    R = np.hypot(VX - VX[v], VY - VY[v]).max()
    mx = 0.5 * (VX[v] + VX[w]); my = 0.5 * (VY[v] + VY[w])
    dth = min(g / (4.0 * (R + L + 1.0)), 1e-3)
    sn = np.abs(an * b - bn * a); sn = sn[sn > 1e-13]
    if len(sn): dth = min(dth, sn.min() / 4.0)
    tab = {0: (VX[v], VY[v], 0, 0), 1: (VX[v], VY[v], dth, 0), 2: (VX[v], VY[v], -dth, 0),
           3: (VX[w], VY[w], dth, 0), 4: (VX[w], VY[w], -dth, 0), 5: (mx, my, 0, g / 4), 6: (mx, my, 0, -g / 4),
           7: (mx, my, dth / 2, 0), 8: (mx, my, -dth / 2, 0)}
    cx, cy, th, sh = tab[kind]
    a2 = an * math.cos(th) - bn * math.sin(th); b2 = an * math.sin(th) + bn * math.cos(th)
    return a2, b2, a2 * cx + b2 * cy + sh


def exact_line(lines, a2, b2, d2, VXYexact=None):
    """Rational approximation a2 x + b2 y = d2 with growing precision; returns list of candidates."""
    from fractions import Fraction
    out = []
    for S in [10**6, 10**9, 10**12, 10**15, 10**18, 10**22, 10**26]:
        v = [round(a2 * S), round(b2 * S), -round(d2 * S)]
        if v[0] == 0 and v[1] == 0:
            continue
        g = math.gcd(math.gcd(abs(v[0]), abs(v[1])), abs(v[2])) or 1
        out.append([x // g for x in v])
    return out


def _hpt(l1, l2):
    a, b, c = l1; d_, e, f = l2
    return (b * f - c * e, c * d_ - a * f, a * e - b * d_)  # homogeneous (X, Y, W)


def _red(v):
    g = 0
    for x in v: g = math.gcd(g, abs(x))
    return [x // (g or 1) for x in v]


def exact_candidates(lines, prs, v, w, kind, a2, b2, d2):
    out = []
    P = _hpt(lines[prs[v][0]], lines[prs[v][1]])
    Q = _hpt(lines[prs[w][0]], lines[prs[w][1]]) if w >= 0 else None
    if kind in (10, 11):
        X, Y, W = P
        for S in [10**4, 10**6, 10**9, 10**12, 10**15]:
            A, B = round(a2 * S), round(b2 * S)
            out.append(_red([A * W, B * W, -(A * X + B * Y)]))
    elif kind == 0:  # line through P and Q = cross product
        X1, Y1, W1 = P; X2, Y2, W2 = Q
        out.append(_red([Y1 * W2 - W1 * Y2, W1 * X2 - X1 * W2, X1 * Y2 - Y1 * X2]))
    elif kind in (1, 2, 3, 4):  # through P (or Q) with rounded normal
        X, Y, W = P if kind in (1, 2) else Q
        for S in [10**4, 10**6, 10**9, 10**12, 10**15]:
            A, B = round(a2 * S), round(b2 * S)
            out.append(_red([A * W, B * W, -(A * X + B * Y)]))
    out += exact_line(lines, a2, b2, d2)
    return out


def run_insert(lines, top=3, verbose=True):
    a, b, d = to_abd(lines)
    # scale so vertex cloud has unit size
    VX, VY, prs = vertices(a, b, d, with_pairs=True)
    sc = max(np.abs(VX).max(), np.abs(VY).max())
    d = d / sc; VX = VX / sc; VY = VY / sc
    T, px, py, ok = base_state(a, b, d, EPS)
    t0 = time.time()
    best = sweep(a, b, d, T, px, py, ok, VX, VY, EPS)
    order = np.argsort(-best[:, 0])
    res = []
    seen = set()
    for v in order[: max(top * 20, 50)]:
        c, w, kind = int(best[v, 0]), int(best[v, 1]), int(best[v, 2])
        if c < 0:
            continue
        a2, b2, d2 = candidate_line(VX, VY, v, w, kind, a, b, d, T, px, py, ok)
        # exact verification: try rationalisations (unscaled: d*sc)
        ex = None
        for cand in exact_candidates(lines, prs, v, w, kind, a2, b2, d2 * sc):
            if max(abs(x) for x in cand) > 10**30:
                continue
            try:
                L2 = [_normalize(tuple(l)) for l in lines] + [_normalize(tuple(cand))]
                if len(set(L2)) < len(L2):
                    continue
                cnt = len(count_triangles(L2))
            except Exception:
                continue
            if ex is None or cnt > ex[0]:
                ex = (cnt, cand)
            if cnt >= c:
                break
        res.append(dict(float_count=c, v=int(v), w=w, kind=kind, exact=ex[0] if ex else None,
                        line=ex[1] if ex else None))
        if len(res) >= top * 5:
            break
    res.sort(key=lambda r: -(r['exact'] or -1))
    if verbose:
        print(f'  base T={T.shape[0]} V={len(VX)} sweep {time.time()-t0:.1f}s best float={int(best[:,0].max())}', flush=True)
    return int(best[:, 0].max()), res, T.shape[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['insert', 'lns'])
    ap.add_argument('arr')
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--out', default=None)
    ap.add_argument('--only', default=None, help='comma list of line indices for lns')
    A = ap.parse_args()
    lines = json.load(open(A.arr))['lines']
    n = len(lines)
    print(f'{A.mode} {A.arr} n={n} exact T={len(count_triangles([_normalize(tuple(l)) for l in lines]))}', flush=True)
    if A.out:
        os.makedirs(A.out, exist_ok=True)
    if A.mode == 'insert':
        bf, res, _ = run_insert(lines, A.top)
        for r in res[: A.top]:
            print('  ', {k: r[k] for k in ('float_count', 'exact', 'kind')}, flush=True)
        if A.out and res and res[0]['exact']:
            L2 = lines + [res[0]['line']]
            fn = os.path.join(A.out, f'n{n+1}_{res[0]["exact"]}_exins_{os.path.basename(A.arr)}')
            json.dump({'lines': L2}, open(fn, 'w')); print('  saved', fn)
    else:
        idxs = range(n) if not A.only else [int(x) for x in A.only.split(',')]
        for i in idxs:
            rest = [l for k, l in enumerate(lines) if k != i]
            bf, res, Tb = run_insert(rest, A.top, verbose=False)
            ex = res[0]['exact'] if res else None
            print(f'  remove {i}: base38 T={Tb} best reinsertion float={bf} exact={ex}', flush=True)
            if A.out and ex and ex > len(count_triangles([_normalize(tuple(l)) for l in lines])):
                L2 = rest + [res[0]['line']]
                fn = os.path.join(A.out, f'n{n}_{ex}_exlns_r{i}.json')
                json.dump({'lines': L2}, open(fn, 'w')); print('  SAVED', fn, flush=True)


if __name__ == '__main__':
    main()
