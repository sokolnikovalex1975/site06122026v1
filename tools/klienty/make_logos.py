#!/usr/bin/env python3
"""Логотипы блока «Наши клиенты»: белые одноцветные WebP с прозрачностью для тёмного сайта.

Исходники — tools/klienty/src/*.png (страница клиентов cen-dez.ru, то же юрлицо ООО «Центр дезинфекционных услуг»;
список для сайта владелец подтверждает отдельно). Большинство исходников — 130×130 px, поэтому логотип
вырезается по содержимому, увеличивается в 2–3 раза и получает ровный край (сглаживание альфа-канала).

Режимы перевода в белый (MODE):
  light — тёмный или цветной знак на белом: прозрачность = «сколько краски» (1 − минимальный канал);
  mix   — многоцветный знак: смесь яркости и «краски», чтобы внутри значка остались детали;
  tonal — по яркости (сложные значки с рисунком);
  dark  — светлый знак на тёмной плашке («Щепка»): прозрачность = максимальный канал.

Результат: img/klienty/<имя>.webp (не больше 360×140 px — запас для экранов 2×) и tools/klienty/logos.json
с размерами, по которым tools/site/clients_block.py выравнивает логотипы по «визуальному весу» (площади).

    python3 tools/klienty/make_logos.py
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'tools' / 'klienty' / 'src'
OUT = ROOT / 'img' / 'klienty'
META = ROOT / 'tools' / 'klienty' / 'logos.json'

MODE = {'shchepka': 'dark', 'veer': 'mix', 'brusnichka': 'mix', 'status': 'mix',
        'sotsagroprodukt': 'tonal', 'gerkules': 'tonal'}
LEVELS = {'light': (0.10, 0.80), 'mix': (0.06, 0.75), 'tonal': (0.05, 0.70), 'dark': (0.10, 0.80)}
BOX = (360, 140)


def _smooth(a, lo, hi):
    t = np.clip((a - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def convert(path, mode):
    im = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    rgb = np.asarray(bg.convert('RGB')).astype(np.float32) / 255.0
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    ink = 1.0 - rgb.min(axis=2)
    if mode == 'dark':
        a = rgb.max(axis=2)
    elif mode == 'tonal':
        a = 1.0 - lum
    elif mode == 'mix':
        a = 0.55 * (1.0 - lum) + 0.45 * ink
    else:
        a = ink
    ys, xs = np.where(a > 0.08)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape
    sc = min(BOX[0] / w, BOX[1] / h)
    ow, oh = max(1, round(w * sc)), max(1, round(h * sc))
    A = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'L').resize((ow, oh), Image.LANCZOS)
    if sc > 1:
        A = A.filter(ImageFilter.GaussianBlur(radius=sc * 0.18))
    lo, hi = LEVELS[mode]
    an = _smooth(np.asarray(A).astype(np.float32) / 255.0, lo, hi)
    out = np.zeros((oh, ow, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (an * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA'), (w, h)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for p in sorted(SRC.glob('*.png')):
        slug = p.stem
        mode = MODE.get(slug, 'light')
        im, src = convert(p, mode)
        dst = OUT / f'{slug}.webp'
        im.save(dst, 'WEBP', quality=92, method=6)
        meta[slug] = {'w': im.width, 'h': im.height, 'src': list(src), 'mode': mode, 'bytes': dst.stat().st_size}
        print(f'  {slug:18} {mode:6} {src[0]}×{src[1]} → {im.width}×{im.height}  {dst.stat().st_size} Б')
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'готово: {len(meta)} логотипов в {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
