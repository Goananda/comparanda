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
const nf = new Intl.NumberFormat('ru-RU');
const f2 = v => v.toFixed(2).replace('.', ',');
const f3 = v => v.toFixed(3).replace('.', ',');
const pc = v => Math.round(v * 100) + '%';
const plural = (n, one, few, many) => { const a = Math.abs(n) % 100, b = a % 10; return a > 10 && a < 20 ? many : b === 1 ? one : b >= 2 && b <= 4 ? few : many; };
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const STATE = {};

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
const SYMS = [d3.symbol(d3.symbolCircle, 50)(), d3.symbol(d3.symbolDiamond, 46)(), d3.symbol(d3.symbolTriangle, 46)(), d3.symbol(d3.symbolSquare, 46)()];
const NSVG = 'http://www.w3.org/2000/svg';
const defs = document.getElementById('geo-defs');
for (const [id, d] of [['geo-land', GEO.land], ['geo-grat', GEO.grat], ['geo-sphere', GEO.sphere]]) {
  const p = document.createElementNS(NSVG, 'path'); p.setAttribute('id', id); p.setAttribute('d', d); defs.append(p);
}
const mapBg = grat => g => { if (grat) g.append('use').attr('href', '#geo-grat'); g.append('use').attr('href', '#geo-land'); if (grat) g.append('use').attr('href', '#geo-sphere'); };
const MAPO = { W: GEO.W, H: GEO.H, y0: GEO.y0 };
const swatch = (cls, shape) => {
  const s = document.createElementNS(NSVG, 'svg'); s.setAttribute('class', 'sw'); s.setAttribute('viewBox', '-8 -8 16 16'); s.setAttribute('aria-hidden', 'true');
  const p = document.createElementNS(NSVG, 'path'); p.setAttribute('d', SYMS[shape || 0]); p.setAttribute('class', 'mk ' + cls); p.setAttribute('transform', 'scale(1.35)'); s.append(p); return s;
};
const steps = (host, vars, titles) => { host.textContent = ''; vars.forEach((v, i) => { const s = h('i'); s.style.background = 'var(--' + v + ')'; if (titles) s.title = titles[i]; host.append(s); }); };

const tipEl = $('#tip');
const Tip = {
  show(e, rows) { tipEl.textContent = ''; for (const r of rows) tipEl.append(r); tipEl.hidden = false; this.move(e); },
  move(e) {
    const pad = 14, w = tipEl.offsetWidth, hh = tipEl.offsetHeight;
    let x = e.clientX + pad, y = e.clientY + pad;
    if (x + w > innerWidth - 8) x = e.clientX - w - pad;
    if (y + hh > innerHeight - 8) y = e.clientY - hh - pad;
    tipEl.style.left = Math.max(8, x) + 'px'; tipEl.style.top = Math.max(8, y) + 'px';
  },
  hide() { tipEl.hidden = true; }
};
const tipTitle = t => h('div', { class: 'tt', text: t });
const tipLine = (strong, rest) => h('div', { class: 'tl' }, strong != null ? h('b', { text: strong }) : null, rest != null ? h('span', { text: rest }) : null);

