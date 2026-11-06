#!/usr/bin/env python3
"""Пакет выкладки страницы гостиниц поверх текущего сайта (06.11.2026).

base   = файлы сайта после выкладки вентиляции 13:17 (= MANIFEST-2026-11-06-vent.sha256), из них собрана ветка deploy-gost
ours   = файлы с сайта сейчас (после выкладок складов 13:59 и санитарного аудита 14:14)
theirs = сборка ветки deploy-gost-2026-11-06 (deploy-vent + гостиницы), dist/timeweb

1. Страницы, которые есть в base: трёхстороннее слияние по токенам (токен заканчивается на «>»):
   правки сайта (base→ours) и правки гостиниц (base→theirs) не должны пересекаться.
2. Страницы сайта, которых нет в base (склады, санитарный аудит и т. п.): только ссылка меню
   ../#otrasl-gostinitsy → ../gostinitsy/ (ровно 3 раза: шапка, мобильное меню, подвал).
3. Новая страница гостиниц: те же правки меню, что на сайте получила страница-образец того же уровня
   (privacy/index.php, base→ours), — по якорям, каждый должен встретиться ровно один раз.

python3 merge-2026-11-06-gost.py BASE OURS THEIRS OUT
"""
import difflib, pathlib, re, sys

BASE, OURS, THEIRS, OUT = (pathlib.Path(a) for a in sys.argv[1:5])
REF = 'privacy/index.php'
NEW = 'gostinitsy/index.php'


def toks(s):
    t = re.split(r'(?<=>)', s)
    assert ''.join(t) == s
    return t


def opcodes(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [(tag, i1, i2, j1, j2) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal']


def changes(a, b):
    ta, tb = toks(a), toks(b)
    return [(''.join(ta[i1:i2]), ''.join(tb[j1:j2])) for _, i1, i2, j1, j2 in opcodes(ta, tb)]


def merge3(base, ours, theirs, name):
    tb, to, tt = toks(base), toks(ours), toks(theirs)
    eo = [(i1, i2, to[j1:j2]) for _, i1, i2, j1, j2 in opcodes(tb, to)]
    et = [(i1, i2, tt[j1:j2]) for _, i1, i2, j1, j2 in opcodes(tb, tt)]
    for a1, a2, _ in eo:
        for b1, b2, _ in et:
            overlap = max(a1, b1) < min(a2, b2)
            same_point = (a1 == a2 or b1 == b2) and (a1 == b1 or a2 == b2) and (a1 <= b2 and b1 <= a2)
            if overlap or same_point:
                sys.exit(f'{name}: правки пересекаются: base[{a1}:{a2}] и base[{b1}:{b2}]')
    out, pos = [], 0
    for i1, i2, rep in sorted(eo + et, key=lambda e: (e[0], e[1])):
        assert i1 >= pos, name
        out += tb[pos:i1] + rep
        pos = i2
    out += tb[pos:]
    return ''.join(out), len(eo), len(et)


def site_files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and (p.name == 'index.php' or p.name == 'sitemap.xml'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report, written = [], []
    base_files = set(site_files(BASE))
    for f in site_files(OURS):
        ours = (OURS / f).read_text(encoding='utf-8')
        if f in base_files:
            base = (BASE / f).read_text(encoding='utf-8')
            theirs = (THEIRS / f).read_text(encoding='utf-8')
            merged, no, nt = merge3(base, ours, theirs, f)
            assert changes(ours, merged) == changes(base, theirs), f + ': лишние отличия от сайта'
            assert changes(theirs, merged) == changes(base, ours), f + ': лишние отличия от сборки гостиниц'
            report.append(f'{f}: правок сайта после 13:17 — {no}, правок гостиниц — {nt}')
        else:
            depth = f.count('/')
            old = '<a href="' + '../' * depth + '#otrasl-gostinitsy">'
            new = '<a href="' + '../' * depth + 'gostinitsy/">'
            n = ours.count(old)
            assert n == 3, (f, n)
            merged = ours.replace(old, new)
            got = changes(ours, merged)
            assert len(got) == 3 and all(a == old and b == new for a, b in got), got
            report.append(f'{f}: ссылок меню на гостиницы — {n}')
        if merged != ours:
            (OUT / f).parent.mkdir(parents=True, exist_ok=True)
            (OUT / f).write_text(merged, encoding='utf-8')
            written.append(f)

    # новая страница: правки меню сайта после 13:17 по образцу privacy/index.php (тот же уровень ../).
    # Позиции правок образца переносятся на страницу гостиниц через совпадающие блоки токенов (меню одинаковые),
    # все правки применяются разом — соседние правки (рестораны и склады рядом) не мешают друг другу.
    tb = toks((BASE / REF).read_text(encoding='utf-8'))
    to = toks((OURS / REF).read_text(encoding='utf-8'))
    th = toks((THEIRS / NEW).read_text(encoding='utf-8'))
    blocks = difflib.SequenceMatcher(None, tb, th, autojunk=False).get_matching_blocks()
    edits = []
    for tag, i1, i2, j1, j2 in opcodes(tb, to):
        for a0, b0, size in blocks:
            if a0 <= i1 and i2 <= a0 + size and (i1 < a0 + size or i1 == i2):
                edits.append((b0 + (i1 - a0), b0 + (i2 - a0), to[j1:j2]))
                break
        else:
            sys.exit(f'{NEW}: не нашлось места для правки {tag} {"".join(tb[i1:i2])[:80]!r}')
    edits.sort()
    out, pos = [], 0
    for k1, k2, rep in edits:
        assert k1 >= pos, NEW
        out += th[pos:k1] + rep
        pos = k2
    out += th[pos:]
    s, src = ''.join(out), ''.join(th)
    assert changes(src, s) == changes(''.join(tb), ''.join(to)), NEW + ': правки меню не совпали с образцом'
    (OUT / NEW).parent.mkdir(parents=True, exist_ok=True)
    (OUT / NEW).write_text(s, encoding='utf-8')
    report.append(f'{NEW}: правок меню как на {REF} — {len(edits)}')
    print('\n'.join(report))
    print('файлов страниц в пакете:', len(written) + 1)


if __name__ == '__main__':
    main()
