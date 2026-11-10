#!/usr/bin/env python3
"""Фото первого экрана и картинка для соцсетей страницы «Дератизация и дезинсекция для организаций».

    python3 tools/deratizatsiya-i-dezinsektsiya/make_images.py <dd-hero-v1-master.png>

Мастер (PNG 2752×1536, 16:9, без сжатия) — в файлах проекта «Страница Дератизация и дезинсекция/Визуалы v1».
Компьютер — кадр целиком (1920×1072, как у остальных страниц), телефон — правая часть 4:3 (специалист, станция,
ловушка для насекомых и УФ-ловушка в кадре), соцсети — 1200×630 по центру.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
NAME = 'dd-hero'
Q = 80


def save(im, path, fmt='WEBP', **kw):
    im.save(path, fmt, **kw)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


im = Image.open(sys.argv[1]).convert('RGB')
assert im.size == (2752, 1536), im.size
for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
    save(im.resize((w, h), Image.LANCZOS), IMG / f'{NAME}{s}.webp', quality=Q, method=6)
mob = im.crop((2752 - 2048, 0, 2752, 1536))
for w, h, s in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
    save(mob.resize((w, h), Image.LANCZOS), IMG / f'{NAME}{s}.webp', quality=Q, method=6)
oh = round(2752 * 630 / 1200)
top = (1536 - oh) // 2
save(im.crop((0, top, 2752, top + oh)).resize((1200, 630), Image.LANCZOS), IMG / 'dd-og.jpg', 'JPEG', quality=82,
     optimize=True, progressive=True)