class Plot {
  constructor(host, o) {
    this.host = host; this.o = Object.assign({ y0: 0, rPx: 3.4, hitPx: 16 }, o);
    this.k = 1; this.u = 1; this.rs = 1; this.pts = []; this.hov = null; this.ext = null; this.sel = null; this.styleFn = () => ({ cls: 'nul' });
    host.classList.add('plot');
    const svg = this.svg = d3.select(host).append('svg').attr('role', 'img').attr('aria-label', this.o.label || '');
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
    new ResizeObserver(() => this.measure()).observe(host);
  }
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
  setPoints(pts) { this.pts = pts; this.hov = null; this.ext = null; this.sel = this.marks.selectAll('path').data(pts, d => d.id).join('path'); return this; }
  restyle(fn) {
    if (fn) this.styleFn = fn; if (!this.sel) return this; const self = this;
    this.sel.each(function (d) {
      const s = d._s = self.styleFn(d);
      this.setAttribute('class', 'mk ' + s.cls + (s.dim ? ' dim' : ''));
      this.setAttribute('d', SYMS[s.shape || 0]);
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
    const go = (fn, a) => { const t = reduceMotion ? this.svg : this.svg.transition().duration(260); t.call(fn, a); };
    const mk = (txt, label, fn) => h('button', { type: 'button', class: 'zb', 'aria-label': label, title: label, text: txt, onclick: fn });
    this.host.append(h('div', { class: 'zoombar' },
      mk('+', 'Приблизить', () => go(z.scaleBy, 1.8)), mk('−', 'Отдалить', () => go(z.scaleBy, 1 / 1.8)), mk('⟲', 'Показать весь мир', () => go(z.transform, d3.zoomIdentity))));
  }
}

let selectMotif = () => {};
const motifBtn = (m, val, noScroll) => h('button', { class: 'mref', type: 'button', title: 'Открыть карту мотива в атласе', onclick: () => selectMotif(m, !noScroll) },
  h('span', { class: 'code', text: M.id[m] }), h('span', { text: M.title[m] }), val ? h('span', { class: 'val', text: val }) : null);
const segInit = (host, cb) => {
  host.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; cb(b.dataset.v); });
  return v => { for (const b of host.querySelectorAll('button')) b.setAttribute('aria-pressed', String(b.dataset.v === String(v))); };
};

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
    const a = act(); return { cls: 'c' + n.hue, shape: n.shape, dim: a != null && a !== n.id, z: a === n.id ? 2 : 1 };
  };
  const tipFor = d => {
    const n = nodeOf(d.g), c = G.n[d.g];
    return [tipTitle(G.name[d.g]), tipLine(null, n ? n.name : 'Меньше 15 мотивов, в расчёт не входила'), tipLine(String(c), plural(c, 'мотив записан', 'мотива записано', 'мотивов записано'))];
  };
  const activeNodes = () => Array.from(new Set(D.labels[st.k])).map(i => nodes[i]).sort((a, b) => a.rank - b.rank);

  const map = new Plot($('#clMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true), label: 'Карта мира: традиции окрашены по кластерам сходства мотивов',
    hover: (d, e, mv) => { if (!d) { Tip.hide(); um.mark(null); return; } if (mv) return Tip.move(e); Tip.show(e, tipFor(d)); um.mark(umByG.get(d.g) || null); } }));
  const PAD = 28;
  const placeUm = p => { for (const d of umPts) { d.x = PAD + d.nx * (p.o.W - 2 * PAD); d.y = PAD + (1 - d.ny) * (p.o.H - 2 * PAD); } };
  const um = new Plot($('#clUmap'), { W: 600, H: 430, pixel: w => Math.max(300, Math.min(470, w * 0.74)), rPx: 3, sorted: true, label: 'Традиции в пространстве сходства, проекция UMAP',
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
      return { n, x: d3.mean(pts, p => p.x), y: d3.mean(pts, p => p.y), w: n.short.length * fs * 0.6 + 8, hh: fs * 1.35, size: pts.length };
    }).sort((p, q) => q.size - p.size);
    const placed = [];
    for (const it of items) {
      it.x = Math.max(it.w / 2 + 2, Math.min(W - it.w / 2 - 2, it.x));
      const y0 = it.y; let t = 0;
      const hit = () => placed.some(p => Math.abs(p.x - it.x) < (p.w + it.w) / 2 && Math.abs(p.y - it.y) < (p.hh + it.hh) / 2);
      while (hit() && t < 14) { t++; it.y = y0 + (t % 2 ? 1 : -1) * Math.ceil(t / 2) * it.hh; }
      it.y = Math.max(it.hh, Math.min(H - it.hh, it.y)); placed.push(it);
    }
    labG.selectAll('text').data(items, d => d.n.id).join('text').attr('class', 'dlab').attr('x', d => d.x).attr('y', d => d.y)
      .attr('font-size', fs).attr('stroke-width', 3.5).text(d => d.n.short).attr('opacity', d => (a != null && a !== d.n.id ? 0.22 : 1));
  }
  function drawLegend() {
    const ul = $('#clLegend'); ul.textContent = '';
    for (const n of activeNodes()) {
      const b = h('button', { class: 'lg', type: 'button', 'data-node': n.id, 'aria-pressed': String(st.pin === n.id) }, swatch('c' + n.hue, n.shape), h('span', { text: n.name }), h('span', { class: 'ct', text: String(n.n) }));
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
    if (a == null) { box.append(h('p', { class: 'hint', text: 'Наведите на кластер в списке, чтобы выделить его на карте и увидеть характерные мотивы. Щелчок закрепляет выбор.' })); return; }
    const n = nodes[a];
    box.append(h('h4', { text: n.name }),
      h('p', { class: 'fine', text: `${n.n} ${plural(n.n, 'традиция', 'традиции', 'традиций')} · медианная доля космологических мотивов ${pc(n.shareA)}` }),
      h('p', { class: 'fine', style: 'margin:8px 0 2px', text: 'Характерные мотивы: доля традиций с мотивом в кластере и вне его' }));
    const ol = h('ol', { class: 'mlist' });
    for (const [m, pin, pout] of n.ind) ol.append(h('li', null, motifBtn(m, pc(pin) + ' / ' + pc(pout))));
    const members = D.kept.filter((g, j) => D.labels[st.k][j] === n.id).map(g => G.name[g]).sort((x, y) => x.localeCompare(y));
    box.append(ol, h('p', { class: 'fine', style: 'margin-top:8px', text: 'Ближе всего к центру кластера: ' + n.core.map(g => G.name[g]).join('; ') }),
      h('details', null, h('summary', { text: `Все ${n.n} ${plural(n.n, 'традиция', 'традиции', 'традиций')} кластера` }), h('div', { class: 'names', text: members.join('; ') })));
  }
  function notes() {
    const sp = D.splits[st.k], p = nodes[sp.parent], kids = sp.children.map(i => nodes[i]).sort((a, b) => a.rank - b.rank);
    const s = $('#splitNote'); s.textContent = '';
    s.append(h('b', { text: `Шаг ${st.k - 1} → ${st.k}. ` }), p.id === 0 ? 'Все традиции делятся' : `Кластер «${p.name}» делится`, ` на «${kids[0].name}» и «${kids[1].name}».`);
    const [same, chance] = D.coh[st.k], c = $('#cohNote'); c.textContent = '';
    c.append('Из десяти географически ближайших соседей каждой традиции ', h('b', { text: pc(same) }), ' попадают в её же кластер. При случайном разбиении на кластеры таких же размеров было бы ', h('b', { text: pc(chance) }), '.');
  }
  function soft() { map.restyle(styleFn); um.restyle(styleFn); drawLabels(); drawInfo(); }
  function render() {
    STATE.k = st.k; range.value = st.k; out.textContent = st.k;
    if (st.pin != null && !D.labels[st.k].includes(st.pin)) st.pin = null;
    st.hov = null; infoFor = -2; drawLegend(); notes(); soft();
  }
  const setK = k => { st.k = Math.max(2, Math.min(12, k)); render(); };
  const stop = () => { if (st.timer) { clearInterval(st.timer); st.timer = null; play.textContent = '▶ Показать по шагам'; } };
  range.addEventListener('input', () => { stop(); setK(+range.value); });
  $('#kMinus').addEventListener('click', () => { stop(); setK(st.k - 1); });
  $('#kPlus').addEventListener('click', () => { stop(); setK(st.k + 1); });
  play.addEventListener('click', () => {
    if (st.timer) return stop();
    play.textContent = '■ Остановить'; setK(2);
    st.timer = setInterval(() => { if (st.k >= 12) return stop(); setK(st.k + 1); }, 1500);
  });
  render();
}

