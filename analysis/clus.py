"""Cluster traditions by motif repertoire: TF-IDF, 30 latent dimensions (LSA), Ward linkage.

Usage: python3 clus.py <work_dir>
Uses traditions with >= 15 motifs and motifs recorded in >= 5 of them. Prints geographic coherence, agreement with k-means and average linkage, and bootstrap stability.
"""
import sys, json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score as ARI
from scipy.cluster.hierarchy import linkage, fcluster
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
MIN_M, MIN_DF = 15, 5
keep_g = X.sum(1) >= MIN_M
keep_m = X[keep_g].sum(0) >= MIN_DF
print('traditions kept', keep_g.sum(), 'motifs kept', keep_m.sum())
Xk = X[keep_g][:, keep_m]
N = Xk.shape[0]
def lsa(Xb, k=30, seed=0):
    df = Xb.sum(0); idf = np.log(Xb.shape[0] / np.maximum(df,1))
    W = normalize(Xb * idf)
    svd = TruncatedSVD(k, random_state=seed, n_iter=10)
    Z = svd.fit_transform(W)
    return W, normalize(Z), svd
W, Z, svd = lsa(Xk)
print('explained var first 10:', np.round(svd.explained_variance_ratio_[:10],3), 'sum30', svd.explained_variance_ratio_.sum().round(3))
rs = Xk.sum(1)
print('corr of richness (log) with first 5 LSA dims (after norm):', [round(np.corrcoef(np.log(rs), Z[:,i])[0,1],2) for i in range(5)])
# geographic helpers
lat = np.radians(G.latitude.values[keep_g]); lon = np.radians(G.longitude.values[keep_g])
def gc(lat, lon):
    s = np.sin(lat)[:,None]*np.sin(lat)[None,:] + np.cos(lat)[:,None]*np.cos(lat)[None,:]*np.cos(lon[:,None]-lon[None,:])
    return 6371*np.arccos(np.clip(s,-1,1))
D = gc(lat, lon)
np.save(f'{out}/D.npy', D)
# Ward hierarchy on LSA coords
L = linkage(Z, 'ward')
lab = {k: fcluster(L, k, 'maxclust') for k in range(2, 16)}
# geographic coherence: share of 10 geographic nearest neighbours in the same cluster vs chance
nn = np.argsort(D, 1)[:, 1:11]
for k in range(2, 16):
    l = lab[k]; same = (l[nn] == l[:,None]).mean()
    p = np.bincount(l)[1:]/N; chance = (p**2).sum()
    print(f'k={k:2d} sizes={sorted(np.bincount(l)[1:].tolist(), reverse=True)} geo-same={same:.2f} chance={chance:.2f}')
# compare with kmeans and average linkage (cosine)
for k in [4,6,8,10,12]:
    km = KMeans(k, n_init=20, random_state=0).fit_predict(Z)
    av = AgglomerativeClustering(k, metric='cosine', linkage='average').fit_predict(Z)
    print(f'k={k}: ARI ward~kmeans {ARI(lab[k], km):.2f}, ward~avg {ARI(lab[k], av):.2f}')
# bootstrap over motifs
rng = np.random.default_rng(1)
res = {k: [] for k in range(2, 13)}
for b in range(30):
    idx = rng.integers(0, Xk.shape[1], Xk.shape[1])
    Xb = Xk[:, idx]
    ok = Xb.sum(0) > 0
    _, Zb, _ = lsa(Xb[:, ok], seed=b)
    Lb = linkage(Zb, 'ward')
    for k in res: res[k].append(ARI(lab[k], fcluster(Lb, k, 'maxclust')))
print('bootstrap ARI (motif resampling):', {k: round(float(np.mean(v)),2) for k,v in res.items()})
np.save(f'{out}/Z.npy', Z); np.save(f'{out}/keep_g.npy', keep_g); np.save(f'{out}/keep_m.npy', keep_m); np.save(f'{out}/ward.npy', L)
pd.DataFrame({f'k{k}': lab[k] for k in lab}).to_csv(f'{out}/ward_labels.csv', index=False)
# quick look plots
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
Gk = G[keep_g].reset_index(drop=True)
fig, axs = plt.subplots(4, 2, figsize=(18, 20))
for ax, k in zip(axs.ravel(), [2,3,4,5,6,8,10,12]):
    ax.scatter(Gk.longitude, Gk.latitude, c=lab[k], cmap='tab20', s=14); ax.set_title(f'Ward k={k}'); ax.set_xlim(-180,180); ax.set_ylim(-60,80)
plt.tight_layout(); plt.savefig(f'{out}/q_ward.png', dpi=60)
