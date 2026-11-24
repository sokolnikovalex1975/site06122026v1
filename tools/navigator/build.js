#!/usr/bin/env node
/* Санитарный навигатор: сборка раздела /normativnaya-baza/ из данных (tools/navigator/data) в оформлении сайта.

   node tools/navigator/build.js [--out dist/navigator-preview]

   Что делает:
   1. Берёт «обвязку» сайта (head, шапка, меню, «Все услуги», заявка, подвал) из normativnaya-baza/index.html.
   2. Собирает страницы раздела: главная, объекты, темы, разборы, документы, календарь, периодичность, поиск, о разделе.
   3. Прежний текст хаба переносит на страницу темы «Насекомые и грызуны» без изменений.
   4. Складывает в папку --out копию сайта (без tools/, server/) с новым разделом — для предпросмотра.
   Исходные страницы сайта в репозитории не меняются. */
'use strict';
const fs = require('fs'), path = require('path');
const R = require('./lib/render');
const { N, Q, F, D, T, C, CO, esc, fmtN, pl, nq } = R;

const REPO = path.join(__dirname, '..', '..');
const argv = process.argv.slice(2);
const HOSTED = argv.indexOf('--hosted') >= 0;   // копия для закрытого предпросмотра: в ссылках явно index.html, хранилище браузера заменено памятью вкладки
const OUT = path.resolve(REPO, argv.indexOf('--out') >= 0 ? argv[argv.indexOf('--out') + 1] : HOSTED ? 'dist/navigator-hosted' : 'dist/navigator-preview');
if (fs.existsSync(OUT)) fs.rmSync(OUT, { recursive: true });
const SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const SEC = 'normativnaya-baza';
const NAME = 'Санитарный навигатор';          // название раздела — в одном месте
const OLD_NAME = 'Нормативная база';
const VER = '20261124nv';
const CHECK_ISO = N.meta.checked.split('.').reverse().join('-');

/* ───────── обвязка сайта ───────── */
const hubSrc = path.join(__dirname, 'src', 'hub-template.html');
const hub = fs.readFileSync(fs.existsSync(hubSrc) ? hubSrc : path.join(REPO, SEC, 'index.html'), 'utf8');
function cut(s, a, b, from) { const i = s.indexOf(a, from || 0); if (i < 0) throw new Error('не найдено: ' + a); const j = s.indexOf(b, i + a.length); if (j < 0) throw new Error('не найдено: ' + b); return [i, j + b.length]; }
const root = s => s.replace(/(["'(]|, |\s)\.\.\//g, (m, a) => a + '{ROOT}');
const iHeadEnd = hub.indexOf('</head>'), iMain = hub.indexOf('<main id="main"'), iVse = hub.indexOf('<section class="s s-vu" id="vse-uslugi"');
if (iHeadEnd < 0 || iMain < 0 || iVse < 0) throw new Error('страница хаба изменилась: не найдены опорные места');
let HEAD = hub.slice(0, iHeadEnd), TOP = hub.slice(iHeadEnd, iMain), TAIL = hub.slice(iVse);
const OLD_MAIN = hub.slice(hub.indexOf('>', iMain) + 1, iVse);                 // содержимое прежнего хаба: первый экран … вопросы
const oldMeta = {
  title: /<title>([^<]*)<\/title>/.exec(hub)[1], desc: /<meta name="description" content="([^"]*)"/.exec(hub)[1],
  ogTitle: /<meta property="og:title" content="([^"]*)"/.exec(hub)[1], ld: JSON.parse(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/.exec(hub)[1])
};
{ // head: свои title/описание/адрес, общий стиль раздела — отдельным файлом, разметка данных — своя
  const [m0] = cut(HEAD, '<title>', '</title>'), m1 = HEAD.indexOf('<link rel="icon"');
  HEAD = HEAD.slice(0, m0) + '{META}\n' + HEAD.slice(m1);
  let pre = '';
  HEAD = HEAD.replace(/<link rel="preload" as="image"[^>]*>\n?/g, m => { pre += m; return ''; });
  HEAD = HEAD.replace('<link rel="preload" href="../fonts/', '{PRELOAD}<link rel="preload" href="../fonts/');
  var HERO_PRELOAD = root(pre);
  const iCss = HEAD.indexOf('<link rel="stylesheet" href="../style.css'), [s0, s1] = cut(HEAD, '<style>', '</style>', iCss);
  var BASE_CSS = HEAD.slice(s0 + 7, s1 - 8);
  HEAD = HEAD.slice(0, s0) + '<link rel="stylesheet" href="../' + SEC + '/nv-base.css?v=' + VER + '">' + HEAD.slice(s1);
  const [l0, l1] = cut(HEAD, '<script type="application/ld+json">', '</script>');
  HEAD = HEAD.slice(0, l0) + '{LD}' + HEAD.slice(l1);
  HEAD = root(HEAD) + '<link rel="stylesheet" href="{ROOT}' + SEC + '/nv.css?v=' + VER + '">\n';
}
TOP = root(TOP.split('<a href="./" aria-current="page">' + OLD_NAME).join('<a href="{SELF}"{CUR}>' + NAME));
TAIL = root(TAIL.split('<a href="./" aria-current="page">' + OLD_NAME).join('<a href="{SELF}"{CUR}>' + NAME))
  .replace('<input type="hidden" name="page" value="' + OLD_NAME + '">', '<input type="hidden" name="page" value="{FORM_PAGE}">')
  .replace("Страница: " + OLD_NAME + " (/" + SEC + "/)", 'Страница: {FORM_PAGE} ({FORM_PATH})');
if (TAIL.indexOf('{FORM_PATH}') < 0 || TOP.indexOf('{SELF}') < 0) throw new Error('обвязка хаба изменилась');
// сценарий «дорожной карты» нужен только странице с прежним текстом хаба
const ROAD_JS = /<script>\/\* Дорожная карта[\s\S]*?<\/script>\n?/.exec(TAIL);
if (ROAD_JS) TAIL = TAIL.replace(ROAD_JS[0], '{ROAD}');
const HERO_JS = root(OLD_MAIN.slice(OLD_MAIN.indexOf('<script id="focal-js">'), OLD_MAIN.indexOf('</script>', OLD_MAIN.indexOf('<script id="hero-in">')) + 9));
const HERO_MEDIA = root(/<div class="d-hero-media">[\s\S]*?<\/div><\/div><\/div>/.exec(OLD_MAIN)[0]);
const REL_SVG = (/<span class="rel-a" aria-hidden="true">(<svg[\s\S]*?<\/svg>)<\/span>/.exec(fs.readFileSync(path.join(REPO, SEC, 'proverochnye-listy', 'index.html'), 'utf8')) || [, ''])[1];

