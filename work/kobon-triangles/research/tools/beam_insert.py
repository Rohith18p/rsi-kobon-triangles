#!/usr/bin/env python3
"""Beam of exhaustive insertions: base (n lines) -> keep top-K exact first insertions
-> exhaustive best second insertion for each (n+2 lines).
Usage: uv run python research/tools/beam_insert.py base.json --k 20 --out dir"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exhaustive_insert import run_insert
from autolab_hill_eval import count_triangles, _normalize
ap = argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('--k', type=int, default=20)
ap.add_argument('--out', default=None); A = ap.parse_args()
L = json.load(open(A.base))['lines']; n = len(L)
bf, res, Tb = run_insert(L, top=A.k)
firsts = [r for r in res if r['exact'] is not None][:A.k]
print(f'base n={n} T={Tb}; first insertions (exact):', [r['exact'] for r in firsts], flush=True)
best = (-1, None)
for r in firsts:
    L1 = L + [r['line']]
    bf2, res2, _ = run_insert(L1, top=1, verbose=False)
    ex = res2[0]['exact'] if res2 else None
    print(f'  first={r["exact"]} -> second best float={bf2} exact={ex}', flush=True)
    if ex and ex > best[0]:
        best = (ex, L1 + [res2[0]['line']])
print('BEST', best[0], flush=True)
if A.out and best[1]:
    os.makedirs(A.out, exist_ok=True)
    fn = os.path.join(A.out, f'n{n+2}_{best[0]}_beam_{os.path.basename(A.base)}')
    json.dump({'lines': best[1]}, open(fn, 'w')); print('saved', fn)
