#!/bin/sh
cd "$(dirname "$0")/src"
for cfg in "18 1 8" "18 2 5" "18 3 5" "18 6 4" "20 1 8" "20 2 5" "20 4 4"; do
  set -- $cfg
  echo "=== n=$1 sym=$2 minutes=$3 $(date +%H:%M:%S)"
  uv run python search.py --n $1 --sym $2 --minutes $3 --workers 10 --seed $((RANDOM)) --out ../candidates 2>&1 | head -4
done
echo "=== DONE $(date +%H:%M:%S)"