/* ───────── помощники страницы ───────── */
const px = html => html.replace(/class="([^"]*)"/g, (m, c) => 'class="' + c.split(/\s+/).filter(Boolean).map(x => x[0] === '=' ? x.slice(1) : 'nv-' + x).join(' ') + '"');
const plain = s => String(s).replace(/<[^>]+>/g, '').replace(/&nbsp;|\u00a0/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>');
const attr = s => esc(plain(s));
function clip(s, n) { s = plain(s).replace(/\s+/g, ' ').trim(); if (s.length <= n) return s; s = s.slice(0, n - 1); return s.slice(0, s.lastIndexOf(' ')).replace(/[,;:—-]+$/, '') + '…'; }

const TABS = [['', 'Навигатор'], ['obekty/', 'Объекты'], ['temy/', 'Темы'], ['voprosy/', 'Разборы'], ['dokumenty/', 'Документы'], ['kalendar/', 'Календарь']];
function subnav(tab, noSearch) {
  return '<div class="sub"><div class="=wrap sub-in"><nav class="tabs" aria-label="Разделы навигатора">' +
    TABS.map(t => '<a href="{S}' + t[0] + '"' + (t[0] === tab ? ' aria-current="page"' : '') + '>' + t[1] + '</a>').join('') + '</nav>' +
    (noSearch ? '' : '<form class="top-search" action="{S}poisk/" method="get" role="search"><label class="=sr-only" for="nvTopQ">Поиск по навигатору</label>' +
      '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="4.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10.5 10.5 14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' +
      '<input id="nvTopQ" name="q" type="search" placeholder="Вопрос, объект или номер документа" enterkeyhint="search"></form>') + '</div></div>';
}
function crumbsHtml(items, withData) {
  return '<nav class="=f-crumbs" aria-label="Навигационная цепочка"' + (withData ? ' data-h' : '') + '>' + items.map((it, i) =>
    (i ? '<span aria-hidden="true">→</span>' : '') + (i < items.length - 1 ? '<a href="' + it[1] + '">' + esc(it[0]) + '</a>' : '<span aria-current="page">' + esc(it[0]) + '</span>')).join('') + '</nav>';
}
function textHero(p) {
  return '<section class="hero" id="hero"><div class="=wrap">' + crumbsHtml(p.crumbs) +
    (p.eyebrow ? '<p class="eyebrow">' + p.eyebrow + '</p>' : '') + '<h1>' + p.h1 + '</h1>' +
    (p.lead ? '<p class="lead">' + p.lead + '</p>' : '') + (p.after || '') + '</div></section>';
}
function faqSection(list, title) {
  if (!list || !list.length) return '';
  const col = (items, off) => '<div class="faq-col" data-group="faq">' + items.map((x, i) => {
    const k = off + i + 1;
    return '<div class="card qa"><button aria-expanded="false" aria-controls="a' + k + '" id="q' + k + '"><span>' + esc(x[0]) + '</span><span class="pm"></span></button><div class="ans" id="a' + k + '" role="region" aria-labelledby="q' + k + '"><div><p>' + esc(x[1]) + '</p></div></div></div>';
  }).join('') + '</div>';
  const h = Math.ceil(list.length / 2);
  return '<section class="s" id="voprosy"><div class="wrap"><div class="head"><div class="eyebrow" data-eyebrow>Вопросы</div><h2 data-split>' + (title || 'Коротко <em>о главном</em>') + '</h2></div>' +
    '<div class="faq">' + col(list.slice(0, h), 0) + (list.length > h ? col(list.slice(h), h) : '') + '</div></div></section>';
}
/* «Смотрите также» — перед вопросами; ссылки только на страницы навигатора */
function relSection(items) {
  if (!items || !items.length) return '';
  return '<section class="s s-rel" id="smotrite-takzhe"><div class="wrap"><div class="head"><div class="eyebrow" data-eyebrow>Смотрите также</div><h2 data-split>Связанные <em>страницы навигатора</em></h2></div>' +
    '<div class="rel-grid" data-group="cards">' + items.slice(0, 4).map(x => '<a class="card rel-card" href="' + x.href + '"><span class="rel-k">' + esc(x.k) + '</span><span class="rel-t">' + esc(x.t) + '</span><span class="rel-d">' + esc(x.d) + '</span><span class="rel-a" aria-hidden="true">' + REL_SVG + '</span></a>').join('') +
    '</div></div></section>';
}
const relOf = {
  obj: f => ({ href: R.U((f.parts ? '/c/' : '/o/') + f.id), k: f.parts ? 'Подборка' : 'Объект', t: f.name, d: f.parts ? 'Вопросы из общих листов, применимые к объекту: ' + nq(f.n) + '.' : 'Проверочный лист: ' + nq(f.n) + ' с документом и пунктом.' }),
  theme: t => ({ href: R.U('/t/' + t.id), k: 'Тема', t: t.name, d: t.hint + '. ' + nq(t.n) + ' по всем объектам.' }),
  card: c => ({ href: R.U('/a/' + c.id), k: 'Разбор', t: c.title, d: clip(c.short, 130) }),
  doc: d => ({ href: R.U('/d/' + d.id), k: 'Документ', t: d.s, d: clip(R.vis(d).t + '. ' + d.t, 130) }),
  page: (p, k, t, d) => ({ href: R.U(p), k, t, d })
};

const ORG = { '@type': 'Organization', '@id': SITE + '/#org', name: 'ПЕСТКОНТРОЛЬ Центр', legalName: 'ООО «Центр дезинфекционных услуг»', url: SITE + '/', telephone: '+7 495 104-35-70', email: 'b2b@pestcontrol-center.ru' };
function ld(p, url) {
  const g = [ORG, { '@type': 'BreadcrumbList', itemListElement: p.ldCrumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c[0], item: SITE + '/' + c[1] })) },
    Object.assign({ '@type': p.ldType || 'WebPage', '@id': url + '#webpage', url, name: plain(p.h1), headline: plain(p.h1), description: p.desc, inLanguage: 'ru', dateModified: CHECK_ISO,
      isPartOf: { '@type': 'WebSite', '@id': SITE + '/#website', url: SITE + '/', name: 'ПЕСТКОНТРОЛЬ Центр' }, publisher: { '@id': SITE + '/#org' } }, p.ldExtra || {})];
  if (p.faq && p.faq.length) g.push({ '@type': 'FAQPage', '@id': url + '#faq', mainEntity: p.faq.map(x => ({ '@type': 'Question', name: x[0], acceptedAnswer: { '@type': 'Answer', text: x[1] } })) });
  return '<script type="application/ld+json">' + JSON.stringify({ '@context': 'https://schema.org', '@graph': g }).replace(/</g, '\\u003c') + '</script>';
}
function metaBlock(p, url, ogType) {
  return '<title>' + esc(p.title) + '</title>\n<meta name="description" content="' + attr(p.desc) + '">\n<link rel="canonical" href="' + url + '">\n<meta name="theme-color" content="#000000">\n' +
    '<meta property="og:type" content="' + (ogType || 'article') + '">\n<meta property="og:locale" content="ru_RU">\n<meta property="og:site_name" content="ПЕСТКОНТРОЛЬ Центр">\n<meta property="og:url" content="' + url + '">\n' +
    '<meta property="og:title" content="' + attr(p.ogTitle || p.h1) + '">\n<meta property="og:description" content="' + attr(p.desc) + '">\n<meta property="og:image" content="' + SITE + '/img/nb-og.jpg">\n' +
    '<meta property="og:image:type" content="image/jpeg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="' + attr(p.ogTitle || p.h1) + '">\n<meta name="twitter:card" content="summary_large_image">';
}

