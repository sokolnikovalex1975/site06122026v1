#!/usr/bin/env python3
"""Сборка страницы /dezinsektsiya/index.html (вёрстка v1 с графикой, SEO по журналу пест-контроля и «что такое дезинсекция»).

python3 tools/dezinsektsiya/assemble.py [--prod <путь>]  ->  dezinsektsiya/index.html (превью с noindex);
с --prod дополнительно пишет версию для сайта без noindex. После сборки: python3 tools/menu/apply_menu.py
Шаблон (шапка, подвал, форма) берётся из текущей страницы договора и сохраняется в template-dogovor.html.
"""
import json, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # корень репозитория
OUT = ROOT / 'dezinsektsiya' / 'index.html'  # превью для GitHub Pages (с noindex)
PROD = pathlib.Path(sys.argv[sys.argv.index('--prod') + 1]) if '--prod' in sys.argv else None  # версия для сайта, без noindex
MENU_DOGOVOR = ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'index.html'

if MENU_DOGOVOR.exists():
    shutil.copy2(MENU_DOGOVOR, HERE / 'template-dogovor.html')

SRC = HERE / 'template-dogovor.html'
URL = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/dezinsektsiya/'
TITLE = 'Дезинсекция для организаций в Москве и области — ПЕСТКОНТРОЛЬ Центр'
OG_TITLE = 'Дезинсекция для организаций и предприятий в Москве и области'
DESC = ('Дезинсекция предприятий и коммерческих помещений по СанПиН 3.3686-21 и IPM: '
        'от 3 500 ₽, обработка без остановки работы, образец журнала пест-контроля и дезинсекции PDF.')

s = SRC.read_text(encoding='utf-8')
main = (HERE / 'main.html').read_text(encoding='utf-8')
css = (HERE / 'extra.css').read_text(encoding='utf-8').strip()
css = re.sub(r'\s*\n\s*', '', css)

# 1. Метаданные, Open Graph и предзагрузка адаптивного Hero
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = s.replace('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/dogovor-deratizatsiya-dezinsektsiya/', URL)
s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', s, count=1)
s = s.replace('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/img/dogovor-og.jpg',
              'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/img/dez-og.jpg')
s = re.sub(r'<meta property="og:image:alt" content="[^"]*">',
           '<meta property="og:image:alt" content="Инженер ПЕСТКОНТРОЛЬ Центр проверяет инсектицидный УФ-облучатель с клеевым экраном и заполняет журнал пест-контроля">',
           s, count=1)
s = s.replace('../img/dogovor-hero-1440.webp 1440w, ../img/dogovor-hero.webp 1920w',
              '../img/dez-hero-1440.webp 1440w, ../img/dez-hero.webp 1920w')
s = s.replace('../img/dogovor-hero-mob-760.webp 760w, ../img/dogovor-hero-mob.webp 1024w',
              '../img/dez-hero-mob-760.webp 760w, ../img/dez-hero-mob.webp 1024w')

# 2. Стили страницы
s, n = re.subn(r'<style>.*?</style>', lambda m: f'<style>{css}</style>', s, count=1, flags=re.S)
assert n == 1

# 3. Разметка Schema.org (BreadcrumbList + Service с ценами + FAQPage с 10 вопросами)
qa_pairs = re.findall(
    r'<div class="card qa[^"]*"><button[^>]*>(.*?)<span class="pm"></span></button>'
    r'<div class="ans"[^>]*><div><p>(.*?)</p></div></div></div>',
    main, flags=re.S
)
assert len(qa_pairs) == 10, f'Expected 10 FAQ items, got {len(qa_pairs)}'
clean = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h).replace('&nbsp;', ' ').replace('&amp;', '&').replace('&gt;', '>')).strip()

