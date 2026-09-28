"""Greedily add k lines using the incremental scorer; existing lines stay exact.
Usage: uv run python src/grow.py base.json --add 2 --out added --tag X"""
import argparse, json, os
import numpy as np
from count import triangles, validate
from polish import to_td
from lns import insert_best, int_line

ap = argparse.ArgumentParser()
ap.add_argument("base"); ap.add_argument("--add", type=int, default=1)
ap.add_argument("--angles", type=int, default=720); ap.add_argument("--out", default="added")
ap.add_argument("--tag", default="")
a = ap.parse_args()
L = json.load(open(a.base))["lines"]
rng = np.random.default_rng(0)
os.makedirs(a.out, exist_ok=True)
for _ in range(a.add):
    t, d = to_td(L)
    th, off, fc = insert_best(t, d, a.angles, rng)
    L = L + [int_line(th, off)]
    validate(L)
    ex = len(triangles(L))
    p = f"{a.out}/n{len(L)}_{ex}_{a.tag}grow.json"
    json.dump({"lines": L}, open(p, "w"))
    print(f"n={len(L)} float={fc} exact={ex} -> {p}", flush=True)