/* ───────── запись страницы ───────── */
const pages = [];      // список для отчёта и будущей карты сайта
function write(rel, html) { const f = path.join(OUT, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, html); }
/* p: path ('' — главная раздела, 'obekty/', 'obekty/gostinitsa/'), title, desc, h1, crumbs [[name, sectionPath]], main (готовая разметка main), faq, index (false — закрыть от индексации в рабочей версии) */
function emit(p) {
  const depth = p.path.split('/').filter(Boolean).length;                   // 0 — главная раздела
  const S = depth ? '../'.repeat(depth) : './', ROOT = '../'.repeat(depth + 1);
  const url = SITE + '/' + SEC + '/' + p.path;
  p.ldCrumbs = [['Главная', '']].concat(p.crumbs.map(c => [c[0], SEC + '/' + c[1]]));
  let head = HEAD.replace('{META}', () => p.metaRaw || metaBlock(p, url, p.ogType)).replace('{LD}', () => p.ldRaw || ld(p, url)).replace('{PRELOAD}', p.photo ? HERO_PRELOAD : '');
  let html = head + TOP.split('{SELF}').join(depth ? '{ROOT}' + SEC + '/' : './').split('{CUR}').join(depth ? '' : ' aria-current="page"') +
    '<main id="main" tabindex="-1">\n' + p.main + '\n' +
    TAIL.split('{SELF}').join(depth ? '{ROOT}' + SEC + '/' : './').split('{CUR}').join(depth ? '' : ' aria-current="page"')
      .split('{FORM_PAGE}').join(esc(NAME + (p.formLabel ? ': ' + p.formLabel : ''))).replace('{FORM_PATH}', '/' + SEC + '/' + p.path).replace('{ROAD}', p.road ? ROAD_JS[0] : '');
  html = html.replace('</body>', '<script src="{ROOT}' + SEC + '/nv.js?v=' + VER + '" defer></script>\n' + (p.scripts || '') + '</body>');
  html = html.split('{S}').join(S).split('{ROOT}').join(ROOT);
  write(path.join(SEC, p.path, 'index.html'), html);
  pages.push({ path: '/' + SEC + '/' + p.path, title: p.title, h1: plain(p.h1), desc: p.desc || '', index: p.index !== false, bytes: Buffer.byteLength(html) });
}
/* обычная страница навигатора: текстовый первый экран + полоса разделов + содержимое */
function navPage(p) {
  const crumbsFull = [['Главная', '{ROOT}'], [NAME, '{S}']].concat(p.crumbs.map(c => [c[0], '{S}' + c[1]]));
  p.crumbs = [[NAME, '']].concat(p.crumbs);
  p.main = '<div class="nv">' + px(textHero({ crumbs: crumbsFull, eyebrow: p.eyebrow, h1: p.h1, lead: p.lead, after: p.after }) + subnav(p.tab, p.noSearch) + p.body) + '</div>\n' + relSection(p.rel) + faqSection(p.faq, p.faqTitle);
  emit(p);
}

/* ═════════ страницы ═════════ */
const yr = '2026';
const em = (a, b) => esc(a) + ' <em>' + esc(b) + '</em>';

