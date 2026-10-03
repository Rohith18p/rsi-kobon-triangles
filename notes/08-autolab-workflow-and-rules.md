# AutoLab workflow and competition rules

Sources: AutoLab hill pages (local-climb instructions), the `hills` skill docs (github.com/autolab-ai/hills), and the **Competition and Judging Handbook** (rsihouse.ai/openmath/handbook.pdf).

## Key dates
- Event: **Sun 27 Sep – Fri 2 Oct 2026**.
- **Hard cutoff:** everything score-bearing must be submitted **before 00:00 EDT Sat 3 Oct** (9 pm PDT Fri). No new math after the cutoff.
- Ties are broken by the **earliest server timestamp**, so submit improvements as soon as they're solid.

## The three pieces
| Thing | What it is | Where |
|---|---|---|
| `hills` CLI | Local evaluator. Scores a submission folder and signs the report with a per-machine key | installed (v0.11.0) |
| `autolab` CLI | Talks to app.autolab.ai: login, pull hills, submit reports, `serve` (turn this machine into a compute node) | not installed yet |
| hills skill | Instructions for the coding agent (the experiment loop, journal.html, iron rules) | `npx skills add autolab-ai/hills` |

## Connecting (one-time)
```sh
curl -fsSL https://app.autolab.ai/install.sh | sh     # installs autolab CLI via uv
autolab --url https://app.autolab.ai login           # opens browser; or --token <PAT>
autolab --url https://app.autolab.ai whoami
npx skills add autolab-ai/hills                      # optional: agent skill
```
Pull a hill. Run this **from rsi-kobon-triangles**, because it lands in `./.autolab/hills/<name>`:
```sh
autolab --url https://app.autolab.ai hills pull alejandrozu/kobon-triangles
```

## Can I solve locally and upload? Yes
1. Develop and search locally with any tools. The handbook allows any AI or tool, but you must disclose them.
2. Score locally with `hills eval <dir> -H <name> -o reports/NNN.json`.
3. Submit the best to the hub leaderboard: `hills eval <best> -H <name> -o report.json`, then `autolab --url https://app.autolab.ai hills submit report.json`.

**Competition credit is a separate step.** Handbook §7.2: every claim needs an AutoLab **submission ID, Hill tree hash, Climb link, immutable final commit, final evaluator report**. The competition-specific workflow (templates, namespaces) "will be linked from the event website before submissions open."
- **Open question to ask the organizers:** does a locally produced report submitted with `autolab hills submit` count as a **Climb**? Or do you need to start a Climb on AutoLab? If you need a Climb, you can choose "On AutoLab" plus "your coding agent" and use **this Mac as the compute node** via `autolab serve`, so you don't have to rent compute.

## How competition points actually work (handbook §4–5)
- **Only formalized, machine-checked results count.** A hill score is necessary but not sufficient. Two human reviewers check fidelity, novelty and attribution.
- Points = `b · m · p · D²/1000`
  - D = OPDP difficulty (0–1000)
  - p = progress (0–1)
  - b = 1.1 for the focus set (these 7 hills)
  - m = 1, or ½ for variations
- Progress bands:
  - **P1 = .01–.05** for a "narrow certified computation"
  - **P2 = .05–.15** for a nontrivial improvement short of the central obstacle
  - **P3 = .15–.35** for a meaningful bound or special case
- Known mathematics earns no open-problem credit. Reproducing a published construction = 0.
- A **new record** (a better bound than the literature) is what earns points. Beating other teams on a leaderboard metric that isn't an open problem, such as `support` or tie-breakers, likely earns ~0. This is my reading of the handbook, so confirm with the organizers.

## Paperwork to keep from day 1 (handbook §6–8)
- A **timestamped baseline commit**, plus an explicit "new-work delta" (what was done during the event).
- Disclose tools: models and versions (e.g. Claude Opus 5.5 via Claude Code), libraries, compute.
- Keep code, seeds, notebooks and provenance. Full prompt logs aren't required.
- Submission packet: identity/target, artifact (hill hash, climb, commit, report), provenance, publication permission.

## hills iron rules (break these and your results are worthless)
- Only `hills eval` output is a result. Anything else is a "dev number".
- Never edit report files (they're signed). Never read `private/`.
- `--final` only once, for the final claim. Don't re-run it and keep the best.
- Don't probe hidden limits or targets with repeated evals.
- Commit before every eval (on branch `hills/<name>`). Never `reset --hard` scored commits.
