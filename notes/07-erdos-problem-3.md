# 7. Erdős Problem #3 ($5,000 prize)

**Hill:** [ottogin/erdos-3](https://app.autolab.ai/hills/ottogin/erdos-3) · v0.1.0
**Reference:** [erdosproblems.com/3](https://www.erdosproblems.com/3)

## The problem in one line
If a set of natural numbers `A` has **Σ_{n∈A} 1/n = ∞**, must `A` contain **arbitrarily long arithmetic progressions**?

## Background
- **k = 3 is solved:** any such A contains a 3-term AP (Bloom–Sisask, 2020).
- **k ≥ 4 is open.** This would strengthen Szemerédi's theorem. Related bounds on `r_k(N)` come from Gowers, Green–Tao, Kelley–Meka, and Leng–Sah–Sawhney.
- Erdős offered **$5,000** for a proof or disproof. The prize is run by erdosproblems.com, **separately** from this competition.

## Task
Write a **machine-checked Lean 4 proof** of the fixed theorem `hill` (Lean toolchain v4.33.1 with Mathlib).
- The statement comes from Google DeepMind's [formal-conjectures](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/3.lean) repo. Its core is:
  ```lean
  ∀ A : Set ℕ, (¬ Summable fun a : A ↦ 1 / (a : ℝ)) →
    ∃ᶠ (k : ℕ) in Filter.atTop, ∃ S ⊆ A, S.IsAPOfLength k
  ```
- You write **only the proof** after `:=`. Don't restate the theorem or add imports.

## What you submit
A folder containing `solution.lean`, holding a proof term or a `by ...` tactic block.

## Scoring
| Metric | Direction | Meaning |
|---|---|---|
| `proved` | maximize | 1 if the proof compiles |

The proof must compile with **no `sorry`** and use **no axioms** beyond `propext`, `Classical.choice`, `Quot.sound`.

## Key takeaways
- It's all or nothing: a full proof means solving a famous open problem.
- The hill README says partial or related results are welcome, but the only score is `proved`.
- For realistic contributions, look at the solved variants in the same Lean file (for example the k = 3 case), which could qualify under the competition's separate **formalization** category.
