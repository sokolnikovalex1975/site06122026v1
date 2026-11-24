/* Данные навигатора: справочники (window.NAV) и вопросы листов (window.NAVQ) + адреса страниц */
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const dir = path.join(__dirname, '..', 'data');
const w = {}; const ctx = { window: w }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(dir, 'core.js'), 'utf8'), ctx);
vm.runInContext(fs.readFileSync(path.join(dir, 'q.js'), 'utf8'), ctx);
const N = w.NAV, Q = w.NAVQ;

const TR = { а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'e', ж: 'zh', з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'h', ц: 'ts', ч: 'ch', ш: 'sh', щ: 'shch', ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu', я: 'ya' };
function translit(s) {
  return String(s).toLowerCase().replace(/№/g, ' ').split('').map(ch => (ch in TR ? TR[ch] : ch)).join('')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

/* адреса объектов, тем и разборов заданы вручную: короткие и в той же транслитерации, что остальной сайт */
const FORM_SLUG = {
  '580_p02': 'obshchepit', '580_p01': 'produktovyy-magazin', '578_p01': 'neprodovolstvennyy-magazin', '578_p24': 'pitanie-detey',
  '578_p02': 'gostinitsa', '578_p03': 'obshchezhitie', '578_p04': 'sotsialnoe-obsluzhivanie', '578_p18': 'detskiy-dom',
  '578_p10': 'meditsinskaya-organizatsiya', '578_p11': 'apteka', '578_p13': 'detskiy-sad', '578_p14': 'shkola',
  '578_p15': 'dopolnitelnoe-obrazovanie', '578_p16': 'kolledzh', '578_p17': 'vuz', '578_p12': 'detskaya-igrovaya-komnata',
  '578_p19': 'lager-dnevnogo-prebyvaniya', '578_p20': 'zagorodnyy-lager', '578_p21': 'palatochnyy-lager', '578_p31': 'lager-truda-i-otdyha',
  '578_p22': 'massovye-meropriyatiya-s-detmi', '578_p23': 'perevozka-detey-po-zheleznoy-doroge', '580_p03': 'sport-basseyn-akvapark',
  '580_p05': 'salon-krasoty', '580_p06': 'banya-sauna', '580_p04': 'prachechnaya-himchistka', '578_p09': 'plyazh',
  '578_p25': 'obshchestvennyy-tualet', '578_p05': 'sanitarnyy-propusknik', '578_p06': 'mnogokvartirnyy-dom', '578_p07': 'vodosnabzhenie',
  '578_p08': 'vodootvedenie', '578_p30': 'usloviya-truda', '578_p29': 'othody', '578_p26': 'sanitarno-zashchitnaya-zona',
  '578_p28': 'pestitsidy-i-agrohimikaty', '578_p27': 'radioelektronnye-sredstva',
  sklad: 'sklad', ofis: 'ofis', pishcheprom: 'pishchevoe-proizvodstvo', farma: 'farmatsevticheskoe-proizvodstvo'
};
const THEME_SLUG = {
  vrediteli: 'nasekomye-i-gryzuny', dez: 'uborka-i-dezinfektsiya', othody: 'othody', voda: 'voda-i-kanalizatsiya',
  vozduh: 'ventilyatsiya-i-mikroklimat', personal: 'personal', pk: 'proizvodstvennyy-kontrol', pitanie: 'pitanie-i-pishchevaya-produktsiya',
  pomesh: 'pomeshcheniya-i-oborudovanie', territoriya: 'territoriya-i-szz', fizfakt: 'osveshchenie-shum-izlucheniya',
  infekcii: 'profilaktika-infektsiy', trud: 'usloviya-truda', razresh: 'uvedomleniya-i-zaklyucheniya', rezhim: 'rezhim',
  pestitsidy: 'pestitsidy-i-agrohimikaty', tovary: 'tovary-i-tehreglamenty'
};
const CARD_SLUG = {
  ventilyaciya: 'ventilyatsiya', legionelly: 'legionelly', vrediteli: 'nasekomye-i-gryzuny', 'konteinernaya-ploshchadka': 'konteynernaya-ploshchadka',
  personal: 'medosmotry-i-obuchenie-personala', 'proizvodstvennyj-kontrol': 'proizvodstvennyy-kontrol', 'uborka-gostinica': 'uborka-v-gostinitse',
  'novye-pravila-2026': 'novye-pravila-2026', szz: 'sanitarno-zashchitnaya-zona', 'othody-proizvodstva': 'othody-proizvodstva',
  medothody: 'meditsinskie-othody', 'sroki-3684-3685': 'sroki-sanpin-3684-i-3685'
};
/* разбор о проверочных листах уже есть на сайте отдельной страницей — второй такой же не создаём */
const CARD_EXT = { 'proverochnye-listy': 'proverochnye-listy/' };

const fIdx = {}, dIdx = {}, tIdx = {}, cIdx = {}, coIdx = {};
N.forms.forEach((f, i) => { fIdx[f.id] = i; f.slug = FORM_SLUG[f.id]; if (!f.slug) throw new Error('нет адреса для листа ' + f.id); });
N.composites.forEach((c, i) => { coIdx[c.id] = i; c.slug = FORM_SLUG[c.id]; if (!c.slug) throw new Error('нет адреса для подборки ' + c.id); });
N.themes.forEach((t, i) => { tIdx[t.id] = i; t.slug = THEME_SLUG[t.id]; if (!t.slug) throw new Error('нет адреса для темы ' + t.id); });
N.cards.forEach((c, i) => { cIdx[c.id] = i; c.slug = CARD_SLUG[c.id] || null; c.ext = CARD_EXT[c.id] || null; if (!c.slug && !c.ext) throw new Error('нет адреса для разбора ' + c.id); });
const seen = {};
N.docs.forEach((d, i) => {
  dIdx[d.id] = i;
  let s = translit(d.s) || d.id;
  if (seen[s]) s = s + '-' + translit(d.id);
  seen[s] = 1; d.slug = s;
});
{ const all = N.forms.map(f => f.slug).concat(N.composites.map(c => c.slug)); if (new Set(all).size !== all.length) throw new Error('адреса объектов повторяются'); }

module.exports = { N, Q, fIdx, dIdx, tIdx, cIdx, coIdx, translit };
