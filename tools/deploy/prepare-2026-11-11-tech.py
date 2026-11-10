#!/usr/bin/env python3
"""Пакет из текущих файлов сайта: оставшиеся технические правки из GitHub (без изменения текстов и оформления).

- role="group" у полосы «Коротко о ...» (подпись aria-label читается экранными дикторами) — 4 страницы;
- первый экран скрыт, пока не загружен целиком (`.d-hero:not(:has(~ *)) .wrap{visibility:hidden}`, против сдвига CLS),
  как уже работает на дератизации, дезинсекции, дезинфекции и складах — вентиляция и магазины.

python3 tools/deploy/prepare-2026-11-11-tech.py <live> <deploy-dir>
"""
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NAME = 'pestcontrol-deploy-2026-11-11-tech'
STRIP_OLD, STRIP_NEW = '<div class="strip" aria-label=', '<div class="strip" role="group" aria-label='
HERO = '.d-hero:not(:has(~ *)) .wrap{visibility:hidden}'
VENT_ANCHOR = '.d-doc .btn-lg{font-size:14px;padding:0 14px}}\n'
VENT_ADD = ('/* Первый экран: пока он не загружен целиком (после него ещё нет следующего блока), содержимое скрыто — '
            'как на главной: иначе при постепенной загрузке текст, выровненный по центру высоты экрана, сдвигается (CLS) */\n'
            + HERO + '\n\n')
MAG_ANCHOR = '.d-btns .btn{font-size:13.5px;padding:0 10px}}.f-lazy:not(.bg-in)'
PAGES = ['gostinitsy', 'magaziny-i-torgovye-seti', 'ochistka-dezinfektsiya-ventilyatsii', 'sanitarnyy-audit']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def patch(page, s):
    assert s.count(STRIP_OLD) == 1 and STRIP_NEW not in s, page
    s = s.replace(STRIP_OLD, STRIP_NEW)
    if page == 'ochistka-dezinfektsiya-ventilyatsii':
        assert HERO not in s and s.count(VENT_ANCHOR) == 1, page
        s = s.replace(VENT_ANCHOR, VENT_ANCHOR + VENT_ADD)
    if page == 'magaziny-i-torgovye-seti':
        assert HERO not in s and s.count(MAG_ANCHOR) == 1, page
        s = s.replace(MAG_ANCHOR, MAG_ANCHOR.replace('}}.f-lazy', '}}' + HERO + '.f-lazy'))
    return s


def main():
    src, dst = map(pathlib.Path, sys.argv[1:3])
    dst.mkdir(parents=True, exist_ok=True)
    order, before, after = [], [], []
    for page in PAGES:
        path = page + '/index.php'
        data = (src / path).read_bytes()
        s = data.decode('utf-8')
        new = patch(page, s)
        assert new != s
        old_c, new_c = COUNTERS.findall(s), COUNTERS.findall(new)
        assert len(old_c) == 1 and old_c == new_c, page
        for k in ('113675622', 'comagic', 'uiscom', 'radist'):
            assert s.count(k) == new.count(k), (page, k)
        assert new.rstrip().endswith('</html>'), page
        b = new.encode('utf-8')
        out = dst / 'pkg' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b)
        order.append(path)
        before.append(sha(data) + '  ' + path)
        after.append(sha(b) + '  ' + path)
        print(page, ': +', len(b) - len(data), 'байт; счётчики без изменений')
    config = (
        '# Технические правки из GitHub: role="group" у полос, первый экран без сдвига. Пакет из текущих файлов сайта.\n'
        f'NAME="{NAME}"\nBK="before-tech_2026-11-11_ftp.zip"\n'
        'ORDER="' + '\n'.join(order) + '"\n'
        'REPLACED="' + ' '.join(order) + '"\n'
        'EXPECTED_BEFORE="' + '\n'.join(before) + '"\n'
        'CHECK_DIRS="' + ' '.join(PAGES) + '"\n'
    )
    (dst / 'deploy.conf').write_text(config, encoding='utf-8')
    (dst / 'MANIFEST.sha256').write_text('\n'.join(after) + '\n', encoding='utf-8')
    shutil.copy2(ROOT / 'tools/deploy/run_all.sh', dst / 'run_all.sh')


if __name__ == '__main__':
    main()
