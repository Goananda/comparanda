"""List systematic disagreements between the assembled pairs and the old table.
usage: python3 -I confusions.py <result_dir> <prefix> <old_groups_motifs.csv> [min_count]"""
import csv, os, sys
from collections import Counter, defaultdict
csv.field_size_limit(10 ** 9)
res, prefix, f_old = sys.argv[1:4]
mn = int(sys.argv[4]) if len(sys.argv) > 4 else 5
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
P = rd(os.path.join(res, prefix + 'pairs.csv')); T = rd(os.path.join(res, prefix + 'traditions.csv'))
old = defaultdict(set)
for r in rd(f_old):
    old[r['motif_id'].lower()].add(r['group'])
areas = {}
for t in T:
    for o in t['tradition'].split(' + '):
        areas[o] = set(t['areas'].split('; ')) - {''}
got = defaultdict(set); names = defaultdict(Counter)
for r in P:
    for o in r['tradition'].split(' + '):
        got[r['motif_id']].add(o)
        for n in r['names_on_page'].split('; '):
            names[o][n.lower()] += 1
conf = Counter(); nm = Counter(); nx = Counter(); both = Counter()
for m in got:
    if m not in old:
        continue
    miss = old[m] - got[m]; extra = got[m] - old[m]
    for a in miss: nm[a] += 1
    for b in extra: nx[b] += 1
    for a in miss:
        for b in extra:
            if areas.get(a, set()) & areas.get(b, set()):
                conf[(a, b)] += 1
rows = [(v, a, b) for (a, b), v in conf.items() if v >= mn and v >= 0.4 * nm[a] and v >= 0.3 * nx[b]]
for v, a, b in sorted(rows, reverse=True)[:60]:
    print(f"{v:3d}  old '{a}' missing ({nm[a]}) <-> site '{b}' extra ({nx[b]}); names: {', '.join(n for n, _ in names[b].most_common(4))}")
print('top missing:', nm.most_common(30))
# names that co-occur with a missing old tradition in its own area and are not explained by the old table
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import region_key
E = defaultdict(list)
for e in rd(os.path.join(res, prefix + 'entries.csv')):
    if e['kind'] == 'main':
        E[e['motif_id']].append((region_key(e['region']), e['name'].lower(), e['tradition'], e['resolution']))
sugg = defaultdict(Counter)
for m in got:
    if m not in old:
        continue
    for t in old[m] - got[m]:
        for rk, n, tr, how in E[m]:
            if rk in areas.get(t, ()) and (not tr or not any(x in old[m] for x in tr.split(' + '))):
                sugg[t][(n, (tr or how)[:24])] += 1
print('--- missing tradition: candidate names (name, current assignment, n motifs)')
for t, n in nm.most_common(int(sys.argv[5]) if len(sys.argv) > 5 else 30):
    top = [(a, b, c) for (a, b), c in sugg[t].most_common(4) if c >= max(2, 0.15 * n)]
    print(f'{t} ({n}):', '; '.join(f'{a}→{b} ×{c}' for a, b, c in top) or '-')
