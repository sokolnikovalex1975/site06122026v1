#!/usr/bin/env python3
"""Превью образцов документов для карточек «Разборы и образцы» на /normativnaya-baza/.

Карточка показывает верх первой страницы в кадре 16:9, поэтому вместо целой страницы A4 (360×509, на телефоне
растягивалась в 2–3 раза) берётся готовая вырезка верха страницы: 480×270 и 720×405 (договор — 680×383,
исходник договора шириной 680). Исходник — те же превью страниц, что на страницах образцов (img/*-720.webp).

    python3 tools/normativnaya-baza/make_thumbs.py
"""
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
IMG = ROOT / 'img'
DOCS = {  # имя превью: исходник
    'programma-sample-p1': 'programma-sample-p1-720.webp',
    'zhurnal-obrazets-p1': 'zhurnal-obrazets-p1-720.webp',
    'ppk-sample-p1': 'ppk-sample-p1-720.webp',
    'dogovor-sample-p1': 'dogovor-sample-p1.webp',
}

for name, src in DOCS.items():
    im = Image.open(IMG / src).convert('RGB')
    w, h = im.size
    top = im.crop((0, 0, w, round(w * 9 / 16)))
    for tw in (480, w):
        out = top if tw == w else top.resize((tw, round(tw * 9 / 16)), Image.LANCZOS)
        p = IMG / f'{name}-top-{tw}.webp'
        out.save(p, 'WEBP', quality=84, method=6)
        print(p.name, out.size, p.stat().st_size // 1024, 'KB')
