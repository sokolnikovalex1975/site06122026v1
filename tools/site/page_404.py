#!/usr/bin/env python3
"""Своя страница 404 «Страница не найдена» — разрешена владельцем 18.11.2026 (технические правки, п. 7).

    python3 tools/site/page_404.py            # 404.html в корне репозитория (из privacy/index.html)
    python3 tools/site/page_404.py --check    # только проверка

Сервер отдаёт её на любой несуществующий адрес (ErrorDocument 404 /404.html в server/.htaccess) с кодом 404,
поэтому все ссылки, стили и скрипты — от корня сайта («/style.css», «/dezinfektsiya/»), а не относительные:
относительные сломались бы на адресе вроде /a/b/c/. Шапка, меню и подвал — как на странице политики (шаблон),
H1 «Страница не найдена», кнопка поиска по сайту (тот же поиск, что под лупой в шапке), ссылки на услуги, отрасли и
материалы (из подвала), телефон. <meta name="robots" content="noindex">, canonical нет, в sitemap.xml не входит.
Счётчики — по закону владельца (tools/site/tracking_laws.py): ставит tools/site/build_prod.py для Timeweb и пакет
выкладки; в репозитории счётчиков нет, как и на остальных страницах.

build(template) применим и к живой странице политики с Timeweb (tools/deploy/prepare-2026-11-22-seo.py).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

TITLE = 'Страница не найдена — ПЕСТКОНТРОЛЬ Центр'
DESCRIPTION = 'Такой страницы на сайте нет. Поиск по сайту, услуги, отрасли и материалы ПЕСТКОНТРОЛЬ Центр.'
STYLE = ('<style id="nf-st">/* страница 404 (tools/site/page_404.py, 18.11.2026) */'
         '.nf-doc{max-width:980px}'
         '.nf-srch{display:flex;align-items:center;gap:12px;width:100%;max-width:620px;min-height:56px;margin:36px 0 0;'
         'padding:0 20px;border:1px solid var(--line2);border-radius:14px;background:rgba(255,255,255,.03);color:var(--t2);'
         'font:inherit;font-size:16px;line-height:1.3;text-align:left;cursor:pointer;transition:border-color .25s,color .25s}'
         '.nf-srch:hover,.nf-srch:focus-visible{border-color:var(--acc);color:var(--t1)}'
         '.nf-srch svg{flex:none;width:20px;height:20px;color:var(--acc)}'
         '.nf-cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px 40px;margin-top:56px}'
         '.nf-h{font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--t2);margin:0 0 16px}'
         '.nf-cols ul{list-style:none;margin:0;padding:0;display:grid;gap:12px}'
         '.nf-cols li{line-height:1.45}'
         '.nf-cols a{color:var(--t1);border-bottom:1px solid rgba(124,134,255,.45);transition:border-color .25s}'
         '.nf-cols a:hover{border-color:var(--t1)}'
         '.nf-call{margin:56px 0 0;color:var(--t2)}'
         '.nf-call a{color:var(--t1)}'
         '.nf-doc .nf-home{margin-top:24px;color:#09090b}'
         '@media (max-width:760px){.nf-cols{grid-template-columns:minmax(0,1fr);gap:28px;margin-top:40px}'
         '.nf-call{margin-top:40px}.nf-doc .nf-home{width:100%;justify-content:center}}'
         '</style>')
LUPA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>')


def absolute(s, base='/privacy/'):
    """Относительные адреса шаблона (страница /privacy/) — от корня сайта."""
    def fix(m):
        attr, val = m.group(1), m.group(2)
        if val == './':
            val = base
        elif val.startswith('../'):
            val = '/' + val[3:]
        return '%s="%s"' % (attr, val)
    s = re.sub(r'\b(href|src)="(\.\.?/[^"]*)"', fix, s)
    assert not re.search(r'\b(?:href|src|srcset)="\.', s), 'остались относительные адреса'
    s, n = re.subn(r'\}\)\("\.\./","(\d+)"\);', r'})("/","\1");', s)
    assert n == 1, 'поиск: корень сайта'
    return s


def column(footer, title):
    m = re.search(r'<h4>%s</h4><ul>(.*?)</ul>' % title, footer, re.S)
    assert m, 'подвал: ' + title
    items = re.findall(r'<li(?: class="([^"]*)")?>(.*?)</li>', m.group(1), re.S)
    keep = [x for cls, x in items if 'ft-sub' not in cls and 'href="#' not in x and '/#' not in x]
    return '<ul>%s</ul>' % ''.join('<li>%s</li>' % x for x in keep)


def main_html(footer):
    lead = typo('Такой страницы на сайте нет: возможно, адрес устарел или в нём опечатка. Найдите нужное через поиск '
                'или выберите раздел.')
    call = typo('Не нашли нужное — позвоните: ') + '<a href="tel:+74951043570">+7 (495) 104-35-70</a>' + typo(
        '. Пн–Пт: 8:00–20:00, срочные выезды — 24/7.')
    cols = ''.join('\n      <nav aria-labelledby="nf-%s"><h2 class="nf-h" id="nf-%s">%s</h2>%s</nav>' % (k, k, t, column(footer, t))
                   for k, t in (('u', 'Услуги'), ('o', 'Отрасли'), ('m', 'Материалы')))
    return ('<main class="wrap l-main" id="main" tabindex="-1">\n'
            '  <article class="l-doc nf-doc">\n'
            '    <p class="l-kicker">Ошибка 404</p>\n'
            '    <h1>Страница не найдена</h1>\n'
            '    <p class="l-lead">%s</p>\n'
            '    <button class="nf-srch" type="button" data-srch aria-haspopup="dialog">%s<span>%s</span></button>\n'
            '    <div class="nf-cols">%s\n    </div>\n'
            '    <p class="nf-call">%s</p>\n'
            '    <a href="../" class="btn btn-w btn-lg nf-home"><span class="btn-t">На главную</span></a>\n'
            '  </article>\n'
            '</main>' % (lead, LUPA, typo('Поиск по сайту: услуги, документы, нормативы'), cols, call))


def build(template):
    """template — страница политики (privacy/index.html репозитория или index.php с Timeweb) с готовым подвалом."""
    s = template
    assert 'mc.yandex' not in s and 'uiscom' not in s, 'в шаблоне не должно быть счётчиков'
    s, n = re.subn(r'<title>[^<]*</title>', '<title>%s</title>' % TITLE, s, count=1)
    assert n == 1
    s, n = re.subn(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % DESCRIPTION,
                   s, count=1)
    assert n == 1
    s, n = re.subn(r'<meta name="robots" content="[^"]*">(?:<!--[^>]*-->)?', '<meta name="robots" content="noindex">', s,
                   count=1)
    assert n == 1, 'robots'
    assert 'rel="canonical"' not in s
    footer = s[s.index('<footer'):s.index('</footer>')]
    m = re.search(r'<main\b.*?</main>', s, re.S)
    assert m
    s = s[:m.start()] + main_html(footer) + s[m.end():]
    s = s.replace(' aria-current="page"', '')
    old = 'footer .ft-company p+p{margin-top:4px}</style>'
    assert s.count(old) == 1
    s = s.replace(old, old + '\n' + STYLE)
    s = absolute(s)
    assert '<h1>' in s and s.count('<h1') == 1
    return s


def main():
    check = '--check' in sys.argv[1:]
    sys.path.insert(0, str(ROOT / 'tools' / 'site'))
    new = build((ROOT / 'privacy' / 'index.html').read_text(encoding='utf-8'))
    f = ROOT / '404.html'
    if check:
        ok = f.exists() and f.read_text(encoding='utf-8') == new
        print('page_404:', '404.html совпадает со сборкой' if ok else '404.html устарел или отсутствует')
        sys.exit(0 if ok else 1)
    f.write_text(new, encoding='utf-8')
    print('page_404: 404.html —', len(new.encode()), 'байт')


if __name__ == '__main__':
    main()
