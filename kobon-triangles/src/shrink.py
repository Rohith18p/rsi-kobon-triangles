"""Re-round an arrangement to small integer coefficients, keeping the exact count.

Tries increasing scales and keeps the smallest one whose exact count equals the
original. Usage: uv run python src/shrink.py in.json [out.json]
"""
import json, math, sys
from count import triangles, validate
from polish import to_td
from search import to_integer_lines

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else src.replace(".json", "_small.json")
L = json.load(open(src))["lines"]
target = len(triangles(L))  # exact count of the original (no bound check needed)
t, d = to_td(L)
for e in range(6, 29):
    M = to_integer_lines(t, d, 10**e)
    try:
        validate(M)
    except ValueError:
        continue
    c = len(triangles(M))
    if c == target:
        json.dump({"lines": M}, open(out, "w"))
        print(f"{src}: count {target} kept at scale 1e{e} -> {out}")
        break
else:
    print(f"{src}: FAILED to shrink while keeping {target}")
