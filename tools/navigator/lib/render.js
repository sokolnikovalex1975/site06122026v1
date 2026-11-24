/* Санитарный навигатор: разметка блоков. Перенос отрисовки из прототипа (sannav/app.js) в статические страницы.
   Классы пишутся без приставки; build.js добавляет «nv-» ко всем, кроме помеченных знаком «=» (классы самого сайта).
   Ссылки внутри раздела начинаются с {S} (корень раздела), на остальной сайт — с {ROOT}. */
'use strict';
const { N, Q, fIdx, dIdx, tIdx, cIdx, coIdx } = require('./data');
const F = N.forms, D = N.docs, T = N.themes, C = N.cards, CO = N.composites, G = N.groups;
const NBSP = '\u00a0';

function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'); }
function fmtN(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, NBSP); }
function pl(n, f) { const a = Math.abs(n) % 100, b = a % 10; return a > 10 && a < 20 ? f[2] : b > 1 && b < 5 ? f[1] : b === 1 ? f[0] : f[2]; }
function nq(n) { return fmtN(n) + NBSP + pl(n, ['вопрос', 'вопроса', 'вопросов']); }
function nl(n) { return n + NBSP + pl(n, ['лист', 'листа', 'листов']); }
function inL(n) { return 'в' + NBSP + n + NBSP + pl(n, ['листе', 'листах', 'листах']); }
const MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
function fmtDate(iso, noYear) { const p = iso.split('-'); return (+p[2]) + NBSP + MONTHS[+p[1] - 1] + (noYear ? '' : NBSP + p[0]); }
function isoToday() { const d = new Date(Date.now() + 3 * 3600e3); return d.toISOString().slice(0, 10); }   // дата сборки по Москве
const TODAY = isoToday() > N.meta.today ? isoToday() : N.meta.today;
function daysTo(iso) { return Math.round((Date.parse(iso + 'T00:00:00Z') - Date.parse(TODAY + 'T00:00:00Z')) / 864e5); }
function inDays(n) {
  if (n === 0) return 'сегодня';
  if (n < 0) return '';
  if (n < 120) return 'через ' + n + NBSP + pl(n, ['день', 'дня', 'дней']);
  const m = Math.round(n / 30.4);
  if (m < 24) return 'через ' + m + NBSP + pl(m, ['месяц', 'месяца', 'месяцев']);
  const y = Math.round(n / 365);
  return 'через ' + y + NBSP + pl(y, ['год', 'года', 'лет']);
}

/* адрес из прототипа («/o/578_p02?doc=…») → адрес страницы раздела */
function U(p) {
  let q = '', i = p.indexOf('?');
  if (i >= 0) { q = p.slice(i); p = p.slice(0, i); }
  const s = p.split('/').filter(Boolean);
  const par = {}; if (q) q.slice(1).split('&').forEach(kv => { const j = kv.indexOf('='); par[kv.slice(0, j)] = kv.slice(j + 1); });
  switch (s[0]) {
    case undefined: return '{S}';
    case 'objects': return '{S}obekty/';
    case 'o': return '{S}obekty/' + F[fIdx[s[1]]].slug + '/' + (par.doc ? '?doc=' + dIdx[par.doc] : '');
    case 'c': return '{S}obekty/' + CO[coIdx[s[1]]].slug + '/';
    case 'themes': return '{S}temy/';
    case 't': return '{S}temy/' + T[tIdx[s[1]]].slug + '/' + (par.o ? '?o=' + F[fIdx[par.o]].slug : '');
    case 'answers': return '{S}voprosy/';
    case 'a': { const c = C[cIdx[s[1]]]; return c.ext ? '{S}' + c.ext : '{S}voprosy/' + c.slug + '/'; }
    case 'docs': return '{S}dokumenty/' + q;
    case 'd': return '{S}dokumenty/' + D[dIdx[s[1]]].slug + '/';
    case 'k': return s[1] === 'per' ? '{S}periodichnost/' + (par.o ? '?o=' + F[fIdx[par.o]].slug : '') : '{S}kalendar/';
    case 's': return '{S}poisk/' + q;
    case 'ask': return '#zayavka';
    case 'about': return '{S}o-razdele/';
  }
  throw new Error('неизвестный адрес: ' + p);
}
function A(p, inner, cls, extra) { return '<a href="' + U(p) + '"' + (cls ? ' class="' + cls + '"' : '') + (extra || '') + '>' + inner + '</a>'; }
function X(url, inner, cls) { return '<a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer"' + (cls ? ' class="' + cls + '"' : '') + '>' + inner + '</a>'; }
function S(path, inner, cls) { return '<a href="{ROOT}' + path + '"' + (cls ? ' class="' + cls + '"' : '') + '>' + inner + '</a>'; }   // страница остального сайта
const ARROW = '<svg class="arrow" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const TICK = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

const ORD = { '578': D[dIdx.prikaz578], '580': D[dIdx.prikaz580] };
const qCard = {};
C.forEach((c, ci) => c.ask.forEach(a => { const k = a[0] + ':' + a[1]; if (!(k in qCard)) qCard[k] = ci; }));
const dCards = {};
C.forEach((c, ci) => c.basis.forEach(b => (dCards[b[0]] = dCards[b[0]] || []).push(ci)));

/* ───────── статусы ───────── */
function vis(d) {
  if (d.c === 'ok') return { c: 'ok', t: 'Действует', s: 'действует' };
  if (d.c === 'lim') {
    const n = d.toi ? daysTo(d.toi) : 9999, dt = (d.to || '').slice(0, 10);
    if (n < 0) return { c: 'off', t: 'Срок истёк ' + dt, s: 'срок истёк ' + dt };
    return { c: n <= 366 ? 'lim' : 'ok', t: 'Действует до ' + dt, s: 'до ' + dt };
  }
  if (d.c === 'off') { const z = d.st.indexOf('Заменён') === 0 ? 'Заменён' : 'Утратил силу'; return { c: 'off', t: z, s: z.toLowerCase() }; }
  if (d.c === 'proj') return { c: 'proj', t: 'Проект', s: 'проект' };
  if (d.c === 'soon') { const w = d.fr ? 'Вступает в силу ' + d.fr.slice(0, 10) : 'Не вступил в силу'; return { c: 'soon', t: w, s: w.toLowerCase() }; }
  if (d.c === 'srv') return { c: 'srv', t: 'Сервис', s: 'сервис' };
  const o = d.st.split(';')[0]; return { c: 'vol', t: o, s: o.toLowerCase() };
}
function badge(d) { const v = vis(d); return '<span class="badge b-' + v.c + '">' + esc(v.t) + '</span>'; }
function dotA(d, extra) { const v = vis(d); return A('/d/' + d.id, '<b><span class="dot ' + v.c + '"></span>' + esc(d.s) + '</b><small>' + esc(v.s) + (extra ? ' · ' + extra : '') + '</small>'); }
function docA(i, label) { return A('/d/' + D[i].id, esc(label || D[i].s)); }
function rbHtml(d) {
  if (!d.rbi) return esc(d.rb || '');
  return d.rbi.map(j => docA(j) + ' ' + badge(D[j])).join(' ') + (d.rb && d.rb.length > 34 ? '<br><span class="small muted">' + esc(d.rb) + '</span>' : '');
}

