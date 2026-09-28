"""SAT large-neighbourhood search on the signotope encoding (simple arrangements).

Loop: pick k free lines of the current straight arrangement; fix all signotope bits
among the other lines; ask SAT for >= target triangles; if SAT, straighten only the
free lines (sample their slopes inside their slope-order slots, then an LP in their
intercepts), re-count exactly, keep if improved.

Usage: uv run python src/sat_lns.py base.json --k 3 --target 471 --minutes 60 --seed 1
"""
import argparse
import json
import math
import os
import random
import subprocess
import threading
import time
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from scipy.optimize import linprog

from count import triangles, validate
from sig import is_face, sbits, side, to_mb


class Enc:
    def __init__(self, n):
        self.n = n
        self.nv = 0
        self.sv = {}
        for t in combinations(range(n), 3):
            self.nv += 1
            self.sv[t] = self.nv

    def lit(self, t, val):  # literal meaning s[t] == val (val = +1 / -1)
        v = self.sv[t]
        return v if val > 0 else -v

    def side_lit(self, a, b, c, val):  # literal meaning side(p_ab; c) == val
        x, y, z = sorted((a, b, c))
        return self.lit((x, y, z), -val if c == y else val)


def build(s0, n, free, target):
    E = Enc(n)
    free = set(free)
    fixed = [i for i in range(n) if i not in free]
    cl = []
    # fixed bits
    for t, v in s0.items():
        if not (free & set(t)):
            cl.append([E.lit(t, v)])
    # signotope rule on 4-subsets touching a free line: forbid x,!x,x patterns in order
    for q in combinations(range(n), 4):
        if not (free & set(q)):
            continue
        i, j, k, l = q
        seq = [(i, j, k), (i, j, l), (i, k, l), (j, k, l)]
        for a, b, c in combinations(range(4), 3):
            ta, tb, tc = seq[a], seq[b], seq[c]
            for val in (1, -1):  # forbid (val, -val, val)
                cl.append([-E.lit(ta, val), -E.lit(tb, -val), -E.lit(tc, val)])
    # face variables
    faces = []
    fv = {}
    for t in combinations(range(n), 3):
        tf = free & set(t)
        if not tf:
            # blocked already by a fixed line?  then it can never be a face
            if not all(side(s0, t[0], t[1], m) == side(s0, t[0], t[2], m) == side(s0, t[1], t[2], m)
                       for m in fixed if m not in t):
                continue
            ms = [m for m in free]
        else:
            ms = [m for m in range(n) if m not in t]
        E.nv += 1
        f = E.nv
        fv[t] = f
        faces.append(f)
        i, j, k = t
        for m in ms:
            # f -> side(p_ij;m) == side(p_ik;m) == side(p_jk;m)
            for val in (1, -1):
                a1 = E.side_lit(i, j, m, val)
                a2 = E.side_lit(i, k, m, val)
                a3 = E.side_lit(j, k, m, val)
                cl.append([-f, -a1, a2])
                cl.append([-f, -a2, a3])
    card = CardEnc.atleast(lits=faces, bound=target, top_id=E.nv, encoding=EncType.cardnetwrk)
    return E, cl + card.clauses, fv


def build_full(n, target):
    """All constraints for every triple/4-subset; bits get fixed later via assumptions."""
    E = Enc(n)
    cl = []
    for q in combinations(range(n), 4):
        i, j, k, l = q
        seq = [(i, j, k), (i, j, l), (i, k, l), (j, k, l)]
        for a, b, c in combinations(range(4), 3):
            ta, tb, tc = seq[a], seq[b], seq[c]
            for val in (1, -1):
                cl.append([-E.lit(ta, val), -E.lit(tb, -val), -E.lit(tc, val)])
    faces = []
    for t in combinations(range(n), 3):
        E.nv += 1
        f = E.nv
        faces.append(f)
        i, j, k = t
        for m in range(n):
            if m in t:
                continue
            for val in (1, -1):
                a1 = E.side_lit(i, j, m, val)
                a2 = E.side_lit(i, k, m, val)
                a3 = E.side_lit(j, k, m, val)
                cl.append([-f, -a1, a2])
                cl.append([-f, -a2, a3])
    card = CardEnc.atleast(lits=faces, bound=target, top_id=E.nv, encoding=EncType.cardnetwrk)
    return E, cl + card.clauses


