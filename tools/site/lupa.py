#!/usr/bin/env python3
"""«Лёгкая лупа» и облегчённый режим на всём сайте (15.11.2026) — одни и те же точечные правки для страниц
репозитория и для файлов, снятых с рабочего сайта (пакет tools/deploy/prepare-2026-11-15-lupa.py).

    python3 tools/site/lupa.py           # правит страницы репозитория (повторный запуск ничего не меняет)
    python3 tools/site/lupa.py --check   # только проверить: на всех страницах новая разметка и скрипты

Решение владельца 13.11.2026 по превью preview-lupa/: «Перенеси этот вариант на главную и внутренние страницы,
сохрани счётчики и выложи на Timeweb».

Каждая правка — точная замена прежнего текста (число совпадений проверяется), прежний текст берётся из репозитория
на коммите OLD_COMMIT (до выпуска), новый — из нынешних исходников:
  * скрипт в <head> всех страниц — window.pcFx: облегчённый режим (?fx=lite|full|auto, sessionStorage pc-lowfx,
    класс lowfx на <html>), текст — tools/site/unify.py (HEAD_SCRIPT);
  * вход первого экрана <script id="hero-in"> — без размытия в облегчённом режиме (tools/site/hero_in.js);
  * внутренние страницы с лупой (tools/site/fx.py) — новые стили, скрипт и разметка лупы на месте прежних;
  * вентиляция — своя лупа (tools/ventilyatsiya/page.js, extra.css) на месте прежней;
  * главная — разметка лупы и предзагрузка заранее затемнённого фото; её встроенные стили в репозитории собирает
    tools/build.py из style.css, для рабочего сайта — css_hunks() (те же замены в сжатых стилях);
  * версия ?v= у style.css, app.min.js и legal.css (кэш браузера на год).
Счётчики, телефон и почту правки не трогают (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py).
"""
import difflib
import importlib.util
import pathlib
import re
import subprocess
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
import fx  # noqa: E402
import hero_in  # noqa: E402
import unify  # noqa: E402

OLD_COMMIT = 'd08510f'  # репозиторий до выпуска (прежние фонарь, скрипт в <head>, вход первого экрана)
REPO_OLD_V, NEW_V = '20261113zagolovok', '20261115lupa'
# Версии после выпуска лупы (17.11.2026 «шапка» — 20261117shapka, tools/site/unify.py): разметка лупы та же,
# поэтому --check принимает и общую версию из unify.py, а не только 20261115lupa.
LATER_V = tuple(v for v in (unify.VERSION,) if v != NEW_V)
ESBUILD = ['npx', '--yes', 'esbuild@0.24.2']
SKIP = ('preview-', 'tools/', 'dist/', 'server/', 'vendor/', 'node_modules/')


def git_old(path):
    return subprocess.run(['git', 'show', OLD_COMMIT + ':' + path], cwd=ROOT, capture_output=True,
                          check=True).stdout.decode('utf-8')


def module(name, code):
    m = types.ModuleType(name)
    exec(compile(code, name, 'exec'), m.__dict__)
    return m


def esbuild(code, loader):
    res = subprocess.run(ESBUILD + ['--minify', '--loader=' + loader, '--target=es2015', '--charset=utf8',
                                    '--log-level=warning'], input=code, capture_output=True, text=True, cwd=ROOT)
    if res.returncode:
        sys.exit('esbuild: ' + res.stderr)
    return res.stdout.strip()


# ---------------------------------------------------------------- прежний и новый текст
FX_OLD = module('fx_old', git_old('tools/site/fx.py'))
assert FX_OLD.CSS_GLOW == fx.CSS_GLOW, 'стили подсветки карточек не должны меняться'
FX_STYLE = {lit: ('<style data-fx>\n' + FX_OLD.CSS_GLOW + (FX_OLD.CSS_LIT if lit else '') + '</style>\n',
                  '<style data-fx>\n' + fx.CSS_GLOW + (fx.CSS_LIT if lit else '') + '</style>\n') for lit in (True, False)}
FX_SCRIPT = {lit: (FX_OLD._script(lit), fx._script(lit)) for lit in (True, False)}
# страница защиты от проникновения (только превью GitHub): прежний фонарь там был без телефонов
FX_SCRIPT_ALT = FX_OLD._script(True).replace("if(lit&&!mm('(prefers-reduced-motion: reduce)').matches){",
                                             "if(lit&&!mm('(prefers-reduced-motion: reduce)').matches&&!mm('(max-width:860px)').matches){")
assert FX_SCRIPT_ALT != FX_SCRIPT[True][0]
FX_LIT_OLD = re.compile(r'<div class="fx-lit" aria-hidden="true">(<picture>.*?</picture>)</div>', re.S)

HEAD_OLD = "    d.classList.add('js');\n"
_h = unify.HEAD_SCRIPT
HEAD_NEW = _h[_h.index(HEAD_OLD):_h.index("    try { if (location.hash")]
assert HEAD_NEW.startswith(HEAD_OLD) and 'window.pcFx' in HEAD_NEW and HEAD_NEW.endswith('\n')

