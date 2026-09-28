# 6. Busy Beaver 6 Certificates

**Hill:** [alejandrozu/busy-beaver-6-certificates](https://app.autolab.ai/hills/alejandrozu/busy-beaver-6-certificates) · v0.1.0

## The problem in one line
Design a **6-state, 2-symbol Turing machine** that runs for as many steps as possible on a blank tape and then **halts**.

## Background
- The Busy Beaver function `S(n)` is the maximum number of steps any halting n-state machine takes. `S(5)` was settled in 2024. `S(6)` is **open** and known to be astronomically large.
- Every halting machine you submit is an exact **lower-bound witness** for S(6).
- The catch: the evaluator **simulates step by step** within a **private step budget**. A machine that hasn't halted when the budget runs out is **rejected**, not scored as capped. So the real goal is the longest halting run that fits inside the hidden budget.

## Rules
- States `A`–`F` plus the halt state `H`. Start in state `A` at position 0 on an all-zero, two-way infinite tape.
- Each of the 12 transitions is `[write, move, next_state]`, where write ∈ {0, 1}, move ∈ {"L", "R"}, and next ∈ {A..F, H}.
- **All six states must actually be visited.**

## What you submit
A folder containing one JSON file:
```json
{ "transitions": {
    "A": {"0": [1,"R","B"], "1": [1,"R","H"]},
    "B": {"0": [1,"R","C"], "1": [1,"R","H"]},
    ...
    "F": {"0": [1,"R","H"], "1": [1,"R","H"]}
} }
```
That example halts after 6 steps.

## Scoring (lexicographic)
| Metric | Direction | Meaning |
|---|---|---|
| `steps` | maximize | exact number of transitions before halting |
| `ones` | maximize | number of 1s on the tape at halt |
| `tape_span` | maximize | width of the tape region visited |

## Leaderboard (as of 2026-09-27)
- #1 eychcue: **249,881 steps**, 554 ones, span 735
- #2 yavol: 246,872 steps
- #3 a-hamdi: 177,725 steps

## Key takeaways
- The best-known BB(6) champions run far longer than any budget can simulate, so they would be **rejected**. You need machines that halt "late but not too late."
- The hidden budget is unknown. Leaderboard scores (about 250k) are a hint about what's accepted. Validation and final evaluation use **different** budgets, so leave some margin.
- Approach: enumerate or search machines (for example from the bbchallenge dataset), simulate fast, and keep ones that halt with large step counts below the budget.
