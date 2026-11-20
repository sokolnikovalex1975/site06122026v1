#!/usr/bin/env python3
"""Фото первого экрана страницы «Дезинфекция автотранспорта» (20.11.2026).

    python3 tools/avtotransport/make_images.py <avto-hero-master.png>

Мастер (Nano Banana Pro, 2752×1536, PNG без сжатия) — в файлах проекта: «Страница Дезинфекция автотранспорта/
Изображения (мастер)/avto-hero-master.png». Специалист в кузове рефрижератора виден целиком, без логотипов и госномеров.
Компьютер — кадр целиком 1920×1072 и 1440×804; телефон — 16:9 (1024×576, 760×428), как у страниц дезинсекции
и дезинфекции; соцсети — 1200×630 (сверху срезано больше, чем снизу: ботинки остаются в кадре).
Рамка человека и головы для object-position — tools/site/focal_points.json (avto-hero*.webp).
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


def main(src):
    im = Image.open(src).convert('RGB')
    assert im.size == (2752, 1536), im.size
    for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
        save(im.resize((w, h), Image.LANCZOS), IMG / f'avto-hero{s}.webp', quality=Q, method=6)
    mw = round(1536 * 16 / 9)
    mob = im.crop((2752 - mw, 0, 2752, 1536))
    for w, h, s in ((1024, 576, '-mob'), (760, 428, '-mob-760')):
        save(mob.resize((w, h), Image.LANCZOS), IMG / f'avto-hero{s}.webp', quality=Q, method=6)
    oh = round(2752 * 630 / 1200)
    top = 80
    save(im.crop((0, top, 2752, top + oh)).resize((1200, 630), Image.LANCZOS), IMG / 'avto-og.jpg', 'JPEG',
         quality=82, optimize=True, progressive=True)


if __name__ == '__main__':
    main(sys.argv[1])
