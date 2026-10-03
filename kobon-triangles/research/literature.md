# Kobon triangles: literature and data survey (as of 2026-09-27)

Legend: **[V]** = checked directly in the cited source or by my own exact computation. **[I]** = my own inference or heuristic, not published.

## 0. Key corrections to the task brief

- **[V] The n=20 upper bound is 117, not 120.** Wikipedia and OEIS both list 117 = ⌊n(n−7/3)/3⌋ (Bartholdi–Blanc–Loisel 2008, Thm 1.1). 117 was reached in 2026 by Parpalak & Utkin, so both sources treat **a(20)=117 as settled**.
- **[V] The n=18 upper bound is listed as 94, not 95.** Wikipedia's "improvements" row and OEIS column U both give 94, again from Bartholdi et al.
- **[V] Caveat that matters for this competition.** Bartholdi et al. (Thm 1.1) and Blanc (2011) prove their bounds only for **simple** arrangements: no parallel lines, no triple points, pseudolines allowed. For general arrangements, which this hill allows, the only published bound I found is **Clément–Bader 2007**. It gives 95 for n=18 and 119 for n=20, and it is an unpublished draft with an informal proof. So "117 is optimal for n=20" (OEIS/Wikipedia) and "94 is the ceiling for n=18" have **no written proof for non-simple arrangements**. **[I]** The simple-case proofs do not carry over directly: the 18-line, 4-parallel-pair record breaks the Blanc/Bartholdi counting lemma (see §2).
- **[V] Simple arrangements cannot beat 93 at n=18.** Blanc 2011 (Geombinatorics 21:5–17, arXiv:0801.2845), Thm 1 / Cor 2.0.5: a simple affine pseudoline arrangement with n even has at most n(n−5/2)/3 triangles if n≡0,4 (mod 6) and at most (n(n−5/2)−2)/3 if n≡2 (mod 6). That gives **93 for n=18** and **116 for n=20**. Thm 3 says these bounds are reached for all n≤30 except 11 and 12. **So a 94 at n=18 must use triple points and/or parallel lines**, and every simple-only search for 94 (Savchuk-style CNF, the yhinai SAT sweep) is pointless.
- **[V] The competition itself.** This is AutoLab hill `alejandrozu/kobon-triangles` v0.1.0. Its rules and exact evaluator are mirrored in https://github.com/yhinai/openmath/tree/main/challenges/01-openmath/kobon-triangles/hill. The evaluator is copied to `tools/autolab_hill_eval.py`. Scores are ranked **separately for each n from 3 to 100**. Coefficients must satisfy |coef| ≤ 10^30.

## 1. Record table, n = 3..40

