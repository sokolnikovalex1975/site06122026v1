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
}
NEED = {'.v-freq': 'class="d-table v-freq"', '.dz-methods': 'class="d-table dz-methods"', '#sanpin .d-table': 'id="sanpin"'}
OLD = re.compile(r'<style id="t-cards">.*?</style>\n?', re.S)
INSET = re.compile(r'<style id="t-inset">.*?</style>\n?', re.S)


def rule(tables):
    def sel(suffix):
        return ','.join(t + suffix for t in tables)
    css = ('@media (min-width:601px) and (max-width:760px){'
           + sel(' thead') + '{display:none}'
           + ','.join(t + x for t in tables for x in ('', ' tbody', ' tr', ' td')) + '{display:block;width:100%}'
           + sel(' tr') + '{border:1px solid var(--line2);border-radius:var(--r);padding:6px 16px;margin-bottom:12px}'
           + sel(' td') + '{border:0;padding:10px 0;min-width:0}'
           + sel(' td+td') + '{border-top:1px solid var(--line)}'
           + sel(' td::before') + '{content:attr(data-l);display:block;font-size:13px;color:var(--t3);margin-bottom:4px}'
           + '}')
    return ('<style id="t-cards">/* широкие таблицы на 601–760 px — карточками, как на телефоне, без прокрутки вбок'
            ' (tools/site/table_cards.py, 19.11.2026) */' + css + '</style>\n')


def apply(rel, s):
    s = OLD.sub('', s)
    tables = PAGES.get(rel)
    if not tables:
        return s
    for t in tables:
        if NEED[t] not in s:
            raise SystemExit('%s: нет таблицы %s' % (rel, t))
    m = INSET.search(s)
    if not m:
        raise SystemExit('%s: нет строки <style id="t-inset">' % rel)
    line = m.group(0) if m.group(0).endswith('\n') else m.group(0) + '\n'
    out = s[:m.start()] + line + rule(tables) + s[m.end():]
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
