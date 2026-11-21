"""Collect everything the page needs into data.json: cluster hierarchy with names and indicator motifs, NMF complexes,
principal axes (sections A-I and J-N separately), distance decay of similarity, motif atlas.

Usage: python3 export.py <work_dir>   (run after prep.py, clus.py, nmf.py, embed.py)
Cluster and component names were given by hand for the 2021 tables.  For a new version of the data every cluster and
component takes the name of the 2021 one it overlaps most (analysis/reference/); the log marks weak matches with CHECK.
"""
import sys, json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.preprocessing import normalize
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
kg = np.load(f'{out}/keep_g.npy'); km = np.load(f'{out}/keep_m.npy'); Z = np.load(f'{out}/Z.npy')
lab = pd.read_csv(f'{out}/ward_labels.csv')
kidx = np.where(kg)[0]; midx = np.where(km)[0]
Xk = X[kg]; Gk = G[kg].reset_index(drop=True); N = len(Gk)
letters = M.letter.values; isA = np.isin(letters, list('abcdefghi'))
D = {}
# ---------- basics
D['g'] = {'name': G.group.tolist(), 'lon': G.longitude.round(2).tolist(), 'lat': G.latitude.round(2).tolist(), 'n': G.n_motifs.astype(int).tolist()}
_ws = lambda s: ' '.join(str(s).split())
_col = lambda c: [_ws(x) for x in M[c]] if c in M else [''] * len(M)
# 'title', 'desc': the English version; 'tru', 'ru': the Russian version (see analysis/catalogue/scripts/motif_texts.py)
D['m'] = {'id': M.motif_id.tolist(), 'title': _col('title'), 'desc': _col('description'), 'tru': _col('title_ru'), 'ru': _col('description_ru')}
D['inc'] = [np.where(X[:, j] > 0)[0].tolist() for j in range(X.shape[1])]
D['kept'] = kidx.tolist()
# ---------- hierarchy nodes
# Hand-given names (by membership), keyed by (step at which the cluster appears, its size).
# Each entry: Russian name, English name, short Russian label, short English label, colour slot 0-11.
# A cluster keeps the colour of its larger child, so colours stay put while the slider moves.
NAMES = {
 (2,161): ('Евразия от Европы до Индии и Монголии, Магриб', 'Eurasia from Europe to India and Mongolia, Maghreb', 'Запад и центр Евразии', 'West & Central Eurasia', 1),
 (2,670): ('Остальной мир', 'Rest of the world', 'Остальной мир', 'Rest of the world', 3),
 (3,268): ('Африка, юг и восток Азии, Австралия, Океания', 'Africa, South and East Asia, Australia, Oceania', 'Африка, юг Азии, Океания', 'Africa, S Asia, Oceania', 3),
 (3,402): ('Америка, Сибирь и Арктика', 'Americas, Siberia and the Arctic', 'Америка и Сибирь', 'Americas & Siberia', 6),
 (4,174): ('Мезоамерика и Южная Америка', 'Mesoamerica and South America', 'Латинская Америка', 'Latin America', 11),
 (4,228): ('Северная Америка, Сибирь и Арктика', 'North America, Siberia and the Arctic', 'Северная Америка и Сибирь', 'N America & Siberia', 6),
 (5,101): ('Африка южнее Сахары', 'Sub-Saharan Africa', 'Африка', 'Africa', 2),
 (5,167): ('Юг и восток Азии, Австралия, Океания', 'South and East Asia, Australia, Oceania', 'Юг Азии и Океания', 'S Asia & Oceania', 3),
 (6,75): ('Сибирь, Берингия и Арктика', 'Siberia, Beringia and the Arctic', 'Сибирь и Арктика', 'Siberia & Arctic', 6),
 (6,153): ('Северная Америка южнее Субарктики', 'North America south of the Subarctic', 'Северная Америка', 'North America', 8),
 (7,34): ('Мезоамерика', 'Mesoamerica', 'Мезоамерика', 'Mesoamerica', 10),
 (7,140): ('Южная Америка', 'South America', 'Южная Америка', 'South America', 11),
 (8,43): ('Океания', 'Oceania', 'Океания', 'Oceania', 4),
 (8,124): ('Юг и восток Азии, Австралия', 'South and East Asia, Australia', 'Юг и восток Азии', 'S & E Asia', 3),
 (9,62): ('Равнины и восток Северной Америки', 'Plains and eastern North America', 'Равнины и восток', 'Plains & East', 9),
 (9,91): ('Запад Северной Америки', 'Western North America', 'Запад Северной Америки', 'Western N America', 8),
 (10,43): ('Европа', 'Europe', 'Европа', 'Europe', 0),
 (10,118): ('Магриб, Балканы, Кавказ, Центральная и Южная Азия', 'Maghreb, Balkans, Caucasus, Central and South Asia', 'От Магриба до Монголии', 'Maghreb to Mongolia', 1),
 (11,30): ('Сибирь и Приамурье', 'Siberia and the Amur region', 'Сибирь', 'Siberia', 5),
 (11,45): ('Берингия и Арктика: от Камчатки до Гренландии', 'Beringia and the Arctic, Kamchatka to Greenland', 'Берингия и Арктика', 'Beringia & Arctic', 6),
 (12,41): ('Северо-Западное побережье и Плато', 'Northwest Coast and Plateau', 'Северо-Запад', 'Northwest Coast', 7),
 (12,50): ('Калифорния, Большой Бассейн, Юго-Запад', 'California, Great Basin, Southwest', 'Калифорния и Юго-Запад', 'California & Southwest', 8)}