/* — главная раздела: фото первого экрана остаётся, под ним — навигатор — */
(function home() {
  const h1 = '<span class="ln"><span>Санитарные требования ' + yr + ':</span></span> <span class="ln"><span>что обязан выполнять</span></span> <span class="ln"><span><em>ваш объект</em></span></span>';
  const lead = 'Навигатор показывает, что требует санитарное законодательство от организации: ' + N.meta.forms + ' проверочных листов Роспотребнадзора, ' + nq(N.meta.questions) + ' инспектора и ' + N.meta.docs + ' документов со статусом и сроком действия. Выберите объект, тему или документ — увидите требование, пункт и периодичность.';
  const p = {
    path: '', title: 'Санитарные требования ' + yr + ' к объектам: СанПиН, проверочные листы, сроки — ' + NAME,
    desc: 'Справочная система по санитарному законодательству: ' + N.meta.forms + ' проверочных листов Роспотребнадзора, ' + plain(nq(N.meta.questions)) + ' инспектора, ' + N.meta.docs + ' документов со статусом. Требования по объекту, теме, документу и сроку.',
    h1, ogTitle: 'Санитарные требования ' + yr + ': что обязан выполнять ваш объект', ogType: 'website', crumbs: [[NAME, '']], photo: true, formLabel: '',
    faq: [
      ['Какие санитарные правила действуют в ' + yr + ' году?', D.filter(d => d.g === 'Санитарные правила' && (d.c === 'ok' || d.c === 'lim')).slice(0, 9).map(d => d.s + ' — ' + R.vis(d).s).join('; ') + '. Статусы сверены ' + N.meta.checked + '; полный перечень со сроками — в разделе «Документы».'],
      ['По каким проверочным листам Роспотребнадзор проверяет организации?', 'По формам из приказов Роспотребнадзора № 578 (' + F.filter(f => f.order === '578').length + ' ' + pl(F.filter(f => f.order === '578').length, ['лист', 'листа', 'листов']) + ', действует с ' + D[R.N.docs.findIndex(d => d.id === 'prikaz578')].fr + ') и № 580 (' + F.filter(f => f.order === '580').length + ' листов, действует с ' + D[R.N.docs.findIndex(d => d.id === 'prikaz580')].fr + '). Всего в них ' + nq(N.meta.questions) + '; у каждого вопроса указаны документ и пункт.'],
      ['Как узнать, действует ли документ?', 'Откройте раздел «Документы» и введите номер, даже старый. В паспорте документа указаны статус, срок действия, чем документ заменён и на чём основан статус — со ссылкой на источник.'],
      ['Откуда взяты данные и можно ли на них ссылаться?', 'Вопросы взяты из проверочных листов дословно, статусы документов сверены по открытым правовым базам ' + N.meta.checked + '. Темы и периодичность определены автоматически. Навигатор — справочный инструмент: он не заменяет официальный текст документа.']
    ]
  };
  const hero = '<section class="d-hero nb-hero nb-hub-hero nv-home-hero" id="hero"><div class="wrap"><div class="d-hero-copy">' +
    '<nav class="f-crumbs" aria-label="Навигационная цепочка" data-h><a href="{ROOT}">Главная</a><span aria-hidden="true">→</span><span aria-current="page">' + NAME + '</span></nav>' +
    '<div class="eyebrow">' + NAME + ' · справочная система для организаций</div><h1>' + h1 + '</h1>' + HERO_MEDIA +
    '<p class="lead" data-h>' + lead + '</p>' +
    '<div class="d-btns nv nv-herofind" data-h><form class="nv-find" role="search" action="{S}poisk/" method="get" autocomplete="off"><label class="sr-only" for="homeQ">Что вы ищете</label>' +
    '<input id="homeQ" name="q" type="search" placeholder="Например: вентиляция в гостинице или СанПиН 2.1.3684-21" enterkeyhint="search"><button class="nv-btn nv-btn-p" type="submit">Найти</button></form></div>' +
    '<p class="nb-byline p-hero-note" data-h>Статусы документов сверены ' + N.meta.checked + ' · формулировки вопросов — дословно из проверочных листов · <a href="{S}o-razdele/">как устроен раздел</a></p></div>' +
    '<nav class="p-toc nb-toc" aria-label="Разделы навигатора" data-h><a href="{S}obekty/">Объекты</a><a href="{S}temy/">Темы</a><a href="{S}voprosy/">Разборы</a><a href="{S}dokumenty/">Документы</a><a href="{S}kalendar/">Календарь</a><a href="{S}periodichnost/">Периодичность</a></nav></div></section>\n' + HERO_JS;
  p.main = hero + '\n<div class="nv">' + px(R.homeBody()) + '</div>\n' + faqSection(p.faq, 'Вопросы <em>о санитарных требованиях</em>');
  emit(p);
})();

/* — объекты — */
navPage({
  path: 'obekty/', tab: 'obekty/', title: 'Санитарные требования по видам объектов: ' + F.length + ' проверочных листов и ' + CO.length + ' подборки — ' + NAME,
  desc: 'Выберите объект — гостиницу, кафе, магазин, клинику, школу — и откройте вопросы, по которым его проверяет Роспотребнадзор: с документом, пунктом и периодичностью.',
  h1: em('Санитарные требования', 'по видам объектов'), eyebrow: 'Объекты', crumbs: [['Объекты', 'obekty/']], formLabel: 'Объекты',
  lead: 'Выберите объект — откроется список вопросов, по которым его проверяет Роспотребнадзор: ' + F.length + ' проверочных листов и ' + CO.length + ' подборки редакции. Вопросы можно отмечать и скопировать.',
  body: R.objectsBody()
});
const objName = n => n.indexOf(':') >= 0 ? n.replace(':', ' (') + ')' : n;
F.forEach(f => {
  const o = R.objectBody(f.id), nm = objName(f.name), ord = D[N.docs.findIndex(d => d.id === 'prikaz' + f.order)];
  const rel = [];
  o.cards.slice(0, 2).forEach(ci => rel.push(relOf.card(C[ci])));
  f.tc.slice(0, 2).forEach(x => rel.push(relOf.theme(T[x[0]])));
  if (f.per) rel.push(relOf.page('/k/per?o=' + f.id, 'График', 'Периодичность работ', 'Требования листа с прямо названной периодичностью: ' + f.per + '.'));
  navPage({
    path: 'obekty/' + f.slug + '/', tab: 'obekty/', title: nm + ': санитарные требования и проверочный лист Роспотребнадзора ' + yr,
    desc: nm + ': ' + plain(nq(f.n)) + ' проверочного листа Роспотребнадзора (приказ № ' + f.order + ', приложение № ' + f.app + ') — дословно, с документом, пунктом и периодичностью. Сверено ' + N.meta.checked + '.',
    h1: esc(nm) + ': <em>санитарные требования и вопросы проверочного листа</em>', eyebrow: 'Объект', crumbs: [['Объекты', 'obekty/'], [f.name, 'obekty/' + f.slug + '/']], formLabel: f.name,
    lead: 'Объект «' + esc(f.name) + '» Роспотребнадзор проверяет по форме из приложения № ' + f.app + ' к приказу № ' + f.order + ': в листе ' + nq(f.n) + ', приказ действует с ' + esc(ord.fr || '') + '. Ниже — все вопросы дословно, с документом и пунктом. Статусы документов сверены ' + N.meta.checked + '.',
    body: o.html, faq: o.faq, faqTitle: 'Вопросы <em>о проверочном листе</em>', rel
  });
});
CO.forEach(c => {
  const o = R.compositeBody(c.id);
  navPage({
    path: 'obekty/' + c.slug + '/', tab: 'obekty/', title: c.name + ': санитарные требования ' + yr + ' — подборка вопросов проверочных листов',
    desc: c.name + ': отдельного проверочного листа нет. Подборка — ' + plain(nq(c.n)) + ' из общих листов Роспотребнадзора, с документом и пунктом. Сверено ' + N.meta.checked + '.',
    h1: esc(c.name) + ': <em>санитарные требования и вопросы инспектора</em>', eyebrow: 'Объект · подборка редакции', crumbs: [['Объекты', 'obekty/'], [c.name, 'obekty/' + c.slug + '/']], formLabel: c.name,
    lead: 'Для объекта «' + esc(c.name) + '» отдельного проверочного листа в приказах Роспотребнадзора № 578 и № 580 нет. В подборке — ' + nq(c.n) + ' из общих листов, которые к нему применимы.',
    body: o.html, faq: o.faq, faqTitle: 'Вопросы <em>о подборке</em>',
    rel: c.parts.map(p => F[R.N.forms.findIndex(f => f.id === p.form)]).filter((x, i, a) => a.indexOf(x) === i).slice(0, 4).map(relOf.obj)
  });
});

