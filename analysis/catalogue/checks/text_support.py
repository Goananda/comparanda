"""For motifs whose English entry and Russian page may differ: how well the texts of the page support what is specific
to each version.  usage: python3 -I text_support.py <pages_dir> <result motifs.csv> <out.tsv>
A = Russian translation of the authors' English description (+ title); B = the Russian title and definition of the page.
For the stems found in only one of them: the share of the page's texts (abstracts in square brackets) that contain the stem."""
import csv, os, re, sys, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pp_funcs import in_square, page_paragraphs, clean
pages, fm, out = sys.argv[1:4]
csv.field_size_limit(10 ** 9)
M = list(csv.DictReader(open(fm, encoding='utf-8-sig')))
STOP = set('и или в на с со не что он она они оно его ее их то же как к ко по из за от у а но это этот эта эти тот та те так либо об о при для до над под без между чтобы когда который которая которые которого где '
           'персонаж персонажи некто кто того тем этом ему ей им себя свой свою своего своих был была были быть есть является становится один одна одного человек люди '
           'мотив мотивы см ср другой другого другие также тоже уже лишь только затем потом после перед обычно часто иногда реже например может могут'.split())
def stems(s):
    return {w[:5] for w in re.findall('[а-яё]+', s.lower().replace('ё', 'е')) if w not in STOP and len(w) > 2}
def abstracts(code):
    res = []
    for cls, p in page_paragraphs(pages, code):
        if cls in ('NormalLin', 'NormalLis'):
            continue
        for a, b in in_square(p):
            t = clean(p[a:b + 1])
            if len(t) > 25:
                res.append(stems(t))
    return res
docs = [stems(r['title_ru_site'] + ' ' + r['definition_ru_site']) for r in M]
df = collections.Counter(w for d in docs for w in d)
idf = lambda w: math.log(len(docs) / (1 + df[w])) + 0.5
rows = []
for r in M:
    if r['description_en_source'] in ('translated from Russian', '') or r['description_ru_source'] != 'translated from English':
        continue
    A = stems(r['title_ru'] + ' ' + r['description_ru']); B = stems(r['title_ru_site'] + ' ' + r['definition_ru_site'])
    if not A or not B:
        continue
    ab = abstracts(r['motif_id'])
    if not ab:
        continue
    n = len(ab)
    sup = lambda w: sum(w in x for x in ab) / n
    oa = sorted(((sup(w), w) for w in A - B), reverse=True); ob = sorted(((sup(w), w) for w in B - A), reverse=True)
    sa = sum(s * idf(w) for s, w in oa) / max(1e-9, sum(idf(w) for s, w in oa)) if oa else 0
    sb = sum(s * idf(w) for s, w in ob) / max(1e-9, sum(idf(w) for s, w in ob)) if ob else 0
    inter = sum(idf(w) for w in A & B) / math.sqrt(sum(idf(w) for w in A) * sum(idf(w) for w in B))
    fmt = lambda o: ' '.join(f'{w}:{round(100 * s)}' for s, w in o[:7])
    rows.append((r['motif_id'], round(inter, 2), n, round(sa, 3), round(sb, 3), len(oa), len(ob), fmt(oa), fmt(ob)))
with open(out, 'w', encoding='utf-8') as f:
    f.write('motif_id\tsim\tn_texts\tsupport_en_only\tsupport_ru_only\tn_en_only\tn_ru_only\ten_only_stems\tru_only_stems\n')
    for x in rows:
        f.write('\t'.join(str(v) for v in x) + '\n')
print(len(rows), 'motifs compared')
