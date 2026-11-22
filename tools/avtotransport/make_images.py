#!/usr/bin/env python3
"""Фото первого экрана страницы «Дезинфекция автотранспорта» (20.11.2026, фото — вариант 6 от 22.11.2026).

    python3 tools/avtotransport/make_images.py <avto-hero-master.png>

Мастер (Nano Banana Pro, 2752×1536, PNG без сжатия) — в файлах проекта: «Страница Дезинфекция автотранспорта/
Изображения (мастер)/avto-hero-master-v6.png» (22.11.2026, вариант 6): рефрижератор на три четверти сзади — видны
кабина, левый борт с колёсами, задний торец с распахнутыми створками (левая откинута к борту внутренней стороной),
фонари по нижним углам; специалист стоит в кузове справа и обрабатывает правую стенку; виден целиком, без логотипов
и госномеров. Исходный кадр уменьшен до 85% и сдвинут (+518 px вправо, +230 px вниз), поля слева и сверху дорисованы
Nano Banana Pro как продолжение двора, склада и неба, машина и человек — пиксели исходного кадра: на компьютере человек
правее градиента и ниже верхнего затемнения, на телефоне в кадре вся машина.
Компьютер — кадр целиком 1920×1072 и 1440×804; телефон — 16:9 (1024×576, 760×428), как у страниц дезинсекции
и дезинфекции; соцсети — 1200×630 (сверху срезано больше, чем снизу: ботинки остаются в кадре).
Рамка человека и головы для object-position — tools/site/focal_points.json (avto-hero*.webp).
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
IMG = ROOT / 'img'
Q = 86  # фото первого экрана: без ступенек на небе и полос сжатия
MOB = (0.1991, 0.1836)  # телефон: левый край и верх кадра (доли мастера), ширина — до правого края, 16:9
OG = (452, 280)  # соцсети: левый край и верх в px мастера, вся машина


def save(im, path, fmt='WEBP', **kw):
    im.save(path, fmt, **kw)
    print(f'ok {path.relative_to(ROOT)} {im.width}×{im.height} {path.stat().st_size // 1024} КБ')


def main(src):
    im = Image.open(src).convert('RGB')
    assert im.size == (2752, 1536), im.size
    for w, h, s in ((1920, 1072, ''), (1440, 804, '-1440')):
        save(im.resize((w, h), Image.LANCZOS), IMG / f'avto-hero{s}.webp', quality=Q, method=6)
    # телефон: вся машина — кабина, борт, колёса, открытый задний торец и человек целиком
    mx, my = MOB
    mw = 2752 - round(mx * 2752)
    mh = round(mw * 9 / 16)
    y0 = round(my * 1536)
    mob = im.crop((2752 - mw, y0, 2752, y0 + mh))
    for w, h, s in ((1024, 576, '-mob'), (760, 428, '-mob-760')):
        save(mob.resize((w, h), Image.LANCZOS), IMG / f'avto-hero{s}.webp', quality=Q, method=6)
    ox, oy = OG
    ow = 2752 - ox
    oh = round(ow * 630 / 1200)
    save(im.crop((ox, oy, 2752, oy + oh)).resize((1200, 630), Image.LANCZOS), IMG / 'avto-og.jpg', 'JPEG',
         quality=82, optimize=True, progressive=True)


if __name__ == '__main__':
    main(sys.argv[1])
