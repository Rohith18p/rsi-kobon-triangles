#!/usr/bin/env python3
"""Convert kobon-cnf tables (res/kobon-39-rot3.txt etc.) to wiring words, recount K,
and try to stretch each (stretch2.run). Prints viol / LP margin; saves successes as hill JSON.
Usage: OMP_NUM_THREADS=1 uv run python research/tools/stretch39/test_tables.py /tmp/kobon-cnf/res/kobon-39-rot3.txt [start_idx]"""
import ast, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import combinations
from tab2word import tab_to_word
from word import check
from stretch2 import run
from count_ml import count_ml
tabs = ast.literal_eval(open(sys.argv[1]).read()); start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'n39_candidates')
for k, t in enumerate(tabs[start:], start):
    w, h = tab_to_word(t); n = len(t)
    ok, local = check(w, n); rank = [{x: i for i, x in enumerate(L)} for L in local]
    K = sum(1 for i, j, l in combinations(range(n), 3) if abs(rank[i][j]-rank[i][l]) == 1 and abs(rank[j][i]-rank[j][l]) == 1 and abs(rank[l][i]-rank[l][j]) == 1)
    nv, m, b, d = run(w, n, tries=12)
    print(f'table {k}: K={K} viol={nv} LPdelta={d:.3e}', flush=True)
    if d > 1e-7:
        for den in [10**9, 10**12, 10**15]:
            c, L = count_ml(m, b, den)
            if c == K:
                fn = os.path.join(out, f'n{n}_{c}_c3table{k}.json'); json.dump({'lines': [list(x) for x in L]}, open(fn, 'w'))
                print('  SAVED', fn, flush=True); break
