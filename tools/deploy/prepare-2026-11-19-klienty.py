#!/usr/bin/env python3
"""Блок «Наши клиенты» на главной и коммерческих страницах (19.11.2026): пакет для Timeweb.

    python3 tools/deploy/prepare-2026-11-19-klienty.py <новая папка>                  # страницы — с сайта по HTTPS
    python3 tools/deploy/prepare-2026-11-19-klienty.py <новая папка> --base <папка>   # страницы — из папки (например,
                                                                                      # pkg/ пакета, который выкладывается
                                                                                      # перед этим в том же запуске)
    python3 tools/deploy/prepare-2026-11-19-klienty.py <папка> --check                # пересобрать из <папка>/backup

Решение владельца 19.11.2026: «подключить списки во все страницы — да; исправить в коде пробел в „0 ₽“ — да.
Оригиналов логотипов недостающих нет — ищи в интернете. Вноси эти изменения на Timeweb».

Что меняется на рабочем сайте (остальное — байт в байт):
  * главная и коммерческие страницы из tools/site/clients_block.py (PAGES), которые есть на сайте: блок #klienty
    (главная — после прайса #tseny, остальные — перед формой #zayavka), стили <style id="kl-st"> после <style id="pr-st">
    и скрипт <script id="kl-js"> после блока — всё строго через clients_block.patch();
  * новые файлы img/klienty/*.webp (логотипы; на сайте их ещё нет).
Для каждой страницы: если убрать вставленные блок, скрипт и стили, получается исходник байт в байт; счётчики Метрики,
UIS и Radist, телефон и почта — по закону владельца (tracking_laws) до и после; закон независимости — до и после.
"""
import base64
import concurrent.futures
import hashlib
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
sys.path.insert(0, str(ROOT / 'tools/qa'))
import clients_block as cb  # noqa: E402
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'klienty-2026-11-19'
IMG = sorted((ROOT / 'img/klienty').glob('*.webp'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def page_files():
    return [('', 'index.php')] + [(rel, rel + '/index.php') for rel in cb.PAGES]


def one_insert(old, new):
    """new = old + одна вставка в одном месте: вернуть вставку (иначе ошибка)."""
    d = len(new) - len(old)
    assert d > 0
    p = 0
    while p < len(old) and old[p] == new[p]:
        p += 1
    assert new[p + d:] == old[p:], 'кроме вставки изменилось что-то ещё'
    return new[p:p + d]


def check_page(rel, file, old, new):
    t_old, t_new = old.decode('utf-8'), new.decode('utf-8')
    assert '<?php' not in t_old and '<?=' not in t_old, file
    assert 'id="klienty"' not in t_old and 'kl-st' not in t_old and 'kl-js' not in t_old, 'блок уже есть: ' + file
    assert t_new.count('id="klienty"') == 1 and t_new.count('id="kl-st"') == 1 and t_new.count('id="kl-js"') == 1, file
    css = re.search(r'<style id="kl-st">.*?</style>', t_new, re.S).group(0)
    assert css == cb.CSS
    ins = one_insert(t_old, t_new.replace(css, '', 1))
    assert ins.count('<section') == 1 and 'id="klienty"' in ins and 'id="kl-js"' in ins, file
    for bad in ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?'):
        assert bad not in ins.lower() and bad not in css.lower(), file + ': ' + bad
    i = t_new.index(css)
    before = t_new[:i]
    assert (before.endswith('</style>') and before.rfind('<style id="pr-st">') > before.rfind('</style>', 0, len(before) - 8)) \
        or re.search(r'<link rel="stylesheet" href="[^"]*style\.css[^"]*">$', before), 'стили не на месте: ' + file
    assert i < t_new.index('</head>') and not t_new[i + len(css):].startswith('</head>'), file
    for t in (t_old, t_new):
        v = tracking_laws.check_page(t, counters=True)
        assert not v, file + ': ' + '; '.join(map(str, v))
        iv = independence_law.violations(t)
        assert not iv, file + ': ' + '; '.join(map(str, iv))
    for src in re.findall(r'img/klienty/([a-z0-9-]+\.webp)', t_new):
        assert (ROOT / 'img/klienty' / src).is_file(), file + ': нет ' + src
    assert ('0\u00a0₽' in ins and '0 ₽' not in ins) or 'Бесплатный аудит' in ins, file


def snapshot(base):
    import check_live as live
    out = {}

    def job(item):
        rel, file = item
        if base:
            p = base / file
            return file, (p.read_bytes() if p.is_file() else None)
        code, body = live.get(live.SITE + (rel + '/' if rel else ''), tries=8)[:2]
        return file, (body if code == 200 else None)
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for file, body in ex.map(job, page_files()):
            out[file] = body
    return out


def live_images_absent():
    import check_live as live
    for p in IMG[:3]:
        code = live.get(live.SITE + 'img/klienty/' + p.name, tries=4)[0]
        assert code == 404, 'на сайте уже есть img/klienty/' + p.name + ' (код ' + str(code) + ')'


def build(files):
    rows, results = [], {}
    for rel, file in page_files():
        old = files.get(file)
        if old is None:
            continue
        new = cb.patch(old.decode('utf-8'), rel).encode('utf-8')
        check_page(rel, file, old, new)
        results[file] = new
        rows.append({'file': file, 'before': sha(old), 'after': sha(new), 'content': new.decode('utf-8')})
    for p in IMG:
        b = p.read_bytes()
        assert b[:4] == b'RIFF' and b[8:12] == b'WEBP', p.name
        rows.append({'file': 'img/klienty/' + p.name, 'before': None, 'after': sha(b),
                     'content_b64': base64.b64encode(b).decode('ascii')})
    return rows, results


def write_package(out, files, rows, results):
    for file, new in results.items():
        for folder, content in (('backup', files[file]), ('pkg', new)):
            f = out / folder / file
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content)
    for p in IMG:
        f = out / 'pkg/img/klienty' / p.name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(p.read_bytes())
    pages = [r for r in rows if r['before']]
    payload = {'name': NAME, 'count': len(rows), 'pages': len(pages), 'images': len(rows) - len(pages), 'files': rows}
    (out / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file'])
                                              for r in rows), encoding='utf-8')
    shutil.copy2(str(ROOT / 'tools/deploy/publish_klienty.py'), str(out / 'publish_klienty.py'))
    run_once = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_klienty.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_klienty.py --check &&
  python3 publish_klienty.py --publish &&
  python3 publish_klienty.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((out / 'publish_klienty.py').read_bytes()),
       'sd': sha((out / 'deploy_payload.json').read_bytes())}
    (out / 'run_once.sh').write_text(run_once, encoding='utf-8')
    (out / 'run_once.sh').chmod(0o755)


