#!/usr/bin/env python3
"""Пакет из текущих файлов сайта: вход первого экрана без ожидания скриптов анимаций и счётчиков (11.11.2026).

  1. На каждой странице с первым экраном сразу после его </section> — <script id="hero-in"> (tools/site/hero_in.js):
     вход первого экрана рисуют анимации браузера сразу при разборе страницы, а не app.js после загрузки GSAP.
  2. style.css — в конце правила класса hero-in (снимают начальные состояния первого экрана); на главной те же правила
     дописаны в конец встроенных стилей. app.min.js — сборка app.js: при window.pcHero первый экран не трогает.
  3. Версия style.css и app.min.js в ссылках страниц — новая (на сайте они кэшируются на год).
  4. Загрузчик GSAP, ScrollTrigger, Lenis и app.min.js в конце страницы начинает загрузку после того, как браузер показал
     первую отрисовку (FCP, Paint Timing; без неё — после первого кадра, как раньше; страховка — 3 с). Счётчиков это
     не касается: Метрика, UIS и Radist стоят на своих местах и грузятся сразу (закон владельца).
Счётчики, телефон, почта и всё остальное на страницах — байт в байт как на сайте (проверяется: страница без скрипта входа,
номера версии, правил hero-in и с прежним загрузчиком совпадает с копией сайта; закон владельца — tracking_laws.check_page).
Сначала загружаются style.css и app.min.js (они совместимы и со старыми страницами), потом страницы.

    python3 tools/deploy/prepare-2026-11-11-hero.py <копия-страниц-сайта> <копия-статики-сайта> <папка-выкладки>
"""
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402  список страниц сайта
import hero_in  # noqa: E402  вход первого экрана
import tracking_laws as T  # noqa: E402  закон владельца
import unify  # noqa: E402  загрузчик скриптов анимаций (LOADER)

NAME = 'pestcontrol-deploy-2026-11-11-hero'
VERSION = '20261111hero'
VER_RE = re.compile(r'((?:style\.css|app\.min\.js)\?v=)[A-Za-z0-9]+')
BLOCK_RE = re.compile(r'(<!-- style:start --><style>)(.*?)(</style><!-- style:end -->)', re.S)
MARK = '/* ===== Вход первого экрана'
# прежний загрузчик скриптов анимаций (до 11.11.2026) и новый — из tools/site/unify.py (LOADER)
LOADER_OLD = ("    var go = function () { l.forEach(function (u) { var e = document.createElement('script'); e.src = r + u; e.async = false; document.body.appendChild(e); }); };\n"
              "    if (document.visibilityState === 'hidden' || !window.requestAnimationFrame) setTimeout(go, 0);\n"
              "    else requestAnimationFrame(function () { setTimeout(go, 0); });\n")
