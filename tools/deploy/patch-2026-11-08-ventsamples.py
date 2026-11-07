#!/usr/bin/env python3
"""Выкладка 08.11.2026 (вентиляция, образцы заполнения): правка страницы в том виде, как её отдаёт сайт.

Использование:
  python3 tools/deploy/patch-2026-11-08-ventsamples.py <папка с файлами сайта> <папка результата> [MANIFEST]

<папка с файлами сайта> — ochistka-dezinfektsiya-ventilyatsii/index.php, как его отдаёт сайт по HTTPS перед выкладкой
(на 08.11.2026 — файл выкладки 01:05 МСК, sha256 c1bfd1dd…). В <папку результата> пишутся все файлы пакета:
страница и 10 новых PDF (9 образцов заполнения ВНТ-01…ВНТ-09 и все вместе) — из коммита EDIT.

  * Страница: из сравнения сборки «BASE → EDIT» (ochistka-dezinfektsiya-ventilyatsii/index.html) переносятся все правки —
    стили строк раздела документов, подзаголовок раздела, метки «Бланк · N стр.» и ссылки «Образец заполнения», кнопка
    «Образцы заполнения, PDF», ответ в вопросах и в разметке FAQPage. Каждый фрагмент правки расширяется соседним текстом,
    пока не станет единственным в файле с сайта. Меню и подвал сайта не трогаются;
  * проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) байт в байт прежний; ни одна ссылка не пропала,
    новые ссылки — только 10 PDF образцов.
"""
import difflib
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE, EDIT = '52fa5a9', '780e455'
VENT = 'ochistka-dezinfektsiya-ventilyatsii/index.php'
VENT_SRC = 'ochistka-dezinfektsiya-ventilyatsii/index.html'
PDFS = [
    'obraztsy-zapolneniya-dokumentov-ventilyatsii.pdf',
    'vnt-01-akt-obsledovaniya-ventilyatsii-obrazets.pdf', 'vnt-02-akt-ochistki-ventilyatsii-obrazets.pdf',
    'vnt-03-akt-dezinfektsii-ventilyatsii-obrazets.pdf', 'vnt-04-akt-proverki-ognezaderzhivayushchikh-klapanov-obrazets.pdf',
    'vnt-05-akt-otbora-smyvov-ventilyatsii-obrazets.pdf', 'vnt-06-zhurnal-ochistki-i-dezinfektsii-ventilyatsii-obrazets.pdf',
    'vnt-07-zhurnal-rascheta-dezsredstv-obrazets.pdf', 'vnt-08-prikaz-ob-ochistke-i-dezinfektsii-ventilyatsii-obrazets.pdf',
    'vnt-09-opoveshchenie-i-tablichka-ne-vklyuchat-obrazets.pdf',
]
IMGS = []
NEW = IMGS + ['ochistka-dezinfektsiya-ventilyatsii/' + p for p in PDFS]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
HREFS = re.compile(r'href="([^"]+)"')


def tok(s):
    return re.split(r'(?<=>)|(?<=\n)|(?<=\})|(?<=;)', s)


def git_show(commit, path, binary=False):
    out = subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout
    return out if binary else out.decode('utf-8')


def port(prev, new, target, label, ctx=4, gap=8):
    A, B = tok(prev), tok(new)
    ops = [o for o in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes() if o[0] != 'equal']
    if not ops:
        raise SystemExit(f'[{label}] нет правок для переноса')
    chunks = []
    for _, i1, i2, j1, j2 in ops:
        if chunks and i1 - chunks[-1][1] <= gap and A[chunks[-1][1]:i1] == B[chunks[-1][3]:j1]:
            chunks[-1] = (chunks[-1][0], i2, chunks[-1][2], j2)
        else:
            chunks.append((i1, i2, j1, j2))
    out = target
    for i1, i2, j1, j2 in chunks:
        k = ctx
        while True:
            left, right = ''.join(A[max(0, i1 - k):i1]), ''.join(A[i2:i2 + k])
            old = left + ''.join(A[i1:i2]) + right
            n = out.count(old)
            if n == 1:
                break
            if n == 0:
                raise SystemExit(f'[{label}] фрагмент не найден в файле с сайта: {old[:300]!r}')
            k += 2
            if k > 60:
                raise SystemExit(f'[{label}] фрагмент не однозначен: {old[:300]!r}')
        out = out.replace(old, left + ''.join(B[j1:j2]) + right, 1)
    return out, len(chunks)


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    manifest = {}
    if len(sys.argv) == 4:
        for line in pathlib.Path(sys.argv[3]).read_text(encoding='utf-8').splitlines():
            if line.strip():
                h, f = line.split()
                manifest[f] = h
    old = (src / VENT).read_text(encoding='utf-8')
    new, n = port(git_show(BASE, VENT_SRC), git_show(EDIT, VENT_SRC), old, f'{BASE}→{EDIT}')
    a, b = COUNTERS.findall(old), COUNTERS.findall(new)
    if len(a) != 1 or a != b:
        raise SystemExit('блок счётчиков изменён или не найден')
    ha, hb = set(HREFS.findall(old)), set(HREFS.findall(new))
    if ha - hb:
        raise SystemExit(f'пропали ссылки: {sorted(ha - hb)}')
    if hb - ha != set(PDFS):
        raise SystemExit(f'неожиданные новые ссылки: {sorted((hb - ha) ^ set(PDFS))}')
    files = {VENT: new.encode('utf-8')}
    for rel in NEW:
        files[rel] = git_show(EDIT, rel, binary=True)
    bad = 0
    for rel in sorted(files):
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(files[rel])
        h = hashlib.sha256(files[rel]).hexdigest()
        mark = ''
        if manifest:
            ok = manifest.get(rel) == h
            bad += not ok
            mark = ' MANIFEST ' + ('совпадает' if ok else 'НЕ СОВПАДАЕТ')
        info = f'{n} фрагм.' if rel == VENT else f'{len(files[rel])} байт'
        print(f'{rel:78s} {info}{mark}')
    if manifest and (bad or set(manifest) != set(files)):
        raise SystemExit(f'расхождений с MANIFEST: {bad}; файлов в MANIFEST {len(manifest)}, в результате {len(files)}')
    print(f'готово: {len(files)} файлов в {dst}')


if __name__ == '__main__':
    main()
