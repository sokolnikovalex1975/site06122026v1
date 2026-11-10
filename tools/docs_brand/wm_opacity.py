#!/usr/bin/env python3
"""Прозрачность водяного знака «пестконтроль-центр.рф» в готовых PDF сайта — без пересборки документов.

Владелец, 10.11.2026: знак на всех документах сайта — 18 % (было 12 %). Новые сборки берут 18 % из
tools/docs_brand/brand.py (WM) и tools/zhurnal/wm.py; этот скрипт меняет уже готовые PDF.

Знак во всех PDF сайта — векторный контур цвета #7c4dff (tools/zhurnal/wm.py); прозрачность заливки задаёт
ExtGState /ca, который включается оператором gs сразу после цвета знака (q … cm  RG rg  /Gn gs  контуры  f Q).
Скрипт:
1) находит ExtGState с прежней прозрачностью и все потоки (страницы, формы XObject), где он включается;
2) проверяет каждое включение: перед ним цвет #7c4dff, после — только контуры и заливка до восстановления
   состояния (Q); если тот же ExtGState нужен чему-то ещё, файл не меняется (код выхода 2);
3) ставит /ca новое значение, дату изменения — сейчас, сохраняет как генераторы (garbage=4, deflate);
4) сверяет новый файл с прежним: страницы, текст и его прозрачность, метаданные (кроме даты изменения), картинки,
   порядок рисования, все рисунки, кроме прозрачности знака, — без изменений; растровое сравнение — пиксели
   меняются только в области знака; знак на всех страницах поверх содержимого (check_watermark.audit).

    python3 tools/docs_brand/wm_opacity.py 0.18 файл.pdf ...   # на месте; уже 0.18 — файл не трогается
"""
import pathlib
import re
import sys
import tempfile

import numpy as np
import pymupdf as fitz

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_watermark import audit, is_wm  # noqa: E402

WM_RGB = (0.4863, 0.302, 1.0)     # #7c4dff в потоках Skia (Chromium): «.4863 .302 1 rg»
OLD = (0.115, 0.125)              # прежняя прозрачность знака — 0.12
DELIM = b'()<>[]{}/%'
WS = b'\x00\t\n\x0c\r '
PATH_OPS = {b'm', b'l', b'c', b'v', b'y', b'h', b're', b'f', b'F', b'f*', b'B', b'B*', b'b', b'b*', b'n', b'S', b's',
            b'W', b'W*', b'cm', b'q', b'Q', b'w', b'J', b'j', b'M', b'd', b'i', b'ri'}


def tokens(data):
    """Операторы потока содержимого PDF: (оператор, операнды, позиция). Строки, массивы, словари, BI…EI."""
    i, n, ops = 0, len(data), []
    while i < n:
        ch = data[i:i + 1]
        if ch in WS:
            i += 1
        elif ch == b'%':
            while i < n and data[i:i + 1] not in b'\r\n':
                i += 1
        elif ch == b'(':
            depth, i = 1, i + 1
            while i < n and depth:
                c = data[i:i + 1]
                if c == b'\\':
                    i += 2
                    continue
                depth += (c == b'(') - (c == b')')
                i += 1
            ops.append(('str', None, i))
        elif data.startswith(b'<<', i) or data.startswith(b'>>', i):
            ops.append(('dict', None, i)); i += 2
        elif ch == b'<':
            j = data.index(b'>', i); ops.append(('str', None, j)); i = j + 1
        elif ch in b'[]{}':
            ops.append(('arr', None, i)); i += 1
        elif ch == b'/':
            j = i + 1
            while j < n and data[j:j + 1] not in WS and data[j:j + 1] not in DELIM:
                j += 1
            ops.append(('name', data[i + 1:j], i)); i = j
        else:
            j = i
            while j < n and data[j:j + 1] not in WS and data[j:j + 1] not in DELIM:
                j += 1
            word = data[i:j]
            if not word:
                raise ValueError(f'непонятный байт {data[i:i + 1]!r} в позиции {i}')
            if re.fullmatch(rb'[+-]?(\d+\.?\d*|\.\d+)', word):
                ops.append(('num', float(word), i))
            elif word in (b'true', b'false', b'null'):
                ops.append(('kw', word, i))
            else:
                ops.append(('op', word, i))
                if word == b'ID':  # встроенная картинка: данные до «EI»
                    m = re.compile(rb'\sEI(?=[\s]|$)').search(data, j + 1)
                    if not m:
                        raise ValueError('BI … ID без EI')
                    j = m.end()
            i = j
    # операнды к операторам
    out, stack = [], []
    for kind, val, pos in ops:
        if kind == 'op':
            out.append((val, stack, pos)); stack = []
        else:
            stack.append((kind, val))
    return out


