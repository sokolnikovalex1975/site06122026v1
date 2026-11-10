#!/usr/bin/env python3
"""Превью страниц документов (img/*.webp) из текущих PDF сайта — после правки PDF без пересборки (wm_opacity.py).

Каждое превью делается тем же способом, что у его генератора (размер, рендер, качество WEBP):
  pymupdf  — 200 dpi, LANCZOS, WEBP q80 (tools/docs_brand/brand_pdf.py, tools/zhurnal/finalize.py,
             tools/ppk/sample/build_sample.py; акт — высота по пропорции 360 × 509, tools/akt/build_akt.py);
  opros    — 200 dpi без альфа-канала, q82 (tools/razrabotka-ppk/oprosnyy/build_pdf.py);
  poppler  — pdftoppm 200 dpi, у альбомного листа левая часть в пропорции A4, q82
             (tools/ventilyatsiya/docs/build_vent_docs.py);
  top      — верх страницы 16:9 из готового превью, q84 (tools/normativnaya-baza/make_thumbs.py).

    python3 tools/docs_brand/wm_previews.py                 # записать превью в img/
    python3 tools/docs_brand/wm_previews.py --check DIR     # без записи: собрать превью из PDF в DIR (прежние файлы
                                                            # с той же структурой папок) и сравнить с img/ — проверка,
                                                            # что способ сборки совпадает с исходным
"""
import io
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
import pymupdf as fitz
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
IMG = ROOT / 'img'
VENT = 'ochistka-dezinfektsiya-ventilyatsii'
DOK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora'

# (PDF, страница с 1, способ, [(файл превью, ширина)])
SPEC = [
    ('dogovor-deratizatsiya-dezinsektsiya/obrazets-dogovora-pestkontrol-tsentr.pdf', 1, 'pymupdf',
     [('dogovor-sample-p1.webp', 680), ('dogovor-sample-p1-240.webp', 240), ('dogovor-sample-p1-360.webp', 360)]),
    *[('materialy/programma-pest-kontrolya/obrazets-programmy-pest-kontrolya.pdf', p, 'pymupdf',
       [(f'programma-sample-p{p}-{w}.webp', w) for w in (240, 360, 720)]) for p in (1, 3, 5)],
    ('materialy/zhurnal-pest-kontrolya/obrazets-zhurnala-pest-kontrolya.pdf', 1, 'pymupdf',
     [(f'zhurnal-obrazets-p1-{w}.webp', w) for w in (360, 720)]),
    ('materialy/zhurnal-pest-kontrolya/obrazets-zhurnala-pest-kontrolya.pdf', 8, 'pymupdf',
     [(f'zhurnal-obrazets-p8-{w}.webp', w) for w in (360, 720)]),
    ('materialy/zhurnal-pest-kontrolya/obrazets-zhurnala-pest-kontrolya.pdf', 6, 'pymupdf',
     [(f'zhurnal-obrazets-p6-{w}.webp', w) for w in (480, 960)]),
    ('materialy/zhurnal-pest-kontrolya/shablon-zhurnala-pest-kontrolya.pdf', 1, 'pymupdf',
     [(f'zhurnal-shablon-p1-{w}.webp', w) for w in (360, 720)]),
    *[('materialy/programma-proizvodstvennogo-kontrolya-haccp/obrazets-programmy-proizvodstvennogo-kontrolya.pdf', p,
       'pymupdf', [(f'ppk-sample-p{p}-{w}.webp', w) for w in (240, 360, 720)]) for p in (1, 11, 20)],
    (f'{DOK}/obrazets-akta-dezinsektsii-i-deratizatsii.pdf', 1, 'akt',
     [(f'akt-obrazets-p1-{w}.webp', w) for w in (360, 720)]),
    ('razrabotka-ppk/oprosnyy-list-ppk.pdf', 1, 'opros', [(f'oprosnyy-ppk-p1-{w}.webp', w) for w in (240, 360, 720)]),
    ('razrabotka-ppk/oprosnyy-list-ppk-po-haccp.pdf', 1, 'opros',
     [(f'oprosnyy-haccp-p1-{w}.webp', w) for w in (240, 360, 720)]),
    *[(f'{VENT}/{slug}.pdf', 1, 'poppler', [(f'vnt-{slug[4:6]}-p1-{w}.webp', w) for w in (120, 240)]) for slug in (
        'vnt-01-akt-obsledovaniya-ventilyatsii', 'vnt-02-akt-ochistki-ventilyatsii', 'vnt-03-akt-dezinfektsii-ventilyatsii',
        'vnt-04-akt-proverki-ognezaderzhivayushchikh-klapanov', 'vnt-05-akt-otbora-smyvov-ventilyatsii',
        'vnt-06-zhurnal-ochistki-i-dezinfektsii-ventilyatsii', 'vnt-07-zhurnal-rascheta-dezsredstv',
        'vnt-08-prikaz-ob-ochistke-i-dezinfektsii-ventilyatsii', 'vnt-09-opoveshchenie-i-tablichka-ne-vklyuchat')],
    (f'{VENT}/dokumenty-ochistka-dezinfektsiya-ventilyatsii.pdf', 1, 'poppler',
     [(f'vnt-komplekt-p1-{w}.webp', w) for w in (360, 720)]),
    (f'{VENT}/vnt-02-akt-ochistki-ventilyatsii.pdf', 1, 'poppler', [(f'vnt-02-p1-{w}.webp', w) for w in (360, 720)]),
]
# верх страницы 16:9 для карточек /normativnaya-baza/ (make_thumbs.py): из какого превью
TOP = {'programma-sample-p1': 'programma-sample-p1-720.webp', 'zhurnal-obrazets-p1': 'zhurnal-obrazets-p1-720.webp',
       'ppk-sample-p1': 'ppk-sample-p1-720.webp', 'dogovor-sample-p1': 'dogovor-sample-p1.webp'}
