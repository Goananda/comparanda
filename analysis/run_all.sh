#!/usr/bin/env bash
# Rebuild everything from data/source: analysis outputs, derived tables and index.html.
# Usage: bash analysis/run_all.sh [work_dir]   (work_dir defaults to ./build; takes roughly 15 minutes)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${1:-$ROOT/build}"
mkdir -p "$WORK"
python3 "$ROOT/analysis/prep.py"   "$ROOT/data/source" "$WORK"    # 0/1 matrix, tidy tradition and motif lists
python3 "$ROOT/analysis/clus.py"   "$WORK"                         # LSA + Ward, consensus over 1,200 resamples of motifs (8 minutes)
python3 "$ROOT/analysis/nmf.py"    "$WORK" 12                      # 12 NMF motif complexes
python3 "$ROOT/analysis/embed.py"  "$WORK"                         # UMAP of traditions and motifs
python3 "$ROOT/analysis/export.py" "$WORK"                         # axes, distance decay, everything the page needs -> data.json
python3 "$ROOT/analysis/make_tables.py" "$WORK" "$ROOT/data/derived"
(cd "$ROOT/analysis" && npm install --silent && node build_geo.mjs "$WORK/data.json" "$WORK/geo.json")
python3 "$ROOT/analysis/site/build.py" "$ROOT/analysis/site/src" "$ROOT" "$WORK/data.json" "$WORK/geo.json"
echo "done: index.html and data/derived/ are up to date"
