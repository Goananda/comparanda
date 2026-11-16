"""Collect everything the page needs into data.json: cluster hierarchy with names and indicator motifs, NMF complexes,
principal axes (sections A-I and J-N separately), distance decay of similarity, motif atlas.

Usage: python3 export.py <work_dir>   (run after prep.py, clus.py, nmf.py, embed.py)
Cluster and component names are assigned by hand from their membership and are specific to this version of the data.
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
D['m'] = {'id': M.motif_id.tolist(), 'title': M.title.tolist(), 'desc': M.description.tolist()}
D['inc'] = [np.where(X[:, j] > 0)[0].tolist() for j in range(X.shape[1])]
D['kept'] = kidx.tolist()
# ---------- hierarchy nodes
NAMES = {(2,161): 'Евразия от Европы до Индии и Монголии, Магриб', (2,670): 'Остальной мир',
 (3,268): 'Африка, юг и восток Азии, Австралия, Океания', (3,402): 'Америка, Сибирь и Арктика',
 (4,174): 'Мезоамерика и Южная Америка', (4,228): 'Северная Америка, Сибирь и Арктика',
 (5,101): 'Африка южнее Сахары', (5,167): 'Юг и восток Азии, Австралия, Океания',
 (6,75): 'Сибирь, Берингия и Арктика', (6,153): 'Северная Америка южнее Субарктики',
 (7,34): 'Мезоамерика', (7,140): 'Южная Америка',
 (8,43): 'Океания', (8,124): 'Юг и восток Азии, Австралия',
 (9,62): 'Равнины и восток Северной Америки', (9,91): 'Запад Северной Америки',
 (10,43): 'Европа', (10,118): 'Магриб, Балканы, Кавказ, Центральная и Южная Азия',
 (11,30): 'Сибирь и Приамурье', (11,45): 'Берингия и Арктика: от Камчатки до Гренландии',
 (12,41): 'Северо-Западное побережье и Плато', (12,50): 'Калифорния, Большой Бассейн, Юго-Запад'}
# style: hue family 0..7 = [WE, AF, SA, OC, SI, NA, MA, SAm]; shape 0 circle, 1 diamond, 2 triangle
STYLE = {(2,161): (0,0), (2,670): (2,0), (3,268): (2,0), (3,402): (4,0), (4,174): (7,0), (4,228): (4,0), (5,101): (1,0), (5,167): (2,0),
 (6,75): (4,0), (6,153): (5,0), (7,34): (6,0), (7,140): (7,0), (8,43): (3,0), (8,124): (2,0), (9,62): (5,1), (9,91): (5,0),
 (10,43): (0,1), (10,118): (0,0), (11,30): (4,1), (11,45): (4,0), (12,41): (5,2), (12,50): (5,0)}
SHORT = {'Евразия от Европы до Индии и Монголии, Магриб': 'Запад и центр Евразии', 'Остальной мир': 'Остальной мир',
 'Африка, юг и восток Азии, Австралия, Океания': 'Африка, юг Азии, Океания', 'Америка, Сибирь и Арктика': 'Америка и Сибирь',
 'Мезоамерика и Южная Америка': 'Латинская Америка', 'Северная Америка, Сибирь и Арктика': 'Северная Америка и Сибирь',
 'Африка южнее Сахары': 'Африка', 'Юг и восток Азии, Австралия, Океания': 'Юг Азии и Океания',
 'Сибирь, Берингия и Арктика': 'Сибирь и Арктика', 'Северная Америка южнее Субарктики': 'Северная Америка',
 'Мезоамерика': 'Мезоамерика', 'Южная Америка': 'Южная Америка', 'Океания': 'Океания', 'Юг и восток Азии, Австралия': 'Юг и восток Азии',
 'Равнины и восток Северной Америки': 'Равнины и восток', 'Запад Северной Америки': 'Запад Северной Америки',
 'Европа': 'Европа', 'Магриб, Балканы, Кавказ, Центральная и Южная Азия': 'От Магриба до Монголии',
 'Сибирь и Приамурье': 'Сибирь', 'Берингия и Арктика: от Камчатки до Гренландии': 'Берингия и Арктика',
 'Северо-Западное побережье и Плато': 'Северо-Запад', 'Калифорния, Большой Бассейн, Юго-Запад': 'Калифорния и Юго-Запад', 'Все традиции': 'Все'}
def members(k):
    l = lab[f'k{k}'].values
    return [frozenset(np.where(l == c)[0].tolist()) for c in np.unique(l)]
nodes = [{'id': 0, 'name': 'Все традиции', 'parent': -1, 'k': 1, 'mem': frozenset(range(N))}]
prev = [nodes[0]['mem']]; byset = {nodes[0]['mem']: 0}; splits = {}
for k in range(2, 13):
    cur = members(k); new = [c for c in cur if c not in prev]; parent = [p for p in prev if p not in cur][0]
    ids = []
    for c in sorted(new, key=len):
        nid = len(nodes); byset[c] = nid; ids.append(nid)
        nodes.append({'id': nid, 'name': NAMES[(k, len(c))], 'parent': byset[parent], 'k': k, 'mem': c, 'hue': STYLE[(k, len(c))][0], 'shape': STYLE[(k, len(c))][1]})
    splits[k] = {'parent': byset[parent], 'children': ids}
    prev = cur
# leaf order for legends (geographic tour)
LEAF_ORDER = ['Европа', 'Магриб, Балканы, Кавказ, Центральная и Южная Азия', 'Африка южнее Сахары', 'Юг и восток Азии, Австралия', 'Океания', 'Сибирь и Приамурье',
              'Берингия и Арктика: от Камчатки до Гренландии', 'Северо-Западное побережье и Плато', 'Калифорния, Большой Бассейн, Юго-Запад', 'Равнины и восток Северной Америки', 'Мезоамерика', 'Южная Америка']
leaves12 = members(12); leafrank = {}
for c in leaves12: leafrank[c] = LEAF_ORDER.index(nodes[byset[c]]['name'])
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
for nd in nodes: nd['short'] = SHORT[nd['name']]
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
    print(nd['id'], nd['k'], nd['n'], nd['name'], '| hue', nd['hue'], 'shape', nd['shape'], '| shareA', nd['shareA'], '|', '; '.join(f"{M.motif_id[j]} {M.title[j]} ({a}/{b})" for j, a, b in nd['ind'][:5]))
# ---------- NMF
Wn = np.load(f'{out}/nmf_W_12.npy'); H = np.load(f'{out}/nmf_H_12.npy')
NMF_NAMES = {'Uzbek': 'Передняя и Центральная Азия, Кавказ', 'Germans': 'Европа', 'Muslim Malay': 'Юго-Восточная Азия и Южный Китай', 'Tagish': 'Северо-Западное побережье и Субарктика',
             'Wayampi, Emerillon': 'Амазония и Гвиана', 'Totonac, Tepehua': 'Мезоамерика', 'Northern Paiute': 'Большой Бассейн, Калифорния, Плато', 'Ngonde,Safwa.Mkulwe,Kinga': 'Африка южнее Сахары',
             'Western Evenki': 'Сибирь', 'Plains Cree': 'Равнины и Великие озёра', 'Polar Eskimo': 'Эскимосская Арктика', 'Ulithi, Ngulu': 'Океания'}
NMF_ORDER = ['Европа', 'Передняя и Центральная Азия, Кавказ', 'Африка южнее Сахары', 'Юго-Восточная Азия и Южный Китай', 'Океания', 'Сибирь', 'Эскимосская Арктика',
             'Северо-Западное побережье и Субарктика', 'Большой Бассейн, Калифорния, Плато', 'Равнины и Великие озёра', 'Мезоамерика', 'Амазония и Гвиана']
comps = []
for ci in range(12):
    w = Wn[:, ci]; h = H[ci]; spec = h / (H.sum(0) + 1e-12)
    topm = np.argsort(-(h * spec))[:8]; topg = np.argsort(-w)[:8]
    name = NMF_NAMES[Gk.group[topg[0]]]
    wq = np.clip(np.round(100 * w / np.percentile(w, 99)), 0, 100).astype(int)
    comps.append({'name': name, 'w': wq.tolist(), 'motifs': [int(midx[j]) for j in topm], 'trad': [int(kidx[j]) for j in topg], 'active': int((wq >= 15).sum())})
comps.sort(key=lambda c: NMF_ORDER.index(c['name']))
D['nmf'] = comps
for c in comps: print('NMF', c['name'], '| active', c['active'], '|', '; '.join(M.motif_id[j] + ' ' + M.title[j] for j in c['motifs'][:4]))
# ---------- axes
fam8 = np.array([nodes[i]['hue'] for i in labels[8]]); FAM = ['WE', 'AF', 'SA', 'OC', 'SI', 'NA', 'MA', 'SAm']
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
             'nA': int(isA.sum()), 'nB': int((~isA).sum()), 'boot': {2: 0.81, 3: 0.59, 4: 0.65, 5: 0.73, 6: 0.71, 7: 0.68, 8: 0.63, 9: 0.59, 10: 0.64, 11: 0.68, 12: 0.66}}
json.dump(D, open(f'{out}/data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import os; print('data.json bytes', os.path.getsize(f'{out}/data.json'))
