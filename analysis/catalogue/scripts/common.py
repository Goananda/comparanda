"""Helpers shared by the catalogue scripts (names, area keys)."""
import re


def norm(s):
    s = s.lower().replace('ё', 'е').replace('ë', 'е')
    s = re.sub(r'[«»"“”‘’`\']', '', s)
    # Latin look-alike letters typed inside Cyrillic words (cаамы, cуму, мохo)
    if re.search(r'[а-я]', s):
        s = s.translate(str.maketrans('aceopxyk', 'асеорхук')) if not re.search(r'[a-z]{3,}', s) else s
    return re.sub(r'\s+', ' ', s).strip()


def area_key(s):
    """Order-independent key of an area or region heading:
    'Микронезия – Полинезия' and 'Полинезия, Микронезия' give the same key."""
    s = s.lower().replace('ё', 'е')
    s = re.sub(r'\(.*?\)', '', s)
    s = s.replace('\u00ad', '').lstrip('( ')
    s = re.sub(r'^\s*[cс]р(\.\s*|\s+)', '', s)   # 'Ср.' = compare; the first letter is sometimes Latin
    s = s.replace('–', '-').replace('—', '-').replace(',', '-')
    parts = [p.strip(' .') for p in re.split(r'\s-\s|-(?=\s)|(?<=\s)-', s) if p.strip(' .')]
    return ' | '.join(sorted(parts))


# canonical page region heading -> area heading of the page 'Этносы и ареалы' (both as area_key)
ALIAS = {
    'северная европа': 'балтоскандия', 'арктика': 'эскоалеуты', 'равнины': 'великие равнины',
    'япония': 'курилы | рюкю', 'св азия': 'северо-восточная азия',
    'кавказ | малая азия': 'кавказ | передняя азия', 'юв бразилия': 'южная и приатлантическая бразилия',
    'южная бразилия': 'южная и приатлантическая бразилия', 'антилы': 'большие антилы', 'арагуая': 'южная амазония',
    'индонезия | малайзия': 'индонезия и соседние острова | малайзия',
}

_FIX = None


def heading_key(region):
    """key of a page region heading after known misspellings and old names are mapped to the
    canonical heading (manual/regions.tsv next to the scripts directory)"""
    global _FIX
    if _FIX is None:
        import csv, os
        _FIX = {}
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'manual', 'regions.tsv')
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
                _FIX[area_key(r['variant'])] = area_key(r['canonical'])
    k = area_key(region)
    return _FIX.get(k, k)


def region_key(region):
    k = heading_key(region)
    return ALIAS.get(k, k)


_CODES = """10 ЮЗ Африка|11 Бантуязычная Африка|12 Западная Африка|13 Судан – Восточная Африка|14 Северная Африка|15 Южная Европа
16 Западная Европа|17 Передняя Азия|18 Австралия|19 Меланезия|20 Полинезия – Микронезия|21 Тибет – Северо-Восток Индии
22 Бирма – Индокитай|23 Южная Азия|24 Малайзия – Индонезия|25 Тайвань – Филиппины|26 Китай – Корея|27 Балканы|28 Средняя Европа
29 Кавказ – Малая Азия|30 Иран – Средняя Азия|31 Северная Европа|32 Волга – Пермь|33 Туркестан|34 Южная Сибирь – Монголия
35 Западная Сибирь|36 Восточная Сибирь|37 Амур – Сахалин|38 Япония|39 СВ Азия|40 Арктика|41 Субарктика|42 СЗ побережье
43 Побережье – Плато|44 Средний Запад|45 Северо-Восток|46 Равнины|47 Юго-Восток США|48 Калифорния|49 Большой Бассейн
50 Большой Юго-Запад|51 СЗ Мексика|52 Мезоамерика|53 Гондурас – Панама|54 Антилы|55 Северные Анды|56 Льяносы|57 Южная Венесуэла
59 Гвиана|60 Эквадор|61 Западная Амазония|62 СЗ Амазония|63 Центральная Амазония|64 Восточная Амазония|65 Центральные Анды
66 Монтанья – Журуа|67 Боливия – Гуапоре|68 Южная Амазония|69 Арагуая|70 Восточная Бразилия|71 ЮВ Бразилия|72 Чако
73 Южная Бразилия|74 Южный Конус"""
# canonical region headings of the catalogue (introduction to the catalogue): key -> numeric code
REGION_CODES = {}
for _item in _CODES.replace('\n', '|').split('|'):
    _c, _name = _item.split(' ', 1)
    REGION_CODES[area_key(_name)] = int(_c)


# ---- area codes of a motif heading
_REF = re.compile(r'\(?\b(?:ATU|AaTh|AT|Th)\.?\s*\d[\dA-Za-z*]*(?:\s*[,;]\s*\d[\dA-Za-z*]*)*\)?\.?|\b[A-Z]\d+(?:\.\d+)*[a-z]?\+?\.?(?=[\s,;.)]|$)')
_BLOCK = re.compile(r'(?<![A-Za-zА-Яа-яЁё0-9№:])(?:\(\s*)?\.?\s*(?:1\d|[2-6]\d|7[0-4])\s*[.,/](?:[\d.,/\-–() ]|\s)*')


def area_codes(s):
    """Area codes in a motif heading: (codes outside brackets, codes in brackets only, the matched pieces of text).
    The site writes them as .11.-.13.(.15.).27. ; a few headings drop the leading dot (21.22.26.) or use a comma or a slash.
    Index numbers (ATU 62, A1131.4) are not area codes.  a.-.b is a range; only 10..74 are areas."""
    s2 = _REF.sub(lambda m: ' ' * len(m.group(0)), s)
    inc, brk, pieces = set(), set(), []
    for m in _BLOCK.finditer(s2):
        blk = m.group(0); depth = 0; prev = None; rng = False; got = False
        for tk in re.findall(r'\(|\)|[-–]|\d+', blk):
            if tk == '(':
                depth += 1
            elif tk == ')':
                depth = max(0, depth - 1)
            elif tk in '-–':
                rng = True
            else:
                n = int(tk)
                if not 10 <= n <= 74:
                    prev = None; rng = False; continue
                tgt = brk if depth else inc
                if rng and prev is not None:
                    tgt.update(range(prev + 1, n + 1))
                else:
                    tgt.add(n)
                prev, rng, got = n, False, True
        if got:
            pieces.append(s[m.start():m.end()])
    return inc, brk - inc, pieces


def codes_text(inc, brk):
    """canonical spelling of area codes: .11.12.13.(.15.)"""
    a = ''.join(f'.{n}' for n in sorted(inc)) + ('.' if inc else '')
    b = ('(' + ''.join(f'.{n}' for n in sorted(brk)) + '.)') if brk else ''
    return a + b
