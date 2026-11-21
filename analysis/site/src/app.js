(() => {
'use strict';
const D = JSON.parse(document.getElementById('data').textContent);
const GEO = JSON.parse(document.getElementById('geo').textContent);
const G = D.g, M = D.m, NG = G.name.length, NM = M.id.length, nodes = D.nodes;
const $ = (s, r = document) => r.querySelector(s);
const h = (tag, props, ...kids) => {
  const e = document.createElement(tag);
  if (props) for (const k in props) {
    if (k === 'class') e.className = props[k];
    else if (k === 'text') e.textContent = props[k];
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), props[k]);
    else e.setAttribute(k, props[k]);
  }
  for (const c of kids) if (c != null) e.append(c);
  return e;
};
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const STATE = {};
const RERENDER = [];
let LANG = 'en';

// ---------- language: English is the default, Russian is the alternative. Motif and tradition names stay as in the data.
const NF = { en: new Intl.NumberFormat('en-US'), ru: new Intl.NumberFormat('ru-RU') };
const nf = v => NF[LANG].format(v);
const dec = s => (LANG === 'ru' ? s.replace('.', ',') : s);
const f2 = v => dec(v.toFixed(2)), f3 = v => dec(v.toFixed(3));
const pc = v => Math.round(v * 100) + '%';
const ruPl = (n, one, few, many) => { const a = Math.abs(n) % 100, b = a % 10; return a > 10 && a < 20 ? many : b === 1 ? one : b >= 2 && b <= 4 ? few : many; };
const nTrad = n => (LANG === 'ru' ? `${nf(n)} ${ruPl(n, 'традиция', 'традиции', 'традиций')}` : `${nf(n)} ${n === 1 ? 'tradition' : 'traditions'}`);
const nm = o => (LANG === 'ru' ? o.name : o.name_en);
const sh = o => (LANG === 'ru' ? o.short : o.short_en);
const TX = {
  en: {
    zoomIn: 'Zoom in', zoomOut: 'Zoom out', zoomReset: 'Show the whole world', openMotif: 'Click to open the motif in the atlas',
    motifOther: 'No English text for this motif. In Russian:', motifNoDesc: 'The catalogue gives this motif no description.',
    navLabel: 'Sections', langLabel: 'Language', kLess: 'One cluster fewer', kMore: 'One cluster more',
    clMapLabel: 'World map: traditions coloured by cluster of motif similarity', clUmapLabel: 'Traditions in similarity space, UMAP projection',
    lowData: 'Fewer than 15 motifs; left out of the analysis',
    motifsRecorded: n => (n === 1 ? 'motif recorded' : 'motifs recorded'),
    clHint: 'Hover over a cluster in the list to highlight it on the map and see its characteristic motifs. Click to pin it.',
    clMeta: (n, share) => `${nTrad(n)} · median share of cosmological motifs ${share}`,
    clInd: 'Characteristic motifs: share of traditions with the motif inside the cluster / outside it',
    clCore: 'Closest to the cluster centre: ', clAll: n => `All ${nTrad(n)} in the cluster`,
    step: (a, b) => `Step ${a} → ${b}. `, splitAll: 'All traditions split', splitOne: name => `The cluster “${name}” splits`, splitInto: (a, b) => ` into “${a}” and “${b}”.`,
    coh1: 'Of the ten geographically nearest neighbours of each tradition, ', coh2: ' fall into its own cluster. A random partition into clusters of the same sizes would give ', coh3: '.',
    play: '▶ Play the splits', stop: '■ Stop',
    nmfTop: '90% and above', nmfStrong: 'Strongest in: ', nmfTip: 'of the maximum weight of this set',
    nmfLabel: name => `Map of the “${name}” complex: traditions where the motif set is present`,
    axMapLabel: 'World map: position of traditions on the principal axis', axTip: 'position on the axis, from −100 to +100',
    axis: (i, neg, pos) => `Axis ${i}: ${neg} ↔ ${pos}. `,
    axCap: (v, ng, nmot) => `The axis explains ${v}% of the variance. It is computed on ${nTrad(ng)} with 15 or more motifs of this group and ${nf(nmot)} motifs. Scores are scaled so that ±100 is the 97th percentile.`,
    axPole: 'Traditions at this pole: ',
    km: 'km', moPh: 'code or word: a36, moon, trickster',
    wide: 'widespread', moUmapLabel: 'Motifs in the space of range similarity, UMAP projection', moMapLabel: 'World map: traditions in which the selected motif is recorded',
    moMostIn: name => 'most frequent in: ' + name,
    moUmapCap: n => `Shown are ${nf(n)} motifs recorded in at least five traditions. A motif is assigned to an area when that area accounts for at least 60% of its occurrence, adjusted for how much is recorded there. This is a UMAP projection; the axes mean nothing.`,
    moHas: 'motif recorded', moHasNot: 'motif not recorded', moTotal: n => (n === 1 ? 'motif in total' : 'motifs in total'),
    moMeta: (letter, isA, n, N) => `Catalogue section ${letter} (${isA ? 'cosmology and etiology' : 'adventure and tricksters'}) · recorded in ${nf(n)} of ${nf(N)} traditions · `,
    moLink: 'the motif page in the catalogue (in Russian)',
    moCor: 'compare with other motifs',
    moMapCap: id => `Blue dots: traditions where motif ${id} is recorded. Grey dots: the other traditions in the catalogue.`,
    moShare: 'Share of traditions with the motif in three macro-areas', moOf: (p, a, b) => `${p} · ${a} of ${b}`,
    moAreas: 'The areas come from the three-cluster step. Traditions with 15 or more motifs are counted.',
    moSimilar: 'Motifs with the most similar range', moJacc: 'The number is the share of traditions the two motifs have in common (Jaccard index).',
    moAll: n => `All ${nTrad(n)} with this motif`
  },
  ru: {
    zoomIn: 'Приблизить', zoomOut: 'Отдалить', zoomReset: 'Показать весь мир', openMotif: 'Щелчок открывает мотив в атласе',
    motifOther: 'Русского текста у этого мотива нет. По-английски:', motifNoDesc: 'В каталоге у этого мотива нет описания.',
    navLabel: 'Разделы', langLabel: 'Язык', kLess: 'На один кластер меньше', kMore: 'На один кластер больше',
    clMapLabel: 'Карта мира: традиции окрашены по кластерам сходства мотивов', clUmapLabel: 'Традиции в пространстве сходства, проекция UMAP',
    lowData: 'Меньше 15 мотивов, в расчёт не входила',
    motifsRecorded: n => ruPl(n, 'мотив записан', 'мотива записано', 'мотивов записано'),
    clHint: 'Наведите на кластер в списке, чтобы выделить его на карте и увидеть характерные мотивы. Щелчок закрепляет выбор.',
    clMeta: (n, share) => `${nTrad(n)} · медианная доля космологических мотивов ${share}`,
    clInd: 'Характерные мотивы: доля традиций с мотивом в кластере и вне его',
    clCore: 'Ближе всего к центру кластера: ', clAll: n => `Все ${nTrad(n)} кластера`,
    step: (a, b) => `Шаг ${a} → ${b}. `, splitAll: 'Все традиции делятся', splitOne: name => `Кластер «${name}» делится`, splitInto: (a, b) => ` на «${a}» и «${b}».`,
    coh1: 'Из десяти географически ближайших соседей каждой традиции ', coh2: ' попадают в её же кластер. При случайном разбиении на кластеры таких же размеров было бы ', coh3: '.',
    play: '▶ Показать по шагам', stop: '■ Остановить',
    nmfTop: '90% и выше', nmfStrong: 'Сильнее всего: ', nmfTip: 'от максимального веса набора',
    nmfLabel: name => `Карта комплекса «${name}»: традиции, где набор мотивов выражен`,
    axMapLabel: 'Карта мира: положение традиций на главной оси', axTip: 'положение на оси, от −100 до +100',
    axis: (i, neg, pos) => `Ось ${i}: ${neg} ↔ ${pos}. `,
    axCap: (v, ng, nmot) => `Ось объясняет ${v}% разброса. В расчёт вошли ${nTrad(ng)} с 15 и более мотивами этой группы и ${nf(nmot)} ${ruPl(nmot, 'мотив', 'мотива', 'мотивов')}. Значения нормированы так, что ±100 соответствует 97-му процентилю.`,
    axPole: 'Традиции у полюса: ',
    km: 'км', moPh: 'код или слово: a36, луна, трикстер',
    wide: 'широкий ареал', moUmapLabel: 'Мотивы в пространстве сходства ареалов, проекция UMAP', moMapLabel: 'Карта мира: традиции, в которых записан выбранный мотив',
    moMostIn: name => 'чаще всего: ' + name,
    moUmapCap: n => `Показаны ${nf(n)} ${ruPl(n, 'мотив', 'мотива', 'мотивов')}, записанные хотя бы у пяти традиций. Мотив отнесён к области, если на неё приходится не меньше 60% его встречаемости с поправкой на число записей в области. Проекция UMAP, оси ничего не значат.`,
    moHas: 'мотив записан', moHasNot: 'мотив не записан', moTotal: n => ruPl(n, 'мотив всего', 'мотива всего', 'мотивов всего'),
    moMeta: (letter, isA, n, N) => `Раздел ${letter} каталога (${isA ? 'космология и этиология' : 'приключения и трикстеры'}) · записан у ${nf(n)} ${ruPl(n, 'традиции', 'традиций', 'традиций')} из ${nf(N)} · `,
    moLink: 'страница мотива в каталоге',
    moCor: 'сравнить с другими мотивами',
    moMapCap: id => `Синие точки: традиции, где записан мотив ${id}. Серые: остальные традиции каталога.`,
    moShare: 'Доля традиций с мотивом в трёх больших областях', moOf: (p, a, b) => `${p} · ${a} из ${b}`,
    moAreas: 'Области взяты из третьего шага кластеризации. Учтены традиции с 15 и более мотивами.',
    moSimilar: 'Мотивы с самым похожим ареалом', moJacc: 'Число справа показывает долю общих традиций (мера Жаккара).',
    moAll: n => `Все ${nTrad(n)} с этим мотивом`
  }
};
const t = (k, ...a) => { const v = TX[LANG][k]; return typeof v === 'function' ? v(...a) : v; };
const setAttrs = el => { const d = el.dataset; if (d.tTitle) el.title = t(d.tTitle); if (d.tAria) el.setAttribute('aria-label', t(d.tAria)); if (d.tPh) el.placeholder = t(d.tPh); };
const tAttr = (el, o) => { for (const k in o) el.dataset['t' + k[0].toUpperCase() + k.slice(1)] = o[k]; setAttrs(el); return el; };
const applyAttrs = () => { for (const el of document.querySelectorAll('[data-t-title],[data-t-aria],[data-t-ph]')) setAttrs(el); };

