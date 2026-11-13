#!/usr/bin/env python3
"""Превью «лёгкой лупы» на первом экране главной — папка preview-lupa/ (13.11.2026).

    python3 preview-lupa/build_preview.py

Собирает превью заново из актуальных файлов корня репозитория (index.html, app.js, img/hero.webp, img/hero-m.webp).
Корневые файлы не меняются, в пакет для Timeweb (tools/site/build_prod.py) папка не входит. Счётчиков в превью нет,
как и на всём GitHub Pages: они ставятся только в версию для Timeweb.

Что меняется по сравнению с главной:
  1. Лупа — готовый светлый круг: светлое фото (img/hero-lit.webp) в круглой маске, которое только сдвигается
     (transform). Браузер не перерисовывает фото в каждом кадре, как сейчас, а лишь передвигает готовую картинку.
     Кадры считаются, только пока круг догоняет мышь. Без мыши круг стоит на открытой части фото над панелью
     «Что покажет бесплатный аудит» и сам не ходит — нагрузки нет. Мышь ушла с первого экрана — круг плавно
     возвращается на место. Размер, мягкий край и плавность — как сейчас.
  2. На телефонах и планшетах (нет мыши) лупы нет: фото первого экрана просто затемнено, как сейчас под лупой.
  3. Затемнённое фото (img/hero-dim.webp, img/hero-m-dim.webp) и светлое для лупы подготовлены заранее — в браузере
     фильтры grayscale/brightness/contrast больше не считаются.
  4. Страховка для слабых компьютеров: через 3 с после загрузки страница 2 с считает кадры, а потом — пока лупа догоняет
     мышь (по 40 кадров). Если кадров меньше 40 в секунду,
     включается облегчённый режим (класс lowfx): без лупы, «зерна», сканирующей линии, пульсаций, матового стекла,
     параллакса и размытия при появлении, курсор — обычный. Решение помнится до конца визита.
     Вручную: ?fx=lite — облегчённый режим, ?fx=full — полный, ?fx=auto — определить заново.
  5. Плашка превью внизу по центру (только на компьютере): какой режим включён и сколько кадров в секунду намерено.
"""
import pathlib
import re
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
VER = '20261113lupa'


def once(s, old, new, what):
    n = s.count(old)
    assert n == 1, f'{what}: ожидалось 1 совпадение, найдено {n}'
    return s.replace(old, new)


def once_re(s, pat, new, what, flags=0):
    out, n = re.subn(pat, new, s, flags=flags)
    assert n == 1, f'{what}: ожидалось 1 совпадение, найдено {n}'
    return out


# ---------------------------------------------------------------- фото
def css_filter(img, ops):
    """Фильтры CSS по спецификации Filter Effects (пространство sRGB, слева направо)."""
    a = np.asarray(img.convert('RGB'), dtype=np.float64) / 255.0
    for op, v in ops:
        if op == 'grayscale':
            s = 1 - v
            m = np.array([[0.2126 + 0.7874 * s, 0.7152 - 0.7152 * s, 0.0722 - 0.0722 * s],
                          [0.2126 - 0.2126 * s, 0.7152 + 0.2848 * s, 0.0722 - 0.0722 * s],
                          [0.2126 - 0.2126 * s, 0.7152 - 0.7152 * s, 0.0722 + 0.9278 * s]])
            a = a @ m.T
        elif op == 'brightness':
            a = a * v
        elif op == 'contrast':
            a = a * v + 0.5 * (1 - v)
        a = np.clip(a, 0, 1)
    return Image.fromarray(np.round(a * 255).astype(np.uint8), 'RGB')


DIM = [('grayscale', 0.3), ('brightness', 0.5)]  # .hero-bg главной
LIT = [('grayscale', 0.05), ('brightness', 1.05), ('contrast', 1.05)]  # .hero-lit главной


def bake():
    out = HERE / 'img'
    out.mkdir(exist_ok=True)
    # качество подобрано по отклонению от фильтра CSS: 44–46 дБ (на глаз не отличить); затемнённые фото легче прежних
    jobs = [('hero.webp', 'hero-dim.webp', DIM, 82), ('hero-m.webp', 'hero-m-dim.webp', DIM, 82),
            ('hero.webp', 'hero-lit.webp', LIT, 75)]
    for src, dst, ops, q in jobs:
        im = css_filter(Image.open(ROOT / 'img' / src), ops)
        im.save(out / dst, 'WEBP', quality=q, method=6)
        print(f'img/{dst}: {im.size[0]}×{im.size[1]}, {(out / dst).stat().st_size // 1024} КБ (из img/{src})')


