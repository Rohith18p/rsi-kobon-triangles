"""Bartholdi–Blanc–Loisel Proposition 3.1 doubling, done in exact rationals.

A = {Y0: y = 0} ∪ {L_i: y = m_i (x - a_i)}, i = 1..n (n even), with
{a_1..a_{n-2}} = {tan(k pi / n) : k = ±1..±(n/2 - 1)}, a_{n-1} in (-1/n, 0), a_n in (0, 1/n),
and Y0 touching n-1 triangles. Adding M_i: y = mu_i (x - b_i), b_i = tan(beta_i),
beta_i = -pi/2 + (2i-1) pi/(2n), mu_i = sigma * m_min * delta * (sin(2 beta_i) + eps2 / b_i)
gives 2n+1 lines with n^2 more triangles (paper: delta = n^-10, eps2 = n^-6; larger delta
often still works and keeps coefficients small). Iterates via Remark 3.2.

Lines are kept as (m, a) exact Fractions; tan/sin values are rational approximations
(the hypotheses are open conditions, so this is fine; the exact count is the proof).

Usage: uv run python src/doubling.py --base 7|15|3|p19 --iters K --delta-exp 4
"""

import argparse
import csv
import json
import math
import os
from fractions import Fraction as F

from count import triangles, validate

PREC = 10**40
EPS2 = 6


def rat(x):
    return F(x).limit_denominator(PREC)


def base_lines(name, eps):
    """Return (m, a) pairs for the non-Y0 lines, ordered so the last two have tiny a."""
    if name == "7":
        tbl = [(-2, 3), (-1, 1), (1, -1), (2, -3)]  # (k for a = tan(k pi/6), m)
        L = [(F(m), rat(math.tan(k * math.pi / 6))) for k, m in tbl]
        L += [(F(-7), -eps), (F(7), eps)]
        return L
    if name == "15":
        tbl = [(-6, 1.66), (-5, 4.4), (-4, 3.28), (-3, 14.4), (-2, 13.1), (-1, -65), (1, -52),
               (2, -12.4), (3, -22), (4, -4.8), (5, -5.3), (6, -1.86)]
        L = [(rat(m), rat(math.tan(k * math.pi / 14))) for k, m in tbl]
        L += [(F(50), -eps), (F(-45), eps)]
        return L
    if name == "p19":
        path = os.path.join(os.path.dirname(__file__), "..", "research", "raw",
                            "parpalak_triangle-maximal-18-series", "data", "n19", "lines.csv")
        rows = list(csv.DictReader(open(path)))[1:]  # row 0 is Y0: y = 0
        L = []
        for r in rows:
            m, b = F(r["m"]), F(r["b"])
            L.append((m, -b / m))  # y = m x + b = m (x - a) with a = -b/m
        return L[:16] + L[16:]  # rows 17, 18 (the tiny intercepts) are already last
    if name == "3":
        return [(F(1), -eps), (F(-1), eps)]
    raise ValueError(name)


def double(L, delta_exp, eps2_exp=6):
    eps2_exp = EPS2
    n = len(L)
    assert n % 2 == 0
    mmin = min(abs(m) for m, a in L)
    # sigma: do L_{n-1} and L_n meet in the upper half-plane?
    (m1, a1), (m2, a2) = L[-2], L[-1]
    x = (m1 * a1 - m2 * a2) / (m1 - m2)
    sigma = 1 if m1 * (x - a1) > 0 else -1
    delta = F(1, n**delta_exp)
    eps2 = F(1, n**eps2_exp)
    M = []
    for i in range(1, n + 1):
        beta = -math.pi / 2 + (2 * i - 1) * math.pi / (2 * n)
        b = rat(math.tan(beta))
        mu = sigma * mmin * delta * (rat(math.sin(2 * beta)) + eps2 / b)
        M.append((mu, b))
    # new order: regular intercepts first, the two tiny ones last (Remark 3.2)
    return L[:-2] + M + L[-2:]


def to_int_lines(L, digits=29):
    """y = m (x - a)  ->  m x - y - m a = 0, each line scaled so its largest
    coefficient is ~10^digits, then rounded to integers; Y0 is y = 0."""
    out = [[0, 1, 0]]
    for m, a in L:
        c = -m * a
        big = max(abs(m), F(1), abs(c))
        S = F(10**digits) / big
        t = [round(m * S), -round(S), round(c * S)]
        g = math.gcd(math.gcd(abs(t[0]), abs(t[1])), abs(t[2])) or 1
        out.append([v // g for v in t])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="7")
    ap.add_argument("--iters", type=int, default=1)
    ap.add_argument("--delta-exp", type=int, default=10)
    ap.add_argument("--eps", default="1e-6")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--eps2-exp", type=int, default=6)
    ap.add_argument("--out", default="doubled")
    args = ap.parse_args()
    global EPS2
    EPS2 = args.eps2_exp
    L = base_lines(args.base, rat(float(args.eps)))
    os.makedirs(args.out, exist_ok=True)
    for it in range(args.iters + 1):
        lines = to_int_lines(L)
        n = len(lines)
        big = max(len(str(abs(v))) for l in lines for v in l)
        msg = f"n={n} maxdigits={big}"
        if args.count or it == args.iters:
            try:
                validate(lines)
                ok = "valid"
            except ValueError as e:
                ok = f"INVALID ({str(e)[:40]})"
            c = len(triangles(lines))
            msg += f" triangles={c} bound={n * (n - 2) // 3} {ok}"
            json.dump({"lines": lines}, open(f"{args.out}/n{n}_{c}_b{args.base}_d{args.delta_exp}.json", "w"))
        print(msg, flush=True)
        if it < args.iters:
            L = double(L, args.delta_exp)


if __name__ == "__main__":
    main()
