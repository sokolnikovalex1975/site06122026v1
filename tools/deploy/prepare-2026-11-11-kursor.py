#!/usr/bin/env python3
"""Выкладка 11.11.2026: курсор «Фирменный прицел» на всём сайте и блок «Образец план-схемы» (вариант А) на странице
«Схема точек пест-контроля». Решение владельца: «Внедряй вариант В» → «Выкладывай».

    python3 tools/deploy/prepare-2026-11-11-kursor.py <снимок сайта> <папка pkg>

<снимок сайта> — страницы (pages.txt), style.css и app.min.js, как их отдаёт сайт по HTTPS перед выкладкой. Всё правится
точечно поверх снимка (на сайте уже есть правки других выкладок, которых нет в этом репозитории, — «вход первого экрана»,
v=20261111hero), остальное остаётся байт в байт:
  * style.css — блок курсора заменяется новым (style.css репозитория); старый блок должен найтись ровно один раз;
  * app.min.js — в конец дописывается tools/deploy/kursor-addon-2026-11-11.js (сжатый esbuild): классы light / doc и подпись;
  * главная — во встроенных стилях сжатый блок курсора заменяется новым (как в index.html репозитория);
  * все страницы — style.css?v= и app.min.js?v= → 20261111kursor (иначе браузеры возьмут старые файлы из кэша);
  * «Схема точек» — разметка блока #obrazets (<figure class="nb-fig sk-fig">), стили страницы (page.css) и скрипт страницы
    (цели Метрики + план) — из сборки репозитория; «Акт» — стили страницы (общий page.css);
  * новые картинки img/skhema-obrazets-p2-{360,720}.webp.
Проверки: счётчики (Метрика 113675622, UIS, Radist) байт в байт как на сайте и по закону владельца; без noindex и ссылок на
превью; после обратной замены правленых мест страница совпадает со снимком байт в байт.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import tracking_laws  # noqa: E402

V_OLD, V_NEW = '20261111hero', '20261111kursor'
SKH, AKT = 'materialy/skhema-tochek-pest-kontrolya/', 'materialy/akt-deratizatsii-i-dezinsektsii/'
PAGE_CSS_REV = '1a8beaa'  # page.css, который сейчас на сайте (встроен в страницы «Схема» и «Акт»)
CBLOCK = re.compile(r'<!-- Yandex\.Metrika counter.*?<!-- /Yandex\.Metrika counter -->|<!-- UIS -->.*?<!-- UIS -->'
                    r'|<!-- Radist -->.*?<!-- /Radist -->|<!-- Yandex\.Metrika counter: noscript -->.*?</noscript>', re.S)
FIG = re.compile(r'<figure class="nb-fig sk-fig".*?</figure>', re.S)
PJS = re.compile(r"<script>document\.addEventListener\('click',function\(e\)\{var a=e\.target\.closest&&e\.target\.closest\('\[data-dl\]'\).*?</script>", re.S)
NO_COUNTERS = {'privacy/', 'soglasie/'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esbuild(path, css=False):
    args = ['npx', '--yes', 'esbuild@0.24.2', str(path), '--minify', '--charset=utf8', '--log-level=warning']
    args += ['--loader:.css=css'] if css else ['--target=es2015']
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def cursor_block(s):
    a = s.index('.cursor{display:none}')
    return s[a:s.index('/* ===== header ===== */', a)]


def one(s, old, new, what):
    assert s.count(old) == 1, f'{what}: найдено {s.count(old)} раз'
    return s.replace(old, new)


def main():
    live, pkg = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
    pkg.mkdir(parents=True, exist_ok=True)
    tmp = pkg.parent / 'tmp-kursor'
    tmp.mkdir(exist_ok=True)
    out = {}
    git = lambda rev, p: subprocess.run(['git', 'show', f'{rev}:{p}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout

    # 1. style.css
    old_blk = cursor_block(git('d0e2443~1', 'style.css'))
    new_blk = cursor_block((ROOT / 'style.css').read_text(encoding='utf-8'))
    css_live = (live / 'style.css').read_text(encoding='utf-8')
    out['style.css'] = one(css_live, old_blk, new_blk, 'style.css: старый блок курсора')
    # 2. app.min.js + дополнение
    addon = esbuild(ROOT / 'tools' / 'deploy' / 'kursor-addon-2026-11-11.js')
    js_live = (live / 'app.min.js').read_text(encoding='utf-8')
    assert js_live.endswith('\n') and 'cursor-lbl' not in js_live
    out['app.min.js'] = js_live + addon
    # сжатые блоки курсора для встроенных стилей главной
    (tmp / 'ob.css').write_text(old_blk, encoding='utf-8')
    (tmp / 'nb.css').write_text(new_blk, encoding='utf-8')
    ob_min, nb_min = esbuild(tmp / 'ob.css', True).strip(), esbuild(tmp / 'nb.css', True).strip()
    assert (ROOT / 'index.html').read_text(encoding='utf-8').count(nb_min) == 1, 'сжатый блок не совпадает с index.html репозитория'

    page_css_old = git(PAGE_CSS_REV, 'tools/materialy-dokumenty/page.css').strip()
    page_css_new = (ROOT / 'tools' / 'materialy-dokumenty' / 'page.css').read_text(encoding='utf-8').strip()
    pages = [l for l in (live / 'pages.txt').read_text(encoding='utf-8').split('\n') if l]
    report = []
    for f in pages:
        p = f[:-len('index.php')]
        src = live / f
        if not src.exists():
            report.append(f'нет на сайте (404): {f}')
            continue
        text = src.read_text(encoding='utf-8')
        cnt = p not in NO_COUNTERS
        assert not tracking_laws.check_page(text, counters=cnt), f + ': живая страница уже нарушает закон о счётчиках'
        s, undo = text, []
        for kind in ('style.css', 'app.min.js'):
            a, b = f'{kind}?v={V_OLD}', f'{kind}?v={V_NEW}'
            assert f'{kind}?v=' not in s.replace(a, ''), f'{f}: версия {kind} не {V_OLD}'
            if a in s:
                s = s.replace(a, b)
                undo.append((b, a))
        if f == 'index.php':
            s = one(s, ob_min, nb_min, 'главная: встроенный блок курсора')
            undo.append((nb_min, ob_min))
        if p in (SKH, AKT):
            a, b = '\n' + page_css_old + '</style>', '\n' + page_css_new + '</style>'
            s = one(s, a, b, f + ': page.css')
            undo.append((b, a))
            repo = (ROOT / p / 'index.html').read_text(encoding='utf-8')
            lj, rj = PJS.findall(s), PJS.findall(repo)
            assert len(lj) == 1 and len(rj) == 1, f + ': скрипт страницы'
            if lj != rj:
                s = one(s, lj[0], rj[0], f + ': скрипт страницы')
                undo.append((rj[0], lj[0]))
            if p == SKH:
                lf, rf = FIG.findall(s), FIG.findall(repo)
                assert len(lf) == 1 and len(rf) == 1 and 'skg-side' in rf[0] and 'sk-layout' in lf[0]
                s = one(s, lf[0], rf[0], f + ': блок #obrazets')
                undo.append((rf[0], lf[0]))
        # проверки
        assert CBLOCK.findall(s) == CBLOCK.findall(text), f + ': изменились счётчики'
        assert not tracking_laws.check_page(s, counters=cnt), f + ': правка нарушает закон о счётчиках'
        assert 'noindex' not in s or 'noindex' in text, f + ': появился noindex'
        assert 'github.io' not in s or 'github.io' in text, f + ': ссылка на превью'
        back = s
        for b, a in reversed(undo):
            assert back.count(b) >= 1
            back = back.replace(b, a)
        assert back == text, f + ': отличия вне согласованных мест'
        out[f] = s
        report.append(f'{f}: правок {len(undo)}')
    for name in ('skhema-obrazets-p2-360.webp', 'skhema-obrazets-p2-720.webp'):
        out['img/' + name] = (ROOT / 'img' / name).read_bytes()
    manifest = []
    for f, data in out.items():
        b = data.encode('utf-8') if isinstance(data, str) else data
        dst = pkg / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b)
        manifest.append(f'{sha(b)}  {f}')
    (pkg.parent / 'MANIFEST.sha256').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
    before = []
    for f in out:
        if (live / f).exists():
            before.append(f'{sha((live / f).read_bytes())}  {f}')
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text('\n'.join(before) + '\n', encoding='utf-8')
    print('\n'.join(report))
    print('файлов в пакете:', len(out), '; заменяемых:', len(before))


if __name__ == '__main__':
    main()
