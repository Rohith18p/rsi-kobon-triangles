"""Collect the best exact-verified, hill-valid arrangement per n into submissions/.
Scans candidate folders, re-counts exactly, enforces the hill's input rules, and
writes submissions/n<N>/solution.json plus BEST.md (dev numbers; the official score
is `hills eval`)."""
import glob, json, os, re, shutil, sys
from count import triangles, validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_p = os.path.join(ROOT, "logs", "exact_cache.json")
cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
best = {}
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*.json")) + glob.glob(os.path.join(ROOT, "*", "*", "*.json"))):
    if "/research/" in f or "/submissions/" in f or f.endswith("exact_cache.json"):
        continue
    try:
        L = json.load(open(f))["lines"]
    except Exception:
        continue
    key = f"{f}:{os.path.getmtime(f)}"
    if key not in cache:
        try:
            validate(L)
            if len(json.dumps({"lines": L})) > 65536:
                raise ValueError("file too large")
            cache[key] = len(triangles(L))
        except ValueError:
            cache[key] = -1
    c, n = cache[key], len(L)
    if c > best.get(n, (-1,))[0]:
        best[n] = (c, f)
json.dump(cache, open(cache_p, "w"))
rows = []
for n in sorted(best):
    c, f = best[n]
    d = os.path.join(ROOT, "submissions", f"n{n}")
    os.makedirs(d, exist_ok=True)
    shutil.copy(f, os.path.join(d, "solution.json"))
    rows.append(f"| {n} | {c} | {os.path.relpath(f, ROOT)} |")
open(os.path.join(ROOT, "submissions", "BEST.md"), "w").write(
    "| n | triangles (exact, dev) | source |\n|---|---|---|\n" + "\n".join(rows) + "\n")
print("\n".join(rows))
