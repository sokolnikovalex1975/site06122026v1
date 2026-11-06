#!/usr/bin/env python3
"""Веб-версии фото страницы /sklady-i-logistika/ из мастер-файлов (PNG 2752×1536, Nano Banana Pro).

python3 tools/sklady/images.py <папка с мастер-файлами>
Мастер-файлы не уменьшаются и хранятся отдельно (файлы проекта «Страница Склады и логистика/Фото — мастер-файлы»).
"""
import sys, pathlib
from PIL import Image, ImageEnhance

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/workspace/gen')
OUT = pathlib.Path(__file__).resolve().parent.parent.parent / 'img'

def grade(im, b=1.0, c=1.0, s=1.0):
    if b != 1.0: im = ImageEnhance.Brightness(im).enhance(b)
    if c != 1.0: im = ImageEnhance.Contrast(im).enhance(c)
    if s != 1.0: im = ImageEnhance.Color(im).enhance(s)
    return im

def fit(im, w, h):
    """Обрезка по центру до пропорции w:h и уменьшение до w×h."""
    W, H = im.size
    r = w / h
    if W / H > r:
        nw = round(H * r); x0 = (W - nw) // 2; im = im.crop((x0, 0, x0 + nw, H))
    else:
        nh = round(W / r); y0 = (H - nh) // 2; im = im.crop((0, y0, W, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)

def save(im, name, q=80):
    p = OUT / name
    if name.endswith('.jpg'):
        im.save(p, 'JPEG', quality=q, optimize=True, progressive=True)
    else:
        im.save(p, 'WEBP', quality=q, method=6)
    print(name, im.size, p.stat().st_size // 1024, 'KB')

# 1. Hero: весь кадр для десктопа (затемнение под стиль тёмных Hero сайта), отдельный кадр для телефона
hero = grade(Image.open(SRC / 'sklad-hero.png').convert('RGB'), b=0.84, c=1.06, s=0.9)
save(hero.resize((1920, 1072), Image.LANCZOS), 'sklad-hero.webp', 78)
save(hero.resize((1440, 804), Image.LANCZOS), 'sklad-hero-1440.webp', 78)
W, H = hero.size
cw = round(W * 0.70); ch = round(cw * 9 / 16)
cx = round(W * 0.62); x0 = max(0, min(W - cw, cx - cw // 2)); y0 = min(H - ch, round(H * 0.15))
mob = hero.crop((x0, y0, x0 + cw, y0 + ch))
save(mob.resize((1024, 576), Image.LANCZOS), 'sklad-hero-mob.webp', 78)
save(mob.resize((760, 428), Image.LANCZOS), 'sklad-hero-mob-760.webp', 78)
og = fit(hero, 1200, 630)
save(og, 'sklady-og.jpg', 82)

# 2. Фото блоков (карточки 16:9 и шаги регламента)
for name in ['sklad-vorota', 'sklad-holod', 'sklad-fulfilment', 'sklad-produkty', 'sklad-rampa', 'sklad-feromon', 'sklad-farma']:
    im = grade(Image.open(SRC / f'{name}.png').convert('RGB'), b=0.95, c=1.03, s=0.95)
    save(fit(im, 1200, 670), f'{name}.webp', 78)
    save(fit(im, 720, 402), f'{name}-720.webp', 78)
