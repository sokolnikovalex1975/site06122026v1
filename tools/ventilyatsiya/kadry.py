#!/usr/bin/env python3
"""Кадры блока «Что видит камера в коробе» (страница вентиляции): до работ → после очистки → после дезинфекции.

    python3 tools/ventilyatsiya/kadry.py /путь/к/мастерам

Мастер-файлы 2752×1536 (PNG, сгенерированы 13.11.2026, Nano Banana Pro): kadr-1-do-rabot.png,
kadr-2-posle-ochistki.png, kadr-3-chisto-base.png. Один и тот же участок короба: чистый кадр — основа,
«до работ» и «после очистки» получены правкой основы, поэтому фланцы и заклёпки совпадают (сдвиг ≤ 2 px на 2752).

На каждый кадр в правый верхний угол наносится метка «ИЛЛЮСТРАЦИЯ» — кадры не съёмка конкретного объекта
и не должны выдаваться за неё (то же сказано в подписи блока). Нарезка: 1440, 1080 и 720 px по ширине, WebP.
"""
import io
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
FONT = '/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf'
FRAMES = [  # мастер → имя на сайте
    ('kadr-1-do-rabot.png', 'vent-kadr-1-do'),
    ('kadr-2-posle-ochistki.png', 'vent-kadr-2-ochistka'),
    ('kadr-3-chisto-base.png', 'vent-kadr-3-dezinfektsiya'),
]
SIZES = [(1440, ''), (1080, '-1080'), (720, '-720')]
LIMIT = {1440: 100_000, 1080: 64_000, 720: 34_000}  # байт: больше — снижаем качество
MARK = 'ИЛЛЮСТРАЦИЯ'
# положение метки в долях кадра (x0, y0, x1, y1) — его же знает скрипт страницы, чтобы пыль и туман не ложились на метку
MARK_BOX = None


def stamp(im):
    """Метка «ИЛЛЮСТРАЦИЯ»: светлый текст на тёмной полупрозрачной плашке, правый верхний угол."""
    global MARK_BOX
    W, H = im.size
    k = W / 2752
    font = ImageFont.truetype(FONT, round(31 * k))
    track = 4.2 * k  # разрядка
    widths = [font.getlength(ch) for ch in MARK]
    tw = sum(widths) + track * (len(MARK) - 1)
    asc, desc = font.getmetrics()
    ph, px = round(60 * k), round(26 * k)
    x1, y0 = W - round(118 * k), round(74 * k)
    x0 = x1 - round(tw) - 2 * px
    y1 = y0 + ph
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x1, y1), radius=ph // 2, fill=(8, 9, 12, 150), outline=(255, 255, 255, 46), width=max(1, round(2 * k)))
    x = x0 + px
    ty = y0 + (ph - (asc + desc)) / 2 + round(1 * k)
    for ch, w in zip(MARK, widths):
        d.text((x, ty), ch, font=font, fill=(255, 255, 255, 228))
        x += w + track
    MARK_BOX = (x0 / W, y0 / H, x1 / W, y1 / H)
    return Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')


def save_webp(im, path, limit):
    best = None
    for q in range(80, 49, -3):
        b = io.BytesIO()
        im.save(b, 'WEBP', quality=q, method=6)
        best = (q, b.getvalue())
        if len(best[1]) <= limit:
            break
    path.write_bytes(best[1])
    return best[0], len(best[1])


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/workspace/vent-kamera/masters')
    for master, name in FRAMES:
        m = Image.open(src / master).convert('RGB')
        assert m.size == (2752, 1536), (master, m.size)
        for w, suf in SIZES:
            h = round(w * 1536 / 2752)
            im = stamp(m.resize((w, h), Image.LANCZOS))
            q, n = save_webp(im, IMG / f'{name}{suf}.webp', LIMIT[w])
            print(f'{name}{suf}.webp', (w, h), 'q', q, n, 'байт')
    print('метка, доли кадра:', tuple(round(v, 4) for v in MARK_BOX))


if __name__ == '__main__':
    main()
