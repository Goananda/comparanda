"""Assemble tradition x motif pairs from the parsed catalogue pages and check them.

usage: python3 -I assemble.py <out_dir> <pages_dir> <old_groups_motifs.csv> <old_motifs.csv>
                              <old_traditions.csv> <manual_dir> <result_dir> [--prefix all_] [--cv] [--quiet]

Reads the tables written by parse_pages.py, parse_areas.py, match_units.py, match_old.py.
Names that the site-based matcher leaves open are settled with the help of the old table:
  default     an ambiguous name that in the old table nearly always means one tradition;
  learned     an unknown name that keeps co-occurring with one otherwise unexplained tradition of its area;
  correction  a name whose automatic match is contradicted by the old table in favour of another tradition.
--cv measures these rules honestly: they are learned on 4/5 of the old motifs and tested on the rest.
"""
import csv, html, os, re, sys, zlib
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import norm, area_key, heading_key, REGION_CODES

out, pages, f_old, f_oldm, f_oldt, manual_dir, res_dir = sys.argv[1:8]
opts = sys.argv[8:]
prefix = opts[opts.index('--prefix') + 1] if '--prefix' in opts else 'all_'
os.makedirs(res_dir, exist_ok=True)
BASE = 'https://www.ruthenia.ru/folklore/berezkin/'
csv.field_size_limit(10 ** 9)


def rd(path, delim='\t'):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter=delim))


umap = {r['unit_id']: r for r in rd(os.path.join(out, 'unit_map.tsv'))}
motifs = rd(os.path.join(out, 'motifs_raw.tsv'))
old_titles = {r['motif_id'].lower(): r for r in rd(f_oldm, ',')}
old_raw = defaultdict(set)
for r in rd(f_old, ','):
    old_raw[r['motif_id'].lower()].add(r['group'])
old_trads = set().union(*old_raw.values())
old_coords = {r['tradition']: (r['longitude'], r['latitude']) for r in rd(f_oldt, ',')}

# ------------------------------------------------------------------ traditions = connected components
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

unit_olds = {}
for uid, r in umap.items():
    o = r['old_tradition']
    if r['status'] == 'not-in-table' or o in ('-', ''):
        unit_olds[uid] = None
    elif o == 'NEW':
        unit_olds[uid] = []
    else:
        unit_olds[uid] = o.split(' + ')
for uid, olds in unit_olds.items():
    if olds is None:
        continue
    find('U:' + uid)
    for o in olds:
        union('U:' + uid, 'O:' + o)
for t in old_trads:
    find('O:' + t)

new_info = {}
p = os.path.join(manual_dir, 'new_units_en.tsv')
if os.path.exists(p):
    new_info = {r['unit_id']: r for r in rd(p)}

comp_members = defaultdict(lambda: ([], []))
for x in list(parent):
    comp_members[find(x)][0 if x.startswith('O:') else 1].append(x[2:])
comp_label, comp_kind = {}, {}
for c, (olds, us) in comp_members.items():
    olds.sort(); us.sort()
    if olds:
        comp_label[c] = ' + '.join(olds)
        comp_kind[c] = 'old' if len(olds) == 1 else 'old-merged'
    else:
        comp_label[c] = (new_info.get(us[0], {}).get('name_en')
                         or 'NEW: ' + re.split(r'[(:;,]', umap[us[0]]['unit_text'])[0].strip())
        comp_kind[c] = 'new'
EXTRA_AREAS = {'Aragon': 'южная европа', 'Attikamek': 'средний запад', 'Palikur': 'гвиана'}
comp_areas = defaultdict(set)
for uid, r in umap.items():
    if unit_olds.get(uid) is not None:
        comp_areas[find('U:' + uid)].add(area_key(r['area']))
for o, a in EXTRA_AREAS.items():
    if 'O:' + o in parent:
        comp_areas[find('O:' + o)].add(a)


