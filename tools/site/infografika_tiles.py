#!/usr/bin/env python3
"""Иконки инфографики в стиле страницы «Лабораторные исследования» (команда владельца 19.11.2026).

    python3 tools/site/infografika_tiles.py <папка с мастер-файлами <ключ>.png>

Мастер-файлы — PNG 2048×2048 без сжатия: белый матовый предмет с фиолетовыми деталями на чёрном фоне
(Nano Banana Pro). Лежат в файлах проекта «Инфографика в стиле лаборатории/v2 — внедрение/Мастер-файлы 2048».

Фон убирается так же, как в tools/laboratornye-issledovaniya/make_tiles.py: прозрачность пикселя —
его яркость по самому светлому каналу, цвет делится на прозрачность. Затем обрезка по предмету
в квадрат с полем 4% и два размера:

  img/ig-<ключ>-128.webp — до 64 px на экране (×2): строки «Все услуги Центра», «Другие услуги», таблицы;
  img/ig-<ключ>-240.webp — до 120 px (×2): карточки цен, шаги, документы, отрасли, вредители, круг IPM.
Собираются только файлы, на которые ссылаются страницы после tools/site/infografika.py; лишние ig-*.webp убираются.
"""
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'

KEYS = [
    # услуги и этапы работы
    'ipm', 'deratizatsiya', 'dezinsektsiya', 'kompleks', 'dezinfektsiya', 'ventilyatsiya', 'sanaudit',
    'razrabotka-ppk', 'dokumenty-rpn', 'obsledovanie', 'osmotr', 'zashchita', 'dogovor',
    # документы
    'doc-akt', 'doc-otchet', 'doc-personal', 'doc-sgr', 'doc-skhema', 'doc-zhurnal', 'doc-produkciya',
    # отрасли
    'ind-pishchevoe', 'ind-magaziny', 'ind-restorany', 'ind-sklady', 'ind-farma', 'ind-gostinitsy',
    'ind-ofisy', 'ind-medicina', 'ind-shkoly',
    # состав работ по вентиляции
    'vent-vozdukhovody', 'vent-zonty', 'vent-ventilyatory', 'vent-pritochnye', 'vent-reshetki', 'vent-konditsionery',
    # вредители
    'pest-tarakan', 'pest-krysa', 'pest-krysa-chernaya', 'pest-mysh', 'pest-mukha', 'pest-mol', 'pest-klop',
    'pest-golub', 'pest-muravey', 'pest-cheshuynitsa', 'pest-komar', 'pest-tochilshchik',
]
SIZES = (128, 240)
FLOOR = {'ipm': 42}  # у щита слабый отсвет под предметом — срезаем его порогом повыше
FLOOR_DEFAULT = 16   # шум чёрного фона, ниже — полностью прозрачно


def unscreen(im, floor):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    mx = a.max(-1)
    alpha = np.clip((mx - floor) / (255 - floor), 0, 1)
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


def used():
    """Какие файлы нужны страницам: те, на которые ссылается tools/site/infografika.py (лишние не кладём)."""
    sys.path.insert(0, str(ROOT / 'tools/site'))
    import infografika  # noqa: E402
    need = set()
    for rel in infografika.pages():
        f = ROOT / rel
        if f.exists():
            need.update(infografika.used_images(infografika.apply(rel, f.read_text(encoding='utf-8')), rel))
    return need


def main(src):
    need = used()
    for old in IMG.glob('ig-*.webp'):
        if 'img/' + old.name not in need:
            old.unlink()
            print(f'убран лишний {old.relative_to(ROOT)}')
    for key in KEYS:
        sizes = [size for size in SIZES if f'img/ig-{key}-{size}.webp' in need]
        if not sizes:
            continue
        tile = square_crop(unscreen(Image.open(src / f'{key}.png'), FLOOR.get(key, FLOOR_DEFAULT)))
        for size in sizes:
            out = IMG / f'ig-{key}-{size}.webp'
            tile.resize((size, size), Image.LANCZOS).save(out, 'WEBP', quality=80, alpha_quality=70, method=6)
            print(f'ok {out.relative_to(ROOT)} {out.stat().st_size / 1024:.1f} КБ')


if __name__ == '__main__':
    main(pathlib.Path(sys.argv[1]))