QUALITY = {'pymupdf': 80, 'akt': 80, 'opros': 82, 'poppler': 82}


def render(pdf, page, how):
    if how == 'poppler':
        with tempfile.TemporaryDirectory() as t:
            base = pathlib.Path(t) / 'p'
            subprocess.run(['pdftoppm', '-r', '200', '-f', str(page), '-l', str(page), '-png', '-singlefile', str(pdf),
                            str(base)], check=True)
            im = Image.open(str(base) + '.png').convert('RGB')
        if im.width > im.height:
            im = im.crop((0, 0, round(im.height * 210 / 297), im.height))
        return im
    p = fitz.open(pdf)[page - 1]
    if how == 'opros':
        pix = p.get_pixmap(dpi=200, alpha=False)
        return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
    pix = p.get_pixmap(dpi=200)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def build(src_root):
    """{имя файла: (картинка PIL, качество)} из PDF в src_root."""
    out = {}
    for rel, page, how, items in SPEC:
        im = render(src_root / rel, page, how)
        for name, w in items:
            h = round(w * 509 / 360) if how == 'akt' else round(im.height * w / im.width)
            out[name] = (im.resize((w, h), Image.LANCZOS), QUALITY[how])
    for name, src in TOP.items():
        im = Image.open(io.BytesIO(webp(*out[src]))).convert('RGB')  # как make_thumbs.py: из готового файла WEBP
        w = im.width
        top = im.crop((0, 0, w, round(w * 9 / 16)))
        for tw in (480, w):
            out[f'{name}-top-{tw}.webp'] = (top if tw == w else top.resize((tw, round(tw * 9 / 16)), Image.LANCZOS), 84)
    return out


def webp(im, q):
    b = io.BytesIO()
    im.save(b, 'WEBP', quality=q, method=6)
    return b.getvalue()


def main(argv):
    if argv[:1] == ['--check']:
        old = pathlib.Path(argv[1]).resolve()
        worst = 0
        for name, (im, q) in sorted(build(old).items()):
            data = webp(im, q)
            cur = IMG / name
            same = cur.read_bytes() == data
            a = np.asarray(Image.open(cur).convert('RGB'), dtype=np.int16)
            b = np.asarray(Image.open(io.BytesIO(data)).convert('RGB'), dtype=np.int16)
            if a.shape != b.shape:
                print(f'{name}: РАЗМЕР {a.shape} ≠ {b.shape}')
                worst = 99
                continue
            d = np.abs(a - b)
            worst = max(worst, float(d.mean()))
            print(f'{name}: {"байт в байт" if same else f"среднее отличие {d.mean():.3f}, макс. {d.max()}"}')
        print('наибольшее среднее отличие', round(worst, 3))
        return 0
    for name, (im, q) in sorted(build(ROOT).items()):
        p = IMG / name
        before = p.stat().st_size if p.exists() else 0
        p.write_bytes(webp(im, q))
        print(f'{name}: {im.width}×{im.height}, {before} → {p.stat().st_size} байт')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
