#!/usr/bin/env python3
"""Convert Parpalak-Utkin gallery JSON (ud1/kobon-solutions, lines = [slope, intercept],
y = slope*x + intercept, plus a `gens` reduced word with '*' = triple point) into the
AutoLab hill submission format {"lines": [[a, b, c], ...]} meaning a*x + b*y + c = 0,
with exact integer coefficients.

Exact path: decimals are read as exact rationals. If they do not realize `gens` exactly
(triple points / parallels only approximately satisfied), use ud1's own deterministic
`quick_rationalize` repair, then re-check. Output is always re-scored with the hill's
evaluator (tools/autolab_hill_eval.py) and with an independent interior-crossing counter.

Usage: python3 ud1_to_hill.py <gallery json> [<out.json>]
"""
import json
import sys
from decimal import Decimal
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path

import os

HERE = Path(__file__).resolve().parent
# The gallery's own verification code (ud1/kobon-solutions, not redistributed here).
# Point UD1_DIR at a checkout of https://github.com/ud1/kobon-solutions (default: research/raw copy).
UD1_DIR = Path(os.environ.get("UD1_DIR", HERE.parent / "raw" / "ud1_kobon-solutions"))
sys.path.insert(0, str(UD1_DIR / "verification"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "src"))
import quick_check as qc  # noqa: E402
from verify_independent import count_interior  # noqa: E402

try:  # mirrored contest evaluator, if present locally (not redistributed)
    import autolab_hill_eval as hill  # noqa: E402

    def hill_count(triples):
        return len(hill.count_triangles([hill._normalize(tuple(r)) for r in triples]))
except ImportError:  # fall back to our own exact counter (src/count.py)
    from count import triangles as _tri  # noqa: E402

    def hill_count(triples):
        return len(_tri([list(t) for t in triples]))


def to_int_triples(lines):
    out = []
    for m, b in lines:
        m, b = Fraction(m), Fraction(b)
        d = lcm(m.denominator, b.denominator)
        a, bb, c = int(m * d), -d, int(b * d)  # m x - y + b = 0
        g = gcd(gcd(abs(a), abs(bb)), abs(c)) or 1
        out.append([a // g, bb // g, c // g])
    return out


def compact_rationalize(lines, structure, D):
    """Round slopes (shared per parallel class) and the free intercepts to fractions with
    denominator <= D; solve the dependent intercepts exactly from the triple-point
    constraints (linear in intercepts once slopes are fixed)."""
    n = len(lines)
    fl = [(float(m), float(b)) for m, b in lines]
    slopes = [Fraction(m).limit_denominator(D) for m, _ in fl]
    for comp in qc.parallel_components(n, structure.parallel_pairs):
        v = Fraction(sum(fl[i][0] for i in comp) / len(comp)).limit_denominator(D)
        for i in comp:
            slopes[i] = v
    rows = []
    for pt in structure.multiple_points:
        a, b, c = sorted(pt)
        r = [Fraction(0)] * n
        r[a], r[b], r[c] = slopes[b] - slopes[c], slopes[c] - slopes[a], slopes[a] - slopes[b]
        rows.append(r)
    piv = []
    R = [r[:] for r in rows]
    ri = 0
    for col in range(n):
        if ri == len(R):
            break
        k = next((i for i in range(ri, len(R)) if R[i][col] != 0), None)
        if k is None:
            continue
        R[ri], R[k] = R[k], R[ri]
        pv = R[ri][col]
        R[ri] = [x / pv for x in R[ri]]
        for i in range(len(R)):
            if i != ri and R[i][col] != 0:
                f = R[i][col]
                R[i] = [x - f * y for x, y in zip(R[i], R[ri])]
        piv.append(col)
        ri += 1
    b = [Fraction(fl[i][1]).limit_denominator(D) for i in range(n)]
    for r, col in zip(R, piv):
        b[col] = -sum(r[j] * b[j] for j in range(n) if j != col)
    return tuple(zip(slopes, b))


def convert(path):
    data = json.load(open(path), parse_float=Decimal)
    n = len(data["lines"])
    structure = qc.replay_word(data["gens"], n)
    lines = qc.parse_lines(data, n)
    ok, _ = qc.compare_realization(lines, structure)
    how = "exact-decimals"
    if not ok:
        lines = qc.quick_rationalize(lines, structure)
        ok, why = qc.compare_realization(lines, structure)
        how = "quick-rationalized"
        if not ok:
            raise SystemExit(f"cannot rationalize {path}: {why}")
    triples = to_int_triples(lines)
    if max(abs(v) for r in triples for v in r) > 10**30:
        orig = qc.parse_lines(data, n)
        for D in [10, 30, 100, 300, 1000, 3000, 10**4, 3 * 10**4, 10**5, 10**6, 10**7, 10**8]:
            try:
                cand = compact_rationalize(orig, structure, D)
                ok2, _ = qc.compare_realization(cand, structure)
            except (qc.CheckError, ZeroDivisionError):
                ok2 = False
            if ok2:
                t2 = to_int_triples(cand)
                if max(abs(v) for r in t2 for v in r) <= 10**30:
                    triples, how = t2, f"compact-rationalized(D={D})"
                    break
    t_hill = hill_count(triples)
    t_ind = count_interior(triples)
    t_word = qc.count_triangles(structure.rows)
    return triples, dict(n=n, how=how, hill=t_hill, independent=t_ind, word=t_word,
                         maxcoef=max(abs(v) for r in triples for v in r))


if __name__ == "__main__":
    triples, info = convert(sys.argv[1])
    print(json.dumps(info))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps({"lines": triples}))
