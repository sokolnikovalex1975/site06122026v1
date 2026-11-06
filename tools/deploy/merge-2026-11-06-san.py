#!/usr/bin/env python3
"""(Запускалось в песочнице 06.11.2026; пути — временные папки той сессии.)
Пакет выкладки санитарного аудита поверх текущего сайта (после выкладки складов 13:59).

base   = /tmp/qa/dist_before       — сборка ветки deploy-vent (сайт до выкладки складов)
ours   = /tmp/qa/live3             — файлы с сайта сейчас (= MANIFEST выкладки складов)
theirs = deploy-san/dist/timeweb   — сборка deploy-vent + санитарный аудит

Для 14 страниц и sitemap.xml — трёхсторонее слияние по токенам (токен заканчивается на «>»):
правки складов (base→ours) и правки аудита (base→theirs) не должны пересекаться.
Страница складов (её нет в base) получает те же три вставки меню, что и страница пищевого производства.
Новая страница аудита получает правку меню складов: ../#otrasl-sklady → ../sklady-i-logistika/.
"""
import difflib, hashlib, pathlib, re, sys

BASE = pathlib.Path('/tmp/qa/dist_before')
OURS = pathlib.Path('/tmp/qa/live3')
THEIRS = pathlib.Path('/home/user/workspace/deploy-san/dist/timeweb')
OUT = pathlib.Path(sys.argv[1])
PAGES = ['index.php', 'deratizatsiya/index.php', 'dezinsektsiya/index.php', 'ochistka-dezinfektsiya-ventilyatsii/index.php',
         'dogovor-deratizatsiya-dezinsektsiya/index.php', 'pishchevoe-proizvodstvo/index.php', 'magaziny-i-torgovye-seti/index.php',
         'farmatsevticheskie-proizvodstva/index.php', 'materialy/index.php', 'materialy/programma-pest-kontrolya/index.php',
         'materialy/zhurnal-pest-kontrolya/index.php', 'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php',
         'privacy/index.php', 'soglasie/index.php', 'sitemap.xml']


def toks(s):
    t = re.split(r'(?<=>)', s)
    assert ''.join(t) == s
    return t


def opcodes(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [(tag, i1, i2, j1, j2) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal']


def merge3(base, ours, theirs, name):
    tb, to, tt = toks(base), toks(ours), toks(theirs)
    eo = [(i1, i2, to[j1:j2]) for _, i1, i2, j1, j2 in opcodes(tb, to)]
    et = [(i1, i2, tt[j1:j2]) for _, i1, i2, j1, j2 in opcodes(tb, tt)]
    # пересечения: диапазоны base не должны перекрываться и не должны быть вставками в одну точку
    for a1, a2, _ in eo:
        for b1, b2, _ in et:
            overlap = max(a1, b1) < min(a2, b2)
            same_point = (a1 == a2 or b1 == b2) and (a1 == b1 or a2 == b2) and (a1 <= b2 and b1 <= a2)
            if overlap or same_point:
                sys.exit(f'{name}: правки пересекаются: base[{a1}:{a2}] и base[{b1}:{b2}]')
    edits = sorted(eo + et, key=lambda e: (e[0], e[1]))
    out, pos = [], 0
    for i1, i2, rep in edits:
        assert i1 >= pos, name
        out += tb[pos:i1] + rep
        pos = i2
    out += tb[pos:]
    return ''.join(out), len(eo), len(et)


def changes(a, b):
    ta, tb = toks(a), toks(b)
    return [(''.join(ta[i1:i2]), ''.join(tb[j1:j2])) for _, i1, i2, j1, j2 in opcodes(ta, tb)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for f in PAGES:
        base = (BASE / f).read_text(encoding='utf-8')
        ours = (OURS / f).read_text(encoding='utf-8')
        theirs = (THEIRS / f).read_text(encoding='utf-8')
        merged, no, nt = merge3(base, ours, theirs, f)
        # проверка: от сайта отличаемся ровно правками аудита, от сборки аудита — ровно правками складов
        assert changes(ours, merged) == changes(base, theirs), f + ': лишние отличия от сайта'
        assert changes(theirs, merged) == changes(base, ours), f + ': лишние отличия от сборки аудита'
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        (OUT / f).write_text(merged, encoding='utf-8')
        report.append(f'{f}: правок складов {no}, правок аудита {nt}')

    # страница складов: три вставки меню, как на странице пищевого производства (тот же root ../)
    f = 'pishchevoe-proizvodstvo/index.php'
    tb = toks((BASE / f).read_text(encoding='utf-8'))
    tt = toks((THEIRS / f).read_text(encoding='utf-8'))
    ins = []
    for tag, i1, i2, j1, j2 in opcodes(tb, tt):
        if tag == 'insert' and 'sanitarnyy-audit/' in ''.join(tt[j1:j2]):
            ins.append((''.join(tb[max(0, i1 - 4):i1]), ''.join(tt[j1:j2])))
    assert len(ins) == 3, ins
    sk = 'sklady-i-logistika/index.php'
    s = (OURS / sk).read_text(encoding='utf-8')
    for anchor, add in ins:
        assert s.count(anchor) == 1, (sk, anchor)
        s = s.replace(anchor, anchor + add, 1)
    got = changes((OURS / sk).read_text(encoding='utf-8'), s)
    assert len(got) == 3 and all(a == '' and 'sanitarnyy-audit/' in b for a, b in got), got
    (OUT / sk).parent.mkdir(parents=True, exist_ok=True)
    (OUT / sk).write_text(s, encoding='utf-8')
    report.append(f'{sk}: вставок меню {len(got)}')

    # новая страница: меню как на сайте после выкладки складов
    sa = 'sanitarnyy-audit/index.php'
    s = (THEIRS / sa).read_text(encoding='utf-8')
    n = s.count('<a href="../#otrasl-sklady">')
    assert n == 3, n
    s = s.replace('<a href="../#otrasl-sklady">', '<a href="../sklady-i-logistika/">')
    (OUT / sa).parent.mkdir(parents=True, exist_ok=True)
    (OUT / sa).write_text(s, encoding='utf-8')
    report.append(f'{sa}: ссылок меню на склады {n}')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
