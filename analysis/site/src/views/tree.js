Object.assign(TX.en, {
  trLabel: 'Radial tree of the analysed traditions, joined by similarity of their motif sets',
  trMapLabel: 'World map: traditions of the branch selected on the tree',
  trHint: 'Move the pointer over the tree: towards the centre for larger branches, towards the rim for smaller ones. Click to pin a branch, click it again to release.',
  trBranch: n => `Branch: ${nTrad(n)}`, trWhole: 'The whole tree',
  trMotifs: 'Motifs that set the branch apart: share of traditions with the motif inside the branch / outside it',
  trAll: n => `All ${nTrad(n)} of the branch`, trCut: k => `${k} clusters`, trSib: 'Joins first with: '
});
Object.assign(TX.ru, {
  trLabel: 'Круговое дерево традиций, соединённых по сходству наборов мотивов',
  trMapLabel: 'Карта мира: традиции ветви, выбранной на дереве',
  trHint: 'Ведите указателем по дереву: ближе к центру выбираются крупные ветви, ближе к ободу мелкие. Щелчок закрепляет ветвь, повторный щелчок отпускает.',
  trBranch: n => `Ветвь: ${nTrad(n)}`, trWhole: 'Всё дерево',
  trMotifs: 'Мотивы, которые отличают ветвь: доля традиций с мотивом в ветви и вне её',
  trAll: n => `Все ${nTrad(n)} ветви`, trCut: k => `${k} ${ruPl(k, 'кластер', 'кластера', 'кластеров')}`, trSib: 'Сначала соединяется с: '
});