def egs_map(doc, owner):
    """Имена ExtGState из /Resources объекта owner → xref."""
    t, v = doc.xref_get_key(owner, 'Resources/ExtGState')
    if t == 'null':
        return {}
    if t == 'xref':
        v = doc.xref_object(int(v.split()[0]), compressed=True)
    res = {m.group(1).encode(): int(m.group(2)) for m in re.finditer(r'/([^\s/<>\[\]()]+)\s*(\d+)\s+0\s+R', v)}
    if re.search(r'/[^\s/<>\[\]()]+\s*<<', v):
        raise ValueError(f'объект {owner}: ExtGState без ссылки (вложенный словарь) — не поддерживается')
    return res


def ca_of(doc, x):
    t, v = doc.xref_get_key(x, 'ca')
    return float(v) if t == 'float' or t == 'int' else None


def streams_with(doc, target):
    """Потоки, в /Resources которых есть ExtGState target: [(xref потока, {имена})]."""
    found = []
    for x in range(1, doc.xref_length()):
        try:
            names = {k for k, v in egs_map(doc, x).items() if v == target}
        except ValueError:
            raise
        except Exception:
            continue
        if not names:
            continue
        typ = doc.xref_get_key(x, 'Type')[1]
        if typ == '/Page':
            t, v = doc.xref_get_key(x, 'Contents')
            xs = [int(a) for a in re.findall(r'(\d+)\s+0\s+R', v)]
            found += [(c, names) for c in xs]
        elif doc.xref_is_stream(x):
            found.append((x, names))
        else:
            raise ValueError(f'объект {x} ({typ}) ссылается на ExtGState {target} — не поддерживается')
    return found


def check_usage(data, names):
    """Каждое «/имя gs» — знак: перед ним заливка #7c4dff, после — только контуры до Q. Возвращает (знак, прочее)."""
    ops = tokens(data)
    fill = [None]   # стек цвета заливки по q/Q
    wm_uses, other = 0, []
    k = 0
    while k < len(ops):
        op, args, pos = ops[k]
        if op == b'q':
            fill.append(fill[-1])
        elif op == b'Q':
            if len(fill) > 1:
                fill.pop()
        elif op == b'rg':
            fill[-1] = tuple(round(a[1], 4) for a in args)
        elif op in (b'g', b'k', b'sc', b'scn', b'cs'):
            fill[-1] = ('other', op)
        elif op == b'gs' and args and args[-1][0] == 'name' and args[-1][1] in names:
            ok = fill[-1] is not None and len(fill[-1]) == 3 and all(
                isinstance(a, float) and abs(a - b) < 0.002 for a, b in zip(fill[-1], WM_RGB))
            level, j, bad = len(fill), k + 1, None
            depth = level
            while j < len(ops):
                op2, args2, _ = ops[j]
                if op2 == b'q':
                    depth += 1
                elif op2 == b'Q':
                    depth -= 1
                    if depth < level:
                        break
                elif op2 in (b'rg', b'RG'):
                    if any(abs(a[1] - b) > 0.002 for a, b in zip(args2, WM_RGB)):
                        bad = op2
                elif op2 not in PATH_OPS:
                    bad = op2
                if bad:
                    break
                j += 1
            if ok and not bad:
                wm_uses += 1
            else:
                other.append((pos, 'цвет' if not ok else bad.decode('latin-1')))
        k += 1
    return wm_uses, other


def drawings_signature(page):
    sig = []
    for dr in page.get_drawings():
        d = {k: v for k, v in dr.items() if k not in ('fill_opacity',)}
        d['items'] = [tuple(str(p) for p in it) for it in dr['items']]
        sig.append((is_wm(dr), round(dr.get('fill_opacity') or 0, 4), repr(sorted(d.items(), key=lambda kv: kv[0]))))
    return sig


def text_signature(page):
    out = []
    for sp in page.get_texttrace():
        out.append((sp['font'], round(sp['size'], 3), sp['color'], sp['opacity'], sp.get('type'),
                    tuple((c[0], tuple(round(a, 2) for a in c[3])) for c in sp['chars'])))
    return out


