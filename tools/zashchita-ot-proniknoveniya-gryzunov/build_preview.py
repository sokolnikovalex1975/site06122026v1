#!/usr/bin/env python3
"""Безопасная копия новой страницы для уже существующего вложенного превью.

Основной результат находится в корне сайта на GitHub Pages. Эта копия нужна
для перехода из прикреплённого приложения preview-services в пределах одного
просмотра. Ни рабочие счётчики, ни отправка заявки сюда не переносятся.
"""
import pathlib
import re
import shutil
from urllib.parse import urljoin

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'preview-services'
SLUG = 'zashchita-ot-proniknoveniya-gryzunov'
GITHUB = 'https://sokolnikovalex1975.github.io/site06122026v1/'


def build():
    src = (ROOT / SLUG / 'index.html').read_text(encoding='utf-8')
    s = src.replace('<html lang="ru">', '<html lang="ru" class="anim-fail anim-ready no-intro">', 1)
    s, n = re.subn(r'<script>\s*/\* начальные состояния анимаций.*?</script>\s*', '', s, count=1, flags=re.S)
    assert n == 1
    s, n = re.subn(r'<script>\s*/\* скрипты анимаций.*?</script>',
                   '<script src="../interactions.js" defer></script>\n<script src="preview.js" defer></script>',
                   s, count=1, flags=re.S)
    assert n == 1
    # Локальный скрипт темы и самопроверки оставляем, но заглушка fetch здесь не нужна.
    s, n = re.subn(r'/\* На GitHub Pages.*?(?=/\* Самопроверка)', '', s, count=1, flags=re.S)
    assert n == 1

    def link(match):
        tag = match.group(0)
        value = re.search(r'href="([^"]*)"', tag)
        if not value:
            return tag
        href = value.group(1)
        if href and not re.match(r'^(#|https?:|tel:|mailto:|data:)', href):
            dest = urljoin(GITHUB + SLUG + '/', href)
            if dest == GITHUB:
                dest = '../'
            tag = tag.replace('href="' + href + '"', 'href="' + dest + '"')
        return tag
    s = re.sub(r'<a\b[^>]*>', link, s)
    s = s.replace('<div class="fbody">', '<div class="fbody"><fieldset data-proof-fields disabled style="border:0;padding:0;margin:0;min-width:0"><legend class="sr-only">Тестовая заявка</legend>', 1)
    s = s.replace('Заполнение займёт меньше минуты', 'Тестовая форма: данные не отправляются и не сохраняются', 1)
    s, n = re.subn(r'(\s*</div>\s*)(<div class="ok" role="status")',
                   r'</fieldset>\1\2', s, count=1)
    assert n == 1
    s = s.replace('<h3>Заявка отправлена</h3>', '<h3>Проверка заполнения завершена</h3>', 1)
    s = s.replace('Перезвоним в\u00a0ближайшее рабочее время, чтобы уточнить задачу и\u00a0согласовать обследование объекта.',
                  'Это тестовая версия. Заявка никуда не отправлена, данные не сохранены.', 1)
    dest = OUT / SLUG
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'index.html').write_text(s, encoding='utf-8')
    shutil.copy2(ROOT / 'tools' / SLUG / 'preview.js', dest / 'preview.js')
    shutil.copy2(ROOT / 'style.css', OUT / 'style.css')
    paths = set(re.findall(r'(?:img|fonts)/[A-Za-z0-9_.-]+\.(?:webp|woff2)', s + (ROOT / 'style.css').read_text()))
    for path in paths:
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, target)
    assert not any(x in s for x in ['sessionStorage', 'localStorage', 'mc.yandex.ru', 'app.uiscom.ru/static/', 'track.radist.me'])
    assert not re.search(r'<script[^>]+src="[^"]*app\.min\.js', s)
    assert src == (ROOT / SLUG / 'index.html').read_text(encoding='utf-8')
    print('preview-services:', SLUG, '; ресурсов', len(paths))


if __name__ == '__main__':
    build()
