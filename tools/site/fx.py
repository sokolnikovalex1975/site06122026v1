#!/usr/bin/env python3
"""Эффекты под курсором, как на главной, для внутренних страниц сайта (повторный запуск ничего не дублирует).

  * «фонарь» на фото первого экрана (.d-hero и .f-hero): вне круга фото приглушено, в круге — в полную яркость;
    круг следует за мышью, без движения мыши и на телефоне плавно ходит сам. Второй слой фото — копия того же
    <picture> с теми же адресами, поэтому фото не скачивается второй раз. При «уменьшить движение» фонаря нет;
  * подсветка рамки информационных карточек за курсором (как у .card на главной) — только мышь, на телефоне нет;
  * плавное появление формы заявки (data-form), если его не было;
  * лёгкий параллакс фото в карточках отраслей, кейсов и этапов (data-parallax), как на главной;
  * наклон карточек отраслей с иконками на странице дезинфекции (data-tilt), как у карточек отраслей.

Главная (#heroLit) и страница вентиляции (#vLit) уже содержат свой фонарь — фонарь на них не добавляется.
Функция apply(s) работает и с исходником страницы (index.html), и с файлом с сайта (index.php со счётчиками):
вставки привязаны к концу <head>, к скрипту-загрузчику анимаций и к разметке первого экрана.
Вызывается из tools/site/unify.py; для выкладки — из скрипта правки файлов, снятых с сайта.
"""
import re

# карточки без .card, которым нужна подсветка рамки (у .card она уже есть в style.css)
GLOW_SEL = '.d-card,.p-sec,.p-fcard,.p-duty-box,.p-dl-card,.pm-step-card,.pm-scen,.pm-link-card,.k-err,.w-sample,.d-doc-prev'

CSS_GLOW = (
    '/* подсветка рамки карточек за курсором — как у .card на главной (tools/site/fx.py) */\n'
    ':where(' + GLOW_SEL + '){position:relative}\n'
    ':where(' + GLOW_SEL + ')::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1.4px;pointer-events:none;'
    'background:radial-gradient(360px circle at var(--mx,-999px) var(--my,-999px),rgba(124,134,255,.85),rgba(124,134,255,.15) 35%,transparent 60%);'
    '-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;'
    'mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);mask-composite:exclude;opacity:0;transition:opacity .4s;z-index:2}\n'
    '@media (hover:hover) and (pointer:fine){:where(' + GLOW_SEL + '):hover::after{opacity:1}}\n'
)
CSS_LIT = (
    '/* «фонарь» на фото первого экрана — как на главной (tools/site/fx.py) */\n'
    '.fx-lit{position:absolute;inset:0;opacity:0;pointer-events:none;'
    '-webkit-mask-image:radial-gradient(circle var(--sr,320px) at var(--sx,72%) var(--sy,46%),#000 0%,rgba(0,0,0,.55) 45%,transparent 72%);'
    'mask-image:radial-gradient(circle var(--sr,320px) at var(--sx,72%) var(--sy,46%),#000 0%,rgba(0,0,0,.55) 45%,transparent 72%);'
    'transition:opacity 1.8s cubic-bezier(.16,1,.3,1)}\n'
    '#hero :is(.d-hero-media,.hero-media)>picture>img{transition:filter 1.8s cubic-bezier(.16,1,.3,1)}\n'
    '#hero.fx-lit-on :is(.d-hero-media,.hero-media)>picture>img{filter:grayscale(.3) brightness(.56)}\n'
    '#hero.fx-lit-on .fx-lit img{filter:brightness(1.08) contrast(1.06) saturate(1.06)}\n'
    '#hero.fx-lit-on .fx-lit{opacity:1}\n'
)

