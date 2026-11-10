#!/usr/bin/env python3
"""Сверка рабочего сайта пестконтроль-центр.рф с репозиторием: перед выкладкой и после неё.

    python3 tools/qa/check_live.py            # сборка для Timeweb (build_prod.py) и сверка с сайтом по HTTPS
    python3 tools/qa/check_live.py --build    # сначала полная сборка (build_site.py): она не должна менять файлы в git
    python3 tools/qa/check_live.py --no-prod  # сверить с уже собранной папкой dist/timeweb
    python3 tools/qa/check_live.py --quick    # только страницы, счётчики, стили, скрипты и sitemap (без картинок и PDF)

Что проверяется:
  1. (--build) полная сборка не меняет файлы репозитория — исходники, страницы и server/sitemap.xml согласованы;
  2. каждая страница сборки для Timeweb (dist/timeweb/**/index.php) против страницы на сайте: совпадает байт в байт
     или в каких частях отличается (head, шапка, мобильное меню, main, подвал, счётчики);
  3. счётчики на сайте: на каждой странице, кроме политики и согласия, ровно один блок «Яндекс Метрика 113675622 +
     UIS + Radist», байт в байт как в server/counters.html; на политике и согласии счётчиков нет (так задумано);
  4. style.css, legal.css, app.min.js, robots.txt, а также (без --quick) PDF и DOCX рядом со страницами, картинки,
     шрифты и скрипты, на которые ссылаются страницы: отвечают 200 и совпадают с репозиторием;
  5. sitemap.xml на сайте — те же адреса, даты изменения и приоритеты, что в server/sitemap.xml.

Код выхода 1 — ошибки: нет или сломан блок счётчиков, файл не открывается, сборка меняет файлы. Отличия страниц —
сведения, а не ошибка: в main может лежать согласованное, но ещё не выложенное. Перед выкладкой список отличий
должен совпадать с тем, что выкладка меняет; после выкладки все выложенные файлы должны совпасть.
send.php и .htaccess не сверяются: на сервере send.php с настоящим паролем почты, .htaccess по HTTPS не отдаётся.
"""
import concurrent.futures
import difflib
import hashlib
import html
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
LEGAL = {'privacy/index.php', 'soglasie/index.php'}
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
STATIC = ['style.css', 'legal.css', 'app.min.js', 'robots.txt']
SITEMAP_RE = re.compile(r'<loc>([^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>\s*<priority>([^<]*)</priority>')
ASSET_RE = re.compile(r'(?:src|href|srcset|imagesrcset|content|data-src|data-bg)="([^"]+)"|url\(([^)]+)\)')
ASSET_EXT = ('.webp', '.jpg', '.jpeg', '.png', '.svg', '.ico', '.gif', '.avif', '.woff2', '.woff', '.pdf', '.docx', '.js', '.css')
UA = 'pestcontrol-check/1.0 (+tools/qa/check_live.py)'

errors, notes = [], []


def err(msg):
    errors.append(msg)
    print('ОШИБКА', msg)


def get(url, tries=4):
    """GET с повтором: Timeweb из облака иногда отвечает ложным 502."""
    last = None
    for k in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            last = (e.code, b'')
            if e.code < 500:
                return last
        except Exception as e:  # сеть, TLS, таймаут
            last = (0, str(e).encode())
        time.sleep(2 + 2 * k)
    return last


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical_counters():
    c = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    i = c.index('<!-- Yandex.Metrika counter + UIS + Radist')
    return c[i:].strip()


def region(s, pos):
    """В какой части страницы позиция: head, шапка, мобильное меню, main, подвал, счётчики."""
    for name, a, b in (('счётчики', '<!-- Yandex.Metrika counter + UIS + Radist', '<!-- /Yandex.Metrika counter -->'),
                       ('head', '<head', '</head>'), ('шапка', '<header', '</header>'),
                       ('мобильное меню', '<nav class="mmenu"', '</nav>'), ('main', '<main', '</main>'),
                       ('подвал', '<footer', '</footer>')):
        i = s.find(a)
        j = s.find(b, i + 1) if i >= 0 else -1
        if i >= 0 and i <= pos <= j + len(b):
            return name
    return 'вне основных блоков'


def tok(s):
    return re.split(r'(?<=>)|(?<=\n)', s)


def describe(live, built, limit=4):
    A, B = tok(live), tok(built)
    ops = [o for o in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes() if o[0] != 'equal']
    out, pos = [], [0]
    for t in A:
        pos.append(pos[-1] + len(t))
    regions = {}
    for _, i1, i2, j1, j2 in ops:
        r = region(live, pos[i1])
        regions[r] = regions.get(r, 0) + 1
    for _, i1, i2, j1, j2 in ops[:limit]:
        a = re.sub(r'\s+', ' ', ''.join(A[i1:i2]))[:110]
        b = re.sub(r'\s+', ' ', ''.join(B[j1:j2]))[:110]
        out.append(f'      [{region(live, pos[i1])}] на сайте: {a!r}\n      {" " * (len(region(live, pos[i1])) + 2)} в сборке: {b!r}')
    head = ', '.join(f'{k} — {v}' for k, v in regions.items())
    return f'{len(ops)} мест ({head})', out


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def git_changed():
    r = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], capture_output=True, text=True)
    return [l[3:] for l in r.stdout.splitlines() if l and not l.startswith('??')]


