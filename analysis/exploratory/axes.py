"""Exploratory: principal axes by PCA and by correspondence analysis for all, A-I and J-N motifs, with quick-look maps.
Usage: python3 axes.py <work_dir>
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.preprocessing import normalize
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
letters = M.letter.values
sets = {'all': np.ones(len(M), bool), 'A': np.isin(letters, list('abcdefghi')), 'B': np.isin(letters, list('jklmn'))}
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def pca_tfidf(Xs):
    df = Xs.sum(0); idf = np.log(Xs.shape[0]/df)
    W = normalize(Xs*idf); Wc = W - W.mean(0)
    U, S, Vt = np.linalg.svd(Wc, full_matrices=False)
    return U*S, S**2/np.sum(S**2), Vt
def ca(Xs):
    P = Xs/Xs.sum(); r = P.sum(1); c = P.sum(0)
    R = (P - np.outer(r,c))/np.sqrt(np.outer(r,c))
    U, S, Vt = np.linalg.svd(R, full_matrices=False)
    return (U*S)/np.sqrt(r)[:,None], S**2/np.sum(S**2), Vt/np.sqrt(c)[None,:]
for name, ms in sets.items():
    for MIN_M, MIN_DF in [(15, 10)]:
        kg = X[:, ms].sum(1) >= MIN_M
        km = ms & (X[kg].sum(0) >= MIN_DF)
        Xs = X[kg][:, km]; Gs = G[kg].reset_index(drop=True); Ms = M[km].reset_index(drop=True)
        rs = np.log(Xs.sum(1))
        for meth, f in [('pca', pca_tfidf), ('ca', ca)]:
            sc, ev, V = f(Xs)
            print(f'== {name} {meth}: n={Xs.shape}, var {np.round(ev[:6],3)}, corr with log-richness {[round(float(np.corrcoef(rs, sc[:,i])[0,1]),2) for i in range(5)]}')
            fig, axs = plt.subplots(2, 2, figsize=(18, 10))
            for i, ax in enumerate(axs.ravel()):
                v = sc[:, i]; lim = np.percentile(np.abs(v), 97)
                ax.scatter(Gs.longitude, Gs.latitude, c=v, cmap='RdBu_r', vmin=-lim, vmax=lim, s=16, edgecolors='k', linewidths=.2)
                ax.set_title(f'{name} {meth} axis {i+1} ({ev[i]*100:.1f}%)'); ax.set_xlim(-180,180); ax.set_ylim(-60,80)
                top = np.argsort(V[i]); 
                if meth == 'pca':
                    print(f'  axis {i+1} (+):', '; '.join(f"{Ms.motif_id[j]} {Ms.title[j]}" for j in top[::-1][:8]))
                    print(f'  axis {i+1} (-):', '; '.join(f"{Ms.motif_id[j]} {Ms.title[j]}" for j in top[:8]))
            plt.tight_layout(); plt.savefig(f'{out}/q_axes_{name}_{meth}.png', dpi=55); plt.close()
