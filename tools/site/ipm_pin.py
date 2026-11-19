#!/usr/bin/env python3
"""Главная, блок «Пест-менеджмент по системе IPM» (#podhod): круг «IPM — цикл визита» замирает, пока прокручиваются шаги.

    python3 tools/site/ipm_pin.py            # правит index.html
    python3 tools/site/ipm_pin.py --check    # только проверка, код 1 — нужно поправить

Запрос владельца 19.11.2026: «Схема справа от него, с кругом… Она прокручивается, когда скроллишь страницу. Нужно сделать
так, чтобы эта сама схема замирала, пока прокручивается контент слева, чтобы показывалась динамика перехода от пункта
к пункту».

Компьютер (от 1025 px, две колонки):
  * круг закреплён (position: sticky) по центру экрана под шапкой и не больше высоты экрана; шаги слева прокручиваются;
  * активен шаг, середина которого прошла центр круга; точка бежит по кольцу от значка к значку (Осмотр → Санитария →
    Учёт → Действие → снова Осмотр), за ней — светящийся след и заполнение кольца; номер «01 / 04» меняется;
  * между карточками шагов — больше воздуха (до 16 % высоты экрана), под последней — запас, чтобы круг успел замкнуться,
    пока он закреплён (считается по размерам экрана);
  * тексты карточек не бледнеют: активная лишь подсвечена рамкой, как раньше.
Планшет и телефон (до 1024 px, одна колонка): поведение прежнее (кольцо по прокрутке, шаг по линии 62 % экрана,
автосмена значков каждые 1,8 с, пока круг на экране) — тот же код, без GSAP.

Как устроено: прежний код круга в app.js ищет #cycleStep; здесь номер шага получает id="cycleNum", поэтому app.js блок
пропускает, и круг главной ведёт только <script id="ipm-pin-js"> сразу после секции. app.min.js и другие страницы
(круг на «Дератизации») не меняются. Стиль — строка <style id="ipm-pin"> перед <style id="tel-plain">
(не перед </head>: там по закону владельца стоит UIS). Счётчики, телефон и почту скрипт не трогает.
Повторный запуск ничего не меняет. Проверка в браузере: node tools/qa/ipm_pin_test.mjs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PAGE = ROOT / 'index.html'
ANCHOR = '<style id="tel-plain">'

CSS = (
    '.cycle-dot{display:none}'
    '.cycle-step.flip{animation:cyNum .5s cubic-bezier(.2,.8,.2,1)}'
    '@keyframes cyNum{from{opacity:0;transform:translateY(6px)}}'
    '@media (min-width:1025px){'
    '.appr-pin{align-items:start}'
    '.appr-pin>.cycle{position:sticky;top:var(--pin-top,calc(var(--hdr-c,64px) + 24px));'
    'max-width:min(620px,calc(100vh - var(--hdr-c,64px) - 64px))}'
    '.appr-pin .steps{gap:clamp(24px,16vh,170px);padding-bottom:var(--pin-pad,0px)}'
    '.appr-pin .cycle-arc{transition:none}'
    '.appr-pin .cycle-dot{display:block;position:absolute;inset:12%;pointer-events:none;will-change:transform}'
    '.appr-pin .cycle-dot::after{content:"";position:absolute;left:50%;top:0;width:12px;height:12px;margin:-6px 0 0 -6px;'
    'border-radius:50%;background:#fff;box-shadow:0 0 0 4px rgba(124,134,255,.28),0 0 22px 6px rgba(124,134,255,.75)}'
    '.appr-pin .node{z-index:1}'
    '.appr-pin .node.done b{color:var(--t1)}'
    '}'
)
STYLE = '<style id="ipm-pin">' + CSS + '</style>\n'
STYLE_RE = re.compile(r'<style id="ipm-pin">.*?</style>\n?', re.S)

JS = r"""(function () {
  var cy = document.getElementById('cycle'), root = cy && cy.parentNode;
  var prog = document.getElementById('cycleProg'), arc = document.getElementById('cycleArc'), lbl = document.getElementById('cycleNum');
  if (!cy || !prog || !arc || !lbl) return;
  var box = root.querySelector('.steps'), steps = [].slice.call(root.querySelectorAll('.step')), nodes = [].slice.call(cy.querySelectorAll('.node'));
  var dot = document.getElementById('cycleDot'), N = steps.length;
  var mq = matchMedia('(min-width: 1025px)'), fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var desk = mq.matches, cur = -1, shown = 0, target = 0, loop = 0, tick = 0, auto = 0, pinTop = 0, H = 0, tail = 0;
  var setOn = function (i) {
    if (i === cur) return; cur = i;
    steps.forEach(function (s, j) { s.classList.toggle('on', j === i); });
    nodes.forEach(function (n, j) { n.classList.toggle('on', j === i); n.classList.toggle('done', desk && j < i); });
    lbl.textContent = '0' + (i + 1) + '\u00a0/ 0' + N;
    if (!reduce) { lbl.classList.remove('flip'); void lbl.offsetWidth; lbl.classList.add('flip'); }
  };
  var draw = function (p) {
    prog.style.strokeDashoffset = (100 - p * 100).toFixed(2);
    if (desk) { var a = p * 360; if (dot) dot.style.transform = 'rotate(' + a.toFixed(2) + 'deg)'; arc.style.transform = 'rotate(' + (a - 90).toFixed(2) + 'deg)'; }
    else arc.style.transform = 'rotate(' + (p * 540).toFixed(1) + 'deg)';
  };
  var ease = function () {
    loop = 0;
    var d = target - shown;
    shown = reduce || Math.abs(d) < 0.0008 ? target : shown + d * 0.16;
    draw(shown);
    if (shown !== target) loop = requestAnimationFrame(ease);
  };
  var layout = function () {
    desk = mq.matches;
    root.style.removeProperty('--pin-pad');
    if (!desk) { root.style.removeProperty('--pin-top'); return; }
    var hdr = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--hdr-c')) || 64, vh = innerHeight;
    H = cy.offsetHeight;
    pinTop = Math.max(hdr + 16, hdr + (vh - hdr - H) / 2);
    root.style.setProperty('--pin-top', pinTop.toFixed(1) + 'px');
    var r = root.getBoundingClientRect(), a = steps[0].getBoundingClientRect(), z = steps[N - 1].getBoundingClientRect();
    var pitch = N > 1 ? (z.top - a.top) / (N - 1) : z.height;
    tail = pitch * 0.6;
    /* круг откреплится, когда низ сетки поднимется к низу круга: к этому моменту середина последнего шага
       должна уйти выше центра круга на «хвост» — тогда кольцо успевает замкнуться, пока круг закреплён */
    var need = (z.top + z.height / 2 - r.top) + H / 2 + tail - (r.bottom - r.top);
    if (need > 0) root.style.setProperty('--pin-pad', Math.ceil(need) + 'px');
  };
  var calc = function () {
    tick = 0;
    var vh = innerHeight, p = 0, i;
    if (desk) {
      var L = pinTop + H / 2, c = steps.map(function (s) { var b = s.getBoundingClientRect(); return b.top + b.height / 2; }), k = -1;
      for (i = 0; i < N; i++) if (c[i] <= L) k = i;
      if (k < 0) { p = 0; k = 0; }
      else if (k < N - 1) p = (k + Math.min(1, (L - c[k]) / (c[k + 1] - c[k]))) / N;
      else p = (k + Math.min(1, (L - c[k]) / tail)) / N;
      setOn(k);
    } else {
      var b = cy.getBoundingClientRect(), s0 = vh * 0.85 - b.top, span = s0 + b.bottom - vh * 0.3;
      p = Math.max(0, Math.min(1, span > 0 ? s0 / span : 0));
      steps.forEach(function (s, j) { var r = s.getBoundingClientRect(); if (r.top <= vh * 0.62 && r.bottom >= vh * 0.62) setOn(j); });
      var vis = b.top <= vh * 0.8 && b.bottom >= vh * 0.2;
      if (vis && !auto && !reduce) auto = setInterval(function () { setOn((cur + 1) % N); }, 1800);
      else if (!vis && auto) { clearInterval(auto); auto = 0; }
    }
    target = p;
    if (!loop) loop = requestAnimationFrame(ease);
  };
  var onScroll = function () { if (!tick) tick = requestAnimationFrame(calc); };
  var refresh = function () { if (auto) { clearInterval(auto); auto = 0; } layout(); calc(); };
  setOn(0);
  layout(); calc();
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', refresh);
  addEventListener('load', refresh);
  if (mq.addEventListener) mq.addEventListener('change', function () { cur = -1; nodes.forEach(function (n) { n.classList.remove('done'); }); refresh(); });
  if (window.ResizeObserver) new ResizeObserver(function () { if (!tick) tick = requestAnimationFrame(function () { tick = 0; layout(); calc(); }); }).observe(box);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
  steps.forEach(function (s, i) { s.addEventListener('pointerenter', function () { if (fine) setOn(i); }); });
})();"""
SCRIPT = '<script id="ipm-pin-js">' + JS + '</script>\n'
SCRIPT_RE = re.compile(r'<script id="ipm-pin-js">.*?</script>\n?', re.S)
SEC_RE = re.compile(r'(<section class="s" id="podhod">.*?</section>\n)', re.S)


def fix(text):
    t = STYLE_RE.sub(lambda m: STYLE, text, count=1) if STYLE_RE.search(text) else text.replace(ANCHOR, STYLE + ANCHOR, 1)
    m = SEC_RE.search(t)
    if not m:
        sys.exit('ipm_pin: нет секции #podhod')
    sec = m.group(1)
    new = sec.replace('<div class="wrap appr">', '<div class="wrap appr appr-pin">', 1)
    new = new.replace('id="cycleStep"', 'id="cycleNum"', 1)
    if 'id="cycleDot"' not in new:
        new = new.replace('<div class="cycle-arc" id="cycleArc"></div>',
                          '<div class="cycle-arc" id="cycleArc"></div><div class="cycle-dot" id="cycleDot"></div>', 1)
    t = t[:m.start()] + new + t[m.end():]
    t = SCRIPT_RE.sub('', t, count=1)
    i = t.find(new) + len(new)
    t = t[:i] + SCRIPT + t[i:]
    return t


def main():
    check = '--check' in sys.argv[1:]
    s = PAGE.read_text(encoding='utf-8')
    if ANCHOR not in s:
        sys.exit('ipm_pin: в index.html нет ' + ANCHOR)
    t = fix(s)
    if t != s and not check:
        PAGE.write_text(t, encoding='utf-8')
    print('ipm_pin: index.html ' + ('нужно поправить' if (check and t != s) else ('исправлено' if t != s else 'без изменений')))
    return 1 if (check and t != s) else 0


if __name__ == '__main__':
    sys.exit(main())