// ---------- derived data
const gMot = Array.from({ length: NG }, () => []);
D.inc.forEach((gs, m) => { for (const g of gs) gMot[g].push(m); });
const mDf = D.inc.map(a => a.length);
const mIsA = M.id.map(s => s.charCodeAt(0) <= 105);
const keptPos = new Int32Array(NG).fill(-1); D.kept.forEach((g, j) => { keptPos[g] = j; });
const GXY = GEO.gxy;
const gByName = new Map(G.name.map((n, i) => [n, i]));
const rad = Math.PI / 180;
const km = (a, b) => {
  const p1 = G.lat[a] * rad, p2 = G.lat[b] * rad, dl = (G.lon[b] - G.lon[a]) * rad;
  const s = Math.sin(p1) * Math.sin(p2) + Math.cos(p1) * Math.cos(p2) * Math.cos(dl);
  return 6371 * Math.acos(Math.max(-1, Math.min(1, s)));
};

// ---------- shared drawing pieces
const DOT = d3.symbol(d3.symbolCircle, 50)();
const NSVG = 'http://www.w3.org/2000/svg';
const defs = document.getElementById('geo-defs');
for (const [id, d] of [['geo-land', GEO.land], ['geo-grat', GEO.grat], ['geo-sphere', GEO.sphere]]) {
  const p = document.createElementNS(NSVG, 'path'); p.setAttribute('id', id); p.setAttribute('d', d); defs.append(p);
}
const mapBg = grat => g => { if (grat) g.append('use').attr('href', '#geo-grat'); g.append('use').attr('href', '#geo-land'); if (grat) g.append('use').attr('href', '#geo-sphere'); };
const MAPO = { W: GEO.W, H: GEO.H, y0: GEO.y0 };
const swatch = cls => {
  const s = document.createElementNS(NSVG, 'svg'); s.setAttribute('class', 'sw'); s.setAttribute('viewBox', '-8 -8 16 16'); s.setAttribute('aria-hidden', 'true');
  const p = document.createElementNS(NSVG, 'path'); p.setAttribute('d', DOT); p.setAttribute('class', 'mk ' + cls); p.setAttribute('transform', 'scale(1.35)'); s.append(p); return s;
};
const steps = (host, vars, titles) => { host.textContent = ''; vars.forEach((v, i) => { const s = h('i'); s.style.background = 'var(--' + v + ')'; if (titles) s.title = titles[i]; host.append(s); }); };

const tipEl = $('#tip');
const Tip = {
  fill(rows, cls) { tipEl.className = cls || ''; tipEl.textContent = ''; for (const r of rows) tipEl.append(r); tipEl.hidden = false; },
  show(e, rows, cls) { this.fill(rows, cls); this.move(e); },
  anchor(el, x) {                   // above a list row so that the rows still to be read stay visible; below it when there is no room
    const r = el.getBoundingClientRect(), w = tipEl.offsetWidth, hh = tipEl.offsetHeight, box = el.closest('.pkbox');
    if (box) {                         // beside a drop-down list, so that the search field stays visible
      const b = box.getBoundingClientRect(); let left = b.right + 8; if (left + w > innerWidth - 8) left = b.left - w - 8;
      tipEl.style.left = Math.max(8, left) + 'px'; tipEl.style.top = Math.max(8, Math.min(r.top, innerHeight - hh - 8)) + 'px'; return;
    }
    let top = r.top - hh - 6; if (top < 52) top = r.bottom + 6;
    tipEl.style.left = Math.max(8, Math.min(x + 16, innerWidth - w - 8)) + 'px'; tipEl.style.top = top + 'px';
  },
  move(e) {
    const pad = 14, w = tipEl.offsetWidth, hh = tipEl.offsetHeight;
    let x = e.clientX + pad, y = e.clientY + pad;
    if (x + w > innerWidth - 8) x = e.clientX - w - pad;
    if (y + hh > innerHeight - 8) y = e.clientY - hh - pad;
    tipEl.style.left = Math.max(8, x) + 'px'; tipEl.style.top = Math.max(8, y) + 'px';
  },
  hide() { tipEl.hidden = true; }
};
const tipTitle = s => h('div', { class: 'tt', text: s });
const tipLine = (strong, rest) => h('div', { class: 'tl' }, strong != null ? h('b', { text: strong }) : null, rest != null ? h('span', { text: rest }) : null);

