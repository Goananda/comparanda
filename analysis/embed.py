"""Two-dimensional UMAP embeddings of traditions and of motifs; NMF stability across random starts.

Usage: python3 embed.py <work_dir>   (run after clus.py and nmf.py)
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, umap
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD, NMF
from scipy.optimize import linear_sum_assignment
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
kg = np.load(f'{out}/keep_g.npy'); km = np.load(f'{out}/keep_m.npy'); Z = np.load(f'{out}/Z.npy')
lab = pd.read_csv(f'{out}/ward_labels.csv')
Xk = X[kg][:, km]; Gk = G[kg].reset_index(drop=True); Mk = M[km].reset_index(drop=True)
# cultures UMAP
for nn, md in [(15, 0.3), (25, 0.4)]:
    E = umap.UMAP(n_neighbors=nn, min_dist=md, metric='cosine', random_state=42).fit_transform(Z)
    np.save(f'{out}/umap_g_{nn}.npy', E)
# motif embedding
df = Xk.sum(0); idf = np.log(Xk.shape[0]/df); W = normalize(Xk*idf)
svd = TruncatedSVD(30, algorithm='arpack', random_state=0).fit(W)
Vm = normalize((svd.components_.T * svd.singular_values_))
Em = umap.UMAP(n_neighbors=20, min_dist=0.25, metric='cosine', random_state=42).fit_transform(Vm)
np.save(f'{out}/umap_m.npy', Em)
# home region of motif at k=6 level via lift
l6 = lab['k6'].values; regs = sorted(set(l6))
P = np.array([Xk[l6 == r].mean(0) for r in regs]).T
letters = Mk.letter.values; isA = np.isin(letters, list('abcdefghi'))
base = np.zeros_like(P)
for sel in [isA, ~isA]: base[sel] = P[sel].mean(0)
lift = P/base; share = lift/lift.sum(1, keepdims=True)
home = share.argmax(1); top = share.max(1)
print('home share quantiles', np.round(np.quantile(top, [.1,.25,.5,.75,.9]), 2))
for r_i, r in enumerate(regs):
    sub = Gk[l6 == r]; print(r, len(sub), sub.sort_values('n_motifs', ascending=False).group.head(3).tolist(), 'motifs with home here:', (home == r_i).sum(), ' strong(>0.5):', ((home == r_i) & (top > .5)).sum())
np.save(f'{out}/motif_share6.npy', share)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(27, 9))
for ax, nn in zip(axs[:2], [15, 25]):
    E = np.load(f'{out}/umap_g_{nn}.npy'); ax.scatter(E[:,0], E[:,1], c=lab['k12'], cmap='tab20', s=14); ax.set_title(f'cultures umap nn={nn}')
c = np.where(top > .45, home, -1)
axs[2].scatter(Em[:,0], Em[:,1], c=c, cmap='tab10', s=8); axs[2].set_title('motifs umap (home region k=6, -1 = widespread)')
plt.tight_layout(); plt.savefig(f'{out}/q_umap.png', dpi=50); plt.close()
# NMF stability at k=12
Hs = []
for seed in range(6):
    m = NMF(12, init='random', random_state=seed, max_iter=600, tol=1e-5); m.fit(W); Hs.append(normalize(m.components_))
ref = normalize(np.load(f'{out}/nmf_H_12.npy'))
for i, H in enumerate(Hs):
    C = ref @ H.T; r, c = linear_sum_assignment(-C); print(f'seed {i}: matched cosine per comp', np.round(C[r, c], 2), 'mean', C[r, c].mean().round(2))