/* ───────── вопрос листа ───────── */
const DIM = /(у контролируемого лица|контролируемым лицом|контролируемое лицо|контролируемого лица|контролируемому лицу)/g;
function qText(text) { return esc(text).replace(DIM, '<span class="dim">$1</span>'); }
function docMark(d) {
  if (d.c === 'off') return ' <span class="off">(утратил силу)</span>';
  if (d.c === 'soon') return ' <span class="off">(' + (d.fr ? 'вступает в силу ' + esc(d.fr.slice(0, 10)) : 'не вступил в силу') + ')</span>';
  return '';
}
function linkDocs(text, list, addMissing) {
  let s = esc(text);
  if (!s) return '';
  const slots = [], missing = [];
  list.forEach(di => {
    const d = D[di];
    const hit = (d.cs || [d.s]).some(name => {
      const re = new RegExp(reEsc(esc(name)) + (/\d$/.test(name) ? '(?!\\d)' : ''), 'gi');
      if (!re.test(s)) return false;
      re.lastIndex = 0;
      s = s.replace(re, m => { slots.push('<a href="' + U('/d/' + d.id) + '" title="' + esc(vis(d).t) + '">' + m + '</a>' + docMark(d)); return '\u0001' + (slots.length - 1) + '\u0002'; });
      return true;
    });
    if (!hit) missing.push(d);
  });
  s = s.replace(/\u0001(\d+)\u0002/g, (m, i) => slots[+i]);
  if (addMissing && missing.length) s += ' <span class="cite-doc">Документ: ' + missing.map(d => '<a href="' + U('/d/' + d.id) + '" title="' + esc(vis(d).t) + '">' + esc(d.s) + '</a>' + docMark(d)).join(', ') + '</span>';
  return s;
}
function citeHtml(q) { return linkDocs(q[2], q[4], true); }
/* o: check — с отметкой; obj — показать объект; theme — показать тему; nocard; hidden — свёрнут до нажатия «Показать все»; data — служебные атрибуты для фильтров */
function qRow(fi, qi, o) {
  o = o || {};
  const f = F[fi], q = Q[f.id][qi], meta = [];
  if (o.obj) meta.push(A('/o/' + f.id, esc(f.name), 'tag-l'));
  meta.push('<span class="cite">' + (q[2] ? citeHtml(q) : 'в листе основание не указано') + '</span>');
  if (q[6]) meta.push('<span class="per">' + esc(q[6]) + '</span>');
  if (o.theme) meta.push(A('/t/' + T[q[3]].id, esc(T[q[3]].short), 'tag-l tag-t'));
  const ck = qCard[fi + ':' + qi];
  if (ck != null && !o.nocard) meta.push(A('/a/' + C[ck].id, 'Разбор', 'razbor'));
  let attrs = '';
  if (o.data) attrs = ' id="v' + (qi + 1) + '" data-i="' + qi + '" data-t="' + q[3] + '" data-s="' + q[5] + '" data-p="' + q[7] + '"' + (q[4].length ? ' data-d="' + q[4].join(' ') + '"' : '');
  if (o.f) attrs += ' data-f="' + fi + '"';
  return '<div class="q' + (o.check ? '' : ' nochk') + '"' + attrs + (o.hidden ? ' hidden' : '') + '>' +
    (o.check ? '<label class="q-c"><input type="checkbox" aria-label="Вопрос ' + esc(q[0]) + ' выполняется"><span>' + TICK + '</span></label>' : '') +
    '<div><p class="q-t"><span class="n">' + esc(q[0]) + '.</span>' + qText(q[1]) + '</p><div class="q-m">' + meta.join('') + '</div></div></div>';
}

/* ───────── плитки и списки ───────── */
function evItems(e, limit) {
  const past = e.d <= TODAY; let out = [];
  e.items.forEach(x => {
    if (x.k === 'repl') out.push(docA(x.old) + ' <span class="ev-k">' + (past ? 'заменён на' : 'будет заменён на') + '</span> ' + docA(x['new']));
    else if (x.k === 'start') out.push('<span class="ev-k">' + (past ? 'Вступил в силу:' : 'Вступает в силу:') + '</span> ' + docA(x.d));
    else if (x.k === 'end') out.push('<span class="ev-k">Утратил силу:</span> ' + docA(x.d));
    else if (x.k === 'exp') out.push('<span class="ev-k">' + (past ? 'Истёк срок действия:' : 'Истекает срок действия:') + '</span> ' + docA(x.d));
    else if (x.k === 'note') out.push(esc(x.text) + '. <span class="ev-k">' + esc(x.what) + '.</span> ' + X(x.u, 'Источник', 'ext'));
  });
  let extra = 0;
  if (limit && out.length > limit) { extra = out.length - limit; out = out.slice(0, limit); }
  return out.map(h => '<div>' + h + '</div>').join('') + (extra ? '<div class="ev-k">и ещё ' + extra + ' — ' + A('/k', 'в календаре') + '</div>' : '');
}
function evRow(e, limit) {
  const n = daysTo(e.d), rel = inDays(n);
  return '<div class="ev"><div class="ev-d"><time datetime="' + e.d + '">' + fmtDate(e.d) + '</time>' + (rel ? '<small class="' + (n <= 200 ? 'soon' : '') + '">' + rel + '</small>' : '') + '</div><div class="ev-b">' + evItems(e, limit) + '</div></div>';
}
function objTiles() {
  return G.map(g => {
    const tiles = F.filter(f => f.group === g.id).map(f => A('/o/' + f.id, '<span>' + esc(f.name) + '</span><i>' + f.n + '</i>', 'obj', ' data-k="' + esc((f.name + ' ' + f.hint).toLowerCase()) + '"'))
      .concat(CO.filter(c => c.group === g.id).map(c => A('/c/' + c.id, '<span>' + esc(c.name) + '</span><i>подборка</i>', 'obj comp', ' data-k="' + esc(c.name.toLowerCase()) + '"')));
    return tiles.length ? '<div class="grp"><p class="grp-h">' + esc(g.name) + '</p><div class="objs">' + tiles.join('') + '</div></div>' : '';
  }).join('');
}
function themeTiles() {
  return '<div class="themes">' + T.map(t => A('/t/' + t.id, '<div class="theme-h"><b>' + esc(t.name) + '</b><i>' + fmtN(t.n) + '</i></div><p>' + esc(t.hint) + '</p>', 'theme')).join('') + '</div>';
}
function cardTiles(list) {
  return '<div class="answers">' + list.map(c => A('/a/' + c.id, '<span class="tag">' + esc(T[c.theme].short) + '</span><b>' + esc(c.title) + '</b><p>' + esc(c.short) + '</p>', 'answer')).join('') + '</div>';
}
function roleTasks(i) { return N.roles[i].tasks.map(t => A(t[1], '<span>' + esc(t[0]) + '</span>' + ARROW, 'task')).join(''); }

