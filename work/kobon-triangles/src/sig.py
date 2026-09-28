"""Signotope (rank-3) encoding of SIMPLE line / pseudoline arrangements.

Lines are sorted by slope (y = m x + b). For a triple x<y<z (slope order) the bit
s(x,y,z) = +1 iff the middle line y passes ABOVE the crossing point p_xz.
Side of crossing p_ab w.r.t. line c (+1 = point above c), for the sorted triple:
    side(p_xz; y) = -s,   side(p_xy; z) = +s,   side(p_yz; x) = +s.
A triple is a bounded face (Kobon triangle) iff no other line separates its 3 vertices.
"""
from fractions import Fraction as F
from itertools import combinations


def to_mb(L):
    """Exact (m, b) for integer lines a x + b y + c = 0 (requires b != 0), sorted by slope."""
    mb = []
    for a, b, c in L:
        if b == 0:
            raise ValueError("vertical line; rotate first")
        mb.append((F(-a, b), F(-c, b)))
    order = sorted(range(len(mb)), key=lambda i: mb[i][0])
    return [mb[i] for i in order], order


def sbits(mb):
    n = len(mb)
    s = {}
    for x, y, z in combinations(range(n), 3):
        (m1, b1), (m2, b2), (m3, b3) = mb[x], mb[y], mb[z]
        px = (b3 - b1) / (m1 - m3)
        py = m1 * px + b1
        v = m2 * px + b2 - py
        if v == 0:
            raise ValueError("not simple")
        s[(x, y, z)] = 1 if v > 0 else -1
    return s


def side(s, a, b, c):
    """side of crossing p_ab w.r.t. line c, from signotope bits."""
    x, y, z = sorted((a, b, c))
    v = s[(x, y, z)]
    return -v if c == y else v


def is_face(s, n, i, j, k):
    for m in range(n):
        if m in (i, j, k):
            continue
        a, b, c = side(s, i, j, m), side(s, i, k, m), side(s, j, k, m)
        if not (a == b == c):
            return False
    return True


def count_faces(s, n):
    return sum(1 for t in combinations(range(n), 3) if is_face(s, n, *t))


def monotone_ok(s, n):
    """Check the 4-subset rule: (s_ijk, s_ijl, s_ikl, s_jkl) has at most one sign change."""
    bad = 0
    for i, j, k, l in combinations(range(n), 4):
        seq = [s[(i, j, k)], s[(i, j, l)], s[(i, k, l)], s[(j, k, l)]]
        ch = sum(1 for u, v in zip(seq, seq[1:]) if u != v)
        if ch > 1:
            bad += 1
    return bad
