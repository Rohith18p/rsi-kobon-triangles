# Kobon triangles, n = 39: 470 triangles

**Team:** rohith18p · Open Math Challenge (Open Problems Hack at MIT, 27 Sep – 2 Oct 2026)
**Hill:** AutoLab [`alejandrozu/kobon-triangles`](https://app.autolab.ai/hills/alejandrozu/kobon-triangles) v0.1.0
**Status as of 2 Oct 2026:** officially scored **470** (submitted 27 Sep), currently **#2** on the n = 39 board

---

## 1. Result at a glance

| | |
|---|---|
| Lines | 39 straight lines, exact integer coefficients (a·x + b·y + c = 0) |
| Triangles (bounded faces no line crosses) | **470** |
| Upper bound | 481 = ⌊39·37/3⌋ (Tamura; holds for all arrangements, Felsner–Kriegel 1999) |
| Published value before this event | none: OEIS [A006066](https://oeis.org/A006066) lists a(39) as "?" |
| Solution file | [`kobon-triangles/n39_470/solution.json`](kobon-triangles/n39_470/solution.json) |
| sha256 | `85ce027ccddc91365ff1f798702fc8ae19838c0d244cd426406f2d3f9b3aa352` |
| Reproduce | `sh kobon-triangles/n39_470/reproduce.sh` rebuilds it byte-identically in about 6 s |

### Official evaluation (AutoLab)

| Field | Value |
|---|---|
| Climb / experiment | `rohith18p/kobon-triangles`, experiment `23e84fc7` ("n39-470") |
| Hill tree hash | `7d3f1d91dcb8be8d0eef20be763557bd6d876707` |
| Params | `n = 39` (primary config: exact-rational arithmetic, bounded-triangular-faces) |
| Report | `passed: true`, `official: true`, `triangles = 470`, timestamp `2026-09-27T19:45:26Z` |
| Submission hash | `sha256:94d4b2efa8681396064459eebdf5f1411def9590a79ef75abdc05d4db417e7ee` |
| Signed report | [`kobon-triangles/n39_470/official_report.json`](kobon-triangles/n39_470/official_report.json) |

### Leaderboard, n = 39 (checked 2 Oct 2026)

| Rank | Entrant | Triangles | Submitted (UTC) |
|---|---|---|---|
| 1 | lavaskiller | 471 | 2026-10-02 17:58 |
| **2** | **rohith18p (us)** | **470** | 2026-09-27 19:45 |
| 3 | octavianboji | 468 | 2026-09-27 18:39 |

From 27 Sep to 2 Oct our 470 was #1 and the best known value anywhere. A 471 was submitted on 2 Oct.

---

## 2. How the 470 is built

**In one sentence:** take a published 38-line arrangement with 450 triangles, then add the single best possible 39th line. That line creates **20 new triangles and destroys none**.

1. **Base: 38 lines, 450 triangles.**
   - Gallery file `38-74kq3v76alw` from the Parpalak–Utkin gallery ([ud1/kobon-solutions](https://github.com/ud1/kobon-solutions), commit `cecd2b1`, file `gallery/data/38/38-74kq3v76alw.json`).
   - 450 is the best known value for n = 38.
   - It has 5 triple points (three lines through one point).
2. **Exact integers.** The gallery stores floating-point slopes and intercepts plus a combinatorial word.
   - We convert to exact integer lines with the gallery's own rationalizer ("compact-rationalized", D = 100), using [`research/tools/ud1_to_hill.py`](kobon-triangles/research/tools/ud1_to_hill.py).
   - The conversion preserves the triple points exactly and gives at most 11-digit coefficients. It is checked against the word's own count (450).
3. **Best 39th line** ([`src/grow.py`](kobon-triangles/src/grow.py), scoring in [`src/lns.py`](kobon-triangles/src/lns.py)).
   - **Candidates:** 720 directions (with a fixed random sub-step offset, seed 0). For each direction, a line through the middle of every gap between consecutive projected crossing points, i.e. every combinatorially different position at that angle.
   - **Scoring** is incremental, O(n³) per candidate: surviving old triangles plus new triangles that use the new line, in float64 (numba, parallel).
   - **The winner is rounded** to integers (scale 10¹²) and **re-counted exactly**.
   - **The added line** is `490546541635·x + 96768230790·y − 82521729656546 = 0` (slope ≈ −5.0693, intercept ≈ 852.78).
4. **Verification.**
   - Two independent exact counters agree on 470: [`src/count.py`](kobon-triangles/src/count.py) and [`research/tools/verify_independent.py`](kobon-triangles/research/tools/verify_independent.py).
   - The counting identity holds (section 3).
   - The contest's own evaluator scored it 470 officially.

### Why this base and line? The full sweep

We applied the same best-line step to **all 248** 38-line arrangements with 450 triangles in the gallery:

| Best with 39 lines | 466 | 467 | 468 | 469 | 470 | ≥ 471 |
|---|---|---|---|---|---|---|
| bases (exhaustive insertion, `research/tools/exhaustive_insert.py`) | 4 | 28 | 70 | 135 | **11** | **0** |

- Eleven bases reach 470 and none reaches 471. The exhaustive tool enumerates every combinatorial position of the new line, so for these 248 drawings **one added line can never give more than 470**.
- The faster grid version ([`n39_470/scan_all_bases.sh`](kobon-triangles/n39_470/scan_all_bases.sh), the same method as step 3) finds the same eleven 470s.

---

## 3. Anatomy of the arrangement

| | 38-line base | **Our 39** |
|---|---|---|
| Triangles | 450 | **470** |
| Crossing points (distinct) | 693 | 731 |
| Triple points | 5 | 5 |
| Parallel pairs | 0 | 0 |
| Bounded segments | 1,353 | 1,428 |
| Segments used by exactly one triangle | 1,330 | 1,390 |
| Segments shared by two triangles | 10 | 10 |
| Unused segments | 13 | 28 |
| Largest coefficient | 11 digits | 14 digits |
| Tamura bound ⌊n(n−2)/3⌋ | 456 | 481 |

**Counting identity** (checked exactly): 3 × triangles = (segments used once) + 2 × (segments shared by two). For the 39: 3 × 470 = 1,390 + 2 × 10 = 1,410.

**Where the gap to 481 goes.**
- With k triple points and every triple point making 2 shared segments, 3T = n(n−2) − k − M, where M = unused segments: 1,443 − 5 − 28 = 1,410 ✓.
- Reaching 481 requires k = M = 0, a *perfect* arrangement with no triple points.
- Reaching 471 needs k + M ≤ 30; ours has 33.

**Shape.** The arrangement spans many orders of magnitude, with a dense central fan of nearly concurrent lines. The slide deck shows a zoom on the added line's 20 triangles ([`notes/kobon_deck.pdf`](notes/kobon_deck.pdf), slide 10).

---

## 4. Reproducing everything

### Requirements
- macOS or Linux, `git`, [`uv`](https://docs.astral.sh/uv/). Python 3.12 dependencies are pinned in [`pyproject.toml`](pyproject.toml) and `uv.lock`: numpy, numba, scipy (HiGHS), sympy, python-sat, …
- **No SAT solver or proprietary tool is needed for the 470.** It is exact integer geometry plus a numba search.
- Internet access to github.com, to fetch the third-party gallery at the pinned commit. Its data and code are not redistributed here: the repository states no license.

### Commands (from the repository root)
```sh
uv sync                                                    # create the Python environment
uv run python kobon-triangles/n39_470/verify.py            # verify the submitted solution (470)
sh kobon-triangles/n39_470/reproduce.sh                    # rebuild from the gallery; byte-identical check
sh kobon-triangles/n39_470/scan_all_bases.sh               # full 248-base sweep and distribution
```
`reproduce.sh` prints `REPRODUCED: byte-identical to kobon-triangles/n39_470/solution.json`. Its steps:
1. fetch `ud1/kobon-solutions` at `cecd2b1b4dd77f6a2453ec45676e4698cd8956f9`
2. convert the base
3. add the best line (deterministic)
4. verify with both counters

### Official score
The hill has private held-out fixtures, so a locally pulled hill only produces *unofficial* reports. Official scores come from an AutoLab **climb** experiment:
1. Put `solution.json` at the climb workspace root.
2. Run `autolab submit`. This makes a locked experiment.
3. Steer the climb's agent to run only that experiment with `-p n=39`.
4. Start the climb, then stop it once the report shows `official: true`.

The signed report is included.

### Optional tools used in related (unsuccessful) experiments
- **Kissat 4.0.4** (`brew install kissat`), the SAT solver.
- **python-sat** (CaDiCaL, cardinality encodings).
- **Savchuk's** [kobon-cnf](https://github.com/zegalur/kobon-cnf) and [LineOrder](https://github.com/zegalur/line-order), for CNF tables and heuristic straightening.
- **SciPy/HiGHS**, for the linear-program straightener in `src/sat_lns.py`.

---

## 5. What we tried to get past 470 (all exact; none succeeded)

| Approach | Scale | Best straight result |
|---|---|---|
| Best single line on all 248 bases (exhaustive) | 248 bases | 470 (11 bases) |
| Remove one line, re-insert the best (on the 470s) | ~2,900 moves | 470: strict local optima |
| Remove / re-insert 2 / 3 / 4 lines (beam search) | 1,334 / 577 / 82 moves | 470 (found 14 more distinct 470s) |
| New line exactly through an existing crossing | 7 bases | 469 |
| 3-fold-symmetric SAT (kobon-cnf + Kissat), then straightening | 4 tables | pseudolines 475 / 477 / 480 / 480. None straightened |
| Perfect (481) pseudoline words (Parpalak–Utkin search), then straightening | 46 words | none straightened |
| SAT neighbourhood search (signotope encoding, 3–6 free lines, LP straightening) | 394 neighbourhoods | no straight 469+ (simple bases) |

**Lesson.** Near-perfect 39-line patterns exist as *pseudolines*: SAT finds 475–481 easily. None we found can be drawn with straight lines, and the stretchable fraction falls steeply with n. That is evidence, not a proof. The local straight-line neighbourhood of the known 38-line families appears to be exhausted at 470.

---

## 6. Credit and provenance

- **38-line base:** Parpalak & Utkin gallery ([ud1/kobon-solutions](https://github.com/ud1/kobon-solutions); arXiv [2604.22035](https://arxiv.org/abs/2604.22035), [2607.29236](https://arxiv.org/abs/2607.29236)). The first 38 lines of our solution are exactly their arrangement, in integer form.
- **Our contribution:** the exact conversion and insertion pipeline, the sweep over all 248 bases, the 39th line, verification and the official submission.
- **Bounds:** Tamura; Felsner & Kriegel (1999); Clément & Bader (2007 draft); Blanc (2011); Bartholdi, Blanc & Loisel (2008).
- **SAT tooling:** Savchuk (arXiv [2507.07951](https://arxiv.org/abs/2507.07951)); Kissat (Biere et al.).
- **Tools:** Python (numba, python-sat, SciPy/HiGHS), Kissat 4.0.4, and Claude Code (Claude Opus 5.5) as an AI assistant. All counts were checked by exact integer arithmetic.

Related: n = 18 (93 triangles, official, ties the best known) in [`kobon-triangles/n18_93/`](kobon-triangles/n18_93/). Observations and a conjecture (a generalized Blanc bound for even n) are in [`notes/09-kobon-observations.md`](notes/09-kobon-observations.md).
