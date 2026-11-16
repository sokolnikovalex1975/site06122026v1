#!/usr/bin/env python3
"""Самопроверка на телефоне: кнопка после пунктов, компактный блок, нижняя панель скрыта (решение владельца 17.11.2026).

    python3 tools/site/samoproverka.py                        # правит страницы репозитория
    python3 tools/site/samoproverka.py --check                # только проверка страниц репозитория, код 1 при нарушениях
    python3 tools/site/samoproverka.py --check-prod <файлы>   # проверка готовых index.php пакета для Timeweb

Замечание владельца 13.11.2026 (скриншот iPhone, блок «Ресторан готов к проверке?»): «логичнее кнопку «Заказать
обследование» делать после выборов пунктов… в мобильной версии кнопка должна стоять ниже… сделать это более компактно».
Макеты согласованы 17.11.2026: «Да, делай в превью. «Заказать обследование», нижнюю панель скрывай» (файлы проекта,
папка «Самопроверка — кнопка после пунктов на телефоне»).

Что делает скрипт в блоке самопроверки <section id="samoproverka"> (повторный запуск ничего не меняет):
  * подсказку .f-check-note и кнопку переносит из левой колонки в <div class="f-check-f"> сразу после списка пунктов:
    на телефоне и планшете (до 1100 px) порядок «заголовок → счёт → пункты → подсказка → кнопка» — и на экране, и для
    экранного диктора; на компьютере (от 1101 px) сетка ставит их на прежнее место — в левую колонку под счёт;
  * счёт .f-check-res оборачивает в <div class="f-check-score"> вместе с полоской <span class="f-check-bar">
    (по отрезку на пункт, на компьютере полоски нет). Отрезков закрашено столько, сколько показывает цифра счёта,
    цвет — как у цифры: классы warn и full у .f-check-res ставит прежний скрипт страницы, он не меняется;
  * номера норм с дефисом в пунктах (СП 2.3.6.4281-26, СанПиН 3.3686-21) — в <span class="nw">, как уже было на части
    страниц: на телефоне пункты стали шире, и «4281-» / «26» иначе разъезжались по строкам; такой номер в отмеченном
    пункте светлеет вместе с текстом (раньше на компьютере оставался серым);
  * надпись «Заказать бесплатное обследование» до 600 px — «Заказать обследование» (вторая надпись .f-bt-m, первая
    .f-bt-d скрыта); шире 600 px — прежняя. Другие надписи кнопок не меняются;
  * перед строкой <style id="mob-fit"> (её нет — перед <style id="tel-plain">) ставит одну строку стилей
    <style id="f-check-m"> (STYLE ниже, не перед </head>: там по закону владельца стоит UIS): до 600 px — пункты
    без двойных отступов (общий стиль .panel ul / .panel li перебивал .f-check-list), во всю ширину, текст 14 px,
    чекбокс 22 px, заголовок 26 px, счёт в одну строку с полоской, кнопка во всю ширину 52 px (надпись 16 px, до 370 px —
    15 px, до 340 px — 13,5 px, чтобы длинные надписи шли одной строкой); до 1100 px — тот же
    порядок блоков; на компьютере сетка ставит подсказку и кнопку в левую колонку под счёт, список — справа на всю высоту;
  * сразу после блока — скрипт <script id="f-check-js"> (SCRIPT ниже): отрезки полоски по числу отмеченных пунктов и
    класс f-check-on у <html>, пока блок в средней половине экрана. С ним нижняя панель «Позвонить / Обследование»
    (.mbar, до 760 px) уезжает вниз, как у формы заявки, — у блока своя кнопка; дальше по странице панель возвращается.
Тексты заголовков, пунктов и подсказок, счёт и скрипт страницы, ссылки телефона и почты, счётчики не трогаются;
app.js и app.min.js не меняются. Страницы превью (preview-*) не трогаются.
Проверка в браузере: node tools/qa/samoproverka_test.mjs (сервер превью — BASE=…, по умолчанию http://127.0.0.1:8833).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP_TOP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'vendor'}
ANCHOR = '<style id="tel-plain">'
# Строка стилей — перед строкой mob_fit.py (та сама встаёт прямо перед tel-plain, иначе шаги сборки двигали бы друг друга);
# у правил ниже селектор с #samoproverka, поэтому порядок строк на результат не влияет.
MOB_FIT = '<style id="mob-fit">'

# Все правила начинаются с #samoproverka: у страниц свои стили блока, а общий .panel ul / .panel li сильнее .f-check-list.
CSS = (
    '/* самопроверка: на телефоне и планшете пункты → подсказка → кнопка, компактно; на компьютере — как раньше'
    ' (tools/site/samoproverka.py, решение владельца 17.11.2026) */'
    '#samoproverka .f-check-bar,#samoproverka .f-bt-m{display:none}'
    'html.f-check-on .mbar{transform:translateY(160%)}'
    '#samoproverka .f-check-in{grid-template-rows:auto 1fr;row-gap:0}'
    '#samoproverka .f-check-l{grid-column:1;grid-row:1}'
    '#samoproverka .f-check-list{grid-column:2;grid-row:1/span 2}'
    '#samoproverka .f-check-f{grid-column:1;grid-row:2}'
    '#samoproverka .f-check-list label>span span{font-size:inherit;line-height:inherit;color:inherit}'
    '@media (max-width:1100px){'
    '#samoproverka .f-check-in{grid-template-rows:none}'
    '#samoproverka .f-check-l,#samoproverka .f-check-list,#samoproverka .f-check-f{grid-column:auto;grid-row:auto}'
    '#samoproverka .f-check-score{display:flex;align-items:center;gap:16px;margin:22px 0 10px}'
    # счёт — обычной строкой, не flex: «0» и «из 5» одним текстом (правило 11.11.2026, tools/site/flex_text.py)
    '#samoproverka .f-check-res{display:block;flex:none;margin:0;line-height:1;white-space:nowrap}'
    '#samoproverka .f-check-res b{vertical-align:middle}'
    '#samoproverka .f-check-bar{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:4px;flex:1;max-width:360px}'
    '#samoproverka .f-check-bar i{display:block;height:4px;border-radius:2px;background:rgba(255,255,255,.1);'
    'transition:background-color .3s}'
    '#samoproverka .f-check-bar i.on{background:var(--acc)}'
    '#samoproverka .f-check-res.warn+.f-check-bar i.on{background:var(--yel)}'
    '#samoproverka .f-check-res.full+.f-check-bar i.on{background:var(--grn)}'
    '#samoproverka .f-check-list{padding:0;margin-top:24px}'
    '#samoproverka .f-check-list li{display:block;padding:0}'
    '#samoproverka .f-check-note{margin:24px 0 20px;max-width:none}'
    '#samoproverka .f-check-f .btn{vertical-align:top}'
    '}'
    '@media (max-width:600px){'
    '#samoproverka.f-checks{padding:20px 0 48px}'
    '#samoproverka .f-check-in{padding:22px 18px 20px}'
    '#samoproverka .badge{margin-bottom:2px}'
    '#samoproverka .f-check-t{font-size:26px;line-height:1.1}'
    '#samoproverka .f-check-score{margin:12px 0 0}'
    '#samoproverka .f-check-res{font-size:14px;color:var(--t2)}'
    '#samoproverka .f-check-res b{font-size:26px;margin-right:5px}'
    '#samoproverka .f-check-list{margin-top:16px}'
    '#samoproverka .f-check-list label{padding:12px 0;gap:13px}'
    '#samoproverka .f-check-list input{width:22px;height:22px;border-radius:7px;background-size:12px}'
    '#samoproverka .f-check-list label>span{font-size:14px;line-height:1.4;color:var(--t2)}'
    '#samoproverka .f-check-list label>span strong{display:inline;margin:0;font-size:inherit;font-weight:500;color:var(--t1)}'
    '#samoproverka .f-check-list input:checked+span{color:var(--t1)}'
    '#samoproverka .f-check-note{font-size:14px;line-height:1.45;margin:16px 0 14px}'
    '#samoproverka .f-check-f .btn{display:flex;width:100%;min-height:52px;font-size:16px;padding-left:16px;padding-right:16px}'
    '#samoproverka .f-bt-d{display:none}'
    '#samoproverka .f-bt-m{display:inline-block}'
    '}'
    # узкие телефоны: длинные надписи («Рассчитать формат для объекта», «Проверить журнал на объекте») — в одну строку
    '@media (max-width:370px){#samoproverka .f-check-f .btn{font-size:15px;padding-left:14px;padding-right:14px}}'
    '@media (max-width:340px){#samoproverka .f-check-f .btn{font-size:13.5px;padding-left:10px;padding-right:10px}}'
)
STYLE = '<style id="f-check-m">' + CSS + '</style>\n'
STYLE_RE = re.compile(r'<style id="f-check-m">.*?</style>\n?', re.S)

JS = (
    '/* самопроверка (tools/site/samoproverka.py): отрезков полоски столько, сколько показывает цифра счёта; пока блок'
    ' в средней половине экрана — класс f-check-on у <html>, нижняя панель «Позвонить / Обследование» уезжает вниз */'
    '(function(){var s=document.getElementById("samoproverka");if(!s)return;'
    'var p=s.querySelector(".f-check")||s,b=s.querySelector(".f-check-bar"),r=s.querySelector(".f-check-res");'
    'if(b&&r){var g=b.children,u=function(){var k=r.querySelector("b"),n=k?parseInt(k.textContent,10):NaN,i,c;'
    'if(isNaN(n)){n=0;c=s.querySelectorAll(".f-check-list input[type=checkbox]");for(i=0;i<c.length;i++)if(c[i].checked)n++}'
    'for(i=0;i<g.length;i++)g[i].classList.toggle("on",i<n)};'
    's.addEventListener("change",function(){setTimeout(u,0)});u()}'
    'if("IntersectionObserver" in window){var h=document.documentElement;'
    'new IntersectionObserver(function(e){h.classList.toggle("f-check-on",e[e.length-1].isIntersecting)},'
    '{rootMargin:"-25% 0px -25% 0px"}).observe(p)}})();'
)
SCRIPT = '<script id="f-check-js">' + JS + '</script>'
SCRIPT_RE = re.compile(r'\n?<script id="f-check-js">.*?</script>', re.S)

SEC_RE = re.compile(r'<section\b[^>]*\bid="samoproverka"[^>]*>.*?</section>', re.S)
IN_OPEN = '<div class="f-check-in">'
NOTE_RE = re.compile(r'\n?[ \t]*<p class="f-check-note"[^>]*>.*?</p>', re.S)
BTN_RE = re.compile(r'\n?[ \t]*<a\b[^>]*\bclass="(?:[^"]*\s)?btn(?:\s[^"]*)?"[^>]*>.*?</a>', re.S)
RES_RE = re.compile(r'<p class="f-check-res\b[^"]*"[^>]*>.*?</p>', re.S)
LIST_RE = re.compile(r'([ \t]*)<ul class="f-check-list"[^>]*>.*?</ul>', re.S)
FREE_RE = re.compile(r'<span class="btn-t">Заказать(?: |\u00a0|&nbsp;)бесплатное(?: |\u00a0|&nbsp;)обследование</span>')
LABEL_D = '<span class="btn-t f-bt-d">Заказать бесплатное обследование</span>'
LABEL_M = '<span class="btn-t f-bt-m">Заказать обследование</span>'


# номер нормы с дефисом (3.3686-21, 2.3.6.4281-26, 3.5.0396-25) — одним куском, без переноса на дефисе
NUM_RE = re.compile(r'(?<![\w.\-])(\d+(?:\.\d+)+-\d{2})(?![\w\-])')
NW_OR_TAG = re.compile(r'<span class="nw">.*?</span>|<[^>]+>', re.S)


def nw_numbers(html):
    """В тексте пунктов (вне тегов и вне готовых <span class="nw">) номера норм с дефисом → <span class="nw">."""
    out, pos = [], 0
    for m in NW_OR_TAG.finditer(html):
        out.append(NUM_RE.sub(r'<span class="nw">\1</span>', html[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(NUM_RE.sub(r'<span class="nw">\1</span>', html[pos:]))
    return ''.join(out)


class Skip(Exception):
    """Блок не по общей схеме — страница не трогается, --check сообщает."""


def _div_end(s, start):
    """Позиция сразу после </div>, закрывающего <div …> в позиции start."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return start + m.end()
    raise Skip('нет закрывающего </div> левой колонки')


