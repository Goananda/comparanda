"""Write the assembled catalogue in the layout the analysis pipeline reads (data/source).

usage: python3 -I make_source.py <result_dir> <prefix> <source_dir>
Writes motifs.csv, groups_motifs.csv (,group,motif_id) and coords_clean.json ([{group, longitude, latitude}]).
motifs.csv: motif_id, title, description (the English version), title_ru, description_ru (the Russian version),
title_source, description_source (where the English text comes from; see motif_texts.py).  Only motifs of the authors'
digital database (area codes outside brackets) are kept.  A tradition that unites two traditions of the old table
gets both names, separated by a comma.
"""
import csv, json, os, sys

res, prefix, dst = sys.argv[1:4]
csv.field_size_limit(10 ** 9)
rd = lambda n: list(csv.DictReader(open(os.path.join(res, prefix + n), encoding='utf-8-sig')))
P, M, T = rd('pairs.csv'), rd('motifs.csv'), rd('traditions.csv')
os.makedirs(dst, exist_ok=True)
disp = lambda t: t.replace(' + ', ', ')

pairs = sorted({(disp(r['tradition']), r['motif_id']) for r in P if r['motif_in_digital_db'] == '1'})
coords = {}
for t in T:
    if t['longitude'] != '' and t['latitude'] != '':
        coords[disp(t['tradition'])] = (float(t['longitude']), float(t['latitude']))
no_xy = sorted({g for g, _ in pairs if g not in coords})
if no_xy:
    print('! traditions without coordinates (dropped):', no_xy)
pairs = [(g, m) for g, m in pairs if g in coords]
used_m = {m for _, m in pairs}
used_g = sorted({g for g, _ in pairs})

mrows = [m for m in M if m['motif_id'] in used_m]
no_title = [m['motif_id'] for m in mrows if not m['title_en']]
if no_title:
    print('! motifs without an English title (Russian title used):', len(no_title), no_title[:20])
with open(os.path.join(dst, 'motifs.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['motif_id', 'title', 'description', 'title_ru', 'description_ru', 'title_source', 'description_source'])
    for m in mrows:
        w.writerow([m['motif_id'], m['title_en'] or m['title_ru'], m['description_en'], m['title_ru'], m['description_ru'],
                    m['title_en_source'], m['description_en_source']])
with open(os.path.join(dst, 'groups_motifs.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['', 'group', 'motif_id'])
    for i, (g, m) in enumerate(pairs):
        w.writerow([i, g, m])
json.dump([{'group': g, 'longitude': coords[g][0], 'latitude': coords[g][1]} for g in used_g],
          open(os.path.join(dst, 'coords_clean.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'source written to {dst}: {len(used_g)} traditions, {len(mrows)} motifs, {len(pairs)} pairs')
