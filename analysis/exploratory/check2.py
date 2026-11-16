"""Exploratory: which pairs of macro-regions fall into the 10-14 and 16-20 thousand km distance bins and how similar they are;
share of cosmological motifs in ancient written traditions. Usage: python3 check2.py <work_dir>   (run after export.py)
"""
import sys, json, numpy as np, pandas as pd
from sklearn.preprocessing import normalize
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float); G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
D = json.load(open(f'{out}/data.json'))
isA = np.isin(M.letter.values, list('abcdefghi'))
fam = np.full(len(G), -1); fam[D['kept']] = [D['nodes'][i]['hue'] for i in D['labels']['8']]
FAM = ['WE', 'AF', 'SA', 'OC', 'SI', 'NA', 'MA', 'SAm']
lat = np.radians(G.latitude.values); lon = np.radians(G.longitude.values)
s_ = np.sin(lat)[:, None]*np.sin(lat)[None, :] + np.cos(lat)[:, None]*np.cos(lat)[None, :]*np.cos(lon[:, None]-lon[None, :])
DD = 6371*np.arccos(np.clip(s_, -1, 1))
for name, ms in [('A', isA), ('B', ~isA)]:
    el = (X[:, ms].sum(1) >= 10) & (fam >= 0)
    Xs = X[el][:, ms]; df = Xs.sum(0); ok = df > 0; idf = np.zeros(Xs.shape[1]); idf[ok] = np.log(el.sum()/df[ok])
    W = normalize(Xs*idf); S = W @ W.T; Dk = DD[el][:, el]; f = fam[el]
    for lo, hi in [(10000, 14000), (16000, 20100)]:
        rows = []
        iu = np.triu_indices(el.sum(), 1); m = (Dk[iu] >= lo) & (Dk[iu] < hi)
        fa, fb = f[iu[0]][m], f[iu[1]][m]; sv = S[iu][m]
        key = np.minimum(fa, fb)*10 + np.maximum(fa, fb)
        t = pd.DataFrame({'key': key, 's': sv}).groupby('key').s.agg(['size', 'mean']).sort_values('size', ascending=False)
        t['pair'] = [FAM[k//10] + '-' + FAM[k % 10] for k in t.index]; t['share'] = t['size']/t['size'].sum()
        print(f'{name} {lo}-{hi}: overall {sv.mean():.4f}'); print(t.head(9)[['pair', 'share', 'mean']].round(3).to_string(index=False))
G['shareA'] = X[:, isA].sum(1)/X.sum(1)
anc = ['Ancient Greece', 'Ancient Italy', 'Ancient Egypt', 'Ugarit, Phoenicia', 'Old Testament', 'Hittite, Hurrit', 'Akkad,Assyria,Babylon', 'Sumer', 'Avesta; Pekhlevi texts', 'Ancient China', 'India, literary sources']
print(G[G.group.isin(anc)][['group', 'n_motifs', 'shareA']].round(2).to_string(index=False))
print('WE block shareA median', G.shareA[fam == 0].median().round(2), 'rest', G.shareA[(fam > 0)].median().round(2))
