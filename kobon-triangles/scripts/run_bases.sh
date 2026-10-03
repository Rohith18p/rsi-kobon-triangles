#!/bin/sh
cd "$(dirname "$0")/.."
for n in 30 34 38 40 42 44 46; do
  echo "=== n=$n $(date +%H:%M:%S)"
  uv run python src/basesearch.py --n $n --minutes 8 --workers 10 --out bases 2>&1 | grep -v "^  File\|^    "
done
echo "=== DONE $(date +%H:%M:%S)"