ld = {
    '@context': 'https://schema.org',
    '@graph': [
        {
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Дезинсекция для организаций', 'item': URL},
            ],
        },
        {
            '@type': 'Service',
            '@id': URL + '#service',
            'name': 'Дезинсекция для организаций и предприятий',
            'serviceType': 'Профилактическая и истребительная дезинсекция по системе IPM (СанПиН 3.3686-21)',
            'description': DESC,
            'url': URL,
            'provider': {
                '@type': 'Organization',
                '@id': 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/#org',
                'name': 'ПЕСТКОНТРОЛЬ Центр',
                'legalName': 'ООО «Центр дезинфекционных услуг»',
                'url': 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/',
                'telephone': '+7 495 104-35-70',
                'email': 'b2b@pestcontrol-center.ru',
            },
            'areaServed': [
                {'@type': 'City', 'name': 'Москва'},
                {'@type': 'AdministrativeArea', 'name': 'Московская область'},
            ],
            'audience': {'@type': 'BusinessAudience', 'audienceType': 'Юридические лица, ИП, предприятия и организации'},
            'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 3500, 'offerCount': 3},
            'hasOfferCatalog': {
                '@type': 'OfferCatalog',
                'name': 'Услуги дезинсекции для юридических лиц',
                'itemListElement': [
                    {
                        '@type': 'Offer',
                        'name': 'Плановая дезинсекция по договору (кафе, ресторан, магазин)',
                        'priceCurrency': 'RUB',
                        'price': 3500,
                        'priceSpecification': {'@type': 'UnitPriceSpecification', 'minPrice': 3500, 'priceCurrency': 'RUB', 'unitText': 'в месяц', 'unitCode': 'MON'},
                    },
                    {
                        '@type': 'Offer',
                        'name': 'Плановая дезинсекция склада или производственного цеха',
                        'priceCurrency': 'RUB',
                        'price': 4500,
                        'priceSpecification': {'@type': 'UnitPriceSpecification', 'minPrice': 4500, 'priceCurrency': 'RUB', 'unitText': 'в месяц', 'unitCode': 'MON'},
                    },
                    {
                        '@type': 'Offer',
                        'name': 'Разовая истребительная дезинсекция помещения',
                        'priceCurrency': 'RUB',
                        'price': 3500,
                        'priceSpecification': {'@type': 'UnitPriceSpecification', 'minPrice': 3500, 'priceCurrency': 'RUB', 'unitText': 'за выезд'},
                    },
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

# 4. Шапка, мобильное меню, подвал и нижняя панель (снимаем aria-current с «Договор» и ставим кнопку «Бесплатный выезд»)
s = s.replace('<a href="./" class="active" aria-current="page">Договор</a>',
              '<a href="../dogovor-deratizatsiya-dezinsektsiya/">Договор</a>')
s = s.replace('<a href="./" aria-current="page">Договор <small>на\u00a0дератизацию и\u00a0дезинсекцию</small></a>',
              '<a href="../dogovor-deratizatsiya-dezinsektsiya/">Договор <small>на\u00a0дератизацию и\u00a0дезинсекцию</small></a>')
s = s.replace('<a href="./" aria-current="page">Договор на\u00a0дератизацию и\u00a0дезинсекцию</a>',
              '<a href="../dogovor-deratizatsiya-dezinsektsiya/">Договор на\u00a0дератизацию и\u00a0дезинсекцию</a>')
s = s.replace('<span class="btn-t">Проект договора</span>', '<span class="btn-t">Бесплатный выезд</span>')
s = s.replace('<span class="btn-t">Получить проект договора</span>', '<span class="btn-t">Заказать бесплатное обследование</span>')
s = s.replace('<a href="#zayavka" class="c2"><span>Проект договора</span></a>',
              '<a href="#zayavka" class="c2"><span>Бесплатный выезд</span></a>')

# 5. Основное содержимое
s, n = re.subn(r'<main id="main"[^>]*>.*?</main>', lambda m: main.strip(), s, count=1, flags=re.S)
assert n == 1

# 6. Интерактивность: предпросмотр, самопроверка, ленивые фоны и упаковка полей формы в msg для send.php
JS = r"""<script>
/* Предпросмотр: вне рабочего домена заявка не отправляется (на пестконтроль-центр.рф этот блок не срабатывает) */
(function(){
  if(!/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname)){
    var origFetch=window.fetch;
    window.fetch=function(u){
      if(typeof u==='string'&&u.indexOf('send.php')>-1){
        return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},400)});
      }
      return origFetch.apply(this,arguments);
    };
  }
  var box=document.getElementById('samoproverka');
  if(box){
    var cbs=box.querySelectorAll('input[type=checkbox]'),res=document.getElementById('chk-res'),note=document.getElementById('chk-note');
    var upd=function(){
      var n=0;for(var i=0;i<cbs.length;i++)if(cbs[i].checked)n++;
      res.innerHTML='<b>'+n+'</b> из '+cbs.length+' на месте';
      res.classList.toggle('warn',n<cbs.length);
      note.textContent=n===cbs.length
        ?'Все 5 пунктов отмечены. На бесплатном обследовании проверим фактическое состояние ловушек, УФ-ламп и записей в журнале пест-контроля.'
        :'Не хватает '+(cbs.length-n)+' из '+cbs.length+'. На бесплатном обследовании покажем уязвимые зоны, заведём журнал пест-контроля и составим схему точек.';
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
      var tk=document.getElementById('fk'),cm=document.getElementById('fm'),ms=document.getElementById('fmsg');
      if(ms){
        var parts=['Страница: дезинсекция для организаций (/dezinsektsiya/)'];
        if(tk&&tk.value)parts.push('Задача: '+tk.value);
        if(cm&&cm.value.trim())parts.push('Комментарий / адрес: '+cm.value.trim());
        ms.value=parts.join('\n');
      }
    },true);
  }
})();
</script>"""
s, n = re.subn(r'<script>\(function\(\)\{var f=document\.getElementById\(\'form\'\);.*?</script>',
               lambda m: JS, s, count=1, flags=re.S)
assert n == 1

s_prod = re.sub(r'<meta name="robots" content="noindex, nofollow"><!--[^>]*-->\n?', '', s, count=1)

OUT.write_text(s, encoding='utf-8')
print('ok preview:', OUT, len(s))
if PROD:
    PROD.parent.mkdir(parents=True, exist_ok=True)
    PROD.write_text(s_prod, encoding='utf-8')
    print('ok prod:', PROD, len(s_prod))