def comp_of_unit(uid):
    if uid.startswith('old:'):
        return find('O:' + uid[4:])
    if unit_olds.get(uid) is None:
        return None
    return find('U:' + uid)


old = {m: {find('O:' + t) for t in ts} for m, ts in old_raw.items()}

# ------------------------------------------------------------------ entries
class E:
    __slots__ = ('m', 'pos', 'region', 'name', 'qual', 'flag', 'unit', 'method', 'cands', 'rk', 'key',
                 'base', 'comp', 'ccomps', 'how', 'fc', 'fcs', 'src')

AUTO = {'area', 'area-weak', 'global', 'global-weak'}
CONF = AUTO | {'manual', 'group'}
WEAK = {'area-weak', 'global-weak'}
entries = []
with open(os.path.join(out, 'entries_units.tsv'), encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        e = E()
        e.m = r['motif_id'].lower(); e.pos = r['pos']; e.region = r['region']; e.name = r['name']; e.qual = r['qualifier']
        e.flag = r['flag']; e.unit = r['unit_id']; e.method = r['method']; e.cands = r['candidates']; e.rk = r['region_key']
        e.key = (e.rk, norm(e.name)); e.comp = None; e.ccomps = (); e.how = ''; e.fc = None; e.fcs = ()
        e.src = tuple(x for x in (r.get('sources') or '').split('|') if x)
        if e.flag in ('', 'summary'):
            if e.unit == '-':
                e.base = 'not-a-tradition'
            else:
                cands = [e.unit] if e.unit else [c for c in e.cands.split(' || ') if c]
                comps = {comp_of_unit(u) for u in cands}
                real = comps - {None}
                if not cands:
                    e.base = 'unresolved'
                elif not real:
                    e.base = 'not-in-table'
                elif len(real) == 1 and None not in comps:
                    e.comp = next(iter(real))
                    e.base = e.method if len(cands) == 1 else 'group'
                else:
                    e.base = 'ambiguous'; e.ccomps = tuple(sorted(real))
        else:
            e.base = 'compare-only' if e.flag in ('cf', 'summary-cf') else 'inside-abstract'
        entries.append(e)
both = [e for e in entries if e.flag in ('', 'summary')]
main = [e for e in both if e.flag == '']
main_by = defaultdict(list)
for e in main:
    main_by[e.m].append(e)
AMBK = {e.key for e in main if e.base == 'ambiguous'}
SITE_SRC = defaultdict(Counter)        # (name key, cited work) -> tradition, from entries settled by the site itself
for e in main:
    if e.key in AMBK and e.base in CONF and e.comp:
        for x in e.src:
            SITE_SRC[(e.key, x)][e.comp] += 1
motif_ids = [m['motif_id'] for m in motifs]
common = sorted(m for m in motif_ids if m in old)
print('motifs parsed:', len(motifs), '| in the old table too:', len(common), '| main entries:', len(main),
      dict(Counter(e.base for e in main)))

# ------------------------------------------------------------------ inclusion rules stated in definitions
CODE = r'[A-Za-zА-Яа-я]\d+[A-Za-zА-Яа-я0-9]*'
LAT = str.maketrans('АВСЕНКМОРТХавсенкмортх', 'ABCEHKMOPTXabcehkmoptx')
idset = set(motif_ids)
include = defaultdict(set)
unknown_refs = Counter()
for m in motifs:
    d = m['definition_ru']
    mid = m['motif_id']
    for mm in re.finditer(r'включен[ыао]?\s+(?:также\s+)?(?:все\s+)?(?:тексты\s+с\s+)?мотив(?:ы|ами|ов)?\s+(' + CODE + r')\s*[–—-]\s*(' + CODE + ')', d):
        a, b = (x.translate(LAT).lower() for x in mm.groups())
        stem = os.path.commonprefix([a, b])
        lo, hi = a[len(stem):len(stem) + 1], b[len(stem):len(stem) + 1]
        for x in motif_ids:
            if x != mid and x.startswith(stem) and len(x) > len(stem) and lo <= x[len(stem)] <= hi:
                include[mid].add(x)
    for mm in re.finditer(r'(?:включает|включены|включены также|входят)\s+(?:также\s+)?(?:все\s+)?тексты\s+(?:с\s+)?мотив(?:ом|ами|а|ов)\s+((?:' + CODE + r'(?:\s*,\s*|\s+и\s+)?)+)', d):
        for x in re.findall(CODE, mm.group(1)):
            x = x.translate(LAT).lower()
            if x in idset and x != mid:
                include[mid].add(x)
            elif x != mid:
                unknown_refs[x] += 1
    for mm in re.finditer(r'[Вв]ключая\s+мотив(?:ы)?\s+((?:' + CODE + r'(?:\s*,\s*|\s+и\s+)?)+)', d):
        for x in re.findall(CODE, mm.group(1)):
            x = x.translate(LAT).lower()
            if x in idset and x != mid:
                include[mid].add(x)
    for mm in re.finditer(r'[Сс]м\.\s+(?:также\s+)?мотивы\s+(' + CODE + r')\s*[-–—]\s*(' + CODE + r')\s*[,;]\s*(?:совокупные данные|в корреляционных таблицах они включены)', d):
        a, b = (x.translate(LAT).lower() for x in mm.groups())
        if a in idset and b in idset:
            i, j = sorted((motif_ids.index(a), motif_ids.index(b)))
            include[mid].update(x for x in motif_ids[i:j + 1] if x != mid)
# transitive closure
changed = True
while changed:
    changed = False
    for m_, subs in include.items():
        add = set().union(*[include.get(x, set()) for x in subs]) - subs - {m_}
        if add:
            subs |= add; changed = True
print('inclusion rules:', len(include), 'motifs include', sum(len(v) for v in include.values()), 'others',
      '| unknown codes in rules:', dict(unknown_refs.most_common(8)))

# ------------------------------------------------------------------ learning from the old table
def top2(counter):
    mc = counter.most_common(2)
    return mc[0][0], mc[0][1], (mc[1][1] if len(mc) > 1 else 0.0)


def learn(train):
    amb_default, unres_map, corr = {}, {}, {}
    R = {}
    for m in train:
        R[m] = {e.comp for e in main_by[m] if e.base in CONF and e.comp}
        for e in main_by[m]:
            if e.base == 'ambiguous':
                R[m].update(e.ccomps)
    # 1. unknown names
    info = {}
    for rnd in range(3):
        votes = defaultdict(Counter); occ = Counter()
        for m in train:
            X = old[m] - R[m]
            seen = set()
            for e in main_by[m]:
                if e.base == 'unresolved' and e.key not in unres_map and e.key not in seen:
                    seen.add(e.key); occ[e.key] += 1
                    c = [x for x in X if e.rk in comp_areas[x]]
                    for x in c:
                        votes[e.key][x] += 1.0 / len(c)
        new = 0
        for K, vc in votes.items():
            c, v, v2 = top2(vc)
            if v >= 3 and v / occ[K] >= 0.6 and v >= 2 * v2:
                unres_map[K] = c; info[K] = ('learned', occ[K], round(v, 1)); new += 1
        if not new:
            break
        for m in train:
            for e in main_by[m]:
                if e.base == 'unresolved' and e.key in unres_map:
                    R[m].add(unres_map[e.key])
    # 2. ambiguous names
    votes = defaultdict(Counter)
    for m in train:
        seen = set()
        for e in main_by[m]:
            if e.base == 'ambiguous' and e.key not in seen:
                have = [c for c in e.ccomps if c in old[m]]
                if len(have) == 1:
                    seen.add(e.key); votes[e.key][have[0]] += 1
    for K, vc in votes.items():
        c, v, _ = top2(vc)
        if v >= 3 and v / sum(vc.values()) >= 0.8:
            amb_default[K] = c; info[K] = ('default', sum(vc.values()), v)
    # 2b. the cited work tells which tradition an ambiguous name stands for
    svotes = defaultdict(Counter)
    for k, vc in SITE_SRC.items():
        svotes[k].update(vc)
    for m in train:
        for e in main_by[m]:
            if e.base == 'ambiguous' and e.src:
                have = [c for c in e.ccomps if c in old[m]]
                if len(have) == 1:
                    for x in e.src:
                        svotes[(e.key, x)][have[0]] += 1
    # 3. automatic matches that the old table contradicts
    stats = defaultdict(lambda: [0, 0])
    for m in train:
        seen = set()
        for e in main_by[m]:
            if e.base in AUTO and e.key not in seen:
                seen.add(e.key)
                s = stats[e.key]; s[0] += 1; s[1] += e.comp in old[m]
    bad = {K for K, (n, h) in stats.items() if n >= 4 and h / n <= 0.25}
    votes = defaultdict(Counter)
    for m in train:
        X = old[m] - R[m]
        seen = set()
        for e in main_by[m]:
            if e.key in bad and e.base in AUTO and e.key not in seen:
                seen.add(e.key)
                c = [x for x in X if e.rk in comp_areas[x]]
                for x in c:
                    votes[e.key][x] += 1.0 / len(c)
    for K, vc in votes.items():
        c, v, v2 = top2(vc)
        n = stats[K][0]
        if v >= 3 and v / n >= 0.5 and v >= 2 * v2:
            corr[K] = c; info[K] = ('correction', n, round(v, 1))
    return amb_default, unres_map, corr, info, svotes


def apply(maps, settle):
    """final tradition(s) of every entry.  One underlined name can stand for several traditions
    (e.g. 'Selkup' followed by texts of both northern and southern Selkup), hence e.fcs is a tuple."""
    amb_default, unres_map, corr = maps[:3]; svotes = maps[4]
    ssum = defaultdict(set)            # traditions named unambiguously in the authors' summary list of the page
    samb = defaultdict(set)            # names that stay ambiguous in the summary list itself
    for e in both:
        if e.flag == 'summary':
            if e.base in AUTO and e.key in corr:
                ssum[e.m].add(corr[e.key])
            elif e.base in CONF:
                ssum[e.m].add(e.comp)
            elif e.base == 'ambiguous':
                samb[e.m].add(e.key)
    for e in both:
        b = e.base
        if b in AUTO and e.key in corr:
            e.fcs, e.how = (corr[e.key],), 'correction'
        elif b in CONF:
            e.fcs, e.how = (e.comp,), b
        elif b == 'ambiguous' and e.key not in samb[e.m] and any(c in ssum[e.m] for c in e.ccomps):
            e.fcs, e.how = tuple(c for c in e.ccomps if c in ssum[e.m]), 'summary'
        elif b == 'ambiguous':
            dec = []
            for x in e.src:
                vc = Counter({c: v for c, v in svotes.get((e.key, x), {}).items() if c in e.ccomps})
                if vc:
                    c, v, _ = top2(vc)
                    if v >= 2 and v / sum(vc.values()) >= 0.8 and c not in dec:
                        dec.append(c)
            how = 'source' if dec else ''
            if not dec and e.key in amb_default:
                dec, how = [amb_default[e.key]], 'default'
            if e.m in settle:
                have = [c for c in e.ccomps if c in old[e.m] and c not in dec]
                if have:
                    dec += have; how = (how + '+old-table') if how else 'old-table'
            e.fcs, e.how = tuple(dec), how or 'ambiguous'
        elif b == 'unresolved' and e.key in unres_map:
            e.fcs, e.how = (unres_map[e.key],), 'learned'
        else:
            e.fcs, e.how = (), b
        e.fc = e.fcs[0] if e.fcs else None
    # A name that stands only in the authors' list and merely resembles the name of a unit is not counted when the
    # page has texts of its own: three out of four such pairs contradict the old table (see --diag-summary).
    # The match is kept when the texts of the page name the same tradition, or when the same name stands for it
    # in the texts of other pages.
    txt = defaultdict(set); est = defaultdict(set)
    for e in main:
        txt[e.m].update(e.fcs); est[e.key[1]].update(e.fcs)
    for e in both:
        if e.flag == "summary" and e.method in WEAK and e.fcs and main_by.get(e.m):
            keep = tuple(c for c in e.fcs if c in txt[e.m] or c in est[e.key[1]])
            if len(keep) != len(e.fcs):
                e.fcs = keep; e.fc = keep[0] if keep else None
                if not keep:
                    e.how = 'weak-in-list'


def pairs_now():
    own = defaultdict(set)
    for e in both:                     # text of the page and the authors' summary list
        for c in e.fcs:
            own[e.m].add(c)
    P = {m: set(own.get(m, ())) for m in motif_ids}
    via = defaultdict(dict)
    for m, subs in include.items():
        for x in sorted(subs):
            for c in own.get(x, ()):
                if c not in P[m]:
                    P[m].add(c); via[m][c] = x
    return P, own, via


def score(P, ms):
    tp = fn = fp = 0
    for m in ms:
        a = len(P[m] & old[m]); tp += a; fn += len(old[m]) - a; fp += len(P[m]) - a
    return tp, fn, fp


def text_only():
    T = defaultdict(set)
    for e in main:
        T[e.m].update(e.fcs)
    return T


NOMAPS = ({}, {}, {}, {}, {})
apply(NOMAPS, set())
P0, _, _ = pairs_now()
tp, fn, fp = score(P0, common)
print(f'old table, {len(common)} common motifs, {tp + fn} pairs. Site-based matching alone: found {tp} ({tp / (tp + fn):.1%}), '
      f'site-only pairs {fp}')
if '--cv' in opts:
    TP = FN = FP = 0
    for f in range(5):
        test = [m for m in common if zlib.crc32(m.encode()) % 5 == f]
        train = [m for m in common if zlib.crc32(m.encode()) % 5 != f]
        apply(learn(train), set())
        Pf, _, _ = pairs_now()
        a, b, c = score(Pf, test); TP += a; FN += b; FP += c
    print(f'   with rules learned from the old table, 5-fold cross-validation (tested on motifs not used for learning): '
          f'found {TP} ({TP / (TP + FN):.1%}), site-only pairs {FP}')
maps = learn(common)
apply(maps, set(common))
P, own, via = pairs_now()
T_ = text_only()
a_ = sum(len(T_[m] & old[m]) for m in common)
print(f'   (of the old pairs, {a_} are found in the page texts alone; the rest of those found come from summary lists and inclusion rules)')
tp, fn, fp = score(P, common)
print(f'   final table (rules learned on all old motifs, remaining ambiguity settled by the old table): found {tp} '
      f'({tp / (tp + fn):.1%}), not found {fn}, site-only pairs {fp}')
print('   rules:', dict(Counter(v[0] for v in maps[3].values())), '| entries by resolution:', dict(Counter(e.how for e in main)))

# why old pairs are missing
why = Counter()
for m in common:
    amb = set()
    for e in main_by[m]:
        if e.how == 'ambiguous':
            amb.update(e.ccomps)
    regs = defaultdict(list)
    for e in main_by[m]:
        regs[e.rk].append(e)
    for c in old[m] - P[m]:
        if c in amb:
            why['among candidates of an ambiguous name'] += 1; continue
        names = [e for a in comp_areas[c] for e in regs.get(a, ())]
        if not names:
            why['its area is absent from the page'] += 1
        elif all(e.fcs and any(c in old[m] for c in e.fcs) for e in names):
            why['area present, every name there matches another old pair'] += 1
        else:
            why['area has names that do not match the old table'] += 1
print('   old pairs not found:', dict(why))

# ------------------------------------------------------------------ authors' summary lists vs the text
S, B = defaultdict(set), defaultdict(set)
s_unres = 0
for e in both:
    if e.flag == 'summary':
        if e.fcs:
            S[e.m].update(e.fcs)
        elif e.how in ('unresolved', 'ambiguous'):
            s_unres += 1
for e in main:
    B[e.m].update(e.fcs)
si = sum(len(S[m] & B[m]) for m in S); so = sum(len(S[m] - B[m]) for m in S)
if si + so:
    print(f'summary lists on {len(S)} pages: traditions named there {si + so}; found in the text below {si} ({si / (si + so):.1%}); '
          f'summary names left open {s_unres}')

# how reliable are traditions that only the summary list gives?  (share confirmed by the old table, by kind of match)
if '--diag-summary' in opts:
    cset = set(common); dg = defaultdict(lambda: [0, 0, 0]); seen = set()
    for e in both:
        if e.flag != 'summary' or not e.fcs:
            continue
        for c in e.fcs:
            if c in B[e.m] or (e.m, c) in seen:
                continue
            seen.add((e.m, c))
            k = (e.method, bool(main_by.get(e.m)))
            dg[k][0] += 1
            if e.m in cset:
                dg[k][1] += 1; dg[k][2] += c in old[e.m]
    for k, (n, nc, no) in sorted(dg.items(), key=lambda x: -x[1][0]):
        print(f'   summary-only pairs, match {k[0]:16s} page has text: {str(k[1]):5s} pairs {n:5d} | on common motifs {nc:5d}, in the old table {no:5d} ({no / max(1, nc):.0%})')

# ------------------------------------------------------------------ area codes of the headings vs regions with names
code_of = REGION_CODES


def expand(s):
    inc, brk, depth, prev, rng = [], [], 0, None, False
    for tk in re.findall(r'\(|\)|\.\s*[-–]\s*\.|\d+', s):
        if tk == '(':
            depth += 1
        elif tk == ')':
            depth = max(0, depth - 1)
        elif not tk.isdigit():
            rng = True
        else:
            n = int(tk); tgt = brk if depth else inc
            tgt.extend(range(prev + 1, n + 1) if (rng and prev is not None and n - prev < 70) else [n])
            prev, rng = n, False
    return set(inc), set(brk)


reg_main = defaultdict(set)
unknown_regions = Counter()
for e in main:
    c = code_of.get(heading_key(e.region))
    if c is None:
        unknown_regions[e.region] += 1
    else:
        reg_main[e.m].add(c)
for m_, subs in include.items():
    for x in subs:
        reg_main[m_] |= reg_main.get(x, set())
n_db = exact = hdr = miss_n = extra_n = 0
for m in motifs:
    if m['in_digital_db'] != '1':
        continue
    inc, _ = expand(m['area_codes']); inc.discard(58)
    got = reg_main[m['motif_id']]
    n_db += 1; hdr += len(inc); miss_n += len(inc - got); extra_n += len(got - inc); exact += inc == got
print(f'area codes: {n_db} motifs of the digital DB, {hdr} areas in headings; exact match on {exact} pages; '
      f'areas without names {miss_n}; areas with names missing from the heading {extra_n}')
if unknown_regions:
    print('   region headings without a code:', len(unknown_regions), 'kinds,', sum(unknown_regions.values()), 'entries;',
          dict(unknown_regions.most_common(25)))

# ------------------------------------------------------------------ result tables
# English text as it stands under the same code on the site's English list or in the 2021 table; motif_texts.py, run next,
# checks which entry really describes each motif and sets the final English and Russian texts.
eng = {}
t = open(os.path.join(pages, 'eng.html'), 'rb').read().decode('cp1251', 'replace')
clean = lambda s: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
for code, title, desc in re.findall(r'<p class="NormalMai"><b>\s*([^.<]{1,12})\.\s*(.*?)</b>(.*?)</p>', t, re.S):
    eng.setdefault(norm(code).translate(LAT).replace(' ', ''), (clean(title).rstrip('.'), clean(desc)))

n_open = Counter(e.m for e in main if e.how in ('unresolved', 'ambiguous'))
db = {m['motif_id'] for m in motifs if m['in_digital_db'] == '1'}
mrows = []
for m in motifs:
    mid = m['motif_id']
    if mid in eng:
        te, de, src = eng[mid][0], eng[mid][1], 'site (English list)'
    elif mid in old_titles:
        te, de, src = old_titles[mid]['title'], old_titles[mid]['description'], 'old database'
    else:
        te, de, src = '', '', ''
    inc, _ = expand(m['area_codes'])
    title_ru = re.sub(r'\s*(\(\.[\d.,\- ]+\)|\[\s*\])\s*$', '', m['title_ru']).strip()
    mrows.append(dict(motif_id=mid, title_en=te, title_en_source=src, description_en=de, title_ru=title_ru,
                      definition_ru=m['definition_ru'], in_old_database=int(mid in old), in_digital_db=m['in_digital_db'],
                      n_traditions=len(P[mid]), n_traditions_old=len(old_raw.get(mid, ())), n_names_on_page=m['n_names'],
                      n_names_open=n_open[mid], n_compare_entries=m['n_cf'], includes=' '.join(sorted(include.get(mid, ()))),
                      area_codes=m['area_codes'], n_areas=len(inc - {58}), url=BASE + mid + '.html'))


def wr(name, rows, fields=None):
    with open(os.path.join(res_dir, prefix + name), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)


wr('motifs.csv', mrows)

agg = defaultdict(lambda: [0, Counter(), Counter(), Counter()])
for e in both:
    for c_ in e.fcs:
        a = agg[(c_, e.m)]
        if e.flag == 'summary':
            a[2]['summary-list'] += 1
        else:
            a[0] += 1; a[2][e.how] += 1
        if len(a[3]) < 6:
            a[3][e.name] += 1
        if e.unit and e.unit != '-' and e.how in CONF:
            a[1][e.unit] += 1
for m, d in via.items():
    for c, x in d.items():
        agg[(c, m)][2]['included-from-' + x] += 1
prow = []
for (c, mid), a in sorted(agg.items(), key=lambda x: (comp_label[x[0][0]].lower(), x[0][1])):
    prow.append(dict(tradition=comp_label[c], motif_id=mid, tradition_status=comp_kind[c],
                     in_old_pairs=(int(c in old[mid]) if mid in old else ''), motif_in_old_database=int(mid in old),
                     motif_in_digital_db=int(mid in db), n_entries=a[0], names_on_page='; '.join(sorted(a[3])),
                     units='; '.join(sorted(a[1])), how='; '.join(f'{k}:{v}' for k, v in sorted(a[2].items()))))
wr('pairs.csv', prow)

erow = []
for e in entries:
    if e.flag.startswith('summary'):
        continue
    erow.append(dict(motif_id=e.m, order=e.pos, region=e.region, name=e.name, qualifier=e.qual,
                     kind={'': 'main', 'cf': 'compare', 'abstract': 'inside-abstract'}[e.flag],
                     tradition=' | '.join(comp_label[c] for c in e.fcs), resolution=e.how or e.base,
                     unit_id=e.unit if e.unit != '-' else '', unit_candidates=e.cands if not e.unit else ''))
wr('entries.csv', erow)

used_units = Counter(e.unit for e in main if e.fc and e.unit and e.how in CONF)
urow = []
for uid, r in umap.items():
    c = comp_of_unit(uid)
    urow.append(dict(unit_id=uid, area_ru=r['area'], no=r['no'], unit_ru=r['unit_text'], in_table=int(r['status'] != 'not-in-table'),
                     tradition=comp_label[c] if c else '', relation_to_old=r['relation'], negligible_data=r['italic'],
                     n_entries=used_units[uid]))
wr('units.csv', urow)

n_mot = Counter(); n_mot_db = Counter()
for mid, cs in P.items():
    for c in cs:
        n_mot[c] += 1
        if mid in db:
            n_mot_db[c] += 1
n_old = Counter(c for m in old for c in old[m])
trow = []
for c in sorted(comp_label, key=lambda x: comp_label[x].lower()):
    olds, us = comp_members[c]
    if olds:
        xy = [old_coords[o] for o in olds if o in old_coords and old_coords[o][0] != '']
        lon = round(sum(float(x) for x, _ in xy) / len(xy), 3) if xy else ''
        lat = round(sum(float(y) for _, y in xy) / len(xy), 3) if xy else ''
        src = 'old database' if xy else ''
    else:
        r = new_info.get(us[0], {})
        lon, lat, src = r.get('longitude', ''), r.get('latitude', ''), ('assigned here, approximate' if r.get('longitude') else '')
    trow.append(dict(tradition=comp_label[c], status=comp_kind[c], n_motifs=n_mot_db[c], n_motifs_all_pages=n_mot[c],
                     n_motifs_old=n_old[c], longitude=lon, latitude=lat, coordinates_source=src,
                     areas='; '.join(sorted(comp_areas[c])), units='; '.join(us)))
wr('traditions.csv', trow)

opn = defaultdict(lambda: [0, set(), set(), ''])
for e in main:
    if e.how in ('unresolved', 'ambiguous'):
        v = opn[(e.region, e.name, e.how)]
        v[0] += 1
        if len(v[1]) < 15:
            v[1].add(e.m)
        if e.qual and len(v[2]) < 8:
            v[2].add(e.qual[:40])
        if e.ccomps:
            v[3] = ' | '.join(comp_label[c] for c in e.ccomps)
orow = [dict(region=k[0], name=k[1], problem=k[2], n_entries=v[0], motifs=' '.join(sorted(v[1])),
             qualifiers='; '.join(sorted(v[2])), candidates=v[3]) for k, v in sorted(opn.items(), key=lambda x: -x[1][0])]
wr('open_names.csv', orow, ['region', 'name', 'problem', 'n_entries', 'motifs', 'qualifiers', 'candidates'])

lrow = [dict(region_key=K[0], name=K[1], rule=v[0], tradition=comp_label[(maps[0].get(K) or maps[1].get(K) or maps[2].get(K))],
             n_old_motifs=v[1], votes=v[2]) for K, v in sorted(maps[3].items(), key=lambda x: (x[1][0], -x[1][1]))]
wr('learned_rules.csv', lrow, ['region_key', 'name', 'rule', 'tradition', 'n_old_motifs', 'votes'])

st = Counter(comp_kind[c] for c in n_mot)
print(f'result: motifs {len(mrows)} (in digital DB {len(db)}), pairs {len(prow)} (digital-DB motifs {sum(1 for r in prow if r["motif_in_digital_db"])}), '
      f'traditions with pairs {len(n_mot)} {dict(st)}')
print('   pairs of old motifs absent from the old table:', sum(1 for r in prow if r['in_old_pairs'] == 0),
      '| pairs of motifs absent from the old table:', sum(1 for r in prow if not r['motif_in_old_database']),
      '| open names:', sum(v[0] for v in opn.values()), 'entries,', len(opn), 'distinct',
      '| motifs without an English title:', sum(1 for m in mrows if not m['title_en']))
if '--quiet' not in opts:
    ck = sorted(((v[1], K, comp_label[maps[2][K]]) for K, v in maps[3].items() if v[0] == 'correction'), reverse=True)[:40]
    print('   corrections (n old motifs, name -> tradition):', [(n, K[1], t) for n, K, t in ck])
    lk = sorted(((v[1], K, comp_label[maps[1][K]]) for K, v in maps[3].items() if v[0] == 'learned'), reverse=True)[:40]
    print('   learned (n old motifs, name -> tradition):', [(n, K[1], t) for n, K, t in lk])
