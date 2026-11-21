"""Parse the catalogue's page 'Этносы и ареалы' into a table of tradition units.

usage: python3 -I parse_areas.py <pages_dir> <out_dir> [--extra manual/extra_units.tsv]
Writes <out_dir>/units_raw.tsv: one row per numbered unit (a tradition of the
authors' correlation table) with its area, number, text, and flags.

--extra adds units that the page does not list: traditions that the motif pages name as such in many texts
(columns area, no, text; the area must be spelled as on the page; the unit id becomes '<area key>#<no>').
"""
import csv, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import area_key

pages, out = sys.argv[1], sys.argv[2]
extra_path = None
if '--extra' in sys.argv:
    k_ = sys.argv.index('--extra')
    extra_path = sys.argv[k_ + 1]
    del sys.argv[k_:k_ + 2]
t = open(os.path.join(pages, 'areas1.html'), 'rb').read().decode('cp1251', 'replace')
body = t[t.find("<div id='main'>"):]
paras = re.findall(r'<p class="(\w+)"[^>]*>(.*?)</p>', body, re.S)


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


rows, notes = [], []
macro = area = None
NUM = re.compile(r'^(\(?)\s*(\d+)\s*([a-zа-я]?)\s*[.,]\s*(.*)$', re.S | re.I)
for cls, p in paras:
    txt = clean(p)
    if not txt:
        continue
    m = NUM.match(txt)
    if m:
        bracket, num, suf, rest = m.groups()
        rest = rest.strip()
        insufficient = bool(bracket) or 'данных недостаточно' in rest or 'недостаточно данных' in rest
        rows.append(dict(area=area, macro=macro, no=num + suf.lower().replace('а', 'a').replace('б', 'b'),
                         text=rest.rstrip(' .)') if bracket else rest.rstrip(' .'),
                         italic=int(bool(re.search(r'<i>', p))), insufficient=int(insufficient)))
        continue
    if re.search(r'<u>', p):
        area = txt.rstrip(' .'); continue
    if txt.upper() == txt and len(txt) < 60:
        macro = txt; continue
    notes.append((area, txt))

n_site = len(rows)
if extra_path and os.path.exists(extra_path):
    macro_of = {r['area']: r['macro'] for r in rows}
    for x in csv.DictReader(open(extra_path, encoding='utf-8'), delimiter='\t'):
        if x['area'] not in macro_of:
            sys.exit(f"extra unit with an area that the page does not have: {x['area']}")
        rows.append(dict(area=x['area'], macro=macro_of[x['area']], no=x['no'], text=x['text'], italic=0, insufficient=0))
    print('units added from', os.path.basename(extra_path), ':', len(rows) - n_site)

seen = {}
for r in rows:
    uid = f"{area_key(r['area'])}#{r['no']}"
    seen[uid] = seen.get(uid, 0) + 1
    r['unit_id'] = uid if seen[uid] == 1 else f'{uid}~{seen[uid]}'
print('duplicate unit numbers:', [k for k, v in seen.items() if v > 1])
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'units_raw.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t'); w.writeheader(); w.writerows(rows)
print('units:', len(rows), '| insufficient-data units:', sum(r['insufficient'] for r in rows),
      '| italic:', sum(r['italic'] for r in rows), '| areas:', len({r['area'] for r in rows}))
print('units counted in the table (not bracketed):', sum(1 for r in rows if not r['insufficient']))
for a, n in notes:
    print('NOTE', a, '|', n[:200])
if len(sys.argv) > 3:
    for r in rows:
        if any(k.lower() in r['area'].lower() for k in sys.argv[3:]):
            print(f"{r['area'][:22]:22s} {r['no']:>4s} {'I' if r['italic'] else ' '}{'X' if r['insufficient'] else ' '} {r['text'][:260]}")
