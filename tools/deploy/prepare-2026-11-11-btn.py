#!/usr/bin/env python3
"""Кнопки с ровным контуром для Timeweb: правит свежие копии живых файлов (backup/).

  * style.css — в конец дописывается блок «Кнопки: ровный контур» из style.css репозитория (байт в байт);
  * главная (стили встроены) — тот же блок, сжатый, отдельным <style id="btn-st"> перед <style id="m-crumbs"> / <!-- UIS -->;
  * все страницы — версия стилей и скриптов ?v=20261111kursor → ?v=20261111btn (сброс кэша).
Всё остальное — байт в байт; счётчики по закону владельца до и после. Манифест: сначала style.css, потом страницы.
Запуск: python3 tools/deploy/prepare-2026-11-11-btn.py <папка с backup/ и pages.txt>
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import tracking_laws  # noqa: E402

OLD_V, NEW_V = '20261111kursor', '20261111btn'
MARK = '/* ===== Кнопки: ровный контур (11.11.2026) ====='


def sha(b):
    return hashlib.sha256(b).hexdigest()


def block():
    css = (ROOT / 'style.css').read_text(encoding='utf-8')
    i = css.index(MARK)
    return '\n' + css[i:].rstrip('\n') + '\n'


def minified(b):
    out = subprocess.run(['npx', '--yes', 'esbuild@0.24.2', '--minify', '--loader=css', '--charset=utf8', '--log-level=warning'],
                         input=b, capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()
    assert out and '.mbar .c1' in out
    return out


def main():
    work = pathlib.Path(sys.argv[1]).resolve()
    pages = (work / 'pages.txt').read_text(encoding='utf-8').split('\n')[:-1]
    blk = block()
    mini = '<style id="btn-st">' + minified(blk) + '</style>'
    manifest, report = [], []

    def emit(rel, original, result):
        out = work / 'pkg' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(result)
        manifest.append(f'{sha(original)}  {sha(result)}  {rel}')
        report.append({'file': rel, 'before': sha(original), 'after': sha(result)})

    css_old = (work / 'backup/style.css').read_bytes()
    css = css_old.decode('utf-8')
    assert MARK not in css, 'на сайте блок уже есть'
    emit('style.css', css_old, (css.rstrip('\n') + '\n' + blk).encode('utf-8'))

    for p in pages:
        original = (work / 'backup' / p / 'index.php').read_bytes()
        text = original.decode('utf-8')
        cnt = p not in ('privacy/', 'soglasie/')
        assert not tracking_laws.check_page(text, counters=cnt), p + ': живая страница нарушает закон о счётчиках'
        assert NEW_V not in text
        result = text.replace('?v=' + OLD_V, '?v=' + NEW_V)
        if p == '':
            assert 'id="btn-st"' not in result and 'style.css' not in result
            head = result[:result.index('</head>')]
            mark = '<style id="m-crumbs">' if '<style id="m-crumbs">' in head else '<!-- UIS -->'
            assert mark in head
            result = result.replace(mark, mini + mark, 1)
            assert '</style></head>' not in result.replace(mini, '')
        if result == text:
            continue
        assert not tracking_laws.check_page(result, counters=cnt), p + ': правка нарушает закон о счётчиках'
        back = result.replace(mini, '').replace('?v=' + NEW_V, '?v=' + OLD_V)
        assert back == text, p + ': изменения вне согласованных мест'
        emit(p + 'index.php', original, result.encode('utf-8'))

    (work / 'MANIFEST.txt').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
    (work / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('файлов в пакете:', len(manifest), '(style.css +', len(manifest) - 1, 'страниц)')


if __name__ == '__main__':
    main()
