import sys, csv, collections
csv.field_size_limit(10**9)
pairs, oldgm = sys.argv[1], sys.argv[2]
old = collections.defaultdict(set)
for r in csv.DictReader(open(oldgm, encoding='utf-8-sig')):
    old[r['group']].add(r['motif_id'])
oldm = set().union(*old.values())
new = collections.defaultdict(set); status = {}
for r in csv.DictReader(open(pairs, encoding='utf-8-sig')):
    if r['motif_in_digital_db'] not in ('1', 'True', 'true', 'yes'): continue
    new[r['tradition']].add(r['motif_id']); status[r['tradition']] = r['tradition_status']
newm = set().union(*new.values()); common = oldm & newm
print('old motifs', len(oldm), 'new motifs', len(newm), 'common', len(common))
rows = []
for t in sorted(set(old) | set(new)):
    o = old.get(t, set()) & common; n = new.get(t, set()) & common
    rows.append((t, len(old.get(t, ())), len(new.get(t, ())), len(o), len(o & n), len(n - o), len(new.get(t, set()) - common)))
print('--- lowest recall of old pairs (old traditions with 15+ old motifs)')
for r in sorted([r for r in rows if r[3] >= 15], key=lambda r: r[4] / r[3])[:32]:
    print(f'{r[0]:44s} old {r[1]:4d} new {r[2]:4d} | common-motif pairs: old {r[3]:4d} found {r[4]:4d} ({100*r[4]/r[3]:3.0f}%) added {r[5]:4d} | on new motifs {r[6]:4d}')
print('--- largest relative gain on common motifs')
for r in sorted([r for r in rows if r[3] >= 10], key=lambda r: -r[5] / r[3])[:32]:
    print(f'{r[0]:44s} old {r[1]:4d} new {r[2]:4d} | common-motif pairs: old {r[3]:4d} found {r[4]:4d} ({100*r[4]/r[3]:3.0f}%) added {r[5]:4d} (+{100*r[5]/r[3]:3.0f}%) | on new motifs {r[6]:4d}')
import statistics
rec = [r[4] / r[3] for r in rows if r[3] >= 15]; print('traditions with 15+ old pairs:', len(rec), 'median recall %.3f' % statistics.median(rec), 'below 0.8:', sum(x < 0.8 for x in rec), 'below 0.6:', sum(x < 0.6 for x in rec))
gain = [r[5] / r[3] for r in rows if r[3] >= 15]; print('median gain on common motifs %.3f' % statistics.median(gain), 'above 0.5:', sum(x > 0.5 for x in gain), 'above 1.0:', sum(x > 1 for x in gain))
