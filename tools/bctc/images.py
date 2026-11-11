#!/usr/bin/env python3
"""Веб-версии фото страницы /biznes-tsentry-torgovye-tsentry-predpriyatiya/ из мастер-файлов (PNG, Nano Banana Pro).

    python3 tools/bctc/images.py <папка с мастер-файлами>

Мастер-файлы не уменьшаются и хранятся в файлах проекта («Страница Промпредприятия, БЦ и ТЦ/Изображения (мастер)»).
"""
import pathlib
import sys

from PIL import Image, ImageEnhance

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/workspace/gen/bctc')
OUT = pathlib.Path(__file__).resolve().parent.parent.parent / 'img'


def grade(im, b=1.0, c=1.0, s=1.0):
    if b != 1.0:
        im = ImageEnhance.Brightness(im).enhance(b)
    if c != 1.0:
        im = ImageEnhance.Contrast(im).enhance(c)
    if s != 1.0:
        im = ImageEnhance.Color(im).enhance(s)
    return im


def fit(im, w, h):
    """Обрезка по центру до пропорции w:h и уменьшение до w×h."""
    W, H = im.size
    r = w / h
    if W / H > r:
        nw = round(H * r)
        x0 = (W - nw) // 2
        im = im.crop((x0, 0, x0 + nw, H))
    else:
        nh = round(W / r)
        y0 = (H - nh) // 2
        im = im.crop((0, y0, W, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)


def save(im, name, q=80):
    p = OUT / name
    if name.endswith('.jpg'):
        im.save(p, 'JPEG', quality=q, optimize=True, progressive=True)
    else:
        im.save(p, 'WEBP', quality=q, method=6)
    print(name, im.size, p.stat().st_size // 1024, 'KB')


# 1. Первый экран: весь кадр для компьютера, для телефона — правая часть кадра со специалистом; картинка для соцсетей
hero = grade(Image.open(SRC / 'bctc-hero.png').convert('RGB'), b=0.94, c=1.04, s=0.92)
save(hero.resize((1920, 1072), Image.LANCZOS), 'bctc-hero.webp', 76)
save(hero.resize((1440, 804), Image.LANCZOS), 'bctc-hero-1440.webp', 76)
W, H = hero.size
cw = round(W * 0.66)
ch = round(cw * 9 / 16)
x0 = W - cw
y0 = min(H - ch, round(H * 0.22))
mob = hero.crop((x0, y0, x0 + cw, y0 + ch))
save(mob.resize((1024, 576), Image.LANCZOS), 'bctc-hero-mob.webp', 76)
save(mob.resize((760, 428), Image.LANCZOS), 'bctc-hero-mob-760.webp', 76)
save(fit(hero.crop((round(W * 0.2), 0, W, H)), 1200, 630), 'bctc-og.jpg', 82)

# 2. Фото блоков: карточки типов объектов и шаги
for name in ['bctc-bc', 'bctc-ofis', 'bctc-tc', 'bctc-zavod', 'bctc-tehnopark', 'bctc-prohodka']:
    im = grade(Image.open(SRC / f'{name}.png').convert('RGB'), b=0.95, c=1.03, s=0.95)
    save(fit(im, 1200, 670), f'{name}.webp', 76)
    save(fit(im, 720, 402), f'{name}-720.webp', 76)

# 3. Фон блока заявки — кадр плитки «Промпредприятия, БЦ и ТЦ» (паркинг и кабельные трассы)
cta = grade(Image.open(SRC / 'ind-bc-tc-master.png').convert('RGB'), b=0.95, c=1.03, s=0.9)
save(fit(cta, 1200, 670), 'bctc-cta.webp', 70)
save(fit(cta, 720, 402), 'bctc-cta-720.webp', 70)

# 4. Подвальный комар — карточка вредителя 240×240, как остальные p-*.webp
save(fit(Image.open(SRC / 'p-mosquito.png').convert('RGB'), 240, 240), 'p-mosquito.webp', 80)