// ============================================================ 2. NMF complexes
function initNmf() {
  const cls = w => (w >= 90 ? 7 : w >= 75 ? 6 : w >= 60 ? 5 : w >= 45 ? 4 : w >= 30 ? 3 : w >= 15 ? 2 : 1);
  steps($('#nmfScale'), ['s1', 's2', 's3', 's4', 's5', 's6', 's7'], ['5–15%', '15–30%', '30–45%', '45–60%', '60–75%', '75–90%', '90% и выше']);
  const grid = $('#nmfGrid');
  for (const c of D.nmf) {
    const host = h('div');
    const list = h('ol', { class: 'mlist' });
    for (const m of c.motifs.slice(0, 6)) list.append(h('li', null, motifBtn(m)));
    grid.append(h('article', { class: 'ncard' },
      h('h3', null, h('span', { text: c.name }), h('span', { class: 'ct', text: `${c.active} ${plural(c.active, 'традиция', 'традиции', 'традиций')}` })),
      host, list, h('p', { class: 'fine', text: 'Сильнее всего: ' + c.trad.slice(0, 5).map(g => G.name[g]).join('; ') })));
    const pts = []; D.kept.forEach((g, j) => { const w = c.w[j]; if (w >= 5) pts.push({ id: g, g, w, x: GXY[g][0], y: GXY[g][1] }); });
    const p = new Plot(host, Object.assign({}, MAPO, { rPx: 2.5, hitPx: 12, sorted: true, bg: mapBg(false), label: `Карта комплекса «${c.name}»: традиции, где набор мотивов выражен`,
      hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine(d.w + '%', 'от максимального веса набора')]); } }));
    p.setPoints(pts).restyle(d => ({ cls: 's' + cls(d.w), f: 0.75 + 0.95 * d.w / 100, z: d.w }));
  }
}

// ============================================================ 3. principal axes
function initAxes(saved) {
  const TXT = {
    A: [
      { pos: 'запад и центр Евразии', neg: 'Южная Америка, Мезоамерика, Океания, Северная Америка', note: 'Положительный полюс собирают космологические мотивы европейских и ближневосточных сказок и легенд. Африка, юг Азии и Сибирь лежат около нуля.' },
      { pos: 'Африка, Южная Америка, юг Азии, Океания', neg: 'Сибирь и Северная Америка', note: 'Южный полюс: происхождение смерти (сброшенная кожа, перепутанная весть), радужный змей, пятна на Луне. Северный полюс: ныряльщик за землёй. Картина близка к противопоставлению индо-тихоокеанского и континентально-евразийского комплексов у Берёзкина.' },
      { pos: 'Африка, юг и восток Азии', neg: 'Южная Америка', note: 'Африкано-азиатский полюс: смерть из-за ложной вести, хамелеон-вестник, бессмертная Луна (мотив a36). Амазонский полюс: инцест Луны, небо птиц, любовники-животные.' },
      { pos: 'запад Северной Америки', neg: 'Сибирь', note: 'Внутри северного мира Сибирь (Большая Медведица как копытное, Млечный Путь как лыжня) отделяется от запада Северной Америки, где смерть связана с Койотом.' }
    ],
    B: [
      { pos: 'запад и центр Евразии', neg: 'Америка', note: 'Сказочный фонд Евразии против Нового Света. Эта ось сильнее других связана с изученностью традиции (корреляция с логарифмом числа мотивов 0,69), поэтому часть контраста отражает объём записей.' },
      { pos: 'Африка южнее Сахары', neg: 'Северная Америка, Сибирь, Европа', note: 'Африканский полюс: трикстер-заяц, гиена-неудачница, смоляное чучело.' },
      { pos: 'Южная Америка и Мезоамерика', neg: 'Северная Америка и Сибирь', note: 'Южноамериканский полюс: женщина у ягуаров, дети убитой матери. Североамериканский: обманутые танцоры, трикстер-ворон.' },
      { pos: 'Равнины и запад Северной Америки', neg: 'Арктика и Сибирь', note: 'Трикстерские эпизоды Равнин (неудачное подражание хозяину) против арктического цикла Ворона.' }
    ]
  };
  const st = { set: saved.axSet === 'B' ? 'B' : 'A', ax: saved.ax >= 0 && saved.ax <= 3 ? saved.ax : 1 };
  const cls = v => (v > 85 ? 'dp4' : v > 60 ? 'dp3' : v > 35 ? 'dp2' : v > 12 ? 'dp1' : v >= -12 ? 'd0' : v >= -35 ? 'dn1' : v >= -60 ? 'dn2' : v >= -85 ? 'dn3' : 'dn4');
  steps($('#axScale'), ['dn4', 'dn3', 'dn2', 'dn1', 'd0', 'dp1', 'dp2', 'dp3', 'dp4']);
  const plot = new Plot($('#axMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true), label: 'Карта мира: положение традиций на главной оси',
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine((d.v > 0 ? '+' : d.v < 0 ? '−' : '') + Math.abs(d.v), 'положение на оси, от −100 до +100')]); } }));
  const setSet = segInit($('#axSet'), v => { st.set = v; render(); });
  const setNum = segInit($('#axNum'), v => { st.ax = +v; render(); });
  function pole(host, color, title, motifs, trad) {
    host.textContent = '';
    const dot = h('i'); dot.style.background = `var(--${color})`;
    const ol = h('ol', { class: 'mlist' }); for (const m of motifs) ol.append(h('li', null, motifBtn(m)));
    host.append(h('h3', null, dot, h('span', { text: title })), ol, h('p', { class: 'fine tr', text: 'Традиции у полюса: ' + trad.map(g => G.name[g]).join('; ') }));
  }
  function render() {
    STATE.axSet = st.set; STATE.ax = st.ax; setSet(st.set); setNum(st.ax);
    const S = D.axes[st.set], a = S.ax[st.ax], t = TXT[st.set][st.ax];
    const pts = S.g.map((g, j) => ({ id: g, g, v: a.s[j], x: GXY[g][0], y: GXY[g][1] }));
    plot.setPoints(pts).restyle(d => ({ cls: cls(d.v), z: Math.abs(d.v) }));
    const up = s => s.charAt(0).toUpperCase() + s.slice(1);
    $('#axNegLab').textContent = t.neg; $('#axPosLab').textContent = t.pos;
    const n = $('#axNote'); n.textContent = '';
    n.append(h('b', { text: `Ось ${st.ax + 1}: ${t.neg} ↔ ${t.pos}. ` }), t.note);
    $('#axCap').textContent = `Ось объясняет ${String(a.var).replace('.', ',')}% разброса. В расчёт вошли ${nf.format(S.g.length)} ${plural(S.g.length, 'традиция', 'традиции', 'традиций')} с 15 и более мотивами этой группы и ${nf.format(S.nm)} ${plural(S.nm, 'мотив', 'мотива', 'мотивов')}. Значения нормированы так, что ±100 соответствует 97-му процентилю.`;
    pole($('#axNeg'), 'dn3', up(t.neg), a.neg, a.negT); pole($('#axPos'), 'dp3', up(t.pos), a.pos, a.posT);
  }
  render();
}

