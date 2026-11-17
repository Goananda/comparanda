"""Assemble the single-file page from src/ and the data.

Usage: python3 build.py <src_dir> <out_dir> <data.json> <geo.json>   -> <out_dir>/index.html

src/style.css, src/body.html and src/app.js hold the frame of the page and the original views.
Every further view is a pair src/views/<name>.html + src/views/<name>.js; they are inserted at the @@VIEWS@@ markers.
"""
import sys, json, glob, os
src, out_dir, data_path, geo_path = sys.argv[1:5]
read = lambda p: open(p, encoding='utf-8').read()
css = read(f'{src}/style.css')
parts = sorted(glob.glob(f'{src}/views/*.js'))
body = read(f'{src}/body.html'); js = read(f'{src}/app.js')
assert body.count('<!--@@VIEWS@@-->') == 1 and js.count('/*@@VIEWS@@*/') == 1
body = body.replace('<!--@@VIEWS@@-->', '\n'.join(read(p[:-3] + '.html') for p in parts))
js = js.replace('/*@@VIEWS@@*/', '\n'.join(f'// ------------------------------------------------------------ views/{os.path.basename(p)}\n' + read(p) for p in parts))
esc = lambda t: t.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
D = json.load(open(data_path, encoding='utf-8')); D['m'].pop('desc', None)  # the page shows codes and titles only; full definitions stay in data/source/motifs.csv
for unused in ('ref', 'decay'): D.pop(unused, None)                     # kept in data.json for the tables, not needed by the page
data = esc(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
geo = esc(json.dumps(json.load(open(geo_path, encoding='utf-8')), ensure_ascii=False, separators=(',', ':')))
assert '</script' not in js.lower()
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Comparanda</title>
<meta name="description" content="Comparanda: myths remember geography. Interactive views of 2,563 folklore and mythology motifs across 923 traditions, based on the Berezkin and Duvakin catalogue.">
<meta property="og:type" content="website">
<meta property="og:title" content="Comparanda: myths remember geography">
<meta property="og:description" content="Group the world's traditions by their folklore motifs alone and the map redraws itself. Culture clusters, the full tree, principal axes, motif complexes, a motif atlas and correlations.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Old+Standard+TT:wght@400&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{body}
<script id="data" type="application/json">{data}</script>
<script id="geo" type="application/json">{geo}</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
{js}
</script>
</body>
</html>
'''
open(f'{out_dir}/index.html', 'w', encoding='utf-8').write(html)
print('index.html bytes', len(html.encode('utf-8')), '| views:', ', '.join(os.path.basename(p)[:-3] for p in parts))
