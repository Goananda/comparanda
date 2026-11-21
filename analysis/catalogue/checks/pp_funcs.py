"""helper for checks: loads the function definitions of scripts/parse_pages.py without running its main loop"""
import os, re, sys, html, csv
from collections import Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
sys.path.insert(0, S)
from common import heading_key, REGION_CODES, area_codes, codes_text, norm
src = open(os.path.join(S, 'parse_pages.py'), encoding='utf-8').read()
a = src[src.index('def norm_name'):src.index('idx = ')] if 'idx = ' in src else ''
b = src[src.index('AREA_RE = '):src.index('mrows, erows, plain')]
exec(compile(a + '\n' + b, 'parse_pages_funcs', 'exec'), globals())
def page_paragraphs(pages, code):
    t = open(os.path.join(pages, code + '.html'), 'rb').read().decode('cp1251', 'replace')
    i = t.find('<div id="main">')
    return paragraphs(t[i:] if i >= 0 else t)
def show(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', lambda m: '⟨' if m.group(0) == '<u>' else ('⟩' if m.group(0) == '</u>' else ''), s))).strip()
