# n = 18: 93 triangles (official)

- `solution.json`: 18 integer lines, 93 triangles. It is a simple arrangement: 153 crossing points, no triple points or parallels, 288 bounded segments, 9 unused.
- Official AutoLab score 93: climb `rohith18p/kobon-triangles`, experiment `9054ca51`, hill tree hash `7d3f1d91dcb8…`, params `n = 18`, 2026-09-27T19:21:08Z. The signed report is `official_report.json`.
- 93 ties the best known value. Blanc (2011) proved that a simple 18-line arrangement has at most 93 triangles. 94 would need triple points or parallels, and none has ever been found.
- Found by simulated annealing (`src/search.py --n 18 --workers 10 --minutes 1`): 7 of 10 one-minute runs reached 93 (`annealing_runs/`). The runs are time-limited, so reruns give different but equivalent 93s.
- Verify: `uv run python kobon-triangles/src/count.py kobon-triangles/n18_93/solution.json`
