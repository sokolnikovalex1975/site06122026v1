#!/usr/bin/env python3
"""Иконки направлений и шагов «Порядка работы» из мастер-файлов Nano Banana Pro (вариант G).

    python3 tools/laboratornye-issledovaniya/make_tiles.py <папка с mono-<код>.png и mono-s1…s5.png>

Мастера (PNG 2048×2048, белый матовый предмет с фиолетовыми деталями на чёрном фоне, без сжатия) лежат
в файлах проекта «Страница Лабораторные исследования/Визуалы v4 — фирменные цвета/G Предмет-макет».

Фон убирается без потери свечения: прозрачность пикселя = его яркость по самому светлому каналу,
цвет делится на прозрачность (обратное «наложению на чёрный»). На тёмных карточках сайта результат
совпадает с мастером, но без квадрата фона. Затем — обрезка по предмету в квадрат с полем 4%.

  img/lab-i-<код>.webp — плитки направлений (192×192: 96 px на компьютере, 64 px на телефоне, ×2)
  img/lab-s<N>.webp    — шаги «Порядка работы» (240×240: 120 px, ×2)
"""
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import data as D  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
SRC = pathlib.Path(sys.argv[1])
FLOOR = 16   # шум чёрного фона, ниже — полностью прозрачно


def unscreen(im):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    mx = a.max(-1)
    alpha = np.clip((mx - FLOOR) / (255 - FLOOR), 0, 1)
    rgb = np.where(alpha[..., None] > 0, a / np.maximum(mx, 1)[..., None] * 255, 0)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def square_crop(im, pad=.04):
    box = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    x0, y0, x1, y1 = box
    side = max(x1 - x0, y1 - y0) * (1 + 2 * pad)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    canvas = Image.new('RGBA', (round(side), round(side)), (0, 0, 0, 0))
    l, t = round(cx - side / 2), round(cy - side / 2)
    canvas.paste(im.crop((max(l, 0), max(t, 0), min(l + round(side), im.width), min(t + round(side), im.height))),
                 (max(-l, 0), max(-t, 0)))
    return canvas


def make(src, out, size):
    im = square_crop(unscreen(Image.open(src))).resize((size, size), Image.LANCZOS)
    im.save(out, 'WEBP', quality=80, alpha_quality=70, method=6)
    print(f'ok {out.relative_to(ROOT)} {out.stat().st_size // 1024} КБ')


for code, *_ in D.GROUPS:
    make(SRC / f'mono-{code}.png', IMG / f'lab-i-{code}.webp', 192)
for n in range(1, 6):
    make(SRC / f'mono-s{n}.png', IMG / f'lab-s{n}.webp', 240)
