#!/usr/bin/env python3
"""Pick, for each gallery series, the max-triangle entry with the smallest 'ratio'
(Parpalak-Utkin's showcase criterion) and write it in hill format to records/."""
import json, sys, glob
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ud1_to_hill as U
import quick_check as qc
root = HERE.parent / "raw" / "ud1_kobon-solutions"
out = HERE.parent / "records"
series = sys.argv[1:]
summary = []
for s in series:
    best = None
    for fn in sorted(glob.glob(str(root / s / "*.json"))):
        d = json.load(open(fn))
        n = len(d["lines"])
        t = qc.count_triangles(qc.replay_word(d["gens"], n).rows)
        key = (-t, d.get("ratio", 1e18))
        if best is None or key < best[0]:
            best = (key, fn, d["gens"].count("*"))
    fn = best[1]
    triples, info = U.convert(fn)
    info.update(series=s, source=f"ud1/kobon-solutions gallery/data/{s}/{Path(fn).name}", triple_points=best[2])
    name = f"n{info['n']}_{info['hill']}_ud1_{s}_{Path(fn).stem}.json"
    (out / name).write_text(json.dumps({"lines": triples}))
    info["file"] = "records/" + name
    print(json.dumps(info)); summary.append(info)
json.dump(summary, open(out / "_ud1_records_summary.json", "w"), indent=1)
