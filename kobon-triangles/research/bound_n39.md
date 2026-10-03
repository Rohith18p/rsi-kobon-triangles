# Upper bound for n = 39, and how close we can realistically get

Date: 2026-09-27. Our standing: #1 on the n=39 board with **469** (`added/n39_469_u38-grow.json`).
During this session the team's search also produced **470** (`lns/n39_470_*.json`, six files). I re-checked one with `verify_independent.py`: 470. **[V]**

Legend:
- **[V]** = verified: quoted verbatim from a source I have locally, or reproduced by my own exact / solver computation.
- **[I]** = inference, heuristic or numerical evidence, not a proof.

Scratch work is in `/tmp/k39`, `/tmp/pseudoline-algorithms`, `/tmp/kobon-cnf` and `/tmp/kissat`. All kept artefacts are under `research/`.

## TL;DR

- **Best provable upper bound: 481** = n(n−2)/3 (Tamura / Felsner–Kriegel). **[V]**
  - Nothing stronger is known for n=39 in any model.
  - Reaching it is **combinatorially possible**: Parpalak–Utkin publish explicit *perfect* simple pseudoline arrangements of 39 pseudolines with 481 triangles. I independently recounted 556 such wiring diagrams: all have K=481. **[V]**
  - So no pseudoline or counting argument can lower the bound. Only a **stretchability** obstruction could, and none is known.
