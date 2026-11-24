#!/usr/bin/env python3
"""Фото первого экрана страниц статей «Пест-контроль по ISO 22000 и FSSC 22000» и «Лицензия на дезинфекцию» из мастер-файлов.

    python3 tools/materialy-stati/make_images.py iso-hero=<мастер.png> lic-hero=<мастер.png>

Мастер-файлы (PNG 2752×1536, Nano Banana Pro, без сжатия) — в файлах проекта SEO, папка seo-agent/visuals/2026-11-24-stati:
    iso-hero-v1-master.png — аудитор и менеджер по качеству у станции контроля грызунов в цехе;
    lic-hero-v1-master.png — менеджер по закупкам сверяет договор, рядом специалист по пест-контролю.
Размеры и кадр для телефона — как в tools/normativnaya-baza/make_images.py (1920×1072, 1440×804, 1024×768, 760×570).
Картинки для соцсетей (img/iso-og.jpg, img/lic-og.jpg) — node tools/materialy-stati/og.mjs.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
LEFT = {'iso-hero': 704, 'lic-hero': 704}  # левая граница кадра 4:3 в мастере
Q = {'iso-hero': 75, 'lic-hero': 75}


def save(im, path, q):
    im.save(path, 'WEBP', quality=q, method=6)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


def main():
    pairs = [a.split('=', 1) for a in sys.argv[1:]]
    if not pairs or any(len(p) != 2 or p[0] not in LEFT for p in pairs):
        sys.exit(__doc__)
    for name, master in pairs:
        im = Image.open(master).convert('RGB')
        assert im.size == (2752, 1536), (master, im.size)
        for w, h, suffix in ((1920, 1072, ''), (1440, 804, '-1440')):
            save(im.resize((w, h), Image.LANCZOS), IMG / f'{name}{suffix}.webp', Q[name])
        x0 = LEFT[name]
        crop = im.crop((x0, 0, x0 + 2048, 1536))
        for w, h, suffix in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
            save(crop.resize((w, h), Image.LANCZOS), IMG / f'{name}{suffix}.webp', Q[name])


if __name__ == '__main__':
    main()
