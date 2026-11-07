#!/usr/bin/env python3
"""Пакет выкладки 08.11.2026: «Нормативная база» и «Проверочные листы» — hero-фото, инфографика, превью образцов.

    python3 tools/deploy/patch-2026-11-08-nbvis.py <файлы с сайта> <сборка «до»> <сборка «после»> <папка pkg>

  <файлы с сайта>  — normativnaya-baza/index.php, normativnaya-baza/proverochnye-listy/index.php, img/nb-og.jpg, img/pl-og.jpg,
                     снятые по HTTPS перед выкладкой;
  <сборка «до»>    — dist/timeweb сборки коммита a721188 (последнее состояние этих страниц на сайте, эффекты fx как на сайте);
  <сборка «после»> — dist/timeweb сборки с правками этой выкладки на той же основе (без не выложенных правок других задач:
                     меню «Разработка ППК по ХАССП» из a130410 в пакет не входит).

Проверяет: сборка «до» совпадает с файлом сайта байт в байт (с одной поправкой — строка <style id="m-crumbs"> в сборке стоит
после <style data-fx>, на сайте — перед ней; в пакете она ставится как на сайте), блок счётчиков (Метрика 113675622, UIS/CoMagic,
Radist) в пакете — байт в байт как на сайте, нет noindex и PHP-вставок, canonical на месте, «фонарь» на фото первого экрана есть.
"""
import hashlib
import pathlib
import re
import shutil
import sys

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
PAGES = ['normativnaya-baza/index.php', 'normativnaya-baza/proverochnye-listy/index.php']
NEW_IMG = [f'img/{n}{s}.webp' for n in ('nb-hero', 'pl-hero') for s in ('', '-1440', '-mob', '-mob-760')] + [
    'img/programma-sample-p1-top-480.webp', 'img/programma-sample-p1-top-720.webp',
    'img/zhurnal-obrazets-p1-top-480.webp', 'img/zhurnal-obrazets-p1-top-720.webp',
    'img/ppk-sample-p1-top-480.webp', 'img/ppk-sample-p1-top-720.webp',
    'img/dogovor-sample-p1-top-480.webp', 'img/dogovor-sample-p1-top-680.webp']
OG = ['img/nb-og.jpg', 'img/pl-og.jpg']
COUNTERS = ['113675622', 'mc.yandex.ru/metrika/tag.js',
            'app.uiscom.ru/static/cs.min.js?k=ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me/tracker.min.js']
MC = re.compile(r'<style id="m-crumbs">.*?</style>\n', re.S)


def as_on_site(s):
    """Строка m-crumbs — перед <style data-fx>, как в файлах сайта."""
    assert s.count('<style id="m-crumbs">') == 1 and s.count('<style data-fx>') == 1
    m = MC.search(s)
    s2 = s[:m.start()] + s[m.end():]
    i = s2.find('<style data-fx>')
    return s2[:i] + m.group(0) + s2[i:]


def counters_tail(s):
    i = s.find("ym(113675622, 'init'")
    assert i > 0, 'нет Метрики'
    return s[s.rfind('<script', 0, i):]


def main(live, before, after, pkg):
    live, before, after, pkg = map(pathlib.Path, (live, before, after, pkg))
    if pkg.exists():
        shutil.rmtree(pkg)
    for p in PAGES:
        lv = (live / p).read_text(encoding='utf-8')
        bf = as_on_site((before / p).read_text(encoding='utf-8'))
        assert bf == lv, (p, 'сборка «до» не совпадает с файлом сайта')
        new = as_on_site((after / p).read_text(encoding='utf-8'))
        assert counters_tail(new) == counters_tail(lv), (p, 'блок счётчиков изменился')
        for c in COUNTERS:
            assert new.count(c) == lv.count(c) >= 1, (p, c)
        assert 'noindex' not in new and new.count('<?') == 0, p
        page = p[:-len('index.php')]
        assert f'<link rel="canonical" href="{SITE}{page}">' in new, (p, 'canonical')
        assert new.count('class="fx-lit"') == 1 and new.count('id="m-crumbs"') == 1, p
        o = pkg / p
        o.parent.mkdir(parents=True, exist_ok=True)
        o.write_bytes(new.encode('utf-8'))
        print(f'ok {p}: {len(new.encode()) - len(lv.encode()):+d} байт, счётчики как на сайте')
    pages_txt = ''.join((pkg / p).read_text(encoding='utf-8') for p in PAGES)
    for f in NEW_IMG:
        assert f.split('/')[-1] in pages_txt, (f, 'на страницах нет ссылки на картинку')
    for f in NEW_IMG + OG:
        o = pkg / f
        o.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(after / f, o)
    for f in OG:
        assert (pkg / f).read_bytes() != (live / f).read_bytes(), (f, 'картинка не изменилась')
    order = NEW_IMG + PAGES[::-1] + OG  # новые картинки → страницы (листы, потом хаб) → картинки для соцсетей
    man = '\n'.join(f'{hashlib.sha256((pkg / f).read_bytes()).hexdigest()}  {f}' for f in order) + '\n'
    (pkg.parent / 'MANIFEST.sha256').write_text(man, encoding='utf-8')
    print(f'pkg: {len(order)} файлов; MANIFEST.sha256 рядом с pkg')
    return order


if __name__ == '__main__':
    main(*sys.argv[1:5])
