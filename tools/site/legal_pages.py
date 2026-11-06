#!/usr/bin/env python3
"""Страницы документов (политика конфиденциальности, согласие) получают шапку, мобильное меню и подвал сайта.

Текст документов не меняется. Стили документа — legal.css (только оформление текста), общие — style.css.
Ссылки меню затем ставит tools/menu/apply_menu.py. Повторный запуск ничего не дублирует.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from unify import VERSION  # noqa: E402

TEMPLATE = 'materialy/index.html'  # та же глубина вложенности (../)
LEGAL = ['privacy/index.html', 'soglasie/index.html']


def grab(s, start_pat, end_tag):
    m = re.search(start_pat, s)
    assert m, start_pat
    e = s.index(end_tag, m.start()) + len(end_tag)
    return s[m.start():e]


def main():
    t = (ROOT / TEMPLATE).read_text(encoding='utf-8')
    header = grab(t, r'<header class="hdr" id="hdr">', '</header>')
    mmenu = grab(t, r'<nav class="mmenu" id="mmenu"', '</nav>')
    footer = grab(t, r'<footer>', '</footer>')
    # на странице документа своей формы нет — кнопки заявки ведут на форму главной
    header = re.sub(r'<a href="#zayavka" class="btn btn-w btn-sm"([^>]*)><span class="btn-t">[^<]*</span></a>',
                    r'<a href="../#zayavka" class="btn btn-w btn-sm"\1><span class="btn-t">Бесплатный аудит</span></a>', header)
    mmenu = re.sub(r'<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">[^<]*</span></a>',
                   '<a href="../#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Заказать бесплатный аудит</span></a>', mmenu)
    for rel in LEGAL:
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        if 'class="hdr"' not in s:
            s = s.replace('<link rel="stylesheet" href="../legal.css', f'<link rel="stylesheet" href="../style.css?v={VERSION}">\n<link rel="stylesheet" href="../legal.css', 1)
            s = re.sub(r'<header class="l-hdr">.*?</header>', lambda m: header + '\n' + mmenu, s, count=1, flags=re.S)
            s = s.replace('<body>\n', '<body class="l-page">\n<a class="skip" href="#main">Перейти к содержанию</a>\n', 1)
            s = s.replace('<main class="wrap">', '<main class="wrap l-main" id="main" tabindex="-1">', 1)
            op = re.search(r'<div class="wrap l-op" id="operator">.*?</div>', s, re.S).group(0)
            ft = footer.replace('\n</footer>', '\n  ' + op + '\n</footer>')
            s = re.sub(r'<footer class="l-ft">.*?</footer>', lambda m: ft, s, count=1, flags=re.S)
            s = s.replace('</body>', f'<script src="../app.min.js?v={VERSION}" defer></script>\n</body>', 1)
        s = re.sub(r'(href="\.\./(?:style|legal)\.css)\?v=[^"]*"', rf'\1?v={VERSION}"', s)
        s = re.sub(r'(src="\.\./app\.min\.js)\?v=[^"]*"', rf'\1?v={VERSION}"', s)
        # текущий документ отмечен в нижней строке подвала
        slug = rel.split('/')[0]
        s = re.sub(r'<div class="fb">.*?</div>', lambda m: m.group(0).replace(f'<a href="../{slug}/">', '<a href="./" aria-current="page">'), s, count=1, flags=re.S)
        f.write_text(s, encoding='utf-8')
        print('ok', rel)


if __name__ == '__main__':
    main()
