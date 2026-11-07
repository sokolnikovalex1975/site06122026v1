#!/usr/bin/env python3
"""Фото первого экрана раздела «Нормативная база» из мастер-файлов.

    python3 tools/normativnaya-baza/make_images.py <мастер хаба.png> <мастер листов.png> [<мастер документов.png>]
    python3 tools/normativnaya-baza/make_images.py dk-hero=<мастер документов.png>   — только одно фото

Мастер-файлы (PNG 2752×1536, без сжатия) хранятся в файлах проекта, папка «Страница Нормативная база/Визуалы v1»:
    nb-hero-v3-master.png — санитарный врач с папкой норм (хаб /normativnaya-baza/);
    pl-hero-v1-master.png — проходим проверочный лист на складе (/normativnaya-baza/proverochnye-listy/);
папка «Страница Документы для Роспотребнадзора/Визуалы v1»:
    dk-hero-v1-master.png — управляющая и специалист сверяют папку документов
                            (/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/, 08.11.2026).

Размеры как у остальных страниц сайта:
    img/<имя>.webp          1920×1072 — компьютер;
    img/<имя>-1440.webp     1440×804;
    img/<имя>-mob.webp      1024×768 — телефон, кадр 4:3 (на телефоне фото стоит между заголовком и текстом);
    img/<имя>-mob-760.webp  760×570.
Кадр для телефона — правая часть мастера: люди и оборудование в ней, левая часть на компьютере уходит под градиент.
Картинки для соцсетей (img/nb-og.jpg, img/pl-og.jpg) собирает tools/normativnaya-baza/og/render.mjs из img/*-hero.webp.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
# (имя, левая граница кадра 4:3 в мастере 2752×1536)
HEROES = [('nb-hero', 704), ('pl-hero', 704), ('dk-hero', 704)]
Q = 80  # как у остальных фото первого экрана (42–97 КБ при 1920 px)


def save(im, path):
    im.save(path, 'WEBP', quality=Q, method=6)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


def main():
    args = sys.argv[1:]
    if not 1 <= len(args) <= len(HEROES):
        sys.exit(__doc__)
    x0s = dict(HEROES)
    if all('=' in a for a in args):  # имя=мастер
        jobs = [(n, x0s[n], m) for n, m in (a.split('=', 1) for a in args)]
    else:  # по порядку HEROES
        jobs = [(n, x0, m) for (n, x0), m in zip(HEROES, args)]
    for name, x0, master in jobs:
        im = Image.open(master).convert('RGB')
        assert im.size == (2752, 1536), (master, im.size)
        for w, h, suffix in ((1920, 1072, ''), (1440, 804, '-1440')):
            save(im.resize((w, h), Image.LANCZOS), IMG / f'{name}{suffix}.webp')
        crop = im.crop((x0, 0, x0 + 2048, 1536))  # 4:3
        for w, h, suffix in ((1024, 768, '-mob'), (760, 570, '-mob-760')):
            save(crop.resize((w, h), Image.LANCZOS), IMG / f'{name}{suffix}.webp')


if __name__ == '__main__':
    main()
