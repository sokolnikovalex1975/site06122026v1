#!/usr/bin/env python3
"""Реквизиты в подвале: покрытие, идемпотентность и сохранение прежнего HTML."""
import importlib.util
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('menu', ROOT / 'tools/menu/apply_menu.py')
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)


def strip_block(s):
    s = re.sub(r'<style id="ft-company-st">.*?</style>\n', '', s, flags=re.S)
    return re.sub(r'  <div class="wrap ft-company" id="requisites">.*?</div>\n', '', s, flags=re.S)


for rel, _, _ in menu.PAGES + menu.LEGAL:
    current = (ROOT / rel).read_text(encoding='utf-8')
    assert current.count('id="requisites"') == 1, rel
    assert current.count('id="ft-company-st"') == 1, rel
    assert menu.company_footer(current) == current, f'{rel}: неидемпотентно'
    assert menu.COMPANY_BLOCK in current, rel
    footer = re.search(r'<footer>.*?</footer>', current, re.S).group()
    assert 'id="requisites"' in footer, rel
    original = subprocess.check_output(
        ['git', 'show', f'8815806:{rel}'], cwd=ROOT
    ).decode('utf-8')
    assert strip_block(current) == original, f'{rel}: изменена посторонняя разметка'

print(f'OK: {len(menu.PAGES + menu.LEGAL)} страниц, идемпотентность, прежний HTML без изменений.')
