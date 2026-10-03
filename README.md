# rsi-kobon-triangles

Work for the **Open Math Challenge** (Open Problems Hack at MIT, Sep 27 – Oct 2, 2026) on the
AutoLab hill [`alejandrozu/kobon-triangles`](https://app.autolab.ai/hills/alejandrozu/kobon-triangles).
The task is the **Kobon triangle problem**: place n straight lines so as to maximize the number of bounded
triangular faces that no other line crosses.

## Results (exact, integer arithmetic; official AutoLab scores where noted)

**For judges:** submission packet [`SUBMISSION.md`](SUBMISSION.md) · paper [`paper/kobon39.pdf`](paper/kobon39.pdf) · main result [`N39_470_SOLUTION.md`](N39_470_SOLUTION.md) (method, verification, reproduction). Frozen at git tag `final-submission`.

| n | triangles | status |
|---|---|---|
| 39 | **470** | Official AutoLab score (experiment `23e84fc7`, 27 Sep 2026). No 39-line arrangement had been published before (OEIS A006066 lists "?"). Upper bound: 481. Rebuild: `sh kobon-triangles/n39_470/reproduce.sh`. |
| 18 | 93 | Official AutoLab score; ties the best known value. See `kobon-triangles/n18_93/`. |
| 40, 44, 47, 48, 51–96 | see `kobon-triangles/RESULTS.md` | First values for n with no published arrangement (dev numbers, exact-verified; not all submitted). |

- Slide deck: [`notes/kobon_deck.pdf`](notes/kobon_deck.pdf)
- Observations and a conjecture (a generalized Blanc bound for even n): [`notes/09-kobon-observations.md`](notes/09-kobon-observations.md)
- Folder guide: [`kobon-triangles/README.md`](kobon-triangles/README.md)
- Solution format: `{"lines": [[a, b, c], ...]}`, one line a·x + b·y + c = 0 per entry.

## Layout

```
notes/                   problem summaries, workflow/rules, observations, slide deck
prompts/                 agent prompts per problem
SUBMISSION.md            judging packet: results, checker scope, references, access, open items
N39_470_SOLUTION.md      the n = 39 / 470 solution: method, anatomy, verification, reproduction
paper/                   paper (kobon39.pdf, Typst source, figures)
kobon-triangles/
  n39_470/               official 470 solution, signed report, verify.py, reproduce.sh, scan_all_bases.sh
  n18_93/                official 93 solution (n = 18), signed report, annealing runs
  src/                   search, exact counting, SAT encodings, construction tools
  scripts/               batch drivers used during the search
  deck/build_deck.py     regenerates the slide deck from the data
  submissions/           best arrangement per n (exact)
  added/ peeled/ bases/ doubled/ simple39/ multiline/   intermediate results
  research/              literature survey and bound analysis (third-party data excluded)
```

Key tools in `kobon-triangles/src/`:
- `count.py`: exact triangle counter
- `stats.py`: crossings, triple points, segment ledger
- `search.py`, `polish.py`: annealing
- `grow.py`, `lns.py`: best-line insertion and remove/re-insert
- `derive.py`, `peel.py`: exact line deletion
- `doubling.py`, `basesearch.py`: Bartholdi–Blanc–Loisel doubling with explicit integer realizations
- `sig.py`, `sat_lns.py`: signotope SAT neighbourhood search with LP straightening

Run with `uv run python kobon-triangles/src/<tool>.py …` (Python 3.12, deps in `pyproject.toml`).

## Credit

Several constructions build on published work, credited where used:
- the 38-line bases and many gallery arrangements: Parpalak & Utkin (ud1/kobon-solutions, arXiv 2604.22035, 2607.29236)
- the doubling construction: Bartholdi, Blanc & Loisel 2008 (arXiv 0706.0723)
- the SAT tooling: Savchuk (arXiv 2507.07951; kobon-cnf, LineOrder), with the Kissat solver
- the upper bounds: Tamura, Felsner–Kriegel, Blanc, Clément–Bader

Third-party papers and data are not redistributed here. `kobon-triangles/research/literature.md` lists the sources.

Tools used: Python (numba, python-sat, SciPy/HiGHS), Kissat 4.0.4, and Claude Code (Claude Opus 5.5) as an AI assistant.
