"""Non-negative matrix factorisation of the TF-IDF matrix into motif complexes.

Usage: python3 nmf.py <work_dir> <k> [<k> ...]   (the page uses k = 12)
Keeps the best of six initialisations and saves nmf_W_<k>.npy and nmf_H_<k>.npy.
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
out = sys.argv[1]; ks = [int(a) for a in sys.argv[2:]]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
kg = X.sum(1) >= 15; km = X[kg].sum(0) >= 5
Xs = X[kg][:, km]; Gs = G[kg].reset_index(drop=True); Ms = M[km].reset_index(drop=True)
df = Xs.sum(0); idf = np.log(Xs.shape[0]/df)
W0 = normalize(Xs*idf)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for k in ks:
    best = None
    for seed in range(6):
        m = NMF(k, init='nndsvda' if seed == 0 else 'random', random_state=seed, max_iter=600, tol=1e-5)
        Wt = m.fit_transform(W0)
        if best is None or m.reconstruction_err_ < best[0]: best = (m.reconstruction_err_, Wt, m.components_, seed)
    err, Wt, H, seed = best
    print(f'===== k={k} err={err:.3f} (seed {seed}); rel err {err/np.linalg.norm(W0):.3f}')
    fig, axs = plt.subplots((k+2)//3, 3, figsize=(24, 4.2*((k+2)//3)))
    order = np.argsort(-Wt.sum(0))
    for j, (ax, ci) in enumerate(zip(axs.ravel(), order)):
        w = Wt[:, ci]; h = H[ci]
        top = np.argsort(-h)[:12]
        # specificity: weight share of this component for each motif
        spec = h / (H.sum(0) + 1e-12)
        tops = np.argsort(-(h*spec))[:10]
        cl = np.average(Gs.latitude, weights=w), np.average(Gs.longitude, weights=w)
        topg = np.argsort(-w)[:8]
        print(f'-- comp {j} (id {ci}) mass {w.sum():.1f}; top traditions: ' + ', '.join(Gs.group[t] for t in topg))
        print('   motifs: ' + '; '.join(f"{Ms.motif_id[t]} {Ms.title[t]} ({int(df[t])})" for t in tops))
        ax.scatter(Gs.longitude, Gs.latitude, c='#ddd', s=6)
        s = w/np.percentile(w, 99)
        ax.scatter(Gs.longitude, Gs.latitude, c=np.clip(s,0,1), cmap='YlOrRd', s=18*np.clip(s,0.05,1)+2, vmin=0, vmax=1)
        ax.set_title(f'comp {j}'); ax.set_xlim(-180,180); ax.set_ylim(-60,80)
    plt.tight_layout(); plt.savefig(f'{out}/q_nmf_{k}.png', dpi=50); plt.close()
    np.save(f'{out}/nmf_W_{k}.npy', Wt); np.save(f'{out}/nmf_H_{k}.npy', H)
