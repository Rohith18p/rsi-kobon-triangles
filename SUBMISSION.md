# Submission packet: Open Problems Hack at MIT (Open Math Challenge 2026)

This file answers the judging requests point by point (handbook §8 minimum packet).
Scope: **Kobon triangles only.**

---

## 1. Entrant and final team

| | |
|---|---|
| Entrant | Rohith Poola (AutoLab `rohith18p`, GitHub `Rohith18p`, poola.r@northeastern.edu) |
| Team roster and class | **Individual entrant.** Rohith Poola is the sole member. |
| Company resources | None. A personal laptop and AutoLab's evaluation agent (platform key) were used only to run the official evaluations. |
| AI tools | Claude Code (Claude Opus 5.5) as an assistant for search, coding and writing. All counts were verified by exact computation (see §7). |

## 2. Results submitted for judging

| # | Result | Target / modality | Claim | Official AutoLab score |
|---|---|---|---|---|
| **R1** | **Kobon triangles, n = 39: an explicit arrangement with 470 triangles** | Kobon problem, focus hill `alejandrozu/kobon-triangles` (M1) | Lower bound $K(39) \ge 470$, where no value was published (OEIS A006066: "?"). No optimality claim. | **470** (experiment `23e84fc7`) |
| R2 | First lower bounds for n with no published arrangement (40, 44, 47, 48, 51, 52, 55, 56, 58–64, 66–72, 74–96) | same | $K(n) \ge$ the listed values (explicit arrangements) | not officially evaluated. Exact and reproducible, see `kobon-triangles/RESULTS.md` |
| R3 | n = 18 with 93 triangles | same | matches the best known value; **not claimed as new** | 93 (experiment `9054ca51`) |
| R4 | Research note: generalized Blanc bound conjecture for even n (§6 of the paper) | same | **conjecture with evidence, not a proof**; offered as a partial / formalizable lead | — |

R1 is the result we ask to be judged. R2 is offered as a narrow certified computation, if eligible. R3 and R4 are context.

## 3. R1: exact arrangement, counts and checker

| Item | Value |
|---|---|
| Exact line arrangement | [`kobon-triangles/n39_470/solution.json`](kobon-triangles/n39_470/solution.json): 39 integer triples (a, b, c), meaning a·x + b·y + c = 0 |
| sha256 | `85ce027ccddc91365ff1f798702fc8ae19838c0d244cd426406f2d3f9b3aa352` |
| Triangle count | **470** (exact). 731 distinct crossing points, 5 triple points, 0 parallel pairs, 1,428 bounded segments (1,390 used once, 10 shared by two triangles, 28 unused). Counting identity: 3 · 470 = 1,390 + 2 · 10. |
| Construction | Published 38-line arrangement `38-74kq3v76alw` (Parpalak–Utkin gallery, 450 triangles), plus the line `490546541635·x + 96768230790·y − 82521729656546 = 0`, which creates 20 triangles and destroys none. Full method: [`N39_470_SOLUTION.md`](N39_470_SOLUTION.md). |
| Checkers | (1) the AutoLab hill evaluator `alejandrozu/kobon-triangles` v0.1.0, tree hash `7d3f1d91dcb8be8d0eef20be763557bd6d876707` (official report: [`kobon-triangles/n39_470/official_report.json`](kobon-triangles/n39_470/official_report.json), `passed: true`, `official: true`, params `n = 39`, 2026-09-27T19:45:26Z, submission hash `sha256:94d4b2ef…7e7ee`); (2) [`kobon-triangles/src/count.py`](kobon-triangles/src/count.py); (3) an independent counter, [`kobon-triangles/research/tools/verify_independent.py`](kobon-triangles/research/tools/verify_independent.py). All three report 470. |
| Checker scope | The checkers certify the exact, finite statement "this explicit integer arrangement of 39 distinct lines has exactly 470 bounded triangular faces not crossed by any line". Arithmetic is exact (integer coefficients, rational intersection points, no floating point, no tolerance). This implies $K(39) \ge 470$. It does **not** address the upper bound or optimality. The trust base is short Python programs plus the contest evaluator. **No proof-assistant certificate (e.g. Lean) has been produced.** |
| Reproduction | From the repository root: `uv sync`, then `uv run python kobon-triangles/n39_470/verify.py`, then `sh kobon-triangles/n39_470/reproduce.sh`. The last rebuilds the file **byte-identically** from the public gallery at a pinned commit, in about 6 s. `sh kobon-triangles/n39_470/scan_all_bases.sh` reproduces the 248-base sweep (none reaches 471 with one line). Requirements: git, uv (Python 3.12; numpy, numba, SciPy). No SAT solver is needed. |

## 4. R2 and R3: exact arrangements and counts

- **R2** files: `kobon-triangles/submissions/n<N>/solution.json`, with the values and sources in [`kobon-triangles/RESULTS.md`](kobon-triangles/RESULTS.md).
  - **Verify one:** `uv run python kobon-triangles/src/count.py kobon-triangles/submissions/n44/solution.json`.
  - **Built by** exact operations on published constructions: single-line insertion (`src/grow.py`), exact deletion (`src/derive.py`, `src/peel.py`), and Bartholdi–Blanc–Loisel doubling with explicit integer realizations (`src/doubling.py`, `src/basesearch.py`).
  - **Same checker scope as R1** (exact count of an explicit arrangement). They have not been run through the AutoLab evaluator.