/* — темы — */
navPage({
  path: 'temy/', tab: 'temy/', title: 'Санитарные требования по темам: вентиляция, вода, отходы, персонал — ' + NAME,
  desc: T.length + ' тем санитарного законодательства: уборка и дезинфекция, отходы, вода, вентиляция, персонал, производственный контроль. По каждой — вопросы проверочных листов по всем объектам.',
  h1: em('Санитарные требования', 'по темам'), eyebrow: 'Темы', crumbs: [['Темы', 'temy/']], formLabel: 'Темы',
  lead: 'Одна тема — требования по всем объектам сразу: ' + T.length + ' тем, ' + nq(N.meta.questions) + ' проверочных листов. Число показывает, сколько вопросов относится к теме.',
  body: R.themesBody()
});
T.forEach(t => {
  if (t.id === 'vrediteli') return;                    // эта тема получает прежний текст хаба — ниже
  const b = R.themeBlock(t.id);
  const rel = C.filter(c => !c.ext && T[c.theme] === t).slice(0, 2).map(relOf.card).concat(t.forms.slice(0, 2).map(x => relOf.obj(F[x[0]])));
  navPage({
    path: 'temy/' + t.slug + '/', tab: 'temy/', title: t.name + ': санитарные требования ' + yr + ' по СанПиН и проверочным листам',
    desc: t.name + ': ' + plain(nq(t.n)) + ' проверочных листов Роспотребнадзора по ' + t.forms.length + ' видам объектов — с документом и пунктом. ' + t.hint + '.',
    h1: esc(t.name) + ': <em>санитарные требования ' + yr + '</em>', eyebrow: 'Тема', crumbs: [['Темы', 'temy/'], [t.short, 'temy/' + t.slug + '/']], formLabel: t.name,
    lead: esc(t.hint) + '. К теме относится ' + nq(t.n) + ' ' + R.inL(t.forms.length) + ' Роспотребнадзора. Ниже — вопросы по каждому объекту дословно, с документом и пунктом.',
    body: '<div class="=wrap page" data-nv="theme">' + b.html + '</div>', faq: b.faq, faqTitle: 'Вопросы <em>по теме</em>', rel
  });
});

/* — тема «Насекомые и грызуны»: прежний текст хаба без изменений + вопросы листов — */
(function pests() {
  const t = T[R.N.themes.findIndex(x => x.id === 'vrediteli')], b = R.themeBlock('vrediteli');
  const pth = 'temy/' + t.slug + '/', url = SITE + '/' + SEC + '/' + pth;
  let m = root(OLD_MAIN);
  const cr = /<nav class="f-crumbs"[\s\S]*?<\/nav>/.exec(m)[0];
  m = m.replace(cr, px(crumbsHtml([['Главная', '{ROOT}'], [NAME, '{S}'], ['Темы', '{S}temy/'], [t.name, '']], true)));
  m = m.replace('<div class="eyebrow">' + OLD_NAME + ' · ', '<div class="eyebrow">' + NAME + ' · тема · ');
  const iHeroEnd = m.indexOf('</script>', m.indexOf('<script id="hero-in">')) + 9;
  m = m.slice(0, iHeroEnd) + '\n<div class="nv">' + px(subnav('temy/')) + '</div>' + m.slice(iHeroEnd);
  const block = '<section class="s" id="voprosy-listov"><div class="wrap"><div class="head"><div class="eyebrow" data-eyebrow>Проверочные листы</div><h2 data-split>Что спросит инспектор <em>о насекомых и грызунах</em></h2></div>' +
    '<div class="nv nv-inset"><p class="nv-lead">К теме относится ' + nq(t.n) + ' ' + R.inL(t.forms.length) + ' Роспотребнадзора. Вопросы приведены дословно, с документом и пунктом; подбор по теме сделан автоматически.</p>' +
    px('<div class="page0" data-nv="theme">' + b.html + '</div>') + '</div></div></section>\n';
  const iAv = m.indexOf('<section class="s" id="avtor">'); if (iAv < 0) throw new Error('в прежнем хабе нет блока автора');
  m = m.slice(0, iAv) + block + m.slice(iAv);
  m = m.replace('<a href="#voprosy">Вопросы</a></nav>', '<a href="#voprosy-listov">Вопросы листов</a><a href="#voprosy">Вопросы</a></nav>');
  // разметка данных прежней страницы — с новым адресом и цепочкой
  const g = JSON.parse(JSON.stringify(oldMeta.ld)), old = SITE + '/' + SEC + '/';
  const crumbs = [['Главная', ''], [NAME, SEC + '/'], ['Темы', SEC + '/temy/'], [t.name, SEC + '/' + pth]];
  g['@graph'].forEach(n => {
    if (n['@type'] === 'BreadcrumbList') n.itemListElement = crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c[0], item: SITE + '/' + c[1] }));
    ['@id', 'url', 'mainEntityOfPage'].forEach(k => { if (typeof n[k] === 'string' && (n[k] === old || n[k].indexOf(old + '#') === 0)) n[k] = url + n[k].slice(old.length); });
  });
  const p = { title: oldMeta.title, desc: oldMeta.desc, h1: oldMeta.ogTitle, ogTitle: oldMeta.ogTitle };
  emit({
    path: pth, title: oldMeta.title, desc: oldMeta.desc, h1: oldMeta.ogTitle, crumbs: [[NAME, ''], ['Темы', 'temy/'], [t.name, pth]], photo: true, road: true, formLabel: t.name,
    metaRaw: metaBlock(p, url), ldRaw: '<script type="application/ld+json">' + JSON.stringify(g).replace(/</g, '\\u003c') + '</script>', main: m
  });
})();

