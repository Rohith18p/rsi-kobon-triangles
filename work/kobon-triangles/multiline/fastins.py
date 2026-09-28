#!/usr/bin/env python3
"""Pruned exhaustive single-line insertion (same candidate set as
research/tools/exhaustive_insert.py, but with branch-and-bound):

  count(line) = T_base - crossed(line) + new(line),   new(line) <= n_base - 1.

For a dual pair (v, w) every perturbation of line vw crosses a superset of the
base triangles strictly crossed by vw itself, so if T - crossed(vw) + n - 1 <=
current best for this v, the whole (v, w) group (9 kinds + the O(V) gap loop) is
skipped. Same for lines through v parallel to a base line. Crossing counts abort
early. `lo` = minimum count worth reporting (prunes more).

Results are identical to the unpruned sweep for every v whose best >= lo.
Near-coincident positions (v, w on a common base line) are skipped, as in the
original tool.
"""
import math, os, sys, time
import numpy as np
from numba import njit, prange

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'research', 'tools'))
from exhaustive_insert import to_abd, base_state, vertices, candidate_line, exact_candidates, score  # noqa
from autolab_hill_eval import count_triangles, _normalize  # exact counter

EPS = 1e-14


@njit(cache=True)
def crossed_upto(T, an, bn, dn, eps, limit):
    """number of base triangles strictly crossed by the line; stops once > limit."""
    c = 0
    for q in range(T.shape[0]):
        s1 = an * T[q, 0] + bn * T[q, 1] - dn
        s2 = an * T[q, 2] + bn * T[q, 3] - dn
        s3 = an * T[q, 4] + bn * T[q, 5] - dn
        if ((s1 > eps) or (s2 > eps) or (s3 > eps)) and ((s1 < -eps) or (s2 < -eps) or (s3 < -eps)):
            c += 1
            if c > limit:
                return c
    return c


@njit(cache=True)
def score_pruned(a, b, d, T, px, py, ok, an, bn, dn, eps, need):
    """exact float score if it can reach `need`, else -1."""
    n = a.shape[0]
    lim = T.shape[0] + n - 1 - need
    if lim < 0:
        return -1
    c = crossed_upto(T, an, bn, dn, eps, lim)
    if c > lim:
        return -1
    return score(a, b, d, T, px, py, ok, an, bn, dn, eps)


@njit(parallel=True, cache=True)
def sweep_pruned(a, b, d, T, px, py, ok, VX, VY, eps, lo):
    V = VX.shape[0]
    n = a.shape[0]
    NT = T.shape[0]
    best = np.full((V, 4), -1.0)
    for v in prange(V):
        bc = lo - 1; bw = 0; bk = -1
        for w in range(v + 1, V):
            dx = VX[w] - VX[v]; dy = VY[w] - VY[v]
            L = math.hypot(dx, dy)
            if L < 1e-12:
                continue
            an = -dy / L; bn = dx / L
            dn = an * VX[v] + bn * VY[v]
            dup = False
            for i in range(n):
                if abs(a[i] * VX[v] + b[i] * VY[v] - d[i]) < 1e-12 and abs(a[i] * VX[w] + b[i] * VY[w] - d[i]) < 1e-12:
                    dup = True
                    break
            if dup:
                continue
            lim = NT + n - 1 - (bc + 1)
            if lim < 0:
                continue
            c0 = crossed_upto(T, an, bn, dn, eps, lim)
            if c0 > lim:
                continue
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
            for i2 in range(n):
                sn = abs(an * b[i2] - bn * a[i2])
                if sn > 1e-13 and sn / 4.0 < dth:
                    dth = sn / 4.0
            for kind in range(9):
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
                c = score_pruned(a, b, d, T, px, py, ok, a2, b2, d2, eps, bc + 1)
                if c > bc:
                    bc = c; bw = w; bk = kind
        for i in range(n):
            an = a[i]; bn = b[i]
            dn = an * VX[v] + bn * VY[v]
            if abs(dn - d[i]) < 1e-12:
                continue
            lim = NT + n - 1 - (bc + 1)
            if lim < 0:
                continue
            c0 = crossed_upto(T, an, bn, dn, eps, lim)
            if c0 > lim:
                continue
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
            for i2 in range(n):
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
                c = score_pruned(a, b, d, T, px, py, ok, a2, b2, d2, eps, bc + 1)
                if c > bc:
                    bc = c; bw = -(i + 1); bk = kind
        if bk >= 0:
            best[v, 0] = bc; best[v, 1] = bw; best[v, 2] = bk
    return best


