#!/bin/sh
# Rebuild the n=39 / 470-triangle arrangement from scratch and check it matches solution.json.
#
#   sh kobon-triangles/n39_470/reproduce.sh        (run from the repository root)
#
# Needs: git, uv (Python 3.12 deps from pyproject.toml), internet access to github.com.
# Steps:
#   1. fetch the Parpalak-Utkin gallery (ud1/kobon-solutions) at the pinned commit
#   2. convert the 38-line base 38-74kq3v76alw (450 triangles) to exact integers
#   3. add the best 39th line (exhaustive angle x gap grid, deterministic, seed 0)
#   4. verify exactly with two counters and compare with the submitted solution.json
set -eu
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PKG="$ROOT/kobon-triangles/n39_470"
BUILD="$PKG/build"
UD1_COMMIT=cecd2b1b4dd77f6a2453ec45676e4698cd8956f9
UD1="$BUILD/ud1-kobon-solutions"
BASE_ID=38-74kq3v76alw
mkdir -p "$BUILD"
cd "$ROOT"

echo "== 1/4 fetch gallery ud1/kobon-solutions @ ${UD1_COMMIT%${UD1_COMMIT#????????}}"
if [ ! -d "$UD1/.git" ]; then
  git init -q "$UD1"
  git -C "$UD1" remote add origin https://github.com/ud1/kobon-solutions.git
fi
git -C "$UD1" fetch -q --depth 1 origin "$UD1_COMMIT"
git -C "$UD1" checkout -q FETCH_HEAD
GALLERY_JSON="$UD1/gallery/data/38/$BASE_ID.json"
test -f "$GALLERY_JSON"

echo "== 2/4 convert base $BASE_ID to exact integer lines"
UD1_DIR="$UD1" uv run python kobon-triangles/research/tools/ud1_to_hill.py "$GALLERY_JSON" "$BUILD/base38.json"

echo "== 3/4 add the best 39th line"
NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-4} uv run python kobon-triangles/src/grow.py "$BUILD/base38.json" \
  --add 1 --angles 720 --out "$BUILD" --tag repro-

echo "== 4/4 verify"
OUT="$BUILD/n39_470_repro-grow.json"
uv run python kobon-triangles/n39_470/verify.py "$OUT"
if cmp -s "$OUT" "$PKG/solution.json"; then
  echo "REPRODUCED: byte-identical to kobon-triangles/n39_470/solution.json"
else
  echo "NOTE: rebuilt file differs byte-wise from solution.json (see verify output for its count)"
fi