/* — разборы — */
const EXTRA = [
  { path: 'proverochnye-listy/', tag: 'Проверочные листы', title: 'Проверочные листы Роспотребнадзора 2026: вопросы о насекомых и грызунах', text: 'Какие вопросы о дезинсекции и дератизации есть в новых листах и чем на них ответить.' },
  { path: 'dokumenty-dlya-rospotrebnadzora/', tag: 'Документы', title: 'Документы по дезинсекции и дератизации для Роспотребнадзора', text: 'Что должно лежать в папке объекта к проверке: договор, акты, журнал, программа.' },
  { path: 'effektivnost-deratizatsii-i-dezinsektsii/', tag: 'Насекомые и грызуны', title: 'Эффективность дератизации и дезинсекции', text: 'Как оценивают результат обработок и какие показатели записывают в документы.' }
];
navPage({
  path: 'voprosy/', tab: 'voprosy/', title: 'Разборы санитарных требований: короткие ответы с пунктом документа — ' + NAME,
  desc: 'Короткие ответы на частые вопросы о санитарных требованиях: вентиляция, отходы, персонал, производственный контроль. В каждом — что требуется, по какому пункту, что сделать и чем подтвердить.',
  h1: em('Разборы санитарных требований:', 'короткие ответы'), eyebrow: 'Разборы', crumbs: [['Разборы', 'voprosy/']], formLabel: 'Разборы',
  lead: 'Короткие ответы на частые вопросы. В каждом разборе: что требуется и по какому пункту, что сделать, чем подтвердить и как об этом спросит инспектор.',
  body: R.answersBody(EXTRA)
});
C.filter(c => !c.ext).forEach(c => {
  const o = R.cardBody(c.id);
  const rel = (c.rel || []).map(x => C.find(y => y.id === x)).filter(Boolean).slice(0, 2).map(relOf.card).concat([relOf.theme(o.t)]).concat(c.basis.slice(0, 1).map(b => relOf.doc(D[b[0]])));
  navPage({
    path: 'voprosy/' + c.slug + '/', tab: 'voprosy/', title: c.title + ' — разбор по СанПиН ' + yr, desc: clip(c.short, 200),
    h1: esc(c.title), eyebrow: 'Разбор · ' + esc(o.t.short), crumbs: [['Разборы', 'voprosy/'], [c.title, 'voprosy/' + c.slug + '/']], formLabel: c.title, ldType: 'Article',
    body: o.html, rel, faq: null,
    ldExtra: { mainEntity: { '@type': 'Question', name: c.title, acceptedAnswer: { '@type': 'Answer', text: c.short } } }
  });
});

/* — документы — */
navPage({
  path: 'dokumenty/', tab: 'dokumenty/', title: 'Санитарные правила и нормативные документы ' + yr + ': ' + D.length + ' документов со статусом — ' + NAME,
  desc: 'Реестр санитарного законодательства: ' + D.length + ' документов — СанПиН, СП, законы, приказы, техрегламенты. У каждого статус, срок действия, чем заменён и в каких проверочных листах назван.',
  h1: em('Санитарные правила и документы ' + yr + ':', 'статус и срок действия'), eyebrow: 'Документы', crumbs: [['Документы', 'dokumenty/']], formLabel: 'Документы',
  lead: 'В реестре ' + D.length + ' документов. У каждого — статус, срок действия, основание статуса и список проверочных листов, которые на него ссылаются. Введите номер, даже старый: покажем, чем документ заменён.',
  body: R.docsBody()
});
D.forEach(d => {
  const o = R.docBody(d.id), v = R.vis(d);
  const tail = d.c === 'off' ? 'утратил силу — чем заменён' : d.c === 'proj' ? 'проект — что известно' : d.c === 'srv' ? 'что это и как пользоваться' : 'действует ли в ' + yr + ' году, статус и срок';
  const rel = (d.rbi || []).concat(d.rpi || []).slice(0, 2).map(j => relOf.doc(D[j])).concat((d.forms || []).slice(0, 2).map(x => relOf.obj(F[x[0]])));
  navPage({
    path: 'dokumenty/' + d.slug + '/', tab: 'dokumenty/', title: d.s + ': ' + tail, desc: clip(R.docAnswer(d) + ' ' + d.t + '. Паспорт документа: статус, срок действия, основание статуса' + (d.cq ? ', вопросы проверочных листов' : '') + '.', 220),
    h1: '<span class="nw">' + esc(d.s) + ':</span> <em>' + (d.c === 'off' ? 'не действует' : d.c === 'proj' ? 'проект' : d.c === 'srv' ? 'сервис' : 'статус на ' + yr + ' год') + '</em>', eyebrow: esc(d.k), crumbs: [['Документы', 'dokumenty/'], [d.s, 'dokumenty/' + d.slug + '/']], formLabel: d.s,
    lead: '<b>' + esc(R.docAnswer(d)) + '</b> ' + esc(d.t) + '. Сверено ' + N.meta.checked + '.', body: o.html, faq: o.faq, faqTitle: 'Вопросы <em>о документе</em>', rel,
    index: !!d.cq || !!(d.rbi && d.rbi.some(j => D[j].cq))        // в рабочей версии сначала открываем документы, названные в листах, и их предшественников
  });
});

