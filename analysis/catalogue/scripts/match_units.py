"""Assign every tradition name found on motif pages to a unit of 'Этносы и ареалы'.

usage: python3 -I match_units.py <out_dir> [manual_names.tsv]
Reads  <out_dir>/entries_raw.tsv, <out_dir>/units_raw.tsv
Writes <out_dir>/entries_units.tsv (entries with unit id, method, score, candidates)
       <out_dir>/name_review.tsv   (distinct names that were not resolved in their own area)
Manual file columns: region_key ('*' = any), name, qualifier_pattern ('' = any, '^$' = no qualifier, '=text' = exactly this,
otherwise a part of the qualifier; the longest matching pattern wins),
unit_id ('-' = not a tradition of the table, '?' = leave unresolved, 'a || b' = explicit candidates, 'a && b' = all of them, '+a' = add a to the units of the other matching '+' rules,
'old:Name' = a tradition of the old database that has no unit on the site's list).
"""
import csv, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import norm, region_key, area_key

out = sys.argv[1]
manual_path = sys.argv[2] if len(sys.argv) > 2 else None

TOK = re.compile(r'[a-zа-я0-9]+(?:-[a-zа-я0-9]+)*')


ABBR = {'о-в', 'о-ва', 'о-вов', 'п-ов', 'п-ва'}        # 'islands', 'peninsula': never split into parts ('ва' is also an ethnonym)


def toks(s):
    res = []
    for w in TOK.findall(norm(s)):
        res.append(w)
        if '-' in w and w not in ABBR:
            res.extend(x for x in w.split('-') if len(x) > 1)
    return res


def similar(a, b):
    if a == b:
        return True
    n = min(len(a), len(b))
    if n < 4 or abs(len(a) - len(b)) > 3:
        return False
    k = 0
    while k < n and a[k] == b[k]:
        k += 1
    return k >= max(4, n - 2)


GENERIC = {'северные', 'южные', 'восточные', 'западные', 'центральные', 'верхние', 'нижние', 'горные', 'лесные',
           'древняя', 'древний', 'древние', 'о-в', 'о-ва', 'о-вов', 'п-ов', 'п-ва', 'оз', 'р', 'и', 'или', 'либо', 'в', 'на',
           'с', 'из', 'у', 'к', 'по', 'юг', 'север', 'запад', 'восток', 'центр', 'южный', 'северный', 'район', 'мыс'}

units = list(csv.DictReader(open(os.path.join(out, 'units_raw.tsv'), encoding='utf-8'), delimiter='\t'))


def prep_unit(u):
    text = norm(u['text'])
    text = re.sub(r'\(([a-zа-я]{1,5}-?)\)([a-zа-я])', lambda m: f'{m.group(1)}{m.group(2)}@@', text)
    text = re.sub(r'([a-zа-я]{1,5}-?)([a-zа-я-]+)@@', lambda m: f'{m.group(1)}{m.group(2)} {m.group(2)}', text)
    text = re.sub(r'\(([a-zа-я]+)\)\s+(?=[a-zа-я])', r'\1 ', text)
    depth, buf_t, buf_i = 0, [], []
    for ch in text:
        if ch == '(':
            depth += 1; buf_i.append(' ')
        elif ch == ')':
            depth = max(0, depth - 1); buf_i.append(' ')
        elif depth:
            buf_i.append(ch)
        else:
            buf_t.append(ch)
    head = re.split(r'[:,;(]', text, maxsplit=1)[0]
    return dict(head=set(toks(head)), top=set(toks(''.join(buf_t))), inner=set(toks(''.join(buf_i))))


LEVELS = (('head', 4.0, 3.0), ('top', 3.0, 2.5), ('inner', 2.0, 1.5))
allt, pref = {}, {}
for i, u in enumerate(units):
    u['id'] = u['unit_id']; u['uid'] = i
    u.update(prep_unit(u))
    allt[i] = u['head'] | u['top'] | u['inner']
    d = defaultdict(list)
    for t in allt[i]:
        if len(t) >= 4:
            d[t[:4]].append(t)
    pref[i] = d


class Index:
    """token -> units; lets a name be scored against the few units that share a word with it"""

    def __init__(self, us):
        self.exact = defaultdict(list)
        self.stem = defaultdict(list)
        for u in us:
            seen = {}
            for name, ex, st in LEVELS:
                for t in u[name]:
                    seen.setdefault(t, (ex, st))
            for t, (ex, st) in seen.items():
                self.exact[t].append((u['uid'], ex))
                if len(t) >= 4:
                    self.stem[t[:4]].append((t, u['uid'], st))

    def scores(self, main):
        tot = defaultdict(float)
        for w in main:
            best = {}
            for uid, sc in self.exact.get(w, ()):
                if sc > best.get(uid, 0):
                    best[uid] = sc
            if len(w) >= 4:
                for t, uid, sc in self.stem.get(w[:4], ()):
                    if t != w and uid not in best and similar(w, t):
                        best[uid] = max(best.get(uid, 0), sc)
            for uid, sc in best.items():
                tot[uid] += sc
        return tot


by_area = defaultdict(list)
for u in units:
    by_area[area_key(u['area'])].append(u)
area_index = {k: Index(v) for k, v in by_area.items()}
global_index = Index(units)


def bonus(uid, extra):
    b = 0.0
    A, P = allt[uid], pref[uid]
    for w in extra:
        if len(w) > 2:
            if w in A:
                b += 0.1
            elif len(w) >= 4 and any(similar(w, x) for x in P.get(w[:4], ())):
                b += 0.04
    return min(0.3, b)


