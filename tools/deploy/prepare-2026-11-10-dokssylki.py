#!/usr/bin/env python3
"""Выкладка 10.11.2026: ссылки на страницу «Документы для Роспотребнадзора» с 13 страниц (решение владельца
«Выкладывай на хостинг» 10.11.2026 на вопрос о невыложенных ссылках, см. CHANGES 08.11.2026).

    python3 tools/site/build_prod.py      # сборка из 054f332 (без невыложенной страницы лабораторных исследований)
    python3 tools/deploy/prepare-2026-11-10-dokssylki.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — 24 страницы index.php и sitemap.xml, как их отдаёт сайт по HTTPS (/tmp/fetch_live.sh).

Страницы на сайте отличаются от сборки и в других местах (место <style id="m-crumbs">, role="group" у бегущей строки,
стили первого экрана вентиляции и карточек насекомых) — их не трогаем: из отличий «сайт → сборка» переносятся только
блоки со ссылкой на страницу документов:
  * главная — ссылка «Полный перечень для Роспотребнадзора» в «Образцах документов»;
  * дезинфекция, вентиляция и шесть отраслей — блок «Для проверки» (`<nav class="more" data-more="dok">`);
  * хаб нормативной базы — широкая карточка в «Разборах и образцах» и её стили (`.nb-link-wide`);
  * проверочные листы — абзац после таблицы «Какими документами ответить» (`.nb-after`);
  * «Материалы» — карточка «Материал 08» и пункт ItemList в JSON-LD;
  * санитарный аудит — ответ на вопрос «Какие документы подготовить к аудиту?» (страница и FAQPage в JSON-LD).
sitemap.xml — lastmod этих страниц 2026-11-10; search-index.json — из страниц пакета (tools/search/build_index.py).
Проверки: на каждой странице блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) ровно один и байт в байт прежний,
как в server/counters.html; поиск по сайту на месте; «сайт → пакет» — только выбранные блоки; «пакет → сборка» — только
отличия, которые оставлены как на сайте.
"""
import difflib
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
DOK = 'dokumenty-dlya-rospotrebnadzora'
LD = '<script type="application/ld+json">'
PAGES = ['index.php', 'dezinfektsiya/index.php', 'ochistka-dezinfektsiya-ventilyatsii/index.php',
         'pishchevoe-proizvodstvo/index.php', 'restorany-i-kafe/index.php', 'magaziny-i-torgovye-seti/index.php',
         'gostinitsy/index.php', 'farmatsevticheskie-proizvodstva/index.php', 'sklady-i-logistika/index.php',
         'normativnaya-baza/index.php', 'normativnaya-baza/proverochnye-listy/index.php', 'materialy/index.php',
         'sanitarnyy-audit/index.php']
EXPECT = {  # сколько блоков переносится на каждой странице
    'index.php': 1, 'normativnaya-baza/index.php': 3, 'normativnaya-baza/proverochnye-listy/index.php': 1,
    'materialy/index.php': 2, 'sanitarnyy-audit/index.php': 2,
}
COUNTERS = re.compile(rb'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def opcodes(a, b):
    return [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if o[0] != 'equal']


def patch(rel, live, new):
    a, b = live.split('\n'), new.split('\n')
    out, pos, n = [], 0, 0
    for t, i1, i2, j1, j2 in opcodes(a, b):
        la, lb = a[i1:i2], b[j1:j2]
        tb = '\n'.join(lb)
        take = None
        ta = '\n'.join(la)
        name = 'Документы для Роспотребнадзора'
        if t == 'replace' and any(x.startswith(LD) for x in la) and (DOK in tb or tb.count(name) > ta.count(name)):
            # строка JSON-LD — из сборки, остальные строки (стиль m-crumbs) — как на сайте
            nl = [x for x in lb if x.startswith(LD)]
            assert len(nl) == 1, rel
            take = [nl[0] if x.startswith(LD) else x for x in la]
        elif DOK in tb and 'id="m-crumbs"' not in tb:
            take = lb
        elif rel == 'normativnaya-baza/index.php' and t == 'insert' and 'nb-link-wide' in tb:
            take = lb
        out += a[pos:i1]
        out += take if take is not None else la
        pos = i2
        n += take is not None
    out += a[pos:]
    return '\n'.join(out), n


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = map(pathlib.Path, sys.argv[1:3])
    cblock = (ROOT / 'server' / 'counters.html').read_bytes()
    files = {}
    for rel in PAGES:
        live = (live_dir / rel).read_text(encoding='utf-8')
        new = (DIST / rel).read_text(encoding='utf-8')
        out, n = patch(rel, live, new)
        assert n == EXPECT.get(rel, 1), f'{rel}: перенесено блоков {n}, ожидалось {EXPECT.get(rel, 1)}'
        # всё, что осталось отличаться от сборки, — не про страницу документов
        for t, i1, i2, j1, j2 in opcodes(out.split('\n'), new.split('\n')):
            rest = '\n'.join(out.split('\n')[i1:i2] + new.split('\n')[j1:j2])
            assert DOK not in rest or 'id="m-crumbs"' in rest, f'{rel}: остался блок со ссылкой на документы'
        lb, pb = live.encode('utf-8'), out.encode('utf-8')
        c1, c2 = COUNTERS.findall(lb), COUNTERS.findall(pb)
        assert len(c1) == 1 and c1 == c2 and c1[0] in cblock, f'{rel}: блок счётчиков изменён или не найден'
        for k in (b'113675622', b'srch', b'comagic', b'uiscom', b'radist'):
            assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'
        assert pb.count(DOK.encode()) > lb.count(DOK.encode()), rel
        files[rel] = pb
        print(f'{rel}: {n} блок(а); ссылок на документы {lb.count(DOK.encode())} → {pb.count(DOK.encode())}; счётчики прежние')
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    for rel in PAGES:
        loc = SITE + rel[:-len('index.php')]
        pat = re.compile(r'(<loc>' + re.escape(loc) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, loc
        sm = pat.sub(r'\g<1>2026-11-10\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in build_prod.PAGES:
            php = rel[:-len('index.html')] + 'index.php'
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files.get(php) or (live_dir / php).read_bytes())
        out = td / 'search-index.json'
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(td),
                            '--out', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        print(r.stdout.strip())
        files['search-index.json'] = out.read_bytes()
    order = ['search-index.json'] + PAGES + ['sitemap.xml']
    lines = ''
    for rel in order:
        d = pkg / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(files[rel])
        lines += f'{sha(files[rel])}  {rel}\n'
    if len(sys.argv) == 4:
        if pathlib.Path(sys.argv[3]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (pkg.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    live_search = live_dir / 'search-index.json'
    exp = ''.join(f'{sha((live_dir / rel).read_bytes())}  {rel}\n' for rel in order if (live_dir / rel).exists())
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'пакет: {len(order)} файлов → {pkg}' + ('' if live_search.exists() else ' (нет search-index.json с сайта для EXPECTED_BEFORE)'))


if __name__ == '__main__':
    main()
