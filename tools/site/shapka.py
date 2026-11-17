#!/usr/bin/env python3
"""Компактная закреплённая шапка (17.11.2026): одни и те же правки для исходников репозитория и для файлов, снятых
с рабочего сайта (пакет tools/deploy/prepare-2026-11-17-shapka.py).

    python3 tools/site/shapka.py --check   # исходники и страницы репозитория: новая шапка, версия ?v=20261117shapka

Решение владельца 17.11.2026 после разбора удобства 13.11.2026 («Юзабилити и закреплённая шапка»): «Внеси изменения
и выложи на сайт».
  * Компьютер и планшет (шире 760 px и выше 500 px): шапка всегда на месте; после 30 px прокрутки — компактная: 64 px
    (от 1281 px), 60 px (761–1280 px), фон rgba(9,9,11,.94) вместо rgba(0,0,0,.72).
  * Телефон (до 760 px) и низкое окно (до 500 px): компактная 56 px; уходит после 48 px прокрутки вниз подряд (дальше
    400 px от начала), возвращается после 24 px вверх с любой скоростью, в первых 120 px видна всегда.
  * Отступ при переходе к блоку и для фокуса клавиатуры (scroll-padding-top, переход к блоку под шапку от 13.11.2026,
    на сайте с 17.11.2026) — от высоты компактной шапки: --hdr-c + 1 px + 20…32 px вместо полной высоты шапки;
    так же считает window.pcAnchor в app.js.
  * Прокрутка к блоку по ссылке — 0,8 с вместо 1,5 с; выпадающие списки шапки открываются наведением через 0,15 с.
Счётчики, телефон, почта, тексты и меню не меняются (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py).

Для рабочего сайта (prepare-2026-11-17-shapka.py; сайт после выкладки «переход к блоку под шапку», ?v=20261117zagolovok):
  style_edits(css)      — точные замены в style.css сайта (те же, что в style.css репозитория);
  home_css_edits(s)     — те же замены во встроенных стилях главной (сжатых esbuild, как их встраивает tools/build.py);
  js_edits(js)          — точные замены в app.min.js сайта: обработчик прокрутки шапки, высота компактной шапки
                          в window.pcAnchor, 0,8 с у прокрутки к блоку;
  page_edits(s)         — версия ?v= у style.css и app.min.js (кэш браузера на год; у legal.css — прежняя) и на главной —
                          встроенные стили.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OLD_V, NEW_V = '20261117zagolovok', '20261117shapka'  # на сайте; в репозитории было 20261115lupa
REPO_OLD_V = '20261115lupa'
ESBUILD = ['npx', '--yes', 'esbuild@0.24.2']

# ---------------------------------------------------------------- style.css: шапка (одинаково в репозитории и на сайте)
HDR_OLD = """.hdr{position:fixed;inset:0 0 auto;z-index:50;transition:background .4s,backdrop-filter .4s,border-color .4s,transform .5s var(--ease);border-bottom:1px solid transparent}
.hdr.scrolled{background:rgba(0,0,0,.72);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-color:var(--line)}
.hdr.hide{transform:translateY(-100%)}
.hdr .wrap{display:flex;align-items:center;justify-content:space-between;height:clamp(68px,6vw,115px);gap:24px}
"""
HDR_NEW = """.hdr{position:fixed;inset:0 0 auto;z-index:50;transition:background .4s,backdrop-filter .4s,border-color .4s,transform .35s var(--ease);border-bottom:1px solid transparent}
.hdr.scrolled{background:rgba(9,9,11,.94);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-color:var(--line)}
.hdr.hide{transform:translateY(-100%)}
.hdr .wrap{display:flex;align-items:center;justify-content:space-between;height:clamp(68px,6vw,115px);gap:24px;transition:height .3s var(--ease)}
/* компактная шапка (17.11.2026, решение владельца после разбора удобства 13.11): после 30 px прокрутки (класс scrolled,
   app.js) шапка 64 px на компьютере, 60 px до 1280 px и 56 px на телефоне (--hdr-c), фон плотнее — текст страницы
   под ней не просвечивает. На компьютере и планшете шапка больше не уезжает; на телефоне и в низком окне (до 500 px)
   уходит при чтении вниз и возвращается при прокрутке вверх (app.js, раздел «шапка, прогресс…»). Кнопки на телефоне
   и планшете не уменьшаются: их размер — для пальца. Было: шапка в полный рост (до 116 px) уезжала на всех экранах */
