#!/usr/bin/env python3
"""Выкладка 08.11.2026 (страница «Разработка ППК»): пакет из файлов, как их отдаёт сайт, и новой страницы.

Использование:
  python3 tools/deploy/patch-2026-11-08-rppk.py <папка с файлами сайта> <папка результата> [MANIFEST]

<папка с файлами сайта> — 22 файла index.php (список PAGES) и sitemap.xml, как их отдаёт сайт по HTTPS перед
выкладкой (или как они лежат в копии tools/deploy/backup/before-rppk_2026-11-08_ftp.zip). В <папку результата>
пишутся файлы пакета pestcontrol-deploy-2026-11-08-rppk; если указан MANIFEST
(tools/deploy/MANIFEST-2026-11-08-rppk.sha256), суммы результата сверяются с ним.

  * 22 страницы сайта — в меню «Услуги» (шапка, мобильное меню, подвал) после «Санитарный аудит (СЭС-аудит)»
    добавляется пункт «Разработка ППК» (/razrabotka-ppk/). Остальное меню — как на сайте: в превью на GitHub
    есть ещё пункт «Разработка ППК по ХАССП» (коммит a130410), он на сайт не выложен и сюда не попадает;
  * новая страница razrabotka-ppk/index.php — razrabotka-ppk/index.html из репозитория, как её делает
    tools/site/build_prod.py (без noindex превью, с блоком счётчиков server/counters.html), а шапка, мобильное меню
    и подвал — как на сайте (из страницы санитарного аудита с новым пунктом; текущая страница — «Разработка ППК»);
  * sitemap.xml — добавлен адрес /razrabotka-ppk/ после санитарного аудита, прочие строки не меняются;
  * картинки первого экрана и Open Graph — из img/ репозитория (rppk-*).
  Проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице байт в байт прежний,
  вне трёх блоков меню файл не меняется, каждый пункт вставлен ровно один раз в каждый блок.
"""
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402  тот же блок счётчиков и та же правка noindex, что в рабочей сборке

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
PAGES = [
    'index.php', 'dezinfektsiya/index.php', 'deratizatsiya/index.php', 'dezinsektsiya/index.php',
    'sanitarnyy-audit/index.php', 'dogovor-deratizatsiya-dezinsektsiya/index.php',
    'ochistka-dezinfektsiya-ventilyatsii/index.php', 'pishchevoe-proizvodstvo/index.php', 'restorany-i-kafe/index.php',
    'magaziny-i-torgovye-seti/index.php', 'gostinitsy/index.php', 'farmatsevticheskie-proizvodstva/index.php',
    'sklady-i-logistika/index.php', 'materialy/index.php', 'materialy/programma-pest-kontrolya/index.php',
    'materialy/zhurnal-pest-kontrolya/index.php', 'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'normativnaya-baza/index.php',
    'normativnaya-baza/proverochnye-listy/index.php', 'privacy/index.php', 'soglasie/index.php',
]
NEW_PAGE = 'razrabotka-ppk/index.php'
IMAGES = ['img/rppk-hero.webp', 'img/rppk-hero-1440.webp', 'img/rppk-hero-mob.webp', 'img/rppk-hero-mob-760.webp',
          'img/rppk-og.jpg']