def before_lit(E, r, a, b):
    """literal: along line r, crossing with a is left of crossing with b."""
    x, y, z = sorted((r, a, b))
    return E.lit((x, y, z), 1 if a < b else -1)


def before_val(s0, r, a, b):
    x, y, z = sorted((r, a, b))
    v = s0[(x, y, z)]
    return v if a < b else -v


def build_seg(s0, n, free, target):
    """Segment encoding: every consecutive pair on every line is a face or flagged unused;
    at most n(n-2) - 3*target flags (simple arrangements: 3T = #used segments)."""
    E = Enc(n)
    free = set(free)
    fixed = [i for i in range(n) if i not in free]
    K = n * (n - 2) - 3 * target
    cl = []
    for t, v in s0.items():
        if not (free & set(t)):
            cl.append([E.lit(t, v)])
    for q in combinations(range(n), 4):
        if not (free & set(q)):
            continue
        i, j, k, l = q
        seq = [(i, j, k), (i, j, l), (i, k, l), (j, k, l)]
        for a, b, c in combinations(range(4), 3):
            ta, tb, tc = seq[a], seq[b], seq[c]
            for val in (1, -1):
                cl.append([-E.lit(ta, val), -E.lit(tb, -val), -E.lit(tc, val)])
    fv = {}
    for t in combinations(range(n), 3):
        tf = free & set(t)
        if not tf:
            if not all(side(s0, t[0], t[1], m) == side(s0, t[0], t[2], m) == side(s0, t[1], t[2], m)
                       for m in fixed if m not in t):
                continue
            ms = list(free)
        else:
            ms = [m for m in range(n) if m not in t]
        E.nv += 1
        f = E.nv
        fv[t] = f
        i, j, k = t
        for m in ms:
            for val in (1, -1):
                a1 = E.side_lit(i, j, m, val)
                a2 = E.side_lit(i, k, m, val)
                a3 = E.side_lit(j, k, m, val)
                cl.append([-f, -a1, a2])
                cl.append([-f, -a2, a3])
    uvars = []
    for r in range(n):
        others = [x for x in range(n) if x != r]
        for a, b in combinations(others, 2):
            T = tuple(sorted((r, a, b)))
            allfixed = not (free & set(T))
            skip = False
            disj = []
            for m in range(n):
                if m in T:
                    continue
                if allfixed and m not in free:
                    o1 = before_val(s0, r, a, m) > 0 and before_val(s0, r, m, b) > 0
                    o2 = before_val(s0, r, b, m) > 0 and before_val(s0, r, m, a) > 0
                    if o1 or o2:
                        skip = True  # a fixed line lies between: never consecutive
                        break
                    continue
                E.nv += 1
                b1 = E.nv
                E.nv += 1
                b2 = E.nv
                cl.append([-b1, before_lit(E, r, a, m)])
                cl.append([-b1, before_lit(E, r, m, b)])
                cl.append([-b2, before_lit(E, r, b, m)])
                cl.append([-b2, before_lit(E, r, m, a)])
                disj += [b1, b2]
            if skip:
                continue
            E.nv += 1
            u = E.nv
            uvars.append(u)
            c = [u] + disj
            if T in fv:
                c.append(fv[T])
            cl.append(c)
    card = CardEnc.atmost(lits=uvars, bound=K, top_id=E.nv, encoding=EncType.seqcounter)
    E.nv = max(E.nv, card.nv)
    return E, cl + card.clauses, fv


