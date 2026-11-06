#!/usr/bin/env python3
"""Сборка страницы /magaziny-i-torgovye-seti/index.html («Магазины и торговые сети»).

python3 tools/magaziny-i-torgovye-seti/make_css.py   # если меняли main.html или own.css
python3 tools/magaziny-i-torgovye-seti/assemble.py   ->  magaziny-i-torgovye-seti/index.html (превью с noindex)
python3 tools/site/build_site.py                     # меню, «Смотрите также», анимации — как на остальных страницах

Шаблон (шапка, подвал, нижняя панель, скрипты) берётся из текущей страницы договора, как у страницы дезинсекции.
Счётчики Метрики, UIS и Radist в превью не вставляются: их добавляет tools/site/build_prod.py для Timeweb.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SLUG = 'magaziny-i-torgovye-seti'
OUT = ROOT / SLUG / 'index.html'
SRC = ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'index.html'
ICONS = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + SLUG + '/'
TITLE = 'Пест-контроль магазинов и торговых сетей в Москве — ПЕСТКОНТРОЛЬ Центр'
OG_TITLE = 'Пест-контроль для магазинов и торговых сетей в Москве и области'
DESC = ('Дератизация и дезинсекция магазинов и торговых сетей по СП 2.3.6.4281-26: ночные визиты, '
        'журнал в каждом магазине, сводный отчёт по сети. От 3 500 ₽/мес.')
OG_ALT = 'Специалист ПЕСТКОНТРОЛЬ Центр ночью проверяет станцию контроля грызунов в закрытом супермаркете'
MODIFIED = '2026-11-06'

s = SRC.read_text(encoding='utf-8')
main = (HERE / 'main.html').read_text(encoding='utf-8')
main = re.sub(r'\{\{i:([a-z0-9-]+)\}\}', lambda m: ICONS[m.group(1)], main)
css = (HERE / 'extra.css').read_text(encoding='utf-8').strip()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = re.sub(r'\s*\n\s*', '', css)

# 1. Метаданные, Open Graph и предзагрузка адаптивного Hero
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = s.replace(SITE + 'dogovor-deratizatsiya-dezinsektsiya/', URL)
s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', s, count=1)
s = s.replace(SITE + 'img/dogovor-og.jpg', SITE + 'img/seti-og.jpg')
s = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', s, count=1)
s = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_TITLE}">', s, count=1)
s = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{DESC}">', s, count=1)
s = s.replace('../img/dogovor-hero-1440.webp 1440w, ../img/dogovor-hero.webp 1920w',
              '../img/seti-hero-1440.webp 1440w, ../img/seti-hero.webp 1920w')
s = s.replace('../img/dogovor-hero-mob-760.webp 760w, ../img/dogovor-hero-mob.webp 1024w',
              '../img/seti-hero-mob-760.webp 760w, ../img/seti-hero-mob.webp 1024w')
assert 'dogovor-hero' not in s.split('<main')[0], 'в <head> остались ссылки на фото договора'

# 2. Стили страницы
s, n = re.subn(r'<style>.*?</style>', lambda m: f'<style>{css}</style>', s, count=1, flags=re.S)
assert n == 1

# 3. Schema.org: WebPage + BreadcrumbList + Service с ценами + FAQPage
qa_pairs = re.findall(
    r'<div class="card qa[^"]*"><button[^>]*>(.*?)<span class="pm"></span></button>'
    r'<div class="ans"[^>]*><div><p>(.*?)</p></div></div></div>',
    main, flags=re.S)
assert len(qa_pairs) == 10, f'Ожидалось 10 вопросов, найдено {len(qa_pairs)}'
clean = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h).replace('&nbsp;', ' ').replace('&amp;', '&')).strip()


def offer(name, price, unit, code=None):
    spec = {'@type': 'UnitPriceSpecification', 'minPrice': price, 'priceCurrency': 'RUB', 'unitText': unit}
    if code:
        spec['unitCode'] = code
    return {'@type': 'Offer', 'name': name, 'priceCurrency': 'RUB', 'price': price, 'priceSpecification': spec}


ld = {
    '@context': 'https://schema.org',
    '@graph': [
        {
            '@type': 'WebPage',
            '@id': URL + '#page',
            'url': URL,
            'name': TITLE,
            'description': DESC,
            'inLanguage': 'ru',
            'dateModified': MODIFIED,
            'about': {'@id': URL + '#service'},
            'author': {'@type': 'Organization', 'name': 'Методический отдел ПЕСТКОНТРОЛЬ Центр', 'url': SITE},
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/seti-og.jpg', 'width': 1200, 'height': 630},
        },
        {
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
                {'@type': 'ListItem', 'position': 2, 'name': 'Магазины и торговые сети', 'item': URL},
            ],
        },
        {
            '@type': 'Service',
            '@id': URL + '#service',
            'name': 'Пест-контроль магазинов и торговых сетей',
            'serviceType': 'Дератизация и дезинсекция магазинов по системе IPM, СП 2.3.6.4281-26 и СанПиН 3.3686-21',
            'description': DESC,
            'url': URL,
            'provider': {
                '@type': 'Organization',
                '@id': SITE + '#org',
                'name': 'ПЕСТКОНТРОЛЬ Центр',
                'legalName': 'ООО «Центр дезинфекционных услуг»',
                'url': SITE,
                'telephone': '+7 495 104-35-70',
                'email': 'b2b@pestcontrol-center.ru',
            },
            'areaServed': [
                {'@type': 'City', 'name': 'Москва'},
                {'@type': 'AdministrativeArea', 'name': 'Московская область'},
            ],
            'audience': {'@type': 'BusinessAudience', 'audienceType': 'Магазины, супермаркеты, дарксторы и торговые сети'},
            'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 3500, 'offerCount': 3},
            'hasOfferCatalog': {
                '@type': 'OfferCatalog',
                'name': 'Пест-контроль для магазинов и торговых сетей',
                'itemListElement': [
                    offer('Пест-контроль магазина по договору (1–2 визита в месяц)', 3500, 'в месяц', 'MON'),
                    offer('Пест-контроль склада или распределительного центра до 1 000 м²', 4500, 'в месяц', 'MON'),
                    offer('Разовая обработка магазина от грызунов или насекомых', 3500, 'за выезд'),
                ],
            },
        },
        {
            '@type': 'FAQPage',
            '@id': URL + '#faq',
            'mainEntity': [
                {'@type': 'Question', 'name': clean(q), 'acceptedAnswer': {'@type': 'Answer', 'text': clean(a)}}
                for q, a in qa_pairs
            ],
        },
    ],
}
ld_json = json.dumps(ld, ensure_ascii=False, separators=(',', ':'))
s, n = re.subn(r'<script type="application/ld\+json">.*?</script>',
               lambda m: f'<script type="application/ld+json">{ld_json}</script>', s, count=1, flags=re.S)
assert n == 1

# 4. Кнопки шапки, мобильного меню и нижней панели: вместо «Проект договора» — «Бесплатный выезд»
s = s.replace('<span class="btn-t">Проект договора</span>', '<span class="btn-t">Бесплатный выезд</span>')
s = s.replace('<span class="btn-t">Получить проект договора</span>', '<span class="btn-t">Заказать бесплатное обследование</span>')
s = s.replace('<a href="#zayavka" class="c2"><span>Проект договора</span></a>',
              '<a href="#zayavka" class="c2"><span>Бесплатный выезд</span></a>')

# 5. Основное содержимое
s, n = re.subn(r'<main id="main"[^>]*>.*?</main>', lambda m: main.strip(), s, count=1, flags=re.S)
assert n == 1

# 6. Скрипт страницы: карта зон, самопроверка, ленивые фоны, упаковка полей формы в msg для send.php
JS = r"""<script>
(function(){
  /* Предпросмотр: вне рабочего домена заявка не отправляется (на пестконтроль-центр.рф этот блок не срабатывает) */
  if(!/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname)){
    var origFetch=window.fetch;
    window.fetch=function(u){
      if(typeof u==='string'&&u.indexOf('send.php')>-1){
        return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},400)});
      }
      return origFetch.apply(this,arguments);
    };
  }
  /* карта зон: наведение или фокус на пункт списка подсвечивает зону на схеме и наоборот */
  var map=document.querySelector('.t-zmap');
  if(map){
    var set=function(z){
      map.querySelectorAll('[data-z]').forEach(function(el){el.classList.toggle('on',!!z&&el.getAttribute('data-z')===z)});
    };
    map.querySelectorAll('.t-zlist li,.t-plan .bdg,.t-plan .zf').forEach(function(el){
      var z=el.getAttribute('data-z')||el.parentNode.getAttribute('data-z');
      el.addEventListener('mouseenter',function(){set(z)});
      el.addEventListener('focus',function(){set(z)});
      el.addEventListener('click',function(){set(z)});
    });
    map.addEventListener('mouseleave',function(){set(null)});
  }
  /* самопроверка готовности магазина */
  var box=document.getElementById('samoproverka');
  if(box){
    var cbs=box.querySelectorAll('input[type=checkbox]'),res=document.getElementById('chk-res'),note=document.getElementById('chk-note');
    var upd=function(){
      var n=0;for(var i=0;i<cbs.length;i++)if(cbs[i].checked)n++;
      res.innerHTML='<b>'+n+'</b> из '+cbs.length+' на месте';
      res.classList.toggle('warn',n<cbs.length);
      note.textContent=n===cbs.length
        ?'Все 5 пунктов на месте. На бесплатном обследовании сверим журнал со схемой и проверим точки контроля на рампе, складе и площадке ТКО.'
        :(n===0?'Отметьте, что уже есть в вашем магазине. Каждый пустой пункт — замечание при проверке Роспотребнадзора или внутреннем аудите сети.'
               :'Не хватает '+(cbs.length-n)+' из '+cbs.length+'. На бесплатном обследовании покажем, что добавить, и заведём журнал и схему точек.');
    };
    for(var i=0;i<cbs.length;i++)cbs[i].addEventListener('change',upd);
  }
  var lz=document.querySelectorAll('.f-lazy');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('bg-in');io.unobserve(e.target)}})},{rootMargin:'300px'});
    lz.forEach(function(el){io.observe(el)});
  }else{lz.forEach(function(el){el.classList.add('bg-in')})}
  var f=document.getElementById('form');
  if(f){
    f.addEventListener('submit',function(){
      var fo=document.getElementById('ff'),co=document.getElementById('fc'),cm=document.getElementById('fm'),ms=document.getElementById('fmsg');
      if(ms){
        var parts=['Формат магазина: '+((fo&&fo.value)||'не выбран'),'Количество магазинов: '+((co&&co.value)||'не указано')];
        if(cm&&cm.value.trim())parts.push('Адрес / комментарий: '+cm.value.trim());
        parts.push('Страница: Пест-контроль магазинов и торговых сетей (/magaziny-i-torgovye-seti/)');
        ms.value=parts.join('\n');
      }
    },true);
  }
})();
</script>"""
s, n = re.subn(r"<script>\(function\(\)\{var f=document\.getElementById\('form'\);.*?</script>",
               lambda m: JS, s, count=1, flags=re.S)
assert n == 1

assert '{{i:' not in s
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(s, encoding='utf-8')
print('OK:', OUT.relative_to(ROOT), len(s), 'символов')
