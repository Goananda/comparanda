#!/usr/bin/env bash
# Rebuild data/source and data/catalogue from the current state of the catalogue's site.
# Usage: bash analysis/catalogue/run_catalogue.sh [work_dir]   (work_dir defaults to ./build_catalogue)
# Downloads about 3,500 pages (125 MB) at roughly one request per second: 40-120 minutes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
S="$ROOT/analysis/catalogue/scripts"; MAN="$ROOT/analysis/catalogue/manual"; OLD="$ROOT/data/source_2021"
W="${1:-$ROOT/build_catalogue}"; mkdir -p "$W/pages" "$W/out" "$W/result"
BASE=https://www.ruthenia.ru/folklore/berezkin
for f in index-left eng areas1 intro; do
  [ -s "$W/pages/$f.html" ] || { curl -sS -m 120 -o "$W/pages/$f.html" "$BASE/$f.html"; sleep 1; }
done
python3 -I "$S/fetch_all.py"   "$W/pages" 2 1.0                    # every motif page, about one request per second
python3 -I "$S/parse_areas.py" "$W/pages" "$W/out" --extra "$MAN/extra_units.tsv"   # units of 'Этносы и ареалы' and six traditions named only on motif pages
python3 -I "$S/parse_pages.py" "$W/pages" all "$W/out"             # names, regions, summary lists, cited sources
python3 -I "$S/match_units.py" "$W/out" "$MAN/names.tsv"           # name -> unit
python3 -I "$S/match_old.py"   "$W/out" "$OLD/groups_motifs.csv" "$MAN/unit_old.tsv"   # unit -> tradition of the 2021 tables
python3 -I "$S/assemble.py"    "$W/out" "$W/pages" "$OLD/groups_motifs.csv" "$OLD/motifs.csv" \
        "$ROOT/analysis/reference/traditions_2021.csv" "$MAN" "$W/result" --prefix "" --cv
python3 -I "$S/motif_texts.py" "$W/pages" "$OLD/motifs.csv" "$MAN" "$W/result" ""   # English and Russian text of every motif
cp "$W/result/"{pairs,motifs,traditions,units,open_names,learned_rules,entries}.csv "$ROOT/data/catalogue/"
python3 -I "$S/make_source.py" "$W/result" "" "$ROOT/data/source"  # the layout analysis/run_all.sh reads
echo "done: data/catalogue and data/source are up to date; now run analysis/run_all.sh"