class Plot {
  constructor(host, o) {
    this.host = host; this.o = Object.assign({ y0: 0, rPx: 3.4, hitPx: 16 }, o);
    this.k = 1; this.u = 1; this.rs = 1; this.pts = []; this.hov = null; this.ext = null; this.sel = null; this.styleFn = () => ({ cls: 'nul' });
    host.classList.add('plot');
    const svg = this.svg = d3.select(host).append('svg').attr('role', 'img');
    this.root = svg.append('g');
    this.bg = this.root.append('g'); this.marks = this.root.append('g'); this.over = this.root.append('g').attr('pointer-events', 'none');
    this.ring = this.over.append('circle').attr('class', 'hov-ring').attr('display', 'none');
    this.setBox();
    if (this.o.bg) this.o.bg(this.bg, this);
    svg.on('pointermove', e => { if (e.pointerType !== 'touch') this.setHover(this.pick(e), e); })
       .on('pointerleave', e => { if (e.pointerType !== 'touch') this.setHover(null); })
       .on('click', e => { const d = this.pick(e); this.setHover(d, e); if (d && this.o.click) this.o.click(d, e); });
    if (this.o.zoom) this.initZoom();
    this.measure(true);
    this.ro = new ResizeObserver(() => this.measure()); this.ro.observe(host);
  }
  label(s) { this.svg.attr('aria-label', s); return this; }
  destroy() { this.ro.disconnect(); }
  setBox() { this.svg.attr('viewBox', `0 ${this.o.y0} ${this.o.W} ${this.o.H}`); }
  measure(silent) {
    const w = this.host.clientWidth; if (!w) return;
    if (this.o.pixel) {
      const H = Math.round(this.o.pixel(w));
      if (w === this.o.W && H === this.o.H) return;
      this.o.W = w; this.o.H = H; this.u = 1; this.setBox();
    } else {
      const u = this.o.W / w; if (Math.abs(u - this.u) < 1e-3) return;
      this.u = u; this.rs = Math.max(0.55, Math.min(1, w / 640)); this.applyScale();
    }
    if (!silent && this.o.resize) this.o.resize(this);
  }
  tf(d) { const s = d._s || {}; return `translate(${d.x},${d.y}) scale(${(this.u / this.k) * (this.o.rPx / 4) * this.rs * (s.f || 1)})`; }
  setPoints(pts) { this.pts = pts; this.hov = null; this.ext = null; this.sel = this.marks.selectAll('path').data(pts, d => d.id).join('path').attr('d', DOT); return this; }
  restyle(fn) {
    if (fn) this.styleFn = fn; if (!this.sel) return this; const self = this;
    this.sel.each(function (d) {
      const s = d._s = self.styleFn(d);
      this.setAttribute('class', 'mk ' + s.cls + (s.dim ? ' dim' : ''));
      if (s.fill) this.style.fill = s.fill; else if (this.style.fill) this.style.fill = '';
      if (s.op != null) this.style.fillOpacity = s.op; else if (this.style.fillOpacity) this.style.fillOpacity = '';
      this.setAttribute('transform', self.tf(d));
      if (s.hide) this.setAttribute('display', 'none'); else this.removeAttribute('display');
    });
    if (this.o.sorted) this.sel.sort((a, b) => (a._s.z || 0) - (b._s.z || 0));
    this.moveRing(); return this;
  }
  applyScale() { if (this.sel) { const self = this; this.sel.attr('transform', d => self.tf(d)); } this.moveRing(); }
  pick(e) {
    const [mx, my] = d3.pointer(e, this.root.node()); const R = this.o.hitPx * this.u / this.k; let best = null, bd = R * R;
    for (const d of this.pts) { const s = d._s; if (!s || s.hide) continue; const dx = d.x - mx, dy = d.y - my, q = dx * dx + dy * dy; if (q < bd) { bd = q; best = d; } }
    return best;
  }
  setHover(d, e) {
    if (d !== this.hov) { this.hov = d; this.moveRing(); this.host.style.cursor = d && this.o.click ? 'pointer' : ''; if (this.o.hover) this.o.hover(d, e, false); }
    else if (d && e && this.o.hover) this.o.hover(d, e, true);
  }
  moveRing() { const d = this.hov || this.ext; if (!d) { this.ring.attr('display', 'none'); return; } this.ring.attr('display', null).attr('cx', d.x).attr('cy', d.y).attr('r', 7 * this.u / this.k); }
  mark(d) { this.ext = d; this.moveRing(); }
  initZoom() {
    const o = this.o, self = this;
    const z = this.zoom = d3.zoom().scaleExtent([1, 12]).extent([[0, o.y0], [o.W, o.y0 + o.H]]).translateExtent([[0, o.y0], [o.W, o.y0 + o.H]])
      .filter(e => {
        if (e.type === 'wheel') return e.ctrlKey || e.metaKey;
        if (e.type === 'dblclick') return true;
        if (e.type.startsWith('touch')) return (e.touches && e.touches.length > 1) || self.k > 1.01;
        return !e.button && self.k > 1.01;
      })
      .on('zoom', e => { self.k = e.transform.k; self.root.attr('transform', e.transform); self.applyScale(); self.host.classList.toggle('zoomed', self.k > 1.01); if (o.onzoom) o.onzoom(self); });
    this.svg.call(z);
    const go = (fn, a) => { const tr = reduceMotion ? this.svg : this.svg.transition().duration(260); tr.call(fn, a); };
    const mk = (txt, key, fn) => tAttr(h('button', { type: 'button', class: 'zb', text: txt, onclick: fn }), { title: key, aria: key });
    this.host.append(h('div', { class: 'zoombar' },
      mk('+', 'zoomIn', () => go(z.scaleBy, 1.8)), mk('−', 'zoomOut', () => go(z.scaleBy, 1 / 1.8)), mk('⟲', 'zoomReset', () => go(z.transform, d3.zoomIdentity))));
  }
}