function formDocs(fid) {
  const cnt = {};
  Q[fid].forEach(q => q[4].forEach(d => { cnt[d] = (cnt[d] || 0) + 1; }));
  return Object.keys(cnt).map(k => [+k, cnt[k]]).sort((a, b) => b[1] - a[1]);
}
function asideDocs(list, title) {
  if (!list.length) return '';
  return '<div class="panel"><p class="panel-t">' + title + '</p><div class="dl">' + list.slice(0, 7).map(x => dotA(D[x[0]], nq(x[1]))).join('') + '</div></div>';
}
function asideCards(list) {
  if (!list.length) return '';
  return '<div class="panel"><p class="panel-t">Разборы</p><div class="dl">' + list.map(ci => A('/a/' + C[ci].id, '<b>' + esc(C[ci].title) + '</b>')).join('') + '</div></div>';
}
/* на странице — одна ссылка на подходящую услугу */
const SERVICES = {
  audit: ['sanitarnyy-audit/', 'Санитарный аудит', 'Специалист пройдёт эти вопросы на объекте и покажет, что исправить до проверки.'],
  rest: ['restorany-i-kafe/', 'Пест-контроль ресторанов и кафе', 'Защита от насекомых и грызунов с документами для проверки.'],
  shop: ['magaziny-i-torgovye-seti/', 'Пест-контроль магазинов', 'Защита от насекомых и грызунов с документами для проверки.'],
  hotel: ['gostinitsy/', 'Пест-контроль гостиниц', 'Защита от насекомых и грызунов с документами для проверки.'],
  sklad: ['sklady-i-logistika/', 'Дератизация и дезинсекция складов', 'Защита от насекомых и грызунов с документами для проверки.'],
  ofis: ['biznes-tsentry-torgovye-tsentry-predpriyatiya/', 'Пест-контроль бизнес-центров и ТЦ', 'Защита от насекомых и грызунов с документами для проверки.'],
  food: ['pishchevoe-proizvodstvo/', 'Пест-контроль на пищевом производстве', 'Защита от насекомых и грызунов с документами для проверки.'],
  farma: ['farmatsevticheskie-proizvodstva/', 'Пест-контроль фармацевтического производства', 'Защита от насекомых и грызунов с документами для проверки.'],
  pest: ['deratizatsiya-i-dezinsektsiya/', 'Дератизация и дезинсекция', 'Обследования, учёт и обработки по договору — с актами и журналом.'],
  dez: ['dezinfektsiya/', 'Дезинфекция помещений', 'Обработка помещений с актом и подбором средства под объект.'],
  vent: ['ochistka-dezinfektsiya-ventilyatsii/', 'Очистка и дезинфекция вентиляции', 'Обследование, очистка и дезинфекция систем с актом и фотоотчётом.'],
  ppk: ['razrabotka-ppk/', 'Разработка программы производственного контроля', 'Программа под ваш объект: перечень исследований, периодичность, ответственные.'],
  lab: ['laboratornye-issledovaniya/', 'Лабораторные исследования', 'Смывы, воздух и вода по программе производственного контроля.']
};
const SVC_FORM = { '580_p02': 'rest', '580_p01': 'shop', '578_p01': 'shop', '578_p02': 'hotel', sklad: 'sklad', ofis: 'ofis', pishcheprom: 'food', farma: 'farma' };
const SVC_THEME = { vrediteli: 'pest', dez: 'dez', vozduh: 'vent', pk: 'ppk' };
function asideHelp(key) {
  const s = SERVICES[key || 'audit'];
  return '<div class="panel"><p class="panel-t">Нужна помощь</p><p class="small muted">' + s[2] + '</p>' +
    '<div class="btns-col">' + S(s[0], s[1], 'btn btn-p btn-sm') + '<a href="#zayavka" class="btn btn-s btn-sm">Задать вопрос врачу</a></div></div>';
}

/* ───────── главная ───────── */
function homeBody() {
  const past = N.events.filter(e => e.d <= TODAY).slice(-3).reverse();
  const fut = N.events.filter(e => e.d > TODAY).slice(0, 4);
  return '<div class="=wrap page">' +
    '<div class="facts">' +
    '<div class="fact"><b>' + N.meta.forms + '</b><span>проверочных листов Роспотребнадзора</span></div>' +
    '<div class="fact"><b>' + fmtN(N.meta.questions) + '</b><span>' + pl(N.meta.questions, ['вопрос', 'вопроса', 'вопросов']) + ' инспектора — с документом и пунктом</span></div>' +
    '<div class="fact"><b>' + N.meta.docs + '</b><span>' + pl(N.meta.docs, ['документ', 'документа', 'документов']) + ' — со статусом и его основанием</span></div>' +
    '<div class="fact"><b>' + N.meta.checked + '</b><span>дата сверки статусов</span></div></div>' +

    '<section class="sec" id="sposoby"><div class="sec-h"><h2>Четыре способа найти ответ</h2></div><div class="ways">' +
    A('/objects', '<span class="way-n">01</span><h3>По объекту</h3><p>Выберите гостиницу, кафе, магазин, клинику или школу и увидите всё, что спросит инспектор.</p><span class="go">' + F.length + ' объектов и ' + CO.length + ' подборки</span>', 'way') +
    A('/themes', '<span class="way-n">02</span><h3>По теме</h3><p>Вентиляция, вода, отходы, персонал, насекомые и грызуны — требования по всем объектам сразу.</p><span class="go">' + T.length + ' тем</span>', 'way') +
    A('/docs', '<span class="way-n">03</span><h3>По документу</h3><p>Действует ли документ, до какого числа, чем заменён и в каких листах на него ссылаются.</p><span class="go">' + D.length + ' документов</span>', 'way') +
    A('/k', '<span class="way-n">04</span><h3>По сроку</h3><p>Что изменилось, какие документы скоро истекают и что нужно делать каждый день, месяц и год.</p><span class="go">Календарь и периодичность</span>', 'way') +
    '</div></section>' +

    '<section class="sec" id="roli"><div class="sec-h"><h2>Кто вы</h2><p>Выберите роль — покажем, с чего начать</p></div>' +
    '<div class="role-tabs" role="tablist" aria-label="Роль">' + N.roles.map((r, i) => '<button class="role-tab" role="tab" id="rt' + i + '" aria-controls="rp' + i + '" data-role="' + i + '" aria-selected="' + (i === 0) + '">' + esc(r.name) + '</button>').join('') + '</div>' +
    N.roles.map((r, i) => '<div class="role-p" id="rp' + i + '" role="tabpanel" aria-labelledby="rt' + i + '"' + (i ? ' hidden' : '') + '><p class="role-hint">' + esc(r.hint) + '</p><div class="tasks">' + roleTasks(i) + '</div></div>').join('') + '</section>' +

    '<section class="sec" id="obekty"><div class="sec-h"><h2>Ваш объект</h2>' + A('/objects', 'Все объекты', 'more') + '</div>' +
    '<p class="muted small mw">Число рядом с названием — сколько вопросов в проверочном листе. Пунктирная рамка — подборка редакции для объектов, у которых своего листа нет.</p>' + objTiles() + '</section>' +

    '<section class="sec" id="temy"><div class="sec-h"><h2>Темы</h2>' + A('/themes', 'Все темы', 'more') + '</div>' + themeTiles() + '</section>' +

    '<section class="sec" id="razbory"><div class="sec-h"><h2>Разборы: короткие ответы на частые вопросы</h2>' + A('/answers', 'Все разборы', 'more') + '</div>' + cardTiles(C.slice(0, 6)) + '</section>' +

    '<section class="sec" id="izmeneniya"><div class="sec-h"><h2>Что изменилось и что впереди</h2>' + A('/k', 'Весь календарь', 'more') + '</div><div class="split">' +
    '<div class="panel"><p class="panel-t">Впереди</p>' + fut.map(e => evRow(e, 3)).join('') + '</div>' +
    '<div class="panel"><p class="panel-t">Уже произошло</p>' + past.map(e => evRow(e, 3)).join('') + '</div></div></section>' +

    '<section class="sec"><div class="cta"><div><h2>Не нашли ответ?</h2><p>Задайте вопрос санитарному врачу: опишите ситуацию в комментарии к заявке — ответим со ссылкой на документ и пункт.</p></div>' +
    '<div class="cta-b"><a href="#zayavka" class="btn btn-p">Задать вопрос</a>' + S('sanitarnyy-audit/', 'Санитарный аудит объекта', 'btn btn-s') + '</div></div></section></div>';
}

