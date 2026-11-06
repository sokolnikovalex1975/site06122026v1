"""Лёгкий разбор HTML с позициями открывающих тегов в исходном тексте.

Нужен, чтобы точечно добавлять атрибуты (data-split, data-fade и т. п.), не пересобирая разметку:
всё, кроме изменённых открывающих тегов, остаётся байт в байт как было.
"""
from html.parser import HTMLParser
import re

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
RAW = {'script', 'style'}


class Node:
    __slots__ = ('tag', 'attrs', 'parent', 'children', 'start', 'end_open', 'raw_open')

    def __init__(self, tag, attrs, parent, start, end_open, raw_open):
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children, self.start, self.end_open, self.raw_open = [], start, end_open, raw_open

    @property
    def classes(self):
        return (self.attrs.get('class') or '').split()

    def has_class(self, *names):
        c = self.classes
        return any(n in c for n in names)

    def iter(self):
        for ch in self.children:
            yield ch
            yield from ch.iter()

    def ancestors(self):
        p = self.parent
        while p is not None:
            yield p
            p = p.parent

    def closest(self, pred):
        n = self
        while n is not None:
            if n.tag != '#root' and pred(n):
                return n
            n = n.parent
        return None

    def __repr__(self):
        return f'<{self.tag} {self.attrs.get("id","")} {self.attrs.get("class","")}>'


class _P(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        # смещения начала строк — для перевода (строка, колонка) в абсолютную позицию
        self.lines = [0]
        for m in re.finditer('\n', text):
            self.lines.append(m.end())
        self.root = Node('#root', {}, None, 0, 0, '')
        self.cur = self.root

    def _abs(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._abs()
        raw = self.get_starttag_text()
        n = Node(tag, {k: (v if v is not None else '') for k, v in attrs}, self.cur, start, start + len(raw), raw)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        start = self._abs()
        raw = self.get_starttag_text()
        n = Node(tag, {k: (v if v is not None else '') for k, v in attrs}, self.cur, start, start + len(raw), raw)
        self.cur.children.append(n)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent


def parse(text):
    p = _P(text)
    p.feed(text)
    p.close()
    return p.root


class Editor:
    """Копит правки открывающих тегов и вставки, применяет их разом с конца документа."""

    def __init__(self, text):
        self.text = text
        self.root = parse(text)
        self.attr_add = {}   # start -> (node, {name: value})
        self.inserts = []    # (pos, order, html)

    def add_attr(self, node, name, value=None):
        if name in node.attrs:
            return False
        d = self.attr_add.setdefault(node.start, (node, {}))[1]
        if name in d:
            return False
        d[name] = value
        node.attrs[name] = value if value is not None else ''
        return True

    def insert(self, pos, html, order=0):
        self.inserts.append((pos, order, html))

    def result(self):
        edits = []
        for start, (node, attrs) in self.attr_add.items():
            raw = node.raw_open
            tail = '/>' if raw.endswith('/>') else '>'
            body = raw[: -len(tail)]
            extra = ''.join(f' {k}' if v is None else f' {k}="{v}"' for k, v in attrs.items())
            edits.append((node.start, node.end_open, body + extra + tail))
        for pos, order, html in self.inserts:
            edits.append((pos, pos, html))
        # с конца, чтобы позиции не съезжали; вставки в одну точку — в порядке добавления
        edits.sort(key=lambda e: (e[0], e[1]), reverse=True)
        out = self.text
        for a, b, rep in edits:
            out = out[:a] + rep + out[b:]
        return out
