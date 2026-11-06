#!/usr/bin/env python3
"""Версия сайта для рабочего хостинга Timeweb (пестконтроль-центр.рф) — со всеми счётчиками.

    python3 tools/site/build_prod.py          → папка dist/timeweb/ (в репозиторий не попадает)

Что меняется по сравнению с превью на GitHub Pages:
  * каждая страница сохраняется как index.php, перед </body> вставляется блок server/counters.html
    (Яндекс Метрика 113675622 с Вебвизором, колл-трекинг UIS с подменой номера, Radist для Telegram и MAX) —
    тот же блок, что стоит на рабочей главной;
  * убирается <meta name="robots" content="noindex, nofollow"> — он нужен только превью;
    страницы политики и согласия остаются «noindex, follow», как на рабочем сайте, и без счётчиков (как сейчас);
  * рядом кладутся .htaccess, robots.txt и sitemap.xml из server/.

send.php и composer.json в пакет НЕ входят: на сервере уже стоит send.php с настоящим паролем почты,
его нельзя перезаписывать версией из репозитория (в ней пароль заменён заглушкой).
Перед выкладкой: если в папке страницы на сервере лежит index.html, его нужно убрать — иначе сервер
может отдать его вместо index.php.
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OUT = ROOT / 'dist' / 'timeweb'
COUNTERS_MARK = '<!-- Yandex.Metrika counter + UIS + Radist'
PAGES = [
    'index.html', 'deratizatsiya/index.html', 'dezinsektsiya/index.html', 'dogovor-deratizatsiya-dezinsektsiya/index.html',
    'ochistka-dezinfektsiya-ventilyatsii/index.html',
    'pishchevoe-proizvodstvo/index.html', 'restorany-i-kafe/index.html', 'magaziny-i-torgovye-seti/index.html', 'farmatsevticheskie-proizvodstva/index.html', 'materialy/index.html', 'materialy/programma-pest-kontrolya/index.html',
    'materialy/zhurnal-pest-kontrolya/index.html', 'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html',
]
LEGAL = ['privacy/index.html', 'soglasie/index.html']
STATIC = ['style.css', 'legal.css', 'app.min.js', 'vendor', 'fonts', 'img']
FILES = ['*.pdf', '*.docx']  # образцы документов рядом со страницами
SERVER = ['.htaccess', 'robots.txt', 'sitemap.xml']
ROBOTS_RE = re.compile(r'<meta name="robots" content="noindex, nofollow">(?:<!--[^>]*-->)?\n?')


def counters():
    c = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    i = c.index(COUNTERS_MARK)
    block = c[i:].strip()
    for need in ("ym(113675622, 'init'", 'uiscom', 'radist', '<!-- /Yandex.Metrika counter -->'):
        assert need in block, 'в server/counters.html нет ' + need
    return block


def main():
    block = counters()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for rel in PAGES + LEGAL:
        s = (ROOT / rel).read_text(encoding='utf-8')
        assert COUNTERS_MARK not in s, rel + ': счётчики уже в HTML — в репозитории их быть не должно'
        if rel in LEGAL:
            s, n = ROBOTS_RE.subn('<meta name="robots" content="noindex, follow">\n', s, count=1)
        else:
            s, n = ROBOTS_RE.subn('', s, count=1)
            s = s.replace('</body>', block + '\n</body>', 1)
            assert s.count("ym(113675622, 'init'") == 1, rel
        assert n == 1, rel + ': нет метки robots превью'
        dst = OUT / rel.replace('index.html', 'index.php')
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(s, encoding='utf-8')
        print('страница', dst.relative_to(OUT), '(со счётчиками)' if rel not in LEGAL else '(документ, без счётчиков)')
    for name in STATIC:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, OUT / name)
        else:
            shutil.copy2(src, OUT / name)
    for pat in FILES:
        for f in ROOT.rglob(pat):
            if any(p in f.parts for p in ('.git', 'dist', 'tools', 'server')):
                continue
            d = OUT / f.relative_to(ROOT)
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
    for name in SERVER:
        shutil.copy2(ROOT / 'server' / name, OUT / name)
    n = sum(1 for _ in OUT.rglob('*') if _.is_file())
    size = sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())
    print(f'готово: {OUT.relative_to(ROOT)} — {n} файлов, {size / 1048576:.1f} МБ')


if __name__ == '__main__':
    sys.exit(main())