def exact_count(lines):
    L = [_normalize(tuple(l)) for l in lines]
    if len(set(L)) < len(L):
        return None, None
    tris = count_triangles(L)
    return len(tris), tris


def insert_top(lines, B=6, lo=0, maxtry=None):
    """Top-B distinct (by resulting triangle set) exact insertions with count >= lo.
    Returns (list of (count, line), float_best, T_base, seconds)."""
    t0 = time.time()
    a, b, d = to_abd(lines)
    VX, VY, prs = vertices(a, b, d, with_pairs=True)
    sc = max(np.abs(VX).max(), np.abs(VY).max())
    d = d / sc; VX = VX / sc; VY = VY / sc
    T, px, py, ok = base_state(a, b, d, EPS)
    best = sweep_pruned(a, b, d, T, px, py, ok, VX, VY, EPS, lo)
    order = np.argsort(-best[:, 0], kind='stable')
    out, seen = [], set()
    tried = 0
    maxtry = maxtry or max(B * 8, 24)
    for v in order:
        c, w, kind = int(best[v, 0]), int(best[v, 1]), int(best[v, 2])
        if c < lo or kind < 0:
            break
        if out and len(out) >= B and c < out[-1][0]:
            break
        tried += 1
        if tried > maxtry:
            break
        a2, b2, d2 = candidate_line(VX, VY, v, w, kind, a, b, d, T, px, py, ok)
        ex = None
        for cand in exact_candidates(lines, prs, v, w, kind, a2, b2, d2 * sc):
            if max(abs(x) for x in cand) > 10**30 or (cand[0] == 0 and cand[1] == 0):
                continue
            cnt, tris = exact_count(list(lines) + [cand])
            if cnt is None:
                continue
            if ex is None or cnt > ex[0]:
                ex = (cnt, cand, tris)
            if cnt >= c:
                break
        if ex is None or ex[0] < lo:
            continue
        key = frozenset(tuple(t) for t in ex[2])
        if key in seen:
            continue
        seen.add(key)
        out.append((ex[0], ex[1]))
        out.sort(key=lambda r: -r[0])
        out = out[:B] if len(out) > B else out
    fb = int(best[:, 0].max())
    return out, fb, T.shape[0], time.time() - t0


# ---------------------------------------------------------------------------
# v2: incremental crossing counts.  For pair (v, w), every perturbation differs
# from line vw only on triangles incident to vertices lying on line vw (v, w and
# collinear vertices); no triangle has two such vertices (its side would lie on a
# base line through v and w, which is the skipped 'dup' case).  So
#   crossed(kind) = c0 + sum_{t incident to collinear set} [cr_kind(t) - cr_vw(t)].
# ---------------------------------------------------------------------------

@njit(cache=True)
def _cr(T, q, an, bn, dn, eps):
    s1 = an * T[q, 0] + bn * T[q, 1] - dn
    s2 = an * T[q, 2] + bn * T[q, 3] - dn
    s3 = an * T[q, 4] + bn * T[q, 5] - dn
    return ((s1 > eps) or (s2 > eps) or (s3 > eps)) and ((s1 < -eps) or (s2 < -eps) or (s3 < -eps))


@njit(cache=True)
def newtri(a, b, d, px, py, ok, an, bn, dn, eps):
    n = a.shape[0]
    cnt = 0
    qx = np.zeros(n); qy = np.zeros(n); qs = np.full(n, np.inf)
    for i in range(n):
        det = a[i] * bn - an * b[i]
        if abs(det) > 1e-14:
            qx[i] = (d[i] * bn - dn * b[i]) / det
            qy[i] = (a[i] * dn - an * d[i]) / det
            qs[i] = -bn * qx[i] + an * qy[i]
    order = np.argsort(qs)
    m_valid = 0
    for i in range(n):
        if qs[order[i]] < np.inf:
            m_valid += 1
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


