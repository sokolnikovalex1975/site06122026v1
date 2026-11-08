#!/usr/bin/env python3
"""Выкладка 08.11.2026 (доделка выкладки «Документы для Роспотребнадзора»): меню и подвал как в GitHub + картинка для соцсетей.

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-08-menufix.py <папка с файлами сайта> <папка пакета> [MANIFEST]

<папка с файлами сайта> — страницы, как их отдаёт сайт по HTTPS перед выкладкой (`<путь>/index.php`).

Что было не так после выкладки ~22:00 МСК (tools/deploy/prepare-2026-11-08-dokumenty.py вставлял ссылку в конец списков):
  * на 23 страницах пункт «Документы для Роспотребнадзора» стоит последним в «Услугах» — ниже итоговой ссылки
    «Пест-контроль по системе IPM» и без стрелки, в меню «Материалы» (компьютер и телефон) его нет, в подвале — в конце
    колонок; на самой странице документов и в GitHub — после «Разработки ППК» и после «Нормативной базы»;
  * картинки для соцсетей страницы документов img/dok-og.jpg на сайте нет (404) — выкладывались только dok-*.webp.

Что делает: в каждой странице сайта заменяет три блока — <header>, мобильное меню <nav class="mmenu"> и <footer> —
теми же блоками из сборки для Timeweb (dist/timeweb, = GitHub). Проверки на каждой странице:
  * вне этих трёх блоков файл байт в байт как на сайте (head, main, формы, скрипты и блок счётчиков не меняются);
  * в блоках, если убрать ссылки на страницу документов, всё совпадает с сайтом байт в байт — меняется только пункт
    «Документы для Роспотребнадзора»;
  * блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) — ровно один и прежний.
Страница документов уже совпадает со сборкой — её не трогаем. Плюс новый файл img/dok-og.jpg из репозитория.
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SLUG = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
SKIP = {SLUG + 'index.php'}
NEW_FILES = ['img/dok-og.jpg']
BLOCKS = [re.compile(r'<header\b.*?</header>', re.S), re.compile(r'<nav class="mmenu".*?</nav>', re.S),
          re.compile(r'<footer\b.*?</footer>', re.S)]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
DOC_LINK = re.compile(r'(?:<li>)?<a href="(?:\.\./)*' + re.escape(SLUG) + r'"[^>]*>.*?</a>(?:</li>)?', re.S)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def outside(s):
    """страница без шапки, мобильного меню и подвала"""
    for rx in BLOCKS:
        s = rx.sub('', s, count=1)
    return s


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    built = sorted(str(p.relative_to(DIST)) for p in DIST.rglob('index.php'))
    assert pages == built, 'набор страниц на сайте и в сборке разный'
    files = []
    for p in pages:
        old = (live_dir / p).read_text(encoding='utf-8')
        b = (DIST / p).read_text(encoding='utf-8')
        if p in SKIP:
            assert old == b, p + ': страница документов на сайте отличается от сборки'
            continue
        new = old
        for rx in BLOCKS:
            lo, bu = rx.findall(old), rx.findall(b)
            assert len(lo) == 1 and len(bu) == 1, f'{p}: блок {rx.pattern[:20]} найден {len(lo)}/{len(bu)} раз'
            assert DOC_LINK.sub('', lo[0]) == DOC_LINK.sub('', bu[0]), f'{p}: в блоке {rx.pattern[:20]} есть другие отличия'
            new = new.replace(lo[0], bu[0], 1)
        assert outside(old) == outside(new), p + ': изменилось что-то вне шапки, меню и подвала'
        c1, c2 = COUNTERS.findall(old), COUNTERS.findall(new)
        if p in ('privacy/index.php', 'soglasie/index.php'):
            assert c1 == c2 == [], p + ': на странице документа появились счётчики'
        else:
            assert len(c1) == 1 and c1 == c2, p + ': блок счётчиков изменён или не найден'
        n_old, n_new = len(DOC_LINK.findall(old)), len(DOC_LINK.findall(new))
        assert (n_old, n_new) == (4, 6), f'{p}: ссылок на документы {n_old} → {n_new}, ожидалось 4 → 6'
        d = out / p
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(new, encoding='utf-8')
        files.append(p)
    for f in NEW_FILES:
        d = out / f
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes((ROOT / f).read_bytes())
        files.append(f)
    lines = ''.join(f'{sha((out / f).read_bytes())}  {f}\n' for f in sorted(files))
    if len(sys.argv) == 4:
        ref = pathlib.Path(sys.argv[3]).read_text(encoding='utf-8')
        if ref != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (out.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / f).read_bytes())}  {f}\n' for f in sorted(files) if f not in NEW_FILES)
    (out.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'страниц: {len(files) - len(NEW_FILES)}, новых файлов: {len(NEW_FILES)}; вне шапки, меню и подвала — без изменений;'
          ' счётчики прежние')


if __name__ == '__main__':
    main()
