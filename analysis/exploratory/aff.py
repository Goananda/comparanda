"""Exploratory: mean similarity between the 12 clusters, separately for A-I and J-N motifs (run dist.py first).
Usage: python3 aff.py <work_dir>
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
out = sys.argv[1]
G = pd.read_csv(f'{out}/groups.csv')
kg = np.load(f'{out}/keep_g.npy'); lab = pd.read_csv(f'{out}/ward_labels.csv')
full = np.full(len(G), -1); full[kg] = lab['k12'].values
names = {}
Gk = G.copy(); Gk['c'] = full
for c in sorted(set(full) - {-1}):
    sub = Gk[Gk.c == c]; names[c] = f"{c}:{sub.sort_values('n_motifs', ascending=False).group.iloc[0][:14]}({len(sub)})"
pd.set_option('display.width', 250)
for name in ['A', 'B']:
    S = np.load(f'{out}/S_{name}.npy'); k = np.load(f'{out}/kg_{name}.npy')
    cl = full[k]
    cs = sorted(set(cl) - {-1})
    Mx = np.zeros((len(cs), len(cs)))
    for i, a in enumerate(cs):
        for j, b in enumerate(cs):
            blk = S[np.ix_(cl == a, cl == b)]
            if a == b:
                n = blk.shape[0]; Mx[i, j] = (blk.sum() - np.trace(blk)) / (n*(n-1))
            else: Mx[i, j] = blk.mean()
    print(f'== {name}: mean cosine x100 between k=12 clusters')
    print(pd.DataFrame(np.round(Mx*100, 1), index=[names[c] for c in cs], columns=[str(c) for c in cs]).to_string())
