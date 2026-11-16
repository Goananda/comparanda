"""Build the 0/1 matrix of traditions x motifs from the source files.

Usage: python3 prep.py <source_dir> <work_dir>
Writes X.npy, groups.csv, motifs.csv. Eight motif ids in groups_motifs.csv end with an underscore; they are mapped to the ids in motifs.csv.
"""
import sys, json
import numpy as np, pandas as pd
dl, out = sys.argv[1], sys.argv[2]
m = pd.read_csv(f'{dl}/motifs.csv', keep_default_na=False)
g = pd.read_csv(f'{dl}/groups_motifs.csv', index_col=0, keep_default_na=False)
g['motif_id'] = g.motif_id.str.rstrip('_')
c = pd.DataFrame(json.load(open(f'{dl}/coords_clean.json')))
print('motifs', m.shape, 'pairs', g.shape, 'coords', c.shape)
print('dup pairs', g.duplicated(['group','motif_id']).sum())
print('motif ids in pairs not in motifs.csv:', len(set(g.motif_id)-set(m.motif_id)), '| motifs never used:', len(set(m.motif_id)-set(g.motif_id)))
print('groups in pairs not in coords:', len(set(g.group)-set(c.group)), '| coords not in pairs:', len(set(c.group)-set(g.group)))
print('dup group names in coords', c.group.duplicated().sum())
groups = sorted(c.group)
motifs = list(m.motif_id)
gi = {x:i for i,x in enumerate(groups)}; mi = {x:i for i,x in enumerate(motifs)}
X = np.zeros((len(groups), len(motifs)), dtype=np.uint8)
X[g.group.map(gi).values.astype(int), g.motif_id.map(mi).values.astype(int)] = 1
print('X', X.shape, 'ones', X.sum())
rs = X.sum(1); cs = X.sum(0)
print('motifs per tradition: min %d q25 %d median %d q75 %d max %d mean %.1f' % (rs.min(), np.percentile(rs,25), np.median(rs), np.percentile(rs,75), rs.max(), rs.mean()))
print('traditions per motif: min %d q25 %d median %d q75 %d max %d' % (cs.min(), np.percentile(cs,25), np.median(cs), np.percentile(cs,75), cs.max()))
for t in [1,2,3,5,10,20]: print('motifs with df>=%d: %d' % (t, (cs>=t).sum()))
for t in [5,10,20,30]: print('traditions with >=%d motifs: %d' % (t, (rs>=t).sum()))
m['letter'] = m.motif_id.str[0]
m['df'] = cs
print(m.groupby('letter').agg(n=('motif_id','size'), mean_df=('df','mean'), total=('df','sum')))
for L, sub in m.groupby('letter'):
    print('---', L); print(sub.sort_values('df', ascending=False).head(6)[['motif_id','title','df']].to_string(index=False, header=False))
c = c.set_index('group').loc[groups].reset_index()
c['n_motifs'] = rs
print(c.sort_values('n_motifs').head(12).to_string()); print(c.sort_values('n_motifs').tail(12).to_string())
print('lon range', c.longitude.min(), c.longitude.max(), 'lat', c.latitude.min(), c.latitude.max())
np.save(f'{out}/X.npy', X); c.to_csv(f'{out}/groups.csv', index=False); m.to_csv(f'{out}/motifs.csv', index=False)