let selectMotif = () => {}, openMotif = () => {}, openCor = () => {}, corSet = null;
// ---------- motif titles and descriptions in the page language (data/source/motifs.csv; the Russian version is a translation
// of the English one wherever the catalogue has its own English text, see analysis/catalogue/scripts/motif_texts.py)
const mT = m => (LANG === 'ru' && M.tru[m]) || M.title[m];
const clip = (s, n) => (s.length > n ? s.slice(0, s.lastIndexOf(' ', n)) + '…' : s);
const motifDesc = (m, n) => {           // rows for a tooltip or the atlas; n limits the length for tooltips
  const ru = LANG === 'ru', own = ru ? M.ru[m] : M.desc[m], other = ru ? M.desc[m] : M.ru[m], cut = s => (n ? clip(s, n) : s);
  if (own) return [h('div', { class: 'dd', text: cut(own) })];
  if (other) return [h('div', { class: 'dn', text: t('motifOther') }), h('div', { class: 'dd', lang: ru ? 'en' : 'ru', text: cut(other) })];
  return [h('div', { class: 'dn', text: t('motifNoDesc') })];
};
const motifTip = (m, hint) => [tipTitle(M.id[m] + ' · ' + mT(m)), ...motifDesc(m, 520), hint ? h('div', { class: 'dh', text: t('openMotif') }) : null].filter(Boolean);
let tipFor = null;                      // the element with data-m whose description is on screen
const tipDrop = () => { if (tipFor) { tipFor = null; Tip.hide(); } };
document.addEventListener('pointerover', e => {
  if (e.pointerType === 'touch') return;
  const el = e.target.closest ? e.target.closest('[data-m]') : null;
  if (el && el !== tipFor) { tipFor = el; Tip.fill(motifTip(+el.dataset.m, el.dataset.open === '1'), 'wide'); Tip.anchor(el, e.clientX); }
});
document.addEventListener('pointermove', e => { if (tipFor && e.pointerType !== 'touch') Tip.anchor(tipFor, e.clientX); });
document.addEventListener('pointerout', e => { if (tipFor && !(e.relatedTarget && tipFor.contains(e.relatedTarget))) tipDrop(); });
document.addEventListener('focusin', e => {
  const el = e.target.closest ? e.target.closest('button[data-m]') : null;
  if (!el || !el.matches(':focus-visible')) return;
  tipFor = el; Tip.fill(motifTip(+el.dataset.m, el.dataset.open === '1'), 'wide'); Tip.anchor(el, el.getBoundingClientRect().left);
});
document.addEventListener('focusout', tipDrop);
document.addEventListener('click', tipDrop, true);
document.addEventListener('scroll', tipDrop, { capture: true, passive: true });
document.addEventListener('keydown', e => { if (e.key === 'Escape') tipDrop(); });
const motifBtn = (m, val, noScroll) => {
  const b = h('button', { class: 'mref', type: 'button', onclick: () => openMotif(m) },
    h('span', { class: 'code', text: M.id[m] }), h('span', { text: mT(m) }), val ? h('span', { class: 'val', text: val }) : null);
  b.dataset.m = m; b.dataset.open = '1'; return b;
};
const segInit = (host, cb) => {
  host.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; cb(b.dataset.v); });
  return v => { for (const b of host.querySelectorAll('button')) b.setAttribute('aria-pressed', String(b.dataset.v === String(v))); };
};

// ---------- shared by several views
const KEPT = D.kept, LEAF = D.labels[12];
const PROJ = d3.geoEqualEarth().rotate([-153, 0]).fitWidth(GEO.W, { type: 'Sphere' });   // the same projection as in analysis/build_geo.mjs
const GEOPATH = d3.geoPath(PROJ);
const arcPath = (a, b) => GEOPATH({ type: 'LineString', coordinates: [[G.lon[a], G.lat[a]], [G.lon[b], G.lat[b]]] });
const leafOf = g => { const j = keptPos[g]; return j < 0 ? null : nodes[LEAF[j]]; };
const chip = cls => { const i = h('i', { class: 'chip ' + cls }); return i; };
// motif search by code or by a word of the title in either language
const MIDX = []; for (let m = 0; m < NM; m++) if (mDf[m] > 0) MIDX.push({ m, id: M.id[m], t: M.title[m].toLowerCase(), r: M.tru[m].toLowerCase().replace(/ё/g, 'е') });
const motifSearch = (q, lim = 8) => {
  q = q.trim().toLowerCase().replace(/ё/g, 'е'); if (!q) return [];
  const ex = [], pre = [], sub = [];
  for (const o of MIDX) { if (o.id === q) ex.push(o); else if (o.id.startsWith(q)) pre.push(o); else if (o.t.includes(q) || o.r.includes(q)) sub.push(o); }
  pre.sort((a, b) => a.id.length - b.id.length || a.id.localeCompare(b.id)); sub.sort((a, b) => mDf[b.m] - mDf[a.m]);
  return ex.concat(pre, sub).slice(0, lim);
};
// a search field whose list drops down on focus and narrows as you type; o.items(query) -> array, o.row(item) -> element, o.pick(item)
function picker(inp, o) {
  const wrap = h('span', { class: 'pk' }), box = h('div', { class: 'pkbox', role: 'listbox' }); inp.replaceWith(wrap); wrap.append(inp, box); box.hidden = true;
  let items = [], shown = 0, act = -1;
  const more = () => {
    for (const end = Math.min(items.length, shown + 150); shown < end; shown++) {
      const it = items[shown], row = o.row(it); row.classList.add('pkrow'); row.setAttribute('role', 'option');
      row.addEventListener('mousedown', e => { e.preventDefault(); choose(it); }); box.append(row);
    }
  };
  const close = () => { box.hidden = true; };
  const open = () => {
    items = o.items(inp.value); box.textContent = ''; shown = 0; act = -1; more(); box.hidden = !items.length; box.scrollTop = 0;
    box.style.left = ''; box.style.right = ''; if (!box.hidden && wrap.getBoundingClientRect().left + box.offsetWidth > document.documentElement.clientWidth - 8) { box.style.left = 'auto'; box.style.right = '0'; }
  };
  const choose = it => { inp.value = ''; close(); inp.blur(); o.pick(it); };
  const move = d => {
    if (box.hidden) open(); const n = box.children.length; if (!n) return; if (act >= 0) box.children[act].classList.remove('act');
    act = Math.max(0, Math.min(n - 1, act + d)); const r = box.children[act]; r.classList.add('act');
    if (r.offsetTop < box.scrollTop) box.scrollTop = r.offsetTop; else if (r.offsetTop + r.offsetHeight > box.scrollTop + box.clientHeight) box.scrollTop = r.offsetTop + r.offsetHeight - box.clientHeight;
  };
  inp.addEventListener('focus', open); inp.addEventListener('input', open); inp.addEventListener('click', () => { if (box.hidden) open(); });
  inp.addEventListener('blur', () => setTimeout(close, 150));
  box.addEventListener('scroll', () => { if (box.scrollTop + box.clientHeight > box.scrollHeight - 120) more(); });
  inp.addEventListener('keydown', e => {
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
    else if (e.key === 'Enter' && !box.hidden && items.length && (act >= 0 || inp.value.trim())) choose(items[Math.max(act, 0)]);
  });
}
const MALL = MIDX.slice().sort((x, y) => x.id.localeCompare(y.id, 'en', { numeric: true }));     // catalogue order: a1, a2, ... a10
const motifItems = q => (q.trim() ? motifSearch(q, 400) : MALL);
const motifRow = o => { const r = h('div', { class: 'mref' }, h('span', { class: 'code', text: o.id }), h('span', { text: mT(o.m) }), h('span', { class: 'val', text: nf(mDf[o.m]) })); r.dataset.m = o.m; return r; };