- **What is excluded [V]:**
  - Only Savchuk's exhaustive SAT result: there is no perfect 39-line table with **13-fold rotational symmetry** (0 tables, 1h28m, Kissat).
  - My SAT run for **3-fold rotation (−R 3)** is **SAT**: it found **two C3-symmetric perfect pseudoline tables** for n=39 (recounted K=481). This is new; Savchuk only reported R13 = UNSAT.
  - Both tables resisted straightening (my stretcher: 459 and 384 violations; Savchuk's symmetric fit.py: at best 316/481 triangles).
  - The **mirror (−M)** run is undecided (§3.3).
  - Nothing else about n=39 is ruled out in the literature.
- **How close is realistic [I]:**
  - Every n=39 perfect wiring diagram I tried (46 diverse ones) failed to stretch. The residuals were large (~290–390 violated local-order constraints of 1443).
  - The stretchable fraction of perfect arrangements drops steeply with n. Published: n=19 ≈ 99.5%, 23 ≥ 45%, 25 ≥ 5%, 27 ≥ 0.6%. My n=27 calibration found 2/201 ≈ 1%.
  - So a straight 481 needs a *structured* (symmetric / constructed) candidate, not random DFS output.
  - On the straight side (§4.2):
    - the best single line added to **any of the 248 gallery 38/450 arrangements** gives **470**;
    - our 469 and all six team 470s are **exact local optima under 1-line replacement**.
    - So progress beyond 470 needs multi-line moves or a new global structure.

## 1. The bound and the perfect-arrangement characterization

### 1.1 Tamura / segment bound

- Clément–Bader 2007 (draft; `papers/clement_bader_2007_oeis_cache.txt`) **[V]**:
  > "Saburo Tamura has proved that K(n) ≤ ⌊n(n − 2)/3⌋ (1) is an upper bound on K(n)."
- Their Prop. 1 ("the maximal number of segments is equal to n(n−2)") is the counting basis.
- For n=39: 39·37/3 = **481**, an integer (39 ≡ 3 mod 6).
- In the simple case the proof is one line. There are n(n−2) bounded segments, each bounded segment borders at most one triangular face (Parpalak–Utkin 2607.29236 §2.3, **[V]**), and 3·a3 + u = n(n−2).

### 1.2 Does it hold for non-simple arrangements (parallels, multi-points)?

- **Felsner–Kriegel 1999**, *Triangles in Euclidean arrangements*, DCG 22:429–438 (author PDF https://page.math.tu-berlin.de/~felsner/Paper/tri.pdf, text extracted to `/tmp/fk_tri.txt`) **[V]**:
  > "Theorem 2. For every arrangement B of n pseudolines in E: (1) If B is simple then p3(B) ≥ n − 2. … (2) If n ≥ 6 then p3(B) ≥ 2n/3 … (3) p3(B) ≤ n(n − 2)/3. Equality is possible for infinitely many values of n."
  - Part (3) has **no simplicity hypothesis**.
  - Their Euclidean arrangements are projective arrangements with one pseudoline declared "line at infinity". Two pseudolines may meet on that line, so **parallel lines are included**, as are multi-points.
  - The proof is only sketched:
    > "The upper bound on the number of triangles in the Euclidean case claimed in (3) of Theorem 2 can be proved along the lines of Roudneff's upper bound for the projective case. The proof is long and the changes necessary to adapt it to the Euclidean case are obvious. Therefore, we will refrain from elaborating on it and refer to Roudneff's original paper [Rou96]."
  - Roudneff 1996 (JCTB) proved Grünbaum's non-simple projective bound p3 ≤ n(n−1)/3 (for n beyond a small threshold; the exact symbol is garbled in the extraction).
- Parpalak–Utkin 2607.29236, intro **[V]**:
  > "perfect arrangements solve both the Kobon problem (including the general non-simple case, for which the same upper bound holds [12])" ([12] = Felsner–Kriegel).
- **Conclusion:** 481 is a valid upper bound for the hill's model (straight lines, parallels and multi-points allowed). **[V]** as a published statement. Its non-simple proof is published only as a sketch, which is irrelevant for us since we are below it.
- **[V] Caution on the naive per-line argument.** In non-simple arrangements a line can touch more than n−2 triangles.
  - Example, 5 lines: y=0, y=x, y=−x, y=2x+2, y=−2x+2. The line y=0 has only 2 bounded edges, both on 2 triangles each. It therefore touches 4 > n−2 = 3 triangles.
  - Hill evaluator count: T=4. Ledger: E=12, M=2, a2=2.
  - So any proof for non-simple arrangements must be global, as in Roudneff / FK. It cannot be done line by line.

### 1.3 Does hitting 481 force a perfect *simple* arrangement?

- Clément–Bader **[V quote; proof informal]**:
  - Def. 1: "A perfect configuration is an arrangement of n pairwise intersecting lines, where each segment is the side of exactly one nonoverlapping triangle and K(n) meets the upper bound (1)."
  - Lemma 1: "If (n mod 3) ∈ {0, 2}, then all configurations that meet the upper bound (1) are perfect configurations."
  - Lemma 2 proof: "In a perfect configuration not more than two lines intersect in the same point because otherwise the number of line segments would decrease …"
  - Lemma 3: "A perfect configuration exists only for odd n."
  - Theorem 1: the bound drops by 1 for n ≡ 0, 2 (mod 6).
  - The key step of Lemma 1 for multi-points: a point where 3 lines meet costs 3 segments but "saves at most two" (two shared sides). It is argued from pictures only, e.g. "every intersection point with more than two corresponding lines is part of at most two pairs of triangles that share a common side".
- For n=39 (≡ 0 mod 3), CB therefore claim that **481 ⇒ perfect ⇒ no parallels and no multi-points**. **[I]**: I believe it (it matches all data), but the only written proof is CB's informal Lemma 1.
- Our own ledger identity **[V]**: 3T = E − M + a2, where E is the number of bounded edges, M the unused edges and a2 the edges shared by two triangles.
  - For 481 we need E − M + a2 = 1443 = n(n−2).
  - Every triple point lowers E by 3, and every parallel pair lowers E by 2. So a non-simple 481 needs a2 − M ≥ (edge deficit), i.e. more than 1.5 shared edges per triple point.
  - Every record we have measured has a2 = 2 per triple point. That leaves a net loss of 1 per triple point, and 469 fits this: E=1434 (3 triple points), M=33, a2=6.
- Parpalak–Utkin equivalences for simple arrangements **[V]** (2607.29236 Lemmas 2.2, 2.3, 2.5):
  - perfect ⇔ defect-free;
  - all triangles share one checkerboard colour;
  - every external black face is an external digon.
- Projective reformulation **[I, elementary]**:
  - A perfect 39-line arrangement plus the line at infinity is a simple projective arrangement of 40 lines with 481 + 39 = **520 = 40·39/3** triangles. That attains the Roudneff/Harborth projective bound, with every line on exactly 39 triangles.
  - Conversely, deleting any line of such a 40-line projective arrangement gives a perfect 39.
  - So "481 is achievable" ⇔ "there is a **straight** projective 40-line arrangement with 520 triangles".

## 2. Literature search 2020–2026: what is known about n = 39

| Source | n=39 content | Status |
|---|---|---|
| OEIS A006066 (fetched 2026-09-27) | table entry "39 ?" | no value, no bound beyond Tamura **[V]** |
| Savchuk 2025, arXiv 2507.07951, Table 1 | row "39, −R 13, tabs 0, T_gen 1h 28m, vars 165984, clauses 13788528" | **exhaustive UNSAT**: no perfect simple pseudoline table of 39 lines with 13-fold rotational symmetry (Kissat v4.0.2). Nothing else for 39 **[V]** |
| Parpalak–Utkin 2026b, arXiv 2607.29236, Table 4 and Cor. 7.1 | first-hit perfect search reaches n=39 in "T = 19ms"; "A triangle-maximal simple pseudoline arrangement, attaining the bound (2.3), exists for every odd n ≤ 89 except n = 11"; the word is in `data/partial/39.from36.asc.words-part.txt` | perfect **pseudoline** 39 **exists** **[V]** (recounted: K=481). Stretchability "not considered: the results are combinatorial" |
| same, §7.5 | 39 is *reducible* (not in the irreducible list 3, 7, 11, 19, 31, 43, …). The only applicable construction is Bokowski–Roudneff–Strempel n ↦ 8n−1 from n=5 | pseudoline construction; stretchability unknown **[V/I]** |
| Parpalak–Utkin 2026a, arXiv 2604.22035 | straight series 18·2^t+1 (19, 37, 73, …), one-step 41, 45, 49; "as n increases, the proportion of stretchable arrangements among the enumerated optimal pseudoline arrangements appears to decrease" | nothing for 39. BBL doubling needs an even base (Prop 3.1: "Let n ≥ 2 be an even number …" gives 2n+1), so **39 = 2·19+1 is not a doubling size** **[V]** |
| BBL 2008 / Blanc 2011 | bounds only for even n (simple) | irrelevant for 39 (odd n: Tamura is best) **[V]** |
| Web search (2026-09) | no paper, record or impossibility result for 39 lines | **[V]** (negative search) |

**Net [V]:** no result rules out 481 for n=39, and none gives a stronger bound. The only exclusion is the 13-fold rotationally symmetric perfect case.

### 2.1 Necessary conditions for a perfect n=39 arrangement (computationally checkable)

1. Simple: 741 distinct crossings, no parallels (CB Def. 1 and Lemma 2; informal for non-simple, see §1.3).
2. Every line touches exactly 37 triangles, alternating sides along the line (CB Lemma 3; PU Lemma 2.2 proof).
3. Checkerboard: all 481 triangles black; the 222 other bounded faces white. External faces alternate, and the 39 black ones are digons (PU Lemma 2.3). Arnold excess b−w = 520 − 261 = **259**: the DFS reports A=259 for every word **[V]**.
4. Extremal vertices have degree 2 (CB Lemma 2): consecutive lines at infinity cross at their mutual last vertex.
5. Reduced-word normal form (PU §4, Lemmas 4.1–4.6 and Cor. B.7). The word is σ37 σ35 … σ1 followed by composite generators K_g = σ_g σ_{g−1} σ_{g+1}, with no consecutive repeat of K_g, subject to the wall-debt constraints. `search/perfect` enumerates exactly these (complete by PU Thm 4.10).
6. Symmetry: rotation order 13 is impossible (Savchuk). Projective symmetries of the 40-line closure are the natural next classes: C3 fixing the line at infinity (= −R 3), D1 (= −M), and a C5 or C8 acting freely on the 40 lines.
7. Stretchability, the only open obstruction. For fixed slopes, the realization problem is an **LP in the intercepts**, so an infeasibility certificate exists for each slope vector. Globally it is ∃R-hard.

## 3. Computational contribution

### 3.1 Perfect pseudoline words for n=39 [V]

- Built `pseudoline-algorithms/search/perfect` in `/tmp` and generated 556 wiring diagrams:
  - 443 consecutive DFS outputs (descending branch order), 30 s;
  - 85 consecutive outputs (ascending order);
  - 27 first hits over `-from H` for H = 2..36 in both orders;
  - plus the published word.
- An independent recount (triangle = triple whose three pairwise crossings are consecutive on all three lines) gives **K = 481 for all 556**.
- Files: `research/n39_candidates/perfect_pseudoline_words/`.

### 3.2 Stretching attempts [V for the runs, I for the interpretation]

- Tool: `research/tools/stretch39/stretch2.py`.
  - Lines y = m x + b with slope order enforced through angles = π/2 − π·cumsum(softmax(u)).
  - Squared-hinge loss on the 1443 consecutive local-order constraints, L-BFGS.
  - Initialized from the word by alternating least squares on crossing "times".
  - Finished with an exact-feasibility **LP in b for the found slopes** (HiGHS, margin δ).
- Calibration:
  - n=15 and 17: 1/1.
  - n=21: **11 of 18** P-classes, exactly PU's published "≥ 11".
  - n=27: 2 of a 201-class sample (PU: ≥ 348/56646).
  - Straight 41-, 43- and 45-line perfect optima from the gallery, converted to words and re-stretched from scratch: all succeed in under 3 s.
- n=39: **46 diverse perfect words (19 consecutive + 27 first hits) all fail.** They end at 288–390 violated constraints out of 1443, with LP margin δ ≤ 0. Logs: `res_seq.jsonl`, `res_from.jsonl`.
  - The residuals are large, not near-misses of a few constraints.
  - This is **not a proof** of non-stretchability.
  - Using near-stretches as straight seeds gives ≤ 218 triangles, so it is useless.

### 3.3 SAT: symmetric perfect n=39 (kobon-cnf + Kissat 4.0.4, 1 thread each)

- `gen.py 39 -R 3`: CNF 165,984 vars, 13,225,368 clauses.
- `gen.py 39 -M`: 165,984 vars, 13,169,052 clauses.
- Both started 15:51.
- **−R 3: SAT twice [V].**
  - Kissat solved the first model in about 30 min wall. That model has 165,984 vars and 13,225,368 clauses and gives table 0.
  - With table 0 blocked, it gave table 1 in about 4 min.
  - `research/n39_candidates/c3_perfect_pseudoline/kobon-39-rot3_tables.txt` holds the tables; `r3word_{0,1}.txt` hold wiring words from `tools/stretch39/tab2word.py`, validated as reduced words of the longest permutation.
  - My independent count gives K = 481 for both.
  - Straightening failed: stretch2 with 12 restarts ends at 459 and 384 violated constraints (LP δ = 0), and `fit.py 39 -R 3` with its built-in parameter sets gives at best 316/481. **[I]** These two tables look non-stretchable (not proven).
- **−M: undecided** at write-up; still running (see §6).
- If either returns a table, straighten it with `fit.py 39 -R 3` (needs `mkdir fit/imgs`; deps in `/tmp/pdfenv`). This was tested end to end on n=15 −R 5: 65/65 straight.
- An UNSAT answer would be a new exclusion, logged by Kissat as `s UNSATISFIABLE`.
  - It covers Savchuk's table model: simple perfect pseudoline arrangements whose table is invariant under his rotation or mirror map.
  - For a checkable certificate, rerun with `kissat --no-binary in.cnf proof.drat` and check with drat-trim.
- Budget note: two extra `--sat --seed=7` portfolio runs were started and then killed to respect the 4-thread cap.

## 4. Constructive guidance: 470–481 for n = 39

### 4.1 Routes, ranked [I]

1. **Symmetric perfect (481, optimal)**:
   - C3 about a point (−R 3), mirror (−M), or projective symmetries of the 40-line closure.
   - Savchuk's n=27 C3 run: 86 tables, **5 straightened** (≈ 6%), versus ≈ 0.6–1% for unsymmetric n=27 classes. Symmetry therefore increases stretchability as well as shrinking the search.
   - Tools: `/tmp/kobon-cnf` (gen.py/fit.py), `/tmp/kissat/build/kissat`, `research/tools/stretch39/stretch2.py`.
   - Clones to recreate: github.com/zegalur/kobon-cnf, zegalur/line-order, arminbiere/kissat, parpalak/pseudoline-algorithms.
2. **Near-perfect pseudoline + stretch (T = 481 − k needs 3k unused segments)**. Two ways to get these:
   - kobon-cnf `-L l1,l2,l3` (three lines each with one missing triangle gives 480), best combined with −R 3 so that one orbit carries the defects;
   - PU's defect-budget DFS.
   - Much larger family, so more likely stretchable. The `-L` model adds ~n⁴ clauses per entry.
3. **BRS 8n−1 construction from the 5-line optimum.** It yields a perfect 39 in pseudolines, but stretchability is unknown.
   - It is highly structured, so it is a better stretching candidate than DFS output.
   - Not attempted: the construction details are in Bokowski–Roudneff–Strempel (ref. [18] of 2607.29236), not local.
4. **Straight-line "base + lines"** (our current method): the exhaustive results below show it is near its limit for the known bases.

### 4.2 Exhaustive single-line insertion (new tool) [V]

- `research/tools/exhaustive_insert.py` enumerates **every combinatorial position of one added straight line**. It visits every dual vertex:
  - lines through two base vertices;
  - lines through one vertex parallel to a base line;
  - plus their perturbations into each adjacent edge and cell.
- Scoring is incremental in floats (eps 1e-12, tiny-triangle-safe area threshold 1e-22). Winners are re-verified with the **exact hill counter**.
- Caveat: positions nearly coincident with an existing line (both defining vertices on the same base line) are skipped.
- Sanity checks:
  - remove/reinsert on the 17/85 optimum recovers 85 for every line;
  - 16/72 + 1 gives 80.
- Results **[V]** (every reported count is exact-verified):

| Experiment | Result |
|---|---|
| Published 38/450 (`records/n38_450_*`) + best line | **469** (7.5 s). No single added line beats 469 |
| Our 38/449 (`derived/base_p38.json`) + best line | 468 |
| **All 248 gallery 38/450 bases** (`derived/g38/`) + best line | **max 470**. Distribution: 466×4, 467×28, 468×70, 469×135, 470×11. Float = exact on all 248. Log: `n39_candidates/exins_g38/scan_g38.jsonl`; the eleven 470s are saved there |
| Exact 1-line replacement, our 469 | all 39 removals → best reinsertion **469**: a local optimum |
| Exact 1-line replacement, the six team 470s (`lns/n39_470_*`) | all 6×39 removals → best reinsertion **470**: all are local optima |
| 37/431 (`derived/base_p37.json`) + 2 lines, beam K=12 (earlier tool version) | 468 |

- **Conclusion [V, within the tool's scope]:** "38-line gallery arrangement + 1 line" can reach at most 470.
  - Every 470 we hold is a strict dead end for single-line moves.
  - Beating 470 needs **multi-line moves** (e.g. remove 2–4 lines and exhaustively reinsert them with a beam), different bases (non-gallery 38s, 40/41-line deletions), or the perfect/near-perfect routes of §4.1.
- One insertion takes about 6–9 s on 2 threads. A 2-line remove/reinsert with a beam of K costs about (1+K)·8 s per line pair, which is feasible for hundreds of pairs.
- Tool-scope caveat: candidate lines that nearly coincide with an existing line are skipped. This was needed to avoid float artefacts, and those configurations are sliver-only.
- Bug history, fixed and regression-tested on 17/85 and on the originals of all 470s:
  - tiny-triangle area threshold;
  - tolerance mismatch;
  - missing "parallel to a base line" events.

### 4.3 What it would take numerically [I]

- **Empirical identity [V on the 5 arrangements whose ledgers I ran: our 469, three team 470s, one exins 470]:** a2 = 2k, where k is the number of triple points, so **3T = 1443 − k − M**.
  - Examples: 469 has k=3, M=33; the 470s have (k, M) = (4, 29), (5, 28), (6, 27).
  - Hence 471 needs k + M = 30, 475 needs 18, and 481 needs k = M = 0 (simple and perfect).
- 470 needs E − M + a2 = 1410.
- The simple-arrangement path means ≤ 33 unused edges; our 469 is at M=33 with 3 triple points (E=1434, a2=6).
- Each additional "good" triple point is worth +1 over a generic crossing only if it comes with 2 shared edges. Otherwise the gain must come from lowering M.
- Moving from 469 to 481 means eliminating all 33 unused edges, i.e. a globally perfect structure. Local search is unlikely to get there; that needs routes 1–3.

## 5. Reproduction

- **Perfect words:**
  ```
  make -C /tmp/pseudoline-algorithms/search/perfect
  ./perfect_asc -n 39 -first -from 36
  ```
- **Stretching:** `uv run python research/tools/stretch39/stretch2.py 39 <wordfile> <idx>`
  - Batch: `NP=2 uv run python research/tools/stretch39/batch.py 39 f1,f2 <tries> out.jsonl`
- **SAT:** `cd /tmp/kobon-cnf && PATH=/tmp/kissat/build:$PATH python3 gen.py 39 -R 3` (or `-M`).
- **Exhaustive insertion:**
  ```
  NUMBA_NUM_THREADS=2 uv run python research/tools/exhaustive_insert.py insert base.json --out dir
  NUMBA_NUM_THREADS=2 uv run python research/tools/exhaustive_insert.py lns arr.json
  uv run python research/tools/beam_insert.py base37.json --k 12
  ```

## 6. Final status of long runs (17:25)

- **kobon-cnf −R 3 (n=39)**: 2 tables found (15:51→16:21 and →16:25). A third model has been running since 16:25; `gen.py` keeps blocking found tables.
  - Test new tables with `uv run python research/tools/stretch39/test_tables.py /tmp/kobon-cnf/res/kobon-39-rot3.txt 2`.
- **kobon-cnf −M (n=39)**: undecided after about 4400 s of Kissat CPU (1h30m wall; paused about 10 min while stretching).
- Both jobs are left running on 1 thread each, logs in `/tmp/k39/gen_R3.log` and `/tmp/k39/gen_M.log`.
  - A watchdog kills them at about 19:35: `sleep 10800; pkill -f "gen.py 39"; pkill -f "kissat tmp/in-kobon-39"`.
  - Stop earlier with `pkill -f "gen.py 39"; pkill -f "kissat tmp/in-kobon-39"`.
- All numba and stretch jobs have finished. No solver certificate (DRAT) was produced, because no run returned UNSAT.
