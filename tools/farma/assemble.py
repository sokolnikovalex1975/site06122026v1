#!/usr/bin/env python3
"""Сборка страницы /farmatsevticheskie-proizvodstva/index.html — «Пест-контроль фармацевтического производства по GMP».

python3 tools/farma/assemble.py [--prod <путь>]  ->  farmatsevticheskie-proizvodstva/index.html (превью с noindex);
с --prod дополнительно пишет версию для сайта без noindex. После сборки: python3 tools/menu/apply_menu.py
Шаблон (шапка, подвал, форма, счётчики-вставки сервера) берётся из текущей страницы договора и сохраняется в template-dogovor.html.
Схема «шесть контуров» рисуется здесь (функция kontur_svg) и вставляется вместо <!--KONTUR_SVG--> в main.html.
"""
import json, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # корень репозитория
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # неразрывные пробелы после коротких слов, как в остальных текстах сайта

SLUG = 'farmatsevticheskie-proizvodstva'
OUT = ROOT / SLUG / 'index.html'  # превью для GitHub Pages (с noindex)
PROD = pathlib.Path(sys.argv[sys.argv.index('--prod') + 1]) if '--prod' in sys.argv else None  # версия для сайта, без noindex
MENU_DOGOVOR = ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'index.html'

if MENU_DOGOVOR.exists():
    shutil.copy2(MENU_DOGOVOR, HERE / 'template-dogovor.html')

SRC = HERE / 'template-dogovor.html'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + SLUG + '/'
TITLE = 'Пест-контроль фармацевтического производства по GMP — ПЕСТКОНТРОЛЬ Центр'
OG_TITLE = 'Пест-контроль фармацевтического производства по GMP в Москве и области'
DESC = ('Пест-контроль фармпроизводств и складов лекарств в Москве и МО по GMP ЕАЭС: '
        'контуры защиты до чистых зон, без яда в помещениях, тренды и документы для инспекции.')
OG_ALT = ('Специалист ПЕСТКОНТРОЛЬ Центр проверяет пронумерованную ловушку КЛТ-14 '
          'в коридоре у чистой зоны фармацевтического производства')


# ---------- схема «шесть контуров защиты» ----------
def rr(x, y, w, h, r):
    return (f'M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}'
            f'H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z')


