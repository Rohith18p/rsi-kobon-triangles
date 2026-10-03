# 3. 3×3 Matrix Multiplication Tensor

**Hill:** [alejandrozu/matrix-multiplication-tensor-3x3](https://app.autolab.ai/hills/alejandrozu/matrix-multiplication-tensor-3x3) · v0.1.0

## The problem in one line
Multiply two 3×3 matrices using as **few scalar multiplications** as possible. The schoolbook method uses 27.

## Background
- **Laderman (1976)** did it with **23** multiplications (rank 23).
- **Open question:** can it be done with **22**? The best known lower bound is 19 (Bläser).
- A rank-22 scheme would be a major result. A **new rank-23 scheme with smaller support** (fewer nonzero coefficients) also counts as progress on this hill.

## How a scheme works
For each product t = 1..R:
```
L_t(A) = Σ U[t][i]·A[i]     (A in row-major order)
R_t(B) = Σ V[t][j]·B[j]     (B in row-major order)
M_t    = L_t(A) · R_t(B)
C[k]   = Σ W[t][k]·M_t      (C indexed column-major: k = 3*col + row)
```
The evaluator checks all **729 Brent equations** exactly.

## What you submit
A folder containing `solution.json` with three matrices `u`, `v`, `w`:
- Same number of rows (R, from 1 to 40), each row with **9** coefficients.
- Coefficients are exact rationals: an integer, or `[num, den]`, with |values| ≤ 10⁶.

## Scoring (lexicographic)
| Metric | Direction | Meaning |
|---|---|---|
| `rank` | minimize | number of products (rows) |
| `support` | minimize | total nonzero entries in u, v, w |

## Starting point
The baseline is Laderman's rank-23 decomposition.

## Key takeaways
- The realistic goal is a rank-23 scheme with support **< 139**.
- Known rank-23 schemes form large families (many are publicly catalogued), so you can search them for sparse members, or use flip-graph / SAT / alternating-least-squares search with rational rounding.
- Watch out for the column-major convention on `W`. It's an easy source of bugs.
