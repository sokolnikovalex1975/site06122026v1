#!/usr/bin/env python3
"""Фото страниц «Дезинсекция кафе, ресторанов и столовых» и «Дератизация ресторанов и кафе» (11.11.2026).

    python3 tools/restorany-uslugi/make_images.py <dzr-hero-v1.png> <drr-hero-v1.png> <drr-pipe-v1.png>

Мастера (Nano Banana Pro, PNG без сжатия) — в файлах проекта, папки страниц, «Визуалы v1».
Первый экран: компьютер — кадр целиком 1920×1072 и 1440×804, телефон — правая часть 4:3 (1024×768, 760×570),
соцсети — 1200×630 по центру. Проходка трубы для блока «Как мыши и крысы попадают в ресторан» — 960 и 640 px, 4:3.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
Q = 80


def save(im, path, fmt='WEBP', **kw):
    im.save(path, fmt, **kw)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


def hero(src, name):
    im = Image.open(src).convert('RGB')
    assert im.size == (2752, 1536), im.size
    for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
        save(im.resize((w, h), Image.LANCZOS), IMG / f'{name}{s}.webp', quality=Q, method=6)
    mob = im.crop((2752 - 2048, 0, 2752, 1536))
    for w, h, s in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
        save(mob.resize((w, h), Image.LANCZOS), IMG / f'{name}{s}.webp', quality=Q, method=6)
    oh = round(2752 * 630 / 1200)
    top = (1536 - oh) // 2
    save(im.crop((0, top, 2752, top + oh)).resize((1200, 630), Image.LANCZOS), IMG / f'{name.replace("-hero", "")}-og.jpg', 'JPEG',
         quality=82, optimize=True, progressive=True)


hero(sys.argv[1], 'dzr-hero')
hero(sys.argv[2], 'drr-hero')
pipe = Image.open(sys.argv[3]).convert('RGB')
for w in (960, 640):
    save(pipe.resize((w, round(w * pipe.height / pipe.width)), Image.LANCZOS), IMG / f'drr-prohodka-{w}.webp', quality=Q, method=6)
