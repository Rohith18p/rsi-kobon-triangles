Climb the AutoLab hill ottogin/erdos-3 on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/rsi-kobon-triangles, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull ottogin/erdos-3` -> ./.autolab/hills/erdos-3.
5. Read `statement.lean`, `eval.py`, `hill.yaml` and the example solution. The README says checking happens "inside the hill's image". Find out whether `hills eval` needs Docker or builds Lean/Mathlib itself, and tell me if something (e.g. Docker Desktop) must be installed.
6. Local Lean environment for development: `lean/formal-conjectures/` (Lean v4.33.1, Mathlib prebuilt, `FormalConjecturesUtil` built). Check drafts with `cd lean/formal-conjectures && lake env lean <file>`. Work in `erdos-3/`: `drafts/`, `submissions/NNN-slug/solution.lean`, `reports/`, `journal.html`. Branch `hills/erdos-3`.

Context:
- Statement (from google-deepmind/formal-conjectures, ErdosProblems/3.lean): if A ⊆ ℕ has Σ_{a∈A} 1/a = ∞, then A contains arithmetic progressions of arbitrarily large length k. The k = 3 case is Bloom–Sisask (2020). k ≥ 4 is **open**. There's a $5,000 Erdős prize, administered by erdosproblems.com, not by this event.
- Scoring: `proved` = 1 only if `solution.lean` (the proof after `:=`) compiles with no `sorry` and no axioms beyond propext / Classical.choice / Quot.sound. So `native_decide` (which adds `Lean.ofReduceBool`) and custom axioms fail.
- Realistic assessment: a full proof would solve a famous open problem, so this hill will almost surely stay at 0. The real value of Lean work here is the competition's **M2 track** (new, reusable formalizations of known math, e.g. pieces toward the k = 3 case or density lemmas not in Mathlib) or **M3B variations**. Those need organizer registration.

Plan I want (agree with me first; this is exploratory, not an autonomous overnight loop):
1. Verify the toolchain end to end: confirm the exact `hill` statement in `statement.lean` matches our local formal-conjectures copy, and that a deliberately `sorry`-free trivial lemma in the same context compiles locally.
2. Survey: what does Mathlib already have (Roth/Szemerédi-type results, `IsAPOfLength`, Behrend-type constructions, Kelley–Meka)? Which of the solved `erdos_3.variants.*` in formal-conjectures are still `sorry` and small enough to formalize this week? Report 2–3 candidate M2/M3B targets with effort estimates.
3. Don't submit anything to this hill unless `proved` = 1. Don't try to game the checker (axioms, `native_decide`, statement tricks). A checker gap is a finding to report, not a result.

Stopping criteria: a toolchain check and a written candidate list, within ~2 hours. Then ask me which target to pursue.

If a proof ever checks: ask me before submitting. If yes: `hills eval <best-dir> -H erdos-3 -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes.