SAN = 'sanitarnyy-audit/index.php'
LABEL = 'Разработка ППК'
SLUG = 'razrabotka-ppk/'
AUDIT = '<span>Санитарный аудит <span class="nw">(СЭС-аудит)</span></span>'
ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
BLOCKS = {  # три блока меню: шапка, мобильное меню, колонка «Услуги» в подвале
    'nav': re.compile(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', re.S),
    'mm': re.compile(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', re.S),
    'ft': re.compile(r'<div><h4>Услуги</h4><ul>.*?</ul></div>', re.S),
}
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
SITEMAP_AFTER = (f'  <url>\n    <loc>{SITE}sanitarnyy-audit/</loc>\n    <lastmod>[0-9-]+</lastmod>\n'
                 '    <priority>[0-9.]+</priority>\n  </url>\n')
SITEMAP_NEW = f'  <url>\n    <loc>{SITE}{SLUG}</loc>\n    <lastmod>2026-11-08</lastmod>\n    <priority>0.9</priority>\n  </url>\n'


def root_of(rel):
    return '../' * rel.count('/')


def audit_item(rel):
    """Ссылка «Санитарный аудит» в меню страницы rel: на самой странице аудита — текущая."""
    if rel == SAN:
        return '<a href="./" aria-current="page">' + AUDIT
    return f'<a href="{root_of(rel)}sanitarnyy-audit/">' + AUDIT


def items(rel):
    """(что найти, что вставить после) для каждого блока меню."""
    a, href = audit_item(rel), root_of(rel) + SLUG
    return {
        'nav': (a + ARR + '</a>', f'<a href="{href}">{LABEL}{ARR}</a>'),
        'mm': (a + '</a>', f'<a href="{href}">{LABEL}</a>'),
        'ft': ('<li>' + a + '</a></li>', f'<li><a href="{href}">{LABEL}</a></li>'),
    }


def one_block(s, key, rel):
    ms = list(BLOCKS[key].finditer(s))
    assert len(ms) == 1, f'{rel}: блок меню {key} найден {len(ms)} раз'
    return ms[0]


def add_item(s, rel):
    assert SLUG not in s, f'{rel}: ссылка на {SLUG} уже есть'
    for key, (find, ins) in items(rel).items():
        m = one_block(s, key, rel)
        block = m.group(0)
        assert block.count(find) == 1, f'{rel}: в блоке {key} пункт аудита найден {block.count(find)} раз'
        s = s[:m.start()] + block.replace(find, find + ins, 1) + s[m.end():]
    return s


def outside(s):
    """Файл без трёх блоков меню — для проверки, что вне меню ничего не изменилось."""
    for rx in BLOCKS.values():
        s = rx.sub('<!--MENU-->', s, count=1)
    return s


def new_page(san_patched):
    s = (ROOT / 'razrabotka-ppk' / 'index.html').read_text(encoding='utf-8')
    assert build_prod.COUNTERS_MARK not in s, 'в странице из репозитория уже есть счётчики'
    s, n = build_prod.ROBOTS_RE.subn('', s, count=1)
    assert n == 1, 'нет метки robots превью'
    s = s.replace('</body>', build_prod.counters() + '\n</body>', 1)
    assert s.count("ym(113675622, 'init'") == 1
    # шапка, мобильное меню и подвал — как на сайте (страница аудита того же уровня), текущая — «Разработка ППК»
    for key in BLOCKS:
        block = one_block(san_patched, key, SAN).group(0)
        cur_a, cur_b = '<a href="./" aria-current="page">' + AUDIT, '<a href="../sanitarnyy-audit/">' + AUDIT
        mine_a, mine_b = f'<a href="../{SLUG}">{LABEL}', f'<a href="./" aria-current="page">{LABEL}'
        assert block.count(cur_a) == 1 and block.count(mine_a) == 1, key
        block = block.replace(cur_a, cur_b, 1).replace(mine_a, mine_b, 1)
        m = one_block(s, key, NEW_PAGE)
        s = s[:m.start()] + block + s[m.end():]
    assert s.count('aria-current="page"') == 4, 'текущая страница: цепочка + 3 блока меню'
    return s


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    manifest = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if dst.exists():
        shutil.rmtree(dst)
    out = {}
    for rel in PAGES:
        s = (src / rel).read_text(encoding='utf-8')
        t = add_item(s, rel)
        assert outside(t) == outside(s), f'{rel}: изменилось что-то вне меню'
        cs, ct = COUNTERS.findall(s), COUNTERS.findall(t)
        assert cs == ct, f'{rel}: блок счётчиков изменился'
        if rel not in ('privacy/index.php', 'soglasie/index.php'):
            assert len(cs) == 1 and "ym(113675622, 'init'" in cs[0] and 'uiscom' in cs[0] and 'radist' in cs[0], rel
        assert t.count(f'href="{root_of(rel)}{SLUG}"') == 3, rel
        out[rel] = t
    out[NEW_PAGE] = new_page(out[SAN])
    sm = (src / 'sitemap.xml').read_text(encoding='utf-8')
    assert SLUG not in sm
    sm2, n = re.subn(SITEMAP_AFTER, lambda m: m.group(0) + SITEMAP_NEW, sm, count=1)
    assert n == 1, 'sitemap.xml: нет адреса санитарного аудита'
    out['sitemap.xml'] = sm2
    for rel, text in out.items():
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode('utf-8'))
    for rel in IMAGES:
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, f)
    rels = IMAGES + [NEW_PAGE] + PAGES + ['sitemap.xml']
    lines = [f'{hashlib.sha256((dst / r).read_bytes()).hexdigest()}  {r}' for r in rels]
    print('\n'.join(lines))
    if manifest:
        want = manifest.read_text(encoding='utf-8').strip().splitlines()
        assert sorted(want) == sorted(lines), 'результат не совпадает с MANIFEST'
        print('== совпадает с', manifest.name)


if __name__ == '__main__':
    main()
