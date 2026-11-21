"""Link every unit of 'Этносы и ареалы' to a tradition of the old database.

usage: python3 -I match_old.py <out_dir> <old_groups_motifs.csv> [manual_unit_old.tsv]
Evidence: (1) similarity of transliterated names, (2) overlap of motif sets on the
motifs present in both versions (entries already assigned to units).
manual file columns: unit_id, old_tradition   ('NEW' = no counterpart, '-' = not in the table)
Writes <out_dir>/unit_map.tsv and prints what still needs a decision.
"""
import csv, os, re, sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

out, f_old = sys.argv[1], sys.argv[2]
manual_path = sys.argv[3] if len(sys.argv) > 3 else None

TR = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i',
      'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
      'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': '', 'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'iu', 'я': 'ia'}


def lat(s):
    return ''.join(TR.get(c, c) for c in s.lower())


def simp(w):
    """rough phonetic key shared by a transliterated Russian and an English ethnonym"""
    w = re.sub(r'[^a-z]', '', w.lower())
    for a, b in (('sch', 'sh'), ('tch', 'ch'), ('dzh', 'j'), ('kh', 'h'), ('ph', 'f'), ('th', 't'), ('ck', 'k'), ('qu', 'k'),
                 ('q', 'k'), ('w', 'v'), ('y', 'i'), ('x', 'ks'), ('ts', 'c'), ('tz', 'c'), ('z', 's'), ('ou', 'u'),
                 ('oo', 'u'), ('ee', 'i'), ('gu', 'g'), ('hu', 'u')):
        w = w.replace(a, b)
    w = re.sub(r'c(?=[aouklrnt]|$)', 'k', w)
    w = re.sub(r'(.)\1', r'\1', w)
    w = re.sub(r'(ians|ans|tsi|ci|si|es|s|i|e|a)$', '', w) if len(w) > 4 else w
    return w


STOP = {'of', 'the', 'and', 'etc', 'north', 'south', 'east', 'west', 'northern', 'southern', 'eastern', 'western', 'central',
        'upper', 'lower', 'ancient', 'modern', 'islands', 'island', 'coast', 'river', 'lake', 'new', 'old', 'incl', 'dep'}


def en_keys(name):
    ks = [simp(w) for w in re.findall(r'[A-Za-z]+', name) if len(w) > 2 and w.lower() not in STOP]
    return [k for k in ks if len(k) > 2]


def ru_keys(text):
    text = text.lower().replace('ё', 'е')
    text = re.sub(r'\(([а-я]{1,5}-?)\)([а-я])', r'\2', text)
    top = re.sub(r'\([^()]*\)', ' ', re.sub(r'\([^()]*\)', ' ', text))
    t = [simp(lat(w)) for w in re.findall(r'[а-яa-z]+', top) if len(w) > 2][:14]
    a = [simp(lat(w)) for w in re.findall(r'[а-яa-z]+', text) if len(w) > 2][:60]
    return [k for k in t if len(k) > 2], [k for k in a if len(k) > 2]


_cache = {}
def ratio(a, b):
    if a == b:
        return 1.0
    key = (a, b)
    r = _cache.get(key)
    if r is None:
        if abs(len(a) - len(b)) > 3 or a[0] != b[0] and a[1:3] != b[1:3]:
            r = 0.0
        else:
            sm = SequenceMatcher(None, a, b)
            r = sm.ratio() if sm.quick_ratio() >= 0.7 else 0.0
        _cache[key] = r
    return r


def name_sim(tk, ak, ek):
    if not ek:
        return 0.0
    s_top = max((ratio(e, c) for e in ek for c in tk), default=0.0)
    s_all = max((ratio(e, c) for e in ek for c in ak), default=0.0)
    return max(s_top, 0.9 * s_all)


units = list(csv.DictReader(open(os.path.join(out, 'units_raw.tsv'), encoding='utf-8'), delimiter='\t'))
entries = list(csv.DictReader(open(os.path.join(out, 'entries_units.tsv'), encoding='utf-8'), delimiter='\t'))
old = defaultdict(set)
for r in csv.DictReader(open(f_old, encoding='utf-8')):
    old[r['group']].add(r['motif_id'].lower())
old_motifs = set().union(*old.values())
section = {e['motif_id'][0] for e in entries}

M = defaultdict(set)
for e in entries:
    if e['flag'] == '' and e['unit_id'] and e['unit_id'] != '-':
        M[e['unit_id']].add(e['motif_id'])

