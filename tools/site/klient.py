#!/usr/bin/env python3
"""Правки для клиента и снятие затемнения на внутренних страницах телефона (18.11.2026): точные замены для файлов,
снятых с рабочего сайта (пакет tools/deploy/prepare-2026-11-18-klient.py).

Решение владельца 18.11.2026: «На Timeweb выкладывай правки для клиента. В тот же пакет добавь снятие затемнения
на внутренних страницах для телефона». Сайт до выкладки — после «компактной шапки» (17.11.2026, ?v=20261117shapka).
  * style.css (телефон, до 760 px) — те же правила, что в style.css репозитория (коммиты 163080d и fa5641c):
    фон блока заявки (.cta-bg) не показывается, заливка фото этапов (.tl-img::after) выключена, слова [data-scrub]
    без приглушения, первый экран главной — светлое фото полосой (главная так уже на сайте с 17.11.2026 01:59, во
    встроенных стилях); зона нажатия «Подробнее…» (.pest-more, .hz-more) — не меньше 44 px.
    Не входит: правило data-fp (параллакс фото с людьми, 11.11.2026) — его на сайт не выкладывали.
  * app.min.js — точные замены, повторяющие app.js репозитория: на телефоне [data-scrub] не приглушает слова;
    после отправки заявки «Заявка отправлена» — посередине экрана (__pcok вместо classList.add("sent") и refresh);
    после перехода по якорю анимации появления на экране доводятся до конца (__pcfin в window.pcAnchor).
  * все страницы — ?v=20261117shapka -> ?v=20261118klient у style.css и app.min.js (legal.css — прежняя);
    на главной в блоке стилей hero-scroll-st — только зона нажатия «Подробнее» (остальное там уже есть).
Счётчики, телефон, почта, тексты и меню не меняются (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py).
"""
import re

OLD_V, NEW_V = '20261117shapka', '20261118klient'
CSS_PAIRS = [('  .hero-bg{background-image:url(img/hero-m-dim.webp)}\n  .hero::before{background:linear-gradient(180deg,rgba(9,9,11,.5),rgba(9,9,11,.82) 60%,#000)}\n', '  /* Закон владельца (17.11.2026): на телефоне ничего не затемнять — ни фото, ни текст. Фото первого экрана главной —\n     светлое, полосой над текстом, как на страницах отраслей (снизу — тот же переход в чёрный фон); тёмной заливки\n     поверх фото нет. Затемнённый фон блока заявки и тёмная заливка фото этапов на телефоне не показываются. */\n  .hero-bg{background-image:url(img/hero-m.webp);background-position:50% 42%}\n  .hero::before{display:none}\n  #hero.hero:not(.f-hero){display:block}\n  html #hero.hero:not(.f-hero){padding-top:68px}\n  #hero.hero:not(.f-hero) .hero-media{position:relative;inset:auto;width:100%;height:clamp(104px,calc(100vh - 480px),62vw);height:clamp(104px,calc(100svh - 480px),62vw);overflow:hidden}\n  #hero.hero:not(.f-hero) .hero-media::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 62%,#000 100%);pointer-events:none}\n  #hero.hero:not(.f-hero) .wrap{margin-top:-24px}\n  .tl-img::after{display:none}\n  [data-scrub] .sw{opacity:1!important}\n'), ('  .cta-bg{background-image:url(img/cta-m.webp)}\n', '  .cta-bg{display:none}\n'), ('@media (max-width:760px){#hero.hero:not(.f-hero){padding-bottom:32px}}\n', '@media (max-width:760px){#hero.hero:not(.f-hero){padding-bottom:32px}}\n/* очень низкий экран телефона (до 520 px по высоте): полосы фото нет, как на страницах отраслей */\n@media (max-width:760px) and (max-height:520px){#hero.hero:not(.f-hero) .hero-media{display:none}html #hero.hero:not(.f-hero){padding-top:92px}#hero.hero:not(.f-hero) .wrap{margin-top:0}}\n/* зона нажатия ссылок «Подробнее…» на телефоне — не меньше 44 px (было 18 и 31 px), вид и раскладка прежние (17.11.2026) */\n@media (max-width:760px){.pest-more,.hz-more{position:relative}.pest-more::after,.hz-more::after{content:"";position:absolute;inset:-13px -8px}.hz-more::after{inset:-7px -8px}}\n')]
HOME_CSS_PAIRS = [('@media (max-width:760px) and (max-height:520px){#hero.hero:not(.f-hero) .hero-media{display:none}html #hero.hero:not(.f-hero){padding-top:92px}#hero.hero:not(.f-hero) .wrap{margin-top:0}}',
                   '@media (max-width:760px) and (max-height:520px){#hero.hero:not(.f-hero) .hero-media{display:none}html #hero.hero:not(.f-hero){padding-top:92px}#hero.hero:not(.f-hero) .wrap{margin-top:0}}'
                   '@media (max-width:760px){.pest-more,.hz-more{position:relative}.pest-more:after,.hz-more:after{content:"";position:absolute;inset:-13px -8px}.hz-more:after{inset:-7px -8px}}')]
