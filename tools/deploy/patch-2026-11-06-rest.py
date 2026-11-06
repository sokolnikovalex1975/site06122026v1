#!/usr/bin/env python3
"""Выкладка 06.11.2026 14:25: ссылки на страницу «Пест-контроль ресторанов и кафе» в файлах, которые сейчас на сайте.

Использование:
  python3 tools/deploy/patch-2026-11-06-rest.py <папка с файлами сайта> <папка пакета>

В папке сайта — страницы `index.php` (как их отдаёт сайт по HTTPS, суммы = MANIFEST предыдущей выкладки) и `sitemap.xml`.
В каждый файл вносятся только ссылки на рестораны:
  * пункт «Рестораны и кафе» в меню «Отрасли», в мобильном меню и в подвале: `#otrasl-restorany` → `restorany-i-kafe/`;
  * главная: в карточке отрасли `id="otrasl-restorany"` — ссылка «Подробнее об обслуживании ресторанов» (как в сборке `tools/site/unify.py`);
  * дезинсекция и договор: карточки «Рестораны…» ведут на `../restorany-i-kafe/` вместо `../#otrasli`;
  * `sitemap.xml`: адрес `/restorany-i-kafe/` после пищевых производств.
Скрипт проверяет, что в каждом файле изменились только эти ссылки. Новую страницу (`restorany-i-kafe/index.php`) берите из версии
для Timeweb (`tools/site/build_prod.py`) той сборки, где меню совпадает с сайтом, и сравните её шапку и подвал со страницами пакета.
"""
import difflib, os, re, sys

ARR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
HOME_LINK = f'<a class="ind-more" href="restorany-i-kafe/">Подробнее об обслуживании ресторанов{ARR}</a>'
tok = lambda s: re.findall(r'<[^>]+>|[^<]+', s)


def patch(rel, s):
    if rel == 'index.php':
        s = s.replace('href="#otrasl-restorany"', 'href="restorany-i-kafe/"')
        a = s.find('id="otrasl-restorany"'); b = s.find('</article>', a)
        assert a > 0 and s[b - 6:b] == '</div>' and 'href="restorany-i-kafe/"' not in s[a:b], 'карточка ресторанов на главной'
        return s[:b - 6] + HOME_LINK + s[b - 6:]
    s = re.sub(r'href="((?:\.\./)+)#otrasl-restorany"', r'href="\1restorany-i-kafe/"', s)
    if rel in ('dezinsektsiya/index.php', 'dogovor-deratizatsiya-dezinsektsiya/index.php'):
        s, n = re.subn(r'<a href="\.\./#otrasli">(Рестораны(?:,| и)[^<]*)</a>', r'<a href="../restorany-i-kafe/">\1</a>', s)
        assert n == 1, rel
    return s


def check(rel, old, new):
    A, B = tok(old), tok(new); n = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        o, w = ''.join(A[i1:i2]), ''.join(B[j1:j2]); n += 1
        assert 'restorany-i-kafe' in w and ('otrasl-restorany' in o or '#otrasli' in o or o == ''), (rel, o[:80], w[:80])
    return n


def main(src, out):
    for root, _, files in os.walk(src):
        for f in files:
            if f != 'index.php':
                continue
            rel = os.path.relpath(os.path.join(root, f), src)
            old = open(os.path.join(src, rel), encoding='utf-8').read()
            if 'otrasl-restorany' not in old:
                continue
            new = patch(rel, old)
            n = check(rel, old, new)
            os.makedirs(os.path.dirname(os.path.join(out, rel)) or out, exist_ok=True)
            open(os.path.join(out, rel), 'w', encoding='utf-8').write(new)
            print(f'{rel:60} правок: {n}')
    sm = open(os.path.join(src, 'sitemap.xml'), encoding='utf-8').read()
    assert 'restorany-i-kafe' not in sm
    m = re.search(r'  <url>\n    <loc>https://xn----itbbsflddbfpfdodg9d0f\.xn--p1ai/pishchevoe-proizvodstvo/</loc>\n.*?  </url>\n', sm, re.S)
    entry = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>2026-11-06</lastmod>', m.group(0).replace('pishchevoe-proizvodstvo/', 'restorany-i-kafe/'))
    open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf-8').write(sm[:m.end()] + entry + sm[m.end():])
    print('sitemap.xml: адресов', (sm[:m.end()] + entry + sm[m.end():]).count('<url>'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
