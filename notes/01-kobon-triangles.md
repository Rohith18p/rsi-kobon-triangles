# 1. Kobon Triangles

**Hill:** [alejandrozu/kobon-triangles](https://app.autolab.ai/hills/alejandrozu/kobon-triangles) · v0.1.0

## The problem in one line
Place exactly `n` straight lines in the plane to get as many **bounded triangular faces** as possible.

## Details
- A triangle counts only if **no other line crosses its interior**. A big triangle cut in two by another line doesn't count, but the pieces might.
- Triangles may share vertices. Parallel lines and 3+ lines meeting at one point are allowed.
- This is a **construction** task. A higher count doesn't prove it's the best possible.
- `n` is a parameter from 3 to 100 (default **18**). Each `n` has its own leaderboard.

## What you submit
A folder containing `solution.json`:
```json
{"lines": [[1, 0, 0], [0, 1, 0], [1, 1, -1]]}
```
- Each `[a, b, c]` is the line `a*x + b*y + c = 0`.
- Exactly `n` triples of **integers only** (no floats), each with |coefficient| ≤ 10^30.
- `a` and `b` can't both be 0. Duplicate (proportional) lines are rejected.
- File must be ≤ 64 KB.
- The evaluator uses exact rational arithmetic, with no tolerance and no bounding box.

## Scoring
| Metric | Direction |
|---|---|
| `triangles` | maximize |

## Starting point
The baseline is 18 tangent lines `2i·x − y − i² = 0` for i = 0..17, which gives **16 triangles**.

## Leaderboard (as of 2026-09-27, n = 18)
- Top score: **93 triangles** (six users tied), next is 92.
- **Literature (Wikipedia, Kobon triangle problem):** the best known for n = 18 is **93**. The leaders have matched the known record but not beaten it.
- Upper bound: Tamura gives ⌊n(n−2)/3⌋ = 96. Clément–Bader showed that bound can't be reached when n ≡ 0 or 2 (mod 6), so for n = 18 the max is at most **95**.

## Does a higher count need a proof?
- **No.** The `solution.json` is the proof. The evaluator counts the triangles with exact arithmetic, so a valid 94-line arrangement is a certified "94 is achievable" result.
- Proving that no arrangement can do better (an upper bound or optimality proof) is a separate and much harder problem. This hill doesn't score it.
- For **competition credit**, the organizers also do a review (novelty check against the literature, plus their certificate protocol). Getting 94 or 95 for n = 18 would be a **new record**, not just a leaderboard win.

## Where the gaps are (best known vs. upper bound)
| n | best known | upper bound |
|---|---|---|
| 10, 11, 12 | one short of the bound | |
| 18 | 93 | 95 |
| 20 | 117 | 120 |

## Key takeaways
- To beat the pack at n = 18 you need 94 or 95, and nobody has ever found that. n = 20 has a bigger gap and may be less crowded on the leaderboard.
- Near-optimal arrangements are usually highly symmetric (think rotational symmetry) followed by local perturbation. Output needs exact integer coefficients, so rationalize carefully.
