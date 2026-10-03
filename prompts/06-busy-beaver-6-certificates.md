Climb the AutoLab hill alejandrozu/busy-beaver-6-certificates on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/rsi-kobon-triangles, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/busy-beaver-6-certificates` -> ./.autolab/hills/busy-beaver-6-certificates.
5. Python: `uv run` inside rsi-kobon-triangles (numba for the simulator). Work in `bb6/`: `src/`, `submissions/NNN-slug/solution.json`, `reports/`, `journal.html`. Branch `hills/busy-beaver-6-certificates`, one commit per experiment.

Context (as of 2026-09-27; re-check the board):
- Task: one 6-state, 2-symbol TM (states A–F, halt H), started in state A on a blank tape. It must halt within a **private step budget** and visit all six states. Score = (steps ↑, ones ↑, tape_span ↑). Machines that don't halt within the budget are **rejected**, not capped. Validation and final use **different** budgets.
- Board: #1 eychcue **249,881 steps** (554 ones, span 735), #2 yavol 246,872, #3 a-hamdi 177,725.
- Known BB(6) champions run astronomically long (far beyond any simulation budget), so they would be rejected. The real game is the longest halting run under an unknown budget. The board suggests the budget is at least ~250k steps. A pure simulator means huge step counts cost evaluation time.
- Competition value: not new mathematics (far below known BB(6) bounds), so ~0 competition credit. Leaderboard hill.

Plan I want (agree with me first, then run autonomously):
1. Write a fast numba TM simulator (dev only) and validate step counts exactly against `hills eval` on the sample (6 steps) and one or two nontrivial machines.
2. Candidate generation: (a) enumerate 6-state machines in Tree Normal Form (bbchallenge-style, pruning isomorphic and trivially looping machines) with a step cap, keeping halting ones sorted by steps; (b) mutate and hill-climb from the best halters; (c) build 6-state machines from strong 5-state machines (e.g. the BB(5) champion at 47,176,870 steps, or shorter 5-state halters) by adding a sixth state that's visited, choosing total run lengths across a range of scales.
3. Budget uncertainty: don't reverse-engineer the private budget with repeated evals. That probes held-out data and is against the hills rules. Use judgment: submit strong candidates in increasing order, and stop increasing once one is rejected for not halting within the budget. Tell me each time before going above ~10× the current leader, and keep a margin, because the final budget may differ from validation.

Pitfalls: all six states must actually be reached. The JSON move is "L"/"R" and write is 0/1. Rejected ≠ low score.

Stopping criteria: beat 249,881 by a clear margin with a machine safely inside the budget, or ~4 hours. Keep journal.html current.

Once you have your best result, ask me whether I want it on the leaderboard. If yes: `hills eval <best-dir> -H busy-beaver-6-certificates -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes. Attribute any machine taken from bbchallenge or other public sources.
