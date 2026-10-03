#set document(title: "A 39-line arrangement with 470 Kobon triangles", author: "Rohith Poola")
#set page(paper: "us-letter", margin: (x: 2.2cm, y: 2.2cm), numbering: "1")
#set text(font: "New Computer Modern", size: 10.5pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")
#show heading: set block(above: 1.2em, below: 0.6em)
#show link: set text(fill: rgb("#2a78d6"))

#align(center)[
  #text(size: 17pt, weight: "bold")[A 39-line arrangement with 470 Kobon triangles]
  #v(0.4em)
  Rohith Poola (team rohith18p) · #link("mailto:poola.r@northeastern.edu")[poola.r\@northeastern.edu]
  #v(0.2em)
  #text(size: 9.5pt)[Open Math Challenge (Open Problems Hack at MIT), September 27 – October 2, 2026 · code and data: #link("https://github.com/Rohith18p/rsi-kobon-triangles")[github.com/Rohith18p/rsi-kobon-triangles]]
]

#v(0.6em)
#block(inset: (x: 1.2em))[
  *Abstract.* The Kobon triangle problem asks for $K(n)$, the largest number of bounded triangular faces, not crossed by any line, in an arrangement of $n$ straight lines. Before this event no arrangement of 39 lines had been published (OEIS A006066 lists $K(39)$ as "?"); the only upper bound is Tamura's $floor(n(n-2)/3) = 481$. We give an explicit arrangement of 39 lines with exact integer coefficients and *470* triangles, so $K(39) >= 470$. It is obtained by adding one line to a published 38-line arrangement with 450 triangles (Parpalak–Utkin gallery); the added line creates 20 triangles and destroys none. The count is checked in exact integer arithmetic by two independent counters and by the contest's evaluator. We also report an exhaustive sweep (no published 38-line base extends to 471 by one line), several unsuccessful routes beyond 470, first values for other $n$ without published arrangements, and a counting conjecture for even $n$.
]

= Problem and background

An arrangement $cal(A)$ of $n$ lines in $RR^2$ is given by integer triples $(a_i, b_i, c_i)$, line $a_i x + b_i y + c_i = 0$. A *Kobon triangle* is a bounded face of $cal(A)$ that is a triangle, i.e. a triple of lines whose bounded triangle is crossed in its interior by no other line. Parallel lines and points on three or more lines are allowed. Let $K(n)$ be the maximum count.

*Upper bound.* Each line carries at most $n-2$ bounded segments and each triangle uses three of them, so $K(n) <= floor(n(n-2)/3)$ (Tamura); Felsner and Kriegel @fk prove this for all (also non-simple) arrangements. For $n=39$ this gives 481, and reaching it forces a _perfect_ arrangement (every bounded segment is a side of exactly one triangle) @cb. Bartholdi, Blanc and Loisel @bbl and Blanc @blanc give sharper bounds for even $n$ in the simple case.

*Status of $n = 39$.* OEIS A006066 (revision of 14 Sep 2026) lists "?". The only published exclusion is Savchuk's SAT result that no perfect 39-line pseudoline arrangement with 13-fold rotational symmetry exists @savchuk. 39 is not of the form $2m+1$ with $m$ even, so the doubling construction of @bbl does not reach it.

= Construction

+ *Base.* Arrangement `38-74kq3v76alw` of the Parpalak–Utkin gallery @pu-gallery (commit `cecd2b1`): 38 lines, 450 triangles (the best known value for 38), with 5 triple points.
+ *Exact integers.* The gallery stores floating-point slopes and intercepts together with a combinatorial word; we rationalize with the gallery's own procedure (compact-rationalized, $D=100$), which keeps the triple points exact and yields coefficients of at most 11 digits, and check the count against the word.
+ *One more line.* For each of 720 directions (fixed random sub-step offset, seed 0) we take a line through the midpoint of every gap between consecutive projections of crossing points, which covers every combinatorially distinct position at that direction. Each candidate is scored incrementally in floating point ($O(n^3)$: surviving triangles plus new triangles through the new line); the best is rounded at scale $10^12$ and re-counted exactly. The added line is
  $ 490546541635 x + 96768230790 y - 82521729656546 = 0 $
  (slope $approx -5.0693$). It creates 20 new triangles and destroys none of the 450, giving *470*.