/* ───────── списки: объекты, темы, разборы ───────── */
function objectsBody() {
  return '<div class="=wrap page" data-nv="objects">' +
    '<div class="toolbar first"><input class="filter" id="objF" type="search" placeholder="Найти объект: кафе, школа, аптека" aria-label="Найти объект" style="max-width:420px"></div>' +
    '<div id="objList">' + objTiles() + '</div><p class="empty" id="objNone" hidden>Такого объекта нет. Попробуйте другое слово или <a href="#zayavka" class="link">напишите нам</a>.</p>' +
    '<div class="note mw" style="margin-top:32px"><b>Нет вашего объекта?</b> Для склада, офиса, пищевого и фармацевтического производства отдельных проверочных листов в приказах № 578 и № 580 нет. Для них собраны подборки из общих листов — они отмечены пунктирной рамкой. <a href="#zayavka" class="link">Напишите, какого объекта не хватает</a>.</div></div>';
}
function themesBody() {
  return '<div class="=wrap page">' + themeTiles() +
    '<p class="note mw" style="margin-top:32px">Темы присвоены вопросам автоматически, по ключевым словам. Распределение ещё не проверено санитарным врачом, возможны ошибки.</p></div>';
}
function answersBody(extra) {
  return '<div class="=wrap page">' + cardTiles(C.filter(c => !c.ext)) +
    (extra && extra.length ? '<section class="sec"><div class="sec-h"><h2>Подробные материалы</h2></div><div class="answers">' + extra.map(x =>
      '<a href="{S}' + x.path + '" class="answer"><span class="tag">' + esc(x.tag) + '</span><b>' + esc(x.title) + '</b><p>' + esc(x.text) + '</p></a>').join('') + '</div></section>' : '') +
    '<p class="note mw" style="margin-top:32px">В разборах блок «Что требуется» составлен по формулировкам проверочных листов и текстам документов. Блоки «Что сделать» и «Чем подтвердить» — практика редакции, а не текст документа; санитарный врач их ещё не проверял.</p></div>';
}

/* ───────── объект ───────── */
function objectBody(fid) {
  const fi = fIdx[fid], f = F[fi], qs = Q[fid], ord = ORD[f.order];
  const docs = formDocs(fid);
  const cards = []; C.forEach((c, ci) => { if (c.ask.some(a => a[0] === fi)) cards.push(ci); });
  const soon = docs.filter(x => D[x[0]].c === 'lim' && vis(D[x[0]]).c === 'lim');
  const offd = docs.filter(x => D[x[0]].c === 'off');
  const notyet = docs.filter(x => D[x[0]].c === 'soon');
  // по умолчанию — по темам
  const gs = [], map = {};
  qs.forEach((q, i) => { if (!(q[3] in map)) { map[q[3]] = { key: q[3], items: [] }; gs.push(map[q[3]]); } map[q[3]].items.push(i); });
  gs.sort((a, b) => a.key - b.key);
  const list = gs.map((g, gi) => '<section class="qsec" id="g' + gi + '"><div class="qsec-h"><h2>' + esc(T[g.key].name) + '</h2><span>' + nq(g.items.length) + '</span></div>' +
    g.items.map(i => qRow(fi, i, { check: true, theme: true, data: true })).join('') + '</section>').join('');
  const jump = gs.map((g, gi) => '<a href="#g' + gi + '"><span>' + esc(T[g.key].name) + '</span><i>' + g.items.length + '</i></a>').join('');
  const dnames = {}; docs.forEach(x => { dnames[x[0]] = D[x[0]].s; });
  const data = { fid: fid, name: f.name, order: f.order, app: f.app, url: f.url, n: f.n, checked: N.meta.checked, themes: T.map(t => t.name), secs: f.secs, buckets: N.buckets.map(b => b.name), docs: dnames };
  const html = '<div class="=wrap page" data-nv="object" data-mode="theme">' +
    '<div class="meta"><span>Приказ Роспотребнадзора № ' + f.order + ', приложение № ' + f.app + '</span><span>' + nq(f.n) + '</span><span>действует с ' + esc(ord.fr || '') + '</span>' + X(f.url, 'Официальный текст листа', 'link ext') + '</div>' +
    (f.full ? '<p class="small muted mw" style="margin-top:10px">По названию формы лист применяют при контроле ' + esc(f.full) + '.</p>' : '') +
    '<p class="howto">Отмечайте вопросы, по которым у вас всё в порядке. Останется список того, чем нужно заняться, — его можно скопировать и передать ответственным. Под каждым вопросом указаны документ и пункт, на которых он основан. Отметки хранятся только в вашем браузере.</p>' +
    (soon.length ? '<p class="warn mw">У документов, на которые ссылается лист, скоро истекает срок действия: ' + soon.map(x => docA(x[0]) + ' — до ' + D[x[0]].to.slice(0, 10)).join('; ') + '. После замены номера пунктов изменятся.</p>' : '') +
    (offd.length ? '<p class="warn mw">Лист ссылается на документ, который уже утратил силу: ' + offd.map(x => { const d = D[x[0]]; return docA(x[0]) + (d.rbi ? ' — вместо него ' + d.rbi.map(j => docA(j)).join(', ') : ''); }).join('; ') + '.</p>' : '') +
    (notyet.length ? '<p class="warn mw">Лист ссылается на документ, который ещё не вступил в силу: ' + notyet.map(x => { const d = D[x[0]]; return docA(x[0]) + ' — ' + (d.fr ? 'вступает в силу ' + esc(d.fr.slice(0, 10)) : 'дата вступления не определена'); }).join('; ') + '.</p>' : '') +
    '<div class="toolbar"><div class="seg" role="group" aria-label="Группировка">' +
    '<button type="button" data-mode="theme" aria-pressed="true">По темам</button><button type="button" data-mode="sec" aria-pressed="false">Как в листе</button>' + (f.per ? '<button type="button" data-mode="per" aria-pressed="false">График работ · ' + f.per + '</button>' : '') + '</div>' +
    '<input class="filter" id="qF" type="search" placeholder="Найти в списке" aria-label="Найти в списке вопросов">' +
    '<button type="button" class="chip" id="onlyBtn" aria-pressed="false">Только неотмеченные</button>' +
    '<button type="button" class="chip" id="copyBtn">Скопировать список</button><button type="button" class="chip" id="dlBtn">Скачать</button></div>' +
    '<div class="progress"><span id="prT">Отмечено 0 из ' + qs.length + '</span><div class="bar" aria-hidden="true"><i id="prB"></i></div><button type="button" class="link small" id="resetBtn" hidden>Сбросить отметки</button></div>' +
    '<p class="note" id="docNote" hidden></p>' +
    '<div class="layout"><div id="qlist">' + list + '</div><aside class="aside" aria-label="Справка по листу">' +
    '<div class="panel" id="jumpP"><p class="panel-t">Разделы</p><div class="jump" id="jump">' + jump + '</div></div>' +
    asideCards(cards) + asideDocs(docs, 'Документы листа') + asideHelp(SVC_FORM[fid]) + '</aside></div>' +
    '<script type="application/json" id="nv-data">' + JSON.stringify(data).replace(/</g, '\\u003c') + '</script></div>';
  // ответы на частые вопросы — только из данных листа
  const top = docs.slice(0, 5).map(x => D[x[0]].s + ' (' + nq(x[1]) + ', ' + vis(D[x[0]]).s + ')').join('; ');
  const tc = f.tc.slice(0, 3).map(x => T[x[0]].name.toLowerCase() + ' — ' + x[1]).join(', ');
  const faq = [
    ['Какой проверочный лист применяют для объекта «' + f.name + '»?', 'Форму из приложения № ' + f.app + ' к приказу Роспотребнадзора № ' + f.order + '. В листе ' + nq(f.n) + ', приказ действует с ' + (ord.fr || '') + '. Инспектор задаёт только вопросы из листа; у каждого вопроса указаны документ и пункт, на которых он основан.'],
    ['На какие документы ссылается этот лист?', 'Чаще всего на следующие: ' + top + '. Статусы документов сверены ' + N.meta.checked + '.'],
    ['Какие темы занимают в листе больше всего вопросов?', 'По числу вопросов: ' + tc + '. Темы присвоены вопросам автоматически, по ключевым словам.']
  ];
  if (f.per) {
    const bc = {}; qs.forEach(q => { if (q[7] >= 0) bc[q[7]] = (bc[q[7]] || 0) + 1; });
    faq.push(['Какие работы на объекте нужно выполнять по графику?', 'В листе ' + f.per + ' ' + pl(f.per, ['требование', 'требования', 'требований']) + ' с прямо названной периодичностью: ' +
      Object.keys(bc).sort((a, b) => a - b).map(k => N.buckets[k].name.toLowerCase() + ' — ' + bc[k]).join(', ') + '. Полный график — в режиме «График работ» на этой странице.']);
  }
  return { html, faq, docs, cards };
}