:root{--hdr-c:64px}
.hdr .logo-mark{transition:border-color .4s,transform .6s var(--ease),width .3s var(--ease),height .3s var(--ease)}
.hdr .logo-name,.hdr .logo-sub,.hdr .phone{transition:font-size .3s var(--ease)}
.hdr .nav>a,.hdr .nav-dd-btn{transition:color .25s,font-size .3s var(--ease)}
.hdr .phone::before{transition:transform .4s var(--ease),width .3s var(--ease),height .3s var(--ease)}
.hdr .phone::after{transition:width .3s var(--ease),height .3s var(--ease),margin-top .3s var(--ease)}
.hdr .btn-sm{transition:color .45s var(--ease),border-color .45s var(--ease),box-shadow .45s var(--ease),height .3s var(--ease),padding .3s var(--ease),font-size .3s var(--ease)}
.hdr.scrolled .wrap{height:var(--hdr-c)}
@media (min-width:761px){
  .hdr.scrolled .logo-mark{width:36px;height:36px}
  .hdr.scrolled .logo-name{font-size:clamp(17px,1.45vw,19px)}
  .hdr.scrolled .logo-sub{font-size:clamp(10px,.75vw,11px)}
  .hdr.scrolled .nav>a,.hdr.scrolled .nav-dd-btn{font-size:clamp(14px,1.05vw,15px)}
  .hdr.scrolled .phone{font-size:clamp(14px,1vw,15px)}
  .hdr.scrolled .phone::before,.hdr.scrolled .phone::after{width:32px;height:32px}
  .hdr.scrolled .phone::after{margin-top:-16px}
  .hdr.scrolled .btn-sm{height:40px;padding:0 20px;font-size:clamp(14px,1.05vw,15px)}
  .hdr.scrolled .nav-dd-panel{margin-top:10px}
}
@media (max-width:1280px){:root{--hdr-c:60px}}
@media (max-width:760px){:root{--hdr-c:56px}.hdr.scrolled .logo-mark{width:34px;height:34px}}
"""
DD_OLD = ("  .nav-dd:not(.nohover):hover .nav-dd-panel{opacity:1;visibility:visible;transform:translate(-50%,0);"
          "transition:opacity .2s linear,transform .45s var(--ease)}\n")
DD_NEW = ("  /* наведение открывает список через 0,15 с: мышь по пути к вкладкам браузера не раскрывает его случайно (17.11.2026) */\n"
          "  .nav-dd:not(.nohover):hover .nav-dd-panel{opacity:1;visibility:visible;transform:translate(-50%,0);"
          "transition:opacity .2s linear .15s,transform .45s var(--ease) .15s,visibility 0s .15s}\n")
# отступ сверху (переход к блоку под шапку, 13.11.2026): от высоты компактной шапки, а не полной
SP_OLD = """/* переход к блоку по якорю (13.11.2026): начало блока — сразу под шапкой. Отступ сверху — высота шапки (.hdr .wrap
   и линия 1 px) и ещё 20…32 px; у разделов вычитается их собственный верхний отступ (и линия-разделитель), поэтому
   под шапку встаёт подпись над заголовком. Так же считает app.js (раздел «переход к блоку по якорю»). Было: верх
   раздела на 96 px от верха окна, и над подписью оставалось 180–200 px пустого тёмного поля */
