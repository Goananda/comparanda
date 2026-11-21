"""Finish the motif table: the English and the Russian text shown for every motif.

usage: python3 -I motif_texts.py <pages_dir> <old motifs.csv> <manual_dir> <result_dir> <prefix>
Rewrites <result_dir>/<prefix>motifs.csv (written by assemble.py) with these text columns:

  title_en, description_en          the English version
  title_en_source, description_en_source
        site (English list)             the entry of the site's English list under the same code
        site (English list, entry X)    the entry listed under another code X (the list keeps an earlier numbering there)
        old database                    the authors' 2021 table
        translated from Russian         translated from the Russian page for this table
  title_ru, description_ru          the Russian version: a translation of the English version wherever the English text is the
                                    authors' own, and the text of the Russian page wherever the English was translated from it
  title_ru_source, description_ru_source      'translated from English' or 'site'
  title_ru_site, definition_ru_site the Russian page as it stands on the site

Manual tables (manual_dir): english_fixes.tsv (which entry of the English list describes which motif), en_from_ru.tsv and
ru_from_en.tsv (the translations), text_fixes.tsv (single corrected fields; description_ru_cut drops the list of traditions
that follows a few Russian definitions).
"""
import csv, html, os, re, sys
from collections import Counter

pages, f_old, man, res, prefix = sys.argv[1:6]
csv.field_size_limit(10 ** 9)
path = os.path.join(res, prefix + 'motifs.csv')
rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
tsv = lambda n: list(csv.DictReader(open(os.path.join(man, n), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))

# ---- sources of English text
LAT = str.maketrans('АВЕКМНОРСТХаеорсух', 'ABEKMHOPCTXaeopcyx')
strip_tags = lambda s: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
t = open(os.path.join(pages, 'eng.html'), 'rb').read().decode('cp1251', 'replace')
LIST = {}
for code, title, desc in re.findall(r'<p class="NormalMai"><b>\s*([^.<]{1,12})\.\s*(.*?)</b>(.*?)</p>', t, re.S):
    LIST.setdefault(strip_tags(code).translate(LAT).replace(' ', '').lower(), []).append((strip_tags(title), strip_tags(desc)))
OLD = {r['motif_id'].lower(): (r['title'], r['description']) for r in csv.DictReader(open(f_old, encoding='utf-8-sig'))}
EN = {r['motif_id']: (r['title_en'], r['description_en']) for r in tsv('en_from_ru.tsv')}
RU = {r['source']: (r['title_ru'], r['description_ru']) for r in tsv('ru_from_en.tsv')}
FIX = {r['motif_id']: r for r in tsv('english_fixes.tsv')}
TFIX = {(r['motif_id'], r['field']): r['value'] for r in tsv('text_fixes.tsv')}

CYR = re.compile('[А-Яа-яЁё]')


LOOK = str.maketrans('АВЕКМНОРСТХаеорсухіІ', 'ABEKMHOPCTXaeopcyxiI')
KEYS = str.maketrans('йцукенгшщзфывапролдячсмитьЙЦУКЕНГШЩЗФЫВАПРОЛДЯЧСМИТЬ', 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')


def latin(s):
    """stray Cyrillic in an English text: look-alike letters inside a word, or a word typed in the Russian keyboard layout"""
    cyr, lat = len(CYR.findall(s)), len(re.findall('[A-Za-z]', s))
    if not cyr or cyr > 0.15 * (cyr + lat): return s
    def word(m):
        w = m.group(0)
        if re.search('[A-Za-z]', w) or len(w) == 1: return w.translate(LOOK)
        return w.translate(KEYS)
    return re.sub('[A-Za-zА-Яа-яЁё]+', word, s)


def en_clean(s, title=False):
    s = latin(' '.join(s.replace(chr(173), '').split()))
    s = re.sub(r'\s+([.,;:!?)])', r'\1', s)
    s = re.sub(r'\.{2}$', '.', s)
    if title:
        s = s.rstrip('. ')
        if s.count('(') > s.count(')') and s.startswith('('): s = s[1:]
    elif not re.search('[A-Za-z]', s):
        s = ''
    return s


CODE = r'(?:(?:ATU|AaTh|AA|AT|Th)\.?\s*)?[A-Z]?\d[0-9A-Za-z.*+]*'
SUF = re.compile(r'(?:\s*[,.;/]+\s*|\s+(?=\(|ATU|AaTh|AA |Th ))\(?\s*' + CODE + r'(?:[\s,;/().\-]+(?:' + CODE + r')?)*\)?[\s,.;/\-]*$')


def ru_title(s):
    """the title of a Russian page without the index numbers and area codes that follow it"""
    s = ' '.join(s.replace(chr(173), '').split())
    for _ in range(3):
        s = SUF.sub('', s)
        s = re.sub(r'[\s,.;]+$', '', s) if not s.endswith(('?', '!')) else s
        s = re.sub(r'\s*[,.]\s*$', '', s)
    s = re.sub(r'\s*\(\s*\)$', '', s)
    return typo(s)


def typo(s):
    s = re.sub(r'\s+[–-]\s*|\s*[–]\s+', ' — ', s)
    s = re.sub(r'\bт\.\s?([пдек])\.', r'т. \1.', s)
    return ' '.join(s.split())


BRACKETS = re.compile(r'\s*См\. мотивы, указанные в квадратных скобках\.?|\s*Если не указано, что «шакал», то протагонист [–—] лиса\.')


def ru_def(s):
    s = ' '.join(s.replace(chr(173), '').split())
    s = BRACKETS.sub('', s).strip()
    return typo(s) if CYR.search(s) else ''


def english(src, mid):
    """(title, description) of a source key; None if the key has nothing"""
    if src == 'ru': return EN.get(mid)
    kind, _, code = src.partition(':')
    if kind == 'list':
        code, _, n = code.partition('#')
        e = LIST.get(code, [])
        k = int(n) - 1 if n else 0
        return e[k] if k < len(e) else None
    if kind == 'old': return OLD.get(code)
    raise SystemExit('unknown source ' + src)


def label(src, mid):
    if src == 'ru': return 'translated from Russian'
    kind, _, code = src.partition(':')
    if kind == 'old': return 'old database'
    return 'site (English list)' if code == mid else f'site (English list, entry {code})'


out, stat, warn = [], Counter(), []
for m in rows:
    mid = m['motif_id']
    t_site = m.get('title_ru_site', m.get('title_ru', '')); d_site = m.get('definition_ru_site', m.get('definition_ru', ''))
    default = 'list:' + mid if mid in LIST else ('old:' + mid if mid in OLD else 'ru')
    fx = FIX.get(mid, {})
    src = {f: (default if fx.get(f, '=') in ('=', '') else fx[f]) for f in ('title', 'description')}
    val = {}
    for k, f in enumerate(('title', 'description')):
        e = english(src[f], mid)
        v = en_clean(e[k], f == 'title') if e else ''
        if (not v or CYR.search(v)) and src[f] != 'ru':          # nothing usable in the authors' English: use the translation
            if v: warn.append(f'{mid}: Cyrillic in the English {f} ({src[f]})')
            e2 = EN.get(mid); v2 = en_clean(e2[k], f == 'title') if e2 else ''
            v, src[f] = (v2, 'ru') if v2 else ('', src[f])
        val[f] = v
    title_en = TFIX.get((mid, 'title_en'), val['title']); desc_en = TFIX.get((mid, 'description_en'), val['description'])
    # Russian: the translation of the authors' English, or the page
    rus, rsrc = {}, {}
    for k, f in enumerate(('title', 'description')):
        site = ru_title(t_site) if f == 'title' else ru_def(d_site)
        cut = TFIX.get((mid, 'description_ru_cut'))
        if f == 'description' and cut:
            if cut not in site: warn.append(f'{mid}: the text to cut is not in the Russian definition')
            else: site = site[:site.index(cut)].strip()
        tr = RU.get(src[f], ('', ''))[k] if src[f] != 'ru' and val[f] else ''
        if src[f] != 'ru' and val[f] and not tr and m.get('in_digital_db') == '1' and int(m.get('n_traditions') or 0) > 0:
            warn.append(f'{mid}: no Russian translation of the English {f} ({src[f]})')
        rus[f], rsrc[f] = (tr, 'translated from English') if tr else (site, 'site' if site else '')
    title_ru = TFIX.get((mid, 'title_ru'), rus['title']); desc_ru = TFIX.get((mid, 'description_ru'), rus['description'])
    if (mid, 'description_ru') in TFIX: rsrc['description'] = 'site'
    new = dict(motif_id=mid, title_en=title_en, title_en_source=label(src['title'], mid) if title_en else '',
               description_en=desc_en, description_en_source=label(src['description'], mid) if desc_en else '',
               title_ru=title_ru, description_ru=desc_ru, title_ru_source=rsrc['title'], description_ru_source=rsrc['description'] if desc_ru else '',
               title_ru_site=t_site, definition_ru_site=d_site)
    for k, v in m.items():
        if k not in new and k not in ('title_ru', 'definition_ru'): new[k] = v
    out.append(new)
    if m.get('in_digital_db') == '1' and int(m.get('n_traditions') or 0) > 0:
        stat['motifs'] += 1
        short = lambda x: 'site (English list), another entry' if ', entry' in x else (x or 'none')
        stat['title: ' + short(new['title_en_source'])] += 1
        stat['description: ' + short(new['description_en_source'])] += 1
        stat['ru title: ' + (new['title_ru_source'] or 'none')] += 1
        stat['ru description: ' + (new['description_ru_source'] or 'none')] += 1

with open(path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(f'{path}: {len(out)} motifs')
for k in sorted(stat): print(f'   {k}: {stat[k]}')
unused = [k for k in FIX if not any(r['motif_id'] == k for r in rows)]
if unused: print('! fixes for unknown motifs:', unused)
for w_ in warn[:40]: print('!', w_)
if len(warn) > 40: print('! ...', len(warn), 'warnings')
