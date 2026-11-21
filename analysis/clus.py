"""Cluster traditions by motif repertoire: TF-IDF, 30 latent dimensions (LSA), Ward linkage, consensus over resampled motifs.

Usage: python3 clus.py <work_dir> [n_resamples=1200]   (about 8 minutes)
Uses traditions with >= 15 motifs and motifs recorded in >= 5 of them. Prints the reproducibility of the consensus tree,
geographic coherence and agreement with k-means and average linkage.
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
    # exact decomposition (ARPACK): the randomised solver made the tree depend on its random seed
    svd = TruncatedSVD(k, algorithm='arpack', random_state=seed)
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
# One Ward tree on all motifs. It is kept for comparison only: such a tree changes noticeably when the sample of motifs
# changes (see the figures printed below), so the page is built on a consensus of many trees.
L1 = linkage(Z, 'ward')
lab1 = {k: fcluster(L1, k, 'maxclust') for k in range(2, 16)}
# Consensus tree. Motifs are drawn with replacement B times; every resample goes through the same steps (TF-IDF, LSA,
# Ward) and its tree is cut at the levels CUTS. The co-association of two traditions is the share of resamples and cuts
# in which they fall into one cluster. The final hierarchy is a Ward tree on the rows of the co-association matrix.
# The resamples are split into two independent halves to show how reproducible the result is.
B = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
CUTS = list(range(2, 13)) + [14, 16, 20, 24, 30, 40, 60, 90, 130]
def coassoc(seed, n):
    rng = np.random.default_rng(seed); C = np.zeros((N, N)); single = {k: [] for k in range(2, 13)}
    for b in range(n):
        idx = rng.integers(0, Xk.shape[1], Xk.shape[1])
        Xb = Xk[:, idx]; Xb = Xb[:, Xb.sum(0) > 0]
        Lb = linkage(lsa(Xb)[1], 'ward')
        for k in CUTS:
            l = fcluster(Lb, k, 'maxclust'); C += l[:, None] == l[None, :]
            if k in single: single[k].append(ARI(lab1[k], l))
    return C / (n * len(CUTS)), single
Ca, sa = coassoc(1, B // 2); Cb, sb = coassoc(2, B // 2)
La, Lb2 = linkage(Ca, 'ward'), linkage(Cb, 'ward')
C = (Ca + Cb) / 2
L = linkage(C, 'ward')
lab = {k: fcluster(L, k, 'maxclust') for k in range(2, 16)}
halves = {k: round(float(ARI(fcluster(La, k, 'maxclust'), fcluster(Lb2, k, 'maxclust'))), 2) for k in range(2, 13)}
single = {k: round(float(np.mean(sa[k] + sb[k])), 2) for k in range(2, 13)}
print(f'consensus of {B} resamples; ARI between the trees of two independent halves:', halves)
print('ARI of a single resampled tree with the single tree on all motifs:', single)
print('ARI of the consensus with the single tree on all motifs:', {k: round(float(ARI(lab[k], lab1[k])), 2) for k in range(2, 13)})
json.dump({'n': B, 'halves': halves, 'single': single}, open(f'{out}/boot.json', 'w'))   # read by export.py
# geographic coherence: share of 10 geographic nearest neighbours in the same cluster vs chance
nn = np.argsort(D, 1)[:, 1:11]
for k in range(2, 16):
    l = lab[k]; same = (l[nn] == l[:,None]).mean()
    p = np.bincount(l)[1:]/N; chance = (p**2).sum()
    print(f'k={k:2d} sizes={sorted(np.bincount(l)[1:].tolist(), reverse=True)} geo-same={same:.2f} chance={chance:.2f}')
# compare with kmeans and average linkage (cosine) on the LSA coordinates
for k in [4,6,8,10,12]:
    km = KMeans(k, n_init=20, random_state=0).fit_predict(Z)
    av = AgglomerativeClustering(k, metric='cosine', linkage='average').fit_predict(Z)
    print(f'k={k}: ARI consensus~kmeans {ARI(lab[k], km):.2f}, consensus~avg {ARI(lab[k], av):.2f}')
np.save(f'{out}/coassoc.npy', C.astype(np.float32)); np.save(f'{out}/ward_single.npy', L1)
np.save(f'{out}/Z.npy', Z); np.save(f'{out}/keep_g.npy', keep_g); np.save(f'{out}/keep_m.npy', keep_m); np.save(f'{out}/ward.npy', L)
pd.DataFrame({f'k{k}': lab[k] for k in lab}).to_csv(f'{out}/ward_labels.csv', index=False)
# quick look plots
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
Gk = G[keep_g].reset_index(drop=True)
fig, axs = plt.subplots(4, 2, figsize=(18, 20))
for ax, k in zip(axs.ravel(), [2,3,4,5,6,8,10,12]):
    ax.scatter(Gk.longitude, Gk.latitude, c=lab[k], cmap='tab20', s=14); ax.set_title(f'consensus k={k}'); ax.set_xlim(-180,180); ax.set_ylim(-60,80)
plt.tight_layout(); plt.savefig(f'{out}/q_ward.png', dpi=60)
