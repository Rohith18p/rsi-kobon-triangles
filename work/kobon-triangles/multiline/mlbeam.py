#!/usr/bin/env python3
"""Multi-line remove-and-reinsert beam search.

Job = (seed arrangement, set R of line indices to remove, m = number of lines to
re-insert).  Level j = 1..m: every beam state gets an exhaustive (pruned) best
single-line insertion; the pooled top-B distinct states survive.  Intermediate
levels keep only candidates within `margin` of the best known value at that level
(known = max over j-subsets of the removed lines, i.e. the original positions),
the final level reports the best count >= lo_final.

Usage: uv run python multiline/mlbeam.py jobs.jsonl --wid 0 --nw 2 --log logs/k2_0.jsonl
job line: {"seed": path, "R": [i, j, ...], "m": 2, "tag": "k2"}
"""
import argparse, json, os, sys, time, hashlib
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fastins import insert_top, exact_count, _normalize  # noqa
sys.path.insert(0, os.path.join(HERE, '..', 'src'))
import count as src_count  # noqa

SAVE = HERE
PLATEAU = os.path.join(HERE, 'plateau')


def signature(lines, tris):
    """cheap combinatorial invariant of the triangle hypergraph"""
    n = len(lines)
    deg = [0] * n
    co = {}
    for t in tris:
        for i in t:
            deg[i] += 1
        for p in combinations(sorted(t), 2):
            co[p] = co.get(p, 0) + 1
    pl = sorted((sorted((deg[i], deg[j])), c) for (i, j), c in co.items())
    return hashlib.sha1(json.dumps([sorted(deg), pl]).encode()).hexdigest()[:16]


def verify_and_save(lines, tag):
    c1, _ = exact_count(lines)
    src_count.validate(lines)
    c2 = len(src_count.triangles(lines))
    if c1 != c2:
        print('MISMATCH', c1, c2, flush=True)
    c = min(c1, c2)
    if c >= 471:
        fn = os.path.join(SAVE, f'n{len(lines)}_{c}_{tag}_{int(time.time())}.json')
        json.dump({'lines': [list(map(int, l)) for l in lines]}, open(fn, 'w'))
        print('!!!!! FOUND', c, fn, flush=True)
    return c


def run_job(lines, R, m, B=6, margin=4, lo_final=469, plateau_sigs=None, seed_sig=None, tag=''):
    t0 = time.time()
    base = [l for k, l in enumerate(lines) if k not in set(R)]
    removed = [lines[k] for k in R]
    known = {}
    for j in range(1, m):
        vals = [exact_count(base + list(s))[0] for s in combinations(removed, j)] if j <= len(removed) else []
        known[j] = max(vals) if vals else None
    beam = [base]
    levels = []
    final_best, final_lines, n_final470 = None, None, 0
    ninserts = 0
    for j in range(1, m + 1):
        final = j == m
        if final:
            lo = lo_final
        else:
            lo = known[j] - margin if known.get(j) is not None else 0
        pool = {}
        for st in beam:
            out, fb, Tb, s = insert_top(st, B=(3 if final else B), lo=lo)
            ninserts += 1
            for cnt, line in out:
                L2 = st + [line]
                key = frozenset(_normalize(tuple(x)) for x in L2)
                pool[key] = (cnt, L2)
            if pool:
                bestc = max(v[0] for v in pool.values())
                lo = max(lo, bestc - margin) if not final else max(lo, bestc)
        if not pool:
            levels.append(None)
            break
        ranked = sorted(pool.values(), key=lambda r: -r[0])
        levels.append([r[0] for r in ranked[:B]])
        if final:
            final_best = ranked[0][0]
            for cnt, L2 in ranked:
                if cnt >= 471:
                    c = verify_and_save(L2, tag)
                    final_best = max(final_best, c) if c >= 471 else final_best
                if cnt == 470 and plateau_sigs is not None:
                    cc, tris = exact_count(L2)
                    if cc == 470:
                        sg = signature(L2, tris)
                        if sg != seed_sig and sg not in plateau_sigs:
                            plateau_sigs.add(sg)
                            os.makedirs(PLATEAU, exist_ok=True)
                            fn = os.path.join(PLATEAU, f'n39_470_{sg}.json')
                            json.dump({'lines': [list(map(int, l)) for l in L2]}, open(fn, 'w'))
                            n_final470 += 1
        else:
            beam = [r[1] for r in ranked[:B]]
    return dict(levels=levels, best=final_best, new470=n_final470, ins=ninserts, sec=round(time.time() - t0, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs'); ap.add_argument('--wid', type=int, default=0); ap.add_argument('--nw', type=int, default=1)
    ap.add_argument('--log', required=True); ap.add_argument('--B', type=int, default=6)
    ap.add_argument('--margin', type=int, default=4); ap.add_argument('--lo', type=int, default=469)
    ap.add_argument('--deadline', type=float, default=0, help='unix time to stop')
    A = ap.parse_args()
    jobs = [json.loads(x) for x in open(A.jobs)]
    jobs = jobs[A.wid::A.nw]
    done = set()
    if os.path.exists(A.log):
        for x in open(A.log):
            try:
                r = json.loads(x); done.add((r['seed'], tuple(r['R']), r['m']))
            except Exception:
                pass
    plateau_sigs = set(f.split('_')[-1][:-5] for f in os.listdir(PLATEAU)) if os.path.isdir(PLATEAU) else set()
    cache = {}
    best_all = 0
    with open(A.log, 'a') as fo:
        for jb in jobs:
            if A.deadline and time.time() > A.deadline:
                print('deadline', flush=True); break
            key = (jb['seed'], tuple(jb['R']), jb['m'])
            if key in done:
                continue
            if jb['seed'] not in cache:
                L = json.load(open(jb['seed']))['lines']
                c, tris = exact_count(L)
                cache[jb['seed']] = (L, signature(L, tris), c)
            L, sg, c0 = cache[jb['seed']]
            tag = f"{jb.get('tag','')}_{os.path.basename(jb['seed'])[:-5]}_R{'-'.join(map(str, jb['R']))}"
            r = run_job(L, jb['R'], jb['m'], B=A.B, margin=A.margin, lo_final=A.lo, plateau_sigs=plateau_sigs, seed_sig=sg, tag=tag)
            r.update(seed=jb['seed'], R=jb['R'], m=jb['m'], tag=jb.get('tag', ''), seed_count=c0)
            fo.write(json.dumps(r) + '\n'); fo.flush()
            if r['best'] and r['best'] > best_all:
                best_all = r['best']
                print('best so far', best_all, key, flush=True)
    print('DONE best', best_all, flush=True)


if __name__ == '__main__':
    main()
