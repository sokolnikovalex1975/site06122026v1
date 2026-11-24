#!/usr/bin/env python3
"""Технические правки сервера по аудиту 17.11.2026 — разрешены владельцем 18.11.2026 в 13:53 МСК, выкладка 22.11.2026.

    python3 tools/site/seo_server.py            # правит server/.htaccess и server/sitemap.xml
    python3 tools/site/seo_server.py --check    # только проверка (код 1, если правки нет)

Решение владельца 18.11.2026 (seo-agent/drafts/2026-11-17-tech-fixes.md, пп. 1, 2, 3, 7): «переадресации, index.php,
lastmod, 404». Строка Clean-param для robots.txt (п. 8) в решение не вошла — robots.txt не меняется.

.htaccess (htaccess()):
  * адрес папки без слеша — сразу https и слеш, один переход 301 вместо двух (сейчас Apache за nginx отправляет
    на http://…/папка/, затем nginx — на https);
  * /index.php и /раздел/index.php — 301 на адрес со слешем; правило срабатывает только на прямой запрос (THE_REQUEST),
    не на внутреннюю подстановку index.php, и только если такая папка есть на сайте (уточнено 22.11.2026 пакетом
    seo-2026-11-22-fix: адреса несуществующих папок снова отвечают 404, а не 301); форма отправляется на /send.php —
    её правила не касаются;
  * ErrorDocument 404 /404.html — своя страница «Страница не найдена» (tools/site/page_404.py), код ответа остаётся 404.
  Правила ставятся после запретов vendor/ внутри <IfModule mod_rewrite.c>; правило www и запреты не меняются.

sitemap.xml (sitemap()): lastmod — дата последней правки title, description, H1 или текста страницы (без шапки,
меню и подвала, как в снимках SEO-машины seo-agent/tools/site_snapshot.py). Даты сверены 22.11.2026 по снимкам
17, 18 и 20.11, пакетам выкладки 19–20.11 (backup/ и pkg/ в tools/deploy/) и копиям рабочего сайта 22.11; страницы,
которые меняет выкладка 22.11.2026 (DEPLOY_PAGES: текст, ссылки в тексте, title или разметка), получают дату выкладки.
Правки только оформления, меню и подвала lastmod не меняют. Адреса, которых нет в LASTMOD (например,
dezinfektsiya/avtotransport/ — выложена на Timeweb 23.11.2026), не трогаются. Повторный запуск ничего не меняет.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'

# ---------- .htaccess ----------
HT_ANCHOR = '  RewriteRule ^vendor/autoload\\.php$ - [F,L]\n'
HT_DIR = (
    '\n'
    '  # Адрес папки без слеша: сразу https и слеш — один переход вместо двух (решение владельца 18.11.2026)\n'
    '  RewriteCond %{REQUEST_FILENAME} -d\n'
    '  RewriteCond %{REQUEST_URI} !/$\n'
    '  RewriteRule ^(.+)$ https://%{HTTP_HOST}/$1/ [R=301,L]\n'
    '\n'
)
# Выложено 22.11.2026 в 22:29 МСК (пакет seo-2026-11-22): правило срабатывало и для папок, которых нет на сайте
# (/нет-такой-папки/index.php отвечал 301 на адрес, который отвечает 404).
HT_INDEX_2211 = (
    '  # /index.php и /раздел/index.php — на адрес со слешем (только прямой запрос, не внутренняя подстановка index.php)\n'
    '  RewriteCond %{THE_REQUEST} ^[A-Z]+\\s/(.*/)?index\\.php[\\s?] [NC]\n'
    '  RewriteRule ^(.*/)?index\\.php$ https://%{HTTP_HOST}/$1 [R=301,L,NC]\n'
)
# Уточнено 22.11.2026 (пакет seo-2026-11-22-fix): 301 только если такая папка есть на сайте, иначе — 404.
HT_INDEX = (
    '  # /index.php и /раздел/index.php — на адрес со слешем (только прямой запрос, не внутренняя подстановка index.php)\n'
    '  # и только если такая папка есть на сайте; адреса несуществующих папок отвечают 404\n'
    '  RewriteCond %{THE_REQUEST} ^[A-Z]+\\s/(.*/)?index\\.php[\\s?] [NC]\n'
    '  RewriteCond %{REQUEST_FILENAME} ^(.*/)index\\.php$ [NC]\n'
    '  RewriteCond %1 -d\n'
    '  RewriteRule ^(.*/)?index\\.php$ https://%{HTTP_HOST}/$1 [R=301,L,NC]\n'
)
HT_RULES = HT_DIR + HT_INDEX
HT_END = '</IfModule>\n'
HT_404 = ('\n# Своя страница «Страница не найдена» (tools/site/page_404.py); код ответа остаётся 404 (решение владельца 18.11.2026)\n'
          'ErrorDocument 404 /404.html\n')


def htaccess(s):
    """Правила переадресации и ErrorDocument 404; если они уже есть — файл без изменений."""
    if 'ErrorDocument 404 /404.html' in s:
        if HT_DIR + HT_INDEX_2211 in s:  # выложенная 22.11.2026 в 22:29 редакция — уточняем правило index.php
            assert s.count(HT_DIR + HT_INDEX_2211) == 1
            s = s.replace(HT_DIR + HT_INDEX_2211, HT_RULES)
        assert HT_RULES in s and s.count('ErrorDocument') == 1, '.htaccess: правила 22.11.2026 записаны иначе'
        return s
    assert 'ErrorDocument' not in s and 'index\\.php' not in s and 'REQUEST_FILENAME' not in s, '.htaccess: уже есть похожие правила'
    assert s.count(HT_ANCHOR) == 1, '.htaccess: нет запрета vendor/autoload.php'
    assert s.count(HT_END) == 1 and s.endswith(HT_END), '.htaccess: </IfModule> не в конце файла'
    assert s.index(HT_ANCHOR) < s.index(HT_END)
    s = s.replace(HT_ANCHOR, HT_ANCHOR + HT_RULES)
    return s + HT_404


# ---------- sitemap.xml ----------
DEPLOY_DATE = '2026-11-22'
DEPLOY_PAGES = [  # страницы, у которых выкладка 22.11.2026 меняет текст, ссылки в тексте, title или разметку
    '', 'deratizatsiya/', 'dezinfektsiya/', 'dezinsektsiya/', 'deratizatsiya-i-dezinsektsiya/', 'razrabotka-ppk/',
    'sanitarnyy-audit/', 'pishchevoe-proizvodstvo/', 'restorany-i-kafe/', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/', 'materialy/kak-berut-smyvy/',
    'laboratornye-issledovaniya/analiz-vody/', 'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/',
]
LASTMOD = {  # дата последней правки текста до выкладки 22.11.2026
    '': '2026-11-19',
    'biznes-tsentry-torgovye-tsentry-predpriyatiya/': '2026-11-19',
    'deratizatsiya-i-dezinsektsiya/': '2026-11-19',
    'deratizatsiya/': '2026-11-19',
    'deratizatsiya/restorany-i-kafe/': '2026-11-19',
    'dezinfektsiya/': '2026-11-19',
    'dezinsektsiya/': '2026-11-19',
    'dezinsektsiya/restorany-i-kafe/': '2026-11-19',
    'dogovor-deratizatsiya-dezinsektsiya/': '2026-11-19',
    'farmatsevticheskie-proizvodstva/': '2026-11-19',
    'gostinitsy/': '2026-11-19',
    'laboratornye-issledovaniya/': '2026-11-19',
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/': '2026-11-19',
    'laboratornye-issledovaniya/analiz-smyvov/': '2026-11-19',
    'laboratornye-issledovaniya/analiz-vody/': '2026-11-19',
    'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/': '2026-11-19',
    'laboratornye-issledovaniya/izmerenie-mikroklimata/': '2026-11-19',
    'laboratornye-issledovaniya/kontrol-sterilizatorov/': '2026-11-19',
    'laboratornye-issledovaniya/zamer-osveshchennosti/': '2026-11-19',
    'magaziny-i-torgovye-seti/': '2026-11-19',
    'materialy/': '2026-11-24',  # 24.11.2026: карточки материалов 14 и 15
    'materialy/akt-deratizatsii-i-dezinsektsii/': '2026-11-11',
    'materialy/kak-berut-smyvy/': '2026-11-19',
    'materialy/litsenziya-na-dezinfektsiyu/': '2026-11-24',  # новая статья, выложена 24.11.2026
    'materialy/kontrol-raboty-sterilizatorov/': '2026-11-14',
    'materialy/pest-kontrol-iso-22000-fssc-22000/': '2026-11-24',  # новая статья, выложена 24.11.2026
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/': '2026-11-19',
    'materialy/programma-pest-kontrolya/': '2026-11-19',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/': '2026-11-19',
    'materialy/skhema-tochek-pest-kontrolya/': '2026-11-19',
    'materialy/zamer-osveshchennosti-i-mikroklimata/': '2026-11-19',
    'materialy/zhurnal-pest-kontrolya/': '2026-11-19',
    'normativnaya-baza/': '2026-11-11',
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/': '2026-11-11',
    'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/': '2026-11-11',
    'normativnaya-baza/proverochnye-listy/': '2026-11-11',
    'ochistka-dezinfektsiya-ventilyatsii/': '2026-11-19',
    'pishchevoe-proizvodstvo/': '2026-11-24',  # 24.11.2026: строка про FSSC 22000 версии 7 и ISO 22002-100:2025
    'razrabotka-ppk/': '2026-11-20',
    'restorany-i-kafe/': '2026-11-19',
    'sanitarnyy-audit/': '2026-11-19',
    'sklady-i-logistika/': '2026-11-19',
    'zashchita-ot-proniknoveniya-gryzunov/': '2026-11-19',
}
assert len(LASTMOD) == 43 and all(p in LASTMOD for p in DEPLOY_PAGES)


def dates():
    out = dict(LASTMOD)
    for p in DEPLOY_PAGES:
        out[p] = DEPLOY_DATE
    return out


def sitemap(s):
    """lastmod адресов из LASTMOD (если в файле дата позже — она остаётся); остальные адреса и порядок строк не меняются."""
    want = dates()
    seen = set()

    def fix(m):
        path = m.group(2)[len(SITE):]
        if path not in want:
            return m.group(0)
        seen.add(path)
        return m.group(1) + max(m.group(3), want[path]) + m.group(4)  # более позднюю дату (правка в репозитории) не трогаем
    new = re.sub(r'(<loc>(%s[^<]*)</loc>\s*<lastmod>)(\d{4}-\d\d-\d\d)(</lastmod>)' % re.escape(SITE), fix, s)
    assert seen == set(want), 'sitemap.xml: нет адресов ' + ', '.join(sorted(set(want) - seen))
    assert new.count('<url>') == s.count('<url>') and len(new) == len(s)
    return new


def main():
    check = '--check' in sys.argv[1:]
    bad = []
    for name, fn in (('.htaccess', htaccess), ('sitemap.xml', sitemap)):
        f = ROOT / 'server' / name
        s = f.read_text(encoding='utf-8')
        new = fn(s)
        assert fn(new) == new, name + ': повторный запуск меняет файл'
        if new != s:
            if check:
                bad.append(name)
            else:
                f.write_text(new, encoding='utf-8')
                print('seo_server: изменён server/' + name)
    if check:
        print('seo_server:', 'нет правок в ' + ', '.join(bad) if bad else 'правки 22.11.2026 на месте')
        sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
