#!/usr/bin/env python3
"""Фото первого экрана страницы «Лабораторные исследования» из мастер-файла.

    python3 tools/laboratornye-issledovaniya/make_images.py <lab-hero-v1-master.png>

Мастер (PNG 1536×1024, 3:2, без сжатия) — в файлах проекта «Страница Лабораторные исследования/Визуалы v1».
Компьютер — кадр 1536×858 от верхнего края (как 1920×1072 у остальных страниц), телефон — правая часть 4:3.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
NAME = 'lab-hero'
Q = 80


def save(im, path):
    im.save(path, 'WEBP', quality=Q, method=6)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


im = Image.open(sys.argv[1]).convert('RGB')
assert im.size == (1536, 1024), im.size
wide = im.crop((0, 0, 1536, 858))
for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
    save(wide.resize((w, h), Image.LANCZOS), IMG / f'{NAME}{s}.webp')
mob = im.crop((1536 - 1365, 0, 1536, 1024))
for w, h, s in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
    save(mob.resize((w, h), Image.LANCZOS), IMG / f'{NAME}{s}.webp')
