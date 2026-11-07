/* Поиск по сайту ПЕСТКОНТРОЛЬ Центра: движок и окно поиска.

   Загружается только по требованию: по нажатию на лупу в шапке или клавише «/» (загрузчик — блок <script id="srch-js">
   в <head> каждой страницы, его вставляет tools/menu/apply_menu.py) и на странице «Документы для Роспотребнадзора»
   при первом вводе в поиск по перечню (там используется только движок: PCSearch.engine).
   Индекс — search-index.json в корне сайта (tools/search/build_index.py собирает его из готовых страниц).

   Движок: приведение слов к основе (окончания), синонимы и бытовые названия («сэс» → «роспотребнадзор»,
   «крысы» → «дератизация»), исправление раскладки («frn lthfnbpfwbb» → «акт дератизации»), одна опечатка в длинных
   словах. Все слова запроса должны найтись в записи; если таких записей нет — показываем близкие.

   Цели Метрики (счётчик 113675622): poisk — пользователь открыл результат (клик или Enter), один раз за открытие окна;
   poisk_net — ничего не нашлось (через 1,5 с после ввода, один раз на запрос). Параметры: query, count, place.
   Сборка: npx esbuild@0.24.2 --minify --target=es2015 tools/search/search.js → search.min.js (tools/search/build_index.py). */
