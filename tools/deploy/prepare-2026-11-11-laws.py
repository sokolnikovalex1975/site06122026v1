#!/usr/bin/env python3
"""Пакет из текущих файлов сайта: ЗАКОН ВЛАДЕЛЬЦА 11.11.2026 (замечания программиста) на всех страницах сайта.

  1. Счётчики: отложенный блок (с 28.10.2026: Метрика, UIS и Radist грузились после касания, прокрутки или через 5 с,
     перехват нажатия на телефон) убран. Официальные коды — server/counters.html: Метрика 113675622 в <head> сразу после
     <meta name="viewport">, UIS прямо перед </head>, <noscript> Метрики сразу после <body>, Radist в конце <body>.
  2. Телефон и почта: в ссылках только «+7 (495) 104-35-70» обычными пробелами и «b2b@pestcontrol-center.ru» — без <span>,
     <wbr>, <i>, <svg>, &nbsp; и копий номера в aria-label; значок телефона в шапке — стилем <style id="tel-plain">.
Всё остальное на страницах — байт в байт как на сайте (проверяется: маска страницы без счётчиков, ссылок телефона и почты
и стиля tel-plain до и после совпадает). Правки из main, которых ещё нет на сайте, в пакет не попадают.

    python3 tools/deploy/prepare-2026-11-11-laws.py <копия-сайта> <папка-выкладки>
Копия сайта — index.php всех страниц (build_prod.PAGES + политика и согласие), скачанные по HTTPS перед подготовкой.
"""
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402  список страниц сайта
import tracking_laws as T  # noqa: E402  закон владельца

NAME = 'pestcontrol-deploy-2026-11-11-laws'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def mask(s):
    """Страница без того, что меняет закон: счётчики, ссылки телефона и почты, стиль tel-plain."""
    s = T.strip_counters(s)
    s = T.STYLE_RE.sub('', s)
    s = T.TEL_A.sub(lambda m: '<a TEL' + re.sub(r'\s+aria-label="[^"]*"', '', m.group('attrs')) + '>'
                    + ('#' if re.search(r'\d', T.plain(m.group('inner'))) else m.group('inner')) + '</a>', s)
    s = T.MAIL_A.sub(lambda m: '<a MAIL' + m.group('attrs') + '>#</a>', s)
    s = T.TEXT_PHONE.sub('PHONE', s)
    return re.sub(r'\s+', ' ', s)


def main():
    src, dst = map(pathlib.Path, sys.argv[1:3])
    parts = T.counter_parts()
    pages = [r.replace('index.html', 'index.php') for r in build_prod.PAGES + build_prod.LEGAL]
    present = [p for p in pages if (src / p).exists()]
    missing = sorted(set(pages) - set(present))
    print('нет на сайте (не выложены, в пакет не входят):', ', '.join(missing) or '—')
    if (dst / 'pkg').exists():
        shutil.rmtree(dst / 'pkg')
    order, before, after = [], [], []
    for path in present:
        data = (src / path).read_bytes()
        s = data.decode('utf-8')
        legal = path in T.NO_COUNTERS
        old_block = re.findall(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', s, re.S)
        assert len(old_block) == (0 if legal else 1), (path, 'ожидался один отложенный блок счётчиков')
        new = T.normalize_contacts(s)
        if not legal:
            new = T.install_counters(new, parts)
        bad = T.check_page(new, counters=not legal, parts=parts)
        assert not bad, (path, bad)
        assert mask(new) == mask(s), path + ': изменилось что-то кроме счётчиков, телефона и почты'
        assert T.normalize_contacts(new) == new and (legal or T.install_counters(new, parts) == new), path + ': не идемпотентно'
        assert new.rstrip().endswith('</html>'), path
        for k in ('113675622', 'ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me'):
            assert (k in new) == (not legal), (path, k)
        b = new.encode('utf-8')
        out = dst / 'pkg' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b)
        order.append(path)
        before.append(sha(data) + '  ' + path)
        after.append(sha(b) + '  ' + path)
        tel = len([m for m in T.TEL_A.finditer(new) if re.search(r'\d', T.plain(m.group('inner')))])
        print(f'{path}: {len(b) - len(data):+d} байт; ссылок с номером {tel}; '
              + ('без счётчиков (документ)' if legal else 'счётчики — официальные коды на своих местах'))
    config = (
        '# Закон владельца 11.11.2026 (замечания программиста): счётчики сразу, телефон и почта без лишних тегов.\n'
        '# Пакет из текущих файлов сайта (tools/deploy/prepare-2026-11-11-laws.py). Счётчики меняются намеренно:\n'
        '#   ALLOW_COUNTERS_CHANGE=1 bash run_all.sh deploy\n'
        f'NAME="{NAME}"\nBK="before-laws_2026-11-11_ftp.zip"\n'
        'ORDER="' + '\n'.join(order) + '"\n'
        'REPLACED="' + ' '.join(order) + '"\n'
        'EXPECTED_BEFORE="' + '\n'.join(before) + '"\n'
        'CHECK_DIRS="privacy soglasie materialy normativnaya-baza laboratornye-issledovaniya"\n'
    )
    (dst / 'deploy.conf').write_text(config, encoding='utf-8')
    (dst / 'MANIFEST.sha256').write_text('\n'.join(after) + '\n', encoding='utf-8')
    shutil.copy2(ROOT / 'tools/deploy/run_all.sh', dst / 'run_all.sh')
    shutil.copy2(ROOT / 'tools/deploy/launch-2026-11-11-laws.sh', dst / 'launch.sh')
    print(f'готово: {len(order)} страниц в {dst}/pkg')


if __name__ == '__main__':
    main()
