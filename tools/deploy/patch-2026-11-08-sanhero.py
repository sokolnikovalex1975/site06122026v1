#!/usr/bin/env python3
"""Выкладка 08.11.2026 (санитарный аудит, первый экран): правка страницы в том виде, как её отдаёт сайт.

Использование:
  python3 tools/deploy/patch-2026-11-08-sanhero.py <папка с файлами сайта> <папка результата> [MANIFEST]

<папка с файлами сайта> — sanitarnyy-audit/index.php, как его отдаёт сайт по HTTPS перед выкладкой
(на 08.11.2026 — файл выкладки «Документы для Роспотребнадзора» ~22:00 МСК со ссылками в меню и подвале,
sha256 8ec7a3e9… = MANIFEST-2026-11-08-dokumenty). В <папку результата> пишется новый sanitarnyy-audit/index.php.

  * Из сравнения сборки «BASE → EDIT» (sanitarnyy-audit/index.html) переносятся все правки: стили первого экрана
    в конце стилей страницы и разметка секции #hero (фото внутри .hero-copy, плашка с «МО» для телефона, части описания
    в span.lead-x, лицензия и три пункта — в .sa-hero-more). Каждый фрагмент правки расширяется соседним текстом, пока
    не станет единственным в файле с сайта. Меню, подвал и остальные блоки страницы не трогаются;
  * проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) байт в байт прежний; набор ссылок (href)
    и номеров телефона не изменился; текст описания без тегов прежний.
"""
import difflib
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE, EDIT = 'ce1b75a', '04c5d92'
PAGE = 'sanitarnyy-audit/index.php'
PAGE_SRC = 'sanitarnyy-audit/index.html'
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
HREFS = re.compile(r'href="([^"]+)"')
TELS = re.compile(r'tel:\+?\d+')
LEAD = re.compile(r'<p class="lead"[^>]*>(.*?)</p>', re.S)


def tok(s):
    return re.split(r'(?<=>)|(?<=\n)|(?<=\})|(?<=;)', s)


def git_show(commit, path):
    if commit == 'WORKTREE':
        return (ROOT / path).read_text(encoding='utf-8')
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout.decode('utf-8')


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


def plain(s):
    return re.sub(r'<[^>]+>', '', s)


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
    old = (src / PAGE).read_text(encoding='utf-8')
    new, n = port(git_show(BASE, PAGE_SRC), git_show(EDIT, PAGE_SRC), old, f'{BASE}→{EDIT}')
    a, b = COUNTERS.findall(old), COUNTERS.findall(new)
    if len(a) != 1 or a != b:
        raise SystemExit('блок счётчиков изменён или не найден')
    if HREFS.findall(old) != HREFS.findall(new):
        raise SystemExit('изменился список ссылок')
    if TELS.findall(old) != TELS.findall(new):
        raise SystemExit('изменились телефонные ссылки')
    la, lb = LEAD.findall(old), LEAD.findall(new)
    if len(la) != 1 or len(lb) != 1 or plain(la[0]) != plain(lb[0]):
        raise SystemExit('изменился текст описания первого экрана')
    if new.count('<section class="hero f-hero" id="hero">') != 1 or new.count('class="sa-hero-more"') != 1:
        raise SystemExit('первый экран не найден после правки')
    data = new.encode('utf-8')
    out = dst / PAGE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    h = hashlib.sha256(data).hexdigest()
    mark = ''
    if manifest:
        ok = manifest.get(PAGE) == h
        mark = ' MANIFEST ' + ('совпадает' if ok else 'НЕ СОВПАДАЕТ')
        if not ok or set(manifest) != {PAGE}:
            raise SystemExit(f'расхождение с MANIFEST: {h}')
    print(f'{PAGE:40s} {n} фрагм., {len(data)} байт, sha256 {h}{mark}')


if __name__ == '__main__':
    main()
