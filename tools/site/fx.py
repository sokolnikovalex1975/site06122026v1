#!/usr/bin/env python3
"""Эффекты под курсором, как на главной, для внутренних страниц сайта (повторный запуск ничего не дублирует).

  * лупа на фото первого экрана (.d-hero и .f-hero, с 15.11.2026 — «лёгкая», как на главной): вне круга фото приглушено,
    в круге — в полную яркость; круг следует за мышью, без мыши стоит на открытой части фото и сам не ходит. Круг —
    блок с неподвижной маской, скрипт только сдвигает его и копию фото внутри (transform). Копия — тот же <picture>
    с теми же адресами, фото не скачивается второй раз. Только компьютер с мышью шире 860 px; при «уменьшить движение»
    и в облегчённом режиме (класс lowfx, window.pcFx) лупы нет и фото не приглушается;
  * подсветка рамки информационных карточек за курсором (как у .card на главной) — только мышь, на телефоне нет;
  * плавное появление формы заявки (data-form), если его не было;
  * лёгкий параллакс фото в карточках отраслей, кейсов и этапов (data-parallax), как на главной;
  * наклон карточек отраслей с иконками на странице дезинфекции (data-tilt), как у карточек отраслей.

Главная (#heroLens) и страница вентиляции (#vLit) уже содержат свою лупу — лупа на них не добавляется.
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
    '/* лупа на фото первого экрана — как на главной (tools/site/fx.py, с 15.11.2026): светлая копия фото в неподвижной\n'
    '   круглой маске; скрипт только сдвигает круг и фото внутри него (transform), фильтры и маска не пересчитываются.\n'
    '   Только компьютер с мышью шире 860 px; на телефонах, планшетах и в облегчённом режиме (lowfx) — обычное фото */\n'
    '.fx-lit{position:absolute;left:0;top:0;width:0;height:0;opacity:0;pointer-events:none;contain:strict;will-change:transform,opacity;'
    '-webkit-mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62.5%,transparent 100%);'
    'mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62.5%,transparent 100%);'
    '-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;transition:opacity 1.8s cubic-bezier(.16,1,.3,1)}\n'
    '.fx-lit-in{position:absolute;left:0;top:0;will-change:transform}\n'
    '.fx-lit img{filter:brightness(1.08) contrast(1.06) saturate(1.06)}\n'
    '#hero :is(.d-hero-media,.hero-media)>picture>img{transition:filter 1.8s cubic-bezier(.16,1,.3,1)}\n'
    '#hero.fx-lit-on :is(.d-hero-media,.hero-media)>picture>img{filter:grayscale(.3) brightness(.56)}\n'
    '#hero.fx-lit-on .fx-lit{opacity:1}\n'
    '.lowfx #hero :is(.d-hero-media,.hero-media)>picture>img{transition:none}\n'
    '@media (max-width:860px),(hover:none),(pointer:coarse){.fx-lit{display:none}}\n'
)

JS_LIT = (
    "  /* лупа: светлая копия фото в круглой маске; сдвигаются только круг и фото внутри него (transform) — без перерисовки фото.\n"
    "     Кадры — только пока круг догоняет мышь; без мыши круг стоит на открытой части фото и сам не ходит, мышь ушла с первого\n"
    "     экрана — плавно возвращается. Только компьютер с мышью шире 860 px; без лупы — при «уменьшить движение» и в облегчённом\n"
    "     режиме (window.pcFx, скрипт в <head>): если, пока круг догоняет мышь, кадров меньше 40 в секунду, режим включается сам */\n"
    "  var hero=document.getElementById('hero'),lit=hero&&hero.querySelector('.fx-lit'),F=window.pcFx||{mode:'',lite:false,hooks:[],set:function(){}};\n"
    "  if(lit&&lit.firstElementChild&&fine&&!F.lite&&!mm('(prefers-reduced-motion: reduce)').matches&&!mm('(max-width:860px)').matches){\n"
    "    var media=lit.parentNode,box=lit.firstElementChild,full=hero.classList.contains('f-hero');\n"
    "    var W=0,H=0,r=0,x=0,y=0,tx=0,ty=0,hx=0,hy=0,raf=0,last=0,vis=true,on=false,follow=false,off=false,dts=[];\n"
    "    var place=function(){ /* круг и копия фото — ровно навстречу: копия стоит на месте фото до долей пикселя */\n"
    "      var X=Math.round((x-r)*10)/10,Y=Math.round((y-r)*10)/10;\n"
    "      lit.style.transform='translate3d('+X+'px,'+Y+'px,0)';box.style.transform='translate3d('+(-X)+'px,'+(-Y)+'px,0)';\n"
    "    };\n"
    "    var size=function(){\n"
    "      if(off)return;var cs=getComputedStyle(media);W=parseFloat(cs.width)||media.offsetWidth;H=parseFloat(cs.height)||media.offsetHeight; /* точный размер: копия совпадает с фото */\n"
    "      r=Math.round(Math.max(240,Math.min(400,innerWidth*.21))*.72);\n"
    "      lit.style.width=lit.style.height=2*r+'px';box.style.width=W+'px';box.style.height=H+'px';\n"
    "      hx=W*(full?.68:.74);hy=H*.47;if(!follow){tx=hx;ty=hy;if(!raf){x=hx;y=hy;}}place();\n"
    "    };\n"
    "    var frame=function(now){\n"
    "      raf=0;if(off||!vis||document.hidden)return;\n"
    "      var dt=last?Math.min(Math.max(now-last,0),100):16.67;\n"
    "      if(last&&F.mode!=='full'){dts.push(now-last);if(dts.length>=40){dts.sort(function(a,b){return a-b;});var med=dts[20];dts=[];\n"
    "        if(med>25){document.documentElement.setAttribute('data-fps',Math.round(1000/med));F.set(true);return;}}}\n"
    "      last=now;var k=1-Math.pow(.94,dt/16.67);x+=(tx-x)*k;y+=(ty-y)*k;\n"
    "      if(Math.abs(tx-x)<.3&&Math.abs(ty-y)<.3){x=tx;y=ty;place();return;}\n"
    "      place();raf=requestAnimationFrame(frame);\n"
    "    };\n"
    "    var kick=function(){if(!raf&&!off&&vis&&!document.hidden){last=0;raf=requestAnimationFrame(frame);}};\n"
    "    hero.addEventListener('pointermove',function(e){\n"
    "      if(e.pointerType!=='mouse'||off)return;var b=media.getBoundingClientRect();if(!b.width||!b.height)return;\n"
    "      tx=(e.clientX-b.left)/b.width*W;ty=(e.clientY-b.top)/b.height*H;follow=true;kick();\n"
    "    },{passive:true});\n"
    "    hero.addEventListener('pointerleave',function(){if(off)return;follow=false;tx=hx;ty=hy;kick();});\n"
    "    if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;kick();}).observe(hero);\n"
    "    document.addEventListener('visibilitychange',kick);\n"
    "    if(window.ResizeObserver)new ResizeObserver(function(){size();}).observe(media);\n"
    "    addEventListener('resize',size);size();\n"
    "    var start=function(){if(on||off)return;on=true;hero.classList.add('fx-lit-on');};\n"
    "    F.hooks.push(function(){off=true;if(raf)cancelAnimationFrame(raf);raf=0;hero.classList.remove('fx-lit-on');});\n"
    "    var eb=hero.querySelector('.eyebrow');\n"
    "    if(eb&&'MutationObserver' in window){\n"
    "      if(eb.classList.contains('in'))start();\n"
    "      else{var mo=new MutationObserver(function(){if(eb.classList.contains('in')){mo.disconnect();start();}});mo.observe(eb,{attributes:true,attributeFilter:['class']});}\n"
    "    }\n"
    "    setTimeout(start,eb?5000:2500);\n"
    "  }\n"
)
JS_GLOW = (
    "  /* подсветка рамки карточек за курсором — как у .card на главной; в облегчённом режиме (window.pcFx) — нет */\n"
    "  if(fine)document.addEventListener('pointermove',function(e){\n"
    "    if(window.pcFx&&pcFx.lite)return;var c=e.target.closest&&e.target.closest('" + GLOW_SEL + "');if(!c)return;\n"
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
# прежняя разметка (до 15.11.2026 — без обёртки .fx-lit-in) и нынешняя
LIT_RE = re.compile(r'<div class="fx-lit" aria-hidden="true">(?:<div class="fx-lit-in">)?<picture>.*?</picture>(?:</div>)?</div>', re.S)
LOADER_MARK = '<script>\n  /* скрипты анимаций подключаются сразу после первой отрисовки'
HERO_RE = re.compile(r'<section class="[^"]*\b(?:d-hero|f-hero)\b[^"]*" id="hero">.*?</section>', re.S)
HERO_PIC_RE = re.compile(r'(<div class="(?:d-hero-media|hero-media)"[^>]*>\s*)'
                         r'(<picture>(?:(?!</picture>).)*?class="(?:d-hero-img|f-hero-img)\b[^"]*"(?:(?!</picture>).)*?</picture>)', re.S)


def lit_layer(pic):
    """Копия <picture> первого экрана для лупы: без id, без приоритета загрузки, с пустым alt. Обёртка .fx-lit-in
    размером с фото сдвигается навстречу кругу — копия стоит ровно на месте фото (tools/site/focal.js кадрирует её так же)."""
    c = re.sub(r'\s(?:id|fetchpriority|loading)="[^"]*"', '', pic)
    c = re.sub(r'\salt="[^"]*"', ' alt=""', c)
    c = re.sub(r'(<img\b[^>]*?class=")([^"]*)"', r'\1\2 fx-lit-img"', c, count=1)
    if 'decoding=' not in c:
        c = c.replace('<img ', '<img decoding="async" ', 1)
    return '<div class="fx-lit" aria-hidden="true"><div class="fx-lit-in">' + c + '</div></div>'


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
    own_lit = any(k in s for k in ('id="heroLens"', 'id="heroLit"', 'id="vLit"'))  # главная и вентиляция — своя лупа и подсветка
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