// ============================================================ 4. relatives and distance decay
function initRel(saved) {
  const inSet = { all: () => true, A: m => mIsA[m], B: m => !mIsA[m] };
  const prep = {};
  const getPrep = s => {
    if (prep[s]) return prep[s];
    const f = inSet[s], elig = new Uint8Array(NG); let ne = 0;
    for (let g = 0; g < NG; g++) { let c = 0; for (const m of gMot[g]) if (f(m)) c++; if (c >= 10) { elig[g] = 1; ne++; } }
    const idf = new Float64Array(NM);
    for (let m = 0; m < NM; m++) { if (!f(m)) continue; let df = 0; for (const g of D.inc[m]) df += elig[g]; idf[m] = df > 0 ? Math.log(ne / df) : 0; }
    const norm = new Float64Array(NG);
    for (let g = 0; g < NG; g++) { if (!elig[g]) continue; let q = 0; for (const m of gMot[g]) q += idf[m] * idf[m]; norm[g] = Math.sqrt(q); }
    return (prep[s] = { elig, idf, norm, ne });
  };
  const sims = (s, f) => {
    const p = getPrep(s), acc = new Float64Array(NG), out = new Float64Array(NG).fill(NaN);
    if (!p.elig[f]) return out;
    for (const m of gMot[f]) { const w = p.idf[m]; if (!w) continue; const w2 = w * w; for (const g of D.inc[m]) acc[g] += w2; }
    for (let g = 0; g < NG; g++) if (p.elig[g] && p.norm[g] > 0) out[g] = acc[g] / (p.norm[f] * p.norm[g]);
    return out;
  };
  const TH = [0.03, 0.06, 0.10, 0.15, 0.22, 0.32];
  const cls = v => { if (!(v > 0)) return 'nul'; let c = 1; for (const t of TH) if (v >= t) c++; return 's' + c; };
  steps($('#relScale'), ['s1', 's2', 's3', 's4', 's5', 's6', 's7'], ['ниже 0,03', '0,03–0,06', '0,06–0,10', '0,10–0,15', '0,15–0,22', '0,22–0,32', '0,32 и выше']);
  $('#relScale').prepend(h('i', { class: 't', text: '0' })); $('#relScale').append(h('i', { class: 't', text: '0,32+' }));
  const st = { set: ['all', 'A', 'B'].includes(saved.relSet) ? saved.relSet : 'all', f: gByName.has(saved.focus) ? gByName.get(saved.focus) : gByName.get('Chukchi') };
  const dl = $('#relNames'); for (const n of G.name.slice().sort((a, b) => a.localeCompare(b))) dl.append(h('option', { value: n }));
  const mapPts = d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] }));
  let S = null, dist = null, scPts = [], scByG = new Map();
  const tipFor = g => {
    if (g === st.f) return [tipTitle(G.name[g]), tipLine(null, 'выбранная традиция')];
    if (isNaN(S[g])) return [tipTitle(G.name[g]), tipLine(null, 'меньше 10 мотивов этой группы')];
    return [tipTitle(G.name[g]), tipLine(f2(S[g]), 'сходство с ' + G.name[st.f]), tipLine(nf.format(Math.round(dist[g] / 10) * 10) + ' км', 'расстояние')];
  };
  const map = new Plot($('#relMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true), label: 'Карта мира: сходство традиций с выбранной',
    hover: (d, e, mv) => { if (!d) { Tip.hide(); sc.mark(null); return; } if (mv) return Tip.move(e); Tip.show(e, tipFor(d.g)); sc.mark(scByG.get(d.g) || null); },
    click: d => setFocus(d.g) }));
  const focRing = map.over.append('circle').attr('class', 'sel-ring');
  map.o.onzoom = map.o.resize = () => { const p = mapPts[st.f]; focRing.attr('cx', p.x).attr('cy', p.y).attr('r', 9 * map.u / map.k); };
  const sc = new Plot($('#relScatter'), { W: 600, H: 360, pixel: w => Math.max(260, Math.min(380, w * 0.62)), rPx: 2.6, hitPx: 14, sorted: true, label: 'Сходство с выбранной традицией в зависимости от расстояния',
    hover: (d, e, mv) => { if (!d) { Tip.hide(); map.mark(null); return; } if (mv) return Tip.move(e); Tip.show(e, tipFor(d.g)); map.mark(mapPts[d.g]); },
    click: d => setFocus(d.g), resize: () => drawScatter() });
  const axG = sc.bg.append('g').attr('class', 'ax'), lineG = sc.bg.append('g');
  map.setPoints(mapPts);
  const setSeg = segInit($('#relSet'), v => { st.set = v; render(); });
  $('#relSearch').addEventListener('change', e => { const g = gByName.get(e.target.value.trim()); if (g != null) { setFocus(g); e.target.value = ''; } });
  function setFocus(g) { st.f = g; render(); }
  function drawScatter() {
    const W = sc.o.W, H = sc.o.H, L = 40, R = 14, T = 26, B = 38;
    let mx = 0; if (S) for (let g = 0; g < NG; g++) if (g !== st.f && S[g] > mx) mx = S[g];
    const dec = D.decay[st.set]; mx = Math.max(mx, d3.max(dec.mean));
    const ymax = Math.min(1, Math.max(0.3, Math.ceil(mx * 10) / 10));
    const x = d3.scaleLinear([0, 20000], [L, W - R]), y = d3.scaleLinear([0, ymax], [H - B, T]);
    axG.selectAll('*').remove();
    const yt = d3.range(0, ymax + 1e-9, ymax > 0.6 ? 0.2 : 0.1);
    for (const v of yt) {
      axG.append('line').attr('class', v === 0 ? 'base' : 'grid').attr('x1', L).attr('x2', W - R).attr('y1', y(v)).attr('y2', y(v));
      axG.append('text').attr('x', L - 6).attr('y', y(v)).attr('text-anchor', 'end').attr('dominant-baseline', 'central').attr('font-size', 11).text(f2(v).replace(/0$/, ''));
    }
    for (const v of [0, 5000, 10000, 15000, 20000]) axG.append('text').attr('x', x(v)).attr('y', H - B + 15).attr('text-anchor', v === 20000 ? 'end' : v === 0 ? 'start' : 'middle').attr('font-size', 11).text(v === 0 ? '0' : nf.format(v));
    axG.append('text').attr('class', 'ttl').attr('x', (L + W - R) / 2).attr('y', H - 6).attr('text-anchor', 'middle').attr('font-size', 11.5).text('расстояние до выбранной традиции, км');
    axG.append('text').attr('class', 'ttl').attr('x', 4).attr('y', 5).attr('text-anchor', 'start').attr('font-size', 11.5).attr('dominant-baseline', 'hanging').text('сходство с выбранной традицией');
    const mid = dec.mean.map((v, i) => [(D.decay.bins[i] + D.decay.bins[i + 1]) / 2, v]);
    lineG.selectAll('*').remove();
    lineG.append('path').attr('class', 'meanline').attr('d', d3.line().x(d => x(d[0])).y(d => y(d[1])).curve(d3.curveMonotoneX)(mid));
    for (const d of scPts) { d.x = x(dist[d.g]); d.y = y(Math.min(ymax, S[d.g])); }
    sc.applyScale();
  }
  function render() {
    STATE.relSet = st.set; STATE.focus = G.name[st.f]; setSeg(st.set);
    const p = getPrep(st.set), ok = !!p.elig[st.f];
    S = sims(st.set, st.f); dist = new Float64Array(NG); for (let g = 0; g < NG; g++) dist[g] = km(st.f, g);
    map.restyle(d => d.g === st.f ? { cls: 'foc', f: 1.5, z: 9 } : isNaN(S[d.g]) ? { cls: 'low', f: 0.72, z: -1 } : { cls: cls(S[d.g]), z: S[d.g] });
    map.o.resize();
    scPts = []; if (ok) for (let g = 0; g < NG; g++) if (g !== st.f && !isNaN(S[g])) scPts.push({ id: g, g, x: 0, y: 0 });
    scByG = new Map(scPts.map(d => [d.g, d]));
    sc.setPoints(scPts); drawScatter(); sc.restyle(d => ({ cls: cls(S[d.g]), z: S[d.g] }));
    const note = $('#relNote'); note.textContent = '';
    const setName = { all: 'все мотивы', A: 'космологические и этиологические мотивы', B: 'приключенческие и трикстерские мотивы' }[st.set];
    note.append(h('b', { text: G.name[st.f] + '. ' }));
    const list = $('#relList'); list.textContent = '';
    if (!ok) { note.append(`У этой традиции меньше 10 мотивов выбранной группы, сходство для неё не считается. Выберите другую традицию или другую группу мотивов.`); return; }
    const order = scPts.map(d => d.g).sort((a, b) => S[b] - S[a]);
    const far = order.filter(g => dist[g] > 5000).slice(0, 1)[0];
    note.append(`Учитываются ${setName}; сравнение с ${nf.format(p.ne - 1)} традициями.`);
    if (far != null) note.append(` Самая похожая традиция дальше 5 000 км: ${G.name[far]} (сходство ${f2(S[far])}, ${nf.format(Math.round(dist[far] / 100) * 100)} км).`);
    order.slice(0, 15).forEach((g, i) => {
      const dot = h('i'); dot.style.background = `var(--${cls(S[g])})`;
      const b = h('button', { class: 'rrow', type: 'button', title: 'Сделать выбранной традицией', onclick: () => setFocus(g) },
        h('span', { class: 'rk', text: String(i + 1) }), dot, h('span', { text: G.name[g] }), h('span', { class: 'v', text: f2(S[g]) }), h('span', { class: 'km', text: nf.format(Math.round(dist[g] / 10) * 10) + ' км' }));
      b.addEventListener('mouseenter', () => { map.mark(mapPts[g]); sc.mark(scByG.get(g)); }); b.addEventListener('mouseleave', () => { map.mark(null); sc.mark(null); });
      list.append(h('li', null, b));
    });
  }
  render();
}