/* — календарь, периодичность, поиск, о разделе — */
navPage({
  path: 'kalendar/', tab: 'kalendar/', title: 'Календарь изменений санитарного законодательства ' + yr + '–2027 — ' + NAME,
  desc: 'Когда санитарные правила вступают в силу, заменяются и истекают: даты по ' + N.events.length + ' событиям с ссылкой на паспорт документа. Сверено ' + N.meta.checked + '.',
  h1: em('Календарь изменений', 'санитарного законодательства'), eyebrow: 'Календарь', crumbs: [['Календарь', 'kalendar/']], formLabel: 'Календарь',
  lead: 'Когда документы вступают в силу, заменяются и истекают. Даты взяты из паспортов документов — нажмите на название, чтобы увидеть основание.',
  body: R.calBody()
});
navPage({
  path: 'periodichnost/', tab: 'kalendar/', title: 'Периодичность санитарных работ по СанПиН: что делать каждый день, месяц и год — ' + NAME,
  desc: N.meta.periodic + ' требований проверочных листов, в которых прямо названа периодичность: ежедневно, раз в месяц, раз в год. Выберите объект и получите график обязательных работ.',
  h1: em('Периодичность санитарных работ:', 'что и как часто'), eyebrow: 'Календарь', crumbs: [['Календарь', 'kalendar/'], ['Периодичность работ', 'periodichnost/']], formLabel: 'Периодичность работ',
  lead: 'В проверочных листах ' + N.meta.periodic + ' требований, в которых прямо названа периодичность: ежедневно, раз в месяц, раз в год. Выберите объект — получите готовый график обязательных работ.',
  body: R.perBody()
});
navPage({
  path: 'poisk/', tab: '-', noSearch: true, title: 'Поиск по санитарным требованиям — ' + NAME, desc: 'Поиск по вопросам проверочных листов, документам, объектам и разборам санитарного навигатора.',
  h1: 'Поиск <em>по навигатору</em>', eyebrow: 'Поиск', crumbs: [['Поиск', 'poisk/']], formLabel: 'Поиск', body: R.searchBody(), index: false,
  scripts: '<script src="{ROOT}' + SEC + '/nv-search-data.js?v=' + VER + '" defer></script>\n<script src="{ROOT}' + SEC + '/nv-search.js?v=' + VER + '" defer></script>\n'
});
navPage({
  path: 'o-razdele/', tab: '-', title: 'Как устроен ' + NAME.toLowerCase() + ': источники и метод', desc: 'Из чего собран санитарный навигатор, что сделано автоматически, на чём основан статус документа и чем отличаются метки «Норма» и «Практика».',
  h1: em('Как устроен', NAME.toLowerCase()), eyebrow: 'О разделе', crumbs: [['Как устроен раздел', 'o-razdele/']], formLabel: 'О разделе',
  lead: 'Навигатор отвечает на три вопроса: что требуется от объекта, на каком документе это основано и действует ли этот документ сегодня. Статусы документов сверены ' + N.meta.checked + '.',
  body: R.aboutBody()
});

/* ═════════ файлы раздела ═════════ */
write(path.join(SEC, 'nv-base.css'), BASE_CSS);
write(path.join(SEC, 'nv.css'), require('./lib/css').build());
write(path.join(SEC, 'nv.js'), fs.readFileSync(path.join(__dirname, 'src', 'nv.js'), 'utf8'));
write(path.join(SEC, 'nv-search.js'), fs.readFileSync(path.join(__dirname, 'src', 'nv-search.js'), 'utf8'));
{ // данные для поиска: только то, что нужно странице поиска
  const v = d => R.vis(d);
  const data = {
    today: R.TODAY, checked: N.meta.checked, syn: N.syn, examples: N.examples,
    F: F.map(f => ({ id: f.id, name: f.name, hint: f.hint, n: f.n, u: 'obekty/' + f.slug + '/' })),
    CO: CO.map(c => ({ id: c.id, name: c.name, u: 'obekty/' + c.slug + '/' })),
    T: T.map(t => ({ name: t.name, short: t.short, hint: t.hint, n: t.n, u: 'temy/' + t.slug + '/' })),
    C: C.map(c => ({ title: c.title, short: c.short, hay: c.scope + ' ' + c.norm.map(n => n[0]).join(' ') + ' ' + (c.more || ''), u: c.ext || 'voprosy/' + c.slug + '/' })),
    D: D.map(d => ({ s: d.s, t: d.t, x: (d.about || '') + ' ' + (d.n || '') + ' ' + (d.rp || ''), c: d.c, vc: v(d).c, vt: v(d).t, to: d.to || '', rb: d.rb || '', rbi: d.rbi || null, cq: d.cq || 0, u: 'dokumenty/' + d.slug + '/' })),
    Q: {}
  };
  F.forEach(f => { data.Q[f.id] = Q[f.id].map(q => [q[0], q[1], q[2], q[3], q[6]]); });
  write(path.join(SEC, 'nv-search-data.js'), 'window.NVS=' + JSON.stringify(data) + ';');
}

/* ═════════ копия сайта для предпросмотра ═════════ */
const SKIP = new Set(['tools', 'server', 'dist', '.git', '.github', 'node_modules', 'report.txt', '.DS_Store'].concat(HOSTED ? ['preview-audit', 'preview-kamera-ventilyatsii', 'preview-lupa', 'preview-mobile', 'preview-services', '404.html'] : []));
const GEN = new Set(pages.map(p => path.join(OUT, p.path, 'index.html')));
const reMenu = new RegExp('(<a href="[^"]*(?:' + SEC + '/|\\./)"[^>]*>)' + OLD_NAME + '(?=<)', 'g');
let copied = 0, patched = 0;
(function walk(rel) {
  fs.readdirSync(path.join(REPO, rel), { withFileTypes: true }).forEach(e => {
    if (!rel && SKIP.has(e.name)) return;
    if (e.name.endsWith('.md') || e.name === '.DS_Store') return;
    const r = path.join(rel, e.name), dst = path.join(OUT, r);
    if (e.isDirectory()) return walk(r);
    if (GEN.has(dst)) return;                                   // страница собрана заново
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    if (e.name.endsWith('.html')) {
      let s = fs.readFileSync(path.join(REPO, r), 'utf8'), s0 = s;
      // название раздела в меню, подвале и цепочках — только в копии для предпросмотра
      s = s.replace(reMenu, '$1' + NAME).split('<span class="rel-k">' + OLD_NAME + '</span>').join('<span class="rel-k">' + NAME + '</span>')
        .split('"name": "' + OLD_NAME + '", "item": "' + SITE + '/' + SEC + '/"').join('"name": "' + NAME + '", "item": "' + SITE + '/' + SEC + '/"');
      if (s !== s0) patched++;
      fs.writeFileSync(dst, s);
    } else fs.copyFileSync(path.join(REPO, r), dst);
    copied++;
  });
})('');

