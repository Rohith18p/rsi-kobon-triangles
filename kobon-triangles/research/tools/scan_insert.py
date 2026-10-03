#!/usr/bin/env python3
"""Exhaustive best single-line insertion over many bases (one process, numba compiled once).
Usage: uv run python research/tools/scan_insert.py out.jsonl savedir base1.json base2.json ...
       (or a single @list.json containing [[T, path], ...])"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exhaustive_insert import run_insert
out, savedir, bases = sys.argv[1], sys.argv[2], sys.argv[3:]
if len(bases) == 1 and bases[0].startswith('@'):
    bases = [p for _, p in json.load(open(bases[0][1:]))]
os.makedirs(savedir, exist_ok=True)
best_all = 0
with open(out, 'a') as fo:
    for p in bases:
        L = json.load(open(p))['lines']
        t = time.time()
        bf, res, Tb = run_insert(L, top=2, verbose=False)
        ex = res[0]['exact'] if res else None
        fo.write(json.dumps(dict(base=p, n=len(L), T=Tb, best_float=bf, best_exact=ex, sec=round(time.time() - t, 1))) + '\n'); fo.flush()
        if ex and ex > best_all:
            best_all = ex
        if ex and ex >= 470:
            fn = os.path.join(savedir, f'n{len(L)+1}_{ex}_exins_{os.path.basename(p)}')
            json.dump({'lines': L + [res[0]['line']]}, open(fn, 'w'))
            print('SAVED', fn, flush=True)
print('BEST', best_all)