import os
REFDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reference')
_ref = pd.read_csv(os.path.join(REFDIR, 'cluster_membership_2021.csv'))
REF_SETS = {n: set(g.tradition) for n, g in _ref.groupby('cluster_name_en')}
BY_EN = {v[1]: v for v in NAMES.values()}
# Names of the clusters. Every cluster of the tree is a union of the twelve smallest ones, and each of those holds one of
# the anchor traditions below, so a cluster is recognised by the set of anchors it contains. Names that the 2021 tree
# already had are reused (BY_EN); the others were written by hand from the membership. A cluster with an unforeseen set of
# anchors (after a change in the data) falls back on the 2021 cluster it overlaps most and is flagged in the log.
ANCHORS = ['Germans', 'Persians', 'Hindi, Chhattisgarhi', 'Kongo', 'Viets', 'Samoa', 'Yakut', 'Polar Eskimo', 'Maidu', 'Plains Cree', 'Tzotzil', 'Yanomamo']
_E, _C, _I, _F, _V, _O, _S, _P, _W, _N, _M, _A = ANCHORS
NAMES_2025 = {
 (_E, _C, _I): BY_EN['Eurasia from Europe to India and Mongolia, Maghreb'],
 (_F, _V, _O, _S, _P, _W, _N, _M, _A): BY_EN['Rest of the world'],
 (_F, _V, _O): ('Африка южнее Сахары, юг и восток Азии, Океания', 'Sub-Saharan Africa, South and East Asia, Oceania', 'Африка, юг Азии, Океания', 'Africa, S Asia, Oceania', 3),
 (_S, _P, _W, _N, _M, _A): BY_EN['Americas, Siberia and the Arctic'],
 (_M, _A): BY_EN['Mesoamerica and South America'],
 (_S, _P, _W, _N): BY_EN['North America, Siberia and the Arctic'],
 (_F,): BY_EN['Sub-Saharan Africa'],
 (_V, _O): ('Юг и восток Азии, Океания', 'South and East Asia, Oceania', 'Юг Азии и Океания', 'S Asia & Oceania', 3),
 (_E,): BY_EN['Europe'],
 (_C, _I): ('Магриб, Кавказ, Передняя, Центральная и Южная Азия, Монголия', 'Maghreb, Caucasus, Western, Central and South Asia, Mongolia', 'От Магриба до Монголии', 'Maghreb to Mongolia', 1),
 (_W, _N): BY_EN['North America south of the Subarctic'],
 (_S, _P): ('Сибирь, Арктика, Субарктика, Северо-Западное побережье', 'Siberia, the Arctic, the Subarctic, Northwest Coast', 'Сибирь и Арктика', 'Siberia & Arctic', 6),
 (_A,): ('Амазония, Гвиана, Чако, восток Бразилии', 'Amazonia, the Guianas, Chaco, eastern Brazil', 'Амазония и Чако', 'Amazonia & Chaco', 11),
 (_M,): ('Мезоамерика, Анды, Австралия', 'Mesoamerica, the Andes, Australia', 'Мезоамерика, Анды, Австралия', 'Mesoamerica, Andes, Australia', 10),
 (_C,): ('Кавказ, Передняя и Средняя Азия, Магриб', 'Caucasus, Western and Central Asia, Maghreb', 'Кавказ и Передняя Азия', 'Caucasus & W Asia', 1),
 (_I,): ('Южная Азия, Монголия, Южная Сибирь, Африканский Рог', 'South Asia, Mongolia, South Siberia, Horn of Africa', 'Индия и Монголия', 'India & Mongolia', 7),
 (_S,): BY_EN['Siberia and the Amur region'],
 (_P,): ('Арктика, Субарктика, Северо-Западное побережье, Чукотка и Камчатка', 'Arctic, Subarctic, Northwest Coast, Chukotka and Kamchatka', 'Арктика и Субарктика', 'Arctic & Subarctic', 6),
 (_O,): BY_EN['Oceania'],
 (_V,): ('Южная, Восточная и Юго-Восточная Азия', 'South, East and Southeast Asia', 'Юг и восток Азии', 'S & E Asia', 3),
 (_N,): BY_EN['Plains and eastern North America'],
 (_W,): BY_EN['Western North America']}
