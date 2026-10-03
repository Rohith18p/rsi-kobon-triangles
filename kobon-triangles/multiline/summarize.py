#!/usr/bin/env python3
import json, glob, os, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
rs = []
for f in sorted(glob.glob(HERE + '/logs/*.jsonl')):
    rs += [json.loads(x) for x in open(f)]
by = collections.defaultdict(list)
for r in rs:
    base = 'g38base' if '/derived/g38/' in r['seed'] else ('469' if '469' in r['seed'] else ('plateau' if 'plateau' in r['seed'] else '470seed'))
    by[(r['tag'], base)].append(r)
for k, v in sorted(by.items()):
    c = collections.Counter(r['best'] for r in v)
    print(k, 'jobs', len(v), 'insertions', sum(r['ins'] for r in v), 'cpu_s', round(sum(r['sec'] for r in v)),
          'best', max((r['best'] or 0) for r in v), 'dist', dict(sorted(c.items(), key=lambda t: -(t[0] or 0))),
          'new470', sum(r['new470'] for r in v))
print('total jobs', len(rs), 'plateau files', len(glob.glob(HERE + '/plateau/*.json')))
print('>=471 files', glob.glob(HERE + '/n39_47[1-9]*.json') + glob.glob(HERE + '/n39_48*.json'))