_L = unify.LOADER
LOADER_NEW = _L[_L.index('    var go = '):_L.index("  })('{root}'")]
assert LOADER_NEW != LOADER_OLD and 'PerformanceObserver' in LOADER_NEW


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esbuild_css(text):
    res = subprocess.run(hero_in.ESBUILD + ['--minify', '--loader=css', '--charset=utf8', '--log-level=warning'],
                         input=text, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit('esbuild: ' + res.stderr)
    return res.stdout.strip()


def main():
    src, static, dst = map(pathlib.Path, sys.argv[1:4])
    js = hero_in.minified()
    parts = T.counter_parts()

    # ---- статика: на сайте должна быть та же, что в репозитории до этой правки (иначе в пакет попало бы чужое)
    css_new = (ROOT / 'style.css').read_text(encoding='utf-8')
    i = css_new.index(MARK)
    css_add = css_new[i:]
    live_css = (static / 'style.css').read_text(encoding='utf-8')
    assert live_css.rstrip() == css_new[:i].rstrip(), 'style.css на сайте не совпадает с репозиторием до правки'
    head_app = subprocess.run(['git', 'show', 'HEAD:app.min.js'], cwd=ROOT, capture_output=True).stdout
    assert head_app and (static / 'app.min.js').read_bytes() == head_app, 'app.min.js на сайте не совпадает с репозиторием (HEAD)'
    rules_min = esbuild_css(css_add)
    assert rules_min.startswith('html.js.hero-in') and len(rules_min) < 600, rules_min

    pages = [r.replace('index.html', 'index.php') for r in build_prod.PAGES + build_prod.LEGAL]
    present = [p for p in pages if (src / p).exists()]
    print('нет на сайте (в пакет не входят):', ', '.join(sorted(set(pages) - set(present))) or '—')
    if (dst / 'pkg').exists():
        shutil.rmtree(dst / 'pkg')
    (dst / 'pkg').mkdir(parents=True)

    order, before, after = [], [], []
    for name in ('style.css', 'app.min.js'):  # сначала статика: она совместима и со старыми страницами
        old = (static / name).read_bytes()
        new = (ROOT / name).read_bytes()
        (dst / 'pkg' / name).write_bytes(new)
        order.append(name)
        before.append(sha(old) + '  ' + name)
        after.append(sha(new) + '  ' + name)
        print(f'{name}: {len(new) - len(old):+d} байт')

    for path in present:
        data = (src / path).read_bytes()
        s = data.decode('utf-8')
        legal = path in T.NO_COUNTERS
        new = hero_in.apply(s, js)
        nl = new.count(LOADER_OLD)
        assert nl == (0 if legal else 1), (path, 'прежних загрузчиков скриптов анимаций', nl)
        new = new.replace(LOADER_OLD, LOADER_NEW)
        new, nv = VER_RE.subn(lambda m: m.group(1) + VERSION, new)
        if path == 'index.php':
            m = BLOCK_RE.search(new)
            assert m and MARK not in m.group(2) and 'hero-in' not in m.group(2), 'главная: нет встроенных стилей или правила уже есть'
            new = new[:m.end(2)] + rules_min + new[m.end(2):]
        # кроме скрипта входа, версий и правил hero-in — всё байт в байт как на сайте
        back = hero_in.OLD.sub('', new).replace(rules_min, '').replace(LOADER_NEW, LOADER_OLD)
        assert VER_RE.sub(r'\g<1>X', back) == VER_RE.sub(r'\g<1>X', s), path + ': изменилось что-то лишнее'
        bad = T.check_page(new, counters=not legal, parts=parts)
        assert not bad, (path, bad)
        if not legal:
            for k in ('metrika', 'uis', 'noscript', 'radist'):
                assert s.count(parts[k]) == 1 and new.count(parts[k]) == 1, (path, k)
        has_hero = hero_in.hero_end(s) is not None
        assert has_hero == (not legal), (path, 'первый экран')
        assert hero_in.check(new, js) == [], (path, hero_in.check(new, js))
        assert nv >= 1, (path, 'нет ссылок style.css / app.min.js с версией')
        b = new.encode('utf-8')
        out = dst / 'pkg' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b)
        order.append(path)
        before.append(sha(data) + '  ' + path)
        after.append(sha(b) + '  ' + path)
        print(f'{path}: {len(b) - len(data):+d} байт; версий заменено {nv}'
              + ('' if legal else '; скрипт входа после первого экрана; загрузчик после FCP; счётчики байт в байт'))

    config = (
        '# Вход первого экрана без ожидания скриптов анимаций и счётчиков; загрузчик анимаций после FCP (11.11.2026).\n'
        '# Пакет из текущих файлов сайта (tools/deploy/prepare-2026-11-11-hero.py). Счётчики не меняются.\n'
        f'NAME="{NAME}"\nBK="before-hero_2026-11-11_ftp.zip"\n'
        'ORDER="' + '\n'.join(order) + '"\n'
        'REPLACED="' + ' '.join(order) + '"\n'
        'EXPECTED_BEFORE="' + '\n'.join(before) + '"\n'
        'CHECK_DIRS="privacy soglasie materialy normativnaya-baza laboratornye-issledovaniya"\n'
    )
    (dst / 'deploy.conf').write_text(config, encoding='utf-8')
    (dst / 'MANIFEST.sha256').write_text('\n'.join(after) + '\n', encoding='utf-8')
    shutil.copy2(ROOT / 'tools/deploy/run_all.sh', dst / 'run_all.sh')
    launch = ROOT / 'tools/deploy/launch-2026-11-11-hero.sh'
    if launch.exists():
        shutil.copy2(launch, dst / 'launch.sh')
    print(f'готово: {len(order)} файлов в {dst}/pkg (статика — первой)')


if __name__ == '__main__':
    main()
