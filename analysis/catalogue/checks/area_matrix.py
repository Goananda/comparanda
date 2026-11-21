"""Within one area: which names on the pages explain which old traditions?
usage: python3 -I area_matrix.py <entries_units.tsv> <old_groups_motifs.csv> <unit_map.tsv> <area_key> [min_pages]"""
import sys, csv, collections
csv.field_size_limit(10**9)
f_ent, f_old, f_map, area = sys.argv[1:5]; mn = int(sys.argv[5]) if len(sys.argv) > 5 else 8
old = collections.defaultdict(set)
for r in csv.DictReader(open(f_old, encoding='utf-8-sig')): old[r['group']].add(r['motif_id'].lower())
um = list(csv.DictReader(open(f_map, encoding='utf-8'), delimiter='\t'))
print(um[0].keys())
links = {}
for r in um:
    if r['unit_id'].startswith(area + '#'): links[r['unit_id']] = r
for u, r in sorted(links.items(), key=lambda x: int(x[0].split('#')[1].split('~')[0].rstrip('abcdefghijklmnop') or 0)):
    print('  ', u, '|', {k: v for k, v in r.items() if k != 'unit_id'})
pages = collections.defaultdict(set); unit_of = collections.defaultdict(collections.Counter); allp = set()
with open(f_ent, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        allp.add(r['motif_id'])
        if r['flag'] in ('', 'summary') and r['region_key'] == area:
            pages[r['name'].lower()].add(r['motif_id']); unit_of[r['name'].lower()][r['unit_id']] += 1
olds = sorted({r.get('old', r.get('old_tradition', '')) for r in links.values()} - {''})
tr = [t for t in old if any(t in o.replace(' + ', '|').split('|') for o in olds)] or olds
print('old traditions linked to this area:', olds)
def jac(a, b): return len(a & b) / len(a | b) if a | b else 0
names = [n for n in pages if len(pages[n]) >= mn]
for t in sorted(old):
    s = old[t] & allp
    if len(s) < 8: continue
    best = sorted(names, key=lambda n: -jac(s, pages[n]))[:4]
    if jac(s, pages[best[0]]) >= 0.25:
        print(f'{t:36s} n={len(s):3d} <- ' + '; '.join(f'{n} (pages {len(pages[n])}, J={jac(s, pages[n]):.2f}, recall {len(s & pages[n])/len(s):.2f}, unit {unit_of[n].most_common(1)[0][0].split("#")[-1]})' for n in best))
