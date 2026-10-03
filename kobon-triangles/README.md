# kobon-triangles/: folder guide

| Folder | What it holds |
|---|---|
| **`n39_470/`** | **Main result:** the official 470-triangle solution for n = 39, its signed AutoLab report, `verify.py`, `reproduce.sh` (byte-identical rebuild) and `scan_all_bases.sh` (248-base sweep). See [`../N39_470_SOLUTION.md`](../N39_470_SOLUTION.md). |
| `n18_93/` | Official n = 18 solution (93 triangles), its signed report, and the annealing runs that found it. |
| `src/` | Code: exact counter (`count.py`), structure statistics (`stats.py`), annealing (`search.py`, `polish.py`), best-line insertion (`grow.py`, `addline.py`, `grow_tp.py`), remove/re-insert (`lns.py`), exact deletion (`derive.py`, `peel.py`), doubling constructions (`doubling.py`, `basesearch.py`), SAT neighbourhood search (`sig.py`, `sat_lns.py`), bookkeeping (`best.py`, `report.py`, `shrink.py`, `simplify.py`, `official_check.py`). |
| `submissions/` | Best exact arrangement per n (`n*/solution.json`) and `BEST.md`. |
| `RESULTS.md` | Table of best values vs. upper bounds and published values. |
| `added/`, `derived/`, `peeled/`, `bases/`, `doubled/`, `simple39/`, `lns/`, `multiline/` | Intermediate arrangements from each method (insertion, deletion, peeling, doubling bases, simple versions, local search, multi-line beam). |
| `research/` | Literature survey (`literature.md`), n = 39 bound analysis (`bound_n39.md`), helper tools and n = 39 candidate pseudoline data. Third-party papers and gallery data are not included; sources are listed. |
| `deck/` | `build_deck.py` regenerates the slide deck (`../notes/kobon_deck.pdf`). |
| `scripts/` | Batch drivers used during the search (`run_*.sh`). |

Run everything from the repository root with `uv run python kobon-triangles/<path>.py …`.