@njit(cache=True)
def _eval_kind(a, b, d, T, tp, nbp, nbm, ok, a2, b2, d2, eps, c0, col, ncol, iptr, iidx, an, bn, dn, bc):
    n = a.shape[0]
    cr = c0
    for t in range(ncol):
        u = col[t]
        for p in range(iptr[u], iptr[u + 1]):
            q = iidx[p]
            cr += np.int64(_cr(T, q, a2, b2, d2, eps)) - np.int64(_cr(T, q, an, bn, dn, eps))
    if T.shape[0] - cr + n - 1 <= bc:
        return -1
    return T.shape[0] - cr + newtri3(a, b, d, ok, tp, nbp, nbm, a2, b2, d2, eps)


@njit(parallel=True, cache=True)
def sweep_fast(a, b, d, T, tp, nbp, nbm, ok, VX, VY, eps, lo, iptr, iidx):
    V = VX.shape[0]
    n = a.shape[0]
    NT = T.shape[0]
    best = np.full((V, 4), -1.0)
    for v in prange(V):
        col = np.zeros(V, dtype=np.int64)
        bc = lo - 1; bw = 0; bk = -1
        for w in range(v + 1, V):
            dx = VX[w] - VX[v]; dy = VY[w] - VY[v]
            L = math.hypot(dx, dy)
            if L < 1e-12:
                continue
            an = -dy / L; bn = dx / L
            dn = an * VX[v] + bn * VY[v]
            dup = False
            for i in range(n):
                if abs(a[i] * VX[v] + b[i] * VY[v] - d[i]) < 1e-12 and abs(a[i] * VX[w] + b[i] * VY[w] - d[i]) < 1e-12:
                    dup = True
                    break
            if dup:
                continue
            lim = NT + n - 1 - (bc + 1)
            if lim < 0:
                continue
            c0 = crossed_upto(T, an, bn, dn, eps, lim)
            if c0 > lim:
                continue
            nw0, ex0 = newtri3x(a, b, d, ok, tp, nbp, nbm, an, bn, dn, eps)
            if NT - c0 + nw0 > bc:
                bc = NT - c0 + nw0; bw = w; bk = 0
            if NT - c0 + nw0 + ex0 <= bc:
                continue
            g = 1e300; R = 0.0
            ncol = 2; col[0] = v; col[1] = w
            for u in range(V):
                if u == v or u == w:
                    continue
                s = abs(an * VX[u] + bn * VY[u] - dn)
                if s > 1e-13 and s < g:
                    g = s
                if s <= 1e-13:
                    col[ncol] = u; ncol += 1
                r = math.hypot(VX[u] - VX[v], VY[u] - VY[v])
                if r > R:
                    R = r
            if g > 1e299:
                g = 1.0
            mx = 0.5 * (VX[v] + VX[w]); my = 0.5 * (VY[v] + VY[w])
            dth = min(g / (4.0 * (R + L + 1.0)), 1e-3)
            for i2 in range(n):
                sn = abs(an * b[i2] - bn * a[i2])
                if sn > 1e-13 and sn / 4.0 < dth:
                    dth = sn / 4.0
            for kind in range(1, 9):
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
                c = _eval_kind(a, b, d, T, tp, nbp, nbm, ok, a2, b2, d2, eps, c0, col, ncol, iptr, iidx, an, bn, dn, bc)
                if c > bc:
                    bc = c; bw = w; bk = kind
        for i in range(n):
            an = a[i]; bn = b[i]
            dn = an * VX[v] + bn * VY[v]
            if abs(dn - d[i]) < 1e-12:
                continue
            lim = NT + n - 1 - (bc + 1)
            if lim < 0:
                continue
            c0 = crossed_upto(T, an, bn, dn, eps, lim)
            if c0 > lim:
                continue
            nw0, ex0 = newtri3x(a, b, d, ok, tp, nbp, nbm, an, bn, dn, eps)
            if NT - c0 + nw0 + ex0 + 2 <= bc:
                continue
            g = 1e300; R = 0.0
            ncol = 1; col[0] = v
            for u in range(V):
                if u == v:
                    continue
                s = abs(an * VX[u] + bn * VY[u] - dn)
                if s > 1e-13 and s < g:
                    g = s
                if s <= 1e-13:
                    col[ncol] = u; ncol += 1
                r = math.hypot(VX[u] - VX[v], VY[u] - VY[v])
                if r > R:
                    R = r
            if g > 1e299:
                g = 1.0
            dth = min(g / (4.0 * (R + 1.0)), 1e-3)
            for i2 in range(n):
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
                c = _eval_kind(a, b, d, T, tp, nbp, nbm, ok, a2, b2, d2, eps, c0, col, ncol, iptr, iidx, an, bn, dn, bc)
                if c > bc:
                    bc = c; bw = -(i + 1); bk = kind
        if bk >= 0:
            best[v, 0] = bc; best[v, 1] = bw; best[v, 2] = bk
    return best