def main(argv):
    out = pathlib.Path(argv[0]).resolve()
    if argv[1:] == ['--check']:
        files = {p.relative_to(out / 'backup').as_posix(): p.read_bytes()
                 for p in sorted((out / 'backup').rglob('*')) if p.is_file()}
        rows, results = build(files)
        payload = json.loads((out / 'deploy_payload.json').read_text(encoding='utf-8'))
        assert [(r['file'], r['before'], r['after']) for r in rows] == \
               [(r['file'], r['before'], r['after']) for r in payload['files']], 'payload не совпадает с пересборкой'
        for file, b in results.items():
            assert (out / 'pkg' / file).read_bytes() == b, 'pkg/' + file + ' не совпадает с пересборкой'
        print('Пересборка совпала: %d файлов' % len(rows))
        return
    assert not out.exists(), 'используйте новую папку: прежние копии не перезаписываются'
    base = pathlib.Path(argv[argv.index('--base') + 1]).resolve() if '--base' in argv else None
    live_images_absent()
    files = snapshot(base)
    rows, results = build(files)
    write_package(out, files, rows, results)
    skipped = [f for f, b in files.items() if b is None]
    print('Готово: %d страниц, %d логотипов; нет на сайте (пропущены): %s. Пакет: %s' % (
        len(results), len(IMG), ', '.join(skipped) or '—', out))


if __name__ == '__main__':
    main(sys.argv[1:])
