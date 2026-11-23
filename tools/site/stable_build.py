#!/usr/bin/env python3
"""Устойчивая полная сборка: повторный запуск tools/site/build_site.py не меняет готовые страницы (с 23.11.2026).

Зачем. Многие шаги сборки убирают свой блок стилей в <head> и вставляют его заново перед якорем, а генераторы
отдельных страниц (tools/gostinitsy, tools/deratizatsiya-i-dezinsektsiya и др.) пересобирают <head> из шаблона и теряют
блоки, которые позже добавили шаги сборки. Из-за этого полная сборка останавливалась (шагу не находился якорь
<style id="mob-fit"> / <style id="tel-plain">) или переставляла блоки стилей на всех страницах, хотя по содержанию
ничего не менялось.

Что делает (вызывается из build_site.py, сам по себе ничего не правит):
  * snapshot()      — до сборки запоминает все страницы репозитория;
  * carry_head()    — после генераторов страниц возвращает в <head> блоки с id (и <style data-fx>, подключения
                      скриптов), которые генератор выбросил, — в прежнем порядке, перед </head>; дальше их, как
                      и раньше, обновляют свои шаги сборки;
  * stabilize()     — в конце правки страниц: если страница по содержанию та же (те же блоки <head>, тот же <body>
                      с точностью до пустых строк), остаётся байт в байт прежней; если содержание изменилось —
                      блоки <head>, которые были на странице, стоят в прежнем порядке (новые — там, куда их поставил
                      шаг), а пустые строки в <body> не трогаются, если изменились только они.
Порядок блоков стилей важен для каскада CSS, поэтому сохраняется порядок, который уже стоит на страницах (и на сайте).
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = ('tools/', 'dist/', 'node_modules/', 'vendor/')
TOKEN = re.compile(r'<style\b[^>]*>.*?</style>|<script\b[^>]*>.*?</script>|<link\b[^>]*>|<meta\b[^>]*>'
                   r'|<title>.*?</title>|<!--.*?-->', re.S)


def pages():
    for f in sorted(ROOT.rglob('index.html')):
        rel = f.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield rel, f


def snapshot():
    return {rel: f.read_text(encoding='utf-8') for rel, f in pages()}


def _key(tok):
    """Ключ блока <head>: id, data-fx или адрес без ?v=. Без ключа (мета, title, безымянный <style>) — None."""
    open_tag = tok[:tok.find('>') + 1]
    m = re.search(r'\bid="([^"]+)"', open_tag)
    if m:
        return open_tag[:7] + '#' + m.group(1)
    if open_tag.startswith('<style data-fx'):
        return 'style[data-fx]'
    m = re.match(r'<script\b[^>]*\bsrc="([^"?]+)', open_tag)
    if m:
        return 'script@' + m.group(1)
    return None


def _split(html):
    i = html.find('</head>')
    return (html[:i], html[i:]) if i >= 0 else (html, '')


def _tokens(head, with_newline=False):
    """Блоки <head>. with_newline — вместе с переводом строки сразу после блока: при перестановке он едет с блоком
    (иначе блоки слипаются в одну строку, и шаги, которые ищут «блок + перевод строки», вырезают лишнее)."""
    out = []
    for m in TOKEN.finditer(head):
        end = m.end() + 1 if with_newline and head[m.end():m.end() + 1] == '\n' else m.end()
        out.append((m.start(), end, head[m.start():end]))
    return out


def _blank(s):
    return re.sub(r'\n[ \t]*(?=\n)', '', s)


def carry_head(snap, rels=None):
    """Вернуть в <head> блоки, которые генератор страницы выбросил. Возвращает список правленых страниц."""
    fixed = []
    for rel, f in pages():
        if rels is not None and rel not in rels:
            continue
        old = snap.get(rel)
        if old is None:
            continue
        new = f.read_text(encoding='utf-8')
        if new == old:
            continue
        oh, _ = _split(old)
        nh, nb = _split(new)
        have = {_key(t) for _, _, t in _tokens(nh)} - {None}
        lost = [t for _, _, t in _tokens(oh) if _key(t) and _key(t) not in have]
        if not lost:
            continue
        nh = nh.rstrip('\n') + '\n' + '\n'.join(lost) + '\n'
        f.write_text(nh + nb, encoding='utf-8')
        fixed.append(rel)
    return fixed


def _reorder(old_head, new_head):
    """Блоки, которые были на странице, — в прежнем порядке на тех же местах; новые блоки остаются на своих."""
    old_order = {}
    for _, _, t in _tokens(old_head):
        k = _key(t)
        if k and k not in old_order:
            old_order[k] = len(old_order)
    toks = _tokens(new_head, with_newline=True)
    slots = [i for i, (_, _, t) in enumerate(toks) if _key(t) in old_order]
    keys = [_key(toks[i][2]) for i in slots]
    if len(set(keys)) != len(keys):  # повторяющиеся ключи — не трогаем
        return new_head
    ordered = sorted(slots, key=lambda i: old_order[_key(toks[i][2])])
    repl = {slot: toks[src][2] for slot, src in zip(slots, ordered)}
    out, pos = [], 0
    for i, (a, b, t) in enumerate(toks):
        out.append(new_head[pos:a])
        out.append(repl.get(i, t))
        pos = b
    out.append(new_head[pos:])
    return ''.join(out)


def _canon_head(head):
    toks = sorted(t for _, _, t in _tokens(head))
    rest = TOKEN.sub('', head)
    return toks, re.sub(r'\s+', '', rest)


def stabilize(snap):
    """Страницы без изменений по содержанию — байт в байт прежние; остальные — с прежним порядком блоков."""
    kept, reordered = 0, 0
    for rel, f in pages():
        old = snap.get(rel)
        if old is None:
            continue
        new = f.read_text(encoding='utf-8')
        if new == old:
            continue
        oh, ob = _split(old)
        nh, nb = _split(new)
        same_body = _blank(ob) == _blank(nb)
        if same_body and _canon_head(oh) == _canon_head(nh):
            f.write_text(old, encoding='utf-8')
            kept += 1
            continue
        head = _reorder(oh, nh)
        if _canon_head(head) == _canon_head(oh) and not same_body:
            head = oh  # <head> по содержанию прежний — прежние и пробелы между блоками
        body = ob if same_body else nb
        res = head + body
        if res != new:
            f.write_text(res, encoding='utf-8')
            reordered += 1
    return kept, reordered
