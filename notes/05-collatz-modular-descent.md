# 5. Collatz Modular Descent

**Hill:** [alejandrozu/collatz-modular-descent](https://app.autolab.ai/hills/alejandrozu/collatz-modular-descent) · v0.1.0

## The problem in one line
Write exact "descent rules" proving that every odd number in a residue class gets **smaller** after a fixed number of Collatz steps. Cover as many hidden target classes as possible.

> This does **not** ask you to prove the Collatz conjecture. Finite coverage settles nothing about it.

## Background
The accelerated Collatz step for odd `n` is:
```
C(n) = (3n + 1) / 2^v2(3n + 1)
```
A **rule** says: for all `n ≡ r (mod 2^k)`, the 2-adic valuations along the first `s` steps are exactly `[e1, ..., es]`, and `C^s(n) < n`.

The evaluator checks that:
- `k ≥ 1 + e1 + ... + es`, so the valuation pattern is fixed for the whole class
- `3^s < 2^(e1 + ... + es)`, so the map is contracting
- `C^s(n) < n` for every positive n in the class

## What you submit
A folder containing one JSON file:
```json
{ "rules": [
    {"modulus_power": 4, "residue": 9,  "exponents": [2]},
    {"modulus_power": 4, "residue": 13, "exponents": [3]}
] }
```
- `modulus_power` k is 2..32, `residue` is odd with 0 < r < 2^k.
- Limits: ≤ 512 rules, ≤ 24 steps per rule, exponents ≤ 32. No duplicate rules.

## Hidden targets
- These are secret odd residue classes mod 2^8 … 2^12, weighted.
- A target is covered if it's a subclass of one of your rules. **Broader rules (smaller k) cover more.**
- Validation and final evaluation use different secret target sets.

## Scoring (lexicographic)
| Metric | Direction | Meaning |
|---|---|---|
| `coverage_ppm` | maximize | fraction of targets covered × 10⁶ |
| `min_descent_ppm` | maximize | weakest contraction among rules that are used × 10⁶ |
| `rule_count` | minimize | number of rules |

## Key takeaways
- Some odd classes (for example n ≡ 3 mod 4 paths like 27) need long exponent sequences, so full coverage with few rules is a clever-compression problem.
- Only worth attempting if you can improve `min_descent_ppm` while keeping 100% coverage and ≤ 3 rules.
