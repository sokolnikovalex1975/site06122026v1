#!/usr/bin/env python3
"""«Цена» и «Вопросы» в меню ведут к блокам этой же страницы — решение владельца 12.11.2026.

    python3 tools/site/menu_anchors.py           # страницы репозитория (шаг build_site.py после industry_links.py)
    python3 tools/site/menu_anchors.py --check   # только проверка: правило выполнено, все якоря существуют

Вопрос владельца 12.11.2026: «на страницах сайта в верхнем и нижнем меню "Цена" должна вести на ту часть страницы,
где указана цена же?» После предложения — «Вноси все эти правки и выкладывай всё на Timeweb».

До правки «Цена» в шапке, мобильном меню и подвале на всех страницах вела на прайс главной (../#tseny),
а «Вопросы» в подвале — на вопросы главной (../#voprosy): посетитель уходил со страницы услуги.

Правило:
  • «Цена» (шапка, мобильное меню, подвал) → свой блок цен страницы:
      #stoimost — «Сколько стоит …» (услуги, отрасли, договор, ППК, санаудит, вентиляция, статья о пест-менеджменте);
      #ceny     — «Цены на …» (лабораторные исследования);
      #tseny    — главная и страницы, где свой блок цен так и называется (комплекс, общепит);
    нет своего блока → каталог «Один подрядчик — все санитарные задачи» с ценами (#vse-uslugi) на этой же странице,
    он стоит прямо перед формой заявки (материалы, нормативная база);
    нет и его (политика, согласие) → прайс главной, как раньше.
  • «Вопросы» (подвал) → свой блок вопросов страницы (#voprosy); нет его → вопросы главной, как раньше.

Якоря блоков не переименовываются: прежние ссылки на них (в том числе из рекламы) работают. Ссылки на якоря той же
страницы обрабатывает app.js: плавная прокрутка с поправкой на шапку, мобильное меню закрывается; «Цена» в шапке
подсвечивается у блока цен, как на главной. Скрипт идемпотентен. Та же функция patch(s, rel) применяется к страницам
рабочего сайта при выкладке: tools/deploy/prepare-2026-11-12-menu-anchors.py.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKIP = ('tools/', 'preview-', 'server/', 'vendor/', 'node_modules/', '.git/')
PRICE_OWN = ('stoimost', 'ceny', 'tseny')  # свой блок цен страницы, по приоритету
PRICE_CATALOG = 'vse-uslugi'               # каталог услуг с ценами перед формой заявки


def has_section(s, sid):
    return re.search(r'<section\b[^>]*\bid="%s"' % re.escape(sid), s) is not None


def price_target(s):
    for sid in PRICE_OWN:
        if has_section(s, sid):
            return sid
    if has_section(s, PRICE_CATALOG):
        return PRICE_CATALOG
    return None


def root_of(rel):
    cur = rel.strip('/')
    return '../' * (cur.count('/') + 1) if cur else ''


def patch(s, rel):
    """rel — адрес страницы без «/» по краям ('' — главная). Возвращает (HTML, [(было, стало, сколько)])."""
    root = root_of(rel)
    rules = []
    sid = price_target(s)
    if sid:
        rules.append(('<a href="%s#tseny">Цена</a>' % root, '<a href="#%s">Цена</a>' % sid))
    if has_section(s, 'voprosy'):
        rules.append(('<a href="%s#voprosy">Вопросы</a>' % root, '<a href="#voprosy">Вопросы</a>'))
    changes = []
    for old, new in rules:
        n = s.count(old)
        if old != new and n:
            s = s.replace(old, new)
            changes.append((old, new, n))
    return s, changes


def pages():
    out = []
    for f in sorted(ROOT.rglob('index.html')):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP):
            continue
        out.append((rel[:-len('index.html')], f))
    return out


def check(s, rel, home_ids):
    """Ошибки правила на странице: число ссылок, правило выполнено, якорь существует."""
    bad = []
    links = re.findall(r'<a href="([^"]*)">Цена</a>', s)
    if len(links) != 3:
        bad.append('ссылок «Цена» %d вместо 3' % len(links))
    if patch(s, rel)[1]:
        bad.append('правило не применено')
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    for href in links + re.findall(r'<a href="([^"]*)">Вопросы</a>', s):
        path, _, frag = href.partition('#')
        if not path:
            if frag not in ids:
                bad.append('нет якоря #%s на странице' % frag)
        elif path == root_of(rel):
            if frag not in home_ids:
                bad.append('нет якоря #%s на главной' % frag)
        else:
            bad.append('неожиданная ссылка %s' % href)
    return bad


def main():
    mode_check = '--check' in sys.argv[1:]
    home_ids = set(re.findall(r'\bid="([^"]+)"', (ROOT / 'index.html').read_text(encoding='utf-8')))
    changed, errors, summary = 0, [], {}
    for rel, f in pages():
        s = f.read_text(encoding='utf-8')
        if mode_check:
            errors += ['%s: %s' % (rel or '/', e) for e in check(s, rel, home_ids)]
            continue
        new, ch = patch(s, rel)
        if ch:
            f.write_text(new, encoding='utf-8')
            changed += 1
        target = re.search(r'<a href="([^"]*)">Цена</a>', new)
        key = 'нет ссылки' if not target else (
            target.group(1).split('#')[-1] + ('' if target.group(1).startswith('#') else ' на главной'))
        summary.setdefault(key, []).append(rel or '/')
    if mode_check:
        if errors:
            print('\n'.join(errors))
            sys.exit('menu_anchors: нарушений %d' % len(errors))
        print('menu_anchors: правило выполнено на всех %d страницах, все якоря существуют' % len(pages()))
        return
    for k, v in sorted(summary.items()):
        print('«Цена» → #%s: %d стр.' % (k, len(v)))
    print('menu_anchors: изменено страниц %d' % changed)


if __name__ == '__main__':
    main()
