"""Why does a motif heading list an area that has no text with a name on the page?
usage: python3 -I heading_areas.py <pages_dir> <out_dir (entries_raw, motifs_raw)> <result_dir> <prefix> [n_examples]"""
import csv, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pp_funcs import *
pages, out, res, pre = sys.argv[1:5]
nex = int(sys.argv[5]) if len(sys.argv) > 5 else 12
csv.field_size_limit(10 ** 9)
NAME = {v: k for k, v in REGION_CODES.items()}
code_of = lambda region: REGION_CODES.get(heading_key(region))
main = collections.defaultdict(set); cf = collections.defaultdict(set); summ = collections.defaultdict(set)
for e in csv.DictReader(open(os.path.join(out, 'entries_raw.tsv'), encoding='utf-8'), delimiter='\t'):
    c = code_of(e['region'])
    if c is None:
        continue
    {'': main, 'cf': cf, 'abstract': cf, 'summary': summ, 'summary-cf': cf}[e['flag']][e['motif_id']].add(c)
incl = collections.defaultdict(set)
p = os.path.join(res, pre + 'motifs.csv')
M = list(csv.DictReader(open(p, encoding='utf-8-sig')))
for m in M:
    for x in (m.get('includes') or '').split():
        incl[m['motif_id']].add(x)
cls = collections.Counter(); ex = collections.defaultdict(list); extra_n = 0; extra = collections.Counter()
n_db = n_head = 0
for m in M:
    if m['in_digital_db'] != '1':
        continue
    mid = m['motif_id']
    inc, brk, _ = area_codes(m['area_codes'])
    inc.discard(58)
    got = set(main[mid])
    for x in incl[mid]:
        got |= main[x]
    n_db += 1; n_head += len(inc)
    for c in sorted(got - inc - brk):
        extra[c] += 1; extra_n += 1
    miss = inc - got
    if not miss:
        continue
    heads = set()
    for cl, par in page_paragraphs(pages, mid):
        mb = re.search(r'<b>(.*?)</b>', par, re.S)
        cands = []
        if mb:
            cands.append(clean(mb.group(1)).rstrip('.').strip())
        mh = re.match(r'\(?\s*((?:[CcСс]р\.\s*)?[^.\[\]:;<>]{3,60})\.', clean(par[:400]))
        if mh:
            cands.append(mh.group(1).strip())
        for b in cands:
            b = re.sub(r'[.,]?\s*(См|Ср)\. мотив.*$', '', b).strip(' /.')
            c = code_of(b)
            if c is not None:
                heads.add(c)
    for c in sorted(miss):
        if c in cf[mid]:
            k = 'only compared texts (Ср.) in this area'
        elif c in heads:
            k = 'a paragraph of this area exists, no name found in it'
        elif c in summ[mid]:
            k = 'named only in the summary list'
        elif c not in NAME:
            k = 'code without a region'
        else:
            k = 'no trace of the area on the page'
        cls[k] += 1
        if len(ex[k]) < nex:
            ex[k].append(f'{mid}:{c} {NAME.get(c, "?")}')
print(f'motifs of the database: {n_db}; areas in headings: {n_head}; heading areas without a text: {sum(cls.values())}')
for k, v in cls.most_common():
    print(f'  {v:5} {k} | ' + '; '.join(ex[k]))
print('areas with texts that the heading does not list:', extra_n, '| by area:', [(c, NAME.get(c, '?'), n) for c, n in extra.most_common(12)])
