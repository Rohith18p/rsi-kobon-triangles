#!/bin/sh
cd "$(dirname "$0")"
B=derived/big
export NUMBA_NUM_THREADS=4
uv run python src/grow.py added/n39_469_u38-grow.json --add 1 --tag g39-
uv run python src/derive.py derived/n48_720_p49-b5-del47_small.json --delete 1 --out derived --tag d48-
uv run python src/grow.py added/n47_691_p46-add.json --add 1 --tag g47-
uv run python src/derive.py $B/50-1ca8a076ws55c.json --delete 2 --out derived --tag u50b-
for f in $B/50-*.json; do uv run python src/grow.py $f --add 1 --tag u50$(basename $f .json | cut -c4-8)- ; done
uv run python src/derive.py $B/54-17vssivj9h53k.json --delete 2 --out derived --tag u54-
uv run python src/grow.py added/n51_812_u50-grow.json --add 1 --tag g51-
uv run python src/grow.py $B/53-15mkncfph5119.json --add 3 --tag u53-
echo DONE