/* поиск по сайту (лупа в шапке): прежние разделы хаба переехали на страницу темы, страницы навигатора добавлены в индекс */
{
  const f = path.join(OUT, 'search-index.json'), idx = JSON.parse(fs.readFileSync(f, 'utf8'));
  const oldU = SEC + '/', pest = pages.find(p => p.path.indexOf('/temy/nasekomye-i-gryzuny/') > 0), newU = pest.path.slice(1);
  const navPaths = new Set(pages.filter(p => p !== pest && p.path.indexOf('/poisk/') < 0).map(p => p.path.slice(1)));
  // при повторном запуске на ветке с уже собранным разделом убираем прежние записи навигатора, чтобы не плодить дубли
  if (idx.p.some(p => p[1] === newU)) {
    const keepIdx = new Map();
    const newP = [];
    idx.p.forEach((p, i) => { if (!navPaths.has(p[1])) { keepIdx.set(i, newP.length); newP.push(p); } });
    idx.p = newP;
    idx.i = idx.i.filter(r => !navPaths.has(r[1]) && keepIdx.has(r[5])).map(r => (r[5] = keepIdx.get(r[5]), r));
  } else {
    const k = idx.p.findIndex(p => p[1] === oldU); if (k < 0) throw new Error('в индексе поиска нет прежнего хаба');
    idx.p[k] = ['Насекомые и грызуны: требования', newU];
    idx.i.forEach(r => { if (r[1] === oldU || r[1].indexOf(oldU + '#') === 0 || r[1].indexOf(oldU + '?') === 0) r[1] = newU + r[1].slice(oldU.length); });
  }
  pages.forEach(p => {
    if (p === pest || p.path.indexOf('/poisk/') > 0) return;
    idx.p.push([clip(p.h1, 60), p.path.slice(1)]);
    idx.i.push(['p', p.path.slice(1), p.h1, clip(p.desc || '', 190), p.title, idx.p.length - 1]);
  });
  idx.v = VER;
  fs.writeFileSync(f, JSON.stringify(idx));
}

/* копия для закрытого предпросмотра */
if (HOSTED) {
  const SHIM = '<script>/* предпросмотр: вместо хранилища браузера — память вкладки */(function(w){function mk(p){function all(){try{return JSON.parse(w.name||"{}")||{}}catch(e){return{}}}function put(o){try{w.name=JSON.stringify(o)}catch(e){}}return{getItem:function(k){var o=all();return(p+k)in o?o[p+k]:null},setItem:function(k,v){var o=all();o[p+k]=String(v);put(o)},removeItem:function(k){var o=all();delete o[p+k];put(o)},clear:function(){var o=all(),k;for(k in o)if(k.indexOf(p)===0)delete o[k];put(o)}}}w.__pcSS=mk("s:");w.__pcLS=mk("l:");w.NV_INDEX="index.html"})(window)</script>\n';
  const store = s => s.replace(/\bsessionStorage\b/g, '__pcSS').replace(/\blocalStorage\b/g, '__pcLS');
  const link = u => {
    if (/^(?:[a-z][a-z0-9+.-]*:|#|\/\/)/i.test(u) || u === '') return u;
    const m = /^([^?#]*)([?#].*)?$/.exec(u); let p = m[1];
    if (p === '' ) return u;
    if (p === '.' || p === '..' || /\/\.\.?$/.test(p)) p += '/';
    return /\/$/.test(p) ? p + 'index.html' + (m[2] || '') : u;
  };
  let nh = 0;
  (function walk(dir) {
    fs.readdirSync(dir, { withFileTypes: true }).forEach(e => {
      const f = path.join(dir, e.name);
      if (e.isDirectory()) return walk(f);
      if (e.name.endsWith('.html')) {
        let s = fs.readFileSync(f, 'utf8');
        s = s.replace(/(\s(?:href|action)=")([^"]*)(")/g, (m, a, u, b) => a + link(u) + b);
        s = store(s).replace(/<head>\n?/, m => m + SHIM);
        // загрузчик поиска по сайту получает корень «../» — адреса из индекса уже с index.html
        fs.writeFileSync(f, s); nh++;
      } else if (e.name.endsWith('.js')) fs.writeFileSync(f, store(fs.readFileSync(f, 'utf8')));
      else if (e.name === 'search-index.json') {
        const idx = JSON.parse(fs.readFileSync(f, 'utf8')), fix = u => { const m = /^([^?#]*)([?#].*)?$/.exec(u); return (m[1] === '' || /\/$/.test(m[1])) ? m[1] + 'index.html' + (m[2] || '') : u; };
        idx.p.forEach(p => { p[1] = fix(p[1]); }); idx.i.forEach(r => { r[1] = fix(r[1]); });
        fs.writeFileSync(f, JSON.stringify(idx));
      }
    });
  })(OUT);
  console.log('Копия для закрытого предпросмотра: ссылки с index.html и память вкладки вместо хранилища — ' + nh + ' страниц');
}

if (!HOSTED) fs.writeFileSync(path.join(__dirname, 'pages.json'), JSON.stringify(pages.map(p => ({ path: p.path, title: p.title, h1: p.h1, index: p.index, bytes: p.bytes })), null, 1));
const tot = pages.reduce((a, p) => a + p.bytes, 0);
console.log('Страниц раздела: ' + pages.length + ' (' + (tot / 1048576).toFixed(1) + ' МБ), из них к индексации в рабочей версии: ' + pages.filter(p => p.index).length);
console.log('Самые тяжёлые: ' + pages.slice().sort((a, b) => b.bytes - a.bytes).slice(0, 5).map(p => p.path + ' ' + Math.round(p.bytes / 1024) + ' КБ').join('; '));
console.log('Скопировано файлов сайта: ' + copied + ', страниц с новым названием раздела: ' + patched);
console.log('Готово: ' + OUT);