def unused_segments(s0, n):
    """(r, a, b) for consecutive pairs on line r that are not triangle faces."""
    out = []
    for r in range(n):
        others = [x for x in range(n) if x != r]
        for a, b in combinations(others, 2):
            T = tuple(sorted((r, a, b)))
            between = any((before_val(s0, r, a, m) > 0 and before_val(s0, r, m, b) > 0) or
                          (before_val(s0, r, b, m) > 0 and before_val(s0, r, m, a) > 0)
                          for m in range(n) if m not in T)
            if not between and not is_face(s0, n, *T):
                out.append((r, a, b))
    return out


def pick_free(rng, segs, n, k):
    free = []
    order = rng.sample(segs, len(segs))
    for seg in order:
        for x in seg:
            if x not in free:
                free.append(x)
        if len(free) >= k:
            break
    free = free[:k]
    while len(free) < k:
        x = rng.randrange(n)
        if x not in free:
            free.append(x)
    return sorted(free)


def kissat(clauses, _unused, timeout, stem):
    """Run kissat on clauses; returns (True, model) / (False, None) / (None, None) on timeout."""
    nv = max(abs(x) for c in clauses for x in c)
    cnf = stem + ".cnf"
    with open(cnf, "w") as f:
        f.write(f"p cnf {nv} {len(clauses)}\n")
        f.write("".join(" ".join(map(str, c)) + " 0\n" for c in clauses))
    r = subprocess.run(["kissat", f"--time={int(timeout)}", "-q", cnf], capture_output=True, text=True)
    os.remove(cnf)
    if r.returncode == 20:
        return False, None
    if r.returncode != 10:
        return None, None
    model = []
    for line in r.stdout.splitlines():
        if line.startswith("v"):
            model.extend(int(x) for x in line[1:].split() if x != "0")
    return True, model


def decode(E, model, n):
    pos = set(x for x in model if x > 0)
    return {t: (1 if v in pos else -1) for t, v in E.sv.items()}


def side_lin(mb_m, bfix, free_idx, a, b, c):
    """side(p_ab; c) as (coef vector over free intercepts, const) given all slopes."""
    ma, mbv, mc = mb_m[a], mb_m[b], mb_m[c]
    # side = p.y - c(p.x) = (ma - mc)(b_b - b_a)/(ma - mb) + b_a - b_c
    k = (ma - mc) / (ma - mbv)
    coef = {}
    const = 0.0

    def add(line, w):
        nonlocal const
        if line in free_idx:
            coef[line] = coef.get(line, 0.0) + w
        else:
            const += w * bfix[line]
    add(b, k)
    add(a, -k)
    add(a, 1.0)
    add(c, -1.0)
    return coef, const


def straighten(s, n, free, mb, tries, rng):
    """Find slopes+intercepts for free lines realizing s (other lines fixed). Returns mb or None."""
    free = sorted(free)
    ms0 = [float(m) for m, b in mb]
    bs0 = [float(b) for m, b in mb]
    col = {f: i for i, f in enumerate(free)}
    trip = [t for t in combinations(range(n), 3) if set(t) & set(free)]
    for attempt in range(tries):
        ms = list(ms0)
        for f in free:  # sample slope within its slot (neighbours in slope order)
            lo = ms0[f - 1] if f > 0 else ms0[f] - 1.0
            hi = ms0[f + 1] if f + 1 < n else ms0[f] + 1.0
            if attempt == 0:
                ms[f] = ms0[f]
            else:
                u = rng.random()
                ms[f] = lo + (hi - lo) * (0.02 + 0.96 * u)
        if any(ms[i] >= ms[i + 1] for i in range(n - 1)):
            continue
        A, ub = [], []
        for x, y, z in trip:
            val = s[(x, y, z)]
            coef, const = side_lin(ms, bs0, col, x, z, y)  # side(p_xz; y) must equal -val
            req = -val
            row = np.zeros(len(free) + 1)
            for line, w in coef.items():
                row[col[line]] = -req * w
            row[-1] = 1.0  # margin t:  req*side >= t  ->  -req*coef.b + t <= req*const
            A.append(row)
            ub.append(req * const)
        c = np.zeros(len(free) + 1)
        c[-1] = -1.0
        scale = max(1.0, max(abs(b) for b in bs0))
        bounds = [(-100 * scale, 100 * scale)] * len(free) + [(None, 1.0)]
        res = linprog(c, A_ub=np.array(A), b_ub=np.array(ub), bounds=bounds, method="highs")
        if res.status == 0 and res.x[-1] > 1e-9:
            out = list(mb)
            for f in free:
                out[f] = (F(ms[f]).limit_denominator(10**12), F(res.x[col[f]]).limit_denominator(10**12))
            return out
    return None


