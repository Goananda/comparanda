"""Write the derived tables (CSV) from the analysis outputs.

Usage: python3 make_tables.py <work_dir> <out_dir>
<work_dir> must hold X.npy, groups.csv, motifs.csv (from prep.py) and data.json (from export.py).
"""
import sys, json, os
import numpy as np, pandas as pd

work, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
X = np.load(f'{work}/X.npy').astype(int)
G = pd.read_csv(f'{work}/groups.csv')
M = pd.read_csv(f'{work}/motifs.csv', keep_default_na=False)
D = json.load(open(f'{work}/data.json', encoding='utf-8'))
nodes = D['nodes']; kept = D['kept']
isA = np.isin(M.letter.values, list('abcdefghi'))

EN = {
    'Все традиции': 'All traditions',
    'Евразия от Европы до Индии и Монголии, Магриб': 'Eurasia from Europe to India and Mongolia, Maghreb',
    'Остальной мир': 'Rest of the world',
    'Африка, юг и восток Азии, Австралия, Океания': 'Africa, South and East Asia, Australia, Oceania',
    'Америка, Сибирь и Арктика': 'Americas, Siberia and the Arctic',
    'Мезоамерика и Южная Америка': 'Mesoamerica and South America',
    'Северная Америка, Сибирь и Арктика': 'North America, Siberia and the Arctic',
    'Африка южнее Сахары': 'Sub-Saharan Africa',
    'Юг и восток Азии, Австралия, Океания': 'South and East Asia, Australia, Oceania',
    'Сибирь, Берингия и Арктика': 'Siberia, Beringia and the Arctic',
    'Северная Америка южнее Субарктики': 'North America south of the Subarctic',
    'Мезоамерика': 'Mesoamerica',
    'Южная Америка': 'South America',
    'Океания': 'Oceania',
    'Юг и восток Азии, Австралия': 'South and East Asia, Australia',
    'Равнины и восток Северной Америки': 'Plains and eastern North America',
    'Запад Северной Америки': 'Western North America',
    'Европа': 'Europe',
    'Магриб, Балканы, Кавказ, Центральная и Южная Азия': 'Maghreb, Balkans, Caucasus, Central and South Asia',
    'Сибирь и Приамурье': 'Siberia and the Amur region',
    'Берингия и Арктика: от Камчатки до Гренландии': 'Beringia and the Arctic, Kamchatka to Greenland',
    'Северо-Западное побережье и Плато': 'Northwest Coast and Plateau',
    'Калифорния, Большой Бассейн, Юго-Запад': 'California, Great Basin, Southwest',
    # NMF components
    'Передняя и Центральная Азия, Кавказ': 'Western and Central Asia, Caucasus',
    'Юго-Восточная Азия и Южный Китай': 'Southeast Asia and South China',
    'Сибирь': 'Siberia',
    'Эскимосская Арктика': 'Eskimo (Inuit and Yupik) Arctic',
    'Северо-Западное побережье и Субарктика': 'Northwest Coast and Subarctic',
    'Большой Бассейн, Калифорния, Плато': 'Great Basin, California, Plateau',
    'Равнины и Великие озёра': 'Plains and Great Lakes',
    'Амазония и Гвиана': 'Amazonia and the Guianas',
}
mid = lambda j: M.motif_id[j]
gname = lambda g: G.group[g]

# ---- 0/1 matrix
mat = pd.DataFrame(X, columns=M.motif_id); mat.insert(0, 'tradition', G.group)
mat.to_csv(f'{out}/matrix_traditions_x_motifs.csv', index=False)

# ---- traditions
T = pd.DataFrame({'tradition': G.group, 'longitude': G.longitude, 'latitude': G.latitude, 'n_motifs': X.sum(1),
                  'n_motifs_cosmology': X[:, isA].sum(1), 'n_motifs_adventure': X[:, ~isA].sum(1)})
T['in_analysis'] = 0; T.loc[kept, 'in_analysis'] = 1
for k in range(2, 13):
    col = pd.Series(pd.NA, index=T.index, dtype='Int64'); col.iloc[kept] = D['labels'][str(k)]; T[f'cluster_k{k}'] = col
um = np.array(D['umapG'])
for i, c in enumerate(['umap_x', 'umap_y']):
    col = pd.Series(np.nan, index=T.index); col.iloc[kept] = um[:, i]; T[c] = col
for i, comp in enumerate(D['nmf'], 1):
    col = pd.Series(pd.NA, index=T.index, dtype='Int64'); col.iloc[kept] = comp['w']; T[f'nmf_{i:02d}'] = col