manual = defaultdict(list)
if manual_path and os.path.exists(manual_path):
    ids = {u['id'] for u in units}
    for r in csv.DictReader(open(manual_path, encoding='utf-8'), delimiter='\t'):
        for x in re.split(r' \|\| | && ', r['unit_id'].lstrip('+')):
            if x not in ids and x not in ('-', '?') and not x.startswith('old:'):
                print('! manual rule points to unknown unit:', r['region_key'], r['name'], x)
        manual[norm(r['name'])].append((r['region_key'], norm(r['qualifier_pattern']), r['unit_id']))


def resolve(region, name, qual):
    rk = region_key(region)
    n = norm(name); q = norm(qual)
    best_m = None; plus = []
    for mrk, mqp, muid in manual.get(n, ()):
        exact = mqp.startswith('=')              # '=text' must equal the whole qualifier
        if (mrk == '*' or mrk == rk) and ((mqp == '^$' and q == '') or (exact and q == mqp[1:].strip()) or
                                          (mqp != '^$' and not exact and (mqp == '' or mqp in q))):
            if muid.startswith('+'):             # additive rule: every matching one contributes its unit
                plus.append(muid[1:]); continue
            cand = (len(mqp) + (1000 if exact else 0), mrk != '*')
            if best_m is None or cand > best_m[0]:
                best_m = (cand, muid)
    if plus:
        return ' && '.join(sorted(set(plus))), 'manual', 1.0, ''
    if best_m:
        if best_m[1] == '?':
            return '', 'none', 0, ''
        if ' || ' in best_m[1]:
            return '', 'manual-ambiguous', 1.0, best_m[1]
        return best_m[1], 'manual', 1.0, ''
    name_t, qual_t = toks(name), toks(qual)
    if not name_t:
        return '', 'empty', 0, ''
    main = [w for w in name_t if w not in GENERIC] or name_t
    extra = [w for w in name_t if w in GENERIC] + qual_t
    for scope, index in (('area', area_index.get(rk)), ('global', global_index)):
        if index is None:
            continue
        tot = index.scores(main)
        sc = []
        for uid, s in tot.items():
            s = s / (4 * len(main))
            if s >= 0.2:
                s += bonus(uid, extra)
                if s >= 0.5:
                    sc.append((s, uid))
        if not sc:
            continue
        sc.sort(reverse=True)
        top = sc[0]
        ties = [i for s, i in sc if s >= top[0] - 0.05]
        if len(ties) == 1:
            return units[top[1]]['id'], scope if top[0] >= 0.75 else scope + '-weak', round(top[0], 2), ''
        return '', scope + '-ambiguous', round(top[0], 2), ' || '.join(units[i]['id'] for i in ties[:8])
    return '', 'none', 0, ''


src = open(os.path.join(out, 'entries_raw.tsv'), encoding='utf-8')
rdr = csv.DictReader(src, delimiter='\t')
fields = rdr.fieldnames + ['unit_id', 'method', 'score', 'candidates', 'region_key']
dst = open(os.path.join(out, 'entries_units.tsv'), 'w', encoding='utf-8', newline='')
w = csv.DictWriter(dst, fieldnames=fields, delimiter='\t'); w.writeheader()
cache = {}
cnt = Counter(); todo = defaultdict(lambda: [0, set(), '', 0]); ok_keys = set(); no_area = Counter(); n_main = 0
for e in rdr:
    key = (e['region'], e['name'], e['qualifier'])
    r = cache.get(key)
    if r is None:
        r = cache[key] = resolve(*key)
    e['unit_id'], e['method'], e['score'], e['candidates'] = r
    e['region_key'] = region_key(e['region'])
    if ' && ' in e['unit_id']:                 # a manual rule says the name stands for several units at once
        for u in e['unit_id'].split(' && '):
            w.writerow(dict(e, unit_id=u))
    else:
        w.writerow(e)
    if e['flag'] == '':
        n_main += 1; cnt[e['method']] += 1
        if e['region_key'] not in by_area:
            no_area[e['region']] += 1
        if e['method'] in ('area', 'manual', 'manual-ambiguous'):
            ok_keys.add((e['region_key'], norm(e['name'])))
        else:
            t = todo[(e['region_key'], norm(e['name']), e['method'])]
            t[0] += 1
            if e['qualifier'] and len(t[1]) < 12:
                t[1].add(e['qualifier'][:40])
            t[2] = e['unit_id'] or e['candidates']; t[3] = e['score']
dst.close()
print('main entries:', n_main, dict(cnt))
print('region headings without an area:', dict(no_area.most_common(30)))
rows = sorted(todo.items(), key=lambda x: (-x[1][0], x[0]))
with open(os.path.join(out, 'name_review.tsv'), 'w', encoding='utf-8', newline='') as f:
    wr = csv.writer(f, delimiter='\t'); wr.writerow(['region_key', 'name', 'method', 'n', 'score', 'guess_or_candidates', 'qualifiers'])
    for (rk, n, m), (c, quals, guess, s) in rows:
        wr.writerow([rk, n, m, c, s, guess, ' ; '.join(sorted(quals))])
print('distinct (region, name) not resolved in their area:', len(rows), '| entries involved:', sum(v[0] for v in todo.values()),
      '| distinct resolved in area:', len(ok_keys), '| distinct lookups:', len(cache))
