#!/usr/bin/env python3
"""Иллюстрации плиток «Направления исследований» из мастер-файлов Nano Banana Pro.

    python3 tools/laboratornye-issledovaniya/make_tiles.py <папка с lab-<код>.png>

Мастера (PNG 2400×1792, 4:3, чёрный фон, без сжатия) лежат в файлах проекта
«Страница Лабораторные исследования/Визуалы v1/Плитки направлений».
Из каждого мастера: обрезка по объектам с полями → кадр 4:3 на чёрном фоне →
img/lab-t-<код>-640.webp (компьютер, 2×) и img/lab-t-<код>-360.webp (телефон, 2×).
"""
import pathlib
import sys

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import data as D  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
Q = 78
SRC = pathlib.Path(sys.argv[1])


def content_box(im):
    # всё, что заметно светлее фона, считаем объектом
    mask = im.convert('L').point(lambda v: 255 if v > 14 else 0)
    return mask.getbbox()


for code, *_ in D.GROUPS:
    im = Image.open(SRC / f'lab-{code}.png').convert('RGB')
    x0, y0, x1, y1 = content_box(im)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # объект занимает ~78% ширины или ~80% высоты кадра 4:3
    w = max((x1 - x0) / .78, (y1 - y0) / .80 * 4 / 3)
    h = w * 3 / 4
    box = (round(cx - w / 2), round(cy - h / 2), round(cx + w / 2), round(cy + h / 2))
    canvas = Image.new('RGB', (round(w), round(h)), (0, 0, 0))
    canvas.paste(im.crop((max(box[0], 0), max(box[1], 0), min(box[2], im.width), min(box[3], im.height))),
                 (max(-box[0], 0), max(-box[1], 0)))
    for tw in (640, 360):
        out = IMG / f'lab-t-{code}-{tw}.webp'
        canvas.resize((tw, tw * 3 // 4), Image.LANCZOS).save(out, 'WEBP', quality=Q, method=6)
        print(f'ok {out.relative_to(ROOT)} {out.stat().st_size // 1024} КБ')
