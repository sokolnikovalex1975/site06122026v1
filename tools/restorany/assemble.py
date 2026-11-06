#!/usr/bin/env python3
"""Страница «Пест-контроль ресторанов и кафе» (/restorany-i-kafe/).

    python3 tools/restorany/assemble.py      → restorany-i-kafe/index.html
    python3 tools/site/build_site.py         → общие шапка, меню, подвал, анимации, бегущая строка, sitemap

Шаблон — собранная страница пищевых производств (та же отраслевая страница: шапка, подвал,
стили f-hero, самопроверки и схемы зон). Из шаблона берём оболочку, а заменяем:
  * title, description, canonical, Open Graph (+ картинка rest-og.jpg), предзагрузку фото первого экрана;
  * стили — дописываем extra.css к стилям шаблона;
  * структурированные данные — BreadcrumbList, Service с ценами, FAQPage (вопросы берутся из main.html);
  * <main> — целиком из main.html (типографика: неразрывные пробелы после коротких слов);
  * скрипт страницы — самопроверка, схема зон, переключатель «Визит», сборка поля msg для send.php.

Форма совместима со штатным send.php: тип объекта «Ресторан или кафе» есть в списке разрешённых,
формат заведения, задача и адрес передаются в поле msg (send.php читает только name, phone, email, type, msg).
"""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + 'restorany-i-kafe/'
TITLE = 'Пест-контроль ресторанов и кафе в Москве — ПЕСТКОНТРОЛЬ Центр'
OG_TITLE = 'Пест-контроль ресторанов и кафе в Москве и области'
DESC = ('Дезинсекция и дератизация ресторанов, кафе и баров по договору: визиты после закрытия, '
        'гели и ловушки на кухне, журнал и акты по СанПиН. От 3 500 ₽ в месяц, обследование бесплатно.')
OG_ALT = 'Специалист ПЕСТКОНТРОЛЬ Центр проверяет зону под посудомоечной машиной на кухне ресторана после закрытия'

SRC = ROOT / 'pishchevoe-proizvodstvo' / 'index.html'
TPL = HERE / 'template-food.html'
OUT = ROOT / 'restorany-i-kafe' / 'index.html'


def sub(pat, rep, s, flags=0, count=1):
    s2, n = re.subn(pat, rep, s, count=count, flags=flags)
    assert n, 'не найдено: ' + pat[:80]
    return s2


def faq_items(main):
    items = []
    for m in re.finditer(r'<button aria-expanded="false" aria-controls="a\d+" id="q\d+">(.*?)<span class="pm"></span></button>'
                         r'<div class="ans"[^>]*><div>(.*?)</div></div>', main, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).replace('\xa0', ' ').strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).replace('\xa0', ' ').strip()
        items.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    assert len(items) == 10, f'вопросов: {len(items)}'
    return items


def ld_json(main):
    org = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
           'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
           'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}

    def offer(name, unit):
        return {'@type': 'Offer', 'name': name, 'priceCurrency': 'RUB', 'price': 3500,
                'priceSpecification': {'@type': 'UnitPriceSpecification', 'minPrice': 3500, 'priceCurrency': 'RUB', 'unitText': unit}}

    data = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Пест-контроль ресторанов и кафе', 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': 'Пест-контроль ресторанов и кафе',
         'serviceType': 'Дезинсекция и дератизация предприятий общественного питания по договору (СанПиН 3.3686-21, СанПиН 2.3/2.4.4282-26)',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Рестораны, кафе, бары, столовые, сети общественного питания'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 3500, 'offerCount': 2},
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Пест-контроль для общепита', 'itemListElement': [
             offer('Договор на пест-контроль ресторана или кафе', 'в месяц'),
             offer('Разовая истребительная дезинсекция ресторана или кафе', 'за выезд')]}},
        {'@type': 'FAQPage', 'mainEntity': faq_items(main)},
    ]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