AFAM = dict(zip(ANCHORS, [0, 0, 0, 1, 2, 3, 4, 4, 5, 5, 6, 7]))      # the eight macro-regions used to orient the axes
def sig(c):
    names = set(Gk.group[sorted(c)])
    return tuple(a for a in ANCHORS if a in names)
_used = {}
def name_for(k, c):
    names = set(Gk.group[sorted(c)]); sg = sig(c)
    if sg in NAMES_2025:
        v = NAMES_2025[sg]
        print(f'NODE k={k} n={len(c)} -> {v[1]}')
        return v
    en, j = max(((n, len(names & s) / len(names | s)) for n, s in REF_SETS.items()), key=lambda x: x[1])
    print(f'NODE k={k} n={len(c)} -> {en} (overlap {j:.2f}, anchors {sg})   <-- CHECK: no name for this set of anchors' + (' [name already used]' if en in _used else ''))
    _used[en] = (k, len(c))
    return BY_EN[en]
def members(k):
    l = lab[f'k{k}'].values
    return [frozenset(np.where(l == c)[0].tolist()) for c in np.unique(l)]
nodes = [{'id': 0, 'name': 'Все традиции', 'name_en': 'All traditions', 'short': 'Все', 'short_en': 'All', 'parent': -1, 'k': 1, 'mem': frozenset(range(N))}]
prev = [nodes[0]['mem']]; byset = {nodes[0]['mem']: 0}; splits = {}
for k in range(2, 13):
    cur = members(k); new = [c for c in cur if c not in prev]; parent = [p for p in prev if p not in cur][0]
    ids = []
    for c in sorted(new, key=len):
        nid = len(nodes); byset[c] = nid; ids.append(nid)
        ru, en, sru, sen, col = name_for(k, c)
        nodes.append({'id': nid, 'name': ru, 'name_en': en, 'short': sru, 'short_en': sen, 'col': col, 'parent': byset[parent], 'k': k, 'mem': c})
    splits[k] = {'parent': byset[parent], 'children': ids}
    prev = cur
# leaf order for legends: a geographic tour in the order of the anchors
leaves12 = members(12); leafrank = {}
def _leaf_rank(c):
    sg = sig(c)
    if len(sg) == 1:
        return ANCHORS.index(sg[0])
    print('LEAF with', len(sg), 'anchors:', nodes[byset[c]]['name_en'], '  <-- CHECK')
    return ANCHORS.index(sg[0]) + 0.5 if sg else len(ANCHORS)
for c in leaves12: leafrank[c] = _leaf_rank(c)
for nd in nodes: nd['rank'] = min(leafrank[c] for c in leaves12 if c <= nd['mem'])
# indicator motifs (IndVal-like vs rest of world), member cores
cen_all = None
for nd in nodes[1:]:
    idx = np.array(sorted(nd['mem'])); mask = np.zeros(N, bool); mask[idx] = True
    pin = Xk[mask].mean(0); pout = Xk[~mask].mean(0)
    score = np.where(Xk[mask].sum(0) >= 3, pin * pin / (pin + pout + 1e-12), 0)
    top = np.argsort(-score)[:8]
    nd['ind'] = [[int(j), round(float(pin[j]), 2), round(float(pout[j]), 2)] for j in top]
    cen = Z[idx].mean(0); cen /= np.linalg.norm(cen)
    nd['core'] = [int(kidx[i]) for i in idx[np.argsort(-(Z[idx] @ cen))][:6]]
    nd['n'] = len(idx)
    nd['shareA'] = round(float(np.median(Xk[mask][:, isA].sum(1) / Xk[mask].sum(1))), 2)