JS_LIT = (
    "  /* «фонарь»: следует за мышью, без движения мыши плавно ходит сам; на сенсорных экранах ходит сам (30 кадров в секунду).\n"
    "     Не считаем, пока первый экран не виден или вкладка скрыта. Старт — вместе со входом первого экрана */\n"
    "  var hero=document.getElementById('hero'),lit=hero&&hero.querySelector('.fx-lit');\n"
    "  if(lit&&!mm('(prefers-reduced-motion: reduce)').matches){\n"
    "    var media=lit.parentNode,small=mm('(max-width:860px)').matches,full=hero.classList.contains('f-hero');\n"
    "    lit.style.setProperty('--sr',small?'150px':'clamp(240px, 21vw, 400px)');\n"
    "    var cx=small?.5:(full?.68:.74),ax=small?.24:(full?.16:.13),cy=small?.5:.47,ay=small?.2:.17;\n"
    "    var sx=cx,sy=cy,tx=cx,ty=cy,last=-1e9,vis=true,on=false,raf=0,lt=0;\n"
    "    var frame=function(now){\n"
    "      raf=0;if(!on||!vis||document.hidden)return;\n"
    "      var dt=now-lt;if(!fine&&dt<30){raf=requestAnimationFrame(frame);return;}\n"
    "      lt=now;if(now-last>2600){var t=now/1000;tx=cx+ax*Math.sin(t*.33);ty=cy+ay*Math.sin(t*.47+1.3);}\n"
    "      var k=1-Math.pow(.94,Math.min(dt,100)/16.67);sx+=(tx-sx)*k;sy+=(ty-sy)*k;\n"
    "      lit.style.setProperty('--sx',(sx*100).toFixed(2)+'%');lit.style.setProperty('--sy',(sy*100).toFixed(2)+'%');\n"
    "      raf=requestAnimationFrame(frame);\n"
    "    };\n"
    "    var kick=function(){if(!raf&&on&&vis&&!document.hidden){lt=performance.now();raf=requestAnimationFrame(frame);}};\n"
    "    hero.addEventListener('pointermove',function(e){\n"
    "      if(e.pointerType!=='mouse')return;var r=media.getBoundingClientRect();if(!r.width||!r.height)return;\n"
    "      tx=(e.clientX-r.left)/r.width;ty=(e.clientY-r.top)/r.height;last=performance.now();kick();\n"
    "    },{passive:true});\n"
    "    if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;kick();}).observe(hero);\n"
    "    document.addEventListener('visibilitychange',kick);\n"
    "    var start=function(){if(on)return;on=true;hero.classList.add('fx-lit-on');kick();};\n"
    "    var eb=hero.querySelector('.eyebrow');\n"
    "    if(eb&&'MutationObserver' in window){\n"
    "      if(eb.classList.contains('in'))start();\n"
    "      else{var mo=new MutationObserver(function(){if(eb.classList.contains('in')){mo.disconnect();start();}});mo.observe(eb,{attributes:true,attributeFilter:['class']});}\n"
    "    }\n"
    "    setTimeout(start,eb?5000:2500);\n"
    "  }\n"
)
JS_GLOW = (
    "  /* подсветка рамки карточек за курсором — как у .card на главной */\n"
    "  if(fine)document.addEventListener('pointermove',function(e){\n"
    "    var c=e.target.closest&&e.target.closest('" + GLOW_SEL + "');if(!c)return;\n"
    "    var r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px');\n"
    "  },{passive:true});\n"
)


def _script(lit):
    return ('<script data-fx>\n'
            '/* Эффекты под курсором, как на главной (tools/site/fx.py) */\n'
            '(function(){\n'
            '  var mm=window.matchMedia;if(!mm)return;\n'
            "  var fine=mm('(hover: hover) and (pointer: fine)').matches;\n"
            + (JS_LIT if lit else '') + JS_GLOW +
            '})();\n'
            '</script>\n')


STYLE_RE = re.compile(r'<style data-fx>.*?</style>\n', re.S)
SCRIPT_RE = re.compile(r'<script data-fx>.*?</script>\n', re.S)
LIT_RE = re.compile(r'<div class="fx-lit" aria-hidden="true"><picture>.*?</picture></div>', re.S)
LOADER_MARK = '<script>\n  /* скрипты анимаций подключаются сразу после первой отрисовки'
HERO_RE = re.compile(r'<section class="[^"]*\b(?:d-hero|f-hero)\b[^"]*" id="hero">.*?</section>', re.S)
HERO_PIC_RE = re.compile(r'(<div class="(?:d-hero-media|hero-media)"[^>]*>\s*)'
                         r'(<picture>(?:(?!</picture>).)*?class="(?:d-hero-img|f-hero-img)\b[^"]*"(?:(?!</picture>).)*?</picture>)', re.S)