Column meanings:
- T = Tamura ⌊n(n−2)/3⌋.
- CB = Clément–Bader (T−1 when n≡0,2 mod 6). This is the only bound claimed for general arrangements.
- BBL = ⌊n(n−7/3)/3⌋ for even n. Proven for simple arrangements only.
- Bl = Blanc's simple bound for even n (⌊·⌋).
- Best = best known, from OEIS A006066 (rev. #245, 2026-09-14) and the Parpalak–Utkin gallery.

All "best" values from n=8 to n=38 in the table were re-verified by me in exact arithmetic (hill evaluator plus an independent counter) on downloaded arrangements, except n=9, 11, 13, 15, 25, 27, 29, 31, 33–37, which I did not re-run.

| n | n mod 6 | T | CB | BBL | Bl (simple) | Best | Status / source of best |
|---|---|---|---|---|---|---|---|
| 3–7 | | 1,2,5,8,11 | 1,2,5,7,11 | | | 1,2,5,7,11 | optimal |
| 8 | 2 | 16 | 15 | 15 | 14 | 15 | optimal. Needs 2 triple points; simple max is 14 (Liu 2026, Zenodo 21181452) |
| 9 | 3 | 21 | 21 | – | – | 21 | optimal |
| 10 | 4 | 26 | 26 | 25 | 25 | 25 | optimal (Grünbaum) |
| 11 | 5 | 33 | 33 | – | – | 32 | optimal. SAT proof that 33 is impossible (Savchuk 2025) |
| 12 | 0 | 40 | 39 | 38 | 38 (simple max is 37) | 38 | optimal if BBL holds generally (Kabanovitch). Non-simple |
| 13 | 1 | 47 | 47 | – | – | 47 | optimal |
| 14 | 2 | 56 | 55 | 54 | 53 | 54 | Maiorana 2026 and Parpalak–Utkin, with triple points. OEIS says "exact" |
| 15 | 3 | 65 | 65 | – | – | 65 | optimal (Suzuki) |
| 16 | 4 | 74 | 74 | 72 | 72 | 72 | Bader. "Optimal" per OEIS via BBL |
| 17 | 5 | 85 | 85 | – | – | 85 | optimal (Bader 2007) |
| **18** | 0 | 96 | **95** | **94** | **93** | **93** | Bader (3-fold symmetric). **OPEN**; 94 needs a non-simple arrangement |
| 19 | 1 | 107 | 107 | – | – | 107 | optimal (Kyle Wood; 18·2^t+1 base, Parpalak–Utkin 2026) |
| **20** | 2 | 120 | **119** | **117** | 116 | **117** | Parpalak–Utkin 2026. Every known 117 has ≥3 triple points. "Optimal" per OEIS/Wikipedia |
| 21 | 3 | 133 | 133 | – | – | 133 | optimal (Savchuk, github.com/zegalur/kobon-21) |
| 22 | 4 | 146 | 146 | 144 | 143 | 143 | Savchuk. Open (144 needs non-simple) |
| 23 | 5 | 161 | 161 | – | – | 161 | optimal (Savchuk) |
| 24 | 0 | 176 | 175 | 173 | 172 | 172 | Savchuk. Record uses 6 parallel pairs and is "perfect" (every edge used). Open |
| 25 | 1 | 191 | 191 | – | – | 191 | optimal |
| 26 | 2 | 208 | 207 | 205 | 203 | 204 | Parpalak–Utkin. Open |
| 27 | 3 | 225 | 225 | – | – | 225 | optimal (Savchuk) |
| 28 | 4 | 242 | 242 | 239 | 238 | 238 | Zarzuelo. Open |
| 29 | 5 | 261 | 261 | – | – | 261 | optimal |
| 30 | 0 | 280 | 279 | 276 | 275 | 275 | Zarzuelo. Open |
| 31 | 1 | 299 | 299 | – | – | 299 | optimal (Wood) |
| 32 | 2 | 320 | 319 | 316 | 314 | 315 | Parpalak–Utkin. Open |
| 33 | 3 | 341 | 341 | – | – | 341 | optimal |
| 34 | 4 | 362 | 362 | 358 | 357 | 357 | Zarzuelo. Open |
| 35 | 5 | 385 | 385 | – | – | 385 | optimal |
| 36 | 0 | 408 | 407 | 404 | 402 | 402 | Parpalak–Utkin. Open |
| 37 | 1 | 431 | 431 | – | – | 431 | optimal (18·2^t+1 series) |
| 38 | 2 | 456 | 455 | 451 | 449 | 450 | Parpalak–Utkin. Open |
| **39** | 3 | 481 | 481 | – | – | **? (none published)** | OEIS "?" |
| **40** | 4 | 506 | 506 | 502 | 500 | **? (none published)** | OEIS "?" |

For n>40, OEIS lists: 41=533, 42≥553, 43=587, 44 ?, 45=645, 46≥667, 47 ?, 48 ?, 49=767, 50≥792. The gallery also has 53=901 and 54=927.

**Discrepancies between sources [V]:**
- Wikipedia and OEIS: 18 → 94, 20 → 117. Wikipedia's "known upper bounds" prose still describes the Clément–Bader bound first.
- MathWorld (updated 2026-09-02) lists the Clément–Bader values 95 and 119, and mentions the BBL bound separately.
- Clément–Bader's own 2007 table gives 18 → 95, 20 → 119, with best-known values 93 and 115 at the time.
- Bader's archived page lists 18 → upper bound 96.
- BBL 2008 Thm 1.4 lists 18 as "93−94" and 20 as "116−117" for simple pseudolines.
- The "kobon-duel" repo says best known for 14 and 20 is 53 and 116. That is out of date.
- Wikipedia's table header lists n=12 as "one below bound" but also marks 38 as optimal.

**Pattern [V from table, I as a conjecture]:** for every even n from 4 to 38, the best known equals ⌈n(n−5/2)/3⌉, i.e. Blanc's simple bound rounded up.
- For n≡2 (mod 6) (8, 14, 20, 26, 32, 38), triple points gain exactly +1 over the simple maximum.
- For n≡0,4 (mod 6), where n(n−5/2)/3 is an integer, **nobody has ever beaten Blanc's simple bound**. n=12 only reaches it.
- So 94 at n=18 would be the first case of a non-simple arrangement beating an integral Blanc bound.

## 2. Recent results (2020–2026)

- **Savchuk 2025**, arXiv:2507.07951, "Constructing Optimal Kobon Triangle Arrangements via Table Encoding, SAT Solving, and Heuristic Straightening". Code: github.com/zegalur/kobon-cnf (CNF + Kissat) and github.com/zegalur/line-order (straightening).
  - The CNF model only covers **simple, perfect-type arrangements (n mod 6 ∈ {3,5})** plus "missing triangle" slack.
  - The table notation supports parallel lines and multi-points, but the SAT side does not.
  - Proved **a(11)=32**: 33 is impossible even for pseudolines. Also found optimal 23→161 and 27→225, enumerated all optima for n=3,5,9,15,17, and built 22≥143 and 24≥172 by inserting a line into odd optima.
  - Symmetric runs that came back empty: n=35 with mirror symmetry, n=35 with 7-fold rotation, n=39 with 13-fold rotation (Table 1).
- **Parpalak & Utkin 2026a**, arXiv:2604.22035, "The 18·2^t+1 triangle-maximal series of straight lines". A 19-line straight base configuration satisfying BBL Prop 3.1 gives optimal straight arrangements for all n=18·2^t+1 (19, 37, 73, …).
  - They searched n=21, 23, 25 (pentagon-defect subclass) and 27 for new iterable bases and found none. They did find one-step examples giving **41→533, 45→645** (optimal) and 49 lines + the line at infinity = projective optimum 815.
  - Counts of projective classes of optimal simple pseudoline arrangements: n=15: 1, 17: 3, 19: 1312, 21: 18, 23: 112, 27: 56646. Stretchable lower bounds: 1, 3, ≥1306, ≥11, ≥51, ≥348.
  - Code: github.com/parpalak/triangle-maximal-18-series.
- **Parpalak & Utkin 2026b**, arXiv:2607.29236, "Enumeration and classification of triangle-maximal pseudoline arrangements". Complete classification of perfect arrangements for n≤27 and 2-defective ones for n≤19, for **odd n only**. They say explicitly: "the even case (… non-simple arrangements in the Kobon problem) is beyond the scope". Code and data: github.com/parpalak/pseudoline-algorithms.
- **Parpalak–Utkin gallery** (https://ud1.github.io/kobon-solutions/gallery/, repo ud1/kobon-solutions). **[V]** I re-counted all 10,326 entries with their exact checker.
  - n=18: 2376 simple-slope arrangements with 93 (up to 8 triple points), 593 with 1 parallel pair (93), 47 with 4 pairs (93), 14 with 6 pairs (92), 6 with 9 pairs (90). **No 94 anywhere.**
  - n=20: 305 with 117 (every one has 3–8 triple points), 42 with 1 parallel pair (117), 44 with 6 pairs (116), 19 with 9 pairs (114).
  - This is strong evidence that a large, systematic search has been run on n=18 without finding 94. There is no written impossibility proof.
- **Maiorana 2026** (OEIS; github.com/rufio72/kobon_triangles_k14). Fifteen 14-line arrangements with 54 triangles, each with 2 or 4 triple points and no parallels. The README says "not yet independently confirmed". **[V]** An independent Parpalak–Utkin 54 checks out in my exact counters.
- **Zarzuelo Urdiales** (the hill owner "alejandrozu" is presumably him), "New Lower Bounds for Even Kobon Numbers", archivara.org/paper/48b411c9-0e03-4592-931e-179b9a1c2312. Credited in OEIS for 28≥238, 30≥275, 34≥357. The page would not render for me; contents not verified.
- **Liu 2026** (Zenodo 21181452, not peer reviewed) proves K_cell(8)=14<15=K(8) by enumeration. It also gives a local "desingularization" formula: moving one line of a triple point changes T by 1−τ. **Liang–Liu–Zhang 2026** (Zenodo 21181834) claims that optimal *simple* n=28 arrangements must be asymmetric. That paper misses Blanc's bound (it quotes 238–239 for simple, when Blanc already gives 238), so treat it with caution.
- **Other bounds.** Felsner & Kriegel 1999 (DCG 22:429–438) show ⌊n(n−2)/3⌋ holds in the non-simple case (as cited in 2607.29236). Blanc 2011 gives the tight simple even-n bounds above. **I found no paper proving 94 impossible for n=18, or 118 impossible for n=20, for general arrangements, and no general-arrangement bound stronger than Clément–Bader.**
- **Third-party SAT attempt** (yhinai/openmath, `raw/yhinai_kobon94_sat/`). A simple-pseudoline CNF: the N=18 "≥94" instance timed out; "≥96" is DRAT-certified UNSAT; "≥93" is SAT. Blanc's theorem already makes this redundant.
- **Perfect arrangements / necessary conditions [V].** Tamura bound = segment count. A perfect arrangement uses every bounded segment in exactly one triangle.
  - Clément–Bader: for n≡0,2 (mod 3), hitting Tamura forces perfection, and perfection forces odd n.
  - For n≡1 (mod 6), optima have 2 unused segments forming a pentagon or two quadrilaterals ("2-defective", 2607.29236).
  - Blanc Prop 2.0.4 (even n, simple): every line forces an unused bounded segment on a neighbouring line, so M ≥ n/2.
  - **[V]** This lemma **fails with parallel lines**. The 18-line, 4-parallel-pair 93 record has only **M=1** unused bounded edge (E=280, 3·93=279), where the lemma would force M≥9. It also fails with triple points: the n=8 optimum has M=1 with E=42 and 4 shared edges.
  - That is exactly why the simple-case bounds (BBL, Blanc) cannot simply be quoted for this hill.

## 3. Data sources and downloaded files

Everything is under `research/`. Provenance is in `raw/SOURCES.md`.

- `records/*.json` are **hill-format submissions** ({"lines": [[a,b,c],…]}, a·x+b·y+c=0, integers, |coef| ≤ 10^30).
  - Each was checked three ways: by the hill evaluator (`tools/autolab_hill_eval.py`), by my independent interior-crossing counter (`tools/verify_independent.py`), and by the combinatorial count of the source word.
  - Two files were also run through the actual `eval()` entry point: passed=True, 93 and 117.
  - Coverage: n8=15, n10=25, n12=38, n14=54, n16=72, n17=85, n18=93 (four variants: 4 triple points / 1 parallel pair + 3 triple points / 4 parallel pairs / the yhinai Lean one), n19=107, n20=117 (two variants), n21=133, n22=143, n23=161, n24=172, n26=204, n32=315, n38=450.
  - `records/_ud1_records_summary.json` gives the source file for each.
  - Converted with `tools/ud1_to_hill.py`. Triple-point arrangements are rationalized by rounding the slopes and the free intercepts, then solving the concurrency constraints exactly, giving 5–16 digit integers. The naive projection method gives more than 100 digits and fails the 10^30 limit.
- `tools/edge_ledger.py` prints E, the multi-points, parallel pairs, unused edges M and shared edges a2. The exact identity is **3T = E − M + a2**. In every downloaded record with triple points, a2 = 2·(number of triple points).
- `raw/ud1_kobon-solutions/`: thousands of gallery arrangements, including all 3016 n=18 ones with 93 and all 347 n=20 ones with 117, plus certificates and checkers.
- `raw/parpalak_triangle-maximal-18-series/`: the 19/107 base with interval certificates, and lines for 37, 38, 41, 42, 45, 46, 49.
- `raw/maiorana_k14/`: the 14/54 exact rationals.
- `raw/zegalur_line-order_gallery/`: Savchuk's tables, including Bader 18/93.
- `papers/`: PDFs and text of BBL 2008, Blanc 2011, Savchuk 2025, Parpalak–Utkin 2026a and 2026b, Clément–Bader 2007, Pegg 2006, Bader's page, the Liu Zenodo papers and Alkauskas 2025.
- `oeis_A006066.txt` is the full OEIS entry.
- Not fetched: Bader's original 18/93 coordinates (only images and a PDF via web.archive, but the gallery and LineOrder contain equivalent 93s); Zarzuelo's paper; the AutoLab leaderboard (needs login/API key).

## 4. Construction methods

1. **Symmetric constructions.** Mirror symmetry or k-fold rotation shrink the search. Bader's 18/93 is 3-fold rotationally symmetric. Savchuk's CNF supports mirror (-M) and rotation (-R) constraints. Liang et al. claim even-order rotations are trivially UNSAT in the kobon-cnf encoding.
2. **Doubling / iteration.**
   - Forge–Ramírez Alfonsín 1998 (DCG 20:155) and BBL 2008 Prop 3.1: from an optimal odd arrangement Y0,L1..Ln with x-intercepts ±tan(kπ/n) and two tiny intercepts ±ε, where Y0 touches n−1 triangles, add n lines to get 2n+1 lines and +n² triangles.
   - Series: 2·2^t+1, 6·2^t+1, 14·2^t+1, 18·2^t+1 (the last straight since 2026). One-step versions give 41, 45 and 49.
   - Blanc 2011 §4 has a pseudoline doubling for even n (n → 2n−2).
3. **Add a line to an odd optimum** (Savchuk's `lineorder.add_1_2_line`). This produced 16/72 from 15, 20/116 (Wood), 22/143 and 24/172.
4. **Pseudoline search, then stretching.**
   - Enumerate allowable sequences / wiring diagrams / O-matrices by DFS (Parpalak–Utkin, Wood, Bartholdi) or SAT (Savchuk).
   - Stretch by constrained least squares (Savchuk: variables are angle and offset per line), or with fixed intercepts where the problem becomes an LP (Parpalak–Utkin with HiGHS).
   - Stretchability is ∃R-complete in general, but the success rate is high for these instances (e.g. ≥1306 of 1312 classes at n=19).
5. **Non-simple features.** Triple points and parallel pairs are how every even-n record beats or matches the simple maximum: 8, 12, 14, 20, 26, 32, 38 use triple points; 24/172 and 18/93 variants use parallel pairs. Tools: Savchuk's table notation encodes multi-points as groups; ud1's `gens` words mark triple points with `k*`.

## 5. Recommended target n

- **n=18 (93 → 94): the smallest genuinely open case. The only route is non-simple (Blanc). Hard, but not ruled out.**
  - It needs E − M + a2 = 282 with E = 288 − 2·(parallel pairs) − 3·(triple points) (for distinct multi-points).
  - **[I]** The known 18-line records sit at 279, 280 or 281 on this measure. For example, the 4-triple-point record has E=276, M=5, a2=8, i.e. 279.
  - Suggested plan: extend a pseudoline SAT/DFS model to **allow triple points and parallel pairs**. Savchuk's table format already supports both, but his CNF does not. Target E−M+a2 ≥ 282, then straighten with the LP/least-squares methods and exact-verify with the hill evaluator.
  - Candidates **[I]**: several disjoint triple points each bordered by shared-edge triangle pairs (known records get exactly 2 shared edges per triple point, and 94 needs a2 − 3k − 2p − M ≥ −6), and mixed parallel + triple designs. Parpalak–Utkin have evidently mined thousands of variants without success, so budget accordingly.
- **n=20 (117 → 118):** not rigorously excluded (only CB's 119 applies to general arrangements), but it would contradict the OEIS/Wikipedia "optimal" label and the ⌈n(n−5/2)/3⌉ pattern. **[I]** Harder than n=18. Not recommended as the main target.
- **Same kind of open gap as n=18, but bigger:** n=22 (143 vs 144), 24 (172 vs 173), 26 (204 vs 205), 28, 30, 32, 34, 36 (402 vs 404), 38. Each needs a non-simple arrangement beating the (rounded-up) Blanc bound, and none has ever been found.
- **Most practical "new record" wins [I]:** n values where **no arrangement is published**: **39, 40, 44, 47, 48**, and most n from 51 to 100 (the gallery stops at 54, apart from the doubling series 57, 65, 73, 97).
  - Examples: n=39 (bound 481, perfect needed; Savchuk found no 13-fold-symmetric table) and n=40 (Blanc simple bound 500). Any strong construction, e.g. adding a line to a 39- or 41-line arrangement, or SAT + straightening, would be the first published value.
  - Before choosing one, check the AutoLab leaderboard for existing submissions at that n.
- **Ready baseline:** `records/n18_93_*.json` and `records/n20_117_*.json` tie the best known and pass the hill evaluator. Submit one as a fallback.
