"""Exploratory: how stable is the place of selected groups of traditions in the tree when motifs are resampled?
Usage: python3 robust.py <work_dir> [n_resamples=60]
For each resample (motifs drawn with replacement) the LSA + Ward steps of clus.py are repeated and, for several cuts of
the tree, the script counts how often a group falls into one cluster with an anchor tradition of a neighbouring region.
"""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
from scipy.cluster.hierarchy import linkage, fcluster
out = sys.argv[1]; B = int(sys.argv[2]) if len(sys.argv) > 2 else 60
X = np.load(f'{out}/X.npy').astype(float); G = pd.read_csv(f'{out}/groups.csv')
kg = np.load(f'{out}/keep_g.npy'); km = np.load(f'{out}/keep_m.npy')
Xk = X[kg][:, km]; Gk = G[kg].reset_index(drop=True); pos = {g: i for i, g in enumerate(Gk.group)}
def lsa(Xb, k=30, seed=0):
    df = Xb.sum(0); idf = np.log(Xb.shape[0] / np.maximum(df, 1)); W = normalize(Xb * idf)
    return normalize(TruncatedSVD(k, algorithm='arpack', random_state=seed).fit_transform(W))
GROUPS = {
 'Australia': ['Arnham Land', 'Central Australia', 'Kimberley Plateau', 'Queensland', 'SE Australia', 'Southern Australia', 'Western Australia'],
 'Mongolia and South Siberia': ['Mongols (Khalkha)', 'Buryat', 'Tuvinians', 'Khakas', 'Altai-Kiji, Telengit', 'Oirat', 'Shor', 'Tofa'],
 'Siberia': ['Yakut', 'Western Evenki', 'Nganasan', 'Ket, Yug', 'Tundra Nenets', 'Hanty', 'Nivkh', 'Evens (Lamuts)'],
 'Chukotka and Kamchatka': ['Chukchi', 'Kerek', 'Maritime Koryak (Alyutor)', 'Reindeer Koryak', 'Kamchadal'],
 'South Asia (Indo-Aryan and Dravidian)': ['Hindi, Chhattisgarhi', 'Bengali', 'Marathi', 'Tamil', 'Punjabi', 'Sinhalese'],
 'Ancient written traditions': ['Sumer', 'Akkad,Assyria,Babylon', 'Ancient Egypt', 'Ancient Greece', 'Old Testament', 'Ugarit, Phoenicia'],
}
ANCH = {'S America': 'Yanomamo', 'Mainland SE Asia': 'Viets', 'Oceania': 'Samoa', 'Siberia': 'Yakut', 'N America': 'Plains Cree',
        'Arctic': 'Polar Eskimo', 'Europe': 'Germans', 'W Asia': 'Persians', 'Africa': 'Kongo', 'Island SE Asia': 'Bali, Lombok'}
GROUPS = {g: [t for t in ts if t in pos] for g, ts in GROUPS.items()}; ANCH = {a: t for a, t in ANCH.items() if t in pos}
rng = np.random.default_rng(7); res = []; first = []
for b in range(B):
    idx = rng.integers(0, Xk.shape[1], Xk.shape[1]); Xb = Xk[:, idx]; Xb = Xb[:, Xb.sum(0) > 0]
    L = linkage(lsa(Xb, seed=b), 'ward')
    for k in (3, 6, 8, 12):
        l = fcluster(L, k, 'maxclust')
        for g, ts in GROUPS.items():
            for a, t in ANCH.items():
                res.append((k, g, a, np.mean([l[pos[x]] == l[pos[t]] for x in ts if x != t])))
    l2 = fcluster(L, 2, 'maxclust'); s = lambda a, b_: l2[pos[ANCH[a]]] == l2[pos[ANCH[b_]]]
    first.append('west Eurasia apart' if s('Europe', 'W Asia') and not s('Europe', 'Oceania') and s('Oceania', 'S America') and s('Oceania', 'Africa')
                 else 'Americas and Siberia apart' if s('N America', 'S America') and s('N America', 'Siberia') and not s('N America', 'Europe') and s('Europe', 'Oceania')
                 else 'other')
R = pd.DataFrame(res, columns=['k', 'group', 'anchor', 'share']).groupby(['group', 'k', 'anchor']).share.mean().unstack().round(2)
pd.set_option('display.width', 250); print(R.to_string())
print('first split over', B, 'resamples:', pd.Series(first).value_counts().to_dict())
