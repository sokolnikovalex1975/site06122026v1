/* Санитарный навигатор: поиск. Данные — window.NVS (nv-search-data.js). Логика перенесена из прототипа без изменений. */
(function () {
  'use strict';
  var N = window.NVS, d = document, B = '../';
  if (!N || !d.getElementById('sRes')) return;
  var F = N.F, D = N.D, T = N.T, C = N.C, CO = N.CO, Q = N.Q, fIdx = {};
  F.forEach(function (f, i) { fIdx[f.id] = i; });
  var NBSP = '\u00a0';
  function $(s, r) { return (r || d).querySelector(s); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'); }
  function fmtN(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, NBSP); }
  function norm(s) { return String(s).toLowerCase().replace(/ё/g, 'е'); }
  var IDX = window.NV_INDEX || '';   // на хостинге предпросмотра адреса папок не открываются без имени файла
  function L(u, inner, cls, q) { return '<a href="' + B + u + IDX + (q || '') + '"' + (cls ? ' class="' + cls + '"' : '') + '>' + inner + '</a>'; }
  function badge(x) { return '<span class="nv-badge nv-b-' + x.vc + '">' + esc(x.vt) + '</span>'; }
  var ARROW = '<svg class="nv-arrow" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var STOP = {}; 'в во на и или по для как что о об к ко с со у ли не это а но же бы за из от до при над под то какие какой какая каким каких нужно надо можно часто должна должен должны быть есть ли где когда чем кто его ее их мой наш'.split(' ').forEach(function (w) { STOP[w] = 1; });
  var ENDS = ['иями', 'ями', 'ами', 'ться', 'ией', 'иях', 'ого', 'его', 'ому', 'ему', 'ыми', 'ими', 'ять', 'ать', 'ить', 'еть', 'ую', 'юю', 'ая', 'яя', 'ое', 'ее', 'ые', 'ие', 'ый', 'ий', 'ой', 'ом', 'ем', 'ам', 'ям', 'ах', 'ях', 'ов', 'ев', 'ей', 'ию', 'ью', 'ия', 'ья', 'ье', 'а', 'я', 'о', 'е', 'ы', 'и', 'у', 'ю', 'ь', 'й'];
  function stem(w) {
    if (w.length < 4 || /[\d]/.test(w) || !/[а-я]/.test(w)) return w;
    for (var i = 0; i < ENDS.length; i++) { var e = ENDS[i]; if (w.length - e.length >= 3 && w.slice(-e.length) === e) return w.slice(0, -e.length); }
    return w;
  }
  function partRe(p) {
    if (/\s/.test(p) || /^[\d.\/-]+[а-я-]*$/.test(p) || /\d/.test(p)) return new RegExp(reEsc(p));
    return new RegExp('(^|[^а-яa-z0-9])' + reEsc(p));
  }
  function tokens(q) {
    var out = [];
    norm(q).replace(/[«»"“”(),;:!?]/g, ' ').split(/\s+/).forEach(function (w) {
      w = w.replace(/^[.-]+|[.]+$/g, '');
      if (!w || STOP[w] || (w.length < 2 && !/\d/.test(w))) return;
      if (w === 'п' || w === 'пп' || w === 'ст' || w === '№' || w === 'n') return;
      var s = stem(w), syn = N.syn[s];
      if (!syn) { for (var k in N.syn) { if (k.length >= 3 && s.indexOf(k) === 0) { syn = N.syn[k]; break; } } }
      var alts = (syn || [[s]]).map(function (alt) { return alt.map(function (p) { return { p: p, re: partRe(p) }; }); });
      out.push({ w: w, s: s, alts: alts });
    });
    return out;
  }
  function tokMatch(t, hay) { return t.alts.some(function (alt) { return alt.every(function (p) { return p.re.test(hay); }); }); }
  function mkHl(altsList) {
    var parts = [];
    altsList.forEach(function (alts) { alts.forEach(function (alt) { alt.forEach(function (p) { if (p.p.length >= 3 && parts.indexOf(p.p) < 0) parts.push(p.p); }); }); });
    if (!parts.length) return null;
    parts.sort(function (a, b) { return b.length - a.length; });
    return new RegExp('(^|[^а-яёa-z0-9])((?:' + parts.map(function (p) { return reEsc(esc(p)); }).join('|') + ')[а-яёa-z0-9-]*)', 'gi');
  }
  var HAY = null;
  function qHay() { return HAY || (HAY = F.map(function (f) { return Q[f.id].map(function (q) { return [norm(q[1]), norm(q[2])]; }); })); }
  var dHayC = [];
  function docHay(i) { return dHayC[i] || (dHayC[i] = norm(D[i].s + ' ' + D[i].t + ' ' + D[i].x)); }
  var OBJ_KW = {
    '580_p02': ['ресторан', 'кафе', 'столов', 'общепит', 'кейтеринг', 'бар', 'пиццери', 'кофейн'], '580_p01': ['продуктов', 'рынок', 'рынк', 'супермаркет', 'магазин'], '578_p01': ['непродовольств', 'промтовар', 'магазин'],
    '578_p02': ['гостиниц', 'отел', 'хостел'], '578_p03': ['общежит'], '578_p04': ['соцобслуж', 'интернат', 'пансионат'], '578_p10': ['больниц', 'клиник', 'поликлиник', 'стационар', 'стоматолог', 'медорганизац'],
    '578_p11': ['аптек'], '578_p13': ['детсад', 'садик', 'сад', 'дошкольн'], '578_p14': ['школ'], '578_p16': ['колледж', 'техникум'], '578_p17': ['вуз', 'университет', 'институт'],
    '578_p19': ['лагер'], '578_p20': ['лагер'], '578_p21': ['лагер', 'палаточн'], '578_p31': ['лагер'],
    '580_p03': ['бассейн', 'спорт', 'фитнес', 'аквапарк', 'спортзал'], '580_p05': ['салон', 'парикмахерск', 'маникюр', 'косметолог'], '580_p06': ['баня', 'бани', 'бане', 'баню', 'бань', 'саун'],
    '580_p04': ['прачечн', 'химчистк'], '578_p06': ['мкд', 'управляющ', 'тсж', 'многоквартирн'], '578_p30': ['завод', 'цех'],
    sklad: ['склад', 'логистик'], ofis: ['офис', 'бизнес-центр', 'бц', 'тц'], pishcheprom: ['пищев'], farma: ['фарм']
  };
  function kwHit(s, kw) { return s === kw || (s.length >= 3 && kw.length >= 4 && kw.indexOf(s) === 0) || (kw.length >= 4 && s.indexOf(kw) === 0); }
  function search(query) {
    var toks = tokens(query), res = { toks: toks, docs: [], cards: [], objs: [], comps: [], themes: [], qs: [], qTotal: 0, byObj: {}, off: null, objF: null };
    if (!toks.length) return res;
    var objSet = {}, objTok = {};
    toks.forEach(function (t, ti) { for (var id in OBJ_KW) { if (OBJ_KW[id].some(function (kw) { return kwHit(t.s, kw); })) { objSet[id] = 1; objTok[ti] = 1; } } });
    var hasObj = Object.keys(objSet).length > 0;
    var rest = toks.filter(function (t, i) { return !objTok[i]; });
    D.forEach(function (x, i) {
      var hs = norm(x.s), hay = docHay(i);
      if (toks.every(function (t) { return tokMatch(t, hay); })) {
        var inS = toks.every(function (t) { return tokMatch(t, hs); });
        res.docs.push({ i: i, sc: (inS ? 1e6 : 0) + (x.cq || 0) + (x.c === 'off' ? -1 : 0) });
      }
    });
    res.docs.sort(function (a, b) { return b.sc - a.sc; });
    var top = res.docs[0];
    if (top && top.sc >= 1e6 - 1 && D[top.i].c === 'off' && toks.some(function (t) { return /\d/.test(t.w); })) res.off = top.i;
    C.forEach(function (c, i) {
      var hay = norm(c.title + ' ' + c.short + ' ' + c.hay);
      var hit = toks.filter(function (t) { return tokMatch(t, hay); }).length;
      var need = rest.length ? rest.every(function (t) { return tokMatch(t, hay); }) : hit === toks.length;
      if (need && hit) res.cards.push({ i: i, sc: hit + (toks.every(function (t) { return tokMatch(t, norm(c.title)); }) ? 5 : 0) });
    });
    res.cards.sort(function (a, b) { return b.sc - a.sc; });
    F.forEach(function (f, i) { if (objSet[f.id] || toks.every(function (t) { return tokMatch(t, norm(f.name + ' ' + f.hint)); })) res.objs.push(i); });
    CO.forEach(function (c, i) { if (objSet[c.id] || toks.every(function (t) { return tokMatch(t, norm(c.name)); })) res.comps.push(i); });
    T.forEach(function (t, i) { if (rest.length && rest.every(function (x) { return tokMatch(x, norm(t.name + ' ' + t.hint)); })) res.themes.push(i); });
    var hay = qHay(), fset = null;
    if (hasObj && rest.length) { fset = {}; Object.keys(objSet).forEach(function (id) { if (fIdx[id] != null) fset[fIdx[id]] = 1; }); if (!Object.keys(fset).length) fset = null; }
    var qt = fset ? rest : toks;
    var thSet = {}; res.themes.forEach(function (i) { thSet[i] = 1; });
    if (qt.length) {
      F.forEach(function (f, fi) {
        if (fset && !fset[fi]) return;
        var rows = Q[f.id];
        hay[fi].forEach(function (h, qi) {
          var inText = 0, ok = true;
          for (var k = 0; k < qt.length; k++) { if (tokMatch(qt[k], h[0])) inText++; else if (!tokMatch(qt[k], h[1])) { ok = false; break; } }
          if (!ok) return;
          res.qs.push([fi, qi, inText * 10 + (thSet[rows[qi][3]] ? 5 : 0) - Math.min(4, h[0].length / 150)]);
          res.byObj[fi] = (res.byObj[fi] || 0) + 1;
        });
      });
      res.qs.sort(function (a, b) { return b[2] - a[2]; });
      res.qTotal = res.qs.length; res.qTok = qt; res.objF = fset;
    }
    return res;
  }
  function qRow(fi, qi, hl) {
    var f = F[fi], q = Q[f.id][qi], s = esc(q[1]);
    if (hl) s = s.replace(hl, function (m, a, b) { return a + '<mark>' + b + '</mark>'; });
    return '<div class="nv-q nv-nochk"><div><p class="nv-q-t"><span class="nv-n">' + esc(q[0]) + '.</span>' + s + '</p><div class="nv-q-m">' +
      L(f.u, esc(f.name), 'nv-tag-l') + '<span class="nv-cite">' + (q[2] ? esc(q[2]) : 'в листе основание не указано') + '</span>' +
      (q[4] ? '<span class="nv-per">' + esc(q[4]) + '</span>' : '') + L(f.u, 'Открыть в листе', 'nv-res-go', '#v' + (qi + 1)) + '</div></div></div>';
  }
  var hint = $('#sRes').innerHTML, objOnly = null, lim = 15, inp = $('#sQ');
  function draw(q) {
    var out = '';
    if (!q.trim()) { $('#sRes').innerHTML = hint; return; }
    var r = search(q);
    if (r.off != null) {
      var o = D[r.off];
      out += '<p class="nv-replaced nv-mw" style="margin-top:24px">' + L(o.u, esc(o.s)) + ' не действует' + (o.to ? ' с ' + esc(o.to) : '') + '. ' +
        (o.rbi ? 'Вместо него: ' + o.rbi.map(function (j) { return L(D[j].u, esc(D[j].s)) + ' ' + badge(D[j]); }).join(' ') : esc(o.rb)) + '</p>';
    }
    if (r.cards.length) out += '<div class="nv-res-h"><h2>Разборы</h2></div><div class="nv-res-list">' + r.cards.slice(0, 4).map(function (x) {
      var c = C[x.i]; return L(c.u, '<div><b>' + esc(c.title) + '</b><small>' + esc(c.short.split('. ')[0]) + '.</small></div>' + ARROW, 'nv-res');
    }).join('') + '</div>';
    if (r.objs.length || r.comps.length) out += '<div class="nv-res-h"><h2>Объекты</h2></div><div class="nv-chips">' +
      r.objs.slice(0, 8).map(function (i) { return L(F[i].u, esc(F[i].name) + ' <b>' + F[i].n + '</b>', 'nv-chip'); }).join('') +
      r.comps.map(function (i) { return L(CO[i].u, esc(CO[i].name) + ' <b>подборка</b>', 'nv-chip'); }).join('') + '</div>';
    if (r.themes.length) out += '<div class="nv-res-h"><h2>Темы</h2></div><div class="nv-chips">' + r.themes.slice(0, 5).map(function (i) { return L(T[i].u, esc(T[i].name) + ' <b>' + fmtN(T[i].n) + '</b>', 'nv-chip'); }).join('') + '</div>';
    if (r.docs.length) out += '<div class="nv-res-h"><h2>Документы</h2><span>' + r.docs.length + '</span></div><div class="nv-res-list">' + r.docs.slice(0, 5).map(function (x) {
      var o = D[x.i]; return L(o.u, '<div><b>' + esc(o.s) + '</b><small>' + esc(o.t.length > 150 ? o.t.slice(0, 150) + '…' : o.t) + '</small></div><div class="nv-r">' + badge(o) + '</div>', 'nv-res');
    }).join('') + '</div>' + (r.docs.length > 5 ? '<div class="nv-showmore">' + L('dokumenty/', 'Все документы по запросу — ' + r.docs.length, 'nv-chip', '?q=' + encodeURIComponent(q)) + '</div>' : '');
    if (r.qTotal) {
      var objs = Object.keys(r.byObj).map(function (k) { return [+k, r.byObj[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
      if (objOnly != null && !r.byObj[objOnly]) objOnly = null;
      var list = objOnly == null ? r.qs : r.qs.filter(function (x) { return x[0] === objOnly; });
      var hl = mkHl(r.qTok.map(function (t) { return t.alts; }));
      out += '<div class="nv-res-h"><h2>Вопросы проверочных листов</h2><span>' + fmtN(r.qTotal) + (r.objF ? ' · только по названному объекту' : '') + '</span></div>' +
        (objs.length > 1 ? '<div class="nv-chips" style="margin-bottom:8px"><button type="button" class="nv-chip' + (objOnly == null ? ' nv-on' : '') + '" data-obj="">Все объекты</button>' + objs.slice(0, 8).map(function (x) {
          return '<button type="button" class="nv-chip' + (objOnly === x[0] ? ' nv-on' : '') + '" data-obj="' + x[0] + '">' + esc(F[x[0]].name) + ' <b>' + x[1] + '</b></button>';
        }).join('') + '</div>' : '') +
        list.slice(0, lim).map(function (x) { return qRow(x[0], x[1], hl); }).join('') +
        (list.length > lim ? '<button type="button" class="nv-btn nv-btn-s nv-btn-sm nv-showmore" id="sMore">Показать ещё ' + Math.min(30, list.length - lim) + ' из ' + (list.length - lim) + '</button>' : '');
    }
    if (!out) out = '<p class="nv-empty">Ничего не нашли. Попробуйте другое слово или номер документа.</p>';
    out += '<div class="nv-cta" style="margin-top:40px"><div><h2>Не нашли ответ?</h2><p>Задайте вопрос санитарному врачу: опишите ситуацию в комментарии к заявке.</p></div><div class="nv-cta-b"><a href="#zayavka" class="nv-btn nv-btn-p">Задать вопрос</a></div></div>';
    $('#sRes').innerHTML = out;
  }
  var q0 = ''; try { q0 = decodeURIComponent(((/[?&]q=([^&#]*)/.exec(location.search) || [])[1] || '').replace(/\+/g, ' ')); } catch (e) { }
  inp.value = q0; draw(q0);
  var tm;
  function run() { var v = inp.value; objOnly = null; lim = 15; try { history.replaceState(null, '', location.pathname + (v ? '?q=' + encodeURIComponent(v) : '')); } catch (e) { } draw(v); }
  inp.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(run, 180); });
  $('#sFind').addEventListener('submit', function (e) { e.preventDefault(); clearTimeout(tm); run(); });
  $('#sRes').addEventListener('click', function (e) {
    var b = e.target.closest('[data-obj]');
    if (b) { objOnly = b.getAttribute('data-obj') === '' ? null : +b.getAttribute('data-obj'); lim = 15; draw(inp.value); return; }
    if (e.target.closest('#sMore')) { lim += 30; draw(inp.value); }
  });
})();