// ============================================================ 0. home: the cluster map at eight clusters, without controls
function initHome() {
  const lab = D.labels[8], st = { hov: null };
  const nodeOf = g => { const j = keptPos[g]; return j < 0 ? null : nodes[lab[j]]; };
  const map = new Plot($('#hmMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true),
    hover: (d, e, mv) => {
      if (!d) return Tip.hide(); if (mv) return Tip.move(e); const n = nodeOf(d.g), c = G.n[d.g];
      Tip.show(e, [tipTitle(G.name[d.g]), tipLine(null, n ? nm(n) : t('lowData')), tipLine(String(c), t('motifsRecorded', c))]);
    } }));
  map.setPoints(d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] })));
  const paint = () => map.restyle(d => { const n = nodeOf(d.g); return n ? { cls: 'k' + n.col, dim: st.hov != null && st.hov !== n.id, z: st.hov === n.id ? 2 : 1 } : { cls: 'low', f: 0.72, z: 0 }; });
  function texts() {
    map.label(t('clMapLabel')); const leg = $('#hmLegend'); leg.textContent = '';
    for (const n of Array.from(new Set(lab)).map(i => nodes[i]).sort((a, b) => a.rank - b.rank)) {
      const it = h('span', { class: 'it' }, swatch('k' + n.col), sh(n));
      it.addEventListener('mouseenter', () => { st.hov = n.id; paint(); }); it.addEventListener('mouseleave', () => { st.hov = null; paint(); });
      leg.append(it);
    }
    paint();
  }
  RERENDER.push(texts); texts();
}

// ============================================================ 1. clusters
function initClusters(saved) {
  const st = { k: saved.k >= 2 && saved.k <= 12 ? saved.k : 8, pin: null, hov: null, timer: null };
  const range = $('#kRange'), out = $('#kOut'), play = $('#kPlay');
  const mapPts = d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] }));
  const umPts = D.kept.map((g, j) => ({ id: g, g, nx: D.umapG[j][0], ny: D.umapG[j][1], x: 0, y: 0 }));
  const umByG = new Map(umPts.map(p => [p.g, p]));
  const nodeOf = g => { const j = keptPos[g]; return j < 0 ? null : nodes[D.labels[st.k][j]]; };
  const act = () => (st.hov != null ? st.hov : st.pin);
  const styleFn = d => {
    const n = nodeOf(d.g); if (!n) return { cls: 'low', f: 0.72, z: 0 };
    const a = act(); return { cls: 'k' + n.col, dim: a != null && a !== n.id, z: a === n.id ? 2 : 1 };
  };
  const tipFor = d => {
    const n = nodeOf(d.g), c = G.n[d.g];
    return [tipTitle(G.name[d.g]), tipLine(null, n ? nm(n) : t('lowData')), tipLine(String(c), t('motifsRecorded', c))];
  };
  const activeNodes = () => Array.from(new Set(D.labels[st.k])).map(i => nodes[i]).sort((a, b) => a.rank - b.rank);

  const map = new Plot($('#clMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true),
    hover: (d, e, mv) => { if (!d) { Tip.hide(); um.mark(null); return; } if (mv) return Tip.move(e); Tip.show(e, tipFor(d)); um.mark(umByG.get(d.g) || null); } }));
  const PAD = 28;
  const placeUm = p => { for (const d of umPts) { d.x = PAD + d.nx * (p.o.W - 2 * PAD); d.y = PAD + (1 - d.ny) * (p.o.H - 2 * PAD); } };
  const um = new Plot($('#clUmap'), { W: 600, H: 430, pixel: w => Math.max(300, Math.min(470, w * 0.74)), rPx: 3, sorted: true,
    hover: (d, e, mv) => { if (!d) { Tip.hide(); map.mark(null); return; } if (mv) return Tip.move(e); Tip.show(e, tipFor(d)); map.mark(mapPts[d.g]); },
    resize: p => { placeUm(p); p.applyScale(); drawLabels(); } });
  const labG = um.over.append('g');
  placeUm(um);
  map.setPoints(mapPts); um.setPoints(umPts);

  function drawLabels() {
    if (!um.sel) return;
    const fs = 12, W = um.o.W, H = um.o.H, a = act();
    const items = activeNodes().map(n => {
      const pts = umPts.filter(p => nodeOf(p.g) === n);
      return { n, x: d3.mean(pts, p => p.x), y: d3.mean(pts, p => p.y), w: sh(n).length * fs * 0.6 + 8, hh: fs * 1.35, size: pts.length };
    }).sort((p, q) => q.size - p.size);
    const placed = [];
    for (const it of items) {
      it.x = Math.max(it.w / 2 + 2, Math.min(W - it.w / 2 - 2, it.x));
      const y0 = it.y; let tr = 0;
      const hit = () => placed.some(p => Math.abs(p.x - it.x) < (p.w + it.w) / 2 && Math.abs(p.y - it.y) < (p.hh + it.hh) / 2);
      while (hit() && tr < 14) { tr++; it.y = y0 + (tr % 2 ? 1 : -1) * Math.ceil(tr / 2) * it.hh; }
      it.y = Math.max(it.hh, Math.min(H - it.hh, it.y)); placed.push(it);
    }
    labG.selectAll('text').data(items, d => d.n.id).join('text').attr('class', 'dlab').attr('x', d => d.x).attr('y', d => d.y)
      .attr('font-size', fs).attr('stroke-width', 3.5).text(d => sh(d.n)).attr('opacity', d => (a != null && a !== d.n.id ? 0.22 : 1));
  }
  function drawLegend() {
    const ul = $('#clLegend'); ul.textContent = '';
    for (const n of activeNodes()) {
      const b = h('button', { class: 'lg', type: 'button', 'data-node': n.id, 'aria-pressed': String(st.pin === n.id) }, swatch('k' + n.col), h('span', { text: nm(n) }), h('span', { class: 'ct', text: String(n.n) }));
      const on = () => { st.hov = n.id; soft(); }, off = () => { st.hov = null; soft(); };
      b.addEventListener('mouseenter', on); b.addEventListener('mouseleave', off); b.addEventListener('focus', on); b.addEventListener('blur', off);
      b.addEventListener('click', () => { st.pin = st.pin === n.id ? null : n.id; for (const x of ul.querySelectorAll('.lg')) x.setAttribute('aria-pressed', String(+x.dataset.node === st.pin)); soft(); });
      ul.append(h('li', null, b));
    }
    $('#clLegSub').textContent = '· ' + st.k;
  }
  let infoFor = -2;
  function drawInfo() {
    const a = act(), key = a == null ? -1 : a; if (key === infoFor) return; infoFor = key;
    const box = $('#clInfo'); box.textContent = '';
    if (a == null) { box.append(h('p', { class: 'hint', text: t('clHint') })); return; }
    const n = nodes[a];
    box.append(h('h4', { text: nm(n) }), h('p', { class: 'fine', text: t('clMeta', n.n, pc(n.shareA)) }), h('p', { class: 'fine', style: 'margin:8px 0 2px', text: t('clInd') }));
    const ol = h('ol', { class: 'mlist' });
    for (const [m, pin, pout] of n.ind) ol.append(h('li', null, motifBtn(m, pc(pin) + ' / ' + pc(pout))));
    const members = D.kept.filter((g, j) => D.labels[st.k][j] === n.id).map(g => G.name[g]).sort((x, y) => x.localeCompare(y));
    box.append(ol, h('p', { class: 'fine', style: 'margin-top:8px', text: t('clCore') + n.core.map(g => G.name[g]).join('; ') }),
      h('details', null, h('summary', { text: t('clAll', n.n) }), h('div', { class: 'names', text: members.join('; ') })));
  }
  function notes() {
    const sp = D.splits[st.k], p = nodes[sp.parent], kids = sp.children.map(i => nodes[i]).sort((a, b) => a.rank - b.rank);
    const s = $('#splitNote'); s.textContent = '';
    s.append(h('b', { text: t('step', st.k - 1, st.k) }), p.id === 0 ? t('splitAll') : t('splitOne', nm(p)), t('splitInto', nm(kids[0]), nm(kids[1])));
    const [same, chance] = D.coh[st.k], c = $('#cohNote'); c.textContent = '';
    c.append(t('coh1'), h('b', { text: pc(same) }), t('coh2'), h('b', { text: pc(chance) }), t('coh3'));
  }
  function soft() { map.restyle(styleFn); um.restyle(styleFn); drawLabels(); drawInfo(); }
  function texts() { map.label(t('clMapLabel')); um.label(t('clUmapLabel')); play.textContent = st.timer ? t('stop') : t('play'); infoFor = -2; drawLegend(); notes(); }
  function render() {
    STATE.k = st.k; range.value = st.k; out.textContent = st.k;
    if (st.pin != null && !D.labels[st.k].includes(st.pin)) st.pin = null;
    st.hov = null; texts(); soft();
  }
  const setK = k => { st.k = Math.max(2, Math.min(12, k)); render(); };
  const stop = () => { if (st.timer) { clearInterval(st.timer); st.timer = null; play.textContent = t('play'); } };
  range.addEventListener('input', () => { stop(); setK(+range.value); });
  $('#kMinus').addEventListener('click', () => { stop(); setK(st.k - 1); });
  $('#kPlus').addEventListener('click', () => { stop(); setK(st.k + 1); });
  play.addEventListener('click', () => {
    if (st.timer) return stop();
    st.timer = setInterval(() => { if (st.k >= 12) return stop(); setK(st.k + 1); }, 1500);
    setK(2);
  });
  RERENDER.push(() => { texts(); soft(); });
  render();
}

