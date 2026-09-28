# Kobon triangles: what we established, what we observed, what is only conjectured

Labels:
- **[P]** proved here (elementary)
- **[C]** computational fact (exact, reproducible)
- **[E]** empirical pattern, not proven
- **[K]** already known in the literature

"Not found in the literature" means not found in our survey (research/literature.md, research/bound_n39.md). It does not guarantee novelty.

Notation (all exact):
- n = number of lines, T = number of triangles
- k = triple points, p = parallel pairs
- E = bounded segments
- M = unused segments
- a2 = segments shared by two triangles

## 1. Accounting identities
1. **[P] Double counting:** 3T = (segments used once) + 2·a2 = E − M + a2. Verified on every result.
2. **[P] Segment count:** E = n(n−2) − 3k − 2p, when no point has 4 or more lines.
   - A triple point merges 3 crossings into 1, so each of its 3 lines loses one segment.
   - A parallel pair loses one crossing on each of its 2 lines.
   - [C] Held in 330 of 330 arrangements, n = 6–54.
3. **[K] Simple arrangements:** a2 = 0, so 3T = n(n−2) − M (Parpalak–Utkin 2607.29236 §2.3).
4. **[E] Shared-segment rule:** a2 ≤ 2k. Each triple point creates at most 2 shared segments.
   - [C] Held in 330 of 330: equality in 323, strictly less in 7.
   - Clément–Bader (2007) claim this informally, from pictures. No written proof exists.
5. **Consequence of 1, 2 and 4:** 3T ≤ n(n−2) − k − 2p − M.
   - A triple point costs 1 unit of budget; a parallel pair costs 2.
   - They help only by reducing wasted segments M. This explains why records use them sparingly.
   - Corollary: T = ⌊n(n−2)/3⌋ with n ≡ 0 (mod 3) forces k = p = M = 0, so the arrangement must be perfect and simple. That gives a clean proof of Clément–Bader's Lemmas 1–2, provided the rule in item 4 is proved.
6. **[C] All five n=18 records we measured have the same total defect,** k + 2p + M = 9, spent in different ways:
   - 9 unused segments (ours, simple)
   - 4 triple points + 5 unused
   - 3 triple points + 1 parallel pair + 4 unused
   - 4 parallel pairs + 1 unused
   - 1 parallel pair + 7 unused

## 2. Main conjecture (generalized Blanc bound), not found in the literature
- **[E] For even n:** k + 2p + M ≥ n/2 − 1, i.e. **T ≤ ⌊(n−2)(2n−1)/6⌋**.
  - [C] No violation among 330 arrangements.
  - The formula equals the best known value for every even n from 4 to 38, and for 42, 46, 50 and 54.
- **Relation to known results:**
  - Blanc (2011) proved M ≥ n/2 for **simple** arrangements [K].
  - The conjecture extends this to non-simple arrangements, at a cost of at most 1.
  - For n ≡ 0 or 4 (mod 6) it gives the same number as Blanc's simple bound, so triple points and parallels would never help.
  - For n ≡ 2 (mod 6) it allows exactly +1, which matches every known record (8, 14, 20, 26, 32, 38, 50).
- **If proved:**
  - **94 is impossible for n=18**, so a(18) = 93. That's an open question today; the published general bound is 95 or 96.
  - 118 is impossible for n=20, making a(20) = 117 rigorous for general arrangements.
  - It would close many "open" even cases (22, 24, 28, 30, 34, 36, …) at their current best known values.
- **Testable prediction:** n=44 → 609, using a triple point. Our simple 608 already meets Blanc's simple bound. A single anchored insertion only reached 608, so the prediction is not yet confirmed.

## 3. New computational facts
- **[C] n=39 SAT results:**
  - 3-fold-symmetric **perfect** (481) pseudoline arrangements exist (bound agent). Previously only the 13-fold case had been tested, and it was UNSAT.
  - 3-fold-symmetric **near-perfect** pseudoline arrangements with 475, 477 and 480 triangles exist (our SAT runs).
- **[E] None of these could be straightened:**
  - 46 perfect words, all 3-fold tables, and the 475–480 tables all failed.
  - That's evidence the near-perfect region at n=39 is not stretchable. It is not a proof.
- **[C] Exhaustive single-line insertion:** over all 248 published 38/450 realizations, the best 39-line arrangement has exactly **470**.
  - None of those realizations extends to 471 or more by one line.
  - The statement is about these realizations, not every realization of their combinatorial types.
- **[C] Our 470s are strict local optima** under 1-line replacement. We also searched about 1,800 2-line moves without improvement.
- **[C] Doubling (BBL Prop 3.1) works with much larger constants** than the proof needs: δ = n^−4 and ε₂ = n^−2, instead of n^−10 and n^−6.
  - This keeps all coefficients below 10^30, even for 97 lines.
  - It gives explicit integer realizations of the optimal 49, 57, 65, 73 and 97.
  - Bases found by search (not perfect) double correctly as well: T(2n+1) = T(base) + n², e.g. 31/290 → 61/1190 and 35/338 → 69/1494.
- **[C] Deleting any one line from a perfect odd-n arrangement** loses exactly n−2 triangles. Occasionally the greedy choice gains 1 back (73 → 72: 1657; 97 → 96: 2977).

## 4. New lower bounds (first values for n with no published arrangement; exact, verified)
- 39: 470 (AutoLab #1)
- 40: 494
- 44: 608 (simple, meets Blanc's simple bound)
- 47: 691
- 48: 721
- 51: 815
- 52: 850
- 55: 954
- 56: 990
- 58–61: 1036, 1086, 1137, 1190
- 62–64: 1185, 1243, 1302
- 66–72: 1329, 1383, 1438, 1494, 1525, 1590, 1657
- 74–96: from peeling the 97-line arrangement (e.g. 96: 2977)

Most are simple operations (insert, delete, double) on published constructions, so credit is shared. Several are clearly improvable (e.g. 62 < 61).

## 5. What we did NOT establish
- No impossibility proof for any n.
- No proof of the shared-segment rule or the main conjecture.
- The Tamura bound of 481 for n=39 is still the only proven upper bound.
