"""Exploratory: derive a red colour ramp with the same OKLCH lightness steps as the blue one, for the diverging scale on the page.
Usage: python3 ramps.py
"""
import numpy as np
def s2l(c): c = np.asarray(c, float); return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def l2s(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, 12.92*c, 1.055*c**(1/2.4)-0.055)
def hex2lin(h): h = h.lstrip('#'); return s2l([int(h[i:i+2], 16)/255 for i in (0, 2, 4)])
def lin2oklab(rgb):
    r, g, b = rgb
    l = np.cbrt(0.4122214708*r + 0.5363325363*g + 0.0514459929*b); m = np.cbrt(0.2119034982*r + 0.6806995451*g + 0.1073969566*b); s = np.cbrt(0.0883024619*r + 0.2817188376*g + 0.6299787005*b)
    return np.array([0.2104542553*l + 0.7936177850*m - 0.0040720468*s, 1.9779984951*l - 2.4285922050*m + 0.4505937099*s, 0.0259040371*l + 0.7827717662*m - 0.8086757660*s])
def oklab2lin(lab):
    L, a, b = lab
    l = (L + 0.3963377774*a + 0.2158037573*b)**3; m = (L - 0.1055613458*a - 0.0638541728*b)**3; s = (L - 0.0894841775*a - 1.2914855480*b)**3
    return np.array([4.0767416621*l - 3.3077115913*m + 0.2309699292*s, -1.2684380046*l + 2.6097574011*m - 0.3413193965*s, -0.0041960863*l - 0.7034186147*m + 1.7076147010*s])
def lch(h): L, a, b = lin2oklab(hex2lin(h)); return L, np.hypot(a, b), np.degrees(np.arctan2(b, a)) % 360
def from_lch(L, C, H):
    for c in np.linspace(C, 0, 200):
        rgb = oklab2lin([L, c*np.cos(np.radians(H)), c*np.sin(np.radians(H))])
        if rgb.min() >= -1e-4 and rgb.max() <= 1 + 1e-4: break
    return '#' + ''.join(f'{int(round(float(v)*255)):02x}' for v in l2s(rgb))
blue = {100:'#cde2fb',150:'#b7d3f6',200:'#9ec5f4',250:'#86b6ef',300:'#6da7ec',350:'#5598e7',400:'#3987e5',450:'#2a78d6',500:'#256abf',550:'#1c5cab',600:'#184f95',650:'#104281',700:'#0d366b'}
redH = lch('#e34948')[2]; print('red hue', round(redH, 1), 'blue hue', round(lch('#2a78d6')[2], 1))
for k, v in blue.items(): print(k, v, 'L %.3f C %.3f' % lch(v)[:2])
light_steps = [200, 350, 500, 650]; dark_steps = [600, 450, 300, 150]
for name, steps in [('light', light_steps), ('dark', dark_steps)]:
    reds = []
    for st in steps:
        L, C, _ = lch(blue[st]); reds.append(from_lch(L, C * 1.05, redH))
    print(name, 'blue arm', [blue[s] for s in steps], 'red arm', reds, 'L', [round(lch(r)[0], 3) for r in reds], 'C', [round(lch(r)[1], 3) for r in reds])
