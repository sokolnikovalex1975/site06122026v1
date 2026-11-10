"""Типографика и вырезка из шаблона — копия функций tools/razrabotka-ppk/build_page.py (typeset, plain, cut)."""
import re

from typo import typo  # noqa: F401  (tools/legal в sys.path ставит build_page.py)

NW_RE = re.compile(r'(?<![\w>-])([А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])')
# номера документов не разрываем на дефисе: «СанПиН 2.3/2.4.4282-26», «52-ФЗ», «ТР ТС 021/2011»
CODE_RE = re.compile(r'(?<![\w/.-])((?:\d+[./])*\d+-(?:\d+|ФЗ)(?:[-/]\d+)*)(?![\w-])')
TRTS_RE = re.compile(r'ТР ТС (\d{3}/\d{4})')
DOC_RE = re.compile(r'\b(СП|СанПиН|ГОСТ|МУК|МУ|МР) (?=\d|<span class="nw">\d)')
SKIP = {'svg', 'script', 'style', 'option', 'textarea', 'title', 'select'}
VOID = {'img', 'input', 'br', 'source', 'meta', 'link', 'hr'}


def typeset(html):
    """Типографика только в тексте: неразрывные пробелы и слова через дефис без переноса (класс nw).
    Атрибуты, svg, option и скрипты не трогаем."""
    out, stack = [], []
    for part in re.split(r'(<[^>]+>)', html):
        if part.startswith('<'):
            m = re.match(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)', part)
            if m:
                tag, closing = m.group(2).lower(), m.group(1) == '/'
                if tag in SKIP and tag not in VOID and not part.endswith('/>'):
                    if closing:
                        if stack and stack[-1] == tag:
                            stack.pop()
                    else:
                        stack.append(tag)
            out.append(part)
            continue
        if stack or not part.strip():
            out.append(part)
            continue
        t = NW_RE.sub(r'<span class="nw">\1</span>', part)
        t = CODE_RE.sub(r'<span class="nw">\1</span>', t)
        t = TRTS_RE.sub(r'<span class="nw">ТР ТС \1</span>', t)
        t = typo(t)
        # обозначение документа не отрывается от номера: «СП 1.1.1058-01», «СанПиН 2.3/2.4.4282-26»
        t = DOC_RE.sub('\\1\u00a0', t)
        out.append(t)
    return ''.join(out)


def plain(html):
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html))
    return t.replace('&nbsp;', ' ').replace('\u00a0', ' ').replace('&amp;', '&').strip()



def cut(s, start, end, after=False):
    i = s.index(start)
    j = s.index(end, i)
    return s[i:j + (len(end) if after else 0)]


