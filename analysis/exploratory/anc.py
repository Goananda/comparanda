"""Exploratory: share of cosmological motifs by cluster and nearest relatives of selected traditions (run dist.py first).
Usage: python3 anc.py <work_dir>
"""
import sys, numpy as np, pandas as pd
out = sys.argv[1]
X = np.load(f'{out}/X.npy'); G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
isA = np.isin(M.letter.values, list('abcdefghi'))
G['shareA'] = X[:, isA].sum(1)/X.sum(1)
kg = np.load(f'{out}/keep_g.npy'); lab = pd.read_csv(f'{out}/ward_labels.csv'); c12 = np.full(len(G), -1); c12[kg] = lab['k12']
G['c12'] = c12
print('share of cosmological (A-I) motifs by cluster (median):'); print(G[G.c12 > 0].groupby('c12').shareA.median().round(2).to_dict())
S = np.load(f'{out}/S_all.npy'); k = np.load(f'{out}/kg_all.npy'); idx = np.where(k)[0]; pos = {g: i for i, g in enumerate(idx)}
for name in ['Ancient Greece', 'Sumer', 'Old Testament', 'Ancient Egypt', 'Yamana', 'Bushmen', 'Chukchi', 'Yanomamo', 'Maori,Moriori', 'Russians', 'Hausa', 'Japan', 'Trans New Guinea East', 'Tlingit']:
    gi = G.index[G.group == name][0]; i = pos[gi]; o = np.argsort(-S[i])[1:9]
    print(f'{name} (n={G.n_motifs[gi]}, shareA={G.shareA[gi]:.2f}, c12={G.c12[gi]}):', '; '.join(f'{G.group[idx[j]]} {S[i,j]:.2f}' for j in o))
