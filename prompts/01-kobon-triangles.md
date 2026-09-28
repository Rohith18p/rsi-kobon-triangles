Climb the AutoLab hill alejandrozu/kobon-triangles on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/RSI_Math, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/kobon-triangles` -> ./.autolab/hills/kobon-triangles.
5. Python for search code: `uv run` inside RSI_Math (numpy, numba, sympy, ortools, python-sat available). Work in `work/kobon-triangles/`: search code in `src/`, one folder per candidate in `submissions/NNN-slug/solution.json`, signed reports in `reports/`, and `journal.html`. Branch `hills/kobon-triangles`, one commit per experiment.

Context (as of 2026-09-27; re-check the board with `/api/v1/hills/alejandrozu/kobon-triangles/board`):
- Task: exactly n integer lines `[a,b,c]` (|coef| ≤ 1e30, no duplicates). Score = number of bounded triangular faces not crossed by any line. Exact arithmetic. Each n has its own leaderboard.
- n=18 board: top is 93 (six-way tie). Literature best known for n=18 is 93. The upper bound is 95 (Tamura ⌊n(n−2)/3⌋ = 96, reduced by 1 for n ≡ 0, 2 mod 6 by Clément–Bader). So **94 or 95 would be a new world record**. 93 just ties everyone, and the tie goes to whoever submitted earliest.
- n=20: best known 117, bound 120. The board for n=20 is likely empty or thin. A 118+ would be a record.
- Competition value: only a **new record** is new mathematics (a "certified computation", modest progress band). Matching the known 93 is worth ~0.

Plan I want (agree with me first, then run autonomously):
1. Write a fast local triangle counter (dev only) and cross-check it against `hills eval` on the baseline (16) and a few random arrangements, so dev numbers match official ones.
2. Reproduce 93 at n=18 from a known construction (literature: Bartholdi, Blanc, Feldt, Schmidt et al.; Johannes Bader's Kobon constructions). Confirm the scorer agrees.
3. Record attempt: search combinatorial (pseudoline) arrangements that meet the count-based necessary conditions for 94/95, e.g. with SAT via python-sat. Then attempt **geometric realization** by numeric optimization followed by exact rational rounding. Checking realizability matters, because many pseudoline arrangements are not stretchable.
4. In parallel, try n=20 (and other n where best known < bound) with the same pipeline, since those boards may be uncontested.
5. First do a quick literature check (recent SAT/computer-assisted Kobon papers) for whether 94 at n=18 has already been ruled out. If it has, stop spending time on n=18.

Pitfalls: no floats in the JSON. Triangles cut by another line don't count. Rounding can merge or split faces, so always score the exact rational version. The watchdog is 120 s.

Stopping criteria: a verified record (n=18 ≥ 94 or n=20 ≥ 118), a found proof that it's impossible, or ~6 hours with no progress. Keep journal.html current throughout.

Once you have your best result, ask me whether I want it on the leaderboard. If yes: `hills eval <best-dir> -H kobon-triangles -p n=<n> -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes. Record tool/model versions for the competition disclosure.



### Backup
Climb the AutoLab hill alejandrozu/kobon-triangles on this machine with the hills skill.

Setup (check each before installing):
1. `npx skills add autolab-ai/hills` — the hills skill; it bootstraps the `hills` CLI.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in: `autolab --url https://app.autolab.ai login`
   (`--token <PAT>` if headless).
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/kobon-triangles` -> ./.autolab/hills/kobon-triangles.

Then follow the hills skill: read the hill's README and `hills describe kobon-triangles`, agree the plan with me, and run its experiment loop — change only the code you are optimizing, score every attempt with `hills eval <dir> -H kobon-triangles`, keep what improves, and leave the report the skill describes.

Once you have your best result, ask me whether I want it on the alejandrozu/kobon-triangles hub leaderboard. If yes: `hills eval <best-dir> -H kobon-triangles -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes.