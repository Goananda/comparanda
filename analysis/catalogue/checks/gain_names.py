"""Which names on the pages feed the pairs that a tradition gained relative to the old table?
usage: python3 -I gain_names.py <pairs.csv> <old_groups_motifs.csv> <tradition> [...]"""
import sys, csv, collections
csv.field_size_limit(10**9)
f_pairs, f_old = sys.argv[1:3]; targets = set(sys.argv[3:])
old = collections.defaultdict(set)
for r in csv.DictReader(open(f_old, encoding='utf-8-sig')): old[r['group']].add(r['motif_id'].lower())
oldm = set().union(*old.values())
add = collections.defaultdict(collections.Counter); kept = collections.defaultdict(collections.Counter); how = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(f_pairs, encoding='utf-8-sig')):
    t = r['tradition']
    if t not in targets: continue
    names = {n.lower() for n in r['names_on_page'].split('; ') if n}
    tgt = add if (r['motif_id'] in oldm and r['motif_id'] not in old[t]) else kept if r['motif_id'] in old[t] else None
    if tgt is None: continue
    for n in names: tgt[t][n] += 1
    if tgt is add: how[t][r['how'].split(':')[0].split(';')[0]] += 1
for t in targets:
    print(f'=== {t}: names behind added pairs on old motifs (and the same names behind confirmed pairs)')
    print('    ' + '; '.join(f'{n} {c} ({kept[t][n]})' for n, c in add[t].most_common(14)))
    print('    how:', dict(how[t].most_common(6)))
