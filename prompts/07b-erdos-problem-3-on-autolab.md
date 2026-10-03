You are climbing the AutoLab hill ottogin/erdos-3 (Lean 4, toolchain v4.33.1, Mathlib inside the hill's image).

Goal and honest framing:
- The theorem `hill` in statement.lean is Erdős Problem #3 (from google-deepmind/formal-conjectures, ErdosProblems/3.lean): if A ⊆ ℕ has Σ_{a∈A} 1/a = ∞, then A contains arithmetic progressions of arbitrarily large length. k = 3 is Bloom–Sisask (2020); k ≥ 4 is OPEN.
- Score `proved` = 1 only if solution.lean (the proof after `:=`) compiles with no `sorry` and no axioms beyond propext / Classical.choice / Quot.sound. `native_decide`, custom axioms, or statement tricks all fail, and they're not acceptable anyway.
- A full proof would solve a famous open problem, so do not expect `proved` = 1. Your job is to produce **useful formal progress and a map of what is feasible**, because the competition also credits new formalizations of known mathematics (M2) and nontrivial variations (M3B).

Work plan:
1. Read README.md, statement.lean, eval.py and examples/. Run `hills eval` on the example to confirm the pipeline and learn how long one check takes.
2. Write down the exact Lean statement and how `answer(sorry)` / `IsAPOfLength` / `Summable` are defined in this context.
3. Survey Mathlib and formal-conjectures: what exists for Roth/Szemerédi-type results, APs (`Set.IsAPOfLength`, `IsAPOfLengthFree`), Behrend constructions, and density/reciprocal-sum lemmas? Which `erdos_3.variants.*` are still `sorry`?
4. Propose 2–3 concrete, formally checkable targets that could be finished this week. Examples: a clean formal reduction such as "if r_k(N) ≤ N/(log N)^{1+ε} for all large N, then the k-case holds", the partial-summation step linking r_k bounds to divergent reciprocal sums, or small special cases. For each, estimate effort and state whether it's known mathematics (M2) or a variation (M3B).
5. Formalize the most promising target in a separate Lean file. Check it by compiling (with the same toolchain) and keep it `sorry`-free. Commit each working step.

Rules:
- Never read private/. Never edit reports. Don't submit to the hill unless `proved` = 1, and ask me first.
- Keep a journal (journal.html or JOURNAL.md): what you tried, what compiled, what failed and why, and the current best artifact.
- Record the model/tool versions used, for the competition's disclosure requirements.
- Stop and report after the survey (step 4) so I can choose the target, then continue autonomously on the chosen one.