JS_PAIRS = [(';T.addEventListener("submit",function(t){', ';var __pcok=function(){T.classList.add("sent"),tt();var e=a(".ok",T);if(e){var o=e.getBoundingClientRect(),r=innerHeight,n=(S?S.getBoundingClientRect().height:0)+16;if(o.top<n||o.bottom>r-16){var f=Math.max(0,Math.round(pageYOffset+o.top-Math.max(n,(r-o.height)/2)));d?d.scrollTo(f,{duration:D?0:.9,immediate:D,force:!0}):window.scrollTo({top:f,behavior:D?"auto":"smooth"})}e.setAttribute("tabindex","-1");try{e.focus({preventScroll:!0})}catch(s){}}};T.addEventListener("submit",function(t){'), ('setTimeout(function(){T.classList.add("sent"),tt()},700)', 'setTimeout(__pcok,700)'), ('T.classList.add("sent"),tt()}).catch(', '__pcok()}).catch('), ('i("[data-scrub]").forEach(function(t){Yt(t,!0),gsap.fromTo(', 'i("[data-scrub]").forEach(function(t){if(Yt(t,!0),matchMedia("(max-width: 760px)").matches)return;gsap.fromTo('), ('(function(){var t=window,i=document,B=i.documentElement,a=i.getElementById("hdr"),E=0,p=0,', '(function(){var t=window,i=document,B=i.documentElement,a=i.getElementById("hdr"),E=0,p=0,__pcfin=function(){var e=t.gsap;if(e&&e.globalTimeline){var n=t.innerHeight;e.globalTimeline.getChildren(!1,!0,!1).forEach(function(r){r.progress()>=1||r.repeat()||r.scrollTrigger&&r.scrollTrigger.vars&&r.scrollTrigger.vars.scrub||r.targets().some(function(o){if(!o||!o.getBoundingClientRect)return!1;var f=o.getBoundingClientRect();return f.bottom>0&&f.top<n})&&r.progress(1)})}},'), ('(r?r.scrollTo(y,{immediate:!0}):g(y,!1)),setTimeout(function(){f===p&&s(!1)},150)', '(r?r.scrollTo(y,{immediate:!0}):g(y,!1)),__pcfin(),setTimeout(__pcfin,300),setTimeout(function(){f===p&&s(!1)},150)'), ('[300,1e3,2e3].forEach(function(e){setTimeout(l,e)}),setTimeout(C,2500)', '[300,1e3,2e3].forEach(function(e){setTimeout(l,e)}),[300,1e3].forEach(function(e){setTimeout(function(){T||__pcfin()},e)}),setTimeout(C,2500)')]
VERSION_PAIRS = [('app.min.js?v=' + OLD_V, 'app.min.js?v=' + NEW_V), ('style.css?v=' + OLD_V, 'style.css?v=' + NEW_V)]


def _edits(s, pairs, what):
    out = []
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, '%s: «%s» найдено %d раз' % (what, a[:70], n)
        out.append([a, b, 1])
    return out


def style_edits(css):
    return _edits(css, CSS_PAIRS, 'style.css')


def js_edits(js):
    for name in ('__pcok', '__pcfin'):
        assert name not in js, 'app.min.js: имя %s уже занято' % name
    return _edits(js, JS_PAIRS, 'app.min.js')


def page_edits(s):
    edits = []
    for a, b in VERSION_PAIRS:
        n = s.count(a)
        if n:
            edits.append([a, b, n])
    assert edits and edits[0][0].startswith('app.min.js') and edits[0][2] in (1, 2), 'нет ссылки на app.min.js?v=' + OLD_V
    left = re.findall(r'(?:style\.css|app\.min\.js)\?v=(?!' + NEW_V + ')[a-z0-9]+', apply(s, edits))
    assert not left, 'остались ссылки с другой версией: %s' % left
    if '<!-- style:start -->' in s:
        assert 'style.css?v=' not in s, 'главная: style.css встроен'
        # стили хвоста главной — в блоке <style id="hero-scroll-st"> после встроенного style.css (как на сайте)
        block = re.search(r'<style id="hero-scroll-st">(.*?)</style>', s, re.S).group(1)
        for e in _edits(block, HOME_CSS_PAIRS, 'стили главной (hero-scroll-st)'):
            assert s.count(e[0]) == 1, 'главная: замена встречается вне блока стилей'
            edits.append(e)
    else:
        assert len(edits) == 2, 'внутренняя страница: нужны ссылки и на style.css, и на app.min.js'
    return edits


def apply(s, edits):
    out = s
    for a, b, c in edits:
        assert out.count(a) == c, 'число совпадений изменилось: ' + a[:60]
        out = out.replace(a, b)
    return out


def revert(s, edits):
    out = s
    for a, b, c in reversed(edits):
        assert out.count(b) == c, 'обратная замена: ' + b[:60]
        out = out.replace(b, a)
    return out