def incidence(T, VX, VY):
    """CSR list of base triangles incident to each (deduplicated) vertex."""
    V = len(VX)
    lists = [[] for _ in range(V)]
    P = np.stack([VX, VY], 1)
    for q in range(T.shape[0]):
        for c in range(3):
            x, y = T[q, 2 * c], T[q, 2 * c + 1]
            dd = (P[:, 0] - x) ** 2 + (P[:, 1] - y) ** 2
            u = int(np.argmin(dd))
            lists[u].append(q)
    iptr = np.zeros(V + 1, dtype=np.int64)
    for u in range(V):
        iptr[u + 1] = iptr[u] + len(lists[u])
    iidx = np.array([q for l in lists for q in l], dtype=np.int64)
    return iptr, iidx


def prep(lines):
    a, b, d = to_abd(lines)
    VX, VY, prs = vertices(a, b, d, with_pairs=True)
    sc = max(np.abs(VX).max(), np.abs(VY).max())
    d = d / sc; VX = VX / sc; VY = VY / sc
    T, px, py, ok = base_state(a, b, d, EPS)
    return a, b, d, VX, VY, prs, sc, T, px, py, ok


USE_FAST = True


def insert_top(lines, B=6, lo=0, maxtry=None):  # noqa: F811  (v2 replaces v1 above)
    t0 = time.time()
    a, b, d, VX, VY, prs, sc, T, px, py, ok = prep(lines)
    if USE_FAST:
        iptr, iidx = incidence(T, VX, VY)
        tp, nbp, nbm = line_params(a, b, px, py, ok)
        best = sweep_fast(a, b, d, T, tp, nbp, nbm, ok, VX, VY, EPS, lo, iptr, iidx)
    else:
        best = sweep_pruned(a, b, d, T, px, py, ok, VX, VY, EPS, lo)
    order = np.argsort(-best[:, 0], kind='stable')
    out, seen = [], set()
    tried = 0
    maxtry = maxtry or max(B * 8, 24)
    for v in order:
        c, w, kind = int(best[v, 0]), int(best[v, 1]), int(best[v, 2])
        if c < lo or kind < 0:
            break
        if out and len(out) >= B and c < out[-1][0]:
            break
        tried += 1
        if tried > maxtry:
            break
        a2, b2, d2 = candidate_line(VX, VY, v, w, kind, a, b, d, T, px, py, ok)
        ex = None
        for cand in exact_candidates(lines, prs, v, w, kind, a2, b2, d2 * sc):
            if max(abs(x) for x in cand) > 10**30 or (cand[0] == 0 and cand[1] == 0):
                continue
            cnt, tris = exact_count(list(lines) + [cand])
            if cnt is None:
                continue
            if ex is None or cnt > ex[0]:
                ex = (cnt, cand, tris)
            if cnt >= c:
                break
        if ex is None or ex[0] < lo:
            continue
        key = frozenset(tuple(t) for t in ex[2])
        if key in seen:
            continue
        seen.add(key)
        out.append((ex[0], ex[1]))
        out.sort(key=lambda r: -r[0])
        out = out[:B] if len(out) > B else out
    fb = int(best[:, 0].max())
    return out, fb, T.shape[0], time.time() - t0


# ---------------------------------------------------------------------------
# v3: O(n log n) new-triangle count.  For consecutive crossings q_i, q_j on the new
# line, triangle (p_ij, q_i, q_j) is a face iff q_i lies on the edge of line i
# incident to p_ij (towards q_i) and likewise q_j on line j: any line crossing the
# triangle cannot cross side q_i q_j, so it must cross the other two sides.
# ---------------------------------------------------------------------------

