#!/usr/bin/env python3
"""Версия сайта для рабочего хостинга Timeweb (пестконтроль-центр.рф) — со всеми счётчиками.

    python3 tools/site/build_prod.py          → папка dist/timeweb/ (в репозиторий не попадает)

Что меняется по сравнению с превью на GitHub Pages:
  * каждая страница сохраняется как index.php со счётчиками из server/counters.html — по ЗАКОНУ ВЛАДЕЛЬЦА
    (tools/site/tracking_laws.py, с 11.11.2026): Яндекс Метрика 113675622 с Вебвизором — в <head> сразу после
    <meta name="viewport">, UIS — прямо перед </head>, <noscript> Метрики — сразу после <body>, Radist — в конце <body>.
    Все коды официальные и грузятся сразу вместе со страницей, без отложенной загрузки. Телефон и почта в ссылках —
    без лишних тегов и неразрывных пробелов. Страница, нарушающая закон, в сборку не попадает (сборка останавливается);
  * убирается <meta name="robots" content="noindex, nofollow"> — он нужен только превью;
    страницы политики и согласия остаются «noindex, follow», как на рабочем сайте, и без счётчиков (как сейчас);
  * рядом кладутся .htaccess, robots.txt, sitemap.xml и файл ключа IndexNow (<ключ>.txt, с 11.11.2026) из server/.

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
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import tracking_laws  # noqa: E402  закон владельца: счётчики сразу, телефон и почта без лишних тегов (11.11.2026)

OUT = ROOT / 'dist' / 'timeweb'
PAGES = [
    'index.html', 'dezinfektsiya/index.html', 'deratizatsiya/index.html', 'zashchita-ot-proniknoveniya-gryzunov/index.html', 'dezinsektsiya/index.html', 'deratizatsiya-i-dezinsektsiya/index.html', 'dogovor-deratizatsiya-dezinsektsiya/index.html',
    'sanitarnyy-audit/index.html', 'razrabotka-ppk/index.html', 'laboratornye-issledovaniya/index.html', 'ochistka-dezinfektsiya-ventilyatsii/index.html',
    'pishchevoe-proizvodstvo/index.html', 'restorany-i-kafe/index.html', 'magaziny-i-torgovye-seti/index.html', 'gostinitsy/index.html', 'farmatsevticheskie-proizvodstva/index.html', 'sklady-i-logistika/index.html',
    'biznes-tsentry-torgovye-tsentry-predpriyatiya/index.html',  # с 11.11.2026 (tools/bctc)
    'materialy/index.html', 'materialy/programma-pest-kontrolya/index.html',
    'materialy/zhurnal-pest-kontrolya/index.html', 'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html',
    'normativnaya-baza/index.html', 'normativnaya-baza/proverochnye-listy/index.html',
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html',
    'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.html',  # с 11.11.2026
    'materialy/akt-deratizatsii-i-dezinsektsii/index.html', 'materialy/skhema-tochek-pest-kontrolya/index.html',  # акт и схема точек, с 11.11.2026
    # страницы направлений и статьи раздела «Лабораторные исследования» (с 11.11.2026)
    # страницы «услуга + сфера» для общепита (с 11.11.2026)
    'dezinsektsiya/restorany-i-kafe/index.html', 'deratizatsiya/restorany-i-kafe/index.html',
    'laboratornye-issledovaniya/analiz-smyvov/index.html',
    'laboratornye-issledovaniya/izmerenie-mikroklimata/index.html',
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.html',
    'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/index.html',
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.html',
    'laboratornye-issledovaniya/analiz-vody/index.html',
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.html',
    'materialy/kak-berut-smyvy/index.html',
    'materialy/zamer-osveshchennosti-i-mikroklimata/index.html',
    'materialy/kontrol-raboty-sterilizatorov/index.html',
]
LEGAL = ['privacy/index.html', 'soglasie/index.html']
STATIC = ['style.css', 'legal.css', 'app.min.js', 'search.min.js', 'search-index.json', 'vendor', 'fonts', 'img']
FILES = ['*.pdf', '*.docx']  # образцы документов рядом со страницами
# 6e3f9d70….txt — ключ IndexNow для Яндекса (с 11.11.2026, в корне сайта; отправка адресов — tools/seo/indexnow.py)
SERVER = ['.htaccess', 'robots.txt', 'sitemap.xml', '6e3f9d70b48c34299ede4719e3b5e4a1.txt']
ROBOTS_RE = re.compile(r'<meta name="robots" content="noindex, nofollow">(?:<!--[^>]*-->)?\n?')


def main():
    parts = tracking_laws.counter_parts()  # части server/counters.html: metrika, uis, noscript, radist
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for rel in PAGES + LEGAL:
        s = (ROOT / rel).read_text(encoding='utf-8')
        assert not any(k in s for k in tracking_laws.LEFTOVER), rel + ': счётчики уже в HTML — в репозитории их быть не должно'
        s = tracking_laws.normalize_contacts(s)  # телефон и почта по закону, даже если страницу собрали без build_site.py
        if rel in LEGAL:
            s, n = ROBOTS_RE.subn('<meta name="robots" content="noindex, follow">\n', s, count=1)
        else:
            s, n = ROBOTS_RE.subn('', s, count=1)
            s = tracking_laws.install_counters(s, parts)
        assert n == 1, rel + ': нет метки robots превью'
        bad = tracking_laws.check_page(s, counters=rel not in LEGAL, parts=parts)
        assert not bad, rel + ': нарушение закона владельца (tools/site/tracking_laws.py) — ' + '; '.join(bad)
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
