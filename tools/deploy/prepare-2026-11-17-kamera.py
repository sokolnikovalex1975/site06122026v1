#!/usr/bin/env python3
"""«Что видит камера в коробе» на странице вентиляции: пакет для Timeweb из рабочего сайта (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-kamera.py <новая папка пакета>

Решение владельца 17.11.2026 («Выкладывай на сайт») по превью /preview-kamera-ventilyatsii/ (14.11.2026):
SVG-схема блока «Что видит камера в коробе» → три реалистичных кадра одного участка короба со сменой WebGL
(tools/ventilyatsiya/kamera/README.md).

Страница снимается с сайта по HTTPS (index.php на сервере — готовый HTML) и правится тем же apply.py, что и превью;
для сервера правка записывается точными заменами (подпись, кадр, «Что видно на кадре», 11 правил стилей, скрипт блока).
Проверки: последовательные замены дают байт в байт результат apply.py; закон о счётчиках и контактах
(tracking_laws.check_page) и закон независимости — без нарушений до и после; Метрика, UIS, Radist, телефон и почта —
те же строки, в том же числе; вне блока страница не меняется. 9 кадров img/vent-kadr-*.webp — из репозитория, на сайте
их ещё нет (HTTP 404).

Другие задачи 17.11.2026 выкладывают пакеты zagolovok-2026-11-13 (выложен в 01:39 МСК) и shapka-2026-11-17 (на этой
странице у обоих — только ?v= у style.css и app.min.js). Если такой пакет ещё не выложен, пакет принимает страницу в обоих
видах: как сейчас на сайте и после той выкладки (её замены — из tools/deploy/zagolovok-2026-11-13/deploy_payload.json или
SHAPKA_ROW ниже, сверяются по суммам) — выкладки не мешают друг другу, если эта идёт второй.

В папке пакета: backup/ и pkg/ (страница до и после, кадры), MANIFEST.txt, deploy_payload.json, publish_kamera.py, run_once.sh.
"""
import base64
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'kamera-2026-11-17'
PAGE = 'ochistka-dezinfektsiya-ventilyatsii/index.php'
IMAGES = ['img/vent-kadr-%s%s.webp' % (k, w) for k in ('1-do', '2-ochistka', '3-dezinfektsiya')
          for w in ('-720', '-1080', '')]


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


live = module('check_live', 'tools/qa/check_live.py')
kam = module('kamera_apply', 'tools/ventilyatsiya/kamera/apply.py')
K = ROOT / 'tools/ventilyatsiya/kamera'


def pairs(s):
    """Те же правки, что kam.apply(s), — списком точных замен (старое, новое) в порядке применения."""
    fig = re.search(r'<figure class="v-duct" id="vduct".*?</figure>', s, re.S).group(0)
    lab = re.search(r'<span class="v-duct-k">Схема · (что видит камера в[ \u00a0]коробе)</span>', fig).group(0)
    art = re.search(r'      <div class="v-duct-art">\s*<svg.*?</svg>\s*</div>\n', fig, re.S).group(0)
    leg = re.search(r'      <ul class="v-legend".*?</ul>\n', fig, re.S).group(0)
    out = [
        (lab, lab.replace('<span class="v-duct-k">Схема · ', '<span class="v-duct-k">Иллюстрация · ')),
        (art, (K / 'art.html').read_text(encoding='utf-8')),
        (leg, (K / 'legend.html').read_text(encoding='utf-8')),
        (kam.OLD_CSS[0], kam.mini_css((K / 'block.css').read_text(encoding='utf-8'))),
    ]
    out += [(rule, '') for rule in kam.OLD_CSS[1:]]
    out.append((kam.OLD_CSS_RM, ''))
    a = s.index(kam.JS_START)
    b = s.index(kam.JS_END, a)
    out.append((s[a:b], (K / 'block.js').read_text(encoding='utf-8')))
    return out


OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

status, body = live.get(live.SITE + '/ochistka-dezinfektsiya-ventilyatsii/', tries=8)  # Timeweb из облака иногда отвечает ложным 502
assert status == 200, 'HTTP %s' % status
old = body.decode('utf-8')
assert '<?php' not in old and '<?=' not in old, 'PHP в файле'
bad = tracking_laws.check_page(old, counters=True)
assert not bad, 'исходная страница: %s' % bad
assert independence_law.violations(old) == [], 'закон независимости (до)'

reps = pairs(old)


def patched(src):
    out = src
    for a, b in reps:
        assert out.count(a) == 1, '«%s…» найдено %d раз' % (a[:60], out.count(a))
        out = out.replace(a, b)
    assert out == kam.apply(src), 'замены не совпали с apply.py'
    bad = tracking_laws.check_page(out, counters=True)
    assert not bad, 'результат: %s' % bad
    assert independence_law.violations(out) == [], 'закон независимости (после)'
    for k in ('113675622', 'mc.yandex.ru', 'uiscom', 'radist', 'tel:', 'mailto:', '<script', '</script>', '<form', 'send.php', '?v='):
        assert src.count(k) == out.count(k), 'изменилось число «%s»' % k
    return out


