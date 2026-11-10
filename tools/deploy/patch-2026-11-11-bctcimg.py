#!/usr/bin/env python3
"""Фото плитки «Промпредприятия, БЦ и ТЦ» на странице дератизации (11.11.2026).

Замечание владельца: на плитке стояло фото пищевого производства (img/ind-ready.webp). Новое фото —
технический этаж и паркинг бизнес-центра со станцией контроля грызунов (img/ind-bc-tc.webp, 900×542 и 720×434;
мастер-файл 2752×1536 — в файлах проекта «Страница Промпредприятия, БЦ и ТЦ/Изображения (мастер)»).

    python3 patch-2026-11-11-bctcimg.py <файл страницы дератизации>
Меняется только тег <img> этой плитки. Скрипт идемпотентен.
"""
import sys, pathlib

p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
OLD_ALT = 'alt="Производственное предприятие и инженерные зоны"'
NEW_ALT = 'alt="Технический этаж и паркинг бизнес-центра: кабельные трассы, щитовая и станция контроля грызунов у стены"'
if 'ind-bc-tc.webp' in s:
    print('ALREADY', p); sys.exit(0)
a = s.find(OLD_ALT)
if a < 0 or s.count(OLD_ALT) != 1:
    print('ERROR: плитка не найдена', p); sys.exit(1)
i = s.rfind('<img', 0, a)
j = s.find('>', a) + 1
tag = s[i:j]
if tag.count('ind-ready') != 3:
    print('ERROR: неожиданный тег', tag); sys.exit(1)
new = tag.replace('ind-ready', 'ind-bc-tc').replace(OLD_ALT, NEW_ALT)
p.write_text(s[:i] + new + s[j:], encoding='utf-8')
print('OK', p)
