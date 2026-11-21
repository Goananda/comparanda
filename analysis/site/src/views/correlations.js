Object.assign(TX.en, {
  crLabelM: 'World map: traditions where the selected motifs are recorded', crLabelT: 'World map: correlation of every tradition with the selected one',
  crFirst: { m: 'First motif', t: 'First tradition' }, crSecond: { m: 'Second motif', t: 'Second tradition' }, crPh: { m: 'code or word: c6, moon', t: 'start typing a name' },
  crTop: { m: 'Most correlated motifs', t: 'Most correlated traditions' }, crSub: { m: 'correlation, shared traditions', t: 'correlation, shared motifs' },
  crPick: 'Click a row to make it the second one and compare the two.', crNone: 'No other motif shares three or more traditions with this one.',
  crR: 'Correlation', crBoth: 'both', crOnly: 'only ', crRemove: 'Remove the second one', crSwap: 'Swap the first and the second',
  crMotMeta: (n, N) => `recorded in ${nf(n)} of ${nf(N)} traditions`, crTrMeta: n => `${nf(n)} ${n === 1 ? 'motif' : 'motifs'} recorded`, crAtlas: 'map in the atlas', crApart: v => `${v} km apart`,
  crCapM1: id => `Blue dots: traditions where motif ${id} is recorded. Grey dots: the other traditions of the catalogue.`,
  crCapM2: 'A coloured dot is a tradition with at least one of the two motifs. Grey dots have neither.',
  crCapT: name => `Colour shows how strongly each tradition correlates with ${name}. Click a tradition on the map to make it the first one.`,
  crScale: ['weaker correlation', 'stronger'], crKey1: 'first tradition', crKey2: 'second tradition', crHas: 'motif recorded',
  crTipR: name => 'correlation with ' + name, crTipShared: n => (n === 1 ? 'shared motif' : 'shared motifs'), crYes: 'recorded', crNo: 'not recorded',
  crBothTr: n => `Both motifs: ${nTrad(n)}`, crOnlyTr: (id, n) => `Only ${id}: ${nTrad(n)}`,
  crSharedMo: n => `Shared motifs: ${nf(n)}`, crOnlyMo: (name, n) => `Only in ${name}: ${nf(n)}`, crRare: 'Rarest first. The number is how many traditions have the motif.', crAllShared: n => `The other ${nf(n)} shared motifs`
});
Object.assign(TX.ru, {
  crLabelM: 'Карта мира: традиции, в которых записаны выбранные мотивы', crLabelT: 'Карта мира: корреляция каждой традиции с выбранной',
  crFirst: { m: 'Первый мотив', t: 'Первая традиция' }, crSecond: { m: 'Второй мотив', t: 'Вторая традиция' }, crPh: { m: 'код или слово: c6, луна', t: 'начните вводить название' },
  crTop: { m: 'Самые близкие мотивы', t: 'Самые близкие традиции' }, crSub: { m: 'корреляция, общие традиции', t: 'корреляция, общие мотивы' },
  crPick: 'Щёлкните по строке, чтобы сделать её вторым объектом и сравнить два.', crNone: 'Ни один другой мотив не делит с этим три и более традиции.',
  crR: 'Корреляция', crBoth: 'оба', crOnly: 'только ', crRemove: 'Убрать второй объект', crSwap: 'Поменять первый и второй местами',
  crMotMeta: (n, N) => `записан у ${nf(n)} ${ruPl(n, 'традиции', 'традиций', 'традиций')} из ${nf(N)}`, crTrMeta: n => `${nf(n)} ${ruPl(n, 'мотив записан', 'мотива записано', 'мотивов записано')}`, crAtlas: 'карта в атласе', crApart: v => `${v} км между традициями`,
  crCapM1: id => `Синие точки: традиции, где записан мотив ${id}. Серые: остальные традиции каталога.`,
  crCapM2: 'Цветная точка обозначает традицию, у которой есть хотя бы один из двух мотивов. У серых точек нет ни одного.',
  crCapT: name => `Цвет показывает, насколько сильно каждая традиция коррелирует с традицией ${name}. Щёлкните по традиции на карте, чтобы сделать её первой.`,
  crScale: ['корреляция слабее', 'сильнее'], crKey1: 'первая традиция', crKey2: 'вторая традиция', crHas: 'мотив записан',
  crTipR: name => 'корреляция с ' + name, crTipShared: n => ruPl(n, 'общий мотив', 'общих мотива', 'общих мотивов'), crYes: 'записан', crNo: 'не записан',
  crBothTr: n => `Оба мотива: ${nTrad(n)}`, crOnlyTr: (id, n) => `Только ${id}: ${nTrad(n)}`,
  crSharedMo: n => `Общие мотивы: ${nf(n)}`, crOnlyMo: (name, n) => `Только у ${name}: ${nf(n)}`, crRare: 'Сначала самые редкие. Число показывает, у скольких традиций есть мотив.', crAllShared: n => `Остальные общие мотивы: ${nf(n)}`
});