manual = {}
if manual_path and os.path.exists(manual_path):
    ids = {u['unit_id'] for u in units}
    for r in csv.DictReader(open(manual_path, encoding='utf-8'), delimiter='\t'):
        if r['unit_id'] not in ids:
            print('! manual: unknown unit', r['unit_id'])
        for o in r['old_tradition'].split(' + '):
            if o not in old and o not in ('NEW', '-'):
                print('! manual: unknown old tradition', repr(o), 'for', r['unit_id'])
        manual[r['unit_id']] = r['old_tradition']

old_k = {t: en_keys(t) for t in old}
old_sec = {t: {m for m in bt if m[0] in section} for t, bt in old.items()}
res = []
for u in units:
    uid = u['unit_id']
    mu = M.get(uid, set()) & old_motifs
    tk, ak = ru_keys(u['text'])
    cands = []
    for t, bt in old.items():
        ns = name_sim(tk, ak, old_k[t])
        inter = len(mu & bt)
        un = len(mu | old_sec[t])
        jac = inter / un if un else 0.0
        if ns >= 0.72 or (inter >= 3 and jac >= 0.3):
            cands.append((round(0.6 * ns + 0.4 * jac, 3), t, round(ns, 2), inter, len(old_sec[t]), round(jac, 2)))
    cands.sort(reverse=True)
    c = cands[:4]
    if uid in manual:
        status, best = 'manual', manual[uid]
    elif u['insufficient'] == '1':
        status, best = 'not-in-table', '-'
    elif c and c[0][2] >= 0.85 and (c[0][5] >= 0.25 or (len(mu) <= 2 and c[0][3] >= min(1, len(mu)))) \
            and (len(c) == 1 or c[0][0] - c[1][0] >= 0.08):
        status, best = 'auto', c[0][1]
    elif c:
        status, best = 'review', c[0][1]
    else:
        status, best = 'nomatch', ''
    res.append(dict(unit_id=uid, area=u['area'], no=u['no'], unit_text=u['text'], italic=u['italic'],
                    insufficient=u['insufficient'], n_motifs=len(M.get(uid, set())), n_old_motifs=len(mu),
                    status=status, old_tradition=best,
                    candidates=' || '.join(f'{x[1]} ({x[2]},{x[3]}/{x[4]})' for x in c)))

share = Counter(o for r in res if r['status'] in ('auto', 'manual') for o in r['old_tradition'].split(' + ') if o not in ('NEW', '-', ''))
for r in res:
    o = r['old_tradition']
    if r['status'] in ('review', 'nomatch'):
        r['relation'] = 'undecided'
    elif o == 'NEW':
        r['relation'] = 'new'
    elif o in ('-', ''):
        r['relation'] = 'not-in-table'
    elif ' + ' in o:
        r['relation'] = 'merge'
    else:
        r['relation'] = 'split' if share[o] > 1 else 'same'
with open(os.path.join(out, 'unit_map.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(res[0]), delimiter='\t'); w.writeheader(); w.writerows(res)

used = [r for r in res if r['n_motifs'] > 0]
print('units:', len(res), '| with entries here:', len(used))
print('  status (all):', dict(Counter(r['status'] for r in res)))
print('  status (with entries):', dict(Counter(r['status'] for r in used)))
print('  relation (with entries):', dict(Counter(r['relation'] for r in used)))
print('  old traditions linked:', len(share), 'of', len(old), '| old traditions with entries in this section but not linked:',
      len([t for t in old if old_sec[t] and t not in share]))
if '--show' in sys.argv:
    for r in used:
        if r['status'] in ('review', 'nomatch'):
            print(f"{r['unit_id']}|{r['unit_text'][:46]}|{r['n_motifs']}/{r['n_old_motifs']}|{r['candidates'][:150]}")
if '--unlinked' in sys.argv:
    print('UNLINKED OLD:', ' ; '.join(f'{t} ({len(old_sec[t])})' for t in sorted(old) if t not in share))
if '--splits' in sys.argv:
    by = defaultdict(list)
    for r in res:
        if r['relation'] == 'split':
            by[r['old_tradition']].append(f"{r['unit_id'].split('#')[1]}:{r['unit_text'][:28]}[{r['status'][0]}]")
    for o, l in sorted(by.items()):
        print('SPLIT', o, '<=', ' / '.join(l))