def step_build():
    print('== 1. Полная сборка (build_site.py) не должна менять файлы репозитория')
    dirty = git_changed()
    if dirty:
        err('в рабочей копии есть незакоммиченные изменения — сначала закоммитьте или отложите их: ' + ', '.join(dirty[:8]))
        return
    r = run('tools/site/build_site.py')
    if r.returncode:
        err('сборка остановилась с ошибкой:\n' + (r.stdout + r.stderr)[-1500:])
        return
    changed = git_changed()
    if changed:
        err('сборка изменила файлы — исходники и страницы в репозитории расходятся: ' + ', '.join(changed)
            + '\n      (посмотреть: git diff; вернуть: git checkout -- <файлы>)')
    else:
        print('   OK: сборка ничего не меняет')


def main():
    args = set(sys.argv[1:])
    if '--build' in args:
        step_build()
    if '--no-prod' not in args:
        r = run('tools/site/build_prod.py')
        if r.returncode:
            err('сборка для Timeweb (build_prod.py) остановилась:\n' + (r.stdout + r.stderr)[-1500:])
            return finish()
    if not DIST.exists():
        err('нет dist/timeweb — запустите без --no-prod')
        return finish()

    block = canonical_counters()
    pages = sorted(str(p.relative_to(DIST)) for p in DIST.rglob('index.php'))
    print(f'== 2–3. Страницы ({len(pages)}) и счётчики на сайте')
    same, diff = [], []
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        live = dict(zip(pages, ex.map(lambda p: get(SITE + p[:-len('index.php')]), pages)))
    for p in pages:
        built = (DIST / p).read_bytes()
        code, body = live[p]
        url = '/' + p[:-len('index.php')]
        if code != 200:
            err(f'{url}: ответ {code}')
            continue
        text = body.decode('utf-8', 'replace')
        found = COUNTERS.findall(text)
        if p in LEGAL:
            if found:
                notes.append(f'{url}: на странице документа есть счётчики (по задумке их там нет)')
        elif len(found) != 1:
            err(f'{url}: блоков счётчиков на сайте — {len(found)} (нужен ровно один)')
        elif found[0] != block:
            err(f'{url}: блок счётчиков на сайте отличается от server/counters.html — выяснить, какой верный,'
                ' и не выкладывать страницу, пока не решено')
        elif "ym(113675622, 'init'" not in found[0] or 'uiscom' not in found[0] or 'radist' not in found[0]:
            err(f'{url}: в блоке счётчиков нет Метрики 113675622, UIS или Radist')
        if sha(body) == sha(built):
            same.append(url)
        else:
            summary, lines = describe(text, built.decode('utf-8'))
            diff.append(url)
            print(f'   отличается {url}: {summary}')
            for l in lines:
                print(l)
    print(f'   совпадают байт в байт: {len(same)} из {len(pages)}; отличаются: {len(diff)}')
    print('   счётчики: ' + ('OK на всех страницах' if not any('счётчик' in e for e in errors) else 'есть ошибки (выше)'))

    print('== 4. Стили, скрипты, robots.txt' + ('' if '--quick' in args else ', картинки, шрифты, PDF и DOCX'))
    assets = set(STATIC)
    if '--quick' not in args:
        for p in pages:
            s = (DIST / p).read_text(encoding='utf-8')
            base = SITE + p[:-len('index.php')]
            for m in ASSET_RE.finditer(s):
                raw = html.unescape(m.group(1) or m.group(2).strip('\'" '))
                for part in raw.split(','):
                    u = part.strip().split(' ')[0]
                    if not u or u.startswith(('data:', 'mailto:', 'tel:', '#', 'javascript:')):
                        continue
                    full = urllib.parse.urljoin(base, u)
                    if not full.startswith(SITE):
                        continue
                    path = urllib.parse.unquote(urllib.parse.urlsplit(full).path)[1:]
                    if path.lower().endswith(ASSET_EXT):
                        assets.add(path)
        for f in list(DIST.rglob('*.pdf')) + list(DIST.rglob('*.docx')):
            assets.add(str(f.relative_to(DIST)))
    assets = sorted(assets)
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        got = dict(zip(assets, ex.map(lambda a: get(SITE + urllib.parse.quote(a)), assets)))
    a_same, a_diff, a_missing_repo = 0, [], []
    for a in assets:
        code, body = got[a]
        local = DIST / a
        if code != 200:
            err(f'/{a}: ответ {code}' + ('' if local.exists() else ' (и в репозитории файла нет)'))
            continue
        if not local.exists():
            a_missing_repo.append('/' + a)
        elif sha(body) == sha(local.read_bytes()):
            a_same += 1
        else:
            a_diff.append('/' + a)
    print(f'   файлов: {len(assets)}; совпадают: {a_same}; отличаются: {len(a_diff)}'
          + (f'; на сайте есть, в сборке нет: {len(a_missing_repo)}' if a_missing_repo else ''))
    for a in a_diff[:20]:
        print('   отличается', a)
    for a in a_missing_repo[:10]:
        print('   нет в сборке', a)

    print('== 5. sitemap.xml')
    code, body = get(SITE + 'sitemap.xml')
    if code != 200:
        err(f'/sitemap.xml: ответ {code}')
    else:
        L = SITEMAP_RE.findall(body.decode('utf-8'))
        R = SITEMAP_RE.findall((ROOT / 'server' / 'sitemap.xml').read_text(encoding='utf-8'))
        if L == R:
            print(f'   OK: {len(L)} адресов, даты и приоритеты как в server/sitemap.xml')
        else:
            dl, dr = dict((x[0], x[1:]) for x in L), dict((x[0], x[1:]) for x in R)
            for loc in sorted(set(dl) | set(dr)):
                if dl.get(loc) != dr.get(loc):
                    print(f'   отличается {loc.replace(SITE, "/")}: на сайте {dl.get(loc)}, в репозитории {dr.get(loc)}')
    return finish()


def finish():
    for n in notes:
        print('примечание:', n)
    print('== ИТОГ: ' + ('ошибок нет' if not errors else f'ошибок — {len(errors)}'))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
