"""Cross-check candidates with the mirrored AutoLab evaluator (still a dev number;
the official score is `hills eval` on the pulled hill)."""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "tools"))
from autolab_hill_eval import eval as hill_eval

for f in sys.argv[1:]:
    n = len(json.load(open(f))["lines"])
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(f, Path(d) / "solution.json")
        r = hill_eval(Path(d), n=n)
    print(f"{f}: n={n} passed={r.get('passed')} metrics={r.get('metrics')}")