function initTree() {
  const T = D.tree, N = KEPT.length, NN = 2 * N - 1, root = NN - 1, R0 = 300, VB = 348, TAU = 2 * Math.PI;
  const st = { k: 12, pin: -1, hov: -1 };
  // children, parents and heights; leaves are 0..N-1 (indices into the analysed traditions), merges follow
  const ca = new Int32Array(NN).fill(-1), cb = new Int32Array(NN).fill(-1), par = new Int32Array(NN).fill(-1), hh = new Float64Array(NN);
  T.merge.forEach(([a, b], i) => { const k = N + i; ca[k] = a; cb[k] = b; par[a] = k; par[b] = k; hh[k] = T.h[i]; });
  const lo = new Int32Array(NN), hi = new Int32Array(NN), order = [];
  (function walk(k) { if (k < N) { lo[k] = hi[k] = order.length; order.push(k); return; } walk(ca[k]); walk(cb[k]); lo[k] = lo[ca[k]]; hi[k] = hi[cb[k]]; })(root);
  // angles run clockwise from the top; the twelve clusters are set apart by small gaps
  const GAP = 5, la = new Float64Array(N); let nb = 0;
  for (let i = 0; i < N; i++) { if (i && LEAF[order[i]] !== LEAF[order[i - 1]]) nb++; la[i] = i + 0.5 + (nb + 0.5) * GAP; }
  const total = N + (nb + 1) * GAP, hs = TAU * 0.5 / total;
  for (let i = 0; i < N; i++) la[i] = TAU * la[i] / total;
  const ang = new Float64Array(NN), rad = new Float64Array(NN);
  for (let i = 0; i < N; i++) { ang[order[i]] = la[i]; rad[order[i]] = R0; }
  for (let k = N; k < NN; k++) { ang[k] = (ang[ca[k]] + ang[cb[k]]) / 2; rad[k] = R0 * (1 - 0.97 * Math.sqrt(hh[k] / hh[root])); }
  const f1 = v => Math.round(v * 10) / 10;
  const px = (a, r) => [f1(r * Math.sin(a)), f1(-r * Math.cos(a))];
  const arc = (a0, a1, r, sweep) => `A${f1(r)},${f1(r)} 0 ${Math.abs(a1 - a0) > Math.PI ? 1 : 0} ${sweep} ${px(a1, r)}`;
  const branch = k => `M${px(ang[ca[k]], rad[ca[k]])}L${px(ang[ca[k]], rad[k])}${arc(ang[ca[k]], ang[cb[k]], rad[k], 1)}L${px(ang[cb[k]], rad[cb[k]])}`;
  const sectorPath = k => { const a0 = la[lo[k]] - hs, a1 = la[hi[k]] + hs, ro = R0 + 8, ri = par[k] >= 0 ? rad[par[k]] : 0; return `M${px(a0, ro)}${arc(a0, a1, ro, 1)}L${px(a1, ri)}${arc(a1, a0, ri, 0)}Z`; };

  const host = $('#trTree'); host.classList.add('plot');
  const svg = d3.select(host).append('svg').attr('class', 'tree').attr('role', 'img').attr('viewBox', `${-VB} ${-VB} ${2 * VB} ${2 * VB}`);
  const gCut = svg.append('g'), sector = svg.append('path').attr('class', 'tsector').attr('display', 'none'), gBr = svg.append('g'), gLf = svg.append('g'), gLab = svg.append('g');
  const ring = svg.append('circle').attr('class', 'hov-ring').attr('r', 5).attr('display', 'none');
  const br = gBr.selectAll('path').data(d3.range(N, NN)).join('path').attr('d', branch);
  const lf = gLf.selectAll('circle').data(d3.range(N)).join('circle').attr('r', 1.7).attr('cx', d => px(ang[d], R0 + 4)[0]).attr('cy', d => px(ang[d], R0 + 4)[1]);
  const cut = gCut.append('circle').attr('class', 'tcut'), cutLab = gCut.append('text').attr('class', 'tcutlab').attr('text-anchor', 'middle').attr('font-size', 11.5);

  const mapPts = KEPT.map((g, j) => ({ id: g, g, j, x: GXY[g][0], y: GXY[g][1] }));
  const map = new Plot($('#trMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, rPx: 3, bg: mapBg(false),
    hover: (d, e, mv) => {
      if (!d) { Tip.hide(); ring.attr('display', 'none'); return; } if (mv) return Tip.move(e);
      Tip.show(e, [tipTitle(G.name[d.g]), tipLine(null, nm(nodes[D.labels[st.k][d.j]]))]);
      const [x, y] = px(ang[d.j], R0 + 4); ring.attr('display', null).attr('cx', x).attr('cy', y);
    },
    click: d => { st.pin = st.pin === d.j ? -1 : d.j; st.hov = -1; update(); } }));
  map.setPoints(mapPts);

  const on = new Uint8Array(NN), inSub = new Uint8Array(NG);
  const markSub = k => { on.fill(0); if (k < 0) return; const stk = [k]; while (stk.length) { const x = stk.pop(); on[x] = 1; if (x >= N) { stk.push(ca[x]); stk.push(cb[x]); } } };
  function indicators(k) {
    const n = hi[k] - lo[k] + 1; inSub.fill(0); for (let i = lo[k]; i <= hi[k]; i++) inSub[KEPT[order[i]]] = 1;
    const res = [];
    for (let m = 0; m < NM; m++) {
      const a = D.inc[m]; if (a.length < 5) continue; let cin = 0, call = 0;
      for (const g of a) { if (keptPos[g] < 0) continue; call++; if (inSub[g]) cin++; }
      if (cin < Math.max(2, 0.15 * n)) continue; const pin = cin / n, pout = (call - cin) / (N - n); res.push([m, pin, pout, pin - pout]);
    }
    return res.sort((x, y) => y[3] - x[3]).slice(0, 6);
  }
  function info(k) {
    const box = $('#trInfo'); box.textContent = '';
    if (k < 0) { box.append(h('p', { class: 'hint', text: t('trHint') })); return; }
    const lab = D.labels[st.k], n = hi[k] - lo[k] + 1, cnt = new Map();
    for (let i = lo[k]; i <= hi[k]; i++) { const id = lab[order[i]]; cnt.set(id, (cnt.get(id) || 0) + 1); }
    const comp = h('p', { class: 'hleg', style: 'margin:4px 0 0' });
    for (const [id, c] of Array.from(cnt).sort((a, b) => b[1] - a[1])) comp.append(h('span', { class: 'it' }, chip('ck' + nodes[id].col), k < N ? nm(nodes[id]) : `${sh(nodes[id])} · ${c}`));
    const names = i0 => { const a = []; for (let i = lo[i0]; i <= hi[i0]; i++) a.push(G.name[KEPT[order[i]]]); return a.sort((x, y) => x.localeCompare(y)); };
    if (k < N) {
      const g = KEPT[k], sib = par[k] >= 0 ? (ca[par[k]] === k ? cb[par[k]] : ca[par[k]]) : -1;
      box.append(h('h4', { text: G.name[g] }), comp, h('p', { class: 'fine', style: 'margin-top:6px', text: `${G.n[g]} ${t('motifsRecorded', G.n[g])}` }));
      if (sib >= 0) { const s = names(sib); box.append(h('p', { class: 'fine', style: 'margin-top:6px', text: t('trSib') + s.slice(0, 8).join('; ') + (s.length > 8 ? ' …' : '') })); }
      return;
    }
    box.append(h('h4', { text: k === root ? t('trWhole') : t('trBranch', n) }), comp);
    if (k !== root && n >= 3) {
      const ol = h('ol', { class: 'mlist' }); for (const [m, pin, pout] of indicators(k)) ol.append(h('li', null, motifBtn(m, pc(pin) + ' / ' + pc(pout))));
      box.append(h('p', { class: 'fine', style: 'margin:10px 0 2px', text: t('trMotifs') }), ol);
    }
    const all = names(k);
    if (n <= 30) box.append(h('p', { class: 'fine', style: 'margin-top:8px', text: all.join('; ') }));
    else box.append(h('details', null, h('summary', { text: t('trAll', n) }), h('div', { class: 'names', text: all.join('; ') })));
  }
  let shown = -2;
  function update(force) {
    const k = st.hov >= 0 ? st.hov : st.pin; if (k === shown && !force) return; shown = k;
    markSub(k); svg.classed('has-sel', k >= 0);
    br.classed('on', d => on[d] === 1); lf.classed('on', d => on[d] === 1);
    sector.attr('display', k >= 0 ? null : 'none'); if (k >= 0) sector.attr('d', sectorPath(k));
    const lab = D.labels[st.k];
    map.restyle(d => (k < 0 || on[d.j] ? { cls: 'k' + nodes[lab[d.j]].col, z: 2, f: k < 0 ? 1 : 1.3 } : { cls: 'nul', f: 0.6, z: 0 }));
    info(k);
  }
  const nodeLab = new Int32Array(NN);
  function colour() {                                        // a branch takes the colour of a cluster when all its leaves belong to it
    const lab = D.labels[st.k];
    for (let i = 0; i < N; i++) nodeLab[i] = lab[i];
    for (let k = N; k < NN; k++) nodeLab[k] = nodeLab[ca[k]] === nodeLab[cb[k]] ? nodeLab[ca[k]] : -1;
    br.attr('class', d => 'tbr' + (nodeLab[d] >= 0 ? ' ck' + nodes[nodeLab[d]].col : ''));
    lf.attr('class', d => 'tlf ck' + nodes[nodeLab[d]].col);
    const rc = (rad[NN - st.k + 1] + rad[NN - st.k]) / 2;      // between the last merge undone and the first one kept
    cut.attr('r', rc); cutLab.attr('y', -rc - 5).text(t('trCut', st.k));
    $('#trK').textContent = st.k;
  }
  let small = null;
  function labels() {
    small = host.clientWidth < 520; gLab.selectAll('*').remove();
    const lab = D.labels[st.k], groups = [], fs = 12.5, last = [-9, -9], leg = $('#trLegend'); leg.textContent = ''; leg.hidden = !small;
    for (let i = 1, s0 = 0; i <= N; i++) if (i === N || lab[order[i]] !== lab[order[s0]]) { groups.push({ n: nodes[lab[order[s0]]], a0: la[s0] - hs, a1: la[i - 1] + hs }); s0 = i; }
    for (const g of groups) {
      gLab.append('path').attr('class', 'tarc ck' + g.n.col).attr('d', `M${px(g.a0, R0 + 11)}${arc(g.a0, g.a1, R0 + 11, 1)}`);
      if (small) { leg.append(h('span', { class: 'it' }, chip('ck' + g.n.col), sh(g.n))); continue; }
      const txt = sh(g.n), am = (g.a0 + g.a1) / 2, half = (txt.length * fs * 0.29 + 5) / (R0 + 24);
      const lvl = am - half > last[0] ? 0 : 1; last[lvl] = am + half;
      const bottom = am > Math.PI / 2 && am < 1.5 * Math.PI, r = R0 + 19 + lvl * 15 + (bottom ? 9 : 0), w = half * 1.7, id = 'trl' + g.n.id;
      gLab.append('path').attr('id', id).attr('fill', 'none').attr('d', bottom ? `M${px(am + w, r)}${arc(am + w, am - w, r, 0)}` : `M${px(am - w, r)}${arc(am - w, am + w, r, 1)}`);
      gLab.append('text').attr('class', 'tlab').attr('font-size', fs).append('textPath').attr('href', '#' + id).attr('startOffset', '50%').attr('text-anchor', 'middle').text(txt);
    }
  }
  const pick = e => {                                         // the branch whose sector lies under the pointer
    const [mx, my] = d3.pointer(e, svg.node()), r = Math.hypot(mx, my); if (r > R0 + 16) return -1;
    let a = Math.atan2(mx, -my); if (a < 0) a += TAU;
    let i = d3.bisectLeft(la, a); if (i >= N) i = N - 1; else if (i > 0 && a - la[i - 1] < la[i] - a) i--;
    let k = order[i]; while (par[k] >= 0 && rad[par[k]] >= r) k = par[k]; return k;
  };
  const tipFor = k => (k < N ? [tipTitle(G.name[KEPT[k]]), tipLine(null, nm(nodes[D.labels[st.k][k]]))] : [tipTitle(k === root ? t('trWhole') : t('trBranch', hi[k] - lo[k] + 1))]);
  svg.on('pointermove', e => { if (e.pointerType === 'touch') return; const k = pick(e); if (k < 0) { Tip.hide(); } else if (k !== st.hov) Tip.show(e, tipFor(k)); else Tip.move(e); st.hov = k; update(); })
     .on('pointerleave', () => { Tip.hide(); st.hov = -1; update(); })
     .on('click', e => { const k = pick(e); st.pin = k < 0 || k === st.pin ? -1 : k; st.hov = -1; update(); });
  const setK = k => { st.k = Math.max(2, Math.min(12, k)); colour(); labels(); update(true); };
  $('#trMinus').addEventListener('click', () => setK(st.k - 1)); $('#trPlus').addEventListener('click', () => setK(st.k + 1));
  new ResizeObserver(() => { if (host.clientWidth && (host.clientWidth < 520) !== small) labels(); }).observe(host);
  const texts = () => { svg.attr('aria-label', t('trLabel')); map.label(t('trMapLabel')); colour(); labels(); update(true); };
  RERENDER.push(texts); texts();
}