new = patched(old)
variants = [[sha(body), sha(new.encode('utf-8'))]]
vnames = ['as built']
# Пакеты других задач, которые ещё могут выйти раньше этого (на этой странице у них — только ?v= у style.css
# и app.min.js): страница после такого пакета — второй исходный вид. zagolovok-2026-11-13 лежит в репозитории;
# shapka-2026-11-17 к 02:05 МСК 17.11.2026 был только на сервере (Home/pestcontrol-shapka-2026-11-17/deploy_payload.json,
# загружен 01:55 МСК) — его строка этой страницы переписана оттуда, «до» и «после» сверяются по суммам.
SHAPKA_ROW = {
    'file': PAGE,
    'before': '6052cac21db2f55a705b7abbe279ae36f88c7d712a68851cc57ed5a0c1cc46f0',
    'after': '2ecd5bc7a682ae19aaddf8e81bb7c7cc4bcbb5fb85260bb1badfb1ab6203272f',
    'replace': [['app.min.js?v=20261117zagolovok', 'app.min.js?v=20261117shapka', 1],
                ['style.css?v=20261117zagolovok', 'style.css?v=20261117shapka', 1]],
}
OTHERS = []
zp = ROOT / 'tools/deploy/zagolovok-2026-11-13/deploy_payload.json'
if zp.exists():
    OTHERS += [('zagolovok-2026-11-13', r) for r in json.loads(zp.read_text(encoding='utf-8'))['files'] if r['file'] == PAGE]
sp = ROOT / 'tools/deploy/shapka-2026-11-17/deploy_payload.json'
srow = [r for r in json.loads(sp.read_text(encoding='utf-8'))['files'] if r['file'] == PAGE] if sp.exists() else []
assert not srow or {k: srow[0][k] for k in SHAPKA_ROW} == SHAPKA_ROW, 'shapka: строка в репозитории не та, что на сервере'
OTHERS.append(('shapka-2026-11-17', SHAPKA_ROW))
for oname, orow in OTHERS:
    if orow['before'] != sha(body):
        print('%s: страница на сайте не в виде «до» этого пакета (%s…) — второй вид от него не нужен' % (oname, sha(body)[:8]))
        continue
    assert len(variants) == 1, 'второй исходный вид уже есть'
    oold = old
    for a, b, c in orow['replace']:
        assert oold.count(a) == c and '?v=' in a and '?v=' in b, '%s: %s' % (oname, a)
        oold = oold.replace(a, b)
    assert sha(oold.encode('utf-8')) == orow['after'], '%s: сумма после не совпала' % oname
    onew = patched(oold)
    variants.append([orow['after'], sha(onew.encode('utf-8'))])
    vnames.append('after ' + oname)
    short = oname.split('-')[0]
    for folder, content in (('backup-after-' + short, oold), ('pkg-after-' + short, onew)):
        f = OUT / folder / PAGE
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content.encode('utf-8'))
    print('%s ещё не выложен: второй исходный вид страницы %s… → %s…' % (oname, variants[1][0][:8], variants[1][1][:8]))
# вне блока (figure, стили страницы, скрипт страницы) — байт в байт
fo = re.search(r'<figure class="v-duct" id="vduct".*?</figure>', old, re.S)
fn = re.search(r'<figure class="v-duct" id="vduct".*?</figure>', new, re.S)
assert old[:old.index('<style>')] == new[:new.index('<style>')], 'изменилось начало страницы до <style>'
so, sn = old.index('</style>', old.index('<style>')), new.index('</style>', new.index('<style>'))
assert old[so:fo.start()] == new[sn:fn.start()], 'изменилось между стилями и блоком'
jo, jn = old.index(kam.JS_END), new.index(kam.JS_END)
assert old[jo:] == new[jn:], 'изменилось после скрипта блока'
assert '<?php' not in new

rows = []
for rel in IMAGES:
    data = (ROOT / rel).read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP', rel
    st, _ = live.get(live.SITE + '/' + rel, tries=4)
    assert st == 404, '%s уже есть на сайте (HTTP %s)' % (rel, st)
    rows.append({'file': rel, 'before': None, 'after': sha(data),
                 'content_b64': base64.b64encode(data).decode('ascii')})
    f = OUT / 'pkg' / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)
result = new.encode('utf-8')
for folder, content in (('backup', body), ('pkg', result)):
    f = OUT / folder / PAGE
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(content)
rows.append({'file': PAGE, 'variants': variants, 'variant_names': vnames, 'replace': [[a, b, 1] for a, b in reps]})

payload = {'name': NAME, 'images': len(IMAGES), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (b, a, r['file']) for r in rows
                                          for b, a in (r.get('variants') or [['-' * 64, r['after']]])), encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_kamera.py'), str(OUT / 'publish_kamera.py'))
# Разовый запуск заданием «Crontab» панели Timeweb (SSH-консоль из облака недоступна, как 15–17.11.2026).
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_kamera.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_kamera.py --check &&
  python3 publish_kamera.py --publish &&
  python3 publish_kamera.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_kamera.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    for b, a in (r.get('variants') or [['новый', r['after']]]):
        print('OK %s: %s → %s…' % (r['file'], b[:8], a[:8]))
print('Готово: 9 кадров и страница (%d замен, %d → %d байт); счётчики и контакты — без нарушений, независимость — '
      'без нарушений. Пакет: %s' % (len(reps), len(body), len(result), OUT))