# ---------------------------------------------------------------- ссылки на общие файлы: через ../
SKIP_URL = ('#', 'http:', 'https:', '//', '/', 'data:', 'mailto:', 'tel:', 'javascript:', 'about:', 'blob:', '?')


def up(u):
    u = u.strip()
    if not u or u.startswith(SKIP_URL):
        return u
    return '../' + (u[2:] if u.startswith('./') else u)


def relink(html):
    parts = re.split(r'(<script\b[^>]*>.*?</script>)', html, flags=re.S)
    for i in range(0, len(parts), 2):  # всё, кроме скриптов
        p = parts[i]
        p = re.sub(r'(?<![\w-])(src|href|poster)="([^"]*)"', lambda m: f'{m[1]}="{up(m[2])}"', p)
        p = re.sub(r'(?<![\w-])(srcset|imagesrcset)="([^"]*)"',
                   lambda m: m[1] + '="' + ', '.join(' '.join([up(x.split()[0])] + x.split()[1:])
                                                    for x in m[2].split(',') if x.strip()) + '"', p)
        p = re.sub(r'url\((["\']?)([^)"\']+)\1\)', lambda m: f'url({m[1]}{up(m[2])}{m[1]})', p)
        parts[i] = p
    return ''.join(parts)


# ---------------------------------------------------------------- стили превью
LENS_CSS = (
    '.hero-bg{position:absolute;inset:0;background:url(img/hero-dim.webp) center/cover}'
    '.hero-lens{position:absolute;left:0;top:0;width:0;height:0;opacity:0;pointer-events:none;overflow:hidden;'
    'contain:strict;will-change:transform,opacity;'
    '-webkit-mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62.5%,transparent 100%);'
    'mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62.5%,transparent 100%);'
    '-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;transition:opacity 2s cubic-bezier(.19,1,.22,1)}'
    '.hero-lens.on{opacity:1}'
    '.hero-lens-img{position:absolute;left:0;top:0;background:center/cover no-repeat;will-change:transform}'
)
FX_CSS = """<style id="lupa-fx">/* превью «лёгкой лупы» (preview-lupa/build_preview.py) */
@media (max-width:760px),(hover:none),(pointer:coarse){.hero-lens{display:none}}
.lowfx .hero-lens,.lowfx .grain,.lowfx .panel-scan{display:none}
.lowfx .dot:before,.lowfx .phone i:after,.lowfx .phone::after{animation:none;display:none}
.lowfx .scroll-cue i:after,.lowfx .chip-y:before,.lowfx .cycle-arc,.lowfx .cycle-glow{animation:none}
.lowfx .hdr.scrolled,.lowfx .nav-dd-panel,.lowfx .btn-o,.lowfx .badge,.lowfx .panel,.lowfx .form,.lowfx .mbar{-webkit-backdrop-filter:none;backdrop-filter:none}
.lowfx .panel{background:#18181bf0}.lowfx .hdr.scrolled{background:#000000eb}.lowfx .form{background:#09090bf0}.lowfx .mbar{background:#121214f7}
.lupa-badge{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:240;width:max-content;max-width:calc(100vw - 220px);padding:9px 16px;border-radius:999px;background:#09090bf2;border:1px solid #ffffff2e;color:#d4d4d8;font:500 12.5px/1.35 Inter,system-ui,sans-serif;box-shadow:0 12px 32px -12px #000}
.lupa-badge b{color:#fff;font-weight:600}.lupa-badge a{color:#a5b4fc;text-decoration:underline;text-underline-offset:2px}.lupa-badge a:hover{color:#fff}
@media (max-width:760px){.lupa-badge{display:none}}
</style>"""

HEAD_JS = """d.classList.add('js');
    /* превью «лёгкой лупы»: облегчённый режим — ?fx=lite или уже определён на этом визите; ?fx=full — полный, ?fx=auto — заново */
    try { var fxq = (location.search.match(/[?&]fx=(lite|full|auto)\\b/) || [])[1]; if (fxq === 'auto') sessionStorage.removeItem('pc-lowfx');
      if (fxq === 'lite' || (!fxq && sessionStorage.getItem('pc-lowfx') === '1')) d.classList.add('lowfx'); } catch (e) { }"""