- **R3:** [`kobon-triangles/n18_93/`](kobon-triangles/n18_93/), containing the solution, its signed official report and the annealing runs.

## 5. Scope of this submission

This submission concerns **only the Kobon triangle problem**. No other hill or problem (in particular no Ramsey K4 multiplicity result) is submitted for judging.

## 6. Paper and novelty / limitations note

- **Paper:** [`paper/kobon39.pdf`](paper/kobon39.pdf), "A 39-line arrangement with 470 Kobon triangles". Source: `paper/kobon39.typ` (Typst 0.15). Figures are made by `paper/make_figures.py`.
- **Slide deck:** [`notes/kobon_deck.pdf`](notes/kobon_deck.pdf).
- **New:**
  - an explicit arrangement giving $K(39) \ge 470$, where no value was published
  - a pipeline that rebuilds it bit-for-bit from public data
  - an exhaustive one-line sweep over all 248 published 38-line bases (maximum 470)
  - C3-symmetric perfect (481) and near-perfect (475–480) 39-line *pseudoline* arrangements exist (found by SAT; none straightened)
  - first lower bounds for the n in R2
  - the R4 conjecture, with evidence from 330 arrangements
- **Not new or not ours:**
  - the 38-line base (Parpalak & Utkin): 38 of the 39 lines are exactly their arrangement, in integer form
  - the doubling construction (Bartholdi–Blanc–Loisel)
  - the SAT encoding (Savchuk) and the Kissat solver
  - all upper bounds (Tamura; Felsner–Kriegel; Clément–Bader; Blanc)
- **Limitations:**
  1. no optimality claim; the gap 471–481 is open to us
  2. Python exact checkers, not a formal proof
  3. R4 is unproven, and its shared-segment rule is only empirical
  4. R2's novelty rests on our literature survey (`kobon-triangles/research/literature.md`), and most R2 values are far from the bounds
  5. reproduction depends on a third-party gallery that states no license; it is fetched at a pinned commit, not redistributed

## 7. Provenance and disclosures

- **New-work delta:** all code and results in this repository were produced during the event window (27 Sep – 2 Oct 2026). Pre-existing material used: the Parpalak–Utkin gallery data and verification code (fetched, not copied), Savchuk's kobon-cnf and LineOrder (used for the unsuccessful SAT experiments), and published papers (cited in the paper).
- **Tools and versions:** Python 3.12 (numpy, numba, SciPy/HiGHS, python-sat), Kissat 4.0.4, hills CLI 0.11.0, autolab CLI, Typst 0.15.1, Claude Code (Claude Opus 5.5).
- **Compute:** one personal laptop. AutoLab's evaluation agent was used only to run the official evaluations of our fixed, locked solution files; it did not search.
- **Outside help:** none, beyond the cited sources and tools.

## 8. Final submission and references

| | |
|---|---|
| Repository (public) | https://github.com/Rohith18p/rsi-kobon-triangles |
| Final commit | git tag **`final-submission`**. Run `git rev-parse final-submission` for the hash; it is also listed on GitHub under Releases → Tags. |
| AutoLab climb | `rohith18p/kobon-triangles` (https://app.autolab.ai/projects/rohith18p/kobon-triangles). Experiments `23e84fc7` (n = 39, 470) and `9054ca51` (n = 18, 93). |
| Hill | `alejandrozu/kobon-triangles` v0.1.0, tree hash `7d3f1d91dcb8be8d0eef20be763557bd6d876707` |

## 9. Reviewer access

- **GitHub repository:** public; no access needed.
- **AutoLab climb** `rohith18p/kobon-triangles`: the reviewers already have access. The signed official reports are also included in this repository.

## 10. Missing material and possible blockers

Resolved: team (individual entrant), scope (Kobon only), reviewer access (reviewers already have the climb).

Remaining notes for the reviewers:
1. **Formal certificate:** none. The checkers are the contest evaluator plus two exact Python counters. Please advise whether this meets the approved trust boundary for the Kobon hill.
2. **R2 values:** not evaluated on AutoLab (only n = 18 and n = 39 were); available on request.
3. **Third-party dependency:** the reproduction fetches the Parpalak–Utkin gallery (no license stated) at commit `cecd2b1b4dd77f6a2453ec45676e4698cd8956f9`.
4. **Publication authority (handbook §8.4 and §10.1): granted.**
   - **Attribution approval:** I approve the attribution as stated in this packet and the paper. The author of the new work is Rohith Poola; third-party material is credited to its authors (§6).
   - **Permission:** I grant the organizers a non-exclusive, worldwide permission to host, reproduce, verify, index, and include the submitted statement, arrangements and other artifacts, relevant code, disclosures, and approved text in the competition's public record and bundled publication, under the competition terms.
   - **Rights kept:** I keep copyright and authorship and remain free to publish and extend the work elsewhere.
   - **Third-party material:** this permission covers only my own contributions. The third-party gallery data and code are not redistributed here; see item 3.
   - No company is involved: this is an individual entry.
