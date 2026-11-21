"""Does each old tradition resemble, by content, the new tradition that carries its name?
usage: python3 -I content_match.py <pairs.csv> <old_groups_motifs.csv> <traditions.csv>"""
import sys, csv, collections
csv.field_size_limit(10**9)
f_pairs, f_old, f_trad = sys.argv[1:4]
old = collections.defaultdict(set)
for r in csv.DictReader(open(f_old, encoding='utf-8-sig')): old[r['group']].add(r['motif_id'].lower())
new = collections.defaultdict(set)
for r in csv.DictReader(open(f_pairs, encoding='utf-8-sig')): new[r['tradition']].add(r['motif_id'])
area = {r['tradition']: r['areas'] for r in csv.DictReader(open(f_trad, encoding='utf-8-sig'))}
common = set().union(*old.values()) & set().union(*new.values())
old = {t: s & common for t, s in old.items()}; newc = {t: s & common for t, s in new.items()}
inv = collections.defaultdict(set)
for t, s in newc.items():
    for m in s: inv[m].add(t)
def jac(a, b): return len(a & b) / len(a | b) if a | b else 0
rows = []
for t, s in old.items():
    if len(s) < 12: continue
    cand = collections.Counter()
    for m in s:
        for u in inv[m]: cand[u] += 1
    best = max(cand, key=lambda u: jac(s, newc[u])) if cand else None
    own = [u for u in newc if t in u.split(' + ')]
    js = jac(s, newc[own[0]]) if own else 0
    jb = jac(s, newc[best]) if best else 0
    if best and best not in own and jb > js + 0.05:
        rows.append((jb - js, t, len(s), js, best, len(newc[best]), jb, area.get(own[0] if own else t, '?'), area.get(best, '?')))
print(len(rows), 'old traditions resemble another new tradition more than their namesake:')
for r in sorted(rows, reverse=True):
    print(f'{r[1]:40s} n={r[2]:4d} J(namesake)={r[3]:.2f} | best: {r[4]:40s} n={r[5]:4d} J={r[6]:.2f} | {r[7]} / {r[8]}')