labels = {}
for k in range(2, 13):
    l = np.zeros(N, int)
    for c in members(k): l[list(c)] = byset[c]
    labels[k] = l.tolist()
D['nodes'] = [{kk: v for kk, v in nd.items() if kk != 'mem'} for nd in nodes]
D['labels'] = labels; D['splits'] = splits
E = np.load(f'{out}/umap_g_25.npy'); E = (E - E.min(0)) / (E.max(0) - E.min(0))
D['umapG'] = np.round(E, 4).tolist()
# geo coherence stats
Dm = np.load(f'{out}/D.npy'); nn = np.argsort(Dm, 1)[:, 1:11]
coh = {}
for k in range(2, 13):
    l = np.array(labels[k]); p = np.bincount(l) / N
    coh[k] = [round(float((l[nn] == l[:, None]).mean()), 3), round(float((p**2).sum()), 3)]
D['coh'] = coh
print('coherence', coh)
for nd in D['nodes'][1:]:
    print(nd['id'], nd['k'], nd['n'], nd['name_en'], '| colour', nd['col'], '| shareA', nd['shareA'], '|', '; '.join(f"{M.motif_id[j]} {M.title[j]} ({a}/{b})" for j, a, b in nd['ind'][:5]))
# ---------- NMF
Wn = np.load(f'{out}/nmf_W_12.npy'); H = np.load(f'{out}/nmf_H_12.npy')
NMF_NAMES = {'Uzbek': ('Передняя и Центральная Азия, Кавказ', 'Western and Central Asia, Caucasus'), 'Germans': ('Европа', 'Europe'),
             'Muslim Malay': ('Юго-Восточная Азия и Южный Китай', 'Southeast Asia and South China'), 'Tagish': ('Северо-Западное побережье и Субарктика', 'Northwest Coast and Subarctic'),
             'Wayampi, Emerillon': ('Амазония и Гвиана', 'Amazonia and the Guianas'), 'Totonac, Tepehua': ('Мезоамерика', 'Mesoamerica'),
             'Northern Paiute': ('Большой Бассейн, Калифорния, Плато', 'Great Basin, California, Plateau'), 'Ngonde,Safwa.Mkulwe,Kinga': ('Африка южнее Сахары', 'Sub-Saharan Africa'),
             'Western Evenki': ('Сибирь', 'Siberia'), 'Plains Cree': ('Равнины и Великие озёра', 'Plains and Great Lakes'),
             'Polar Eskimo': ('Эскимосская Арктика', 'Eskimo (Inuit and Yupik) Arctic'), 'Ulithi, Ngulu': ('Океания', 'Oceania')}
NMF_ORDER = ['Европа', 'Передняя и Центральная Азия, Кавказ', 'Африка южнее Сахары', 'Юго-Восточная Азия и Южный Китай', 'Океания', 'Сибирь', 'Эскимосская Арктика',
             'Северо-Западное побережье и Субарктика', 'Большой Бассейн, Калифорния, Плато', 'Равнины и Великие озёра', 'Мезоамерика', 'Амазония и Гвиана']
_t21 = pd.read_csv(os.path.join(REFDIR, 'traditions_2021.csv')).set_index('tradition')
_c21 = pd.read_csv(os.path.join(REFDIR, 'nmf_components_2021.csv'))
_cols = [f'nmf_{i:02d}' for i in range(1, 13)]
_common = [g for g in Gk.group if g in _t21.index and not np.isnan(_t21.loc[g, 'nmf_01'])]
_pos = [int(np.where(Gk.group.values == g)[0][0]) for g in _common]
_R = np.corrcoef(np.c_[Wn[_pos], _t21.loc[_common, _cols].values.astype(float)].T)[:12, 12:]
from scipy.optimize import linear_sum_assignment
_ri, _ci = linear_sum_assignment(-_R)
NMF_MATCH = {int(a): (_c21.name_ru[int(b)], _c21.name_en[int(b)], float(_R[a, b])) for a, b in zip(_ri, _ci)}
comps = []
for ci in range(12):
    w = Wn[:, ci]; h = H[ci]; spec = h / (H.sum(0) + 1e-12)
    topm = np.argsort(-(h * spec))[:8]; topg = np.argsort(-w)[:8]
    name, name_en, _r = NMF_MATCH[ci]
    print(f'NMFNAME {ci} -> {name_en} (r {_r:.2f})' + ('   <-- CHECK' if _r < 0.6 else '') + ' | top: ' + '; '.join(Gk.group[topg[:5]]))
    wq = np.clip(np.round(100 * w / np.percentile(w, 99)), 0, 100).astype(int)
    comps.append({'name': name, 'name_en': name_en, 'w': wq.tolist(), 'motifs': [int(midx[j]) for j in topm], 'trad': [int(kidx[j]) for j in topg], 'active': int((wq >= 15).sum())})