#figure(image("fig_arrangement.png", width: 78%),
  caption: [The 39-line arrangement, zoomed on the 20 triangles (shaded) of the added line (green). Orange dots are the five triple points inherited from the base. The full arrangement spans many orders of magnitude.])

*Sweep.* Applying the same step to all 248 gallery arrangements with 38 lines and 450 triangles, with an exhaustive enumeration of the new line's combinatorial positions, gives the distribution in Fig. 2: 11 bases reach 470 and none reaches 471. Hence *no published 38-line realization extends to 471 by adding one line*.

#figure(image("fig_sweep.png", width: 66%),
  caption: [Best count after adding one line, over all 248 published 38-line arrangements with 450 triangles.])

= Verification and checker scope

The solution is the file `kobon-triangles/n39_470/solution.json` (sha256 `85ce027c…3aa352`): 39 distinct integer triples, largest coefficient 14 digits (the contest allows $10^30$). All intersection points are exact rationals; no floating-point number enters any count.

- *Counter 1* (`src/count.py`): for every non-degenerate triple, test every other line for vertices strictly on both sides. *Counter 2* (`research/tools/verify_independent.py`) is an independent implementation. Both give 470.
- *Identity.* $3T = s_1 + 2 s_2$ where $s_1, s_2$ count bounded segments used by one or two triangles: $3 dot 470 = 1390 + 2 dot 10$. ✓
- *Official evaluation.* The AutoLab hill `alejandrozu/kobon-triangles` v0.1.0 (tree hash `7d3f1d91dcb8…`), with parameter $n = 39$, scored it 470 (`passed: true, official: true`, 2026-09-27T19:45:26Z); the signed report is included.
- *Reproduction.* `sh kobon-triangles/n39_470/reproduce.sh` fetches the gallery at the pinned commit, converts the base, adds the line and re-verifies; the output is byte-identical to the submitted file (about 6 s).

*Scope.* The checkers certify the exact statement "this explicit arrangement has 470 Kobon triangles", hence $K(39) >= 470$. They do not address optimality. The trust base is the (short, readable) Python counters and the hill evaluator; no proof assistant was used.

= Structure

#figure(table(columns: 3, align: (left, right, right), stroke: 0.4pt + luma(180),
  [], [*38-line base*], [*39 lines*],
  [triangles], [450], [*470*],
  [distinct crossing points], [693], [731],
  [triple points / parallel pairs], [5 / 0], [5 / 0],
  [bounded segments $E$], [1353], [1428],
  [segments used once / shared by two / unused], [1330 / 10 / 13], [1390 / 10 / 28],
  [Tamura bound], [456], [481]),
  caption: [Segment ledger. Every triple point removes three segments ($E = n(n-2) - 3k$) and here creates two shared segments, so $3T = n(n-2) - k - M$ with $M$ unused segments: $1443 - 5 - 28 = 1410$.])

Under this ledger, 471 requires $k + M <= 30$ (ours has 33) and 481 requires $k = M = 0$, a perfect simple arrangement.

= Attempts beyond 470