for s in ['A', 'B']:
    for a, ax in enumerate(D['axes'][s]['ax'], 1):
        col = pd.Series(pd.NA, index=T.index, dtype='Int64'); col.iloc[D['axes'][s]['g']] = ax['s']; T[f'axis_{s}{a}'] = col
T.to_csv(f'{out}/traditions.csv', index=False)

# ---- clusters and long membership
rows = []
for n in nodes[1:]:
    rows.append({'cluster_id': n['id'], 'name_ru': n['name'], 'name_en': EN[n['name']], 'created_at_k': n['k'], 'parent_id': n['parent'],
                 'n_traditions': n['n'], 'median_share_cosmology': n['shareA'],
                 'indicator_motifs': '; '.join(f"{mid(j)} ({a:.2f}/{b:.2f})" for j, a, b in n['ind']),
                 'core_traditions': '; '.join(gname(g) for g in n['core'])})
pd.DataFrame(rows).to_csv(f'{out}/clusters.csv', index=False)
rows = []
for k in range(2, 13):
    for g, c in zip(kept, D['labels'][str(k)]):
        rows.append({'tradition': gname(g), 'k': k, 'cluster_id': c, 'cluster_name_ru': nodes[c]['name'], 'cluster_name_en': EN[nodes[c]['name']]})
pd.DataFrame(rows).to_csv(f'{out}/cluster_membership.csv', index=False)

# ---- motif summary
S = pd.DataFrame({'motif_id': M.motif_id, 'title': M.title, 'section': M.letter.str.upper(),
                  'category': np.where(isA, 'cosmology_etiology', 'adventure_trickster'), 'n_traditions': X.sum(0)})
A = D['atlas']; am = A['m']; regs = [EN[nodes[i]['name']] for i in A['regs']]
S['in_analysis'] = 0; S.loc[am, 'in_analysis'] = 1
xy = np.array(A['xy']); sh = np.array(A['share'])
for i, c in enumerate(['atlas_x', 'atlas_y']):
    col = pd.Series(np.nan, index=S.index); col.iloc[am] = xy[:, i]; S[c] = col
home = pd.Series(pd.NA, index=S.index, dtype='object'); home.iloc[am] = [regs[h] if h < 3 else 'widespread' for h in A['home']]; S['home_region'] = home
for i, c in enumerate(['share_west_central_eurasia', 'share_africa_south_asia_oceania', 'share_americas_siberia']):
    col = pd.Series(np.nan, index=S.index); col.iloc[am] = sh[:, i]; S[c] = col
S.to_csv(f'{out}/motif_summary.csv', index=False)

# ---- NMF components
rows = []
for i, c in enumerate(D['nmf'], 1):
    rows.append({'component': f'nmf_{i:02d}', 'name_ru': c['name'], 'name_en': EN[c['name']], 'n_traditions_weight_ge_15': c['active'],
                 'top_motifs': '; '.join(f"{mid(j)} {M.title[j]}" for j in c['motifs']), 'top_traditions': '; '.join(gname(g) for g in c['trad'])})
pd.DataFrame(rows).to_csv(f'{out}/nmf_components.csv', index=False)

# ---- principal axes
rows = []
for s, label in [('A', 'cosmology_etiology (sections A-I)'), ('B', 'adventure_trickster (sections J-N)')]:
    for a, ax in enumerate(D['axes'][s]['ax'], 1):
        for pole, mk, tk in [('negative', 'neg', 'negT'), ('positive', 'pos', 'posT')]:
            rows.append({'axis': f'axis_{s}{a}', 'motif_set': label, 'variance_explained_pct': ax['var'], 'corr_with_log_n_motifs': ax['rho'], 'pole': pole,
                         'top_motifs': '; '.join(f"{mid(j)} {M.title[j]}" for j in ax[mk]), 'top_traditions': '; '.join(gname(g) for g in ax[tk])})
pd.DataFrame(rows).to_csv(f'{out}/axes.csv', index=False)

# ---- distance decay
dec = D['decay']; b = dec['bins']
pd.DataFrame({'km_from': b[:-1], 'km_to': [min(20000, v) for v in b[1:]],
              'mean_similarity_all': dec['all']['mean'], 'mean_similarity_cosmology': dec['A']['mean'], 'mean_similarity_adventure': dec['B']['mean'],
              'n_pairs_all': dec['all']['n'], 'n_pairs_cosmology': dec['A']['n'], 'n_pairs_adventure': dec['B']['n']}).to_csv(f'{out}/distance_decay.csv', index=False)
print('tables written to', out, ':', sorted(os.listdir(out)))