comps.sort(key=lambda c: NMF_ORDER.index(c['name']))
D['nmf'] = comps
for c in comps: print('NMF', c['name_en'], '| active', c['active'], '|', '; '.join(M.motif_id[j] + ' ' + M.title[j] for j in c['motifs'][:4]))
# ---------- axes
FAM = ['WE', 'AF', 'SA', 'OC', 'SI', 'NA', 'MA', 'SAm']
def _fam(i):
    sg = sig(nodes[i]['mem'])
    return AFAM[sg[0]] if sg else 0
fam8 = np.array([_fam(i) for i in labels[12]])            # macro-region of every tradition, from its smallest cluster
ANCH = {('A',0): 0, ('A',1): 1, ('A',2): 1, ('A',3): 5, ('B',0): 0, ('B',1): 1, ('B',2): 7, ('B',3): 5}
axes = {}
for name, ms in [('A', isA), ('B', ~isA)]:
    g_ok = X[:, ms].sum(1) >= 15
    m_ok = ms & (X[g_ok].sum(0) >= 10)
    Xs = X[g_ok][:, m_ok]; gi = np.where(g_ok)[0]; mi = np.where(m_ok)[0]
    df = Xs.sum(0); idf = np.log(Xs.shape[0] / df); W = normalize(Xs * idf); Wc = W - W.mean(0)
    U, S, Vt = np.linalg.svd(Wc, full_matrices=False); ev = S**2 / np.sum(S**2)
    famfull = np.full(len(G), -1); famfull[kidx] = fam8; fs = famfull[gi]
    lst = []
    for a in range(4):
        sc = U[:, a] * S[a]; v = Vt[a].copy()
        if sc[fs == ANCH[(name, a)]].mean() < 0: sc = -sc; v = -v
        lim = np.percentile(np.abs(sc), 97)
        q = np.clip(np.round(100 * sc / lim), -100, 100).astype(int)
        o = np.argsort(v); og = np.argsort(sc)
        fm = {FAM[f]: round(float(q[fs == f].mean())) for f in range(8)}
        print(f'AXIS {name}{a+1} var {ev[a]*100:.1f}% corr(log n) {np.corrcoef(np.log(Xs.sum(1)), sc)[0,1]:.2f} fam means {fm}')
        print('   +', '; '.join(M.motif_id[mi[j]] + ' ' + M.title[mi[j]] for j in o[::-1][:8])); print('   -', '; '.join(M.motif_id[mi[j]] + ' ' + M.title[mi[j]] for j in o[:8]))
        print('   + trad:', '; '.join(G.group[gi[j]] for j in og[::-1][:8])); print('   - trad:', '; '.join(G.group[gi[j]] for j in og[:8]))
        lst.append({'var': round(float(ev[a] * 100), 1), 's': q.tolist(), 'pos': [int(mi[j]) for j in o[::-1][:8]], 'neg': [int(mi[j]) for j in o[:8]],
                    'posT': [int(gi[j]) for j in og[::-1][:6]], 'negT': [int(gi[j]) for j in og[:6]], 'rho': round(float(np.corrcoef(np.log(Xs.sum(1)), sc)[0, 1]), 2)})
    axes[name] = {'g': gi.tolist(), 'nm': int(m_ok.sum()), 'ax': lst}
D['axes'] = axes
# ---------- distance decay with the JS-replicable similarity
lat = np.radians(G.latitude.values); lon = np.radians(G.longitude.values)
s_ = np.sin(lat)[:, None] * np.sin(lat)[None, :] + np.cos(lat)[:, None] * np.cos(lat)[None, :] * np.cos(lon[:, None] - lon[None, :])
DD = 6371 * np.arccos(np.clip(s_, -1, 1))
bins = [0, 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 14000, 16000, 20100]
decay = {'bins': bins}; ref = {}; rng = np.random.default_rng(0)
def simset(ms):
    el = X[:, ms].sum(1) >= 10
    Xs = X[el][:, ms]; df = Xs.sum(0); ok = df > 0
    idf = np.zeros(Xs.shape[1]); idf[ok] = np.log(el.sum() / df[ok])
    W = normalize(Xs * idf); return el, W @ W.T