html{scroll-behavior:smooth;scroll-padding-top:calc(clamp(68px,6vw,115px) + 1px + clamp(20px,2.2vw,32px))}
"""
SP_NEW = """/* переход к блоку по якорю (13.11.2026): начало блока — сразу под шапкой. Отступ сверху — высота компактной шапки
   (--hdr-c и линия 1 px; после прокрутки шапка компактная, 17.11.2026) и ещё 20…32 px; у разделов вычитается их
   собственный верхний отступ (и линия-разделитель), поэтому под шапку встаёт подпись над заголовком. Тот же отступ
   держит фокус клавиатуры ниже шапки. Так же считает app.js (раздел «переход к блоку по якорю»). Было: верх
   раздела на 96 px от верха окна, и над подписью оставалось 180–200 px пустого тёмного поля */
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--hdr-c) + 1px + clamp(20px,2.2vw,32px))}
"""
SP_REPO_NEW = SP_NEW.split('\n')[-2] + '\n'
CSS_PAIRS_LIVE = [(SP_OLD, SP_NEW), (HDR_OLD, HDR_NEW), (DD_OLD, DD_NEW)]

# ---------------------------------------------------------------- app.min.js рабочего сайта: точные замены
# Имена в сжатом файле сайта: S — #hdr, Y — меню открыто, Z — прошлое положение прокрутки, kt — обработчик прокрутки,
# e — «наверх» в scrollToEl; в разделе «переход к блоку по якорю» (сжат отдельно): t — window, B — <html>, a — #hdr,
# d — anchorY, w — плавность, r — Lenis, o — «уменьшение движения». Новые переменные — с приставкой __pch (их нет
# в файле). Те же правки, что в app.js (esbuild даёт тот же код с другими именами).
JS_PAIRS = [
    # шапка: на компьютере не уезжает, на телефоне и в низком окне — после 48 px вниз, возвращается после 24 px вверх
    ('Z=0,kt=function(t){S.classList.toggle("scrolled",t>30),S.classList.contains("hold")?S.classList.remove("hide"):'
     'Y||(t>Z+4&&t>500?S.classList.add("hide"):(t<Z-4||t<200)&&S.classList.remove("hide")),Z=t;var e=',
     'Z=scrollY,__pchr=0,__pchm=matchMedia("(max-width: 760px), (max-height: 500px)"),kt=function(t){var __pchd=t-Z;Z=t,'
     'S.classList.toggle("scrolled",t>30),Y||t<120||!__pchm.matches||S.classList.contains("hold")?(S.classList.remove("hide"),'
     '__pchr=0):__pchd&&(__pchd>0!=__pchr>0&&(__pchr=0),__pchr+=__pchd,__pchr>48&&t>400?S.classList.add("hide"):__pchr<-24&&'
     'S.classList.remove("hide"));var e='),
    (',kt(scrollY),S.addEventListener("focusin",function(){S.classList.remove("hide")});',
     ',kt(scrollY);var __pchf=function(){kt(scrollY)};__pchm.addEventListener?__pchm.addEventListener("change",__pchf):'
     '__pchm.addListener&&__pchm.addListener(__pchf),S.addEventListener("focusin",function(){S.classList.remove("hide"),__pchr=0});'),
    # прокрутка к блоку без window.pcAnchor — 0,8 с
    ('{offset:e?0:-80,duration:1.5,', '{offset:e?0:-80,duration:.8,'),
    # window.pcAnchor: высота шапки на месте прихода — компактная (--hdr-c), у самого начала страницы — полная
    ('E=0,p=0,d=function(e){',
     'E=0,p=0,__pchH=function(e){if(!a)return 0;var n=parseFloat(getComputedStyle(B).getPropertyValue("--hdr-c"));'
     'return e&&n?n+1:Math.min(115,Math.max(68,t.innerWidth*.06))+1},d=function(e){'),
    ('var h=(a?a.getBoundingClientRect().height:0)+Math.min(32,Math.max(20,t.innerWidth*.022));'
     'return Math.max(0,Math.min(Math.round(n+t.pageYOffset-h),B.scrollHeight-t.innerHeight))}',
     'var h=Math.min(32,Math.max(20,t.innerWidth*.022)),__pcha=n+t.pageYOffset,__pchy=__pcha-__pchH(!0)-h;'
     'return __pchy<=30&&(__pchy=__pcha-__pchH(!1)-h),Math.max(0,Math.min(Math.round(__pchy),B.scrollHeight-t.innerHeight))}'),
    # window.pcAnchor: Lenis за 0,8 с вместо 1,5 с
    ('r?r.scrollTo(0,{duration:1.5,easing:w}):g(0,!o)', 'r?r.scrollTo(0,{duration:.8,easing:w}):g(0,!o)'),
    ('r.scrollTo(d(e),{duration:1.5,easing:w,onComplete:h})', 'r.scrollTo(d(e),{duration:.8,easing:w,onComplete:h})'),
]
# версия у style.css и app.min.js на страницах сайта (у legal.css — прежняя: legal.css не меняется)
VERSION_PAIRS = [('app.min.js?v=' + OLD_V, 'app.min.js?v=' + NEW_V), ('style.css?v=' + OLD_V, 'style.css?v=' + NEW_V)]

def esbuild_css(code):
    res = subprocess.run(ESBUILD + ['--minify', '--loader=css', '--charset=utf8', '--log-level=warning'],
                         input=code, capture_output=True, text=True, cwd=str(ROOT))
    if res.returncode:
        sys.exit('esbuild: ' + res.stderr)
    return res.stdout.strip()


def _dd_rule(s):
    return s.strip().split('\n')[-1].strip()  # правило без пояснения (во встроенных стилях пояснений нет)


def home_css_pairs():
    """Те же замены в стилях, сжатых esbuild (встроенные стили главной)."""
    pairs = [(esbuild_css(a), esbuild_css(b)) for a, b in ((SP_OLD, SP_NEW), (HDR_OLD, HDR_NEW),
                                                          (_dd_rule(DD_OLD), _dd_rule(DD_NEW)))]
    for a, b in pairs:
        assert a and b and a != b and '\n' not in a, (a[:60], b[:60])
    return pairs


def _edits(s, pairs, what):
    out = []
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, '%s: «%s» найдено %d раз' % (what, a[:70], n)
        out.append([a, b, 1])
    return out


def style_edits(css):
    return _edits(css, CSS_PAIRS_LIVE, 'style.css')


def js_edits(js):
    for name in ('__pchr', '__pchm', '__pchd', '__pchf', '__pchH', '__pcha', '__pchy'):
        assert name not in js, 'app.min.js: имя %s уже занято' % name
    return _edits(js, JS_PAIRS, 'app.min.js')


def page_edits(s, home_pairs=None):
    """Замены для страницы сайта (index.php): версия ?v= у style.css и app.min.js; у главной — встроенные стили."""
    edits = []
    for a, b in VERSION_PAIRS:
        n = s.count(a)
        if n:
            edits.append([a, b, n])
    assert edits and edits[0][0].startswith('app.min.js') and edits[0][2] in (1, 2), 'нет ссылки на app.min.js?v=' + OLD_V
    left = re.findall(r'(?:style\.css|app\.min\.js)\?v=(?!' + NEW_V + ')[a-z0-9]+', apply(s, edits))
    assert not left, 'остались ссылки с другой версией: %s' % left
    if '<!-- style:start -->' in s:
        assert home_pairs, 'главная: нужны замены встроенных стилей'
        assert 'style.css?v=' not in s, 'главная: style.css встроен, отдельной ссылки быть не должно'
        block = re.search(r'<!-- style:start --><style>(.*?)</style><!-- style:end -->', s, re.S).group(1)
        for e in _edits(block, home_pairs, 'встроенные стили главной'):
            assert s.count(e[0]) == 1, 'главная: замена встречается вне встроенных стилей'
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


def check_repo():
    """Исходники репозитория уже с новой шапкой: style.css, app.js (и app.min.js из него), главная, версия на страницах."""
    probs = []
    css = (ROOT / 'style.css').read_text(encoding='utf-8')
    for name, x in (('шапка', HDR_NEW), ('выпадающий список', DD_NEW), ('отступ сверху', SP_REPO_NEW)):
        if css.count(x) != 1:
            probs.append('style.css: нет нового правила «%s»' % name)
    for x in (HDR_OLD, DD_OLD, SP_OLD):
        if x in css:
            probs.append('style.css: осталось прежнее правило ' + x[:50])
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    for x in ("var awayMq = matchMedia('(max-width: 760px), (max-height: 500px)');", 'if (run > 48 && y > 400)',
              "duration: 0.8", "var hdrH = function (compact) {"):
        if x not in js:
            probs.append('app.js: нет «%s»' % x)
    if 'duration: 1.5, easing: ease' in js or "offset: isTop ? 0 : -80, duration: 1.5" in js:
        probs.append('app.js: осталась прокрутка к блоку за 1,5 с')
    mjs = (ROOT / 'app.min.js').read_text(encoding='utf-8')
    if 'matchMedia("(max-width: 760px), (max-height: 500px)")' not in mjs:
        probs.append('app.min.js не собран из нового app.js (python3 tools/build.py)')
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    if '.hdr.scrolled .wrap{height:var(--hdr-c)}' not in home:
        probs.append('index.html: встроенные стили без компактной шапки (python3 tools/build.py)')
    pages = 0
    for p in sorted(ROOT.rglob('index.html')):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(('tools/', 'dist/', 'node_modules/', 'vendor/', 'server/', 'preview-')):
            continue  # превью — свои версии
        s = p.read_text(encoding='utf-8')
        if re.search(r'(?:style\.css|app\.min\.js)\?v=(?!' + NEW_V + ')', s):
            probs.append(rel + ': версия style.css или app.min.js не ' + NEW_V)
        pages += 1
    return probs, pages


if __name__ == '__main__':
    if sys.argv[1:] != ['--check']:
        sys.exit(__doc__)
    probs, pages = check_repo()
    for x in probs:
        print('НЕТ', x)
    print('shapka: %s (%d страниц)' % ('нарушений нет' if not probs else 'нарушений %d' % len(probs), pages))
    sys.exit(1 if probs else 0)