// ============================================================ 2. NMF complexes
function initNmf() {
  const cls = w => (w >= 90 ? 7 : w >= 75 ? 6 : w >= 60 ? 5 : w >= 45 ? 4 : w >= 30 ? 3 : w >= 15 ? 2 : 1);
  const grid = $('#nmfGrid'); let plots = [];
  function build() {
    for (const p of plots) p.destroy(); plots = []; grid.textContent = '';
    steps($('#nmfScale'), ['s1', 's2', 's3', 's4', 's5', 's6', 's7'], ['5–15%', '15–30%', '30–45%', '45–60%', '60–75%', '75–90%', t('nmfTop')]);
    for (const c of D.nmf) {
      const host = h('div'), list = h('ol', { class: 'mlist' });
      for (const m of c.motifs.slice(0, 6)) list.append(h('li', null, motifBtn(m)));
      grid.append(h('article', { class: 'ncard' },
        h('h3', null, h('span', { text: nm(c) }), h('span', { class: 'ct', text: nTrad(c.active) })),
        host, list, h('p', { class: 'fine', text: t('nmfStrong') + c.trad.slice(0, 5).map(g => G.name[g]).join('; ') })));
      const pts = []; D.kept.forEach((g, j) => { const w = c.w[j]; if (w >= 5) pts.push({ id: g, g, w, x: GXY[g][0], y: GXY[g][1] }); });
      const p = new Plot(host, Object.assign({}, MAPO, { rPx: 2.5, hitPx: 12, sorted: true, bg: mapBg(false),
        hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine(d.w + '%', t('nmfTip'))]); } }));
      p.label(t('nmfLabel', nm(c))).setPoints(pts).restyle(d => ({ cls: 's' + cls(d.w), f: 0.75 + 0.95 * d.w / 100, z: d.w }));
      plots.push(p);
    }
  }
  RERENDER.push(build);
  build();
}

