import sys, json, numpy as np, pandas as pd, csv
from scipy.cluster.hierarchy import fcluster
out, trad = sys.argv[1], sys.argv[2]
X = np.load(f'{out}/X.npy'); G = pd.read_csv(f'{out}/groups.csv')
kg = np.load(f'{out}/keep_g.npy'); L = np.load(f'{out}/ward.npy')
Gk = G[kg].reset_index(drop=True); n = len(Gk)
st = {r['tradition'].replace(' + ', ', '): r for r in csv.DictReader(open(trad, encoding='utf-8-sig'))}
D = json.load(open(f'{out}/data.json'))
lab = fcluster(L, 8, 'maxclust')
anchors = {'Germans': 'WEur', 'Kongo': 'Afr', 'Viets': 'SEAs', 'Samoa': 'Oce', 'Chukchi': 'Sib', 'Plains Cree': 'NAm', 'Tzotzil': 'Meso', 'Yanomamo': 'SAm'}
pos = {g: i for i, g in enumerate(Gk.group)}
nm = {lab[pos[a]]: s for a, s in anchors.items()}; assert len(nm) == 8, nm
lon = np.radians(Gk.longitude.values); lat = np.radians(Gk.latitude.values)
d = np.arccos(np.clip(np.sin(lat)[:, None] * np.sin(lat)[None] + np.cos(lat)[:, None] * np.cos(lat)[None] * np.cos(lon[:, None] - lon[None]), -1, 1)) * 6371
rows = []
for i in range(n):
    o = np.argsort(d[i])[1:9]; c = pd.Series(lab[o]).value_counts()
    same = d[i][(lab == lab[i]) & (np.arange(n) != i)].min()
    if c.index[0] != lab[i] and (lab[o] == lab[i]).sum() <= 1:
        s = st.get(Gk.group[i], {})
        rows.append((same, Gk.group[i], nm[lab[i]], nm[c.index[0]], int(Gk.n_motifs[i]), round(Gk.longitude[i], 1), round(Gk.latitude[i], 1), s.get('status', '?'), s.get('n_motifs_old', '?')))
print(len(rows), 'traditions whose cluster differs from that of their neighbours (km to the nearest member of own cluster):')
for r in sorted(rows, reverse=True): print(f'{r[0]:7.0f} km  {r[1]:42s} {r[2]:5s} among {r[3]:5s} n={r[4]:4d} ({r[7]}, old n={r[8]})  lon {r[5]} lat {r[6]}')