def kontur_svg():
    R = [(8, 8, 624, 444, 30), (42, 42, 556, 376, 26), (76, 76, 488, 308, 22),
         (110, 110, 420, 240, 18), (144, 144, 352, 172, 14), (178, 178, 284, 104, 10)]
    labels = ['Территория и периметр', 'Оболочка здания', 'Склады и карантин',
              'Технические и бытовые зоны', 'Шлюзы и переходы']
    sq = lambda x, y: f'<rect class="ik" x="{x - 4.5}" y="{y - 4.5}" width="9" height="9" rx="1.5"/>'
    dot = lambda x, y: f'<circle class="it" cx="{x}" cy="{y}" r="4.2"/>'
    fer = lambda x, y: f'<path class="if" d="M{x} {y - 5.5}L{x + 5.5} {y + 4}H{x - 5.5}Z"/>'
    uv = lambda x, y, v=False: (f'<rect class="iu" x="{x - 2.5}" y="{y - 8}" width="5" height="16" rx="2.5" filter="url(#glow)"/>' if v
                                else f'<rect class="iu" x="{x - 8}" y="{y - 2.5}" width="16" height="5" rx="2.5" filter="url(#glow)"/>')
    sop = lambda x, y: f'<circle class="is" cx="{x}" cy="{y}" r="4.6"/>'
    icons = {
        1: [sq(x, 435) for x in (110, 190, 270, 350, 430, 510)]
           + [sq(25, y) for y in (130, 215, 300, 385)] + [sq(615, y) for y in (130, 215, 300, 385)]
           + [sq(x, 25) for x in (300, 380, 460, 540)],
        2: [dot(x, 59) for x in (330, 425, 520)] + [dot(x, 401) for x in (130, 235, 405, 510)]
           + [dot(59, y) for y in (150, 240, 330)] + [dot(581, y) for y in (150, 240, 330)],
        3: [dot(x, 93) for x in (320, 410, 500)] + [fer(x, 367) for x in (175, 285, 395)] + [dot(465, 367)]
           + [dot(93, y) for y in (175, 285)] + [uv(547, 190, True), dot(547, 290)],
        4: [dot(x, 127) for x in (360, 455)] + [dot(x, 333) for x in (205, 320, 435)]
           + [uv(127, 230, True), dot(513, 230)],
        5: [sop(250, 299), sop(390, 299), sop(161, 230), sop(479, 230)],
    }
    g = []
    for i, (x, y, w, h, r) in enumerate(R, start=1):
        if i < 6:
            ix, iy, iw, ih, ir = R[i]
            d = rr(x, y, w, h, r) + rr(ix, iy, iw, ih, ir)
            body = (f'<path class="kz" fill-rule="evenodd" d="{d}"/>'
                    f'<g class="kn"><circle cx="{x + 17}" cy="{y + 17}" r="9.5"/><text x="{x + 17}" y="{y + 17.5}">{i}</text></g>'
                    f'<text class="kl" x="{x + 33}" y="{y + 21.5}">{labels[i - 1]}</text>'
                    f'<g class="ph-ic">{"".join(icons[i])}</g>')
        else:
            cx = x + w / 2
            body = (f'<path class="kz" d="{rr(x, y, w, h, r)}"/>'
                    f'<g class="kn"><circle cx="{x + 17}" cy="{y + 17}" r="9.5"/><text x="{x + 17}" y="{y + 17.5}">6</text></g>'
                    f'<text class="kc1" x="{cx}" y="{y + 44}">Чистые помещения</text>'
                    f'<text class="kc2" x="{cx}" y="{y + 66}">D → C → B → A</text>'
                    f'<text class="kc3" x="{cx}" y="{y + 88}">без ловушек и средств</text>')
        g.append(f'<g class="kz-g kz-{i}" data-z="{i}">{body}</g>')
    return ('<svg id="ph-map" viewBox="0 0 640 460" role="img" aria-labelledby="ph-map-t">'
            '<title id="ph-map-t">Схема шести контуров защиты фармацевтического производства: '
            'от территории с запираемыми станциями до чистых помещений без ловушек и средств</title>'
            '<defs><filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            + ''.join(g) + '</svg>')


s = SRC.read_text(encoding='utf-8')
main = (HERE / 'main.html').read_text(encoding='utf-8')
css = (HERE / 'extra.css').read_text(encoding='utf-8').strip()
css = re.sub(r'\s*\n\s*', '', css)

# 1. Метаданные, Open Graph и предзагрузка адаптивного Hero
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = s.replace(SITE + 'dogovor-deratizatsiya-dezinsektsiya/', URL)
s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', s, count=1)
s = s.replace(SITE + 'img/dogovor-og.jpg', SITE + 'img/farma-og.jpg')
s = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', s, count=1)
for a, b in (('../img/dogovor-hero-1440.webp 1440w, ../img/dogovor-hero.webp 1920w', '../img/farma-hero-1440.webp 1440w, ../img/farma-hero.webp 1920w'),
             ('../img/dogovor-hero-mob-760.webp 760w, ../img/dogovor-hero-mob.webp 1024w', '../img/farma-hero-mob-760.webp 760w, ../img/farma-hero-mob.webp 1024w')):
    assert a in s, a
    s = s.replace(a, b)
assert 'dogovor-hero' not in s.split('<main')[0], 'в <head> осталась картинка договора'

# 2. Стили страницы
s, n = re.subn(r'<style>.*?</style>', lambda m: f'<style>{css}</style>', s, count=1, flags=re.S)
assert n == 1

# 3. Разметка Schema.org (BreadcrumbList + Service + FAQPage с 10 вопросами)
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
                {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
                {'@type': 'ListItem', 'position': 2, 'name': 'Фармацевтические производства', 'item': URL},
            ],
        },
        {
            '@type': 'Service',
            '@id': URL + '#service',
            'name': 'Пест-контроль фармацевтического производства по GMP',
            'serviceType': 'Пест-контроль (IPM) фармацевтических производств, складов и дистрибьюторов лекарственных средств',
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
            'audience': {'@type': 'BusinessAudience', 'audienceType': 'Фармацевтические производства, склады и дистрибьюторы лекарственных средств'},
            'hasOfferCatalog': {
                '@type': 'OfferCatalog',
                'name': 'Пест-контроль фармацевтического предприятия',
                'itemListElement': [
                    {'@type': 'Offer', 'name': 'Бесплатное обследование и расчёт', 'price': 0, 'priceCurrency': 'RUB'},
                    {'@type': 'Offer', 'name': 'Программа пест-контроля и план-схема точек контроля'},
                    {'@type': 'Offer', 'name': 'Регулярный мониторинг, дератизация и дезинсекция по договору'},
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

# 4. Шапка, мобильное меню, подвал и нижняя панель (снимаем aria-current с «Договор», кнопка — «Бесплатный выезд»)
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

# 5. Основное содержимое (типографика, неразрывные слова через дефис, схема контуров)
def nowrap_hyphens(html):
    """Слова через дефис («пест-контроль», «GMP-инспекции») не переносим: оборачиваем в <span class="nw">.
    Не трогаем атрибуты и содержимое <option>, <title>, <textarea>, <script>, <style>."""
    parts, out, skip = re.split(r'(<[^>]+>)', html), [], 0
    for part in parts:
        if part.startswith('<'):
            if re.match(r'<(option|title|textarea|script|style)\b', part, re.I):
                skip += 1
            elif re.match(r'</(option|title|textarea|script|style)>', part, re.I):
                skip = max(0, skip - 1)
            out.append(part)
            continue
        if skip or '-' not in part:
            out.append(part)
            continue
        out.append(re.sub(r'(?<![\w-])(\w+(?:-\w+)+)(?![\w-])', r'<span class="nw">\1</span>', part))
    return ''.join(out)


def heading_breaks(html):
    """В заголовках длинное слово после предлога может уходить на новую строку отдельно,
    иначе «на\u00a0фармацевтическом» не помещается в ширину телефона."""
    fix = lambda m: re.sub(r'(?<![\w-])(\w{1,3})\u00a0(\w{14,})', r'\1 \2', m.group(0))
    return re.sub(r'<h([123])\b.*?</h\1>', fix, html, flags=re.S)


# Номер телефона оставляем в точности как на остальных страницах («+7 (495) 104-35-70» обычными пробелами, без вложенных тегов):
# по нему подменяет номер колл-трекинг UIS
PHONE, PH_TOKEN = '+7 (495) 104-35-70', 'PHONETOKEN0'
assert PH_TOKEN not in main
body = typo(main.strip().replace(PHONE, PH_TOKEN))
# дефисные слова не переносим только в заголовках и вопросах FAQ (в flex-контейнерах — кнопках, бейджах — вложенный span ломает раскладку,
# поэтому вопрос FAQ целиком лежит в <span class="q">)
body = re.sub(r'<h([123])\b[^>]*>.*?</h\1>', lambda m: nowrap_hyphens(m.group(0)), body, flags=re.S)
body = re.sub(r'<span class="q">.*?</span><span class="pm">', lambda m: nowrap_hyphens(m.group(0)), body, flags=re.S)
body = heading_breaks(body).replace(PH_TOKEN, PHONE)
assert body.count(PHONE) == main.count(PHONE)
assert body.count('<!--KONTUR_SVG-->') == 1
body = body.replace('<!--KONTUR_SVG-->', kontur_svg())
s, n = re.subn(r'<main id="main"[^>]*>.*?</main>', lambda m: body, s, count=1, flags=re.S)
assert n == 1

# 6. Интерактивность: предпросмотр, самопроверка, схема контуров, ленивые фоны и упаковка полей формы в msg для send.php
JS = r"""<script>
/* Локальная проверка: на localhost заявка не отправляется (на GitHub Pages отправку отключает app.js, на сайте заявка уходит в send.php) */
(function(){
  if(/^(localhost|127\.0\.0\.1)$/.test(location.hostname)){
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
        ?'Все 5 пунктов на месте. На бесплатном обследовании сверим схему с объектом и проверим записи за последние месяцы.'
        :(n===0?'Отметьте, что уже есть на вашем предприятии. Каждый пункт инспектор или аудитор может сверить по документам и на месте.'
        :'Не хватает '+(cbs.length-n)+' из '+cbs.length+'. На бесплатном обследовании покажем, что добавить в программу и документы до инспекции.');
    };
    for(var i=0;i<cbs.length;i++)cbs[i].addEventListener('change',upd);
  }
  var map=document.getElementById('ph-map'),zl=document.getElementById('ph-zl');
  if(map&&zl){
    var rings=map.querySelectorAll('.kz-g'),items=zl.querySelectorAll('li[data-z]'),cur=null;
    var set=function(z){
      cur=z;
      for(var i=0;i<rings.length;i++)rings[i].classList.toggle('on',rings[i].getAttribute('data-z')===z);
      for(var j=0;j<items.length;j++)items[j].classList.toggle('on',items[j].getAttribute('data-z')===z);
    };
    var bind=function(el){
      var z=el.getAttribute('data-z');
      el.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse')set(z)});
      el.addEventListener('click',function(){set(cur===z&&el.tagName!=='LI'?null:z)});
      if(el.tagName==='LI'){
        el.addEventListener('focus',function(){set(z)});
        el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();set(z)}});
      }
    };
    for(var a=0;a<rings.length;a++)bind(rings[a]);
    for(var b=0;b<items.length;b++)bind(items[b]);
    var wrapK=map.closest('.ph-kontur');
    if(wrapK)wrapK.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')set(null)});
  }
  var lz=document.querySelectorAll('.f-lazy');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('bg-in');io.unobserve(e.target)}})},{rootMargin:'300px'});
    lz.forEach(function(el){io.observe(el)});
  }else{lz.forEach(function(el){el.classList.add('bg-in')})}
  var f=document.getElementById('form');
  if(f){
    f.addEventListener('submit',function(){
      var pr=document.getElementById('fk'),ins=document.getElementById('fi'),cm=document.getElementById('fm'),ms=document.getElementById('fmsg');
      if(ms){
        var parts=['Страница: пест-контроль фармацевтического производства (/farmatsevticheskie-proizvodstva/)'];
        if(pr&&pr.value)parts.push('Профиль производства: '+pr.value);
        if(ins&&ins.value)parts.push('Ближайшая проверка: '+ins.value);
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
assert 'noindex' not in s_prod

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(s, encoding='utf-8')
print('ok preview:', OUT, len(s))
if PROD:
    PROD.parent.mkdir(parents=True, exist_ok=True)
    PROD.write_text(s_prod, encoding='utf-8')
    print('ok prod:', PROD, len(s_prod))