BADGE = """<div class="lupa-badge" id="lupaBadge">Превью «лёгкая лупа» · <b id="lupaMode">полный режим</b> · <a href="?fx=full">полный</a> · <a href="?fx=lite">облегчённый</a> · <a href="?fx=auto">авто</a></div>
<script>/* плашка превью: какой режим включён и сколько кадров в секунду намерено */
(function(){var h=document.documentElement,b=document.getElementById('lupaMode'),q=(location.search.match(/[?&]fx=(lite|full|auto)\\b/)||[])[1];
function pl(n){var a=n%10,c=n%100;return a===1&&c!==11?'кадр':a>=2&&a<=4&&(c<12||c>14)?'кадра':'кадров'}
function upd(){var lite=h.classList.contains('lowfx'),f=+h.getAttribute('data-fps')||0;
b.textContent=(lite?'облегчённый режим':'полный режим')+(q==='lite'||q==='full'?' (вручную)':f?' (авто: '+f+' '+pl(f)+' в секунду)':lite?' (авто, с прошлой страницы)':' (авто: замер через 3 с после загрузки)')}
upd();document.addEventListener('pc:fx',upd)})();</script>
"""


def build_html():
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    s = relink(s)
    # скрипты: общие файлы — из корня, app.min.js — свой
    s = once_re(s, r"\}\)\('', \['vendor/gsap\.min\.js', 'vendor/ScrollTrigger\.min\.js', 'vendor/lenis\.min\.js', "
                   r"'app\.min\.js\?v=[0-9a-z]+'\]\);",
                "})('../', ['vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', "
                f"'preview-lupa/app.min.js?v={VER}']);", 'загрузчик скриптов')
    s = once_re(s, r'\}\)\("\./","(\d+)"\);</script>', r'})("../","\1");</script>', 'поиск по сайту')
    # фото первого экрана: заранее затемнённое
    s = once(s, '<link rel="preload" href="../img/hero.webp" as="image" media="(min-width:761px)">',
             '<link rel="preload" href="img/hero-dim.webp" as="image" media="(min-width:761px)">', 'preload фото')
    s = once(s, '<link rel="preload" href="../img/hero-m.webp" as="image" media="(max-width:760px)">',
             '<link rel="preload" href="img/hero-m-dim.webp" as="image" media="(max-width:760px)">', 'preload фото (телефон)')
    s = once_re(s, r'\.hero-bg,\.hero-lit\{position:absolute;inset:0;background:url\(\.\./img/hero\.webp\) center/cover\}'
                   r'\.hero-bg\{filter:grayscale\(\.3\) brightness\(\.5\)\}\.hero-lit\{[^}]*\}',
                LENS_CSS.replace('\\', '\\\\'), 'стили лупы')
    s = once(s, '.hero-bg,.hero-lit{background-image:url(../img/hero-m.webp)}',
             '.hero-bg{background-image:url(img/hero-m-dim.webp)}', 'фото на телефоне')
    s = once(s, '<div class="hero-lit" id="heroLit"></div>',
             '<div class="hero-lens" id="heroLens" data-src="img/hero-lit.webp"><div class="hero-lens-img"></div></div>',
             'разметка лупы')
    # вход первого экрана: без размытия в облегчённом режиме
    s = once(s, 'H=b&&!m.matchMedia("(max-width: 760px)").matches',
             'H=b&&!m.matchMedia("(max-width: 760px)").matches&&!h.classList.contains("lowfx")', 'размытие при входе')
    s = once(s, "d.classList.add('js');", HEAD_JS, 'облегчённый режим в <head>')
    s = once(s, '<!-- style:end -->', '<!-- style:end -->' + FX_CSS, 'стили облегчённого режима')
    s = once(s, '</body>', BADGE + '</body>', 'плашка превью')
    # проверка: не осталось ссылок на общие файлы без ../ (кроме своих файлов превью)
    left = [u for u in re.findall(r'(?<![\w-])(?:src|href)="([^"]*)"', re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S))
            if u and not u.startswith(SKIP_URL + ('../',)) and not u.startswith('img/hero-')]
    assert not left, 'ссылки без ../: ' + ', '.join(left[:10])
    (HERE / 'index.html').write_text(s, encoding='utf-8')
    print('index.html:', len(s.encode()) // 1024, 'КБ')


# ---------------------------------------------------------------- app.js
LOWFX_JS = """var mobile = matchMedia('(max-width: 760px)').matches;

  /* ---------- облегчённый режим (превью «лёгкой лупы», 13.11.2026) ----------
     Через 3 с после загрузки 2 с считаются кадры (и потом, пока лупа догоняет мышь, — см. initLens). Меньше 40 в секунду (середина промежутков между кадрами длиннее
     25 мс) — слабый компьютер или браузер без видеоускорения: класс lowfx на <html> выключает лупу, «зерно»,
     сканирующую линию, пульсации, матовое стекло, параллакс и наклон панели, нарисованный курсор (остаётся обычный).
     Решение помнится до конца визита (sessionStorage pc-lowfx). Вручную: ?fx=lite, ?fx=full, ?fx=auto. */
  var fxMode = (location.search.match(/[?&]fx=(lite|full|auto)\\b/) || [])[1] || '';
  var lowfx = html.classList.contains('lowfx'), lowfxHooks = [];
  var fxEvent = function () { try { document.dispatchEvent(new CustomEvent('pc:fx')); } catch (e) { } };
  var setLowfx = function (remember) {
    if (lowfx) return;
    lowfx = true;
    html.classList.add('lowfx');
    if (remember) { try { sessionStorage.setItem('pc-lowfx', '1'); } catch (e) { } }
    lowfxHooks.forEach(function (f) { try { f(); } catch (e) { } });
  };
  var fxProbe = function () {
    if (lowfx || fxMode === 'full' || fxMode === 'lite') return;
    if (document.hidden) { setTimeout(fxProbe, 2000); return; }
    var ts = [], t0 = 0, hid = false, onVis = function () { hid = true; };
    document.addEventListener('visibilitychange', onVis);
    var step = function (t) {
      if (!t0) t0 = t;
      ts.push(t);
      if (t - t0 < 2000 && !hid) { requestAnimationFrame(step); return; }
      document.removeEventListener('visibilitychange', onVis);
      if (hid || document.hidden) { setTimeout(fxProbe, 2000); return; } /* вкладку прятали — замер не в счёт */
      var d = [];
      for (var i = 1; i < ts.length; i++) d.push(ts[i] - ts[i - 1]);
      d.sort(function (a, b) { return a - b; });
      var med = d.length ? d[d.length >> 1] : 1000;
      html.setAttribute('data-fps', Math.round(1000 / med));
      if (d.length < 20 || med > 25) setLowfx(true);
      fxEvent();
    };
    requestAnimationFrame(step);
  };
  if (document.readyState === 'complete') setTimeout(fxProbe, 3000);
  else addEventListener('load', function () { setTimeout(fxProbe, 3000); });"""

HERO_JS = """  /* ---------- первый экран: лупа инспектора, параллакс, наклон панели ----------
     Лупа (превью 13.11.2026): светлое фото img/hero-lit.webp в круглой маске только сдвигается (transform) —
     браузер не перерисовывает фото. Кадры считаются, только пока круг догоняет мышь (та же плавность, что раньше);
     без мыши круг стоит на открытой части фото над панелью «Что покажет бесплатный аудит» и сам не ходит.
     Мышь ушла с первого экрана — круг плавно возвращается на место. Телефоны, планшеты, облегчённый режим — без лупы. */
  var hero = $('#hero'), media = $('#heroMedia'), lens = $('#heroLens'), panel = $('#panel');
  /* первый экран внутренних страниц: .d-hero (услуги, договор, материалы), .p-hero (раздел и журнал), .f-hero (отрасль) */
  var dHero = $('.d-hero') || $('.p-hero') || $('.f-hero'), dMedia = dHero ? $('.d-hero-media, .hero-media', dHero) : null;
  var lensShow = function () { };
  var initLens = function () {
    var img = lens.firstElementChild, src = lens.getAttribute('data-src');
    var W = 0, H = 0, r = 0, x = 0, y = 0, tx = 0, ty = 0, hx = 0, hy = 0;
    var raf = 0, last = 0, visible = true, follow = false, off = false, ready = false, want = false, dts = [];
    var home = function () {
      /* открытая часть фото: над панелью, когда она стоит справа от текста (шире 1280 px), иначе — справа вверху */
      var p = panel, px = 0, py = 0, el = p;
      if (p && matchMedia('(min-width: 1281px)').matches) {
        for (; el && el !== hero; el = el.offsetParent) { px += el.offsetLeft; py += el.offsetTop; }
      }
      if (p && el === hero) {
        var hdr = $('#hdr'), hh = hdr ? hdr.offsetHeight : 0;
        hx = px + p.offsetWidth / 2 - media.offsetLeft;
        hy = (hh + py) / 2 - media.offsetTop;
      } else { hx = W * 0.78; hy = H * 0.22; }
    };
    var apply = function () {
      lens.style.transform = 'translate3d(' + (x - r).toFixed(1) + 'px,' + (y - r).toFixed(1) + 'px,0)';
      img.style.transform = 'translate3d(' + (r - x).toFixed(1) + 'px,' + (r - y).toFixed(1) + 'px,0)';
    };
    var size = function () {
      if (off) return;
      W = media.offsetWidth; H = media.offsetHeight;
      r = Math.round(Math.max(240, Math.min(400, innerWidth * 0.21)) * 0.72); /* как раньше: clamp(240px, 21vw, 400px) */
      lens.style.width = lens.style.height = 2 * r + 'px';
      img.style.width = W + 'px'; img.style.height = H + 'px';
      home();
      if (!follow) { tx = hx; ty = hy; if (!raf) { x = hx; y = hy; } }
      apply();
    };
    var tick = function (now) {
      raf = 0;
      if (off || !visible) return;
      var dt = last ? Math.min(Math.max(now - last, 0), 100) : 16.67;
      if (last && fxMode !== 'full') {
        /* страховка и в движении: середина из 40 кадров длиннее 25 мс (меньше 40 кадров в секунду) — облегчённый режим */
        dts.push(now - last);
        if (dts.length >= 40) {
          dts.sort(function (a, b) { return a - b; });
          var med = dts[20]; dts = [];
          if (med > 25) { html.setAttribute('data-fps', Math.round(1000 / med)); setLowfx(true); fxEvent(); return; }
        }
      }
      last = now;
      var k = 1 - Math.pow(0.94, dt / 16.67);
      x += (tx - x) * k; y += (ty - y) * k;
      if (Math.abs(tx - x) < 0.3 && Math.abs(ty - y) < 0.3) { x = tx; y = ty; apply(); return; } /* догнал — кадры не нужны */
      apply();
      raf = requestAnimationFrame(tick);
    };
    var go = function () { if (!raf && !off && visible) { last = 0; raf = requestAnimationFrame(tick); } };
    var reveal = function () { if (ready && want && !off) lens.classList.add('on'); };
    hero.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse' || off) return;
      var b = media.getBoundingClientRect();
      tx = (e.clientX - b.left) / b.width * W; ty = (e.clientY - b.top) / b.height * H;
      follow = true; go();
    }, { passive: true });
    hero.addEventListener('pointerleave', function () { if (off) return; follow = false; tx = hx; ty = hy; go(); });
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) go(); }).observe(hero);
    if (window.ResizeObserver) new ResizeObserver(function () { size(); }).observe(media);
    addEventListener('resize', size);
    size();
    /* светлое фото — после загрузки страницы, чтобы не мешать первому экрану */
    var loadLit = function () {
      var im = new Image();
      im.onload = function () {
        var set = function () { img.style.backgroundImage = 'url("' + src + '")'; ready = true; reveal(); };
        if (im.decode) im.decode().then(set, set); else set();
      };
      im.src = src;
    };
    if (document.readyState === 'complete') loadLit(); else addEventListener('load', loadLit);
    lowfxHooks.push(function () { off = true; if (raf) cancelAnimationFrame(raf); raf = 0; lens.classList.remove('on'); });
    return function () { want = true; reveal(); };
  };
  if (lens && media && hero) {
    if (fine && !mobile && !lowfx) lensShow = initLens();
    if (fine && panel) {
      var mX = gsap.quickTo(media, 'x', { duration: 1.4, ease: 'power3' }), mY = gsap.quickTo(media, 'y', { duration: 1.4, ease: 'power3' });
      var pY = gsap.quickTo(panel, 'rotationY', { duration: 1.1, ease: 'power3' }), pX = gsap.quickTo(panel, 'rotationX', { duration: 1.1, ease: 'power3' });
      /* нули — явно: вход панели может ещё идти анимацией браузера (tools/site/hero_in.js), её промежуточное положение
         GSAP не должен принять за исходное */
      gsap.set(panel, { transformPerspective: 1200, x: 0, y: 0, rotationX: 0, rotationY: 0 });
      hero.addEventListener('pointermove', function (e) {
        if (lowfx) return; /* облегчённый режим: без параллакса, наклона и блика панели */
        var px = e.clientX / innerWidth - 0.5, py = e.clientY / innerHeight - 0.5;
        mX(-px * 30); mY(-py * 20); pY(px * 9); pX(-py * 9);
        var r = panel.getBoundingClientRect();
        panel.style.setProperty('--gx', (e.clientX - r.left) + 'px'); panel.style.setProperty('--gy', (e.clientY - r.top) + 'px');
      });
      hero.addEventListener('pointerleave', function () { mX(0); mY(0); pX(0); pY(0); });
      lowfxHooks.push(function () { mX(0); mY(0); pX(0); pY(0); });
    }
"""


def build_js():
    s = (ROOT / 'app.js').read_text(encoding='utf-8')
    s = once(s, "var mobile = matchMedia('(max-width: 760px)').matches;", LOWFX_JS, 'облегчённый режим')
    s = once(s, 'var richFx = fine && !mobile;', 'var richFx = fine && !mobile && !lowfx;', 'размытие при появлении')
    s = once(s, "  if (fine) {\n    html.classList.add('has-cursor');",
             "  if (fine && !lowfx) {\n    html.classList.add('has-cursor');\n"
             "    lowfxHooks.push(function () { html.classList.remove('has-cursor'); }); /* облегчённый режим — обычный курсор */",
             'курсор')
    s = once(s, "      var c = e.target.closest && e.target.closest('.card,.form');\n      if (!c) return;",
             "      if (lowfx) return;\n      var c = e.target.closest && e.target.closest('.card,.form');\n      if (!c) return;",
             'подсветка карточек')
    a = s.index('  /* ---------- первый экран: «фонарь» инспектора, параллакс, наклон панели ---------- */')
    b = s.index('    /* уход первого экрана при прокрутке')
    assert s.count('  /* ---------- первый экран: «фонарь»') == 1 and a < b
    s = s[:a] + HERO_JS + s[b:]
    s = once(s, '«фонарь» главной загорается через 0,4 с после начала входа',
             'лупа главной появляется после входа фото (2,6 с)', 'комментарий о лупе')
    s = once(s, '    litOn = true;\n    var tl = gsap.timeline', '    var tl = gsap.timeline', 'вход: litOn')
    s = once(s, '      .to(lit, { opacity: 1, duration: 2 }, 0.4)\n', '      .add(lensShow, 2.65)\n', 'вход: лупа')
    s = once_re(s, r"    var litStart = function \(\) \{\n      if \(dHero \|\| !lit\) return;\n      litOn = true;\n"
                   r"      gsap\.to\(lit, \{[^\n]*\n    \};",
                "    var litStart = function () {\n      if (dHero) return;\n"
                "      /* лупа — после входа фото (2,6 с), иначе круг не совпадёт с фото, которое ещё уменьшается */\n"
                "      setTimeout(lensShow, Math.max(0, pcHero.t0 + 2650 - performance.now()));\n    };", 'лупа после входа')
    for w in ('litOn', 'heroLit', ' lit,', '(lit,', 'lit.style', 'heroVisible', 'lastMove'):
        assert w not in s, 'осталось: ' + w
    (HERE / 'app.js').write_text(s, encoding='utf-8')
    res = subprocess.run(['npx', '--yes', 'esbuild@0.24.2', str(HERE / 'app.js'), '--minify', '--target=es2015',
                          '--charset=utf8', '--outfile=' + str(HERE / 'app.min.js'), '--log-level=warning'],
                         capture_output=True, text=True, cwd=ROOT)
    if res.returncode:
        sys.exit('esbuild: ' + res.stderr)
    print('app.min.js:', (HERE / 'app.min.js').stat().st_size // 1024, 'КБ')


if __name__ == '__main__':
    bake()
    build_html()
    build_js()