def fix_section(sec):
    """Блок самопроверки → новая разметка. Уже переделанный блок возвращается как есть."""
    if 'class="f-check-f"' in sec:
        return sec
    i = sec.find(IN_OPEN)
    if i < 0:
        raise Skip('нет <div class="f-check-in">')
    m = re.compile(r'\s*<div\b[^>]*>').match(sec, i + len(IN_OPEN))
    if not m:
        raise Skip('нет левой колонки')
    l_start = m.end() - len(m.group(0).lstrip())
    l_end = _div_end(sec, l_start)
    left = sec[l_start:l_end]
    note, btn = NOTE_RE.search(left), BTN_RE.search(left)
    res = RES_RE.search(left)
    if not (note and btn and res) or note.start() > btn.start() or res.start() > note.start():
        raise Skip('в левой колонке нет счёта, подсказки и кнопки по порядку')
    lst = LIST_RE.search(sec, l_end)
    if not lst:
        raise Skip('нет списка .f-check-list после левой колонки')
    n = lst.group(0).count('type="checkbox"')
    if not n:
        raise Skip('в списке нет пунктов')
    note_html, btn_html = note.group(0).strip(), btn.group(0).strip()
    btn_html = FREE_RE.sub(LABEL_D + LABEL_M, btn_html, count=1)
    bar = '<span class="f-check-bar" aria-hidden="true">' + '<i></i>' * n + '</span>'
    new_left = left[:res.start()] + '<div class="f-check-score">' + res.group(0) + bar + '</div>' \
        + left[res.end():note.start()] + left[note.end():btn.start()] + left[btn.end():]
    open_tag = re.match(r'<div\b[^>]*>', new_left).group(0)
    if 'f-check-l' not in open_tag:
        cls = re.search(r'\bclass="([^"]*)"', open_tag)
        new_open = (open_tag.replace(cls.group(0), 'class="%s f-check-l"' % cls.group(1), 1) if cls
                    else open_tag[:-1] + ' class="f-check-l">')
        new_left = new_open + new_left[len(open_tag):]
    ind = lst.group(1)
    foot = '\n%s<div class="f-check-f">\n%s  %s\n%s  %s\n%s</div>' % (ind, ind, note_html, ind, btn_html, ind)
    return sec[:l_start] + new_left + sec[l_end:lst.end()] + foot + sec[lst.end():]


