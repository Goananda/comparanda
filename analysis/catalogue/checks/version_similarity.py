"""Screen for differences in meaning between the authors' English entry and the Russian page of the same motif.
usage: python3 -I version_similarity.py <result motifs.csv> <out.tsv>
Similarity = share of common 5-letter stems between the Russian translation of the English entry and the site's Russian text."""
import csv, re, sys, math, collections
csv.field_size_limit(10 ** 9)
M = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
STOP = set('и или в на с со не что он она они оно его ее их то же как к ко по из за от у а но это этот эта эти тот та те так либо об о при для до над под без между чтобы когда который которая которые которого где '
           'персонаж персонажи некто кто того тем этом ему ей им себя свой свою своего своих был была были быть есть является становится один одна одного '
           'мотив мотивы см ср другой другого другие также тоже уже лишь только затем потом после перед'.split())
def toks(s):
    return [w[:5] for w in re.findall('[а-яё]+', s.lower().replace('ё', 'е')) if w not in STOP and len(w) > 2]
docs = []
for r in M:
    docs.append(set(toks(r['title_ru_site'] + ' ' + r['definition_ru_site'])))
df = collections.Counter(w for d in docs for w in d)
idf = lambda w: math.log(len(docs) / (1 + df[w])) + 0.5
def sim(a, b):
    A, B = set(toks(a)), set(toks(b))
    if not A or not B:
        return -1.0
    inter = sum(idf(w) for w in A & B)
    return inter / math.sqrt(sum(idf(w) for w in A) * sum(idf(w) for w in B))
rows = []
for r in M:
    t_auth = r['title_en_source'] != 'translated from Russian' and r['title_en']
    d_auth = r['description_en_source'] not in ('translated from Russian', '') and r['description_en']
    if not (t_auth or d_auth):
        continue
    ts = sim(r['title_ru'], r['title_ru_site']) if (t_auth and r['title_ru_source'] == 'translated from English') else -1
    ds = sim(r['description_ru'], r['definition_ru_site']) if (d_auth and r['description_ru_source'] == 'translated from English') else -1
    ln = (len(r['description_en'].split()) / max(1, len(r['definition_ru_site'].split()))) if d_auth and r['definition_ru_site'] else -1
    rows.append((r['motif_id'], round(ts, 2), round(ds, 2), round(ln, 2), r['title_en'], r['title_ru_site'], r['title_ru'], r['description_en'], r['definition_ru_site'], r['description_ru']))
with open(sys.argv[2], 'w', encoding='utf-8') as f:
    f.write('motif_id\ttitle_sim\tdesc_sim\tlen_ratio\ttitle_en\ttitle_ru_site\ttitle_ru_mine\tdesc_en\tdef_ru_site\tdesc_ru_mine\n')
    for x in rows:
        f.write('\t'.join(str(v).replace('\t', ' ') for v in x) + '\n')
import statistics
ts = [x[1] for x in rows if x[1] >= 0]; ds = [x[2] for x in rows if x[2] >= 0]
print(len(rows), 'motifs with an authors\' English entry | titles compared', len(ts), '| descriptions compared', len(ds))
for name, v in (('title', ts), ('description', ds)):
    q = sorted(v)
    print(name, 'similarity quantiles 5/10/25/50/75:', [q[int(len(q) * p)] for p in (0.05, 0.10, 0.25, 0.5, 0.75)],
          '| <0.2:', sum(x < 0.2 for x in v), '<0.35:', sum(x < 0.35 for x in v), '<0.5:', sum(x < 0.5 for x in v))
