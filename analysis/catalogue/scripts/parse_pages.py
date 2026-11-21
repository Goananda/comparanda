"""Parse motif pages of the Berezkin & Duvakin catalogue into flat tables.

usage: python3 -I parse_pages.py <pages_dir> <section_letter> <out_dir>
Writes <out_dir>/motifs_raw.tsv   (one row per motif page)
       <out_dir>/entries_raw.tsv  (one row per tradition name that opens a text on a page)
No story text is copied: only codes, titles, region headings and names.

A text normally opens with an underlined name.  Three things the site does not do uniformly are handled here:
- names inside round brackets count unless the bracket opens with "Ср." (compare) or "Проверить" (to check): "гур Северной
  Ганы (<u>касена</u>?)", "(включая <u>Окинаву</u>)", "(то же у <u>мехинаку</u>)" name the tradition of the text;
- a round bracket that is never closed ends where the next text starts ('; <u>name</u>');
- a text whose name is not underlined is taken when it opens with a name that is underlined elsewhere in the same region.
"""
import csv, html, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import heading_key, REGION_CODES, area_codes, codes_text

pages, letter, out = sys.argv[1], sys.argv[2].lower(), sys.argv[3]
os.makedirs(out, exist_ok=True)


def norm_name(s):
    return re.sub(r'\s+', ' ', s.lower().replace('ё', 'е')).strip()


SRC = re.compile(r"([A-ZА-ЯЁ][A-Za-zА-Яа-яёÀ-ÿ’'\-]+)(?:,? (?:[A-ZА-ЯЁ][A-Za-zА-Яа-яёÀ-ÿ’'\-]+|и др\.|et al\.))*,?\s+(1[5-9]\d\d|20[0-2]\d)")


def sources_of(seg):
    """'Surname Year' keys of the works cited for one entry (text between this name and the next one,
    abstracts in square brackets removed)"""
    for _ in range(4):
        seg2 = re.sub(r'\[[^\[\]]*\]', ' ', seg)
        if seg2 == seg:
            break
        seg = seg2
    seg = seg.split('[')[0] if seg.count('[') > seg.count(']') else seg
    txt = html.unescape(re.sub(r'<[^>]+>', '', seg))
    keys = []
    for a, y in SRC.findall(txt):
        k = f'{a} {y}'
        if k not in keys:
            keys.append(k)
        if len(keys) >= 8:
            break
    return '|'.join(keys)


def paragraphs(body):
    """(class, inner html) of every <p>; attributes may come in any order and </p> may be missing"""
    parts = re.split(r'<p\b([^>]*)>', body)
    out = []
    for k in range(1, len(parts) - 1, 2):
        m = re.search(r'class\s*=\s*"?(\w+)', parts[k])
        out.append((m.group(1) if m else '', parts[k + 1].replace('</p>', ' ')))
    return out


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


idx = open(os.path.join(pages, 'index-left.html'), 'rb').read().decode('cp1251', 'replace')
index = {}
for code, label in re.findall(r'<li><a[^>]*href="([a-z0-9_]+)\.html"[^>]*>(.*?)</a>', idx, re.I | re.S):
    index.setdefault(code.lower(), clean(label))
codes = [c for c in index if (letter == 'all' or c[0] in letter)
         and os.path.exists(os.path.join(pages, c + '.html')) and os.path.getsize(os.path.join(pages, c + '.html')) > 500]
print('pages listed for', letter, ':', sum(1 for c in index if letter == 'all' or c[0] in letter), '| on disk:', len(codes))

AREA_RE = re.compile(r'(?<![A-Za-z0-9])\(?\s*\.\d\d\.(?:[\d.\-() ]|–)*')


