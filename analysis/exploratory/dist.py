"""Exploratory: similarity against great-circle distance; saves similarity matrices S_all, S_A, S_B used by aff.py and anc.py.
Usage: python3 dist.py <work_dir>
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.preprocessing import normalize
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
letters = M.letter.values
A = np.isin(letters, list('abcdefghi')); B = ~A
lat = np.radians(G.latitude.values); lon = np.radians(G.longitude.values)
s = np.sin(lat)[:,None]*np.sin(lat)[None,:] + np.cos(lat)[:,None]*np.cos(lat)[None,:]*np.cos(lon[:,None]-lon[None,:])
D = 6371*np.arccos(np.clip(s,-1,1))
def cosmat(ms, min_m=10):
    kg = X[:, ms].sum(1) >= min_m
    Xs = X[kg][:, ms]; df = Xs.sum(0); ok = df >= 3
    Xs = Xs[:, ok]; idf = np.log(Xs.shape[0]/df[ok])
    W = normalize(Xs*idf); return kg, W @ W.T
bins = [0,250,500,1000,1500,2000,3000,4000,5000,6000,8000,10000,12000,14000,16000,20100]
for name, ms in [('all', A|B), ('A', A), ('B', B)]:
    kg, S = cosmat(ms)
    Dk = D[kg][:, kg]; iu = np.triu_indices(kg.sum(), 1)
    d = Dk[iu]; sv = S[iu]
    print(f'== {name}: n={kg.sum()} pairs={len(d)}, spearman(sim, dist)={pd.Series(sv).corr(pd.Series(d), method="spearman"):.3f}, pearson(sim, log d)={np.corrcoef(sv, np.log(d+50))[0,1]:.3f}')
    b = np.digitize(d, bins) - 1
    print('   bin_km: mean sim (n)'); print('   ' + ' | '.join(f'{bins[i]}-{bins[i+1]}: {sv[b==i].mean():.3f} ({(b==i).sum()})' for i in range(len(bins)-1)))
    # nearest-neighbour stats: for each tradition, distance to its most similar tradition
    S2 = S.copy(); np.fill_diagonal(S2, -1)
    top = np.argsort(-S2, 1)[:, :5]
    dd = np.take_along_axis(Dk, top, 1)
    print(f'   distance to most similar tradition: median {np.median(dd[:,0]):.0f} km; share of top-5 most similar within 2000 km: {(dd<2000).mean():.2f}; random pair within 2000km: {(d<2000).mean():.3f}')
    np.save(f'{out}/S_{name}.npy', S); np.save(f'{out}/kg_{name}.npy', kg)