// ============================================================ 4b. mean decay curves
function initDecay() {
  const host = $('#decayPlot'), bins = D.decay.bins; host.classList.add('plot');
  const SER = [{ key: 'A', name: 'космология и этиология (A–I)', short: 'космология и этиология', color: 'c2' }, { key: 'B', name: 'приключения и трикстеры (J–N)', short: 'приключения и трикстеры', color: 'c6' }];
  const mids = bins.slice(0, -1).map((b, i) => (b + bins[i + 1]) / 2);
  const rng = i => `${nf.format(bins[i])}–${nf.format(Math.min(20000, bins[i + 1]))} км`;
  const leg = $('#decayLegend');
  for (const s of SER) { const k = h('span', { class: 'lk' }); k.style.borderTopColor = `var(--${s.color})`; leg.append(h('span', { class: 'it' }, k, s.name)); }
  const svg = d3.select(host).append('svg').attr('role', 'img').attr('aria-label', 'Среднее сходство пар традиций в зависимости от расстояния между ними, отдельно для космологических и приключенческих мотивов');
  let x = null, cross = null, T = 28, B = 38, H = 0;
  function draw() {
    const W = host.clientWidth; if (!W) return; H = Math.round(Math.max(240, Math.min(330, W * 0.58)));
    const L = 40, R = 16;
    svg.attr('viewBox', `0 0 ${W} ${H}`).selectAll('*').remove();
    x = d3.scaleLinear([0, 20000], [L, W - R]); const y = d3.scaleLog([0.02, 0.3], [H - B, T]);
    const ax = svg.append('g').attr('class', 'ax');
    for (const v of [0.02, 0.05, 0.1, 0.2, 0.3]) {
      ax.append('line').attr('class', v === 0.02 ? 'base' : 'grid').attr('x1', L).attr('x2', W - R).attr('y1', y(v)).attr('y2', y(v));
      ax.append('text').attr('x', L - 6).attr('y', y(v)).attr('text-anchor', 'end').attr('dominant-baseline', 'central').attr('font-size', 11).text(f2(v));
    }
    for (const v of [0, 5000, 10000, 15000, 20000]) ax.append('text').attr('x', x(v)).attr('y', H - B + 15).attr('text-anchor', v === 20000 ? 'end' : v === 0 ? 'start' : 'middle').attr('font-size', 11).text(v === 0 ? '0' : nf.format(v));
    ax.append('text').attr('class', 'ttl').attr('x', (L + W - R) / 2).attr('y', H - 6).attr('text-anchor', 'middle').attr('font-size', 11.5).text('расстояние между традициями, км');
    ax.append('text').attr('class', 'ttl').attr('x', 4).attr('y', 5).attr('text-anchor', 'start').attr('font-size', 11.5).attr('dominant-baseline', 'hanging').text('среднее сходство пар традиций');
    cross = svg.append('line').attr('class', 'cross').attr('y1', T).attr('y2', H - B).attr('display', 'none');
    for (const s of SER) {
      const pts = mids.map((m, i) => [m, D.decay[s.key].mean[i]]);
      svg.append('path').attr('class', 'dline').attr('d', d3.line().x(d => x(d[0])).y(d => y(d[1]))(pts)).style('stroke', `var(--${s.color})`);
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('class', 'ddot').attr('cx', d => x(d[0])).attr('cy', d => y(d[1])).attr('r', 4).style('fill', `var(--${s.color})`);
      const last = pts[pts.length - 1];
      svg.append('text').attr('class', 'meanlab').attr('x', W - R).attr('y', y(last[1]) - 11).attr('text-anchor', 'end').attr('font-size', 11.5).attr('stroke-width', 3).text(s.short);
    }
  }
  svg.on('pointermove', e => {
    if (!x) return; const mx = d3.pointer(e)[0]; let bi = 0, bd = Infinity;
    mids.forEach((m, i) => { const q = Math.abs(x(m) - mx); if (q < bd) { bd = q; bi = i; } });
    cross.attr('display', null).attr('x1', x(mids[bi])).attr('x2', x(mids[bi]));
    Tip.show(e, [tipTitle(rng(bi))].concat(SER.map(s => { const k = h('span', { class: 'lk' }); k.style.borderTopColor = `var(--${s.color})`; return h('div', { class: 'tl' }, k, h('b', { text: f3(D.decay[s.key].mean[bi]) }), h('span', { text: s.short })); })));
  }).on('pointerleave', () => { if (cross) cross.attr('display', 'none'); Tip.hide(); });
  const tb = h('tbody');
  bins.slice(0, -1).forEach((b, i) => tb.append(h('tr', null, h('td', { text: rng(i) }), h('td', { text: f3(D.decay.A.mean[i]) }), h('td', { text: f3(D.decay.B.mean[i]) }), h('td', { text: f3(D.decay.all.mean[i]) }), h('td', { text: nf.format(D.decay.all.n[i]) }))));
  $('#decayTable').append(h('table', { class: 'tbl' }, h('thead', null, h('tr', null, h('th', { text: 'Расстояние' }), h('th', { text: 'Космология' }), h('th', { text: 'Приключения' }), h('th', { text: 'Все мотивы' }), h('th', { text: 'Пар (все мотивы)' }))), tb));
  new ResizeObserver(draw).observe(host); draw();
}