function initCorrelations(saved) {
  const NMU = mDf.filter(v => v > 0).length;                    // motifs recorded at least once
  const phi = (n11, n1, n2, n) => { const d = Math.sqrt(n1 * (n - n1) * n2 * (n - n2)); return d ? (n11 * n - n1 * n2) / d : 0; };
  const fr = v => (v < 0 ? '−' : '') + f2(Math.abs(v));
  const mById = new Map(M.id.map((id, m) => [id, m])), orNull = v => (v == null ? null : v);
  const resolve = (mode, v) => (v == null ? null : orNull(mode === 'm' ? mById.get(v) : gByName.get(v)));
  const label = (mode, x) => (mode === 'm' ? M.id[x] : G.name[x]);
  const st = { mode: saved.corMode === 't' ? 't' : 'm', m: { a: resolve('m', 'c6'), b: resolve('m', 'h4') }, t: { a: resolve('t', 'Chukchi'), b: resolve('t', 'North Alaskan Inupiat') } };
  if (resolve(st.mode, saved.corA) != null) { st[st.mode].a = resolve(st.mode, saved.corA); st[st.mode].b = resolve(st.mode, saved.corB); }
  const TH = [0.03, 0.06, 0.10, 0.15, 0.22, 0.32], ramp = v => { let c = 1; for (const x of TH) if (v >= x) c++; return 's' + c; };
  const setOf = m => { const u = new Uint8Array(NG); if (m != null) for (const g of D.inc[m]) u[g] = 1; return u; };
  const topMotifs = a => {
    const cnt = new Map(); for (const g of D.inc[a]) for (const m of gMot[g]) if (m !== a) cnt.set(m, (cnt.get(m) || 0) + 1);
    const out = []; for (const [m, c] of cnt) if (c >= 3) out.push({ id: m, r: phi(c, mDf[a], mDf[m], NG), n: c });
    return out.sort((x, y) => y.r - x.r || y.n - x.n).slice(0, 20);
  };
  const corTrad = a => {
    const cnt = new Int32Array(NG), r = new Float64Array(NG); for (const m of gMot[a]) for (const g of D.inc[m]) cnt[g]++;
    for (let g = 0; g < NG; g++) r[g] = g === a ? 1 : phi(cnt[g], gMot[a].length, gMot[g].length, NMU);
    return { r, cnt };
  };
  const cur = { hasA: null, hasB: null, c: null };
  const tipFor = g => {
    const mode = st.mode, { a, b } = st[mode], rows = [tipTitle(G.name[g])];
    if (mode === 'm') { for (const [m, has] of [[a, cur.hasA], [b, cur.hasB]]) if (m != null) rows.push(tipLine(M.id[m], has[g] ? t('crYes') : t('crNo'))); }
    else if (g === a) rows.push(tipLine(null, t('crKey1')));
    else rows.push(tipLine(fr(cur.c.r[g]), t('crTipR', G.name[a])), tipLine(String(cur.c.cnt[g]), t('crTipShared', cur.c.cnt[g])));
    return rows;
  };
  const pts = d3.range(NG).map(g => ({ id: g, g, x: GXY[g][0], y: GXY[g][1] }));
  const map = new Plot($('#crMap'), Object.assign({}, MAPO, { zoom: true, sorted: true, bg: mapBg(true),
    hover: (d, e, mv) => { if (!d) return Tip.hide(); if (mv) return Tip.move(e); Tip.show(e, tipFor(d.g)); },
    click: d => { if (st.mode !== 't' || d.g === st.t.a) return; if (d.g === st.t.b) st.t.b = null; st.t.a = d.g; render(); },
    onzoom: () => rings(), resize: () => rings() }));
  const gArc = map.root.insert('g', () => map.marks.node()), ringA = map.over.append('circle').attr('class', 'sel-ring'), ringB = map.over.append('circle').attr('class', 'sel-ring crb');
  map.setPoints(pts);
  function rings() {
    const u = map.u / map.k, put = (el, g, k) => { if (st.mode !== 't' || g == null) return el.attr('display', 'none'); el.attr('display', null).attr('cx', pts[g].x).attr('cy', pts[g].y).attr('r', k * u); };
    put(ringA, st.t.a, 9); put(ringB, st.t.b, 8);
  }
  function head() {
    const box = $('#crHead'), mode = st.mode, { a, b } = st[mode]; box.textContent = ''; if (a == null) return;
    const line = (x, cls, second) => {
      const row = h('div', { class: 'crsel' }, h('i', { class: 'chip ' + cls }));
      if (mode === 'm') row.dataset.m = x;
      if (mode === 'm') row.append(h('span', { class: 'bigcode', text: M.id[x] }), h('span', { class: 'ttl', text: mT(x) }), h('span', { class: 'meta' }, t('crMotMeta', mDf[x], NG) + ' · ',
        h('a', { href: '#motifs', text: t('crAtlas'), onclick: e => { e.preventDefault(); e.stopPropagation(); openMotif(x); } })));
      else { const lf = leafOf(x); row.append(h('span', { class: 'ttl', text: G.name[x] }), h('span', { class: 'meta', text: t('crTrMeta', G.n[x]) + (lf ? ' · ' + nm(lf) : '') })); }
      if (second) row.append(tAttr(h('button', { class: 'btn sq sm', type: 'button', text: '×', onclick: () => { st[mode].b = null; render(); } }), { title: 'crRemove', aria: 'crRemove' }),
        tAttr(h('button', { class: 'btn sq sm', type: 'button', text: '⇄', onclick: () => { const s = st[mode]; [s.a, s.b] = [s.b, s.a]; render(); } }), { title: 'crSwap', aria: 'crSwap' }));
      return row;
    };
    box.append(line(a, 'ca1', false)); if (b == null) return;
    box.append(line(b, 'ca2', true));
    let nA, nB, both, r;
    if (mode === 'm') { nA = mDf[a]; nB = mDf[b]; both = D.inc[a].filter(g => cur.hasB[g]).length; r = phi(both, nA, nB, NG); }
    else { nA = gMot[a].length; nB = gMot[b].length; both = cur.c.cnt[b]; r = cur.c.r[b]; }
    const parts = [[nA - both, 'ca1', t('crOnly') + label(mode, a)], [both, 'cink', t('crBoth')], [nB - both, 'ca2', t('crOnly') + label(mode, b)]], tot = nA + nB - both || 1;
    const bar = h('div', { class: 'split' }), leg = h('div', { class: 'hleg' });
    for (const [v, cls, name] of parts) { const seg = h('i', { class: cls }); seg.style.flex = `${Math.max(v, tot * 0.006)} 1 0`; bar.append(seg); leg.append(h('span', { class: 'it' }, h('i', { class: 'chip ' + cls }), `${name}: ${nf(v)}`)); }
    box.append(h('p', { class: 'crstat' }, t('crR') + ' ', h('b', { text: fr(r) }), mode === 't' ? ' · ' + t('crApart', nf(Math.round(km(a, b) / 10) * 10)) : ''), bar, leg);
  }
  function paint() {
    const mode = st.mode, { a, b } = st[mode], key = $('#crKey'); key.textContent = ''; gArc.selectAll('*').remove();
    if (mode === 'm') {
      cur.hasA = setOf(a); cur.hasB = setOf(b);
      map.label(t('crLabelM')).restyle(d => { const x = cur.hasA[d.g], y = cur.hasB[d.g]; return x && y ? { cls: 'pab', f: 1.3, z: 3 } : x ? { cls: 'pa', f: 1.1, z: 2 } : y ? { cls: 'pb', f: 1.1, z: 1 } : { cls: 'nul', f: 0.55, z: 0 }; });
      if (b == null) key.append(h('span', { class: 'it' }, swatch('pa'), `${M.id[a]}: ${t('crHas')}`));
      else key.append(h('span', { class: 'it' }, swatch('pa'), t('crOnly') + M.id[a]), h('span', { class: 'it' }, swatch('pab'), t('crBoth')), h('span', { class: 'it' }, swatch('pb'), t('crOnly') + M.id[b]));
      $('#crCap').textContent = b == null ? t('crCapM1', M.id[a]) : t('crCapM2');
    } else {
      cur.c = corTrad(a);
      map.label(t('crLabelT')).restyle(d => (d.g === a ? { cls: 'foc', f: 1.5, z: 9 } : { cls: ramp(cur.c.r[d.g]), z: cur.c.r[d.g] }));
      const sc = h('span', { class: 'scale' }, t('crScale')[0], h('span', { class: 'steps' }), t('crScale')[1]); steps(sc.querySelector('.steps'), ['s1', 's2', 's3', 's4', 's5', 's6', 's7']);
      key.append(sc, h('span', { class: 'it' }, swatch('foc'), t('crKey1'))); if (b != null) { key.append(h('span', { class: 'it' }, h('i', { class: 'chip crring' }), t('crKey2'))); gArc.append('path').attr('class', 'ln crarc').attr('d', arcPath(a, b)); }
      $('#crCap').textContent = t('crCapT', G.name[a]);
    }
    rings();
  }
  function side() {
    const box = $('#crSide'), mode = st.mode, { a, b } = st[mode], ol = h('ol', { class: 'rlist' }); box.textContent = '';
    box.append(h('h3', null, t('crTop')[mode] + ' ', h('span', { class: 'sub', text: t('crSub')[mode] })));
    if (mode === 'm') {
      const top = topMotifs(a); if (!top.length) { box.append(h('p', { class: 'fine', text: t('crNone') })); return; }
      top.forEach((o, i) => ol.append(h('li', null, h('button', { class: 'rrow crrow' + (o.id === b ? ' sel' : ''), type: 'button', 'data-m': o.id, onclick: () => { st.m.b = o.id; render(); } },
        h('span', { class: 'rk', text: String(i + 1) }), h('span', { class: 'code', text: M.id[o.id] }), h('span', { text: mT(o.id) }), h('span', { class: 'v', text: fr(o.r) }), h('span', { class: 'km', text: nf(o.n) })))));
    } else {
      d3.range(NG).filter(g => g !== a).sort((x, y) => cur.c.r[y] - cur.c.r[x]).slice(0, 20).forEach((g, i) => {
        const lf = leafOf(g), row = h('button', { class: 'rrow' + (g === b ? ' sel' : ''), type: 'button', onclick: () => { st.t.b = g; render(); } },
          h('span', { class: 'rk', text: String(i + 1) }), h('i', { class: 'chip ' + (lf ? 'ck' + lf.col : '') }), h('span', { text: G.name[g] }), h('span', { class: 'v', text: fr(cur.c.r[g]) }), h('span', { class: 'km', text: nf(cur.c.cnt[g]) }));
        row.addEventListener('mouseenter', () => map.mark(pts[g])); row.addEventListener('mouseleave', () => map.mark(null)); ol.append(h('li', null, row));
      });
    }
    box.append(ol, h('p', { class: 'fine', style: 'margin-top:8px', text: t('crPick') }));
  }
  function detail() {
    const box = $('#crDetail'), mode = st.mode, { a, b } = st[mode]; box.textContent = ''; if (a == null || b == null) return;
    if (mode === 'm') {
      const both = [], oa = [], ob = [];
      for (let g = 0; g < NG; g++) { const x = cur.hasA[g], y = cur.hasB[g]; if (x && y) both.push(G.name[g]); else if (x) oa.push(G.name[g]); else if (y) ob.push(G.name[g]); }
      const col = (cls, title, names) => h('div', { class: 'crcol' }, h('h4', null, h('i', { class: 'chip ' + cls }), ' ' + title), h('div', { class: 'names', text: names.sort((x, y) => x.localeCompare(y)).join('; ') || '—' }));
      box.append(h('div', { class: 'cr3' }, col('cink', t('crBothTr', both.length), both), col('ca1', t('crOnlyTr', M.id[a], oa.length), oa), col('ca2', t('crOnlyTr', M.id[b], ob.length), ob)));
    } else {
      const A = new Set(gMot[a]), B = new Set(gMot[b]), rare = (x, y) => mDf[x] - mDf[y] || x - y;
      const shared = gMot[b].filter(m => A.has(m)).sort(rare), oa = gMot[a].filter(m => !B.has(m)).sort(rare), ob = gMot[b].filter(m => !A.has(m)).sort(rare);
      const list = ms => { const ol = h('ol', { class: 'mlist' }); for (const m of ms) ol.append(h('li', null, motifBtn(m, nf(mDf[m])))); return ol; };
      const left = h('div', { class: 'crcol' }, h('h4', null, h('i', { class: 'chip cink' }), ' ' + t('crSharedMo', shared.length)), h('p', { class: 'fine', style: 'margin:2px 0 4px', text: t('crRare') }), list(shared.slice(0, 24)));
      if (shared.length > 24) left.append(h('details', null, h('summary', { text: t('crAllShared', shared.length - 24) }), list(shared.slice(24))));
      const only = (cls, x, ms) => h('details', { class: 'cronly' }, h('summary', null, h('i', { class: 'chip ' + cls }), ' ' + t('crOnlyMo', G.name[x], ms.length)), list(ms));
      box.append(h('div', { class: 'cr2' }, left, h('div', { class: 'crcol' }, only('ca1', a, oa), only('ca2', b, ob))));
    }
  }
  const inA = $('#crInA'), inB = $('#crInB');
  const TR = G.name.map((n, g) => ({ g, n, l: n.toLowerCase() })).sort((x, y) => x.n.localeCompare(y.n));
  const tradItems = q => { q = q.trim().toLowerCase(); if (!q) return TR; const pre = [], sub = []; for (const o of TR) { if (o.l.startsWith(q)) pre.push(o); else if (o.l.includes(q)) sub.push(o); } return pre.concat(sub); };
  const tradRow = o => { const lf = leafOf(o.g); return h('div', { class: 'rrow' }, h('span', { class: 'rk' }), h('i', { class: 'chip ' + (lf ? 'ck' + lf.col : '') }), h('span', { text: o.n }), h('span', { class: 'v' }), h('span', { class: 'km', text: nf(G.n[o.g]) })); };
  function choose(slot, x) { const s = st[st.mode]; if (slot === 'a') { s.a = x; if (s.b === x) s.b = null; } else if (x !== s.a) s.b = x; render(); }
  for (const [inp, slot] of [[inA, 'a'], [inB, 'b']])
    picker(inp, { items: q => (st.mode === 'm' ? motifItems(q) : tradItems(q)), row: o => (st.mode === 'm' ? motifRow(o) : tradRow(o)), pick: o => choose(slot, st.mode === 'm' ? o.m : o.g) });
  const setMode = segInit($('#crMode'), v => { st.mode = v === 't' ? 't' : 'm'; inA.value = ''; inB.value = ''; render(); });
  function render() {
    const mode = st.mode, { a, b } = st[mode]; setMode(mode);
    STATE.corMode = mode; STATE.corA = a == null ? null : label(mode, a); STATE.corB = b == null ? null : label(mode, b);
    $('#crLabA').textContent = t('crFirst')[mode]; $('#crLabB').textContent = t('crSecond')[mode];
    for (const inp of [inA, inB]) inp.placeholder = t('crPh')[mode];
    paint(); head(); side(); detail();
  }
  corSet = (mode, a, b) => { st.mode = mode === 't' ? 't' : 'm'; const ra = resolve(st.mode, a); if (ra != null) { st[st.mode].a = ra; st[st.mode].b = resolve(st.mode, b); } render(); };
  RERENDER.push(render); render();
}