/* ───────── подборка ───────── */
function compositeBody(id) {
  const c = CO[coIdx[id]];
  const html = '<div class="=wrap page" data-nv="more">' +
    '<p class="howto">Отдельного проверочного листа для этого объекта в приказах № 578 и № 580 нет. Мы собрали вопросы из общих листов, которые к нему применимы. Подборку составила редакция; санитарный врач её ещё не проверял.</p>' +
    (c.extra ? '<p class="note mw">' + esc(c.extra) + (c.xdocs.length ? ' Документы: ' + c.xdocs.map(i => docA(i)).join(', ') + '.' : '') + '</p>' : '') +
    '<div class="layout"><div>' + c.parts.map((p, pi) => {
      const fi = fIdx[p.form], n = p.r[1] - p.r[0] + 1, first = Math.min(n, 6); let rows = '';
      for (let i = p.r[0]; i <= p.r[1]; i++) rows += qRow(fi, i, { theme: true, hidden: i >= p.r[0] + first });
      return '<section class="qsec" id="g' + pi + '"><div class="qsec-h"><h2>' + esc(p.title) + '</h2><span>' + nq(n) + '</span></div>' +
        '<p class="qsec-n">' + esc(p.note) + ' Источник: ' + A('/o/' + p.form, 'лист «' + esc(F[fi].name) + '»', 'link') + '.</p>' +
        '<div data-rows>' + rows + '</div>' + (n > first ? '<button type="button" class="btn btn-s btn-sm showmore" data-more>Показать все ' + n + '</button>' : '') + '</section>';
    }).join('') + '</div><aside class="aside" aria-label="Справка по подборке"><div class="panel"><p class="panel-t">Разделы</p><div class="jump">' +
    c.parts.map((p, pi) => '<a href="#g' + pi + '"><span>' + esc(p.title) + '</span><i>' + (p.r[1] - p.r[0] + 1) + '</i></a>').join('') + '</div></div>' +
    (c.xforms ? '<div class="panel"><p class="panel-t">Смежные объекты</p><div class="dl">' + c.xforms.map(x => A('/o/' + x, '<b>' + esc(F[fIdx[x]].name) + '</b>')).join('') + '</div></div>' : '') +
    asideHelp(SVC_FORM[id]) + '</aside></div></div>';
  const faq = [
    ['Есть ли отдельный проверочный лист для объекта «' + c.name + '»?', 'Нет. В приказах Роспотребнадзора № 578 и № 580 отдельной формы для такого объекта нет. В подборке — ' + nq(c.n) + ' из общих листов: ' + c.parts.map(p => '«' + F[fIdx[p.form]].name + '»').filter((x, i, a) => a.indexOf(x) === i).join(', ') + '.'],
    ['Из чего состоит подборка?', c.parts.map(p => p.title + ' — ' + nq(p.r[1] - p.r[0] + 1)).join('; ') + '.']
  ];
  return { html, faq };
}

/* ───────── тема ───────── */
function themeBlock(tid) {
  const ti = tIdx[tid], t = T[ti];
  const cards = []; C.forEach((c, ci) => { if (c.theme === ti) cards.push(ci); });
  const secs = t.forms.map(x => {
    const fi = x[0], idx = []; Q[F[fi].id].forEach((q, i) => { if (q[3] === ti) idx.push(i); });
    return '<section class="qsec" data-f="' + F[fi].slug + '"><div class="qsec-h"><h2>' + esc(F[fi].name) + '</h2><span>' + nq(idx.length) + '</span></div>' +
      '<div data-rows>' + idx.map((i, k) => qRow(fi, i, { hidden: k >= 3 })).join('') + '</div>' +
      '<div class="chips showmore">' + (idx.length > 3 ? '<button type="button" class="chip" data-more>Показать все ' + idx.length + '</button>' : '') + A('/o/' + F[fi].id, 'Открыть объект', 'chip') + '</div></section>';
  }).join('');
  const html = '<div class="toolbar first"><select class="filter" id="tObj" aria-label="Объект" style="max-width:420px"><option value="">Все объекты</option>' +
    t.forms.map(x => '<option value="' + F[x[0]].slug + '">' + esc(F[x[0]].name) + ' — ' + x[1] + '</option>').join('') + '</select></div>' +
    '<div class="layout"><div id="tList">' + secs + '</div>' +
    '<aside class="aside" aria-label="Справка по теме">' + asideCards(cards) + asideDocs(t.docs, 'Документы темы') + asideHelp(SVC_THEME[tid]) + '</aside></div>' +
    '<p class="note mw" style="margin-top:32px">Тема присвоена вопросам автоматически, по ключевым словам. Распределение ещё не проверено санитарным врачом.</p>';
  const faq = [
    ['Сколько вопросов проверочных листов относится к теме «' + t.name + '»?', nq(t.n) + ' ' + inL(t.forms.length) + ' Роспотребнадзора (приказы № 578 и № 580). Больше всего — в листах: ' + t.forms.slice(0, 3).map(x => '«' + F[x[0]].name + '» (' + x[1] + ')').join(', ') + '.'],
    ['Какие документы устанавливают эти требования?', 'В вопросах темы чаще всего названы: ' + t.docs.slice(0, 5).map(x => D[x[0]].s + ' (' + nq(x[1]) + ', ' + vis(D[x[0]]).s + ')').join('; ') + '. Статусы сверены ' + N.meta.checked + '.']
  ];
  return { html, faq, t };
}

