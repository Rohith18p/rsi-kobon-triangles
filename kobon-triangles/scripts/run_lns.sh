#!/bin/sh
# usage: run_lns.sh MINUTES TAG n:seed ...
cd "$(dirname "$0")/.."
MIN=$1; TAG=$2; shift 2
for spec in "$@"; do
  n=${spec%%:*}; seed=${spec#*:}
  NUMBA_NUM_THREADS=2 nohup uv run python src/lns.py "$seed" --minutes "$MIN" --out lns --tag "$TAG" --rseed $$ > "logs/lns_${TAG}n$n.log" 2>&1 &
done