def split_label(label):
    """'A21. Светила заброшены в небо, A700.I, A741. .10.12.' -> (code, title, area codes string).
    Area codes are two-digit numbers between dots; Thompson numbers such as A736.1.4.1 are left in the title."""
    ms = list(AREA_RE.finditer(label))
    areas = ' '.join(m.group(0).strip() for m in ms)
    head = AREA_RE.sub(' ', label).strip()
    m2 = re.match(r'([A-Za-zА-Яа-я]+\d+[A-Za-zА-Яа-я0-9]*)\.\s*(.*)', head, re.S)
    return (m2.group(1), re.sub(r'\s+', ' ', m2.group(2)).strip()) + (areas,) if m2 else (None, head, areas)


def expand_areas(s):
    """'.11.-.13.(.15.).27.' -> (included codes, bracketed codes); a.-.b is a range"""
    inc, brk = [], []
    depth = 0
    toks = re.findall(r'\(|\)|\.\s*[-–]\s*\.|\d+', s)
    prev = None; rng = False
    for tk in toks:
        if tk == '(':
            depth += 1
        elif tk == ')':
            depth = max(0, depth - 1)
        elif tk not in '()' and not tk.isdigit():
            rng = True
        else:
            n = int(tk)
            tgt = brk if depth else inc
            if rng and prev is not None:
                tgt.extend(range(prev + 1, n + 1))
            else:
                tgt.append(n)
            prev, rng = n, False
    return inc, brk


CF_OPEN = re.compile(r'\(\s*(?:<[^>]+>\s*)*(?:[CcСс]р(?![а-яёa-z])\.?|[Пп]роверить)')


def round_spans(p, sqs):
    """(start, end, compare) of the round brackets of a paragraph (raw html), ignoring anything inside abstracts (sqs).
    'compare' is true when the bracket opens with 'Ср.' or 'Проверить'.  A bracket that is never closed ends where the
    next text starts ('; <u>'); a compare bracket that is never closed runs to the end of the paragraph."""
    mask = bytearray(len(p) + 1)
    for a_, b_ in sqs:
        for k_ in range(a_, min(b_ + 1, len(p))):
            mask[k_] = 1
    spans, depth, start, cf_now, last, i = [], 0, None, False, '', 0
    while i < len(p):
        ch = p[i]
        if ch == '<':
            if depth and not cf_now and not mask[i] and last == ';' and p.startswith('<u>', i):
                spans.append((start, i, False)); depth = 0
            j = p.find('>', i)
            i = (j + 1) if j >= 0 else len(p)
            continue
        if not mask[i]:
            if ch == '(':
                if depth == 0:
                    start = i; cf_now = bool(CF_OPEN.match(p, i))
                depth += 1
            elif ch == ')' and depth:
                depth -= 1
                if depth == 0:
                    spans.append((start, i, cf_now))
        if not ch.isspace():
            last = ch
        i += 1
    if depth and start is not None:
        spans.append((start, len(p), cf_now))
    return spans


def plain_texts(p, start, sqs, par):
    """Texts of a paragraph that carry no underlined name: (position, opening, qualifier).
    The paragraph is cut at ';' outside brackets; the opening is what stands before the abstract or the source."""
    mask = bytearray(len(p) + 1)
    for a_, b_ in list(sqs) + [(x, y) for x, y, _ in par]:
        for k_ in range(a_, min(b_ + 1, len(p))):
            mask[k_] = 1
    cuts, i = [start], start
    while i < len(p):
        ch = p[i]
        if ch == '<':
            j = p.find('>', i); i = (j + 1) if j >= 0 else len(p); continue
        if ch == '&':
            j = p.find(';', i)
            if 0 < j - i < 9:
                i = j + 1; continue
        if ch == ';' and not mask[i]:
            cuts.append(i + 1)
        i += 1
    cuts.append(len(p))
    out = []
    for a_, b_ in zip(cuts, cuts[1:]):
        seg = p[a_:b_]
        if '<u>' in seg:
            continue
        txt = clean(seg)
        m = re.match(r'\s*([^\[\]:;()]{2,90}?)\s*(?:\(([^()\[\]]{1,90})\))?\s*(\[|:|$)', txt)
        if not m:
            continue
        cands = [m.group(1).strip(' .,?"«»“”')]
        if '. ' in cands[0]:                         # 'По грибам лезут на дерево. Туника'
            cands.append(cands[0].rsplit('. ', 1)[1].strip(' .,?"«»“”'))
        for c in cands:
            if c and not re.search(r'\d', c) and len(c.split()) <= 5:
                out.append((a_, c, (m.group(2) or '').strip()))
    return out