// ============================================================ 3. principal axes
function initAxes(saved) {
  const TXT = {
    en: {
      A: [
        { pos: 'western and central Eurasia', neg: 'South America, Mesoamerica, Oceania, North America', note: 'The positive pole gathers the cosmological motifs of European and Near Eastern tales and legends. Africa, southern Asia and Siberia sit near zero.' },
        { pos: 'Africa, South America, southern Asia, Oceania', neg: 'Siberia and North America', note: 'Southern pole: the origin of death (the shed skin, the muddled message, the chameleon as messenger) and the rainbow serpent. Northern pole: the earth-diver. The picture is close to the contrast between the Indo-Pacific and Continental Eurasian complexes in Berezkin’s work.' },
        { pos: 'Africa, southern and eastern Asia', neg: 'South America', note: 'African and Asian pole: death through a falsified message, the chameleon as messenger, the immortal Moon (motif a36). Amazonian pole: the incestuous Moon, the sky of birds, animal lovers.' },
        { pos: 'Sub-Saharan Africa', neg: 'Mesoamerica, southern and eastern Asia', note: 'African pole: death brought by the chameleon and the falsified message. Opposite pole: several suns that burn the earth, the primeval couple of siblings, the four supports of the world; these motifs link East and Southeast Asia with Mesoamerica.' }
      ],
      B: [
        { pos: 'western and central Eurasia', neg: 'the Americas', note: 'The Eurasian stock of folktales against the New World. This axis is tied more than the others to how well a tradition is documented (correlation with the log number of motifs: 0.68), so part of the contrast reflects the volume of records.' },
        { pos: 'Sub-Saharan Africa', neg: 'North America, Siberia, Europe', note: 'African pole: the hare as trickster, the hyena as the loser, the tar baby.' },
        { pos: 'South America and Mesoamerica', neg: 'North America and Siberia', note: 'South American pole: the woman among jaguars, the children of a murdered mother. North American pole: the hoodwinked dancers, the raven as trickster.' },
        { pos: 'the Plains and western North America', neg: 'the Arctic and Siberia', note: 'Trickster episodes of the Plains (the bungling host) against the Raven cycle of the Arctic.' }
      ]
    },
    ru: {
      A: [
        { pos: 'запад и центр Евразии', neg: 'Южная Америка, Мезоамерика, Океания, Северная Америка', note: 'Положительный полюс собирают космологические мотивы европейских и ближневосточных сказок и легенд. Африка, юг Азии и Сибирь лежат около нуля.' },
        { pos: 'Африка, Южная Америка, юг Азии, Океания', neg: 'Сибирь и Северная Америка', note: 'Южный полюс: происхождение смерти (сброшенная кожа, перепутанная весть, хамелеон-вестник) и радужный змей. Северный полюс: ныряльщик за землёй. Картина близка к противопоставлению индо-тихоокеанского и континентально-евразийского комплексов у Берёзкина.' },
        { pos: 'Африка, юг и восток Азии', neg: 'Южная Америка', note: 'Африкано-азиатский полюс: смерть из-за ложной вести, хамелеон-вестник, бессмертная Луна (мотив a36). Амазонский полюс: инцест Луны, небо птиц, любовники-животные.' },
        { pos: 'Африка южнее Сахары', neg: 'Мезоамерика, юг и восток Азии', note: 'Африканский полюс: смерть из-за хамелеона и ложной вести. Противоположный полюс: несколько солнц, сжигающих землю, первая пара из брата и сестры, четыре опоры мира; эти мотивы связывают Восточную и Юго-Восточную Азию с Мезоамерикой.' }
      ],
      B: [
        { pos: 'запад и центр Евразии', neg: 'Америка', note: 'Сказочный фонд Евразии против Нового Света. Эта ось сильнее других связана с изученностью традиции (корреляция с логарифмом числа мотивов 0,68), поэтому часть контраста отражает объём записей.' },
        { pos: 'Африка южнее Сахары', neg: 'Северная Америка, Сибирь, Европа', note: 'Африканский полюс: трикстер-заяц, гиена-неудачница, смоляное чучело.' },
        { pos: 'Южная Америка и Мезоамерика', neg: 'Северная Америка и Сибирь', note: 'Южноамериканский полюс: женщина у ягуаров, дети убитой матери. Североамериканский: обманутые танцоры, трикстер-ворон.' },
        { pos: 'Равнины и запад Северной Америки', neg: 'Арктика и Сибирь', note: 'Трикстерские эпизоды Равнин (неудачное подражание хозяину) против арктического цикла Ворона.' }
      ]
    }
  };
  const st = { set: saved.axSet === 'B' ? 'B' : 'A', ax: saved.ax >= 0 && saved.ax <= 3 ? saved.ax : 1 };
  const cls = v => (v > 85 ? 'dp4' : v > 60 ? 'dp3' : v > 35 ? 'dp2' : v > 12 ? 'dp1' : v >= -12 ? 'd0' : v >= -35 ? 'dn1' : v >= -60 ? 'dn2' : v >= -85 ? 'dn3' : 'dn4');
  steps($('#axScale'), ['dn4', 'dn3', 'dn2', 'dn1', 'd0', 'dp1', 'dp2', 'dp3', 'dp4']);
  const plot = new Plot($('#axMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true),
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine((d.v > 0 ? '+' : d.v < 0 ? '−' : '') + Math.abs(d.v), t('axTip'))]); } }));
  const setSet = segInit($('#axSet'), v => { st.set = v; render(); });
  const setNum = segInit($('#axNum'), v => { st.ax = +v; render(); });
  function pole(host, color, title, motifs, trad) {
    host.textContent = '';
    const dot = h('i'); dot.style.background = `var(--${color})`;
    const ol = h('ol', { class: 'mlist' }); for (const m of motifs) ol.append(h('li', null, motifBtn(m)));
    host.append(h('h3', null, dot, h('span', { text: title })), ol, h('p', { class: 'fine tr', text: t('axPole') + trad.map(g => G.name[g]).join('; ') }));
  }
  function render() {
    STATE.axSet = st.set; STATE.ax = st.ax; setSet(st.set); setNum(st.ax);
    const S = D.axes[st.set], a = S.ax[st.ax], tx = TXT[LANG][st.set][st.ax];
    const pts = S.g.map((g, j) => ({ id: g, g, v: a.s[j], x: GXY[g][0], y: GXY[g][1] }));
    plot.label(t('axMapLabel')).setPoints(pts).restyle(d => ({ cls: cls(d.v), z: Math.abs(d.v) }));
    const up = s => s.charAt(0).toUpperCase() + s.slice(1);
    $('#axNegLab').textContent = tx.neg; $('#axPosLab').textContent = tx.pos;
    const n = $('#axNote'); n.textContent = '';
    n.append(h('b', { text: t('axis', st.ax + 1, tx.neg, tx.pos) }), tx.note);
    $('#axCap').textContent = t('axCap', dec(String(a.var)), S.g.length, S.nm);
    pole($('#axNeg'), 'dn3', up(tx.neg), a.neg, a.negT); pole($('#axPos'), 'dp3', up(tx.pos), a.pos, a.posT);
  }
  RERENDER.push(render);
  render();
}