// ============================================================ 5. motif atlas
function initMotifs(saved) {
  const A = D.atlas, HUE = A.regs.map(i => nodes[i].hue), REGN = A.regs.map(i => nodes[i]);
  const atlasPos = new Int32Array(NM).fill(-1); A.m.forEach((m, j) => { atlasPos[m] = j; });
  const mById = new Map(M.id.map((id, m) => [id, m]));
  const st = { m: mById.has(saved.motif) ? mById.get(saved.motif) : mById.get('a36') };
  const l3 = D.labels[3], regSize = REGN.map(n => n.n), regIdx = new Map(A.regs.map((id, i) => [id, i]));
  const umPts = A.m.map((m, j) => ({ id: m, m, nx: A.xy[j][0], ny: A.xy[j][1], home: A.home[j], x: 0, y: 0 }));
  const PAD = 16;
  const place = p => { for (const d of umPts) { d.x = PAD + d.nx * (p.o.W - 2 * PAD); d.y = PAD + (1 - d.ny) * (p.o.H - 2 * PAD); } };
  const homeName = i => (i < 3 ? REGN[i].short : 'широкий ареал');
  const um = new Plot($('#moUmap'), { W: 600, H: 480, pixel: w => Math.max(320, Math.min(560, w * 0.86)), rPx: 2.5, hitPx: 12, label: 'Мотивы в пространстве сходства ареалов, проекция UMAP',
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(M.id[d.m] + ' · ' + M.title[d.m]), tipLine(String(mDf[d.m]), plural(mDf[d.m], 'традиция', 'традиции', 'традиций')), tipLine(null, d.home < 3 ? 'чаще всего: ' + homeName(d.home) : 'широкий ареал')]); },
    click: d => selectMotif(d.m, false), resize: p => { place(p); p.applyScale(); ring(); } });
  const selRing = um.over.append('circle').attr('class', 'sel-ring').attr('display', 'none');
  const ring = () => { const j = atlasPos[st.m]; if (j < 0) return selRing.attr('display', 'none'); const d = umPts[j]; selRing.attr('display', null).attr('cx', d.x).attr('cy', d.y).attr('r', 8); };
  place(um); um.setPoints(umPts).restyle(d => ({ cls: d.home < 3 ? 'c' + HUE[d.home] : 'nul', f: d.home < 3 ? 1 : 0.85 }));
  const counts = [0, 0, 0, 0]; for (const v of A.home) counts[v]++;
  const leg = $('#moLegend');
  for (let i = 0; i < 4; i++) leg.append(h('span', { class: 'it' }, swatch(i < 3 ? 'c' + HUE[i] : 'nul', 0), `${homeName(i)} · ${nf.format(counts[i])}`));
  $('#moUmapCap').textContent = `Показаны ${nf.format(A.m.length)} ${plural(A.m.length, 'мотив', 'мотива', 'мотивов')}, записанные хотя бы у пяти традиций. Мотив отнесён к области, если на неё приходится не меньше 60% его встречаемости с поправкой на число записей в области. Проекция UMAP, оси ничего не значат.`;

  const mapPts = d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] }));
  let has = new Uint8Array(NG);
  const map = new Plot($('#moMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, rPx: 3.1, bg: mapBg(true), label: 'Карта мира: традиции, в которых записан выбранный мотив',
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, [tipTitle(G.name[d.g]), tipLine(null, has[d.g] ? 'мотив записан' : 'мотив не записан'), tipLine(String(G.n[d.g]), plural(G.n[d.g], 'мотив всего', 'мотива всего', 'мотивов всего'))]); } }));
  map.setPoints(mapPts);
  const similar = m => {
    const cnt = new Map(); for (const g of D.inc[m]) for (const n of gMot[g]) if (n !== m) cnt.set(n, (cnt.get(n) || 0) + 1);
    const res = []; for (const [n, c] of cnt) { if (c < 3) continue; res.push([n, c / (mDf[m] + mDf[n] - c)]); }
    return res.sort((a, b) => b[1] - a[1]).slice(0, 6);
  };
  function render() {
    const m = st.m; STATE.motif = M.id[m];
    has = new Uint8Array(NG); for (const g of D.inc[m]) has[g] = 1;
    map.restyle(d => (has[d.g] ? { cls: 'on', z: 1, f: 1.2 } : { cls: 'nul', z: 0, f: 0.55 }));
    ring();
    const head = $('#moHead'); head.textContent = '';
    const letter = M.id[m][0].toUpperCase();
    head.append(h('div', { class: 'idline' }, h('span', { class: 'bigcode', text: M.id[m] }), h('span', { class: 'ttl', text: M.title[m] })),
      h('p', { class: 'desc', text: (M.desc && M.desc[m]) || '' }),
      h('p', { class: 'meta' }, `Раздел ${letter} каталога (${mIsA[m] ? 'космология и этиология' : 'приключения и трикстеры'}) · записан у ${nf.format(mDf[m])} ${plural(mDf[m], 'традиции', 'традиций', 'традиций')} из ${nf.format(NG)} · `,
        h('a', { href: 'https://www.ruthenia.ru/folklore/berezkin/eng.html', text: 'список мотивов в каталоге' })));
    $('#moMapCap').textContent = `Синие точки: традиции, где записан мотив ${M.id[m]}. Серые: остальные традиции каталога.`;
    const side = $('#moSide'); side.textContent = '';
    const cnt = [0, 0, 0]; for (const g of D.inc[m]) { const j = keptPos[g]; if (j >= 0) cnt[regIdx.get(l3[j])]++; }
    const meters = h('div', { class: 'meters' });
    REGN.forEach((n, i) => {
      const share = cnt[i] / regSize[i], fill = h('div', { class: 'fill' }); fill.style.width = (share * 100).toFixed(1) + '%'; fill.style.background = `var(--c${n.hue})`;
      meters.append(h('div', { class: 'meter' }, h('div', { class: 'top' }, h('span', { text: n.name }), h('span', { class: 'v', text: `${pc(share)} · ${cnt[i]} из ${regSize[i]}` })), h('div', { class: 'track' }, fill)));
    });
    side.append(h('div', { class: 'info' }, h('h4', { text: 'Доля традиций с мотивом в трёх больших областях' }), meters,
      h('p', { class: 'fine', style: 'margin-top:6px', text: 'Области взяты из третьего шага кластеризации. Учтены традиции с 15 и более мотивами.' })));
    const sim = similar(m);
    if (sim.length) {
      const ol = h('ol', { class: 'mlist' }); for (const [n, j] of sim) ol.append(h('li', null, motifBtn(n, f2(j), true)));
      side.append(h('div', { class: 'info' }, h('h4', { text: 'Мотивы с самым похожим ареалом' }), ol, h('p', { class: 'fine', style: 'margin-top:6px', text: 'Число справа показывает долю общих традиций (мера Жаккара).' })));
    }
    const names = D.inc[m].map(g => G.name[g]).sort((a, b) => a.localeCompare(b));
    side.append(h('details', null, h('summary', { text: `Все ${names.length} ${plural(names.length, 'традиция', 'традиции', 'традиций')} с этим мотивом` }), h('div', { class: 'names', text: names.join('; ') })));
  }
  selectMotif = (m, scroll) => {
    st.m = m; render(); $('#moResults').textContent = '';
    if (scroll) $('#motifs').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
  };
  const idx = []; for (let m = 0; m < NM; m++) if (mDf[m] > 0) idx.push({ m, id: M.id[m], t: M.title[m].toLowerCase() });
  const search = q => {
    q = q.trim().toLowerCase(); if (!q) return [];
    const ex = [], pre = [], sub = [];
    for (const o of idx) { if (o.id === q) ex.push(o); else if (o.id.startsWith(q)) pre.push(o); else if (o.t.includes(q)) sub.push(o); }
    pre.sort((a, b) => a.id.length - b.id.length || a.id.localeCompare(b.id)); sub.sort((a, b) => mDf[b.m] - mDf[a.m]);
    return ex.concat(pre, sub).slice(0, 8);
  };
  const inp = $('#moSearch'), res = $('#moResults');
  const showRes = () => { res.textContent = ''; for (const o of search(inp.value)) res.append(motifBtn(o.m, mDf[o.m] + ' ' + plural(mDf[o.m], 'традиция', 'традиции', 'традиций'), true)); };
  inp.addEventListener('input', showRes);
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') { const r = search(inp.value); if (r.length) { selectMotif(r[0].m, false); inp.value = ''; } } });
  render();
}

// ============================================================ boot
function start(saved) {
  saved = saved || {};
  $('#fG').textContent = nf.format(D.meta.nG); $('#fM').textContent = nf.format(D.meta.nM); $('#fP').textContent = nf.format(D.meta.nPairs); $('#fMed').textContent = nf.format(D.meta.medianM);
  initClusters(saved); initNmf(); initAxes(saved); initRel(saved); initDecay(); initMotifs(saved);
  window.__ready = true;
}
const hot = window.claude && window.claude.hot;
if (hot && hot.snapshot) hot.snapshot(() => STATE);
if (hot && hot.ready) hot.ready(start); else start((hot && hot.data) || {});
})();
