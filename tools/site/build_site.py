#!/usr/bin/env python3
"""Полная сборка сайта site06122026v1 из страниц репозитория.

    python3 tools/site/build_site.py

По шагам:
  1. tools/site/unify.py        — анимации и заголовки в стиле главной, бегущая строка, «Смотрите также», ссылки «Подробнее»;
  2. tools/site/legal_pages.py  — шапка и подвал сайта на страницах политики и согласия;
  3. tools/menu/apply_menu.py   — одинаковые шапка, мобильное меню и подвал на всех страницах;
  4. tools/build.py             — сжатие app.js в app.min.js и встраивание style.css в главную;
  5. server/sitemap.xml         — все страницы сайта для поисковиков.

Счётчики (Метрика, UIS, Radist) в репозитории не вставляются — они в server/counters.html
и добавляются только в версию для Timeweb: python3 tools/site/build_prod.py.
"""
import datetime
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SITEMAP = [  # адрес, приоритет
    ('', '1.0'),
    ('deratizatsiya/', '0.9'), ('dezinsektsiya/', '0.9'), ('dogovor-deratizatsiya-dezinsektsiya/', '0.9'),
    ('ochistka-dezinfektsiya-ventilyatsii/', '0.9'),
    ('pishchevoe-proizvodstvo/', '0.8'), ('magaziny-i-torgovye-seti/', '0.8'),
    ('materialy/', '0.6'), ('materialy/programma-pest-kontrolya/', '0.7'),
    ('materialy/zhurnal-pest-kontrolya/', '0.7'), ('materialy/pest-menedzhment-ili-razovaya-obrabotka/', '0.7'),
]


def run(*args):
    r = subprocess.run([sys.executable, *args], cwd=ROOT)
    if r.returncode:
        sys.exit(f'ошибка: {" ".join(args)}')


def main():
    run('tools/site/unify.py')
    run('tools/site/legal_pages.py')
    run('tools/menu/apply_menu.py')
    run('tools/build.py')
    today = datetime.date.today().isoformat()
    urls = ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{p}</priority>\n  </url>\n' for u, p in SITEMAP)
    (ROOT / 'server' / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n', encoding='utf-8')
    print('server/sitemap.xml:', len(SITEMAP), 'страниц')


if __name__ == '__main__':
    main()
