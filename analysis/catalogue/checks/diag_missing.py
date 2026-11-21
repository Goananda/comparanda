"""For a tradition with low recall: which names stand on the pages of its missing motifs (in its areas)?
usage: python3 -I diag_missing.py <entries_units.tsv> <pairs.csv> <traditions.csv> <old_groups_motifs.csv> <tradition> [...]"""
import sys, csv, collections
csv.field_size_limit(10**9)
f_ent, f_pairs, f_trad, f_old = sys.argv[1:5]; targets = sys.argv[5:]
old = collections.defaultdict(set)
for r in csv.DictReader(open(f_old, encoding='utf-8-sig')): old[r['group']].add(r['motif_id'].lower())
new = collections.defaultdict(set)
for r in csv.DictReader(open(f_pairs, encoding='utf-8-sig')):
    for o in r['tradition'].split(' + '): new[o].add(r['motif_id'])
T = {r['tradition']: r for r in csv.DictReader(open(f_trad, encoding='utf-8-sig'))}
ent = collections.defaultdict(list)
with open(f_ent, encoding='utf-8') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        if r['flag'] in ('', 'summary'): ent[r['motif_id']].append(r)
allm = set(ent)
for t in targets:
    areas = set(T[t]['areas'].split('; ')) if t in T else set()
    miss = (old[t] & allm) - new[t]; have = old[t] & new[t]
    print(f'=== {t}: old {len(old[t])}, found {len(have)}, missing {len(miss)}; areas {sorted(areas)}; units {T[t]["units"][:200] if t in T else "?"}')
    cm = collections.Counter(); ch = collections.Counter(); ex = {}
    for m in miss:
        seen = set()
        for r in ent[m]:
            if r['region_key'] in areas or not areas:
                k = (r['name'].lower(), r['qualifier'][:30], r['unit_id'][:50], r['method'])
                if k not in seen: seen.add(k); cm[k] += 1; ex.setdefault(k, m)
    for m in have:
        seen = set()
        for r in ent[m]:
            if r['region_key'] in areas or not areas:
                k = (r['name'].lower(), r['qualifier'][:30], r['unit_id'][:50], r['method'])
                if k not in seen: seen.add(k); ch[k] += 1
    for k, c in cm.most_common(14):
        print(f'   {c:3d} of missing ({100*c/max(1,len(miss)):3.0f}%), {ch[k]:3d} of found | {k[0]} ({k[1]}) -> {k[2]} [{k[3]}] e.g. {ex[k]}')
