#!/usr/bin/env python3
"""Фото первого экрана страниц раздела «Лабораторные исследования» из мастер-файла.

    python3 tools/laboratornye-issledovaniya/make_images.py <мастер.png>                    # главная раздела: img/lab-hero*.webp
    python3 tools/laboratornye-issledovaniya/make_images.py <мастер.png> <имя> [<имя-og>]   # подстраницы и статьи (11.11.2026)

Мастер (PNG 1536×1024, 3:2, без сжатия) — в файлах проекта «Страница Лабораторные исследования/Визуалы v1»
(главная раздела) и «Визуалы — подстраницы» (направления и статьи).
Компьютер — кадр 1536×858 от верхнего края (как 1920×1072 у остальных страниц), телефон — правая часть 4:3.
Картинка для соцсетей (og:image, 1200×630, JPEG) — кадр 1536×806 от верхнего края.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
Q = 80


def save(im, path):
    im.save(path, 'WEBP', quality=Q, method=6)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


def make(master, name, og=None):
    im = Image.open(master).convert('RGB')
    assert im.size == (1536, 1024), im.size
    wide = im.crop((0, 0, 1536, 858))
    for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
        save(wide.resize((w, h), Image.LANCZOS), IMG / f'{name}{s}.webp')
    mob = im.crop((1536 - 1365, 0, 1536, 1024))
    for w, h, s in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
        save(mob.resize((w, h), Image.LANCZOS), IMG / f'{name}{s}.webp')
    if og:
        p = IMG / f'{og}.jpg'
        im.crop((0, 0, 1536, 806)).resize((1200, 630), Image.LANCZOS).save(p, 'JPEG', quality=82, optimize=True, progressive=True)
        print(f'ok {p.relative_to(ROOT)} 1200×630 {p.stat().st_size // 1024} КБ')


if __name__ == '__main__':
    a = sys.argv[1:]
    make(a[0], a[1] if len(a) > 1 else 'lab-hero', a[2] if len(a) > 2 else None)
