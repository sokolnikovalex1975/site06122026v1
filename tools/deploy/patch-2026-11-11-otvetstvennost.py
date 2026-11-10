#!/usr/bin/env python3
"""Правка 11.11.2026: фото в разделе «Что в программе делает служба пест-контроля, а что — предприятие»
на странице /materialy/programma-pest-kontrolya/.

Владелец 11.11.2026: «тут какая-то огромная картинка стоит в разделе „Что в программе делает служба пест-контроля,
а что — предприятие“ … неправильно, что такое изображение большое висит, и без ничего». Причина: фото обхода КИК у рампы
(класс .p-fig-wide) растягивалось на всю ширину контейнера — 1307×497 px на 1440 px, 1746×665 px на 1920 px (исходник —
1200 px, то есть с растяжением), на телефоне 4:3 — и стояло отдельной полосой между заголовком и списками обязанностей.

Стало: заголовок раздела и фото — одна строка из двух колонок той же сетки, что и карточки обязанностей ниже: фото
слева (над карточкой исполнителя — на нём работа службы пест-контроля), заголовок с подзаголовком справа (над карточкой
предприятия). Фото 16:9 — по высоте вровень с заголовком, без растяжения (колонка уже исходника); на телефоне (до 600 px)
— целиком, 3:2. sizes по фактической ширине колонки (на ноутбуке грузится 720w вместо 1200w). До 860 px — одна колонка:
заголовок, фото, карточки. Тексты, alt, подпись, карточки,
меню, формы и блок счётчиков не меняются.

Использование:
  python3 tools/deploy/patch-2026-11-11-otvetstvennost.py repo <корень репозитория>
      — страница превью (materialy/programma-pest-kontrolya/index.html) и генератор tools/build_programma.py;
  python3 tools/deploy/patch-2026-11-11-otvetstvennost.py live <папка с файлами сайта> <папка пакета>
      — та же правка в index.php, как его отдаёт сайт по HTTPS.

Проверки: правка — точные замены с проверкой числа вхождений; кроме раздела и трёх правил стилей файл не меняется
(сравнение текста без учёта отступов строк раздела); блок счётчиков (Метрика 113675622, UIS, Radist) в файле сайта —
байт в байт прежний; «p-fig-wide» на странице не остаётся.
"""
import pathlib
import re
import sys

COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
PROG = 'materialy/programma-pest-kontrolya/'

SIZES_OLD = 'programma-kik-rampa.webp 1200w" sizes="100vw"'
SIZES_NEW = 'programma-kik-rampa.webp 1200w" sizes="(max-width:860px) calc(100vw - 40px), (max-width:1930px) 45vw, 872px"'

CSS_OLD = ('.p-fig-wide{margin:0 0 24px}\n'
           '.p-fig-wide img{aspect-ratio:21/8;object-position:50% 60%}\n')
# Строка «фото | заголовок» — те же две колонки и тот же зазор 20 px, что у карточек .p-duties: фото стоит ровно над
# карточкой исполнителя, заголовок — над карточкой предприятия; отступ слева у заголовка равен внутреннему полю карточки.
CSS_NEW = ('.p-resp{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-areas:"fig head";'
           'gap:20px;align-items:center;margin-bottom:20px}\n'
           '.p-resp .head{grid-area:head;margin-bottom:0;padding:0 0 0 clamp(24px,2.4vw,36px)}\n'
           '.p-resp-fig{grid-area:fig}\n'
           '.p-resp-fig img{aspect-ratio:16/9;object-position:50% 45%}\n')
MOB_OLD = '  .p-fig-wide img{aspect-ratio:4/3}\n'
MOB_NEW = ('  .p-resp{grid-template-columns:minmax(0,1fr);grid-template-areas:"head" "fig";gap:28px}\n'
           '  .p-resp .head{padding:0}\n')
# На телефоне фото целиком (3:2, без обрезки 16:9) — оно и так во всю ширину экрана
PHONE_OLD = '@media (max-width:600px){.p-obr-btns .btn{width:100%;white-space:normal;text-align:center;line-height:1.25}'
PHONE_NEW = '@media (max-width:600px){.p-resp-fig img{aspect-ratio:3/2}.p-obr-btns .btn{width:100%;white-space:normal;text-align:center;line-height:1.25}'

# Заголовок раздела + фото → обёртка .p-resp (строки раздела сдвигаются на 2 пробела, их текст не меняется)
BLOCK = re.compile(
    r'(<section class="s" id="otvetstvennost">\n  <div class="wrap">\n)'
    r'(    <div class="head">\n.*?\n    </div>\n'
    r'    <figure class="p-fig p-fig-wide"[^>]*>.*?</figure>\n)'
    r'(    <div class="p-duties")', re.S)


