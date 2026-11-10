#!/usr/bin/env python3
"""Полная сборка сайта site06122026v1 из страниц репозитория.

    python3 tools/site/build_site.py

По шагам:
  0. tools/gostinitsy/build_page.py — страница «Пест-контроль гостиниц и отелей» из своих исходников;
     tools/sanitarnyy-audit/build_page.py — страница «Санитарный аудит (СЭС-аудит)» из своих исходников;
     tools/razrabotka-ppk/build_page.py — страница «Разработка ППК» из своих исходников;
     tools/laboratornye-issledovaniya/build_page.py — «Лабораторные исследования» (с 10.11.2026);
     tools/dezinfektsiya/build_page.py — страница «Дезинфекция для организаций» из своих исходников;
     tools/normativnaya-baza/build_pages.py — раздел «Нормативная база» (хаб, «Проверочные листы 2026»
       и «Документы для Роспотребнадзора»);
  1. tools/site/unify.py        — анимации и заголовки в стиле главной, бегущая строка, «Смотрите также», ссылки «Подробнее»;
  2. tools/site/legal_pages.py  — шапка и подвал сайта на страницах политики и согласия;
  3. tools/menu/apply_menu.py   — одинаковые шапка, мобильное меню и подвал на всех страницах;
     tools/site/mobile_crumbs.py — хлебные крошки на телефоне (до 900 px) скрыты на всех страницах;
     tools/site/table_inset.py — отступ первой и последней колонки таблиц от края (шире 900 px) на всех страницах;
     tools/site/hero_fold.py   — кнопки первого экрана целиком видны на телефонах, планшетах и ноутбуках;
     tools/site/required_marks.py — звёздочка « *» у обязательных полей во всех формах заявки;
  4. tools/build.py             — сжатие app.js в app.min.js и встраивание style.css в главную;
     tools/search/build_index.py — поиск по сайту: search-index.json из готовых страниц и search.min.js;
  5. server/sitemap.xml         — все страницы сайта для поисковиков. Дата изменения (lastmod) берётся из прежнего
     server/sitemap.xml и меняется на сегодняшнюю только у страниц, которые эта сборка изменила, и у новых адресов
     (до 08.11.2026 каждая сборка ставила сегодняшнюю дату всем страницам). --keep-lastmod — не менять даты вовсе
     (например, если поменялись только меню и подвал).

Счётчики (Метрика, UIS, Radist) в репозитории не вставляются — они в server/counters.html
и добавляются только в версию для Timeweb: python3 tools/site/build_prod.py.
"""
import datetime
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SITEMAP = [  # адрес, приоритет
    ('', '1.0'),
    ('dezinfektsiya/', '0.9'), ('deratizatsiya/', '0.9'), ('dezinsektsiya/', '0.9'), ('sanitarnyy-audit/', '0.9'), ('razrabotka-ppk/', '0.9'), ('laboratornye-issledovaniya/', '0.9'), ('dogovor-deratizatsiya-dezinsektsiya/', '0.9'),
    ('ochistka-dezinfektsiya-ventilyatsii/', '0.9'),
    ('pishchevoe-proizvodstvo/', '0.8'), ('restorany-i-kafe/', '0.8'), ('magaziny-i-torgovye-seti/', '0.8'), ('gostinitsy/', '0.8'), ('farmatsevticheskie-proizvodstva/', '0.8'), ('sklady-i-logistika/', '0.8'),
    ('materialy/', '0.6'), ('materialy/programma-pest-kontrolya/', '0.7'),
    ('materialy/zhurnal-pest-kontrolya/', '0.7'), ('materialy/pest-menedzhment-ili-razovaya-obrabotka/', '0.7'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp/', '0.7'),
    ('normativnaya-baza/', '0.7'), ('normativnaya-baza/proverochnye-listy/', '0.7'),
    ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '0.7'),
]


def run(*args):
    r = subprocess.run([sys.executable, *args], cwd=ROOT)
    if r.returncode:
        sys.exit(f'ошибка: {" ".join(args)}')


def page_hash(u):
    f = ROOT / u / 'index.html'
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None


def old_lastmod():
    f = ROOT / 'server' / 'sitemap.xml'
    if not f.exists():
        return {}
    pairs = re.findall(r'<loc>([^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>', f.read_text(encoding='utf-8'))
    return {loc[len(SITE):]: lm for loc, lm in pairs if loc.startswith(SITE)}


def main():
    keep = '--keep-lastmod' in sys.argv[1:]
    before = {u: page_hash(u) for u, _ in SITEMAP}
    run('tools/gostinitsy/build_page.py')  # страница гостиниц собирается из своих исходников (tools/gostinitsy)
    run('tools/sanitarnyy-audit/build_page.py')  # санитарный аудит — из своих исходников (tools/sanitarnyy-audit)
    run('tools/razrabotka-ppk/build_page.py')  # разработка ППК — из своих исходников (tools/razrabotka-ppk)
    run('tools/laboratornye-issledovaniya/build_page.py')  # «Лабораторные исследования» — из своих исходников (с 10.11.2026)
    run('tools/sklady/assemble.py')  # страница складов и логистики — из своих исходников (tools/sklady)
    run('tools/dezinfektsiya/build_page.py')  # дезинфекция для организаций — из своих исходников (tools/dezinfektsiya)
    run('tools/normativnaya-baza/build_pages.py')  # нормативная база и проверочные листы (tools/normativnaya-baza)
    run('tools/site/unify.py')
    run('tools/site/legal_pages.py')
    run('tools/menu/apply_menu.py')
    run('tools/site/mobile_crumbs.py')  # хлебные крошки на телефоне не показываются (правило владельца)
    run('tools/site/table_inset.py')  # отступ текста в таблицах от края (правило владельца, 10.11.2026)
    run('tools/site/hero_fold.py')  # кнопки первого экрана видны целиком на любом экране (правило владельца, 10.11.2026)
    run('tools/site/required_marks.py')  # звёздочки у обязательных полей во всех формах (правило владельца, 10.11.2026)
    run('tools/build.py')
    run('tools/search/build_index.py')  # поиск по сайту: индекс из готовых страниц (после меню и разметки)
    today = datetime.date.today().isoformat()
    old = old_lastmod()
    lastmod, fresh = {}, []
    for u, _ in SITEMAP:
        if u in old and (keep or page_hash(u) == before[u]):
            lastmod[u] = old[u]
        else:
            lastmod[u] = today
            fresh.append('/' + u)
    urls = ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{lastmod[u]}</lastmod>\n    <priority>{p}</priority>\n  </url>\n' for u, p in SITEMAP)
    (ROOT / 'server' / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n', encoding='utf-8')
    print('server/sitemap.xml:', len(SITEMAP), 'страниц;', ('дата изменения ' + today + ': ' + ', '.join(fresh)) if fresh else 'даты изменения прежние')


if __name__ == '__main__':
    main()
