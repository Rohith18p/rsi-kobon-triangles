#!/bin/sh
# Reproduce the full sweep: best 39th line for every 38-line / 450-triangle arrangement
# in the Parpalak-Utkin gallery (248 bases). Prints the distribution of results.
#
#   sh kobon-triangles/n39_470/scan_all_bases.sh            (all 248; ~5-10 min on 4 cores)
#   LIMIT=5 sh kobon-triangles/n39_470/scan_all_bases.sh    (quick test on the first 5)
#
# Run reproduce.sh first (it fetches the pinned gallery commit into build/).
set -eu
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
BUILD="$ROOT/kobon-triangles/n39_470/build"
UD1="$BUILD/ud1-kobon-solutions"
OUT="$BUILD/scan"
JOBS=${JOBS:-4}
LIMIT=${LIMIT:-100000}
test -d "$UD1/gallery/data/38" || { echo "run reproduce.sh first"; exit 1; }
mkdir -p "$OUT/bases" "$OUT/grown"
cd "$ROOT"
ls "$UD1"/gallery/data/38/*.json | head -n "$LIMIT" > "$OUT/list.txt"
cat > "$OUT/one.sh" <<EOF
#!/bin/sh
f=\$1; id=\$(basename \$f .json)
cd "$ROOT"
UD1_DIR="$UD1" uv run python kobon-triangles/research/tools/ud1_to_hill.py \$f "$OUT/bases/\$id.json" > /dev/null 2>&1 || { echo "\$id convert-failed"; exit 0; }
NUMBA_NUM_THREADS=1 uv run python kobon-triangles/src/grow.py "$OUT/bases/\$id.json" --add 1 --angles 720 \
  --out "$OUT/grown" --tag "\$id-" 2>/dev/null | sed -n 's/.*exact=\([0-9]*\).*/'"\$id"' \1/p'
EOF
chmod +x "$OUT/one.sh"
xargs -P "$JOBS" -n 1 "$OUT/one.sh" < "$OUT/list.txt" | tee "$OUT/results.txt"
echo "== distribution (triangles with 39 lines : number of bases)"
awk '{print $2}' "$OUT/results.txt" | sort | uniq -c | awk '{print $2" : "$1}'