(function () {
  'use strict';
  var d = document, W = window;
  if (W.PCSearch) return;

  // ================================================================ движок
  var ENDS = ['иями', 'ями', 'ами', 'иях', 'ией', 'ого', 'его', 'ому', 'ему', 'ыми', 'ими', 'ых', 'их', 'ую', 'юю', 'ая', 'яя',
    'ое', 'ее', 'ые', 'ие', 'ый', 'ий', 'ой', 'ей', 'ов', 'ев', 'ам', 'ям', 'ах', 'ях', 'ом', 'ем', 'ия', 'ья', 'ии', 'ию',
    'ью', 'а', 'я', 'о', 'е', 'ы', 'и', 'у', 'ю', 'ь', 'й'];
  function set(s) { var o = {}; s.split(' ').forEach(function (w) { o[w] = 1; }); return o; }
  var STOP = set('и в во на по для как что о об с со к ли или а при от до из не за у какой какие какая какое каким нужен ' +
    'нужна нужны нужно надо мне нам где взять скачать документ документы документа документов документам есть ' +
    'бесплатно онлайн это ли же бы мы вы я наш ваш');
  var LATIN = set('haccp gmp iso ipm pdf word docx fssc prp tpk ppk sop');
  var LAY = { q: 'й', w: 'ц', e: 'у', r: 'к', t: 'е', y: 'н', u: 'г', i: 'ш', o: 'щ', p: 'з', '[': 'х', ']': 'ъ', a: 'ф', s: 'ы',
    d: 'в', f: 'а', g: 'п', h: 'р', j: 'о', k: 'л', l: 'д', ';': 'ж', "'": 'э', z: 'я', x: 'ч', c: 'с', v: 'м', b: 'и', n: 'т',
    m: 'ь', ',': 'б', '.': 'ю', '`': 'ё' };
  var SYN = {
    'сэс': ['сэс', 'роспотребнадзор', 'санпин'], 'роспотребнадзор': ['роспотребнадзор', 'сэс'],
    'чеклист': ['чеклист', 'проверочн'], 'проверочн': ['проверочн', 'чеклист'],
    'проверк': ['проверк', 'проверочн', 'инспектор'], 'инспектор': ['инспектор', 'проверк', 'проверочн'],
    'ппк': ['ппк', 'производственн'], 'хассп': ['хассп', 'haccp'], 'хасп': ['хассп', 'haccp'], 'haccp': ['haccp', 'хассп'],
    'gmp': ['gmp', 'надлежащ'], 'гмп': ['gmp', 'надлежащ'],
    'крыс': ['крыс', 'грызун', 'дератизац'], 'мыш': ['мыш', 'грызун', 'дератизац'], 'грызун': ['грызун', 'дератизац', 'крыс'],
    'дератизац': ['дератизац', 'грызун'],
    'таракан': ['таракан', 'насеком', 'дезинсекц'], 'мух': ['мух', 'насеком', 'дезинсекц'], 'клоп': ['клоп', 'насеком', 'дезинсекц'],
    'муравь': ['муравь', 'насеком', 'дезинсекц'], 'насеком': ['насеком', 'дезинсекц'], 'дезинсекц': ['дезинсекц', 'насеком'],
    'дезинфекц': ['дезинфекц', 'дезинфекцион'], 'вирус': ['вирус', 'дезинфекц'],
    'договор': ['договор', 'контракт'], 'контракт': ['контракт', 'договор'],
    'образец': ['образец', 'образц', 'шаблон', 'бланк', 'пример'], 'образц': ['образц', 'образец', 'шаблон', 'бланк', 'пример'],
    'шаблон': ['шаблон', 'образец', 'образц', 'бланк'], 'бланк': ['бланк', 'шаблон', 'образец', 'образц'],
    'пример': ['пример', 'образец', 'образц'], 'форм': ['форм', 'бланк', 'шаблон'],
    'общепит': ['общепит', 'общественн', 'ресторан', 'каф', 'столов'], 'ресторан': ['ресторан', 'общепит', 'общественн', 'каф'],
    'каф': ['каф', 'общепит', 'общественн', 'ресторан'], 'столов': ['столов', 'общепит', 'общественн'],
    'магазин': ['магазин', 'торговл', 'рынк', 'рынок'], 'торговл': ['торговл', 'магазин', 'рынк'], 'рынок': ['рынок', 'рынк', 'торговл'],
    'рынк': ['рынк', 'рынок', 'торговл'], 'супермаркет': ['супермаркет', 'магазин', 'торговл'],
    'склад': ['склад', 'хранен', 'логистик'], 'логистик': ['логистик', 'склад'],
    'гостиниц': ['гостиниц', 'отел'], 'отел': ['отел', 'гостиниц'], 'хостел': ['хостел', 'гостиниц', 'отел'],
    'клиник': ['клиник', 'медицинск'], 'больниц': ['больниц', 'медицинск'], 'медицинск': ['медицинск', 'клиник'],
    'стоматолог': ['стоматолог', 'медицинск', 'клиник'],
    'школ': ['школ', 'образовательн', 'детск'], 'детск': ['детск', 'школ', 'образовательн'], 'садик': ['садик', 'детск', 'школ'],
    'фарм': ['фарм', 'gmp', 'лекарств'], 'фармацевтическ': ['фармацевт', 'gmp'], 'аптек': ['аптек', 'фарм', 'лекарств'],
    'бан': ['бан', 'саун'], 'саун': ['саун', 'бан'], 'фитнес': ['фитнес', 'спорт', 'бассейн'], 'бассейн': ['бассейн', 'спорт'],
    'салон': ['салон', 'красот', 'парикмахер'], 'парикмахерск': ['парикмахер', 'салон', 'красот'], 'маникюр': ['маникюр', 'салон', 'красот'],
    'прачечн': ['прачечн', 'химчистк'], 'химчистк': ['химчистк', 'прачечн'],
    'лиценз': ['лиценз', 'реестр'], 'штраф': ['штраф', 'коап', 'ответственн'], 'коап': ['коап', 'штраф'],
    'отмен': ['отмен', 'утратил', 'замен', 'устаревш'], 'устаревш': ['устаревш', 'отмен', 'утратил', 'замен'],
    'утратил': ['утратил', 'отмен', 'устаревш'],
    'периодичност': ['периодичност', 'кратност'], 'кратност': ['кратност', 'периодичност'], 'част': ['част', 'кратност', 'периодичност'],
    'тпк': ['тпк', 'точк'], 'точк': ['точк', 'тпк'], 'ловушк': ['ловушк', 'тпк', 'точк'],
    'смыв': ['смыв', 'лаборатор', 'протокол'], 'протокол': ['протокол', 'лаборатор', 'смыв'], 'лаборатор': ['лаборатор', 'протокол', 'смыв'],
    'анализ': ['анализ', 'лаборатор', 'протокол'], 'медкнижк': ['медкнижк', 'медицинск', 'книжк'], 'книжк': ['книжк', 'медкнижк'],
    'вентиляц': ['вентиляц', 'воздуховод'], 'воздуховод': ['воздуховод', 'вентиляц'],
    'пестконтрол': ['пестконтрол', 'пестменеджмент'], 'пестменеджмент': ['пестменеджмент', 'пестконтрол'],
    'аудит': ['аудит', 'сэс'], 'цен': ['цен', 'стоимост', 'стоит', 'прайс', 'расценк'], 'стоимост': ['стоимост', 'цен', 'стоит', 'прайс'],
    'прайс': ['прайс', 'цен', 'стоимост', 'стоит'], 'расценк': ['расценк', 'цен', 'стоимост'], 'сколько': ['сколько', 'стоимост', 'цен', 'стоит']
  };

  function norm(s) {
    return String(s).toLowerCase().replace(/ё/g, 'е')
      .replace(/чек[\s\-]*лист/g, 'чеклист').replace(/пест[\s\-]*контрол/g, 'пестконтрол')
      .replace(/пест[\s\-]*менеджмент/g, 'пестменеджмент').replace(/мед[\s\-.]*книжк/g, 'медкнижк')
      .replace(/[^a-zа-я0-9]+/g, ' ').trim();
  }
  function stem(w) {
    if (/\d/.test(w) || /^[a-z]+$/.test(w) || w.length < 4) return w;
    for (var i = 0; i < ENDS.length; i++) {
      var e = ENDS[i];
      if (w.length - e.length >= 3 && w.slice(-e.length) === e) return w.slice(0, -e.length);
    }
    return w;
  }
  function tokens(s) {
    var seen = {}, out = [];
    norm(s).split(' ').forEach(function (w) { if (!w) return; w = stem(w); if (!seen[w]) { seen[w] = 1; out.push(w); } });
    return out;
  }
  function lev1(a, b) {
    if (a === b) return true;
    var la = a.length, lb = b.length;
    if (Math.abs(la - lb) > 1) return false;
    var i = 0, j = 0, e = 0;
    while (i < la && j < lb) {
      if (a[i] === b[j]) { i++; j++; continue; }
      if (++e > 1) return false;
      if (la > lb) i++; else if (lb > la) j++; else { i++; j++; }
    }
    return e + (la - i) + (lb - j) <= 1;
  }
  // совпадение слова запроса q со словом записи t: 1 — точно, 0.8 — начало слова, 0.5 — одна опечатка
  function mt(q, t) {
    if (t === q) return 1;
    var dig = /\d/.test(q);
    if (q.length >= 3 && t.lastIndexOf(q, 0) === 0) return 0.8;
    if (dig && q.length >= 2 && t.lastIndexOf(q, 0) === 0) return 0.8;
    if (!dig && q.length >= 5 && (lev1(q, t) || lev1(q, t.slice(0, q.length)))) return 0.5;
    return 0;
  }
  function synFor(t) {
    if (SYN[t]) return SYN[t];
    if (t.length >= 3) {
      for (var k in SYN) {
        if (k.length >= 4 && (t.lastIndexOf(k, 0) === 0 || k.lastIndexOf(t, 0) === 0)) return SYN[k].concat([t]);
      }
    }
    return [t];
  }
  // разбор запроса: исправление раскладки, стоп-слова, группы «слово + синонимы»
  function parse(raw) {
    var fixed = false;
    var q = String(raw || '').trim().split(/\s+/).filter(Boolean).map(function (t) {
      var l = t.toLowerCase();
      if (/[a-z]/.test(l) && !/[а-яё]/.test(l) && !LATIN[l.replace(/[^a-z]/g, '')]) {
        fixed = true;
        return l.split('').map(function (c) { return LAY[c] || c; }).join('');
      }
      return t;
    }).join(' ');
    var seen = {}, groups = [];
    norm(q).split(' ').forEach(function (w) {
      if (!w || STOP[w]) return;
      var s = stem(w);
      if (seen[s]) return;
      seen[s] = 1;
      groups.push({ t: s, alts: synFor(s) });
    });
    return { q: q, fixed: fixed ? q : null, groups: groups };
  }
  function groupHit(toks, g) {
    for (var a = 0; a < g.alts.length; a++) for (var i = 0; i < toks.length; i++) if (mt(g.alts[a], toks[i])) return true;
    return false;
  }
  function matchAll(toks, groups) {
    for (var k = 0; k < groups.length; k++) if (!groupHit(toks, groups[k])) return false;
    return groups.length > 0;
  }

  // ---------------------------------------------------------------- индекс
  // запись индекса: [вид, адрес, заголовок, описание, ключевые слова, № страницы в списке p]
  var KIND = { b: 'Папка к проверке', d: 'Документ', f: 'PDF', p: 'Страница', h: 'Раздел', q: 'Вопрос', c: 'Проверочный лист',
    n: 'Норматив', o: 'Отменён' };
  var TORD = { b: 0, d: 1, f: 2, p: 3, h: 4, q: 5, c: 6, n: 7, o: 8 };
  var IDX = null;
  function prep(J) {
    var pages = J.p || [];
    var items = (J.i || []).map(function (r, n) {
      var pt = pages[r[5]] ? pages[r[5]][0] : '';
      return { k: r[0], u: r[1], t: r[2], s: r[3] || '', w: r[4] || '', pi: r[5], pt: pt, n: n, nt: ' ' + norm(r[2]) + ' ',
        f: [[3, tokens(r[2])], [2, tokens(r[4] || '')], [1, tokens(r[3] || '')], [0.6, tokens(pt)]] };
    });
    return { v: J.v, pages: pages, items: items };
  }
  function scoreItem(it, groups) {
    var total = 0, matched = 0;
    for (var g = 0; g < groups.length; g++) {
      var G = groups[g], best = 0;
      for (var a = 0; a < G.alts.length; a++) {
        var q = G.alts[a], k = q === G.t ? 1 : 0.85, small = /^\d{1,2}$/.test(q) ? 0.4 : 1;
        for (var f = 0; f < it.f.length; f++) {
          var w = it.f[f][0], ts = it.f[f][1];
          for (var i = 0; i < ts.length; i++) {
            var m = mt(q, ts[i]);
            if (m) { var sc = w * m * k * small; if (sc > best) best = sc; }
          }
        }
      }
      if (best > 0) { matched++; total += best; }
    }
    return { total: total, matched: matched };
  }
  function search(raw) {
    var P = parse(raw);
    if (!IDX || !P.groups.length) return { P: P, res: [], mode: P.groups.length ? 'wait' : 'empty' };
    var n = P.groups.length, wantOld = P.groups.some(function (g) { return g.alts.indexOf('отмен') > -1; });
    var phrase = ' ' + norm(P.q) + ' ';
    var sc = [];
    IDX.items.forEach(function (it) {
      var r = scoreItem(it, P.groups);
      if (!r.matched) return;
      var adj = r.total;
      if (it.k === 'o') adj += wantOld ? 1.5 : -1.5;
      if (n > 1 && phrase.length > 4 && it.nt.indexOf(phrase.slice(0, -1)) > -1) adj += 1.5;  // фраза целиком в заголовке
      sc.push({ it: it, m: r.matched, a: adj });
    });
    var full = sc.filter(function (x) { return x.m === n; }), mode = 'full';
    if (!full.length) { full = sc; mode = sc.length ? 'partial' : 'none'; }
    full.sort(function (x, y) { return y.m - x.m || y.a - x.a || TORD[x.it.k] - TORD[y.it.k] || x.it.n - y.it.n; });
    return { P: P, res: full.slice(0, 40), mode: mode };
  }

  // ================================================================ окно поиска
  var ROOT = './', V = '', box = null, inp, list, st, more, none, hints, lastBtn = null, active = -1, shown = [], limit = 8;
  var loading = null, opened = 0, goalSent = false, netTimer = 0, netSent = {}, lastQ = '';
  var HINTS = ['Документы для ресторана', 'Акт дератизации', 'Проверочный лист', 'Журнал пест-контроля', 'СанПиН 3.3686-21',
    'Лицензия исполнителя', 'Программа производственного контроля', 'Отменённые СП'];

  function goal(name, params) { try { if (typeof W.ym === 'function') W.ym(113675622, 'reachGoal', name, params); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(text, groups) {  // подсветка найденных слов
    var out = '', re = /[A-Za-zА-Яа-яЁё0-9]+/g, last = 0, m;
    text = String(text);
    while ((m = re.exec(text))) {
      out += esc(text.slice(last, m.index));
      var w = stem(norm(m[0])), hit = false;
      for (var g = 0; g < groups.length && !hit; g++) for (var a = 0; a < groups[g].alts.length && !hit; a++) if (w && mt(groups[g].alts[a], w)) hit = true;
      out += hit ? '<mark>' + esc(m[0]) + '</mark>' : esc(m[0]);
      last = m.index + m[0].length;
    }
    return out + esc(text.slice(last));
  }
  function href(u) { return /^(https?:|tel:|mailto:)/.test(u) ? u : ROOT + u; }
  function askUrl(q) { return ROOT + 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/' + (q ? '?q=' + encodeURIComponent(q.slice(0, 200)) : '') + '#zayavka'; }

  var CSS = '.srch{position:fixed;inset:0;z-index:200;display:flex;justify-content:center;align-items:flex-start;padding:clamp(12px,8vh,96px) 16px 16px;font-family:inherit}' +
    '.srch[hidden]{display:none}' +
    '.srch-bg{position:absolute;inset:0;background:rgba(0,0,0,.72);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}' +
    '.srch-box{position:relative;width:min(760px,100%);max-height:calc(100vh - clamp(24px,12vh,140px));max-height:calc(100dvh - clamp(24px,12vh,140px));display:flex;flex-direction:column;background:#09090b;border:1px solid rgba(255,255,255,.12);border-radius:20px;box-shadow:0 30px 80px rgba(0,0,0,.6);overflow:hidden;color:#fff}' +
    '.srch-top{display:flex;align-items:center;gap:10px;padding:14px 14px 14px 18px;border-bottom:1px solid rgba(255,255,255,.08)}' +
    '.srch-top>svg{width:20px;height:20px;flex:none;color:#7c86ff}' +
    '.srch-in{flex:1;min-width:0;background:transparent;border:0;outline:0;color:#fff;font:inherit;font-size:18px;font-weight:400;padding:8px 0;-webkit-appearance:none;appearance:none}' +
    '.srch-in::placeholder{color:#84848e}.srch-in::-webkit-search-cancel-button{display:none}' +
    '.srch-x{flex:none;height:34px;min-width:34px;padding:0 10px;border-radius:10px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#d4d4d8;font:inherit;font-size:13px;cursor:pointer}' +
    '.srch-x:hover{border-color:#7c86ff;color:#fff}.srch-x:focus-visible,.srch-r:focus-visible,.srch-chip:focus-visible,.srch-more:focus-visible,.srch-none a:focus-visible{outline:2px solid #7c86ff;outline-offset:2px}' +
    '.srch-body{overflow:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;padding:10px 10px 14px}' +
    '.srch-st{margin:4px 8px 8px;font-size:13px;color:#9f9fa9;min-height:18px}.srch-st b{color:#fff;font-weight:500}' +
    '.srch-list{list-style:none;margin:0;padding:0;display:grid;gap:4px}' +
    '.srch-r{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:12px;row-gap:3px;padding:11px 12px;border-radius:12px;color:#fff;text-decoration:none;border:1px solid transparent}' +
    '.srch-r.on,.srch-r:hover{background:rgba(97,95,255,.14);border-color:rgba(124,134,255,.35)}' +
    '.srch-k{grid-row:1 / span 3;align-self:start;margin-top:2px;font-size:11px;font-weight:600;letter-spacing:.02em;line-height:1;padding:5px 7px;border-radius:7px;background:rgba(255,255,255,.07);color:#c7c9ff;white-space:nowrap}' +
    '.srch-k.k-b,.srch-k.k-d,.srch-k.k-f{background:rgba(124,134,255,.2);color:#fff}.srch-k.k-o{background:rgba(255,100,103,.16);color:#ffb4b5}.srch-k.k-n,.srch-k.k-c{background:rgba(253,199,0,.14);color:#ffe27a}' +
    '.srch-t{font-size:15px;font-weight:500;line-height:1.35}.srch-s{font-size:13px;line-height:1.45;color:#a1a1aa;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}' +
    '.srch-p{font-size:12px;color:#84848e;line-height:1.3}.srch mark{background:transparent;color:#a5abff;font-weight:600}' +
    '.srch-more{display:block;margin:8px auto 0;padding:9px 16px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#fff;font:inherit;font-size:14px;cursor:pointer}.srch-more:hover{border-color:#7c86ff}' +
    '.srch-hints{display:flex;flex-wrap:wrap;gap:8px;margin:4px 8px 6px}.srch-hints[hidden]{display:none}' +
    '.srch-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);color:#e4e4e7;font:inherit;font-size:14px;cursor:pointer}.srch-chip:hover{border-color:#7c86ff;color:#fff}' +
    '.srch-none{margin:12px 8px 0;padding:14px 16px;border-radius:14px;border:1px dashed rgba(124,134,255,.45);font-size:14px;line-height:1.5;color:#d4d4d8}.srch-none[hidden]{display:none}' +
    '.srch-none b{color:#fff;font-weight:500}.srch-none a{color:#a5abff;text-decoration:underline;text-underline-offset:2px}' +
    '.srch-foot{display:flex;flex-wrap:wrap;gap:6px 16px;justify-content:space-between;padding:10px 18px;border-top:1px solid rgba(255,255,255,.08);font-size:12px;color:#84848e}' +
    '.srch-foot kbd{font:inherit;font-size:11px;padding:2px 6px;border-radius:5px;border:1px solid rgba(255,255,255,.16);color:#d4d4d8}' +
    'html.srch-lock{overflow:hidden}' +
    '@media (max-width:760px){.srch{padding:0}.srch-box{width:100%;max-height:none;height:100%;border-radius:0;border:0}.srch-in{font-size:17px}.srch-foot{display:none}.srch-r{padding:12px 10px}}' +
    '@media (prefers-reduced-motion:no-preference){.srch-box{animation:srch-in .28s cubic-bezier(.16,1,.3,1)}@keyframes srch-in{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}}';

  var ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-3.6-3.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  function phoneLink() {  // номер берём из шапки: там его подменяет колл-трекинг
    var a = d.querySelector('.hdr .phone') || d.querySelector('a[href^="tel:"]');
    var tel = a ? a.getAttribute('href') : 'tel:+74951043570';
    var txt = a ? (a.textContent || '').replace(/\s+/g, ' ').trim() : '';
    if (!/\d/.test(txt)) txt = (tel || '').replace(/^tel:/, '').replace(/^\+7(\d{3})(\d{3})(\d{2})(\d{2})$/, '+7 ($1) $2-$3-$4');
    return '<a href="' + esc(tel) + '">' + esc(txt) + '</a>';
  }

  function build() {
    var st0 = d.createElement('style');
    st0.id = 'srch-css';
    st0.textContent = CSS;
    d.head.appendChild(st0);
    box = d.createElement('div');
    box.className = 'srch';
    box.hidden = true;
    box.setAttribute('data-lenis-prevent', '');
    box.innerHTML = '<div class="srch-bg" data-srch-close></div>' +
      '<div class="srch-box" role="dialog" aria-modal="true" aria-label="Поиск по сайту">' +
      '<div class="srch-top">' + ICON +
      '<input class="srch-in" type="search" enterkeyhint="search" autocomplete="off" autocorrect="off" spellcheck="false" maxlength="120" ' +
      'placeholder="Документ, норма или вопрос" aria-label="Что найти на сайте" role="combobox" aria-expanded="false" aria-controls="srch-list" aria-autocomplete="list">' +
      '<button class="srch-x" type="button" data-srch-close aria-label="Закрыть поиск">Esc</button></div>' +
      '<div class="srch-body">' +
      '<p class="srch-st" role="status" aria-live="polite"></p>' +
      '<div class="srch-hints"></div>' +
      '<ul class="srch-list" id="srch-list" role="listbox" aria-label="Результаты поиска"></ul>' +
      '<button class="srch-more" type="button" hidden></button>' +
      '<div class="srch-none" hidden></div></div>' +
      '<div class="srch-foot"><span><kbd>↑</kbd> <kbd>↓</kbd> выбрать · <kbd>Enter</kbd> открыть · <kbd>Esc</kbd> закрыть</span>' +
      '<span>Поиск по страницам, документам и образцам сайта</span></div></div>';
    d.body.appendChild(box);
    inp = box.querySelector('.srch-in');
    list = box.querySelector('.srch-list');
    st = box.querySelector('.srch-st');
    more = box.querySelector('.srch-more');
    none = box.querySelector('.srch-none');
    hints = box.querySelector('.srch-hints');
    hints.innerHTML = HINTS.map(function (h) { return '<button class="srch-chip" type="button">' + esc(h) + '</button>'; }).join('');

    inp.addEventListener('input', function () { limit = 8; run(); });
    inp.addEventListener('keydown', onKey);
    box.addEventListener('keydown', trap);
    box.addEventListener('click', function (e) {
      var t = e.target;
      if (t.closest('[data-srch-close]')) { close(); return; }
      var c = t.closest('.srch-chip');
      if (c) { inp.value = c.textContent; limit = 8; run(); inp.focus(); return; }
      if (t.closest('.srch-more')) { limit = 40; render(lastRes); return; }
      var r = t.closest('.srch-r');
      if (r) { sendGoal(); if (go(r, e)) e.preventDefault(); return; }
      if (t.closest('.srch-none a[href*="#zayavka"]')) sendGoal(true);
    });
    list.addEventListener('mousemove', function (e) {
      var r = e.target.closest('.srch-r');
      if (r) setActive(+r.getAttribute('data-i'), true);
    });
  }

  var lastRes = null;
  function run() {
    var q = inp.value;
    lastQ = q.trim();
    if (!lastQ) { lastRes = null; render(null); return; }
    if (!IDX) { st.textContent = 'Загружаем поиск…'; load(); return; }
    lastRes = search(q);
    render(lastRes);
    clearTimeout(netTimer);
    if (lastRes.mode === 'none' && lastQ.length >= 3 && !netSent[lastQ]) {
      var qq = lastQ;
      netTimer = setTimeout(function () {
        if (inp.value.trim() !== qq || netSent[qq]) return;
        netSent[qq] = 1;
        goal('poisk_net', { query: qq.slice(0, 100), count: 0, place: 'shapka' });
      }, 1500);
    }
  }
  function render(R) {
    active = -1;
    shown = [];
    inp.removeAttribute('aria-activedescendant');
    if (!R) {
      list.innerHTML = '';
      more.hidden = true;
      none.hidden = true;
      hints.hidden = false;
      inp.setAttribute('aria-expanded', 'false');
      st.textContent = IDX ? 'Например:' : 'Загружаем поиск…';
      return;
    }
    hints.hidden = R.mode !== 'empty';
    var groups = R.P.groups, fixed = R.P.fixed ? ' Искали «' + esc(R.P.fixed) + '».' : '';
    if (R.mode === 'empty') {
      st.textContent = 'Уточните запрос — например:';
      list.innerHTML = '';
      more.hidden = true;
      none.hidden = true;
      return;
    }
    shown = R.res.slice(0, limit);
    list.innerHTML = shown.map(function (x, i) {
      var it = x.it, path = it.k === 'p' ? 'Страница сайта' : (it.k === 'f' ? 'PDF · ' : '') + it.pt;
      return '<li role="presentation"><a class="srch-r" role="option" aria-selected="false" id="srch-o' + i + '" data-i="' + i + '" href="' +
        esc(href(it.u)) + '"' + (it.k === 'f' ? ' target="_blank" rel="noopener"' : '') + '>' +
        '<span class="srch-k k-' + it.k + '">' + KIND[it.k] + '</span>' +
        '<span class="srch-t">' + mark(it.t, groups) + '</span>' +
        (it.s ? '<span class="srch-s">' + mark(it.s, groups) + '</span>' : '') +
        '<span class="srch-p">' + esc(path) + '</span></a></li>';
    }).join('');
    inp.setAttribute('aria-expanded', shown.length ? 'true' : 'false');
    var total = R.res.length;
    more.hidden = total <= shown.length;
    more.textContent = 'Показать ещё ' + (total - shown.length);
    if (R.mode === 'full') st.innerHTML = 'Найдено: <b>' + total + (total >= 40 ? '+' : '') + '</b>.' + fixed;
    else if (R.mode === 'partial') st.innerHTML = 'Точных совпадений нет — показываем близкие.' + fixed;
    else st.innerHTML = 'Ничего не нашлось.' + fixed;
    none.hidden = false;
    none.innerHTML = (R.mode === 'full' ? '<b>Не нашли нужное?</b> ' : '<b>Не нашли документ?</b> ') +
      '<a href="' + esc(askUrl(lastQ)) + '">Напишите, что ищете</a> — санитарный врач подскажет, какой документ нужен вашему объекту. ' +
      'Или позвоните: ' + phoneLink() + '.';
  }
  function setActive(i, fromMouse) {
    var rs = list.querySelectorAll('.srch-r');
    if (!rs.length) return;
    if (i < 0) i = rs.length - 1;
    if (i >= rs.length) i = 0;
    for (var k = 0; k < rs.length; k++) { rs[k].classList.toggle('on', k === i); rs[k].setAttribute('aria-selected', k === i ? 'true' : 'false'); }
    active = i;
    inp.setAttribute('aria-activedescendant', 'srch-o' + i);
    if (!fromMouse && rs[i].scrollIntoView) rs[i].scrollIntoView({ block: 'nearest' });
  }
  function onKey(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
    else if (e.key === 'Enter') {
      var rs = list.querySelectorAll('.srch-r');
      if (!rs.length) return;
      e.preventDefault();
      var r = rs[active > -1 ? active : 0];
      sendGoal();
      if (!go(r, e)) { if (r.target === '_blank') W.open(r.href, '_blank', 'noopener'); else location.href = r.href; }
    }
  }
  function trap(e) {
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;
    var f = [].slice.call(box.querySelectorAll('input,button:not([hidden]),a[href]')).filter(function (el) {
      return el.offsetParent !== null && !el.closest('[hidden]');
    });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  function sendGoal(ask) {
    if (goalSent || !lastQ) return;
    goalSent = true;
    goal('poisk', { query: lastQ.slice(0, 100), count: lastRes ? lastRes.res.length : 0, place: ask ? 'shapka_vopros' : 'shapka' });
  }
  // переход внутри текущей страницы: закрыть окно и прокрутить; FAQ — раскрыть ответ; сборщик папки — выбрать объект
  function go(a, e) {
    if (a.target === '_blank') return false;
    var u;
    try { u = new URL(a.href, location.href); } catch (_) { return false; }
    // та же страница: адрес без параметров (#q3, #d-…) открываем на месте, не теряя выбранный объект (?obekt=) и отметки
    if (u.pathname !== location.pathname || u.search && u.search !== location.search && !/obekt=/.test(u.search)) return false;
    if (e && (e.ctrlKey || e.metaKey || e.shiftKey)) return false;
    var m = /obekt=([a-z]+)/.exec(u.search);
    var chip = m && d.querySelector('input[name="dk-obekt"][value="' + m[1] + '"]');
    if (m && !chip) return false;
    close(true);
    if (chip) { chip.checked = true; chip.dispatchEvent(new Event('change', { bubbles: true })); }
    var id = decodeURIComponent(u.hash.slice(1)), el = id && d.getElementById(id);
    if (el) {
      if (/^q\d+$/.test(id) && el.getAttribute('aria-expanded') === 'false') el.click();
      var row = el.closest('tr');
      if (row && row.hidden) { var dq = d.getElementById('dk-q'); if (dq && dq.value) { dq.value = ''; dq.dispatchEvent(new Event('input')); } }
      try { history.pushState(null, '', u.pathname + (u.search || location.search) + u.hash); } catch (_) {}
      setTimeout(function () { el.scrollIntoView({ behavior: 'smooth', block: /^q\d+$/.test(id) || row ? 'center' : 'start' }); }, 30);
      if (row) { row.classList.add('dk-hl'); setTimeout(function () { row.classList.remove('dk-hl'); }, 2400); }
    }
    return true;
  }
  function load() {
    if (loading) return loading;
    loading = fetch(ROOT + 'search-index.json?v=' + V, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (J) {
      IDX = prep(J);
      if (box && !box.hidden) run();
    }).catch(function () {
      loading = null;
      if (st) st.innerHTML = 'Поиск временно недоступен. Откройте <a href="' + esc(askUrl('')) .replace('#zayavka', '') + '">перечень документов для проверки</a> или позвоните: ' + phoneLink() + '.';
    });
    return loading;
  }
  function open(root, v, opts) {
    ROOT = root || './';
    V = v || '';
    opts = opts || {};
    if (!box) build();
    if (!box.hidden) { inp.focus(); return; }
    lastBtn = opts.btn || d.activeElement;
    goalSent = false;
    opened++;
    box.hidden = false;
    d.documentElement.classList.add('srch-lock');
    if (opts.q) inp.value = opts.q;
    run();
    load();
    try { inp.focus({ preventScroll: true }); } catch (_) { inp.focus(); }
    inp.select();
  }
  function close(keepFocus) {
    if (!box || box.hidden) return;
    clearTimeout(netTimer);
    box.hidden = true;
    d.documentElement.classList.remove('srch-lock');
    if (!keepFocus && lastBtn && lastBtn.focus) try { lastBtn.focus({ preventScroll: true }); } catch (_) {}
  }

  W.PCSearch = {
    engine: { parse: parse, tokens: tokens, matchAll: matchAll, norm: norm, stem: stem, mt: mt },
    open: open,
    close: close,
    _search: function (q) { return IDX ? search(q) : null; },
    _load: function (root, v) { ROOT = root || ROOT; V = v || V; return load(); }
  };
})();
