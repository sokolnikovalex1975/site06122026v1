#!/usr/bin/env python3
"""Широкие таблицы на планшете — карточками, без прокрутки вбок (команда владельца 19.11.2026).

    python3 tools/site/table_cards.py            # правит страницы репозитория
    python3 tools/site/table_cards.py --check    # только проверка, код 1, если нужно поправить

Команда владельца 19.11.2026: «Исправь прокрутку вбок на вентиляции и дезинсекции в превью, потом покажи мне».
Причина: на этих страницах таблицы .d-table складываются в карточки только до 600 px. На 601–760 px три таблицы с четырьмя
колонками и длинными словами («Микробиологическое», «транспорт», номера СП и СГР одним куском) остаются таблицей
шире экрана (до 652 px при 552–712 px места), и страница уезжает вбок:
  * вентиляция, «Нормы» — таблица .v-freq в <section id="normy"> (601–669 px);
  * дезинсекция, «Методы» — таблица .dz-methods в <section id="metody">;
  * дезинсекция, «Пример заполнения журнала» — таблица .d-table в <section id="sanpin"> (601–690 px).
Вторая команда владельца 19.11.2026: «Исправь ошибки прокрутки вбок на остальных страницах. И выложи их сразу на TimeWeb»
— то же на 601–760 px для таблиц .dzf-kinds и .dzf-freq (дезинфекция, «Виды дезинфекции» 601–740 px и «Как часто»
601–615 px) и .lbs-t (лаборатория: анализ
пищевых продуктов, контроль стерилизаторов, замер освещённости; материалы: контроль работы стерилизаторов; 601–684 px,
номера ГОСТ/СанПиН одним куском), плюс заголовок «Документы по дезинфекции» на 441–520 px (EXTRA ниже).
Скрипт ставит одну строку <style id="t-cards"> сразу после строки <style id="t-inset"> (tools/site/table_inset.py) на
страницах с этими таблицами: на 601–760 px эти три таблицы показываются теми же карточками, что на телефоне (правила
скопированы из стилей страниц для max-width:600px: заголовок колонки над значением, рамка вокруг строки). До 600 px и от
761 px ничего не меняется, другие таблицы (цены, сравнение) не трогаются. Тексты, счётчики, телефон и почта не меняются.
Ничего не затемняется (закон владельца 17.11.2026): цвета подписей — те же, что в карточках на телефоне.
Проверка в браузере: node tools/qa/table_cards_test.mjs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PAGES = {
    'ochistka-dezinfektsiya-ventilyatsii/index.html': ['.v-freq'],
    'dezinsektsiya/index.html': ['.dz-methods', '#sanpin .d-table'],
    # 19.11.2026, вторая команда: «Исправь ошибки прокрутки вбок на остальных страницах»
    'dezinfektsiya/index.html': ['.dzf-kinds', '.dzf-freq'],
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.html': ['.lbs-t'],
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.html': ['.lbs-t'],
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.html': ['.lbs-t'],
    'materialy/kontrol-raboty-sterilizatorov/index.html': ['.lbs-t'],
    # на 601–760 px не шире экрана, шире — см. WIDE и EXTRA
    'materialy/programma-pest-kontrolya/index.html': [],
    'normativnaya-baza/index.html': [],
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html': [],
}
NEED = {'.v-freq': 'class="d-table v-freq"', '.dz-methods': 'class="d-table dz-methods"', '#sanpin .d-table': 'id="sanpin"',
        '.dzf-kinds': 'class="d-table dzf-kinds"', '.dzf-freq': 'class="d-table dzf-freq"', '.lbs-t': 'class="d-table lbs-t"'}
# Не таблица, а заголовок: «Документы по дезинфекции — для Роспотребнадзора и аудиторов» (размер шрифта 9vw, «для» склеено
# с «Роспотребнадзора» неразрывным пробелом типографики) на 445–505 px выходит за колонку текста на 4–21 px, на 445–450 px —
# за край экрана. На 441–520 px только этот заголовок — 8,4vw вместо 9vw (на 5 % меньше), текст не меняется.
# То же у заголовка «Какие договоры нужны для Роспотребнадзора» (#dogovory) на странице «Документы для Роспотребнадзора».
EXTRA = {
    'dezinfektsiya/index.html': [('id="dokumenty"', '@media (min-width:441px) and (max-width:520px){#dokumenty h2{font-size:8.4vw}}')],
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html': [
        ('id="dogovory"', '@media (min-width:441px) and (max-width:520px){#dogovory h2{font-size:8.4vw}}')],
}
# Широкие таблицы на 861–1040 px (проверка всех страниц на 900–1280 px 19.11.2026): таблица складывается в карточки только
# до 860/900 px (src), а на 901–970 px шире экрана. Для 901–980 px скрипт копирует собственные правила карточек страницы
# из @media (max-width:<src>px) (селекторы сужаются до этой таблицы: base → base + table) и снимает табличные правила
# от 901 px (ширины колонок, отступы t-inset у первой и последней ячейки). Карточки выглядят так же, как на 860/900 px.
#   «Программа пест-контроля» — план мероприятий .p-plan-table (861–950 px), карточки страницы до 860 px;
#   «Нормативная база» — таблицы документов .nb-docs (901–970 px), карточки .nb-tbl до 900 px;
#   «Документы для Роспотребнадзора» — перечень .dk-tbl (901–955 px), карточки .nb-tbl/.dk-tbl до 900 px.
# (таблица, src, базовый класс карточек, до скольких px карточки) — граница с запасом по замеру прежней версии:
# программа шире экрана на 861–950 px; таблицы нормативной базы выходят за колонку до 988 px, перечень документов — до
# 1018 px (на 901–955 px — за край экрана).
WIDE = {
    'materialy/programma-pest-kontrolya/index.html': ('.p-plan-table', 860, '.d-table', 980),
    'normativnaya-baza/index.html': ('.nb-docs', 900, '.nb-tbl', 1000),
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html': ('.dk-tbl', 900, '.nb-tbl', 1040),
}
OLD = re.compile(r'<style id="t-cards">.*?</style>\n?', re.S)
INSET = re.compile(r'<style id="t-inset">.*?</style>\n?', re.S)


def rule(tables, extra=''):
    def sel(suffix):
        return ','.join(t + suffix for t in tables)
    if not tables:
        return ('<style id="t-cards">/* широкие таблицы и заголовки без прокрутки вбок (tools/site/table_cards.py,'
                ' 19.11.2026) */' + extra + '</style>\n')
    css = ('@media (min-width:601px) and (max-width:760px){'
           + sel(' thead') + '{display:none}'
           + ','.join(t + x for t in tables for x in ('', ' tbody', ' tr', ' td')) + '{display:block;width:100%}'
           + sel(' tr') + '{border:1px solid var(--line2);border-radius:var(--r);padding:6px 16px;margin-bottom:12px}'
           + sel(' td') + '{border:0;padding:10px 0;min-width:0}'
           + sel(' td+td') + '{border-top:1px solid var(--line)}'
           + sel(' td::before') + '{content:attr(data-l);display:block;font-size:13px;color:var(--t3);margin-bottom:4px}'
           + '}' + extra)
    return ('<style id="t-cards">/* широкие таблицы на 601–760 px — карточками, как на телефоне, без прокрутки вбок'
            ' (tools/site/table_cards.py, 19.11.2026) */' + css + '</style>\n')


def _blocks(css, query):
    """Правила внутри @media <query> (без вложенных @media)."""
    out = []
    for m in re.finditer(r'@media\s*([^{]*)\{', css):
        if m.group(1).strip() != query:
            continue
        i, depth = m.end(), 1
        j = i
        while depth:
            depth += css[j] == '{'
            depth -= css[j] == '}'
            j += 1
        out += re.findall(r'([^{}]+)\{([^{}]*)\}', css[i:j - 1])
    return out


def wide_css(s, table, src, base, to):
    """Карточки таблицы table на <src+1>–<to> px — копия её правил из @media (max-width:<src>px)."""
    css = '\n'.join(re.findall(r'<style(?! id="t-cards")[^>]*>(.*?)</style>', s, re.S))
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    combo = base + ':where(%s)' % table  # :where — без лишнего веса селектора: каскад как на <src> px
    base_re = re.compile(re.escape(base) + r'(?![\w-])')
    rules = []
    for sels, body in _blocks(css, '(max-width:%dpx)' % src):
        keep = []
        for part in sels.split(','):
            part = ' '.join(part.split())
            if table in part:
                keep.append(part)
            elif base_re.search(part):
                keep.append(base_re.sub(combo, part, count=1))
        if keep:
            rules.append(','.join(keep) + '{' + body.strip().rstrip(';') + '}')
    if len(rules) < 5:
        raise SystemExit('%s: мало правил карточек (%d) в @media (max-width:%dpx)' % (table, len(rules), src))
    # табличные правила от 901 px: ширины колонок и отступы t-inset у первой и последней ячейки
    strong = table * 3  # ширины колонок от 901 px бывают и с двумя классами (.nb-docs.nb-3 td:nth-child(3))
    rules.append('%s td:nth-child(n){width:100%%}' % strong)
    rules.append('%s tr>td:first-child{padding-left:0}%s tr>td:last-child{padding-right:0}' % (combo, combo))
    return '@media (min-width:%dpx) and (max-width:%dpx){%s}' % (src + 1, to, ''.join(rules))


def apply(rel, s):
    s = OLD.sub('', s)
    if rel not in PAGES:
        return s
    tables = PAGES[rel]
    if not tables and rel not in WIDE and rel not in EXTRA:
        return s
    for t in tables:
        if NEED[t] not in s:
            raise SystemExit('%s: нет таблицы %s' % (rel, t))
    m = INSET.search(s)
    if not m:
        raise SystemExit('%s: нет строки <style id="t-inset">' % rel)
    extra = ''
    if rel in WIDE:
        table, src, base, to = WIDE[rel]
        if 'class="' not in s or table[1:] not in s:
            raise SystemExit('%s: нет таблицы %s' % (rel, table))
        extra += wide_css(s, table, src, base, to)
    for marker, css in EXTRA.get(rel, []):
        if marker not in s:
            raise SystemExit('%s: нет блока %s' % (rel, marker))
        extra += css
    line = m.group(0) if m.group(0).endswith('\n') else m.group(0) + '\n'
    out = s[:m.start()] + line + rule(tables, extra) + s[m.end():]
    return out


def main():
    check = '--check' in sys.argv[1:]
    changed = []
    for rel in PAGES:
        p = ROOT / rel
        s = p.read_text(encoding='utf-8')
        new = apply(rel, s)
        if new != s:
            changed.append(rel)
            if not check:
                p.write_text(new, encoding='utf-8')
    if check:
        for rel in changed:
            print('table_cards: нужно поправить', rel)
        print('table_cards: страниц %d, нужно поправить %d' % (len(PAGES), len(changed)))
        return 1 if changed else 0
    print('table_cards: страниц %d, изменено %d' % (len(PAGES), len(changed)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