HERO_IN = ('<script id="hero-in">' + esbuild(git_old('tools/site/hero_in.js'), 'js') + '</script>',
           '<script id="hero-in">' + hero_in.minified() + '</script>')
assert 'lowfx' not in HERO_IN[0] and 'lowfx' in HERO_IN[1]


def vent_css(css):
    """Стили страницы вентиляции так, как их встраивает tools/ventilyatsiya/build_page.py."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    return re.sub(r'\s*\n\s*', '', css)


VENT_JS = (git_old('tools/ventilyatsiya/page.js').strip(), (ROOT / 'tools/ventilyatsiya/page.js').read_text(encoding='utf-8').strip())
VENT_CSS = (vent_css(git_old('tools/ventilyatsiya/extra.css')), vent_css((ROOT / 'tools/ventilyatsiya/extra.css').read_text(encoding='utf-8')))
VENT_LIT_OLD = re.compile(r'<div class="v-lit" id="vLit" aria-hidden="true">(<picture>.*?</picture>)</div>', re.S)

HOME_LIT = ('<div class="hero-lit" id="heroLit"></div>',
            '<div class="hero-lens" id="heroLens" aria-hidden="true" data-src="img/hero-lit.webp"><div class="hero-lens-img"></div></div>')
HOME_PRELOAD = [('<link rel="preload" href="img/hero.webp" as="image" media="(min-width:761px)">',
                 '<link rel="preload" href="img/hero-dim.webp" as="image" media="(min-width:761px)">'),
                ('<link rel="preload" href="img/hero-m.webp" as="image" media="(max-width:760px)">',
                 '<link rel="preload" href="img/hero-m-dim.webp" as="image" media="(max-width:760px)">')]


# ---------------------------------------------------------------- стили: те же замены, что в style.css репозитория
def hunks(old, new, split):
    """Точечные замены old → new. Для каждого изменённого куска — варианты с соседними неизменными кусками до и после
    (сначала самые короткие), в каждом прежний текст встречается в old ровно один раз; choose() берёт первый вариант,
    который ровно один раз встречается и в правимом файле (на рабочем сайте соседние правила могут быть другими)."""
    a, b = split(old), split(new)
    assert ''.join(a) == old and ''.join(b) == new
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        variants = []
        for n in range(0, 12):
            for kp in range(n + 1):
                kq = n - kp
                pre, post = ''.join(a[max(0, i1 - kp):i1]), ''.join(a[i2:i2 + kq])
                x, y = pre + ''.join(a[i1:i2]) + post, pre + ''.join(b[j1:j2]) + post
                if x and y and old.count(x) == 1 and new.count(y) == 1 and [x, y] not in variants:
                    variants.append([x, y])
        assert variants, 'не удалось сделать замену однозначной: %r' % ''.join(a[i1:i2])[:80]
        out.append(variants)
    return out


def choose(target, variants, what):
    """Первый вариант замены, прежний текст которого ровно один раз встречается в target."""
    for x, y in variants:
        if target.count(x) == 1 and target.replace(x, y).count(y) == 1:
            return x, y
    raise AssertionError('%s: в файле нет места для замены %r' % (what, variants[0][0][:80]))


def css_lines(s):
    return s.splitlines(keepends=True)


def css_rules(s):
    return [x for x in re.split(r'(?<=\})', s) if x]


def style_hunks():
    """Замены для style.css рабочего сайта: style.css репозитория до выпуска → после (по строкам)."""
    return hunks(git_old('style.css'), (ROOT / 'style.css').read_text(encoding='utf-8'), css_lines)


def home_css_hunks():
    """Замены для встроенных стилей главной: те же правки в стилях, сжатых esbuild, как их встраивает tools/build.py."""
    old = esbuild(git_old('style.css'), 'css')
    new = esbuild((ROOT / 'style.css').read_text(encoding='utf-8'), 'css')
    return hunks(old, new, css_rules)


# ---------------------------------------------------------------- правки страницы
def page_edits(s, old_v, new_v=NEW_V, home_css=None):
    """Список замен [было, стало, сколько раз] для страницы (исходник index.html или index.php с сайта)."""
    edits = []

    def add(old, new, count=1):
        assert old != new and s.count(old) == count, 'ожидалось %d совпадений, найдено %d: %r' % (count, s.count(old), old[:80])
        assert s.replace(old, new).count(new) == count, 'новый текст уже есть на странице: %r' % new[:80]  # иначе не отменить
        edits.append([old, new, count])

    n = s.count('?v=' + old_v)
    assert n >= 1 and '?v=' + new_v not in s, 'версия: ?v=%s — %d раз' % (old_v, n)
    add('?v=' + old_v, '?v=' + new_v, n)
    if HEAD_OLD in s:
        add(HEAD_OLD, HEAD_NEW)
    if '<script id="hero-in">' in s:
        add(HERO_IN[0], HERO_IN[1])
    if '<style data-fx>' in s:
        lit = '.fx-lit{' in s
        if lit:  # без лупы — только подсветка карточек, её стили прежние
            add(FX_STYLE[lit][0], FX_STYLE[lit][1])
        else:
            assert s.count(FX_STYLE[lit][0]) == 1, 'стили tools/site/fx.py — не прежние'
        add(FX_SCRIPT_ALT if lit and FX_SCRIPT_ALT in s else FX_SCRIPT[lit][0], FX_SCRIPT[lit][1])
        if lit:
            found = FX_LIT_OLD.findall(s)
            assert len(found) == 1, 'лупа: разметка %d раз' % len(found)
            add('<div class="fx-lit" aria-hidden="true">' + found[0] + '</div>',
                '<div class="fx-lit" aria-hidden="true"><div class="fx-lit-in">' + found[0] + '</div></div>')
    if 'id="vLit"' in s:
        add(VENT_JS[0], VENT_JS[1])
        add(VENT_CSS[0], VENT_CSS[1])
        found = VENT_LIT_OLD.findall(s)
        assert len(found) == 1, 'вентиляция: разметка лупы %d раз' % len(found)
        add('<div class="v-lit" id="vLit" aria-hidden="true">' + found[0] + '</div>',
            '<div class="v-lit" id="vLit" aria-hidden="true"><div class="v-lit-in">' + found[0] + '</div></div>')
    if 'id="heroLit"' in s:
        add(*HOME_LIT)
        for a, b in HOME_PRELOAD:
            add(a, b)
        for variants in (home_css or []):
            add(*choose(s, variants, 'встроенные стили главной'))
    return edits


def apply(s, edits):
    for a, b, count in edits:
        assert s.count(a) == count, 'число совпадений изменилось: %r' % a[:80]
        s = s.replace(a, b)
    return s


def revert(s, edits):
    for a, b, count in reversed(edits):
        s = s.replace(b, a)
    return s


def problems(s):
    """Что на странице не по новой разметке (пустой список — порядок)."""
    bad = []
    for old in ('id="heroLit"', '.hero-lit{', 'class="hero-lit"', 'var sx=cx,sy=cy', '--sr,320px', "d.classList.add('js');\n    try {"):
        if old in s:
            bad.append('осталось прежнее: ' + old)
    if HEAD_OLD in s and HEAD_NEW not in s:
        bad.append('скрипт в <head> без window.pcFx')
    if '<script id="hero-in">' in s and HERO_IN[1] not in s:
        bad.append('вход первого экрана — не нынешний tools/site/hero_in.js')
    if '<style data-fx>' in s:
        lit = '.fx-lit{' in s
        if FX_STYLE[lit][1] not in s or FX_SCRIPT[lit][1] not in s:
            bad.append('стили или скрипт tools/site/fx.py — не нынешние')
        if lit and s.count('<div class="fx-lit" aria-hidden="true"><div class="fx-lit-in"><picture>') != 1:
            bad.append('разметка лупы — не нынешняя')
    if 'id="vLit"' in s and (VENT_JS[1] not in s or VENT_CSS[1] not in s or 'id="vLit" aria-hidden="true"><div class="v-lit-in">' not in s):
        bad.append('лупа вентиляции — не нынешняя')
    if 'id="heroLens"' in s and not all(b in s for a, b in HOME_PRELOAD):
        bad.append('главная: предзагрузка фото первого экрана — прежняя')
    return bad


def pages():
    for p in sorted(ROOT.rglob('index.html')):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield p, rel


def has_v(s):
    return any('?v=' + v in s for v in (NEW_V,) + LATER_V)


def main(argv):
    check = '--check' in argv
    bad = changed = 0
    for p, rel in pages():
        s = p.read_text(encoding='utf-8')
        if check:
            errs = problems(s)
            if not has_v(s):
                errs.append('версия не ' + ' и не '.join((NEW_V,) + LATER_V))
            for e in errs:
                print('НАРУШЕНИЕ %s: %s' % (rel, e))
            bad += bool(errs)
            continue
        if has_v(s) and not problems(s):
            continue  # уже по-новому
        edits = page_edits(s, REPO_OLD_V, home_css=home_css_hunks() if 'id="heroLit"' in s else None)
        new = apply(s, edits)
        assert revert(new, edits) == s, rel + ': правки необратимы'
        assert not problems(new), rel + ': ' + '; '.join(problems(new))
        p.write_text(new, encoding='utf-8')
        changed += 1
        print('лупа и облегчённый режим: %s (%d замен)' % (rel, len(edits)))
    if check:
        print('OK: лупа и облегчённый режим на всех страницах' if not bad else 'страниц с ошибками: %d' % bad)
        return 1 if bad else 0
    print('страниц изменено: %d' % changed)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
