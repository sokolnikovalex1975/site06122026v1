#!/usr/bin/env python3
"""Текст во flex-ссылках и подписях — одним куском (правка владельца 11.11.2026).

    python3 tools/site/flex_text.py            # правит страницы репозитория
    python3 tools/site/flex_text.py --check    # только проверка, код 1 при нарушениях

Замечание владельца 11.11.2026 (скриншоты с телефона): ссылка «Подробнее о пест-контроле по GMP» в карточке отрасли
на телефоне разъехалась на три колонки: «Подробнее о» · «пест-контроле» · «по GMP». Причина: ссылка — flex-контейнер,
а слово через дефис обёрнуто в <span class="nw"> (чтобы не переносилось по дефису). Во flex каждый кусок текста
и каждый вложенный тег — отдельный элемент, между ними встаёт gap, и каждый переносится в своей колонке.

Что делает скрипт: в элементах, которые на сайте свёрстаны как flex/inline-flex (список FLEX ниже), подряд идущие
куски текста и строчные теги (span.nw, b, em…) оборачивает в один <span class="fxt">. Значки (svg, i, img)
и «плашки» (.v-chip) остаются отдельными элементами, как в дизайне. Стиль .fxt — одной строкой <style id="flex-text">
перед </head> на страницах, где есть .fxt: внутри обёртки — обычный строчный текст (вложенные span не становятся
inline-flex даже там, где правило задано для всех span подписи, как в .f-legend span).

Повторный запуск ничего не меняет. Запускается из build_site.py перед tracking_laws.py. Ссылки телефона и почты
не трогает (ЗАКОН ВЛАДЕЛЬЦА: внутри tel:/mailto: — только номер и адрес).
Проверка в браузере на всех страницах: node tools/qa/flex_split_test.mjs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit', 'preview-services'}

# (тег, класс) flex-контейнеров с текстом; None — любой тег
FLEX = [
    ('a', 'ind-more'),        # «Подробнее о … →» в карточках отраслей (главная, «Дератизация» и др.)
    (None, 'eyebrow'),        # надзаголовок «Определение · МР 3.5.0396-25»
    ('h3', 'v-dg-t'),         # «Рекомендовано · МР 3.5.0396-25» (вентиляция)
    ('a', 'link-arrow'),      # «Образец программы пест-контроля →»
    ('a', 'more'),
]
# прямые потомки flex-элементы: подписи легенд <figcaption class="f-legend"><span><i></i>текст</span>…
# и пункты списков с галочками <ul class="cta-list"><li><svg/>текст</li>…
CHILD_FLEX = [('f-legend', 'span'), ('cta-list', 'li')]

KEEP_SEPARATE = re.compile(r'^<(svg|i|img|picture|br)\b|class="[^"]*\b(v-chip|fxt|ico|badge-dot|dot)\b', re.I)
INLINE = {'span', 'b', 'strong', 'em', 'nobr', 'abbr', 'u', 'small', 'sup', 'sub', 'mark', 'q', 'time'}
TAG = re.compile(r'<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>', re.S)
ARROW = re.compile(r'^\s*[→←↗›»↓]+\s*$')
VOID = {'br', 'img', 'input', 'wbr', 'hr', 'source', 'meta', 'link'}


def split_children(inner):
    """Верхний уровень содержимого: список (вид, html), вид — 'text' или 'el'; None — разметка не разобрана."""
    out, i, n = [], 0, len(inner)
    while i < n:
        lt = inner.find('<', i)
        if lt < 0:
            out.append(('text', inner[i:]))
            break
        if lt > i:
            out.append(('text', inner[i:lt]))
        m = TAG.match(inner, lt)
        if not m or m.group(1):
            return None  # закрывающий тег на верхнем уровне — разметка не та, не трогаем
        name = m.group(2).lower()
        if name in VOID or m.group(4):
            out.append(('el', m.group(0)))
            i = m.end()
            continue
        # ищем парный закрывающий тег с учётом вложенности того же имени
        depth, j = 1, m.end()
        pat = re.compile(r'<(/?)' + re.escape(name) + r'\b[^>]*>', re.I)
        while depth:
            mm = pat.search(inner, j)
            if not mm:
                return None
            depth += -1 if mm.group(1) else 1
            j = mm.end()
        out.append(('el', inner[lt:j]))
        i = j
    return out


def is_inline_text_el(h):
    m = TAG.match(h)
    if not m:
        return False
    if KEEP_SEPARATE.search(h[:m.end()]) or '<svg' in h or '<img' in h:
        return False
    return m.group(2).lower() in INLINE and bool(re.sub(r'<[^>]+>', '', h).strip())


def wrap_runs(inner):
    parts = split_children(inner)
    if parts is None:
        return inner, False
    # группы подряд идущих «текст/строчный тег»
    out, run, changed = [], [], False

    def flush():
        nonlocal changed
        if not run:
            return
        has_text = any(k == 'text' and h.strip() for k, h in run)
        has_el = any(k == 'el' for k, h in run)
        items = [x for x in run if not (x[0] == 'text' and not x[1].strip())]
        if has_el and (has_text or len(items) > 1):
            body = ''.join(h for _, h in run)
            lead = re.match(r'\s*', body).group(0)
            tail = re.search(r'\s*$', body).group(0)
            core = body[len(lead):len(body) - len(tail)] if tail else body[len(lead):]
            out.append(f'{lead}<span class="fxt">{core}</span>{tail}')
            changed = True
        else:
            out.extend(h for _, h in run)
        run.clear()

    for k, h in parts:
        if k == 'text' and ARROW.match(h):  # отдельная стрелка «→» — свой элемент, как в дизайне
            flush()
            out.append(h)
        elif k == 'text' or is_inline_text_el(h):
            run.append((k, h))
        else:
            flush()
            out.append(h)
    flush()
    return ''.join(out), changed


def open_tag_re(tag, cls):
    t = tag or r'[a-z][\w-]*'
    return re.compile(r'<(' + t + r')\b([^>]*\bclass="(?:[^"]*\s)?' + re.escape(cls) + r'(?:\s[^"]*)?")([^>]*)>', re.I)


def element_spans(text, open_re):
    """(начало содержимого, конец содержимого) для каждого найденного элемента."""
    for m in open_re.finditer(text):
        name = m.group(1).lower()
        pat = re.compile(r'<(/?)' + re.escape(name) + r'\b[^>]*>', re.I)
        depth, j = 1, m.end()
        while depth:
            mm = pat.search(text, j)
            if not mm:
                break
            depth += -1 if mm.group(1) else 1
            j = mm.end()
        if depth == 0:
            yield m.end(), mm.start()


def fix(text):
    edits = []
    for tag, cls in FLEX:
        for a, b in element_spans(text, open_tag_re(tag, cls)):
            inner = text[a:b]
            if 'href="tel:' in inner or 'href="mailto:' in inner:
                continue
            new, ch = wrap_runs(inner)
            if ch:
                edits.append((a, b, new))
    # легенды и списки: каждый прямой потомок-flex
    for parent, child in CHILD_FLEX:
        for a, b in element_spans(text, open_tag_re(None, parent)):
            pos = a
            for k, h in split_children(text[a:b]) or []:
                if k == 'el' and re.match(r'<' + child + r'\b', h, re.I) and 'href="tel:' not in h and 'href="mailto:' not in h:
                    m = TAG.match(h)
                    close = h.rfind('</' + child + '>')
                    new, ch = wrap_runs(h[m.end():close])
                    if ch:
                        edits.append((pos + m.end(), pos + close, new))
                pos += len(h)
    # без пересечений: внешние правки важнее вложенных
    edits.sort(key=lambda e: (e[0], -e[1]))
    keep, last = [], -1
    for e in edits:
        if e[0] >= last:
            keep.append(e)
            last = e[1]
    for a, b, new in reversed(keep):
        text = text[:a] + new + text[b:]
    return text, len(keep)


STYLE = '<style id="flex-text">span.fxt.fxt,span.fxt.fxt span{display:inline}</style>'
STYLE_RE = re.compile(r'<style id="flex-text">.*?</style>', re.S)


def with_style(text):
    if 'class="fxt"' not in text:
        return STYLE_RE.sub('', text)
    if STYLE_RE.search(text):
        return STYLE_RE.sub(STYLE, text)
    return text.replace('</head>', STYLE + '\n</head>', 1)


def pages():
    for f in sorted(ROOT.rglob('index.html')):
        if not any(p in SKIP for p in f.relative_to(ROOT).parts):
            yield f


def main():
    check = '--check' in sys.argv[1:]
    total, bad = 0, []
    for f in pages():
        src = f.read_text(encoding='utf-8')
        new, n = fix(src)
        new = with_style(new)
        if new != src and not n:
            n = 0
            if not check:
                f.write_text(new, encoding='utf-8')
            if check:
                bad.append((f.relative_to(ROOT), 'нет стиля flex-text'))
            continue
        if n:
            bad.append((f.relative_to(ROOT), n))
            if not check:
                f.write_text(new, encoding='utf-8')
            total += n
    for f, n in bad:
        print(f'{"нарушение" if check else "исправлено"}: {f} — {n}')
    print(f'flex_text: {"найдено" if check else "обёрнуто"} {total} мест; страниц с правкой: {len(bad)}')
    if check and bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
