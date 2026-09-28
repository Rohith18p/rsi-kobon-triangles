# 4. Grothendieck Constant Witnesses

**Hill:** [alejandrozu/grothendieck-constant-witnesses](https://app.autolab.ai/hills/alejandrozu/grothendieck-constant-witnesses) · v0.1.0

## The problem in one line
Find a small ±1 matrix and unit vectors for which the **vector value** is as large as possible compared with the **sign value**. The ratio is a lower bound for the real Grothendieck constant `K_G`.

## Background
- For a sign matrix `A`:
  - `sign(A) = max over x_i, y_j ∈ {−1, +1} of Σ A_ij x_i y_j`
  - `vector(A; u, v) = Σ A_ij ⟨u_i, v_j⟩` with unit vectors u_i, v_j
- Then **vector / sign ≤ K_G**.
- The exact `K_G` is **open**. Known range is roughly **1.676 ≤ K_G < 1.782**. The lower bound comes from Davie/Reeds, the upper from Krivine, later improved by Braverman et al.

## What you submit
A folder containing `solution.json`:
```json
{
  "matrix": [[1, 1], [1, -1]],
  "left_vectors":  [[[1,1],[0,1]], [[0,1],[1,1]]],
  "right_vectors": [[[3,5],[4,5]], [[3,5],[-4,5]]]
}
```
- `matrix` is m×n with **2 ≤ m, n ≤ 8**, entries ±1.
- Vectors are in dimension **2 ≤ d ≤ 16**, with coordinates as rational pairs `[num, den]` (reduced, |values| ≤ 10⁶).
- Every vector must have squared norm **exactly 1**. No floats.
- That example is the CHSH matrix with ratio **7/5 = 1.4**.

## Scoring (lexicographic)
| Metric | Direction | Meaning |
|---|---|---|
| `gap_ppm` | maximize | ⌊10⁶ · vector / sign⌋ |
| `matrix_area` | minimize | m · n |
| `certificate_bits` | minimize | total bit length of the rational numbers |

## Leaderboard (as of 2026-09-27)
- Top: **gap_ppm = 1414213** (≈ √2) with a 2×2 matrix and 80 bits (tie between a-hamdi and wilsonwu-ai).
- That's just CHSH with near-optimal rational vectors.

## Key takeaways
- √2 is the 2×2 ceiling. To go higher you **need bigger matrices** (up to 8×8) and higher-dimensional vectors.
- Workflow: pick a matrix, solve the SDP for the vector value numerically, then **round to exact rational unit vectors**. Rational points on spheres come from Pythagorean-style parametrizations.
- With only 8×8 matrices you won't reach 1.676. The goal is to beat √2 by as much as possible.
