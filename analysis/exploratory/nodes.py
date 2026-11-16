"""Exploratory: print the core and edge members of every node in the Ward hierarchy.
Usage: python3 nodes.py <work_dir>
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
kg = np.load(f'{out}/keep_g.npy'); Z = np.load(f'{out}/Z.npy')
lab = pd.read_csv(f'{out}/ward_labels.csv')
Gk = G[kg].reset_index(drop=True); Xk = X[kg]
# build node list: track splits from k to k+1
nodes = {}  # frozenset(member idx) -> info
def members(k): 
    l = lab[f'k{k}'].values
    return [frozenset(np.where(l == c)[0]) for c in np.unique(l)]
prev = [frozenset(range(len(Gk)))]
for k in range(2, 13):
    cur = members(k)
    new = [c for c in cur if c not in prev]
    parent = [p for p in prev if p not in cur][0]
    print(f'\n### k={k}: split of node n={len(parent)} into {[len(c) for c in new]}')
    for c in new:
        idx = np.array(sorted(c)); cen = Z[idx].mean(0); cen /= np.linalg.norm(cen)
        order = idx[np.argsort(-(Z[idx] @ cen))]
        lat, lon = Gk.latitude[idx], Gk.longitude[idx]
        print(f'  node n={len(idx)} lat[{lat.quantile(.1):.0f},{lat.quantile(.9):.0f}] lon[{lon.quantile(.1):.0f},{lon.quantile(.9):.0f}] median motifs {np.median(Xk[idx].sum(1)):.0f}')
        print('    core: ' + '; '.join(Gk.group[order[:14]]))
        print('    edge: ' + '; '.join(Gk.group[order[-8:]]))
    prev = cur
