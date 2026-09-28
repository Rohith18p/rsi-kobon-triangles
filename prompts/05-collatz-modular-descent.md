Climb the AutoLab hill alejandrozu/collatz-modular-descent on this machine with the hills skill.

Setup (check each before installing; work from /Users/rohith/My/WORK/Projects/RSI_Math, which is a git repo):
1. `hills --version` (0.11.0 is installed). Load the hills skill if available.
2. `autolab --version`; if missing: `curl -fsSL https://app.autolab.ai/install.sh | sh`.
3. `autolab --url https://app.autolab.ai whoami`; if not signed in, ask me to run `! autolab --url https://app.autolab.ai login`.
4. `autolab --url https://app.autolab.ai hills pull alejandrozu/collatz-modular-descent` -> ./.autolab/hills/collatz-modular-descent.
5. Python: `uv run` inside RSI_Math. Work in `work/collatz/`: `src/`, `submissions/NNN-slug/solution.json`, `reports/`, `journal.html`. Branch `hills/collatz-modular-descent`, one commit per experiment.

Context (as of 2026-09-27; re-check the board):
- Task: ≤ 512 rules {modulus_power k, odd residue r, exponents [e1..es]} with k ≥ 1 + Σe, 3^s < 2^Σe, and C^s(n) < n on the whole class. Score = (coverage of **hidden** odd classes mod 2^8..2^12 ↑, min_descent_ppm ↑, rule_count ↓). Validation and test use different hidden targets.
- Board: top three all tied at **coverage 100%, min_descent 525390, 3 rules**. The hill is saturated. 525390 ppm matches 1 − 3⁵/2⁹, so the weakest rule used has s = 5, Σe = 9.
- Competition value: the README says outright that this is not progress on Collatz. Expect ~0 competition credit. **Low priority.** Only worth a short attempt at the tie-breakers.

Plan I want (agree with me first, then run autonomously; time-box to ~1.5 hours total):
1. Reproduce a 100%-coverage, 3-rule solution from first principles. Understand which broad classes (small k) descend quickly: n ≡ 1 (mod 4) descends after 1 step. Then explain why 3 rules can reach 100% of the hidden targets, which implies the targets are a specific subset. Reason from the README only; never read `private/`.
2. Tie-breakers: find rule sets that keep coverage while **raising the weakest contraction** (every rule used should have a smaller 3^s/2^Σe) or **using fewer rules**. Validation targets differ from test, so prefer rules that cover whole broad classes over rules tuned to guessed targets.
3. Don't probe the hidden targets with many evals. That's the kind of overfitting the hills rules forbid, and it won't transfer to the test split anyway.

Stopping criteria: a strict tie-breaker improvement verified, or the time box expires. Keep journal.html current.

Once you have your best result, ask me whether I want it on the leaderboard. If yes: `hills eval <best-dir> -H collatz-modular-descent -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`. Never submit without my yes.
