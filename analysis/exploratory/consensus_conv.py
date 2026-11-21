"""Does the consensus tree converge as the number of resamples grows?  usage: python3 consensus_conv.py <work_dir> <n_blocks> <block>"""
import sys, time, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import adjusted_rand_score as ari
from scipy.cluster.hierarchy import linkage, fcluster
out = sys.argv[1]; NB = int(sys.argv[2]); BL = int(sys.argv[3])
X = np.load(f'{out}/X.npy').astype(float); kg = np.load(f'{out}/keep_g.npy'); km = np.load(f'{out}/keep_m.npy')
Xk = X[kg][:, km]; N = Xk.shape[0]
CUTS = list(range(2, 13)) + [14, 16, 20, 24, 30, 40, 60, 90, 130]
def lsa(Xb, k=30):
    df = Xb.sum(0); idf = np.log(Xb.shape[0] / np.maximum(df, 1)); W = normalize(Xb * idf)
    return normalize(TruncatedSVD(k, algorithm='arpack', random_state=0).fit_transform(W))
def block(seed):
    rng = np.random.default_rng(seed); C = np.zeros((N, N))
    for b in range(BL):
        idx = rng.integers(0, Xk.shape[1], Xk.shape[1]); Xb = Xk[:, idx]; Xb = Xb[:, Xb.sum(0) > 0]
        L = linkage(lsa(Xb), 'ward')
        for k in CUTS:
            l = fcluster(L, k, 'maxclust'); C += l[:, None] == l[None, :]
    return C / (BL * len(CUTS))
t = time.time(); Cs = [block(100 + i) for i in range(NB)]; print('time', round(time.time() - t), 's'); np.save(f'{out}/conv_blocks.npy', np.array(Cs, dtype=np.float32))
tot = linkage(np.mean(Cs, 0), 'ward')
def row(name, L1, L2): print(f'{name:34s}', ' '.join(f'{ari(fcluster(L1, k, "maxclust"), fcluster(L2, k, "maxclust")):.2f}' for k in range(2, 13)))
print('ARI at k=2..12')
for n in (1, 2, 4):
    if 2 * n <= NB:
        a = linkage(np.mean(Cs[:n], 0), 'ward'); b = linkage(np.mean(Cs[n:2 * n], 0), 'ward')
        row(f'two independent sets of {n * BL}', a, b); row(f'  first set of {n * BL} vs all {NB * BL}', a, tot)
print('sizes of all at k=3..6:', [sorted(np.bincount(fcluster(tot, k, 'maxclust'))[1:], reverse=True) for k in (3, 4, 5, 6)])
print('top merge heights:', np.round(tot[-12:, 2][::-1], 1))
