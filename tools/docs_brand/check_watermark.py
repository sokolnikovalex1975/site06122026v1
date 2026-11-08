#!/usr/bin/env python3
"""Проверка: водяной знак «пестконтроль-центр.рф» лежит поверх содержимого на каждой странице PDF.

Правило сайта (владелец, 08.11.2026): знак не должен сливаться с фоном блоков — заливка ячеек, плашек, таблиц
и картинки не должны его закрывать. Знак — векторный контур цвета #7c4dff с прозрачностью (tools/zhurnal/wm.py).

Скрипт находит контуры знака на странице и по порядку рисования (Page.get_bboxlog) ищет всё, что нарисовано
после него и закрывает его заливкой: залитые фигуры (в том числе белые), картинки, градиенты крупнее 20×4 pt.
Текст поверх знака допускается — он знак не прячет.

    python3 tools/docs_brand/check_watermark.py <файлы PDF>       # без аргументов — все PDF сайта (кроме tools/ и dist/)

Код выхода 1, если хотя бы на одной странице знака нет или он закрыт.
"""
import pathlib
import sys

import pymupdf as fitz

WM_RGB = (0x7C / 255, 0x4D / 255, 1.0)


def is_wm(dr):
    f, op = dr.get("fill"), dr.get("fill_opacity")
    return (f is not None and len(f) == 3 and all(abs(a - b) < 0.02 for a, b in zip(f, WM_RGB))
            and op is not None and op < 0.5)


def audit(path):
    doc = fitz.open(path)
    out = []
    for pno, page in enumerate(doc, 1):
        wms = [dr for dr in page.get_drawings() if is_wm(dr)]
        if not wms:
            out.append((pno, "нет знака", 0))
            continue
        wseqs = {dr["seqno"] for dr in wms}
        first = min(wseqs)
        area = fitz.Rect()
        for dr in wms:
            area |= dr["rect"]
        covering = 0
        for idx, (kind, bbox) in enumerate(page.get_bboxlog()):
            if idx <= first or idx in wseqs or kind not in ("fill-path", "fill-image", "fill-shade"):
                continue
            r = fitz.Rect(bbox)
            if r.width > 20 and r.height > 4 and r.intersects(area):
                covering += 1
        out.append((pno, "поверх" if not covering else "закрыт", covering))
    return out


def main(argv):
    root = pathlib.Path(__file__).resolve().parents[2]
    files = [pathlib.Path(a) for a in argv] or sorted(
        p for p in root.rglob("*.pdf") if not {"tools", "dist", ".git", "node_modules"} & set(p.relative_to(root).parts))
    bad_total = 0
    for f in files:
        res = audit(str(f))
        bad = [r for r in res if r[1] != "поверх"]
        bad_total += len(bad)
        name = f.relative_to(root) if f.is_absolute() and root in f.parents else f
        print(f"{name}: стр. {len(res)} — " + ("знак поверх на всех" if not bad else f"ПРОБЛЕМЫ {bad[:8]}"))
    print(f"итого файлов {len(files)}, страниц с проблемой: {bad_total}")
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
