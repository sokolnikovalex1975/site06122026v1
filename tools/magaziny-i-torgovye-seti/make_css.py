#!/usr/bin/env python3
"""Собирает extra.css страницы «Магазины и торговые сети».

Берёт общие блоки внутренних страниц из tools/dezinsektsiya/extra.css и карту зон из tools/food/extra.css,
оставляет только правила с классами, которые есть в main.html, и добавляет собственные блоки из own.css.
python3 tools/magaziny-i-torgovye-seti/make_css.py  ->  tools/magaziny-i-torgovye-seti/extra.css
"""
import pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent
main = (HERE / 'main.html').read_text(encoding='utf-8')

used = set()
for cls in re.findall(r'class="([^"]+)"', main):
    used.update(cls.split())
used |= {'on', 'warn', 'bg-in', 'open', 'sent', 'err', 'ok', 'bad', 'is-on'}


def blocks(css):
    """Разбивает CSS на верхнеуровневые правила и @-блоки."""
    out, i = [], 0
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    while i < len(css):
        j = css.find('{', i)
        if j < 0:
            break
        sel = css[i:j].strip()
        if sel.startswith('@'):
            depth, k = 1, j + 1
            while depth and k < len(css):
                depth += {'{': 1, '}': -1}.get(css[k], 0)
                k += 1
            out.append((sel, css[j + 1:k - 1]))
            i = k
        else:
            k = css.find('}', j)
            out.append((sel, css[j + 1:k]))
            i = k + 1
    return out


def keep(sel):
    for part in sel.split(','):
        classes = re.findall(r'\.([a-zA-Z0-9_-]+)', part)
        if all(c in used for c in classes):
            return True
    return False


def purge(css):
    res = []
    for sel, body in blocks(css):
        if sel.startswith('@keyframes') or sel.startswith('@font-face'):
            res.append(f'{sel}{{{body}}}')
        elif sel.startswith('@'):
            inner = ''.join(f'{s}{{{b}}}' for s, b in blocks(body) if keep(s))
            if inner:
                res.append(f'{sel}{{{inner}}}')
        elif keep(sel):
            res.append(f'{sel}{{{body}}}')
    return '\n'.join(res)


base = purge((TOOLS / 'dezinsektsiya' / 'extra.css').read_text(encoding='utf-8'))
zones = purge(re.sub(r'\.f-(zmap|plan)\b', r'.t-\1', (TOOLS / 'food' / 'extra.css').read_text(encoding='utf-8')))
own = (HERE / 'own.css').read_text(encoding='utf-8')

# правила из food, которые уже переопределены в own.css (t-zmap/t-plan), не дублируем
zones = '\n'.join(l for l in zones.split('\n') if not re.match(r'\.t-(zmap|plan)', l))

css = '/* ===== Общие блоки внутренних страниц (из tools/dezinsektsiya/extra.css) ===== */\n' + base + \
      '\n/* ===== Легенда и список зон (из tools/food/extra.css) ===== */\n' + zones + '\n' + own
(HERE / 'extra.css').write_text(css, encoding='utf-8')
print('extra.css:', len(css), 'символов')