def lit_layer(pic):
    """Копия <picture> первого экрана для слоя фонаря: без id, без приоритета загрузки, с пустым alt."""
    c = re.sub(r'\s(?:id|fetchpriority|loading)="[^"]*"', '', pic)
    c = re.sub(r'\salt="[^"]*"', ' alt=""', c)
    c = re.sub(r'(<img\b[^>]*?class=")([^"]*)"', r'\1\2 fx-lit-img"', c, count=1)
    if 'decoding=' not in c:
        c = c.replace('<img ', '<img decoding="async" ', 1)
    return '<div class="fx-lit" aria-hidden="true">' + c + '</div>'


def data_attrs(s):
    """Атрибуты анимаций общего скрипта app.js, которых не хватало на внутренних страницах."""
    # форма заявки появляется так же, как на главной
    s = re.sub(r'<form class="form" id="form"((?:(?!data-form)[^>])*)>', r'<form class="form" id="form"\1 data-form>', s, count=1)
    # фото в карточках отраслей, кейсов и этапов — параллакс при прокрутке (размер фото под него задан в style.css)
    def par(m):
        img = m.group(2)
        if 'data-parallax' in img:
            return m.group(0)
        end = '/>' if img.endswith('/>') else '>'
        return m.group(1) + img[:-len(end)].rstrip() + ' data-parallax' + end
    s = re.sub(r'(<div class="(?:ind-img|case-img|tl-img)\b[^"]*"[^>]*>\s*(?:<picture>(?:(?!</picture>).)*?)?)(<img\b[^>]*>)', par, s, flags=re.S)
    # карточки отраслей с иконками на странице дезинфекции наклоняются за курсором, как карточки отраслей с фото
    s = re.sub(r'<article class="card dzf-ind([^"]*)"(?![^>]*data-tilt)', r'<article class="card dzf-ind\1" data-tilt', s)
    return s


def apply(s):
    """Возвращает (страница, сведения). Повторный запуск заменяет прежние вставки, не дублируя их."""
    info = {'lit': False, 'glow': True}
    s = STYLE_RE.sub('', s)
    s = SCRIPT_RE.sub('', s)
    s = LIT_RE.sub('', s)
    s = data_attrs(s)
    own_lit = 'id="heroLit"' in s or 'id="vLit"' in s  # главная и вентиляция — со своим фонарём и подсветкой
    if own_lit:
        return s, {'lit': False, 'glow': False, 'own': True}
    m = HERO_RE.search(s)
    if m:
        hero = m.group(0)
        pm = HERO_PIC_RE.search(hero)
        if pm:
            hero2 = hero[:pm.end(2)] + lit_layer(pm.group(2)) + hero[pm.end(2):]
            s = s[:m.start()] + hero2 + s[m.end():]
            info['lit'] = True
    css = CSS_GLOW + (CSS_LIT if info['lit'] else '')
    # в конец <head>, после стилей страницы: сборщики отраслевых страниц берут стили шаблона от первого <style> до первого </style>
    assert s.count('</head>') == 1, 'нет </head>'
    s = s.replace('</head>', '<style data-fx>\n' + css + '</style>\n</head>', 1)
    i = s.find(LOADER_MARK)
    assert i > 0, 'нет скрипта-загрузчика анимаций'
    s = s[:i] + _script(info['lit']) + s[i:]
    return s, info


if __name__ == '__main__':
    import sys
    for p in sys.argv[1:]:
        t = open(p, encoding='utf-8').read()
        t2, inf = apply(t)
        open(p, 'w', encoding='utf-8').write(t2)
        print(p, inf)