/* ───────── разбор ───────── */
function cardBody(id) {
  const ci = cIdx[id], c = C[ci], t = T[c.theme];
  const known = c.basis.map(b => b[0]).concat(c.docs);
  const basis = c.basis.map(b => {
    const d = D[b[0]]; let what = [b[1], b[2]].filter(Boolean).join(' — ');
    if (what.toLowerCase() === vis(d).s) what = '';
    return '<div class="bas">' + A('/d/' + d.id, esc(d.s), 'bas-n') + (what ? '<span class="bas-p">' + esc(what) + '</span>' : '') + badge(d) + '</div>';
  }).join('');
  const ask = c.ask.map(a => qRow(a[0], a[1], { obj: true, nocard: true })).join('');
  const rel = (c.rel || []).filter(x => cIdx[x] != null).map(x => C[cIdx[x]]);
  const html = '<div class="=wrap page"><div class="layout first"><div class="article">' +
    '<div class="answer-box" style="margin-top:0"><p class="panel-t">Коротко</p><p>' + esc(c.short) + '</p></div>' +
    '<p class="small muted" style="margin-top:16px"><b class="wh">К кому относится.</b> ' + esc(c.scope) + '</p>' +
    (c.warn ? '<p class="warn">' + esc(c.warn) + '</p>' : '') +
    '<section class="blk"><div class="blk-h"><h2>Что требуется</h2><span class="kind norm">Норма</span></div><div class="reqs">' +
    c.norm.map(n => '<div class="req"><p>' + esc(n[0]) + '</p><small class="cite">' + linkDocs(n[1], known) + '</small></div>').join('') + '</div>' +
    (c.note ? '<p class="note">' + esc(c.note) + '</p>' : '') + '</section>' +
    (c.todo.length ? '<section class="blk"><div class="blk-h"><h2>Что сделать</h2><span class="kind prac">Практика</span></div><ol class="steps">' + c.todo.map(x => '<li><span>' + esc(x) + '</span></li>').join('') + '</ol></section>' : '') +
    (c.proof.length ? '<section class="blk"><div class="blk-h"><h2>Чем подтвердить</h2><span class="kind prac">Практика</span></div><ul class="ticks">' + c.proof.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></section>' : '') +
    (ask ? '<section class="blk"><div class="blk-h"><h2>Как об этом спросит инспектор</h2></div><p class="small muted" style="margin-bottom:8px">Вопросы из проверочных листов — дословно.</p>' + ask +
      (c.more ? '<div class="showmore">' + A('/s?q=' + encodeURIComponent(c.more), 'Все вопросы листов по этой теме', 'chip') + '</div>' : '') + '</section>' : '') +
    '<p class="note" style="margin-top:40px">Блок «Что требуется» составлен по формулировкам проверочных листов и текстам документов. Блоки «Что сделать» и «Чем подтвердить» — практика редакции, а не текст документа; санитарный врач их ещё не проверял.</p>' +
    '</div><aside class="aside" aria-label="Основание и связанные материалы">' +
    '<div class="panel"><p class="panel-t">Основание</p>' + basis + '<p class="xs faint" style="margin-top:12px">Статусы сверены ' + N.meta.checked + '. В паспорте документа — срок действия и откуда взят статус.</p></div>' +
    (rel.length ? '<div class="panel"><p class="panel-t">Связанные разборы</p><div class="dl">' + rel.map(r => A('/a/' + r.id, '<b>' + esc(r.title) + '</b>')).join('') + '</div></div>' : '') +
    (c.docs.length ? '<div class="panel"><p class="panel-t">Ещё документы</p><div class="dl">' + c.docs.map(i => dotA(D[i])).join('') + '</div></div>' : '') +
    asideHelp(SVC_THEME[t.id]) + '</aside></div></div>';
  return { html, c, t };
}

/* ───────── документы ───────── */
const ST_F = [['all', 'Все'], ['ok', 'Действует'], ['lim', 'Истекает в течение года'], ['off', 'Не действует'], ['proj', 'Проекты и будущие'], ['other', 'Стандарты и сервисы']];
function stKey(d) { const c = vis(d).c; return c === 'srv' || c === 'vol' ? 'other' : c === 'proj' || c === 'soon' ? 'proj' : c; }
function docRow(d) {
  return A('/d/' + d.id, '<div><div class="doc-s">' + esc(d.s) + '</div><div class="doc-t">' + esc(d.t) + '</div></div><div>' + badge(d) + '</div>' +
    '<div class="doc-q">' + (d.cq ? '<b>' + fmtN(d.cq) + '</b> ' + pl(d.cq, ['вопрос', 'вопроса', 'вопросов']) : '<span class="faint">—</span>') + '</div>', 'doc-row',
    ' data-st="' + stKey(d) + '" data-g="' + esc(d.g) + '"' + (d.rp ? ' data-x="' + esc(d.rp.toLowerCase()) + '"' : ''));
}
function docsBody() {
  const gs = []; D.forEach(d => { if (gs.indexOf(d.g) < 0) gs.push(d.g); });
  const list = D.slice().sort((a, b) => (b.cq || 0) - (a.cq || 0));
  return '<div class="=wrap page" data-nv="docs">' +
    '<div class="toolbar first"><input class="filter" id="dF" type="search" placeholder="Номер или название: 3684, 52-ФЗ, вентиляция" aria-label="Найти документ">' +
    '<select class="filter" id="dG" aria-label="Вид документа" style="max-width:300px"><option value="all">Все виды</option>' + gs.map(g => '<option>' + esc(g) + '</option>').join('') + '</select></div>' +
    '<div class="chips" style="margin-top:12px" id="dSt">' + ST_F.map((x, i) => '<button type="button" class="chip" data-st="' + x[0] + '" aria-pressed="' + (i === 0) + '">' + x[1] + ' <b>' + (x[0] === 'all' ? D.length : D.filter(d => stKey(d) === x[0]).length) + '</b></button>').join('') + '</div>' +
    '<div class="doc-head"><span>Документ</span><span>Статус</span><span>В листах</span></div><div id="dList">' + list.map(docRow).join('') + '</div>' +
    '<p class="empty" id="dNone" hidden>Документов не найдено. Проверьте номер или <a href="#zayavka" class="link">сообщите, какого документа не хватает</a>.</p></div>';
}
const EV_HELP = {
  A: 'В тексте источника есть прямая отметка о статусе или сроке действия.',
  B: 'Открыта действующая редакция; отметки об отмене нет.',
  C: 'Документ назван основанием требований в проверочных листах, которые действуют с октября 2026 года.',
  D: 'Есть отменяющий акт или отметка об утрате силы.',
  E: 'Прямого подтверждения в открытом источнике не найдено. Статус нужно сверить по официальному тексту.',
  P: 'Опубликован текст проекта. Документ не принят.',
  S: 'Это сервис или стандарт вне российского права — статус «действует» к нему не применяется.'
};
/* прямой ответ «действует ли документ» — первой фразой страницы */
function docAnswer(d) {
  const v = vis(d);
  if (d.c === 'ok') return d.s + ' действует' + (d.fr ? ' с ' + d.fr : '') + '.';
  if (d.c === 'lim') return v.c === 'off' ? 'Срок действия ' + d.s + ' истёк ' + d.to.slice(0, 10) + '.' : d.s + ' действует до ' + d.to.slice(0, 10) + (d.fr ? ' (с ' + d.fr + ')' : '') + '.';
  if (d.c === 'off') return d.s + ' не действует' + (d.to ? ' с ' + d.to : '') + '.' + (d.rb ? ' Вместо него: ' + d.rb + '.' : '');
  if (d.c === 'proj') return d.s + ' — проект, документ не принят.';
  if (d.c === 'soon') return d.s + (d.fr ? ' вступает в силу ' + d.fr.slice(0, 10) : ' ещё не вступил в силу') + '.';
  if (d.c === 'srv') return d.s + ' — государственный реестр или сервис; статус «действует» к нему не применяется.';
  return d.s + ': ' + d.st.split(';')[0].toLowerCase() + '.';
}
function docBody(id) {
  const di = dIdx[id], d = D[di];
  const days = d.toi ? daysTo(d.toi) : null;
  const kv = [];
  kv.push(['Вид', esc(d.k)]); kv.push(['Кто принял', esc(d.org)]);
  if (d.d) kv.push(['Дата документа', esc(d.d)]);
  if (d.fr) kv.push(['Действует с', esc(d.fr)]);
  if (d.to) kv.push([d.c === 'off' ? 'Утратил силу' : 'Действует до', esc(d.to) + (d.c === 'lim' && days != null && days >= 0 ? ' <span class="faint">· ' + inDays(days) + '</span>' : '')]);
  if (d.ed) kv.push(['Редакция', esc(d.ed)]);
  if (d.rpi || d.rp) kv.push(['Применяется вместо', (d.rpi ? d.rpi.map(j => docA(j)).join(', ') : esc(d.rp))]);
  if (d.c !== 'off' && (d.rbi || d.rb)) kv.push(['Что дальше', d.rbi ? d.rbi.map(j => docA(j)).join(', ') + (d.rb ? '<br><span class="faint xs">' + esc(d.rb) + '</span>' : '') : esc(d.rb)]);
  kv.push(['Обязательность', esc(d.ob)]);
  const forms = (d.forms || []).map(x => '<tr><td>' + A('/o/' + F[x[0]].id + '?doc=' + d.id, esc(F[x[0]].name), 'dn') + '</td><td class="num">' + nq(x[1]) + '</td></tr>').join('');
  const LIM = 12;
  const pts = (d.pts || []).map((p, pi) => {
    const fs = {}; p[1].forEach(r => { fs[r[0]] = 1; });
    return '<details class="acc"' + (pi === 0 ? ' open' : '') + '><summary><b>' + esc(p[0]) + '</b><span>' + nq(p[1].length) + ' · ' + nl(Object.keys(fs).length) + '</span></summary><div class="acc-b">' +
      p[1].slice(0, LIM).map(r => qRow(r[0], r[1], { obj: true })).join('') +
      (p[1].length > LIM ? '<p class="xs faint" style="padding:10px 0 14px">Показаны первые ' + LIM + ' из ' + p[1].length + '. Остальные — на страницах объектов.</p>' : '') + '</div></details>';
  }).join('');
  const cards = (dCards[di] || []).filter((x, i, a) => a.indexOf(x) === i);
  const html = '<div class="=wrap page">' +
    '<div class="status-box first">' + badge(d) + (d.c === 'lim' && days != null && days >= 0 ? '<span class="small muted">До окончания срока — ' + inDays(days).replace('через ', '') + '</span>' : '') +
    (d.cq ? '<span class="small muted">' + nq(d.cq) + ' ' + inL(d.cf) + '</span>' : '') + '</div>' +
    (d.c === 'off' ? '<p class="replaced mw">Документ не действует' + (d.to ? ' с ' + esc(d.to) : '') + '. ' + (d.rbi ? 'Вместо него: ' + rbHtml(d) : esc(d.rb || 'Сведений о замене в реестре нет.')) + '</p>' : '') +
    '<div class="passport"><div>' +
    '<section><h2>О чём документ</h2><p class="mw" style="margin-top:12px">' + esc(d.about || d.n) + '</p>' +
    (d.about && d.n ? '<p class="mw small muted" style="margin-top:10px">' + esc(d.n) + '</p>' : '') +
    (d.kp && d.kp.length ? '<ul class="ticks" style="margin-top:16px">' + d.kp.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>' : '') + '</section>' +
    (forms ? '<section class="blk"><div class="blk-h"><h2>В каких листах на него ссылаются</h2></div><div class="tbl-wrap"><table class="tbl"><thead><tr><th>Объект</th><th class="num">Вопросов</th></tr></thead><tbody>' + forms + '</tbody></table></div></section>' : '') +
    (pts ? '<section class="blk"><div class="blk-h"><h2>О каких пунктах спрашивают чаще всего</h2></div><p class="small muted" style="margin-bottom:8px">Нажмите на пункт — откроются вопросы проверочных листов, которые на него ссылаются.</p>' + pts + '</section>' : '') +
    (!forms ? '<p class="note mw">В проверочных листах 2026 года этот документ не упоминается.</p>' : '') +
    '</div><aside class="aside" aria-label="Паспорт документа"><div class="panel"><p class="panel-t">Паспорт</p><dl class="kv">' + kv.map(x => '<dt>' + x[0] + '</dt><dd>' + x[1] + '</dd>').join('') + '</dl>' +
    '<div class="btns-col">' + X(d.u, 'Открыть текст документа', 'btn btn-s btn-sm') + (d.off ? X(d.off, 'Официальный источник', 'btn btn-s btn-sm') : '') + '</div></div>' +
    '<div class="panel"><p class="panel-t">Основание статуса</p><p class="small"><b class="wh">' + esc(d.evn) + '</b></p><p class="small muted" style="margin-top:6px">' + esc(d.evt) + '</p>' +
    (d.evu ? '<p class="small" style="margin-top:8px">' + X(d.evu, 'Источник отметки', 'link ext') + '</p>' : '') +
    '<p class="xs faint" style="margin-top:10px">' + esc(EV_HELP[d.evc] || '') + (/сверка \d\d\.\d\d\.\d{4}/.test(d.evt || '') ? '' : ' Сверено ' + N.meta.checked + '.') + '</p></div>' +
    asideCards(cards) + asideHelp() + '</aside></div></div>';
  const faq = [['Действует ли ' + d.s + ' в 2026 году?', docAnswer(d) + ' Основание статуса: ' + d.evn.charAt(0).toLowerCase() + d.evn.slice(1) + '. Сверка — ' + N.meta.checked + '.']];
  if (d.c === 'off') faq.push(['Чем заменён ' + d.s + '?', d.rb ? d.rb + '.' : 'Сведений о замене в реестре навигатора нет.']);
  if (d.cq) faq.push(['В каких проверочных листах ссылаются на ' + d.s + '?', 'В ' + d.cf + ' ' + pl(d.cf, ['листе', 'листах', 'листах']) + ' Роспотребнадзора, всего ' + nq(d.cq) + '. Больше всего — в листах: ' + d.forms.slice(0, 3).map(x => '«' + F[x[0]].name + '» (' + x[1] + ')').join(', ') + '.']);
  return { html, faq, d };
}

/* ───────── календарь и периодичность ───────── */
function calTabs(active) {
  return '<div class="toolbar first"><div class="seg" role="group" aria-label="Вид календаря">' +
    '<a href="{S}kalendar/"' + (active === 'ev' ? ' aria-current="page"' : '') + '>Изменения и сроки</a>' +
    '<a href="{S}periodichnost/"' + (active === 'per' ? ' aria-current="page"' : '') + '>Периодичность работ · ' + N.meta.periodic + '</a></div></div>';
}
function calBody() {
  const fut = N.events.filter(e => e.d > TODAY), past = N.events.filter(e => e.d <= TODAY).reverse();
  function byYear(list) {
    let out = '', y = '';
    list.forEach(e => { const yy = e.d.slice(0, 4); if (yy !== y) { out += (y ? '</div>' : '') + '<div class="year"><p class="year-h">' + yy + '</p>'; y = yy; } out += evRow(e); });
    return out + (y ? '</div>' : '');
  }
  const proj = D.filter(d => d.c === 'proj');
  return '<div class="=wrap page">' + calTabs('ev') +
    '<div class="layout"><div><h2 class="today" style="margin-top:0">Впереди</h2>' + byYear(fut) +
    '<h2 class="today">На ' + fmtDate(TODAY) + ' уже произошло</h2>' + byYear(past) + '</div>' +
    '<aside class="aside" aria-label="Справка"><div class="panel"><p class="panel-t">Готовятся</p><div class="dl">' + proj.map(d => A('/d/' + d.id, '<b><span class="dot proj"></span>' + esc(d.s) + '</b><small>' + esc(d.st.charAt(0).toLowerCase() + d.st.slice(1)) + '</small>')).join('') +
    '</div><p class="xs faint" style="margin-top:12px">Проекты не приняты. Даты в них могут измениться.</p></div>' +
    '<div class="panel"><p class="panel-t">Как пользоваться</p><p class="small muted">Отметьте ближайшие даты в плане пересмотра программы производственного контроля, инструкций и договоров. После замены документа номера пунктов меняются.</p></div>' + asideHelp() + '</aside></div></div>';
}
function perBody() {
  const withPer = F.filter(f => f.per);
  const bs = N.buckets.map(b => ({ name: b.name, items: [] }));
  withPer.forEach(f => { const fi = fIdx[f.id]; Q[f.id].forEach((q, i) => { if (q[7] >= 0) bs[q[7]].items.push([fi, i]); }); });
  return '<div class="=wrap page" data-nv="per">' + calTabs('per') +
    '<div class="toolbar"><select class="filter" id="pObj" aria-label="Объект" style="max-width:420px"><option value="">Все объекты</option>' +
    withPer.map(f => '<option value="' + fIdx[f.id] + '" data-slug="' + f.slug + '">' + esc(f.name) + ' — ' + f.per + '</option>').join('') + '</select>' +
    '<button type="button" class="chip" id="pCopy">Скопировать график</button></div><div id="pList">' +
    bs.filter(b => b.items.length).map(b => '<section class="bucket"><div class="bucket-h"><h2>' + esc(b.name) + '</h2><span>' + nq(b.items.length) + '</span></div><div data-rows>' +
      b.items.map((r, k) => qRow(r[0], r[1], { obj: true, f: true, hidden: k >= 5 })).join('') + '</div>' +
      (b.items.length > 5 ? '<button type="button" class="chip showmore" data-more>Показать все ' + b.items.length + '</button>' : '') + '</section>').join('') + '</div>' +
    '<p class="empty" id="pNone" hidden>Для этого объекта требований с явной периодичностью нет.</p>' +
    '<p class="note mw" style="margin-top:32px">Периодичность найдена в тексте вопросов автоматически. В графике нет требований, где срок задан ссылкой на другой документ или программу производственного контроля.</p></div>';
}

/* ───────── поиск ───────── */
function searchBody() {
  return '<div class="=wrap page" data-nv="search">' +
    '<form class="find first" id="sFind" role="search" autocomplete="off" action="./" method="get"><label class="=sr-only" for="sQ">Запрос</label>' +
    '<input id="sQ" name="q" type="search" placeholder="Вопрос, объект или номер документа" enterkeyhint="search"><button class="btn btn-p" type="submit">Найти</button></form>' +
    '<div id="sRes"><div class="examples" style="margin-top:20px"><span>Попробуйте:</span>' + N.examples.map(x => A('/s?q=' + encodeURIComponent(x), esc(x), 'chip')).join('') + '</div>' +
    '<p class="hint-box mw">Пишите как удобно: «крысы», «медкнижка», «мусорка» — поиск понимает разговорные слова. Номер документа можно вводить частично: «3684». Если назвать объект, вопросы покажем только по нему: «вентиляция в гостинице».</p></div>' +
    '<noscript><p class="note mw">Поиск работает в браузере и требует включённого JavaScript. Без него воспользуйтесь списками: ' + A('/objects', 'объекты', 'link') + ', ' + A('/themes', 'темы', 'link') + ', ' + A('/docs', 'документы', 'link') + '.</p></noscript></div>';
}

/* ───────── о разделе ───────── */
function aboutBody() {
  const ev = {}, names = {}; D.forEach(d => { ev[d.evc] = (ev[d.evc] || 0) + 1; names[d.evc] = d.evn; });
  const order = ['A', 'D', 'C', 'B', 'P', 'S', 'E'];
  let typo = 0;
  F.forEach(f => Q[f.id].forEach(q => { if (q[2] && /class="cite-doc"/.test(citeHtml(q))) typo++; }));
  return '<div class="=wrap page"><div class="article">' +
    '<section class="blk first"><div class="blk-h"><h2>Из чего он собран</h2></div><ul class="ticks">' +
    '<li>' + N.meta.forms + ' проверочных листов Роспотребнадзора из приказов № 578 и № 580 — ' + nq(N.meta.questions) + '. Формулировки взяты из листов дословно.</li>' +
    '<li>В листах ' + fmtN(N.meta.rows) + ' строк. ' + N.meta.headers + ' из них — заголовки групп («Обеспечено ли наличие помещений для:»): они объединены с подпунктами, чтобы каждый вопрос читался целиком. Одна строка в тексте листа повторялась дважды и учтена один раз.</li>' +
    '<li>' + N.meta.docs + ' документов: законы, санитарные правила, постановления, приказы, технические регламенты, методические документы, стандарты.</li>' +
    '<li>' + C.filter(c => !c.ext).length + ' разборов — короткие ответы на частые вопросы — и три подробных материала о проверочных листах, документах к проверке и оценке эффективности обработок.</li>' +
    '<li>' + N.meta.periodic + ' требований с явной периодичностью — основа графика работ.</li></ul></section>' +
    '<section class="blk"><div class="blk-h"><h2>Что сделано автоматически</h2></div><ul class="ticks">' +
    '<li>Темы вопросам присвоены по ключевым словам. Возможны ошибки: распределение ещё не проверено санитарным врачом.</li>' +
    '<li>Ссылки на документы сокращены до вида «п. 14 СП 2.1.4284-26». В ' + N.meta.rawcite + ' вопросах из ' + fmtN(N.meta.questions) + ' ссылка оставлена как в листе. У ' + N.meta.nonorm + ' ' + pl(N.meta.nonorm, ['вопроса', 'вопросов', 'вопросов']) + ' основание в листе не указано: графа пуста или в ней стоит прочерк.</li>' +
    (typo ? '<li>В ' + typo + ' ' + pl(typo, ['вопросе', 'вопросах', 'вопросах']) + ' обозначение документа в листе напечатано с опечаткой или не так, как принято, — например, «СП 2.4.2.4283-2» вместо «СП 2.4.2.4283-26». Текст ссылки оставлен как в листе, рядом указан документ.</li>' : '') +
    '<li>Периодичность найдена в тексте вопросов по словам «ежедневно», «не реже 1 раза в месяц» и похожим.</li></ul></section>' +
    '<section class="blk"><div class="blk-h"><h2>На чём основан статус документа</h2></div><p class="small muted mw" style="margin-bottom:12px">У каждого документа в паспорте указано, откуда взят статус. Сверка — ' + N.meta.checked + '.</p>' +
    '<div class="tbl-wrap"><table class="tbl stack"><thead><tr><th>Основание</th><th>Что это значит</th><th class="num">Документов</th></tr></thead><tbody>' +
    order.filter(k => ev[k]).map(k => '<tr><td>' + esc(names[k]) + '</td><td class="muted">' + esc(EV_HELP[k]) + '</td><td class="num">' + ev[k] + '</td></tr>').join('') +
    '</tbody></table></div></section>' +
    '<section class="blk"><div class="blk-h"><h2>Норма и практика</h2></div><ul class="ticks">' +
    '<li>Метка «Норма» стоит у требований, взятых из проверочных листов и текстов документов, — с пунктом.</li>' +
    '<li>Метка «Практика» стоит у советов редакции: что сделать и чем подтвердить. Это не текст документа.</li></ul></section>' +
    '<section class="blk"><div class="blk-h"><h2>Чего в разделе нет</h2></div><ul class="ticks">' +
    '<li>Экологической отчётности и требований Росприроднадзора.</li>' +
    '<li>Штрафов по каждому вопросу и судебной практики.</li>' +
    '<li>Личного кабинета: отметки на страницах объектов хранятся только в вашем браузере.</li></ul></section>' +
    '<p class="note" style="margin-top:32px">Навигатор — справочный инструмент. Он не заменяет текст документов и консультацию специалиста.</p></div></div>';
}

module.exports = {
  N, Q, F, D, T, C, CO, G, TODAY, esc, fmtN, pl, nq, nl, inL, fmtDate, vis, badge, U, A, docAnswer,
  homeBody, objectsBody, themesBody, answersBody, objectBody, compositeBody, themeBlock, cardBody, docsBody, docBody, calBody, perBody, searchBody, aboutBody,
  SERVICES, SVC_THEME, SVC_FORM
};