for name, ms in [('all', np.ones(len(M), bool)), ('A', isA), ('B', ~isA)]:
    el, S = simset(ms); ei = np.where(el)[0]; Dk = DD[el][:, el]; iu = np.triu_indices(len(ei), 1)
    d = Dk[iu]; sv = S[iu]; b = np.digitize(d, bins) - 1
    decay[name] = {'mean': [round(float(sv[b == i].mean()), 4) for i in range(len(bins) - 1)], 'n': [int((b == i).sum()) for i in range(len(bins) - 1)], 'nel': int(el.sum())}
    pos = {g: i for i, g in enumerate(ei)}
    r = G.index[G.group == 'Russians'][0]; u = G.index[G.group == 'Ukrainians'][0]; c = G.index[G.group == 'Chukchi'][0]; t = G.index[G.group == 'Tlingit'][0]
    ref[name] = {'Russians~Ukrainians': round(float(S[pos[r], pos[u]]), 4), 'Chukchi~Tlingit': round(float(S[pos[c], pos[t]]), 4)}
    S2 = S.copy(); np.fill_diagonal(S2, -1); top = np.argsort(-S2, 1)[:, :5]; dd5 = np.take_along_axis(Dk, top, 1)
    decay[name]['nn_median_km'] = round(float(np.median(dd5[:, 0]))); decay[name]['top5_within2000'] = round(float((dd5 < 2000).mean()), 3); decay[name]['rand_within2000'] = round(float((d < 2000).mean()), 3)
    # bootstrap over traditions: far bin (16-20k) minus mid bins (10-14k)
    diffs = []
    for _ in range(300):
        s = rng.integers(0, len(ei), len(ei)); Ds = Dk[np.ix_(s, s)]; Ss = S[np.ix_(s, s)]; m_ = Ds > 1
        far = Ss[m_ & (Ds >= 16000)].mean(); mid = Ss[m_ & (Ds >= 10000) & (Ds < 14000)].mean(); diffs.append(far - mid)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    decay[name]['far_minus_mid'] = [round(float(sv[b == 14].mean() - sv[(b == 11) | (b == 12)].mean()), 4), round(float(lo), 4), round(float(hi), 4)]
    print('DECAY', name, decay[name])
D['decay'] = decay; D['ref'] = ref; print('REF', ref)
# ---------- motif atlas
Em = np.load(f'{out}/umap_m.npy'); Em = (Em - Em.min(0)) / (Em.max(0) - Em.min(0))
l3 = np.array(labels[3]); regs3 = [nodes[i]['id'] for i in range(len(nodes)) if nodes[i]['k'] in (2, 3) and nodes[i]['id'] in set(labels[3])]
regs3 = sorted(set(labels[3]), key=lambda i: nodes[i]['rank'])
Xkm = Xk[:, km]; P = np.array([Xkm[l3 == r].mean(0) for r in regs3]).T
Am = isA[km]; base = np.zeros_like(P)
for sel in [Am, ~Am]: base[sel] = P[sel].mean(0)
lift = P / base; share = lift / lift.sum(1, keepdims=True)
home = np.where(share.max(1) >= 0.6, share.argmax(1), 3)
print('motif atlas: regs3', [nodes[i]['name'] for i in regs3], 'home counts', np.bincount(home, minlength=4).tolist())
D['atlas'] = {'m': midx.tolist(), 'xy': np.round(Em, 4).tolist(), 'home': home.tolist(), 'share': np.round(share, 2).tolist(), 'regs': [int(i) for i in regs3]}
# ---------- meta
rs = X.sum(1)
D['meta'] = {'nG': int(len(G)), 'nM': int((X.sum(0) > 0).sum()), 'nPairs': int(X.sum()), 'medianM': int(np.median(rs)), 'minM': int(rs.min()), 'maxM': int(rs.max()), 'nKept': int(N), 'nKeptM': int(km.sum()),
             'nA': int(isA.sum()), 'nB': int((~isA).sum()), 'boot': json.load(open(f'{out}/boot.json'))}
Lw = np.load(f'{out}/ward.npy')                                   # the whole consensus tree behind the clusters, drawn on the Tree tab
D['tree'] = {'merge': Lw[:, :2].astype(int).tolist(), 'h': Lw[:, 2].round(3).tolist()}
json.dump(D, open(f'{out}/data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import os; print('data.json bytes', os.path.getsize(f'{out}/data.json'))
