#!/usr/bin/env python3
"""Фото первого экрана страниц «Акт дератизации и дезинсекции» и «Схема точек пест-контроля» из мастер-файлов.

    python3 tools/materialy-dokumenty/make_images.py akt-hero=<мастер.png> skhema-hero=<мастер.png>

Мастер-файлы (PNG 2752×1536, Nano Banana Pro, без сжатия) — в файлах проекта, папка «Страницы Акт и Схема точек/Визуалы v1»:
    akt-hero-v2-master.png    — специалист показывает акт обследования менеджеру по качеству в хлебопекарном цехе (с 11.11.2026, v1 заменён);
    skhema-hero-v1-master.png — на складе сверяют станцию контроля грызунов с план-схемой точек.
Размеры и кадр для телефона — как в tools/normativnaya-baza/make_images.py (1920×1072, 1440×804, 1024×768, 760×570).
Картинки для соцсетей (img/akt-og.jpg, img/skhema-og.jpg) — node tools/materialy-dokumenty/og.mjs.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
LEFT = {'akt-hero': 704, 'skhema-hero': 640}  # левая граница кадра 4:3 в мастере
Q = {'akt-hero': 80, 'skhema-hero': 70}  # склад с мешками детальнее — при 80 фото 109 КБ, при 70 — в пределах остальных


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
