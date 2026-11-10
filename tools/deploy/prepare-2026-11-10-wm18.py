#!/usr/bin/env python3
"""Выкладка 10.11.2026: водяной знак 18 % (было 12 %) на всех документах сайта и превью их страниц.

    python3 tools/deploy/prepare-2026-11-10-wm18.py <папка с файлами сайта> <папка пакета pkg> [MANIFEST]

<папка с файлами сайта> — PDF и img/*.webp из списка ниже, как их отдаёт сайт по HTTPS перед выкладкой
(структура папок как на сайте). Пакет — файлы из рабочей копии: PDF — после tools/docs_brand/wm_opacity.py 0.18,
превью — tools/docs_brand/wm_previews.py. Страницы (index.php), счётчики, поиск и прочие файлы не меняются.

Проверки:
- каждый PDF пакета отличается от файла с сайта только прозрачностью знака: wm_opacity.verify — страницы, текст и его
  прозрачность, метаданные (кроме даты изменения), картинки, порядок рисования, все рисунки кроме знака, растр вне знака;
  знак 0.18 и поверх содержимого на всех страницах;
- превью — тех же размеров, что на сайте;
- чек-лист «Документы для Роспотребнадзора» в пакет не входит: на сайте он уже с 18 % (в main — невыложенная версия).
EXPECTED_BEFORE.txt — суммы файлов с сайта (run_all.sh сверяет их перед загрузкой), MANIFEST.sha256 — суммы пакета.
"""
import hashlib
import pathlib
import shutil
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'docs_brand'))
import wm_opacity  # noqa: E402
import wm_previews  # noqa: E402

PDFS = sorted({rel for rel, *_ in wm_previews.SPEC} | {
    'materialy/programma-pest-kontrolya/shablon-programmy-pest-kontrolya.pdf',
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/blank-akta-dezinsektsii-i-deratizatsii.pdf',
    *[f'ochistka-dezinfektsiya-ventilyatsii/{p.name}' for p in (ROOT / 'ochistka-dezinfektsiya-ventilyatsii').glob('*.pdf')],
})
IMGS = sorted([f'img/{n}' for _, _, _, items in wm_previews.SPEC for n, _ in items]
              + [f'img/{k}-top-{t}.webp' for k in wm_previews.TOP for t in (480, 680 if k == 'dogovor-sample-p1' else 720)])
FILES = PDFS + IMGS


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    assert len(PDFS) == 30 and len(IMGS) == 67, (len(PDFS), len(IMGS))
    assert not any('chek-list' in f for f in FILES)
    if pkg.exists():
        shutil.rmtree(pkg)
    for f in FILES:
        src, dst = ROOT / f, pkg / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if f.endswith('.pdf'):
            wm_opacity.verify(live / f, dst, 0.18)
        else:
            a, b = Image.open(live / f), Image.open(dst)
            assert a.size == b.size and b.format == 'WEBP', f'{f}: {a.size} → {b.size}'
    man = ''.join(f'{sha(pkg / f)}  {f}\n' for f in FILES)
    exp = ''.join(f'{sha(live / f)}  {f}\n' for f in FILES)
    same = [f for f in FILES if sha(pkg / f) == sha(live / f)]
    assert not same, f'файлы не изменились: {same}'
    if len(sys.argv) == 4:
        if pathlib.Path(sys.argv[3]).read_text(encoding='utf-8') != man:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (pkg.parent / 'MANIFEST.sha256').write_text(man, encoding='utf-8')
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    size = sum((pkg / f).stat().st_size for f in FILES)
    print(f'пакет: {len(PDFS)} PDF и {len(IMGS)} превью, {size} байт; PDF отличаются от сайта только прозрачностью знака')


if __name__ == '__main__':
    main()
