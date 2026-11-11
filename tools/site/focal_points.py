#!/usr/bin/env python3
"""Кадрирование фото с людьми по «точке фокуса» — правило владельца с 11.11.2026.

    python3 tools/site/focal_points.py            # правит страницы репозитория
    python3 tools/site/focal_points.py --check    # только проверка, код 1 если страницы не обновлены

Замечание владельца 11.11.2026: на телефоне на странице «Лабораторные исследования» фото первого экрана обрезает
голову человека — «не должно быть такого, что видны какие-то части тела, должен быть виден весь человек».
Причина: высота фото на телефонах зависит от высоты экрана (правило «кнопки на первом экране», hero_fold.py),
а точка кадрирования (object-position) у фото одна на все экраны — на невысоких экранах голова уходит за край.

Что делает скрипт:
  • каждому <img> и <source>, у которого в src/srcset есть файл из tools/site/focal_points.json, ставит
    data-fp="x0 y0 x1 y1 hx0 hy0 hx1 hy1" — рамку людей и рамку голов (доли исходника);
  • вставляет сжатый tools/site/focal.js одной строкой <script id="focal-js"> сразу после первого экрана
    (</section> блока #hero), а на страницах без #hero — перед </body>. Скрипт ставит object-position так,
    чтобы голова всегда была в кадре, а человек — целиком, если помещается.
Рамки в focal_points.json найдены детектором людей (tools/qa/focal/detect_people.py, YOLOv8-pose) и проверены
глазами; новое фото с людьми — добавить в JSON (make_focal_json.py) и пересобрать.

Счётчики и разметку телефона/почты не трогает (ЗАКОН ВЛАДЕЛЬЦА): скрипт ставится до кода Radist, который
build_prod.py добавляет в самый конец <body>. Запускается из build_site.py перед tracking_laws.py; повторный
запуск ничего не меняет.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit', 'preview-services'}
FP = json.loads((ROOT / 'tools/site/focal_points.json').read_text(encoding='utf-8'))
TAG = re.compile(r'<(img|source)\b[^>]*>', re.I)
SCRIPT_RE = re.compile(r'\n?<script id="focal-js">.*?</script>', re.S)


def js():
    src = ROOT / 'tools/site/focal.js'
    out = subprocess.run(['npx', '--yes', 'esbuild@0.24.2', str(src), '--minify', '--target=es2015', '--charset=utf8',
                          '--log-level=warning'], capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        sys.exit('esbuild: ' + out.stderr)
    return '\n<script id="focal-js">' + out.stdout.strip() + '</script>'


def files_of(tag):
    urls = []
    for attr in ('srcset', 'src'):
        m = re.search(r'\s' + attr + r'="([^"]*)"', tag)
        if m:
            urls += [u.strip().split()[0] for u in m.group(1).split(',') if u.strip()]
    return [u.split('?')[0].rsplit('/', 1)[-1] for u in urls]


def fp_attr(name):
    v = FP[name]
    return ' '.join(f'{x:.3f}'.rstrip('0').rstrip('.') if x else '0' for x in v['s'] + v['h'])


def tag_fix(m):
    tag = m.group(0)
    name = next((f for f in files_of(tag) if f in FP), None)
    clean = re.sub(r'\sdata-fp="[^"]*"', '', tag)
    if not name:
        return clean
    end = '/>' if clean.endswith('/>') else '>'
    return clean[: -len(end)].rstrip() + f' data-fp="{fp_attr(name)}"' + end


def hero_end(text):
    m = re.search(r'<section\b[^>]*\bid="hero"[^>]*>', text)
    if not m:
        return None
    pat = re.compile(r'<(/?)section\b[^>]*>', re.I)
    depth, j = 1, m.end()
    while depth:
        mm = pat.search(text, j)
        if not mm:
            return None
        depth += -1 if mm.group(1) else 1
        j = mm.end()
    return j


def fix(text, script):
    new = TAG.sub(tag_fix, text)
    new = SCRIPT_RE.sub('', new)
    if 'data-fp="' in new:
        pos = hero_end(new)
        if pos is None:
            pos = new.rfind('</body>')
        if pos < 0:
            return new
        new = new[:pos] + script + new[pos:]
    return new


def pages():
    for f in sorted(ROOT.rglob('index.html')):
        if not any(p in SKIP for p in f.relative_to(ROOT).parts):
            yield f


def main():
    check = '--check' in sys.argv[1:]
    script = js()
    changed = []
    for f in pages():
        src = f.read_text(encoding='utf-8')
        new = fix(src, script)
        if new != src:
            changed.append(f.relative_to(ROOT))
            if not check:
                f.write_text(new, encoding='utf-8')
    n = sum(1 for f in pages() if 'data-fp="' in f.read_text(encoding='utf-8'))
    print(f'focal_points: {"нужно обновить" if check else "обновлено"} страниц: {len(changed)}; страниц с фото людей: {n}')
    for f in changed:
        print('  ', f)
    if check and changed:
        sys.exit(1)


if __name__ == '__main__':
    main()
