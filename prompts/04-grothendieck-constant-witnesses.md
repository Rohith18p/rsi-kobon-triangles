Climb the AutoLab hill alejandrozu/grothendieck-constant-witnesses on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/rsi-kobon-triangles, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/grothendieck-constant-witnesses` -> ./.autolab/hills/grothendieck-constant-witnesses.
5. Python: `uv run` inside rsi-kobon-triangles (cvxpy with Clarabel/SCS, numpy, numba, gmpy2). Work in `grothendieck/`: `src/`, `submissions/NNN-slug/solution.json`, `reports/`, `journal.html`. Branch `hills/grothendieck-constant-witnesses`, one commit per experiment.

Context (as of 2026-09-27; re-check the board):
- Task: an m×n ±1 matrix (2 ≤ m, n ≤ 8) plus rational unit vectors u_i, v_j in dimension d (2 ≤ d ≤ 16), with coordinates as reduced [num, den] pairs (|values| ≤ 1e6) and squared norm **exactly** 1. Score = (gap_ppm = ⌊1e6 · vector/sign⌋ ↑, m·n ↓, certificate bits ↓). sign(A) is computed by exhaustive enumeration.
- Board: top is **1414213 (≈ √2)** with 2×2, 80 bits (tie: a-hamdi, wilsonwu-ai). That's just CHSH, and √2 is the 2×2 ceiling. **Any gap > √2 needs larger matrices** and takes #1 outright.
- Known: 1.676 ≲ K_G < 1.782. Small matrices can't approach 1.676, so a leaderboard win here isn't new mathematics (probably ~0 competition credit). Treat this as a fast leaderboard hill, not a research target.

Plan I want (agree with me first, then run autonomously):
1. Pipeline, per matrix A: (a) sign(A) exactly by enumerating 2^m choices of x; the best y is then sign(xᵀA) for each x. (b) The SDP upper value: maximize ⟨A, X⟩ over the PSD block Gram matrix with unit diagonal (cvxpy, Clarabel). (c) Factor the Gram matrix into vectors in d ≤ 16 (m + n ≤ 16, so exact rank fits). (d) **Round to exact rational unit vectors** via inverse stereographic projection of rational points (always exactly norm 1). Refine to maximize the exact rational objective.
2. Search over matrices: exhaustive search over small sizes up to row/column permutation and sign flips, then heuristic search (local flips) at 5×5 … 8×8, maximizing the SDP/sign ratio. Check the literature for known good small witnesses (Bell-inequality / "Grothendieck constant of order n" papers) as seeds.
3. For the best ratio, trade denominators against loss: find the smallest-bit rational vectors that keep the same gap_ppm (this is the tie-breaker).

Pitfalls: no floats. Every vector must satisfy |v|² = 1 exactly. The JSON must be ≤ 256 KB. Rounding lowers the objective, so compute the exact value before submitting.

Stopping criteria: best achievable ratio found at 8×8 (search saturates), or ~3 hours. Keep journal.html current.

Once you have your best result, ask me whether I want it on the leaderboard. If yes: `hills eval <best-dir> -H grothendieck-constant-witnesses -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes. Record tool/model versions for the competition disclosure.