def in_square(p):
    """spans inside square brackets (abstracts).  A closing bracket is sometimes missing on the site;
    when a new entry clearly starts ('; <u>name</u> [' or '; <u>name</u>:'), the abstract is taken as closed."""
    spans, sq, start = [], 0, None
    i = 0
    last = ''
    while i < len(p):
        ch = p[i]
        if ch == '<':
            j = p.find('>', i)
            j = j if j >= 0 else len(p) - 1
            if sq and p.startswith('<u>', i) and last == ';':
                k = p.find('</u>', i)
                tail = re.sub(r'<[^>]+>', '', p[k + 4:k + 140]) if k >= 0 else ''
                if re.match(r'\s*(\([^()\[\]]*\))?\s*(\[|:)', tail):
                    spans.append((start, i)); sq = 0
            i = j + 1
            continue
        if ch == '[':
            if sq == 0:
                start = i
            sq += 1
        elif ch == ']' and sq:
            sq -= 1
            if sq == 0:
                spans.append((start, i))
        if not ch.isspace():
            last = ch
        i += 1
    if sq and start is not None:
        spans.append((start, len(p)))
    return spans


mrows, erows, plain = [], [], []
odd_bold = Counter(); n_cont = 0; n_plain = 0; n_loose = 0; n_lin_def = 0; n_cut = 0
for code in codes:
    t = open(os.path.join(pages, code + '.html'), 'rb').read().decode('cp1251', 'replace')
    i = t.find('<div id="main">')
    body = t[i:] if i >= 0 else t
    paras = paragraphs(body)
    first_mai = next((k for k, (c, p) in enumerate(paras) if c not in ('NormalLin', 'NormalLis') and clean(p)), len(paras))
    lin = [clean(p) for c, p in paras[:first_mai] if c == 'NormalLin' and clean(p)]
    lis = [clean(p) for c, p in paras[:first_mai] if c == 'NormalLis' and clean(p)]
    if not lis and len(lin) > 1:                     # a few pages give the definition the paragraph class of the heading
        keep_, moved_ = [lin[0]], []
        for x in lin[1:]:
            (moved_ if len(re.findall(r'[А-Яа-яЁё]{3,}', AREA_RE.sub(' ', x))) >= 3 else keep_).append(x)
        if moved_:
            n_lin_def += 1
        lin, lis = keep_, moved_
    lin_txt = ' '.join(lin)
    pcode, title, areas = split_label(lin_txt)
    extra = ' '.join(m.group(0).strip() for x in lis for m in AREA_RE.finditer(x))
    areas = (areas + ' ' + extra).strip()
    lis = [AREA_RE.sub(' ', x).strip() for x in lis]
    lis = [x for x in lis if x]
    icode, ititle, iareas = split_label(index[code])
    inc, brk = (set(x) for x in expand_areas(areas))
    inc_t, brk_t, pieces = area_codes(lin_txt)            # codes written without the leading dot, with a comma or a slash
    if inc_t - inc or brk_t - brk - inc:
        n_loose += 1
        t2 = lin_txt
        for piece in pieces:
            t2 = t2.replace(piece, ' ')
        title = re.sub(r'[\s,/(]+$', '', split_label(t2)[1])
    inc |= inc_t; brk = (brk | brk_t) - inc
    areas_raw, areas = areas, codes_text(inc, brk)
    n_names = n_cf = 0; regions = []
    pos = 0
    prev_region, prev_cf = '', False
    for cls, p in paras:
        mb = re.search(r'<b>(.*?)</b>', p, re.S)
        btxt = clean(mb.group(1)).rstrip('.').strip() if mb else ''
        btxt = re.sub(r'[.,]?\s*(См|Ср)\. мотив.*$', '', btxt).strip(' /.')
        has_u = bool(re.search(r'<u>', p))
        if not (mb and heading_key(btxt) in REGION_CODES and len(clean(p[:mb.start()])) < 12):
            # the region name is not always bold: accept a known region name that opens the paragraph
            mh = re.match(r'\(?\s*((?:[CcСс]р\.\s*)?[^.\[\]:;<>]{3,60})\.', clean(p[:400]))
            if mh and heading_key(mh.group(1)) in REGION_CODES and (has_u or cls not in ('NormalLin', 'NormalLis')):
                btxt, mb, plain_head = mh.group(1).strip(), True, True
                n_plain += has_u
        if cls in ('NormalLin', 'NormalLis') and not (mb and heading_key(btxt) in REGION_CODES):
            continue                                 # the motif heading and its definition (a few texts carry this class too)
        if not has_u and not (mb and heading_key(btxt) in REGION_CODES and (mb is True or len(clean(p[:mb.start()])) < 12)):
            continue                                 # no underlined name and no region heading: not a paragraph of texts
        if mb and heading_key(btxt) in REGION_CODES and (mb is True or len(clean(p[:mb.start()])) < 12):
            region = btxt
            cf_par = bool(re.match(r'[\s(]*[cс]р[. ]', region.lower()))
            # a paragraph (or its leading part) wrapped in round brackets is a "compare" block
            if clean(p[:80] if mb is True else p[:mb.start()]).startswith('('):
                cf_par = True
            prev_region, prev_cf = region, cf_par
        else:
            # no region heading (or bold text that is not a region): the paragraph continues the previous region
            if btxt:
                odd_bold[btxt] += 1
            region, cf_par = prev_region, prev_cf or clean(p[:40]).startswith('(')   # '( Ср. ...', '( Проверить: ...'
            n_cont += 1
        regions.append(region)
        sqs = in_square(p); par = round_spans(p, sqs)
        ums = list(re.finditer(r'<u>(.*?)</u>', p, re.S))
        for k_, m in enumerate(ums):
            name = clean(m.group(1)).strip(' .,;:')
            if ':' in name or '[' in name or len(name) > 60:
                # an underline that is not closed (or opened too early) takes in the source or the text itself:
                # keep the name that stands after the last ';' or before the first ':' or '[', never the text
                tail = name.rsplit(';', 1)[-1].strip(' .,;:') if ';' in name else ''
                head = re.split(r'[:\[;]', name, 1)[0].strip(' .,;:')
                name = tail if (tail and len(tail) <= 40 and not re.search(r'[:\[\]\d]', tail)) else head
                n_cut += 1
            if not name or len(name) > 60 or not re.search(r'[A-Za-zА-Яа-яЁё]{2}', name) or re.fullmatch(r'https?', name, re.I):
                continue                             # a stray underlined letter, number or link is not a name
            seg = p[m.end():(ums[k_ + 1].start() if k_ + 1 < len(ums) else len(p))]
            inside_sq = any(a < m.start() < b for a, b in sqs)
            inside_par = any(a < m.start() < b and cf_ for a, b, cf_ in par)
            tail = clean(p[m.end():m.end() + 160])
            mq = re.match(r'\s*\(([^()\[\]]{1,90})\)', tail)
            qual = mq.group(1).strip() if mq else ''
            pos += 1
            flag = 'abstract' if inside_sq else ('cf' if (cf_par or inside_par) else '')
            erows.append(dict(motif_id=code, pos=pos, region=region, name=name, qualifier=qual, flag=flag,
                              sources=sources_of(seg)))
            if flag == '':
                n_names += 1
            elif flag == 'cf':
                n_cf += 1
        if not cf_par:
            # texts without an underlined name: kept as candidates, accepted below if the opening is a name of this region
            body_start = mb.end() if (mb not in (None, True) and heading_key(btxt) in REGION_CODES) else 0
            for at_, cand_, q_ in plain_texts(p, body_start, sqs, par):
                pos += 1
                plain.append(((code, len(regions), at_), dict(motif_id=code, pos=pos, region=region, name=cand_, qualifier=q_,
                                                               flag='', sources='')))
    # the authors' own summary list(s) of groups: comma-separated names without underlining that precede the texts
    # (pages that unite several variants have nothing but such lists, sometimes one per variant)
    n_summary = 0
    name2region = {}
    for e in erows:
        if e['motif_id'] == code:
            name2region.setdefault(norm_name(e['name']), e['region'])
    first = True
    for cls, p in paras[first_mai:]:
        txt = clean(p)
        if not txt:
            continue
        if '<u>' in p:
            break
        items, depth, cur = [], 0, ''
        for ch in txt:
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth = max(0, depth - 1)
            if ch in ',;' and depth == 0:
                items.append(cur); cur = ''
            else:
                cur += ch
        items.append(cur)
        items = [it.strip(' .') for it in items if it.strip(' .')]
        lens = sorted(len(re.sub(r'\(.*?\)|\{.*?\}', '', it)) for it in items)
        is_list = bool(items) and lens[len(lens) // 2] <= 30 and (len(items) >= 4 or (first and len(items) >= 2 and lens[-1] <= 40))
        first = False
        if not is_list:
            continue
        last_region = ''
        for it in items:
            cf = it.startswith('(')
            core = it.strip()
            if cf:                                   # an item wholly in brackets is a comparison
                core = core[1:]
                if core.endswith(')') and core.count(')') > core.count('('):
                    core = core[:-1]
            core = core.strip()
            mq = re.search(r'\(([^()]{1,90})\)', core)
            qual = mq.group(1).strip() if mq else ''
            name = re.sub(r'\{.*?\}|\[.*?\]|\(.*?\)', '', core).strip(' .,;:?')
            if '(' in name:                          # a bracket that is never closed: 'French (Upper Brittany'
                name, q2 = (x.strip(' .,;:?)') for x in name.split('(', 1))
                qual = qual or q2
            if not name or len(name) > 60:
                continue
            known = norm_name(name) in name2region
            region = name2region.get(norm_name(name), last_region)
            last_region = region
            pos += 1; n_summary += 1
            erows.append(dict(motif_id=code, pos=pos, region=region, name=name, qualifier=qual,
                              flag='summary-cf' if cf else 'summary', sources='' if known else '?'))
    mrows.append(dict(motif_id=code, page_code=pcode or '', title_ru=title, definition_ru=' '.join(lis), n_summary=n_summary,
                      area_codes=areas, area_codes_raw=areas_raw, n_areas=len(set(inc)), n_areas_bracketed=len(set(brk) - set(inc)),
                      in_digital_db=int(bool(inc)), index_title=ititle, index_area_codes=iareas,
                      n_regions=len(regions), n_names=n_names, n_cf=n_cf, bytes=len(t)))

# texts whose name is not underlined: accept the opening if it is a name underlined elsewhere in the same region
known_in = {}
for e in erows:
    if e['flag'] == '':
        known_in.setdefault(heading_key(e['region']), set()).add(norm_name(e['name']))
NOT_A_NAME = re.compile(r'^(?:кроме|если|обычно|у|ср|см|или|также|как|по|в|на|из|от|для|все|это|то|там|здесь|он|она|они)\b', re.I)


def known_parts(name, known):
    """names of the region found in an opening without underlining: the opening itself, or its parts
    ('карихона и юкуна'), or the name it ends or begins with ('восточные украинцы', 'берберы Марокко')"""
    n = norm_name(name)
    if n in known:
        return [name]
    if NOT_A_NAME.match(n):
        return []
    parts = [x.strip() for x in re.split(r',| и | или |/', name) if x.strip()]
    if len(parts) > 1 and all(norm_name(x) in known for x in parts):
        return parts
    w = name.split()
    for sub in ([w[-1], ' '.join(w[-2:]), w[0], ' '.join(w[:2])] if 2 <= len(w) <= 4 else []):
        if norm_name(sub) in known and len(sub) > 2:
            return [sub]
    return []


known_all = Counter()
for e in erows:
    if e['flag'] == '':
        known_all[norm_name(e['name'])] += 1
taken, n_plain_names, plain_pages, rejected = set(), 0, Counter(), []
for key, e in plain:
    if key in taken:
        continue
    names_ = known_parts(e['name'], known_in.get(heading_key(e['region']), ()))
    if not names_ and known_all[norm_name(e['name'])] >= 5 and not NOT_A_NAME.match(norm_name(e['name'])):
        names_ = [e['name']]                         # a name of another region ('Гуахиро' under Llanos)
    if not names_:
        rejected.append((key, e))
        continue
    taken.add(key)
    for k_, nm_ in enumerate(names_):
        e2 = dict(e, name=nm_, pos=e['pos'] + k_ / 100) if k_ else dict(e, name=nm_)
        erows.append(e2); n_plain_names += 1; plain_pages[e['motif_id']] += 1
rejected = [e for key, e in rejected if key not in taken]
with open(os.path.join(out, 'plain_rejected.tsv'), 'w', encoding='utf-8') as f:
    f.write('motif_id\tregion\topening\tqualifier\n')
    for e in rejected:
        f.write(f"{e['motif_id']}\t{e['region']}\t{e['name']}\t{e['qualifier']}\n")
for m in mrows:
    m['n_names'] += plain_pages[m['motif_id']]
order_ = {c: k for k, c in enumerate(codes)}
erows.sort(key=lambda e: (order_[e['motif_id']], e['pos']))
last_, k_ = None, 0
for e in erows:                                      # positions run 1..n on every page
    k_ = k_ + 1 if e['motif_id'] == last_ else 1
    last_ = e['motif_id']; e['pos'] = k_
print('names without underlining taken as texts:', n_plain_names, 'on', len(plain_pages), 'pages | headings with loosely written area codes:', n_loose)
print('definitions found under the heading\'s paragraph class:', n_lin_def)
print('underlined spans cut down to the name:', n_cut)

# summary names that do not occur in the text of their own page: take the region where the name is most often found elsewhere
where = {}
for e in erows:
    if e['flag'] == '' and e['region']:
        where.setdefault(norm_name(e['name']), Counter())[e['region']] += 1
n_glob = 0
for e in erows:
    if e['flag'].startswith('summary') and e['sources'] == '?':
        c = where.get(norm_name(e['name']))
        if c:
            e['region'] = c.most_common(1)[0][0]; n_glob += 1
        e['sources'] = ''
print('region names recognised without bold type:', n_plain, '| summary names placed by their usual region:', n_glob)
with open(os.path.join(out, 'motifs_raw.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(mrows[0]), delimiter='\t'); w.writeheader(); w.writerows(mrows)
with open(os.path.join(out, 'entries_raw.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(erows[0]), delimiter='\t'); w.writeheader(); w.writerows(erows)

with open(os.path.join(out, 'odd_bold.tsv'), 'w', encoding='utf-8') as f:
    for k_, v_ in odd_bold.most_common():
        f.write(f'{v_}\t{k_}\n')
print('paragraphs without a region heading (continuations):', n_cont, '| bold text that is not a region:', len(odd_bold), 'kinds;',
      dict(odd_bold.most_common(30)))
print('motif pages:', len(mrows), '| entries:', len(erows), dict(Counter(e['flag'] or 'main' for e in erows)),
      '| pages with a summary list:', sum(1 for m in mrows if m['n_summary']))
print('pages whose code differs from the file name:', [(m['motif_id'], m['page_code']) for m in mrows if m['page_code'].lower() != m['motif_id']][:12])
print('pages not in digital DB:', sum(1 for m in mrows if not m['in_digital_db']), '| pages without names:', [m['motif_id'] for m in mrows if m['n_names'] == 0][:40])
regs = Counter(e['region'] for e in erows if not e['flag'].startswith('summary'))
print('distinct region headings:', len(regs))
names = Counter(e['name'].lower() for e in erows if e['flag'] == '')
print('distinct names (main entries):', len(names))
