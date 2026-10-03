#!/bin/sh
# usage: run_g38.sh WORKER NWORKERS
cd "$(dirname "$0")/.."
W=$1; N=$2; i=0
export NUMBA_NUM_THREADS=2
for f in research/raw/ud1_kobon-solutions/38/*.json; do
  i=$((i+1)); [ $((i % N)) -eq $W ] || continue
  id=$(basename $f .json)
  timeout 300 uv run python research/tools/ud1_to_hill.py $f derived/g38/$id.json > /dev/null 2>&1 || { echo "CONVFAIL $id"; continue; }
  uv run python src/grow.py derived/g38/$id.json --add 1 --angles 720 --out added/g38 --tag $id- 2>&1 | grep -E "exact|Error" | sed "s/^/$id /"
done
echo "WORKER $W DONE"