@njit(cache=True)
def line_params(a, b, px, py, ok):
    n = a.shape[0]
    tp = np.zeros((n, n)); nbp = np.full((n, n), np.inf); nbm = np.full((n, n), -np.inf)
    for i in range(n):
        for j in range(n):
            if j != i and ok[i, j]:
                tp[i, j] = -b[i] * px[i, j] + a[i] * py[i, j]
    for i in range(n):
        for j in range(n):
            if j == i or not ok[i, j]:
                continue
            t = tp[i, j]
            for k in range(n):
                if k == i or k == j or not ok[i, k]:
                    continue
                s = tp[i, k]
                if s > t + 1e-12 and s < nbp[i, j]:
                    nbp[i, j] = s
                if s < t - 1e-12 and s > nbm[i, j]:
                    nbm[i, j] = s
    return tp, nbp, nbm


@njit(cache=True)
def _adj(tq, t, up, dn_):
    if tq > t + 1e-12:
        return tq <= up + 1e-12
    if tq < t - 1e-12:
        return tq >= dn_ - 1e-12
    return False


@njit(cache=True)
def newtri3(a, b, d, ok, tp, nbp, nbm, an, bn, dn, eps):
    n = a.shape[0]
    qx = np.zeros(n); qy = np.zeros(n); qs = np.full(n, np.inf)
    for i in range(n):
        det = a[i] * bn - an * b[i]
        if abs(det) > 1e-14:
            qx[i] = (d[i] * bn - dn * b[i]) / det
            qy[i] = (a[i] * dn - an * d[i]) / det
            qs[i] = -bn * qx[i] + an * qy[i]
    order = np.argsort(qs)
    m_valid = 0
    for i in range(n):
        if qs[order[i]] < np.inf:
            m_valid += 1
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
    cnt = 0
    for g in range(ng - 1):
        for u in range(gstart[g], gstart[g + 1]):
            i = order[u]
            ti = -b[i] * qx[i] + a[i] * qy[i]
            for v in range(gstart[g + 1], gstart[g + 2]):
                j = order[v]
                if not ok[i, j]:
                    continue
                tj = -b[j] * qx[j] + a[j] * qy[j]
                if _adj(ti, tp[i, j], nbp[i, j], nbm[i, j]) and _adj(tj, tp[j, i], nbp[j, i], nbm[j, i]):
                    cnt += 1
    return cnt


@njit(cache=True)
def newtri3x(a, b, d, ok, tp, nbp, nbm, an, bn, dn, eps):
    n = a.shape[0]
    qx = np.zeros(n); qy = np.zeros(n); qs = np.full(n, np.inf)
    for i in range(n):
        det = a[i] * bn - an * b[i]
        if abs(det) > 1e-14:
            qx[i] = (d[i] * bn - dn * b[i]) / det
            qy[i] = (a[i] * dn - an * d[i]) / det
            qs[i] = -bn * qx[i] + an * qy[i]
    order = np.argsort(qs)
    m_valid = 0
    for i in range(n):
        if qs[order[i]] < np.inf:
            m_valid += 1
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
    cnt = 0
    for g in range(ng - 1):
        for u in range(gstart[g], gstart[g + 1]):
            i = order[u]
            ti = -b[i] * qx[i] + a[i] * qy[i]
            for v in range(gstart[g + 1], gstart[g + 2]):
                j = order[v]
                if not ok[i, j]:
                    continue
                tj = -b[j] * qx[j] + a[j] * qy[j]
                if _adj(ti, tp[i, j], nbp[i, j], nbm[i, j]) and _adj(tj, tp[j, i], nbp[j, i], nbm[j, i]):
                    cnt += 1
    ex = 0
    for g in range(ng):
        sz = gstart[g + 1] - gstart[g]
        if sz >= 2:
            ex += sz + 1
    return cnt, ex


@njit(cache=True)
def score3(a, b, d, T, ok, tp, nbp, nbm, an, bn, dn, eps):
    cnt = 0
    for q in range(T.shape[0]):
        if not _cr(T, q, an, bn, dn, eps):
            cnt += 1
    return cnt + newtri3(a, b, d, ok, tp, nbp, nbm, an, bn, dn, eps)
