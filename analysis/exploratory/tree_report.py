"""Describe the Ward tree: which cluster splits at each step and what the parts consist of (by catalogue area).
usage: python3 -I tree_report.py <work_dir> <traditions.csv>"""
import sys, csv, collections, numpy as np, pandas as pd
from scipy.cluster.hierarchy import fcluster
out, f_trad = sys.argv[1:3]
G = pd.read_csv(f'{out}/groups.csv'); kg = np.load(f'{out}/keep_g.npy'); L = np.load(f'{out}/ward.npy')
Gk = G[kg].reset_index(drop=True)
area = {r['tradition'].replace(' + ', ', '): r['areas'].split('; ')[0] for r in csv.DictReader(open(f_trad, encoding='utf-8-sig'))}
ar = np.array([area.get(g, '?') for g in Gk.group])
prev = {1: [set(range(len(Gk)))]}
def desc(c):
    cnt = collections.Counter(ar[list(c)]); tot = collections.Counter(ar)
    return ', '.join(f'{a} {n}/{tot[a]}' for a, n in cnt.most_common(40))
cur = [frozenset(range(len(Gk)))]
for k in range(2, 13):
    l = fcluster(L, k, 'maxclust'); new = [frozenset(np.where(l == i)[0]) for i in sorted(set(l))]
    parts = [c for c in new if c not in cur]; parent = [c for c in cur if c not in new][0]
    print(f'--- k={k}: cluster of {len(parent)} splits into {len(parts[0])} + {len(parts[1])}')
    for p in parts: print(f'   [{len(p)}] {desc(p)[:1500]}')
    cur = new
print('sizes at 12:', sorted((len(c) for c in cur), reverse=True))