// ============================================================ 4. motif atlas
function initMotifs(saved) {
  const A = D.atlas, REGN = A.regs.map(i => nodes[i]);
  const atlasPos = new Int32Array(NM).fill(-1); A.m.forEach((m, j) => { atlasPos[m] = j; });
  const mById = new Map(M.id.map((id, m) => [id, m]));
  const st = { m: mById.has(saved.motif) ? mById.get(saved.motif) : mById.get('a36') };
  const l3 = D.labels[3], regSize = REGN.map(n => n.n), regIdx = new Map(A.regs.map((id, i) => [id, i]));
  const umPts = A.m.map((m, j) => ({ id: m, m, nx: A.xy[j][0], ny: A.xy[j][1], home: A.home[j], x: 0, y: 0 }));
  const PAD = 16;
  const place = p => { for (const d of umPts) { d.x = PAD + d.nx * (p.o.W - 2 * PAD); d.y = PAD + (1 - d.ny) * (p.o.H - 2 * PAD); } };
  const homeName = i => (i < 3 ? sh(REGN[i]) : t('wide'));
  const um = new Plot($('#moUmap'), { W: 600, H: 480, pixel: w => Math.max(320, Math.min(560, w * 0.86)), rPx: 2.5, hitPx: 12,
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [...motifTip(d.m), h('div', { class: 'dh', text: nTrad(mDf[d.m]) + ' · ' + (d.home < 3 ? t('moMostIn', homeName(d.home)) : t('wide')) })], 'wide'); },
    click: d => selectMotif(d.m, false), resize: p => { place(p); p.applyScale(); ring(); } });
  const selRing = um.over.append('circle').attr('class', 'sel-ring').attr('display', 'none');
  const ring = () => { const j = atlasPos[st.m]; if (j < 0) return selRing.attr('display', 'none'); const d = umPts[j]; selRing.attr('display', null).attr('cx', d.x).attr('cy', d.y).attr('r', 8); };
  place(um); um.setPoints(umPts).restyle(d => ({ cls: d.home < 3 ? 'k' + REGN[d.home].col : 'nul', f: d.home < 3 ? 1 : 0.85 }));
  const counts = [0, 0, 0, 0]; for (const v of A.home) counts[v]++;
  const mapPts = d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] }));
  let has = new Uint8Array(NG);
  const map = new Plot($('#moMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, rPx: 3.1, bg: mapBg(true),
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine(null, has[d.g] ? t('moHas') : t('moHasNot')), tipLine(String(G.n[d.g]), t('moTotal', G.n[d.g]))]); } }));
  map.setPoints(mapPts);
  const similar = m => {
    const cnt = new Map(); for (const g of D.inc[m]) for (const n of gMot[g]) if (n !== m) cnt.set(n, (cnt.get(n) || 0) + 1);
    const res = []; for (const [n, c] of cnt) { if (c < 3) continue; res.push([n, c / (mDf[m] + mDf[n] - c)]); }
    return res.sort((a, b) => b[1] - a[1]).slice(0, 6);
  };
  function render() {
    const m = st.m; STATE.motif = M.id[m];
    um.label(t('moUmapLabel')); map.label(t('moMapLabel'));
    const leg = $('#moLegend'); leg.textContent = '';
    for (let i = 0; i < 4; i++) leg.append(h('span', { class: 'it' }, swatch(i < 3 ? 'k' + REGN[i].col : 'nul'), `${homeName(i)} · ${nf(counts[i])}`));
    $('#moUmapCap').textContent = t('moUmapCap', A.m.length);
    has = new Uint8Array(NG); for (const g of D.inc[m]) has[g] = 1;
    map.restyle(d => (has[d.g] ? { cls: 'on', z: 1, f: 1.2 } : { cls: 'nul', z: 0, f: 0.55 }));
    ring();
    const head = $('#moHead'); head.textContent = '';
    head.append(h('div', { class: 'idline' }, h('span', { class: 'bigcode', text: M.id[m] }), h('span', { class: 'ttl', text: mT(m) })),
      h('div', { class: 'desc' }, ...motifDesc(m)),
      h('p', { class: 'meta' }, t('moMeta', M.id[m][0].toUpperCase(), mIsA[m], mDf[m], NG), h('a', { href: `https://www.ruthenia.ru/folklore/berezkin/${M.id[m]}.html`, text: t('moLink') }), ' · ',
        h('a', { href: '#correlations', text: t('moCor'), onclick: e => { e.preventDefault(); e.stopPropagation(); openCor('m', M.id[m]); } })));
    $('#moMapCap').textContent = t('moMapCap', M.id[m]);
    const side = $('#moSide'); side.textContent = '';
    const cnt = [0, 0, 0]; for (const g of D.inc[m]) { const j = keptPos[g]; if (j >= 0) cnt[regIdx.get(l3[j])]++; }
    const meters = h('div', { class: 'meters' });
    REGN.forEach((n, i) => {
      const share = cnt[i] / regSize[i], fill = h('div', { class: 'fill' }); fill.style.width = (share * 100).toFixed(1) + '%'; fill.style.background = `var(--k${n.col})`;
      meters.append(h('div', { class: 'meter' }, h('div', { class: 'top' }, h('span', { text: nm(n) }), h('span', { class: 'v', text: t('moOf', pc(share), cnt[i], regSize[i]) })), h('div', { class: 'track' }, fill)));
    });
    side.append(h('div', { class: 'info' }, h('h4', { text: t('moShare') }), meters, h('p', { class: 'fine', style: 'margin-top:6px', text: t('moAreas') })));
    const sim = similar(m);
    if (sim.length) {
      const ol = h('ol', { class: 'mlist' }); for (const [n, j] of sim) ol.append(h('li', null, motifBtn(n, f2(j), true)));
      side.append(h('div', { class: 'info' }, h('h4', { text: t('moSimilar') }), ol, h('p', { class: 'fine', style: 'margin-top:6px', text: t('moJacc') })));
    }
    const names = D.inc[m].map(g => G.name[g]).sort((a, b) => a.localeCompare(b));
    side.append(h('details', null, h('summary', { text: t('moAll', names.length) }), h('div', { class: 'names', text: names.join('; ') })));
  }
  selectMotif = (m, scroll) => {
    st.m = m; render();
  };
  picker($('#moSearch'), { items: motifItems, row: motifRow, pick: o => selectMotif(o.m, false) });
  RERENDER.push(render);
  render();
}

/*@@VIEWS@@*/

// ============================================================ boot: tabs, lazy views, language
const VIEWS = { home: initHome, clusters: initClusters, tree: initTree, axes: initAxes, complexes: initNmf, motifs: initMotifs, correlations: initCorrelations, method: null };
const inited = {};
let currentView = null;
function show(id) {
  if (!(id in VIEWS)) id = 'home';
  if (id === currentView) return;
  const first = currentView === null; currentView = id; STATE.tab = id; Tip.hide();
  for (const s of document.querySelectorAll('main > section')) s.hidden = s.id !== id;
  $('#mast').hidden = id !== 'home';
  for (const a of document.querySelectorAll('#tabs a')) {
    if (a.dataset.tab !== id) { a.removeAttribute('aria-current'); continue; }
    a.setAttribute('aria-current', 'page'); const row = a.parentNode;
    if (row.scrollWidth > row.clientWidth) row.scrollLeft = a.offsetLeft - (row.clientWidth - a.offsetWidth) / 2;
  }
  if (!first) window.scrollTo(0, 0);
  if (!inited[id] && VIEWS[id]) { inited[id] = true; VIEWS[id](STATE); }
}
function go(id) {
  if (!(id in VIEWS)) id = 'home';
  if (location.hash.slice(1) !== id) { try { history.pushState(null, '', '#' + id); } catch (e) { /* a sandboxed frame may refuse */ } }
  show(id);
}
openMotif = m => { STATE.motif = M.id[m]; if (inited.motifs) selectMotif(m); go('motifs'); };
openCor = (mode, a, b) => { STATE.corMode = mode; STATE.corA = a; STATE.corB = b || null; if (corSet) corSet(mode, a, b || null); go('correlations'); };
const fromHash = () => { try { return decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; } };
function facts() { $('#fG').textContent = nf(D.meta.nG); $('#fM').textContent = nf(D.meta.nM); $('#fP').textContent = nf(D.meta.nPairs); $('#fMed').textContent = nf(D.meta.medianM); }
function setLang(l) {
  LANG = l === 'ru' ? 'ru' : 'en'; STATE.lang = LANG; document.documentElement.lang = LANG;
  try { localStorage.setItem('comparanda-lang', LANG); } catch (e) { /* storage is optional */ }
  for (const b of document.querySelectorAll('#langSeg button')) b.setAttribute('aria-pressed', String(b.dataset.v === LANG));
  applyAttrs(); Tip.hide();
  for (const f of RERENDER) f();
}
function start(saved) {
  Object.assign(STATE, saved || {});
  let stored = null; try { stored = localStorage.getItem('comparanda-lang'); } catch (e) { /* storage is optional */ }
  LANG = (STATE.lang || stored) === 'ru' ? 'ru' : 'en'; STATE.lang = LANG; document.documentElement.lang = LANG;
  for (const b of document.querySelectorAll('#langSeg button')) b.setAttribute('aria-pressed', String(b.dataset.v === LANG));
  $('#langSeg').addEventListener('click', e => { const b = e.target.closest('button'); if (b && b.dataset.v !== LANG) setLang(b.dataset.v); });
  document.addEventListener('click', e => {
    const a = e.target.closest ? e.target.closest('a[href^="#"]') : null; if (!a) return;
    const id = a.getAttribute('href').slice(1); if (!(id in VIEWS)) return;
    e.preventDefault(); go(id);
  });
  window.addEventListener('popstate', () => show(fromHash()));
  window.addEventListener('hashchange', () => show(fromHash()));
  applyAttrs(); facts(); RERENDER.push(facts);
  const h0 = fromHash();
  show(h0 in VIEWS ? h0 : (STATE.tab in VIEWS ? STATE.tab : 'home'));
  window.__ready = true;
}
const hot = window.claude && window.claude.hot;
if (hot && hot.snapshot) hot.snapshot(() => STATE);
if (hot && hot.ready) hot.ready(start); else start((hot && hot.data) || {});
})();
