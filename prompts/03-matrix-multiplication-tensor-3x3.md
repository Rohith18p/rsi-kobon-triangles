Climb the AutoLab hill alejandrozu/matrix-multiplication-tensor-3x3 on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/rsi-kobon-triangles, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/matrix-multiplication-tensor-3x3` -> ./.autolab/hills/matrix-multiplication-tensor-3x3.
5. Python: `uv run` inside rsi-kobon-triangles (numpy, sympy, numba, python-sat). Work in `matmul-3x3/`: `src/`, `submissions/NNN-slug/solution.json`, `reports/`, `journal.html`. Branch `hills/matrix-multiplication-tensor-3x3`, one commit per experiment.

Context (as of 2026-09-27):
- Task: factor matrices u, v, w (R rows × 9 exact rationals, |num|, |den| ≤ 1e6) satisfying all 729 Brent equations. Conventions: A and B are row-major; the **W index for C[row][col] is 3·col + row (column-major)**. Score = (rank ↓, support ↓).
- Known: rank 23 (Laderman 1976). Rank ≤ 22 is open, and the lower bound is 19. A rank-22 scheme would be a major result.
- Competition value: support isn't a registered open problem, so a support record is probably not new mathematics. Only rank 22 is real new mathematics, and it's a moonshot. Keep time spent proportionate.

Plan I want (agree with me first, then run autonomously):
1. Write a dev Brent-equation checker (exact, sympy/fractions) and validate it on the Laderman baseline against `hills eval`, including the column-major W convention.
2. Support minimization at rank 23:
   a. Gather known rank-23 schemes (Heule–Kauers–Seidl found thousands via SAT over GF(2), and Kauers–Moosbauer flip graphs; public repos exist). Lift them to Z/Q where needed and score their support.
   b. Apply the symmetry group of the tensor to each scheme to minimize nonzeros: (A, B, C) → (PAQ⁻¹, QBR⁻¹, …) with sparse invertible P, Q, R, plus cyclic transposition symmetry.
   c. Run a flip-graph random walk at rank 23 that optimizes support directly.
3. Moonshot, time-boxed to ~20% of effort: flip-graph search with plateau and reduction moves aiming at rank 22 over GF(2), followed by Hensel lifting to Z.

Pitfalls: the W convention is easy to get wrong. Coefficients must be exact rationals (integers preferred). Up to 40 rows are allowed, but rank = row count, so remove zero rows.

Stopping criteria: support < 139 verified (then keep pushing lower for 2 more hours), or ~5 hours with no improvement. Keep journal.html current.

Once you have your best result, ask me whether I want it on the hill. If yes: `hills eval <best-dir> -H matrix-multiplication-tensor-3x3 -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes. Record tool/model versions and the provenance of any scheme we start from; a published scheme must be attributed, not claimed as new.