JS = r'''<script>
/* Предпросмотр: вне рабочего домена заявка не отправляется (на пестконтроль-центр.рф этот блок не срабатывает) */
(function(){if(/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname))return;var f=window.fetch;window.fetch=function(u){if(typeof u==='string'&&u.indexOf('send.php')>-1)return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},500)});return f.apply(this,arguments)};document.addEventListener('DOMContentLoaded',function(){var p=document.querySelector('.form .fs');if(p)p.textContent='Предпросмотр: заявка никуда не отправляется'})})();
/* самопроверка: счётчик отмеченных пунктов */
document.addEventListener('change',function(e){if(!e.target.closest('.f-check-list'))return;var n=0;document.querySelectorAll('.f-check-list input').forEach(function(i){n+=i.checked?1:0});document.getElementById('chk-n').textContent=n;document.querySelector('.f-check-res').classList.toggle('full',n===5);document.getElementById('chk-note').textContent=n===5?'Всё на месте — на обследовании проверим, как это работает на кухне.':'Чего-то не хватает — на бесплатном обследовании покажем, что добавить до проверки.'});
/* схема зон: подсветка зоны по пункту списка и наоборот */
(function(){var map=document.querySelector('.f-zmap');if(!map)return;var plan=map.querySelector('.f-plan'),items=map.querySelectorAll('.f-zlist li');function set(z){plan.querySelectorAll('[data-z]').forEach(function(g){g.classList.toggle('on',g.getAttribute('data-z')===z)});items.forEach(function(li){li.classList.toggle('on',li.getAttribute('data-z')===z)})}items.forEach(function(li){var z=li.getAttribute('data-z');li.addEventListener('mouseenter',function(){set(z)});li.addEventListener('focus',function(){set(z)});li.addEventListener('click',function(){set(z)})});plan.querySelectorAll('.zf,.bdg').forEach(function(el){var g=el.closest('[data-z]');el.addEventListener('mouseenter',function(){set(g.getAttribute('data-z'))});el.addEventListener('click',function(){set(g.getAttribute('data-z'))})});map.addEventListener('mouseleave',function(){set(null)})})();
/* «Визит после закрытия»: переключатель сценариев (вкладки) и линия прогресса по шагам */
(function(){var box=document.querySelector('.r-visit');if(!box)return;var tabs=[].slice.call(box.querySelectorAll('[role="tab"]')),seen=false;function lit(p){p.classList.remove('r-in');void p.offsetWidth;p.classList.add('r-in')}function show(t,focus){tabs.forEach(function(b){var on=b===t,p=document.getElementById(b.getAttribute('aria-controls'));b.setAttribute('aria-selected',on);b.tabIndex=on?0:-1;p.hidden=!on;if(on&&seen)lit(p)});if(focus)t.focus()}tabs.forEach(function(b,i){b.addEventListener('click',function(){show(b)});b.addEventListener('keydown',function(e){var k=e.key,j=k==='ArrowRight'?i+1:k==='ArrowLeft'?i-1:k==='Home'?0:k==='End'?tabs.length-1:null;if(j===null)return;e.preventDefault();show(tabs[(j+tabs.length)%tabs.length],true)})});var first=document.getElementById('vz-plan');if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){seen=true;var p=box.querySelector('[role="tabpanel"]:not([hidden])');if(p)lit(p);io.disconnect()}})},{rootMargin:'0px 0px -20% 0px'});io.observe(box)}else{seen=true;first.classList.add('r-in')}})();
/* заявка: формат, задача и адрес — в поле msg (send.php принимает name, phone, email, type, msg) */
(function(){var f=document.getElementById('form');if(!f)return;f.addEventListener('submit',function(){var v=function(n){var el=f.elements[n];return el?String(el.value||'').replace(/\u00a0/g,' ').trim():''},rows=[];if(v('format'))rows.push('Формат заведения: '+v('format'));if(v('task'))rows.push('Задача: '+v('task'));if(v('comment'))rows.push('Адрес и комментарий: '+v('comment').slice(0,2500));rows.push('Страница: Пест-контроль ресторанов и кафе ('+location.pathname+')');f.elements.msg.value=rows.join('\n')})})();
</script>
'''


