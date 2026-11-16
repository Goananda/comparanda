"""Exploratory: print full membership of the 12 clusters and the traditions left out for having fewer than 15 motifs.
Usage: python3 members.py <work_dir>
"""
import sys, numpy as np, pandas as pd
out = sys.argv[1]
G = pd.read_csv(f'{out}/groups.csv'); kg = np.load(f'{out}/keep_g.npy'); lab = pd.read_csv(f'{out}/ward_labels.csv')
Gk = G[kg].reset_index(drop=True); Gk['c12'] = lab['k12']; Gk['c8'] = lab['k8']
pd.set_option('display.width', 300)
for c, sub in Gk.groupby('c12'):
    print(f'\n== c12={c} n={len(sub)} (c8={sub.c8.iloc[0]}) lon/lat median {sub.longitude.median():.0f},{sub.latitude.median():.0f}')
    print('; '.join(f"{r.group}[{r.longitude:.0f},{r.latitude:.0f}|{r.n_motifs}]" for r in sub.sort_values('longitude').itertuples()))
low = G[~kg]; print('\nexcluded (<15 motifs):', len(low)); print('; '.join(f"{r.group}[{r.n_motifs}]" for r in low.itertuples()))
