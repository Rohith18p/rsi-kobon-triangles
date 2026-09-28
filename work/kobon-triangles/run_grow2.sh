#!/bin/sh
cd "$(dirname "$0")"
B=derived/big
export NUMBA_NUM_THREADS=4
for f in $B/43-*.json; do uv run python src/grow.py $f --add 1 --tag u43$(basename $f .json | cut -c4-8)- ; done
uv run python src/grow.py research/records/n38_450_ud1_38_38-1l8x1qx7on4je.json --add 2 --tag u38-
uv run python src/grow.py $B/46-357oftdeaclwg.json --add 2 --tag u46-
uv run python src/derive.py $B/41-2efd1i95r9uad.json --delete 1 2 --out derived --tag u41-
uv run python src/derive.py $B/45-1ag30qt2bdlql.json --delete 1 --out derived --tag u45-
echo DONE
