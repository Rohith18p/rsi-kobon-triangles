"""Verify the n=39 / 470-triangle arrangement exactly, with two independent counters.

Usage (from the repository root):
    uv run python kobon-triangles/n39_470/verify.py [kobon-triangles/n39_470/solution.json]

Checks: exactly 39 distinct integer lines, |coefficient| <= 10^30 (contest rules),
triangle count by src/count.py and by research/tools/verify_independent.py,
the counting identity, and prints the structural statistics.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KOBON = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KOBON, "src"))
sys.path.insert(0, os.path.join(KOBON, "research", "tools"))

from count import triangles, validate  # noqa: E402
from stats import stats  # noqa: E402
from verify_independent import count_interior  # noqa: E402


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "solution.json")
    raw = open(path, "rb").read()
    L = json.loads(raw)["lines"]
    validate(L)  # integers, non-degenerate, distinct, |coef| <= 1e30
    n = len(L)
    a = len(triangles(L))
    b = count_interior([tuple(t) for t in L])
    s = stats(L)
    print(f"file            : {path}")
    print(f"sha256          : {hashlib.sha256(raw).hexdigest()}")
    print(f"lines           : {n}")
    print(f"triangles       : {a} (src/count.py)  |  {b} (independent counter)")
    print(f"crossing points : {s['crossing_points']}  (triple points: {s['triple_points']}, parallel pairs: {s['parallel_pairs']})")
    print(f"bounded segments: {s['bounded_segments']}  used once: {s['segments_used_once']}  "
          f"shared by two: {s['segments_shared_by_2']}  unused: {s['unused_segments']}")
    print(f"identity 3T = once + 2*shared : {s['identity_ok']}")
    print(f"upper bound (Tamura)          : {s['tamura_bound']}")
    print(f"largest coefficient digits    : {s['max_coef_digits']}")
    ok = (a == b) and s["identity_ok"]
    print("RESULT:", "OK" if ok else "MISMATCH", "-", a, "triangles")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