def cta_parts(tpl):
    """Иконки и ссылки мессенджеров берём из блока заявки шаблона — как на остальных страницах сайта."""
    i = tpl.index('<section class="cta" id="zayavka"')
    cta = tpl[i:tpl.index('</section>', i)]
    check = re.search(r'<svg aria-hidden="true" focusable="false" class="lucide lucide-circle-check".*?</svg>', cta, re.S).group(0)
    mx = re.search(r'<a href="([^"]+)" class="max"[^>]*>(<svg.*?</svg>)</a>', cta, re.S)
    tg = re.search(r'<a href="([^"]+)" class="tg"[^>]*>(<svg.*?</svg>)</a>', cta, re.S)
    arrow = re.search(r'<svg class="btn-ic".*?</svg>', cta, re.S).group(0)
    ok = re.search(r'<svg class="ok-ic".*?</svg>', cta, re.S).group(0)
    return {'{{ICON_CHECK}}': check, '{{MAX_HREF}}': mx.group(1), '{{ICON_MAX}}': mx.group(2),
            '{{TG_HREF}}': tg.group(1), '{{ICON_TG}}': tg.group(2), '{{ICON_ARROW}}': arrow, '{{ICON_OK}}': ok}


def main():
    if SRC.exists():
        shutil.copy2(SRC, TPL)
    s = TPL.read_text(encoding='utf-8')
    # скрипт формы пищевых производств (вид производства, ближайшая проверка → msg) не нужен: у этой страницы своя форма и свой скрипт
    s = re.sub(r'<script>/\* Форма: вид производства.*?</script>\n', '', s, count=1, flags=re.S)
    body = (HERE / 'main.html').read_text(encoding='utf-8')
    css = (HERE / 'extra.css').read_text(encoding='utf-8').strip()

    body = typo(body)
    for k, v in cta_parts(s).items():
        assert k in body, k
        body = body.replace(k, v)
    assert '{{' not in body

    # <head>
    s = sub(r'<title>[^<]*</title>', '<title>' + TITLE + '</title>', s)
    s = sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + DESC, s)
    s = sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + URL, s)
    s = sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + URL, s)
    s = sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + OG_TITLE, s)
    s = sub(r'(<meta property="og:description" content=")[^"]*("\s*/?>)', lambda m: m.group(1) + DESC + m.group(2), s)
    s = re.sub(r'\n<meta property="og:image[^>]*>', '', s)
    s = re.sub(r'\n<meta name="twitter:card"[^>]*>', '', s)
    og = ('\n<meta property="og:image" content="' + SITE + 'img/rest-og.jpg">'
          '\n<meta property="og:image:type" content="image/jpeg">'
          '\n<meta property="og:image:width" content="1200">'
          '\n<meta property="og:image:height" content="630">'
          '\n<meta property="og:image:alt" content="' + OG_ALT + '">'
          '\n<meta name="twitter:card" content="summary_large_image">')
    s = sub(r'(<meta property="og:description" content="[^"]*"\s*/?>)', lambda m: m.group(1) + og, s)
    pre = ('<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/rest-hero-1440.webp 1440w, ../img/rest-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
           '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/rest-hero-mob-760.webp 760w, ../img/rest-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">')
    s = re.sub(r'\n<link rel="preload"(?=[^>]*as="image")[^>]*>', '', s)
    s = sub(r'(<link rel="preload" href="\.\./fonts/[^>]*>)', lambda m: m.group(1) + '\n' + pre, s)
    s = sub(r'</style>', lambda m: '\n' + css + '\n</style>', s)
    s = sub(r'<script type="application/ld\+json">.*?</script>', lambda m: ld_json(body), s, flags=re.S)

    # <main> и скрипт страницы
    s = sub(r'<main id="main" tabindex="-1">.*?</main>', lambda m: body.strip(), s, flags=re.S)
    s = sub(r'<script>\n/\* Предпросмотр:.*?</script>\n', lambda m: JS, s, flags=re.S)
    s = s.replace('aria-current="page">Пищевые производства</a>', '>Пищевые производства</a>')

    for bad in ('food-hero', 'Вид производства', 'Ближайшая проверка', 'name="production"', 'name="inspection"'):
        assert bad not in s, 'осталось от шаблона: ' + bad
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(s, encoding='utf-8')
    print('ok', OUT.relative_to(ROOT), f'{len(s) // 1024} КБ')


if __name__ == '__main__':
    main()
