#!/usr/bin/env python3
"""Выкладка 06.11.2026: ссылки на страницу «Программа производственного контроля по ХАССП» в файлах, которые сейчас на сайте.

Использование:
  python3 tools/deploy/patch-2026-11-06-ppk.py <папка с файлами сайта> <папка пакета> <dist/timeweb>

В папке сайта — страницы `index.php` (как их отдаёт сайт по HTTPS) и `sitemap.xml`. В каждый файл вносятся только ссылки
на новую страницу /materialy/programma-proizvodstvennogo-kontrolya-haccp/:
  * пункт в выпадающем меню «Материалы» в шапке, в мобильном меню и в колонке «Материалы» подвала — перед «Все материалы»
    (та же разметка, что в сборке `tools/site/unify.py` / `tools/menu/apply_menu.py`);
  * `materialy/index.php`: карточка «Материал 04» (как в сборке), «Материал 04 · Готовится» → «Материал 05 · Готовится»,
    в микроразметке раздела — пункт 4 списка и описание (весь блок JSON-LD берётся из сборки, если остальное в нём совпадает);
  * `materialy/programma-pest-kontrolya/index.php`: ссылка-чип «Образец ППК по ХАССП и раздел пест-контроля →» перед
    «Документы и отчётность на главной»;
  * `sitemap.xml`: адрес новой страницы после «Пест-менеджмент или разовая обработка».
Скрипт проверяет, что в каждом файле изменились только эти места, и что вставленная разметка совпадает со сборкой
(`dist/timeweb`, версия для Timeweb из `tools/site/build_prod.py`).
"""
import difflib, json, os, re, sys

NB = '\u00a0'
SLUG = 'materialy/programma-proizvodstvennogo-kontrolya-haccp/'
NAME = 'Программа производственного контроля по' + NB + 'ХАССП'
ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
tok = lambda s: re.findall(r'<[^>]+>|[^<]+', s)


def root_of(rel):
    return '../' * rel.count('/')


def ins_before(s, pat, frag, what, start=0, unique=True):
    """Вставка frag перед первым совпадением регулярного выражения pat (после позиции start)."""
    found = list(re.finditer(pat, s[start:]))
    assert found and (not unique or len(found) == 1), (what, len(found))
    assert frag not in s, (what, 'уже есть')
    i = start + found[0].start()
    return s[:i] + frag + s[i:]


def patch(rel, s, dist):
    R = root_of(rel)
    href = f'href="{R}{SLUG}"'
    assert href not in s, (rel, 'ссылка уже есть')
    ALL = '(?:' + re.escape(R + 'materialy/') + '|\\./)'   # на странице раздела «Все материалы» ведёт на ./
    # шапка: выпадающее меню «Материалы»
    s = ins_before(s, f'<a href="{ALL}" class="nav-dd-all"[^>]*>Все материалы', f'<a {href}>{NAME}{ARR}</a>', rel + ': шапка')
    # мобильное меню
    s = ins_before(s, f'<a href="{ALL}"[^>]*>Все материалы</a>', f'<a {href}>{NAME}</a>', rel + ': мобильное меню',
                   start=s.index('id="mm-materialy"'), unique=False)
    # подвал
    s = ins_before(s, f'<li><a href="{ALL}"[^>]*>Все материалы</a></li>', f'<li><a {href}>{NAME}</a></li>', rel + ': подвал')
    if rel == 'materialy/index.php':
        # карточка — из сборки
        m = re.search(r'<article class="p-sec">\s*<div>\s*<div class="p-sec-top"><span class="p-sec-num">Материал 04</span>.*?</article>\s*', dist, re.S)
        assert m and './programma-proizvodstvennogo-kontrolya-haccp/' in m.group(0)
        card = m.group(0)
        old = re.search(r'<article class="p-sec">\s*<div>\s*<div class="p-sec-top"><span class="p-sec-num">Материал 04 · Готовится</span>', s)
        assert old, 'materialy: нет карточки «Материал 04 · Готовится»'
        s = s[:old.start()] + card + s[old.start():]
        s = s.replace('<span class="p-sec-num">Материал 04 · Готовится</span>', '<span class="p-sec-num">Материал 05 · Готовится</span>', 1)
        # микроразметка: в сборке — тот же блок + пункт 4 и новое описание
        ld_live = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        ld_dist = re.search(r'<script type="application/ld\+json">(.*?)</script>', dist, re.S)
        a, b = json.loads(ld_live.group(1)), json.loads(ld_dist.group(1))
        for g in (a, b):
            for n in g['@graph']:
                if n.get('@type') == 'CollectionPage':
                    n.pop('description', None)
                    n['mainEntity']['itemListElement'] = [x for x in n['mainEntity']['itemListElement'] if SLUG not in x['url']]
        assert a == b, 'materialy: микроразметка сайта отличается от сборки не только пунктом ППК'
        s = s[:ld_live.start()] + ld_dist.group(0) + s[ld_live.end():]
    if rel == 'materialy/programma-pest-kontrolya/index.php':
        m = re.search(r'<li><a href="\.\./programma-proizvodstvennogo-kontrolya-haccp/">.*?</a></li>\s*', dist, re.S)
        assert m
        s = ins_before(s, re.escape('<li><a href="../../#dokumenty">Документы и' + NB + 'отчётность'), m.group(0), rel + ': чип')
    return s


def check(rel, old, new, dist):
    """Отличия от файла с сайта — только вставки со ссылкой на новую страницу (и замены в разделе «Материалы»);
    каждая вставка есть в сборке."""
    A, B = tok(old), tok(new); n = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        o, w = ''.join(A[i1:i2]), ''.join(B[j1:j2]); n += 1
        if rel == 'materialy/index.php' and ('application/ld+json' in o or o.startswith('{"@context"') or 'Материал 04 · Готовится' in o):
            continue
        assert o == '' and ('programma-proizvodstvennogo-kontrolya-haccp/' in w or 'Материал 04' in w or w.strip() == ''), (rel, op, o[:120], w[:160])
        assert w in dist, (rel, 'вставки нет в сборке', w[:160])
    return n


def main(src, out, dist_root):
    done = []
    for root, _, files in os.walk(src):
        for f in files:
            if f != 'index.php':
                continue
            rel = os.path.relpath(os.path.join(root, f), src)
            if rel.startswith(SLUG):
                continue
            old = open(os.path.join(src, rel), encoding='utf-8').read()
            dist = open(os.path.join(dist_root, rel), encoding='utf-8').read()
            new = patch(rel, old, dist)
            n = check(rel, old, new, dist)
            same = 'совпадает со сборкой' if new == dist else 'в сборке есть и другие правки (не выкладываются)'
            os.makedirs(os.path.dirname(os.path.join(out, rel)) or out, exist_ok=True)
            open(os.path.join(out, rel), 'w', encoding='utf-8').write(new)
            done.append(rel)
            print(f'{rel:60} правок: {n:2}  {same}')
    sm = open(os.path.join(src, 'sitemap.xml'), encoding='utf-8').read()
    assert SLUG not in sm
    m = re.search(r'  <url>\n    <loc>https://xn----itbbsflddbfpfdodg9d0f\.xn--p1ai/materialy/pest-menedzhment-ili-razovaya-obrabotka/</loc>\n.*?  </url>\n', sm, re.S)
    entry = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>2026-11-06</lastmod>',
                   m.group(0).replace('materialy/pest-menedzhment-ili-razovaya-obrabotka/', SLUG))
    sm2 = sm[:m.end()] + entry + sm[m.end():]
    open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf-8').write(sm2)
    print('sitemap.xml: адресов', sm2.count('<url>'))
    return done


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