def mb_to_int(mb):
    L = []
    for m, b in mb:  # y = m x + b  ->  m x - y + b = 0
        den = math.lcm(m.denominator, b.denominator)
        t = [int(m * den), -den, int(b * den)]
        g = math.gcd(math.gcd(abs(t[0]), abs(t[1])), abs(t[2])) or 1
        L.append([v // g for v in t])
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--target", type=int, default=471)
    ap.add_argument("--minutes", type=float, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--straighten-tries", type=int, default=300)
    ap.add_argument("--out", default="satlns")
    ap.add_argument("--sat-timeout", type=float, default=120)
    ap.add_argument("--enc", default="seg", choices=["seg", "card"])
    ap.add_argument("--targeted", type=int, default=1)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    L = json.load(open(args.base))["lines"]
    mb, _ = to_mb(L)
    n = len(mb)
    s0 = sbits(mb)
    cur = len(triangles(mb_to_int(mb)))
    print(f"base n={n} exact={cur} target={args.target} k={args.k}", flush=True)
    os.makedirs(args.out, exist_ok=True)
    deadline = time.time() + args.minutes * 60
    it = 0
    segs = None
    while time.time() < deadline:
        it += 1
        if args.targeted:
            if it == 1 or segs is None:
                segs = unused_segments(s0, n)
            free = pick_free(rng, segs, n, args.k)
        else:
            free = sorted(rng.sample(range(n), args.k))
        t0 = time.time()
        E, cl, fv = (build_seg if args.enc == 'seg' else build)(s0, n, free, args.target)
        tb = time.time() - t0
        ok, model = kissat(cl, E.nv if False else None, args.sat_timeout, f"{args.out}/tmp_s{args.seed}")
        del cl
        dt = time.time() - t0
        status = {True: "SAT", False: "UNSAT", None: "TIMEOUT"}[ok]
        print(f"  it {it} free={free}: {status} ({dt:.0f}s, faces vars {len(fv)})", flush=True)
        if not ok:
            continue
        s = decode(E, model, n)
        pc = sum(1 for t in combinations(range(n), 3) if is_face(s, n, *t))
        mb2 = straighten(s, n, free, mb, args.straighten_tries, rng)
        if mb2 is None:
            print(f"  it {it} free={free}: SAT pseudo={pc} ({dt:.0f}s) -> straighten FAILED", flush=True)
            continue
        L2 = mb_to_int(mb2)
        try:
            validate(L2)
        except ValueError as e:
            print(f"  it {it}: invalid {e}", flush=True)
            continue
        ex = len(triangles(L2))
        print(f"  it {it} free={free}: SAT pseudo={pc} ({dt:.0f}s) -> STRAIGHT exact={ex}", flush=True)
        if ex >= args.target:
            p = f"{args.out}/n{n}_{ex}_satlns_s{args.seed}_it{it}.json"
            json.dump({"lines": L2}, open(p, "w"))
            print(f"  *** FOUND {ex} -> {p}", flush=True)
            mb, s0, cur = to_mb(L2)[0], sbits(to_mb(L2)[0]), ex
            args.target = ex + 1
            segs = None
            print(f"  new base {cur}, next target {args.target}", flush=True)


if __name__ == "__main__":
    main()