def verify(src, dst, target):
    a, b = fitz.open(src), fitz.open(dst)
    assert len(a) == len(b), 'число страниц'
    ma, mb = dict(a.metadata), dict(b.metadata)
    ma.pop('modDate'); mb.pop('modDate')
    assert ma == mb, f'метаданные: {ma} / {mb}'
    changed_px = 0
    for pa, pb in zip(a, b):
        assert pa.rect == pb.rect, 'размер страницы'
        assert pa.get_text() == pb.get_text(), f'текст, стр. {pa.number + 1}'
        assert text_signature(pa) == text_signature(pb), f'шрифты/цвет/прозрачность текста, стр. {pa.number + 1}'
        assert pa.get_bboxlog() == pb.get_bboxlog(), f'порядок рисования, стр. {pa.number + 1}'
        ia = [(i[2], i[3], i[4], i[5]) for i in pa.get_images(full=True)]
        ib = [(i[2], i[3], i[4], i[5]) for i in pb.get_images(full=True)]
        assert ia == ib, f'картинки, стр. {pa.number + 1}'
        sa, sb = drawings_signature(pa), drawings_signature(pb)
        assert len(sa) == len(sb), f'число рисунков, стр. {pa.number + 1}'
        wm_rect = fitz.Rect()
        n_wm = 0
        for (wa, oa, ra), (wb, ob, rb), dr in zip(sa, sb, pa.get_drawings()):
            assert ra == rb, f'рисунок изменился, стр. {pa.number + 1}'
            if wa:
                n_wm += 1
                wm_rect |= dr['rect']
                assert abs(ob - target) < 0.002, f'прозрачность знака {ob}, стр. {pa.number + 1}'
            else:
                assert oa == ob, f'прозрачность не знака изменилась ({oa} → {ob}), стр. {pa.number + 1}'
        assert n_wm, f'нет знака, стр. {pa.number + 1}'
        # растровое сравнение: всё, что изменилось, — в прямоугольнике знака
        xa, xb = pa.get_pixmap(dpi=72, alpha=False), pb.get_pixmap(dpi=72, alpha=False)
        ra_ = np.frombuffer(xa.samples, np.uint8).reshape(xa.height, xa.width, 3)
        rb_ = np.frombuffer(xb.samples, np.uint8).reshape(xb.height, xb.width, 3)
        ys, xs = np.nonzero((ra_ != rb_).any(axis=2))
        changed_px += len(xs)
        area = (wm_rect + (-2, -2, 2, 2)) & pa.rect
        out = (xs + 0.5 < area.x0) | (xs + 0.5 > area.x1) | (ys + 0.5 < area.y0) | (ys + 0.5 > area.y1)
        assert not out.any(), f'{int(out.sum())} пикс. вне знака изменились, стр. {pa.number + 1}'
    res = audit(str(dst))
    bad = [r for r in res if r[1] != 'поверх']
    assert not bad, f'знак не поверх: {bad}'
    return changed_px


def process(path, target):
    path = pathlib.Path(path)
    doc = fitz.open(path)
    ops = {round(dr['fill_opacity'], 3) for p in doc for dr in p.get_drawings() if is_wm(dr)}
    if ops == {round(target, 3)}:
        print(f'{path}: уже {target} — без изменений')
        return 0
    cands = [x for x in range(1, doc.xref_length())
             if not doc.xref_is_stream(x) and ca_of(doc, x) is not None and OLD[0] <= ca_of(doc, x) <= OLD[1]]
    done = []
    for x in cands:
        uses = streams_with(doc, x)
        n_wm, other = 0, []
        for sx, names in uses:
            w, o = check_usage(doc.xref_stream(sx), names)
            n_wm += w
            other += [(sx,) + t for t in o]
        if n_wm and other:
            raise SystemExit(f'{path}: ExtGState {x} (ca {ca_of(doc, x)}) нужен не только знаку: {other[:5]} — не меняю')
        if n_wm:
            doc.xref_set_key(x, 'ca', f'{target:g}'.lstrip('0') if target < 1 else '1')
            done.append((x, n_wm, len(uses)))
    if not done:
        raise SystemExit(f'{path}: ExtGState знака не найден (прозрачность знака сейчас {ops})')
    doc.set_metadata({'modDate': fitz.get_pdf_now()})
    with tempfile.NamedTemporaryFile(suffix='.pdf', dir=path.parent, delete=False) as tf:
        tmp = pathlib.Path(tf.name)
    try:
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        px = verify(path, tmp, target)
        old_size = path.stat().st_size
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()
    print(f'{path}: знак {sorted(ops)} → {target}; ExtGState {[d[0] for d in done]}, включений знака '
          f'{sum(d[1] for d in done)} в {sum(d[2] for d in done)} потоках; сверка OK, изменилось пикселей '
          f'(72 dpi) {px}; {old_size} → {path.stat().st_size} байт')
    return 1


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    tgt = float(sys.argv[1])
    n = sum(process(f, tgt) for f in sys.argv[2:])
    print(f'изменено файлов: {n} из {len(sys.argv) - 2}')