def wrap_block(s, what):
    ms = list(BLOCK.finditer(s))
    assert len(ms) == 1, f'{what}: раздел otvetstvennost — найдено {len(ms)}, ожидалось 1'
    m = ms[0]
    inner = m.group(2)
    assert inner.count('<figure') == 1 and inner.count('<h2') == 1, what + ': неожиданная разметка раздела'
    assert inner.count(SIZES_OLD) == 1, what + ': sizes у фото не найден'
    inner = inner.replace(SIZES_OLD, SIZES_NEW).replace('class="p-fig p-fig-wide"', 'class="p-fig p-resp-fig"')
    inner = ''.join('  ' + line if line.strip() else line for line in inner.splitlines(keepends=True))
    new = m.group(1) + '    <div class="p-resp">\n' + inner + '    </div>\n' + m.group(3)
    return s[:m.start()] + new + s[m.end():]


def replace_once(s, old, new, what):
    n = s.count(old)
    assert n == 1, f'{what}: «{old.strip()[:60]}» — найдено {n}, ожидалось 1'
    return s.replace(old, new)


def patch_text(s, what):
    out = wrap_block(s, what)
    out = replace_once(out, CSS_OLD, CSS_NEW, what)
    out = replace_once(out, MOB_OLD, MOB_NEW, what)
    out = replace_once(out, PHONE_OLD, PHONE_NEW, what)
    assert 'p-fig-wide' not in out, what + ': остался p-fig-wide'
    # кроме раздела и стилей ничего не изменилось: сравнение без отступов и без изменённых фрагментов
    def norm(x):
        for a in (CSS_OLD, CSS_NEW, MOB_OLD, MOB_NEW):
            x = x.replace(a, '')
        x = x.replace(PHONE_NEW, PHONE_OLD)
        x = x.replace(SIZES_NEW, SIZES_OLD).replace('class="p-fig p-resp-fig"', 'class="p-fig p-fig-wide"')
        x = x.replace('    <div class="p-resp">\n', '', 1)
        return re.sub(r'^[ ]+', '', x, flags=re.M)
    a, b = norm(s), norm(out)
    # единственное отличие после нормализации — закрывающий </div> обёртки перед .p-duties
    b2 = b.replace('</figure>\n</div>\n<div class="p-duties"', '</figure>\n<div class="p-duties"', 1)
    assert a == b2, what + ': изменилось что-то кроме раздела и стилей'
    return out


def patch_generator(s, what):
    """tools/build_programma.py: те же стили; в MAIN_HTML нет data-* и типографики — своя форма замены."""
    s = replace_once(s, CSS_OLD, CSS_NEW, what)
    s = replace_once(s, MOB_OLD, MOB_NEW, what)
    s = replace_once(s, PHONE_OLD, PHONE_NEW, what)
    gen = re.compile(
        r'(<section class="s" id="otvetstvennost">\n  <div class="wrap">\n)'
        r'(    <div class="head">\n.*?\n    </div>\n    <figure class="p-fig p-fig-wide">.*?</figure>\n)'
        r'(    <div class="p-duties">)', re.S)
    ms = list(gen.finditer(s))
    assert len(ms) == 1, f'{what}: раздел otvetstvennost — найдено {len(ms)}'
    m = ms[0]
    inner = m.group(2)
    assert inner.count(SIZES_OLD) == 1, what + ': sizes у фото не найден'
    inner = inner.replace(SIZES_OLD, SIZES_NEW).replace('class="p-fig p-fig-wide"', 'class="p-fig p-resp-fig"')
    inner = ''.join('  ' + line if line.strip() else line for line in inner.splitlines(keepends=True))
    s = s[:m.start()] + m.group(1) + '    <div class="p-resp">\n' + inner + '    </div>\n' + m.group(3) + s[m.end():]
    assert 'p-fig-wide' not in s, what + ': остался p-fig-wide'
    return s


def patch_file(src, dst, what, counters=False, gen=False):
    before = pathlib.Path(src).read_bytes().decode('utf-8')
    after = patch_generator(before, what) if gen else patch_text(before, what)
    if counters:
        cb, ca = COUNTERS.findall(before), COUNTERS.findall(after)
        assert len(cb) == 1 and cb == ca, what + ': блок счётчиков изменился'
        for k in ('113675622', 'comagic', 'uiscom', 'radist'):
            assert before.count(k) == after.count(k), (what, k)
    assert after.rstrip().endswith('</html>') or gen, what + ': файл обрезан'
    pathlib.Path(dst).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(dst).write_bytes(after.encode('utf-8'))
    print(f'{what}: {len(before.encode())} → {len(after.encode())} байт' + (', счётчики без изменений' if counters else ''))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'repo':
        root = pathlib.Path(sys.argv[2])
        patch_file(root / PROG / 'index.html', root / PROG / 'index.html', PROG + 'index.html')
        patch_file(root / 'tools' / 'build_programma.py', root / 'tools' / 'build_programma.py',
                   'tools/build_programma.py', gen=True)
    elif mode == 'live':
        src, dst = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
        patch_file(src / PROG / 'index.php', dst / PROG / 'index.php', PROG + 'index.php', counters=True)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
