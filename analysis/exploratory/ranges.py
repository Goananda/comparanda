"""Exploratory: motif ranges as combinations of eight macro-regions, compared with an independence baseline. Not used on the page.
Usage: python3 ranges.py <work_dir>
"""
import sys, warnings, itertools
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
out = sys.argv[1]
X = np.load(f'{out}/X.npy').astype(float)
G = pd.read_csv(f'{out}/groups.csv'); M = pd.read_csv(f'{out}/motifs.csv', keep_default_na=False)
kg = np.load(f'{out}/keep_g.npy'); lab = pd.read_csv(f'{out}/ward_labels.csv')
l8 = lab['k8'].values
Xk = X[kg]; Gk = G[kg].reset_index(drop=True)
# name regions by richest tradition for now
regs = sorted(set(l8))
for r in regs:
    sub = Gk[l8 == r]; print(r, len(sub), 'lat %.0f lon %.0f' % (sub.latitude.median(), sub.longitude.median()), '|', '; '.join(sub.sort_values('n_motifs', ascending=False).group.head(5)))
P = np.array([Xk[l8 == r].mean(0) for r in regs]).T     # motif x region prevalence
Nr = np.array([(l8 == r).sum() for r in regs]); Cnt = np.array([Xk[l8 == r].sum(0) for r in regs]).T
letters = M.letter.values; A = np.isin(letters, list('abcdefghi'))
df = Xk.sum(0)
for TH_P, TH_N in [(0.08, 3), (0.10, 3), (0.05, 3)]:
    pres = (P >= TH_P) & (Cnt >= TH_N)
    use = (df >= 10) & (pres.sum(1) >= 1)
    print(f'\n##### threshold prevalence>={TH_P}, n>={TH_N}: motifs used {use.sum()}, mean #regions {pres[use].sum(1).mean():.2f}; region marginals {np.round(pres[use].mean(0),2)}')
    for name, ms in [('A', A), ('B', ~A)]:
        u = use & ms; Pr = pres[u]
        marg = Pr.mean(0)
        combos = pd.Series([tuple(np.where(row)[0]) for row in Pr]).value_counts()
        # expected under independence
        rows = []
        for combo, n in combos.items():
            pr = np.prod([marg[i] if i in combo else 1 - marg[i] for i in range(len(regs))])
            rows.append((combo, n, pr*u.sum()))
        t = pd.DataFrame(rows, columns=['combo', 'obs', 'exp']); t['ratio'] = t.obs/t.exp
        t['regions'] = t.combo.map(lambda c: '+'.join(str(regs[i]) for i in c))
        print(f'--- {name}: {u.sum()} motifs; top combos by count'); print(t.sort_values('obs', ascending=False).head(22)[['regions','obs','exp','ratio']].round(1).to_string(index=False))
    if TH_P == 0.08: np.save(f'{out}/pres8.npy', pres)