All results below are exact; none produced a straight arrangement above 470.
- Remove one line and re-insert the best one (about 2,900 moves on three 470s; exhaustive single-line replacement on all eleven 470s): the 470s are strict local optima.
- Remove and re-insert 2, 3 or 4 lines (beam search, 1334 / 577 / 82 moves): best 470 (14 further distinct 470s found).
- Force the new line through an existing crossing (new triple point): best 469.
- SAT with 3-fold rotational symmetry (kobon-cnf @savchuk + Kissat): pseudoline arrangements with 475, 477, 480, 480 and 481 triangles exist — the C3-symmetric perfect case was previously untested — but none could be straightened (best fits violate 339–477 of the 1443 order constraints). The 46 perfect pseudoline words of @pu-enum that we tested also failed to straighten.
- SAT neighbourhood search on a signotope encoding (3–6 free lines, segment budget, exact LP straightening): 394 neighbourhoods, no straight improvement.

= Partial results

*First values for $n$ without published arrangements* (exact, reproducible, built by insertion, deletion and doubling from published constructions; most were not officially submitted): $K(40) >= 494$, $K(44) >= 608$ (a simple arrangement meeting Blanc's simple bound), $K(47) >= 691$, $K(48) >= 721$, $K(51) >= 815$, $K(52) >= 850$, $K(55) >= 954$, $K(56) >= 990$, $K(58..61) >= 1036, 1086, 1137, 1190$, $K(63) >= 1243$, $K(64) >= 1302$, $K(66..72) >= 1329, 1383, 1438, 1494, 1525, 1590, 1657$, and values for $74..96$ (repository table). We also give explicit integer realizations (coefficients $< 10^30$) of the doubling series for 49, 57, 65, 73, 97 lines, using much larger constants than the proof in @bbl requires.

*Conjecture (generalized Blanc bound).* Let $k$ be the number of triple points, $p$ the number of parallel pairs, and $M$ the number of unused bounded segments. In all 330 arrangements we measured ($n = 6..54$): $E = n(n-2) - 3k - 2p$ (provable), at most $2k$ segments are shared by two triangles, and, for even $n$, $k + 2p + M >= n/2 - 1$, i.e. $K(n) <= floor((n-2)(2n-1)/6)$. This equals the best known value for every even $n$ from 4 to 38. If true, it would give $K(18) = 93$ and settle $K(20) = 117$ for general arrangements; it predicts $K(44) = 609$ (untested). Blanc @blanc proves the case $k = p = 0$ with $M >= n/2$.

= Novelty and limitations

*New:* an explicit arrangement with $K(39) >= 470$ where no value was published; a reproducible pipeline that rebuilds it bit-for-bit from public data; the exhaustive one-line sweep over all published 38-line bases; the existence of C3-symmetric perfect and near-perfect 39-line pseudoline arrangements; first lower bounds for several $n$; a counting conjecture with evidence.

*Not new or not ours:* the 38-line base (Parpalak–Utkin) — 38 of our 39 lines are exactly their arrangement; the doubling construction (Bartholdi–Blanc–Loisel); the SAT encoding (Savchuk); all upper bounds.

*Limitations:* (i) no optimality claim — the gap to 481 is open, and higher counts for $n=39$ may be known to others; (ii) the checkers are exact Python programs, not a formal proof-assistant certificate; (iii) the conjecture is unproven and the shared-segment rule is only empirically supported (it is stated informally in @cb); (iv) the "first values" rely on our literature survey for their novelty and are mostly weak relative to the bounds; (v) the reproduction depends on the third-party gallery at a pinned commit, which carries no license and is fetched, not redistributed.

= Reproducibility and AI disclosure

Requirements: `git`, `uv` (Python 3.12; numpy, numba, SciPy). Commands (repository root): `uv sync`; `uv run python kobon-triangles/n39_470/verify.py`; `sh kobon-triangles/n39_470/reproduce.sh`; `sh kobon-triangles/n39_470/scan_all_bases.sh`. No SAT solver is needed for the 470; Kissat 4.0.4 and python-sat were used only for the unsuccessful SAT experiments. The work was carried out with Claude Code (Claude Opus 5.5) as an AI assistant for search, coding and writing; every reported count was verified by exact computation.

#bibliography("refs.yml", style: "ieee")
