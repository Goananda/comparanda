"""Check the twelve cluster colours defined in site/src/style.css (--k0 ... --k11).

For the light and the dark theme the script prints the closest pairs of colours for normal vision and
under simulated protanopia and deuteranopia (Machado et al. 2009, severity 1.0), and the contrast of
every colour against the plot surface and the land fill. Distances are Euclidean in OKLab x100.

Usage: python3 check_palette.py <style.css>
"""
import itertools, re, sys
import numpy as np

NAMES = ['Europe', 'Maghreb to South Asia', 'Sub-Saharan Africa', 'South and East Asia', 'Oceania', 'Siberia', 'Beringia and Arctic',
         'Northwest Coast', 'California and Southwest', 'Plains and East', 'Mesoamerica', 'South America']
CVD = {'protan': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
       'deutan': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]}


def hex2lin(h):
    c = np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def oklab(rgb):
    r, g, b = rgb
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return np.array([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s])


def lum(lin):
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = max(lum(a), lum(b)), min(lum(a), lum(b))
    return (hi + 0.05) / (lo + 0.05)


def report(title, colours, surface, land):
    lin = [hex2lin(c) for c in colours]
    normal = [oklab(c) for c in lin]
    sim = {k: [oklab(np.clip(np.array(m) @ c, 0, 1)) for c in lin] for k, m in CVD.items()}
    rows = []
    for i, j in itertools.combinations(range(len(colours)), 2):
        dn = 100 * np.linalg.norm(normal[i] - normal[j])
        dc = min(100 * np.linalg.norm(sim[k][i] - sim[k][j]) for k in sim)
        rows.append((dn, dc, i, j))
    print(f'\n{title}: {len(colours)} colours, {len(rows)} pairs')
    print(f'  smallest distance, normal vision: {min(r[0] for r in rows):.1f}; simulated red-green deficiency: {min(r[1] for r in rows):.1f}')
    for label, key in (('normal vision', 0), ('simulated deficiency', 1)):
        print(f'  closest pairs, {label}:')
        for r in sorted(rows, key=lambda r: r[key])[:3]:
            print(f'    {r[key]:5.1f}  {NAMES[r[2]]} {colours[r[2]]}  /  {NAMES[r[3]]} {colours[r[3]]}')
    cs = [contrast(c, hex2lin(surface)) for c in lin]
    cl = [contrast(c, hex2lin(land)) for c in lin]
    i, j = int(np.argmin(cs)), int(np.argmin(cl))
    print(f'  lowest contrast against the surface {surface}: {min(cs):.2f} ({NAMES[i]}); against the land fill {land}: {min(cl):.2f} ({NAMES[j]})')


css = open(sys.argv[1], encoding='utf-8').read()
blocks = re.findall(r'--k0:[^\n]*', css)
assert len(blocks) == 3, 'expected the light block, the media-query dark block and the forced dark block'
assert blocks[1].strip() == blocks[2].strip(), 'the two dark blocks differ'
get = lambda block: [re.search(rf'--k{i}:(#[0-9a-fA-F]{{6}})', block).group(1) for i in range(12)]
surfaces = re.findall(r'--surface:(#[0-9a-fA-F]{6})', css)
lands = re.findall(r'--land:(#[0-9a-fA-F]{6})', css)
report('Light theme', get(blocks[0]), surfaces[0], lands[0])
report('Dark theme', get(blocks[2]), surfaces[-1], lands[-1])
