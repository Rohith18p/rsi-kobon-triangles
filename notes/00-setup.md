# Setup: tools installed for RSI_Math

## Lean (for Erdős #3 and any formalization work)
- `elan` (Homebrew `elan-init`) with toolchain **leanprover/lean4:v4.33.1**, the default and the same version the erdos-3 checker uses.
- `lean/formal-conjectures/` is a clone of [google-deepmind/formal-conjectures](https://github.com/google-deepmind/formal-conjectures). It pins Lean v4.33.1 and Mathlib, and has the `FormalConjecturesUtil` import that the hill statement uses.
  - Erdős #3 file: `lean/formal-conjectures/FormalConjectures/ErdosProblems/3.lean`
  - Check a file: `cd lean/formal-conjectures && lake env lean path/to/File.lean`
  - After `git pull`, refresh the Mathlib cache with `lake exe cache get`.
- Editor: VS Code with the **lean4** extension. Open the `lean/formal-conjectures` folder.

## Python (for the six construction hills)
- `uv` manages the environment in `.venv/`, defined by `pyproject.toml` (Python 3.12).
- Run code with `uv run python script.py`. Notebooks: `uv run jupyter lab`.
- Packages and what they're for:
  | Package | Use |
  |---|---|
  | numpy, scipy, sympy, mpmath, gmpy2 | numerics, exact rationals, big integers |
  | numba | fast simulators (Busy Beaver, Collatz, triangle counting) |
  | networkx | Ramsey templates, Cayley graphs |
  | cvxpy (Clarabel, SCS, HiGHS) | SDPs for Grothendieck witnesses |
  | ortools | CP-SAT / MIP search |
  | python-sat | SAT search (matrix-multiplication schemes) |
  | matplotlib, jupyterlab, tqdm, pytest | plotting, notebooks, tests |
- Add a package: `uv add <name>`

## AutoLab evaluator
- `hills` CLI v0.11.0 (installed with `uv tool install hills==0.11.0`) scores a submission locally: `hills eval <dir> -H <hill>`.
- Downloading the hill evaluators needs an AutoLab login. Their official route is the agent skill: `npx skills add autolab-ai/hills`.