def fix(text):
    """Вся страница: блок, строка стилей и скрипт. Без блока самопроверки — убирает свои стили и скрипт, если были."""
    t = STYLE_RE.sub('', text)
    t = SCRIPT_RE.sub('', t)
    m = SEC_RE.search(t)
    if not m:
        return t
    anchor = MOB_FIT if MOB_FIT in t else ANCHOR
    if anchor not in t:
        raise Skip('нет <style id="mob-fit"> и <style id="tel-plain"> для строки стилей')
    sec = fix_section(m.group(0))
    sec = LIST_RE.sub(lambda u: nw_numbers(u.group(0)), sec, count=1)
    t = t[:m.start()] + sec + '\n' + SCRIPT + t[m.end():]
    return t.replace(anchor, STYLE + anchor, 1)


def problems(text):
    """Что не так на странице (пустой список — всё в порядке)."""
    try:
        return [] if fix(text) == text else ['блок самопроверки, стили или скрипт не как в samoproverka.py']
    except Skip as e:
        return [str(e)]


def pages():
    for p in sorted(ROOT.rglob('index.html')):
        parts = p.relative_to(ROOT).parts
        if parts[0] in SKIP_TOP or parts[0].startswith('preview'):
            continue
        yield p


def main():
    args = sys.argv[1:]
    if args[:1] == ['--check-prod']:
        files = [pathlib.Path(a) for a in args[1:]]
        bad = 0
        for f in files:
            pr = problems(f.read_text(encoding='utf-8'))
            if pr:
                bad += 1
                print('samoproverka: %s: %s' % (f, '; '.join(pr)))
        print('samoproverka --check-prod: файлов %d, с нарушениями: %d' % (len(files), bad))
        return 1 if bad else 0
    check = '--check' in args
    changed, skipped, blocks = [], [], 0
    for p in pages():
        rel = p.relative_to(ROOT).as_posix()
        s = p.read_text(encoding='utf-8')
        try:
            t = fix(s)
        except Skip as e:
            skipped.append('%s: %s' % (rel, e))
            continue
        if SEC_RE.search(t):
            blocks += 1
        if t != s:
            changed.append(rel)
            if not check:
                p.write_text(t, encoding='utf-8')
    for line in skipped:
        print('samoproverka: не по схеме —', line)
    if check:
        for rel in changed:
            print('samoproverka: нужно поправить', rel)
        print('samoproverka: страниц с блоком %d, нужно поправить %d, не по схеме %d' % (blocks, len(changed), len(skipped)))
        return 1 if (changed or skipped) else 0
    print('samoproverka: страниц с блоком %d, изменено %d' % (blocks, len(changed)))
    for rel in changed:
        print('  ', rel)
    return 1 if skipped else 0


if __name__ == '__main__':
    sys.exit(main())
