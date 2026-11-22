#!/usr/bin/env python3
"""Страница «Дезинфекция автотранспорта» (/dezinfektsiya/avtotransport/): пакет для Timeweb (23.11.2026).

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-23-avto-before.py <сборка 7a506af> <сборка 17401bc> /tmp/A_dist
    python3 tools/deploy/prepare-2026-11-23-avto.py /tmp/A_dist <новая папка пакета>
(сборка «до» — dist/timeweb без правок автотранспорта, см. prepare-2026-11-23-avto-before.py)

Команды владельца: 20.11.2026 «Выложи страницу дезинфекции автотранспорта на Timeweb», 23.11.2026 «Выложи вариант 6
на Timeweb» (страница — коммиты 45fe06e и 17401bc, фото первого экрана — вариант 6 от 22.11.2026). Рабочий сайт отличается от сборки репозитория (его меняли пакетами), поэтому:
  * новые файлы (12): страница index.php, образец и бланк акта в PDF, 9 картинок — содержимое в пакете; у страницы
    метки ?v= файлов style.css и app.min.js — как на рабочем сайте;
  * 43 страницы (меню, «Все услуги», «Смотрите также» и ссылки на «Дезинфекции» и «Складах») — снимаются с рабочего
    сайта по HTTPS, правка — точные замены, вычисленные как разница сборок до (/tmp/A_dist) и после (dist/timeweb):
    каждая замена однозначна и в сборке, и на рабочем сайте, а те же замены на сборке «до» дают ровно сборку «после»;
  * search-index.json — индекс рабочего сайта + записи новой страницы (остальные записи не меняются);
  * sitemap.xml — карта рабочего сайта + адрес новой страницы; дата изменения «Дезинфекции» и «Складов» — сегодня.
Проверки: tracking_laws (Метрика 113675622, UIS, Radist, телефон, почта) до и после на каждой странице, закон
независимости — без нарушений, замены не затрагивают счётчики, скрипты, стили и формы.
"""
import base64
import datetime
import difflib
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

NAME = 'avto-2026-11-23'
PAGE = 'dezinfektsiya/avtotransport/index.php'
URL_NEW = 'dezinfektsiya/avtotransport/'
SITE_XML = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
TODAY = '2026-11-23'
BAD = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?', '<script', '<style', '<link',
       '<form', '<input', '<select', 'fetch(', 'xmlhttp')


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def _fine(a, b, base, out):
    """правки a→b в координатах P (base — начало a в P): общий край отбрасывается, длинный остаток сравнивается
    по тегам и тексту между ними, короткий — посимвольно (посимвольное сравнение длинных строк HTML зависало)"""
    k = 0
    n = min(len(a), len(b))
    while k < n and a[k] == b[k]:
        k += 1
    e = 0
    while e < n - k and a[len(a) - 1 - e] == b[len(b) - 1 - e]:
        e += 1
    a2, b2 = a[k:len(a) - e], b[k:len(b) - e]
    if not a2 and not b2:
        return
    base += k
    if len(a2) + len(b2) <= 4000:
        for t, x1, x2, y1, y2 in difflib.SequenceMatcher(None, a2, b2, autojunk=False).get_opcodes():
            if t != 'equal':
                out.append([base + x1, base + x2, b2[y1:y2]])
        return
    ta, tb = re.findall(r'<[^>]*>|[^<]+|<', a2), re.findall(r'<[^>]*>|[^<]+|<', b2)
    if len(ta) < 2 and len(tb) < 2:
        out.append([base, base + len(a2), b2])
        return
    oa, ob = [0], [0]
    for x in ta:
        oa.append(oa[-1] + len(x))
    for x in tb:
        ob.append(ob[-1] + len(x))
    for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if t == 'equal':
            continue
        if (i1, i2, j1, j2) == (0, len(ta), 0, len(tb)):  # общего нет — правка целиком (без бесконечной рекурсии)
            out.append([base, base + len(a2), b2])
        else:
            _fine(a2[oa[i1]:oa[i2]], b2[ob[j1]:ob[j2]], base + oa[i1], out)


def edits(P, N):
    """минимальные правки P→N: [начало, конец, вставка] в координатах P (строки, затем теги и символы; близкие склеены)"""
    pl, nl = P.splitlines(keepends=True), N.splitlines(keepends=True)
    po, no = [0], [0]
    for x in pl:
        po.append(po[-1] + len(x))
    for x in nl:
        no.append(no[-1] + len(x))
    out = []
    for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, pl, nl, autojunk=False).get_opcodes():
        if t != 'equal':
            _fine(P[po[i1]:po[i2]], N[no[j1]:no[j2]], po[i1], out)
    out.sort(key=lambda e: e[0])
    merged = []
    for e in out:
        if merged and e[0] - merged[-1][1] <= 60:
            m = merged[-1]
            m[2] = m[2] + P[m[1]:e[0]] + e[2]
            m[1] = e[1]
        else:
            merged.append(list(e))
    return merged


def replacements(P, N, L, rel):
    reps = []
    for i1, i2, ins in edits(P, N):
        c = 40
        while True:
            old = P[max(0, i1 - c):i2 + c]
            if P.count(old) == 1 and L.count(old) == 1:
                break
            c += 40
            assert c <= 4000, rel + ': нет однозначного места для правки: ' + P[i1 - 80:i2 + 80]
        reps.append([old, P[max(0, i1 - c):i1] + ins + P[i2:i2 + c], 1])
    return reps


def changed_part(old, new):
    k = 0
    while k < min(len(old), len(new)) and old[k] == new[k]:
        k += 1
    e = 0
    while e < min(len(old), len(new)) - k and old[-1 - e] == new[-1 - e]:
        e += 1
    return old[k:len(old) - e], new[k:len(new) - e]


def check_rep(rel, old, new):
    a, b = changed_part(old, new)
    for x in (a, b):
        low = x.lower()
        for t in BAD:
            assert t not in low, '%s: замена затрагивает %s' % (rel, t)
        for src in re.findall(r'src(?:set)?="([^"]*)"', x):
            assert re.fullmatch(r'(\.\./)*img/ig-avtotransport-(128|240)\.webp( \d+w, (\.\./)*img/ig-avtotransport-240\.webp \d+w)?',
                                src), '%s: картинка %s' % (rel, src)


def apply(s, reps):
    for old, new, c in reps:
        assert s.count(old) == c, old[:80]
        s = s.replace(old, new)
    return s


def main():
    live = module('check_live', 'tools/qa/check_live.py')
    A = pathlib.Path(sys.argv[1]).resolve()
    B = ROOT / 'dist' / 'timeweb'
    OUT = pathlib.Path(sys.argv[2]).resolve()
    assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
    fa = {str(p.relative_to(A)) for p in A.rglob('*') if p.is_file()}
    fb = {str(p.relative_to(B)) for p in B.rglob('*') if p.is_file()}
    new_files = sorted(fb - fa)
    assert not (fa - fb), 'в новой сборке пропали файлы: %s' % sorted(fa - fb)
    changed = [f for f in sorted(fa & fb) if (A / f).read_bytes() != (B / f).read_bytes()]
    pages = [f for f in changed if f.endswith('index.php')]
    assert set(changed) - set(pages) == {'search-index.json', 'sitemap.xml'}, changed
    assert PAGE in new_files and len(new_files) == 12, new_files

    def url(f):
        return live.SITE + (f[:-len('index.php')] if f.endswith('index.php') else f)

    def fetch(f):
        st, body = live.get(url(f), tries=8)  # Timeweb из облака иногда отвечает ложным 502
        return st, body

    rows = []
    # 1. новые файлы: на рабочем сайте их нет
    ref_status, ref = fetch('dezinsektsiya/index.php')
    assert ref_status == 200
    ref = ref.decode('utf-8')
    for f in new_files:
        st, _ = fetch(f)
        assert st == 404, '%s: на сайте уже есть (HTTP %s)' % (f, st)
        b = (B / f).read_bytes()
        if f == PAGE:
            s = b.decode('utf-8')
            for name in ('style.css', 'app.min.js'):
                v_live = re.search(r'(?:\.\./)*' + re.escape(name) + r'\?v=([0-9a-z]+)', ref).group(1)
                m = re.findall(r'((?:\.\./)*' + re.escape(name) + r'\?v=)([0-9a-z]+)', s)
                assert len(m) == 1, name
                s = s.replace(m[0][0] + m[0][1], m[0][0] + v_live)
            assert '<?php' not in s and '<?=' not in s
            bad = tracking_laws.check_page(s, counters=True)
            assert not bad, 'новая страница: %s' % bad
            assert independence_law.violations(s) == [], 'новая страница: закон независимости'
            b = s.encode('utf-8')
        rows.append({'file': f, 'kind': 'new', 'before': None, 'after': sha(b),
                     'content_b64': base64.b64encode(b).decode('ascii')})
        (OUT / 'pkg' / f).parent.mkdir(parents=True, exist_ok=True)
        (OUT / 'pkg' / f).write_bytes(b)
        print('NEW %s: %d байт' % (f, len(b)))
    # 2. страницы — точные замены от рабочего сайта
    for f in pages:
        st, body = fetch(f)
        assert st == 200, '%s: HTTP %s' % (f, st)
        L = body.decode('utf-8')
        P = (A / f).read_text(encoding='utf-8')
        N = (B / f).read_text(encoding='utf-8')
        assert '<?php' not in L and '<?=' not in L, f + ': PHP в файле'
        reps = replacements(P, N, L, f)
        assert apply(P, reps) == N, f + ': замены не дают сборку «после»'
        for old, new, c in reps:
            check_rep(f, old, new)
        R = apply(L, reps)
        counters = f not in ('privacy/index.php', 'soglasie/index.php')
        for label, s in (('до', L), ('после', R)):
            bad = tracking_laws.check_page(s, counters=counters)
            assert not bad, '%s (%s): %s' % (f, label, bad)
        assert independence_law.violations(R) == independence_law.violations(L) == [], f + ': закон независимости'
        k = 'dezinfektsiya/avtotransport/'
        assert R.count(k) - L.count(k) == N.count(k) - P.count(k) > 0, f
        for folder, content in (('backup', body), ('pkg', R.encode('utf-8'))):
            (OUT / folder / f).parent.mkdir(parents=True, exist_ok=True)
            (OUT / folder / f).write_bytes(content)
        rows.append({'file': f, 'kind': 'page', 'before': sha(body), 'after': sha(R.encode('utf-8')), 'replace': reps})
        print('PAGE %s: %d замен, %+d байт' % (f, len(reps), len(R.encode('utf-8')) - len(body)))
    # 3. индекс поиска: индекс рабочего сайта + записи новой страницы
    st, body = fetch('search-index.json')
    assert st == 200
    ix = json.loads(body)
    assert json.dumps(ix, ensure_ascii=False, separators=(',', ':')).encode('utf-8') == body
    rep = json.loads((B / 'search-index.json').read_text(encoding='utf-8'))
    pi_new = [i for i, p in enumerate(rep['p']) if p[1] == URL_NEW]
    assert len(pi_new) == 1 and not any(p[1] == URL_NEW for p in ix['p'])
    mine = [list(e) for e in rep['i'] if e[-1] == pi_new[0]]
    assert mine and all(URL_NEW in e[1] for e in mine)
    dz = [i for i, p in enumerate(ix['p']) if p[1] == 'dezinfektsiya/'][0]
    at = dz + 1
    for e in ix['i']:
        if isinstance(e[-1], int) and e[-1] >= at:
            e[-1] += 1
    ix['p'].insert(at, rep['p'][pi_new[0]])
    for e in mine:
        e[-1] = at
    last = max(i for i, e in enumerate(ix['i']) if e[-1] == dz)
    ix['i'][last + 1:last + 1] = mine
    new_ix = json.dumps(ix, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    rows.append({'file': 'search-index.json', 'kind': 'full', 'before': sha(body), 'after': sha(new_ix),
                 'content_b64': base64.b64encode(new_ix).decode('ascii')})
    for folder, content in (('backup', body), ('pkg', new_ix)):
        (OUT / folder / 'search-index.json').write_bytes(content)
    print('INDEX: +%d записей (%d → %d)' % (len(mine), len(ix['i']) - len(mine), len(ix['i'])))
    # 4. карта сайта
    st, body = fetch('sitemap.xml')
    assert st == 200
    sm = body.decode('utf-8')
    assert URL_NEW not in sm
    blk = '  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n    <priority>%s</priority>\n  </url>\n'
    out = sm
    for u in ('dezinfektsiya/', 'sklady-i-logistika/'):
        m = re.findall(r'  <url>\n    <loc>' + re.escape(SITE_XML + u) + r'</loc>\n    <lastmod>([0-9-]+)</lastmod>\n'
                       r'    <priority>([0-9.]+)</priority>\n  </url>\n', out)
        assert len(m) == 1, u
        out = out.replace(blk % (SITE_XML, u, m[0][0], m[0][1]), blk % (SITE_XML, u, TODAY, m[0][1]))
        if u == 'dezinfektsiya/':
            out = out.replace(blk % (SITE_XML, u, TODAY, m[0][1]),
                              blk % (SITE_XML, u, TODAY, m[0][1]) + blk % (SITE_XML, URL_NEW, TODAY, '0.8'))
    assert out.count('<url>') == sm.count('<url>') + 1 and URL_NEW in out
    new_sm = out.encode('utf-8')
    rows.append({'file': 'sitemap.xml', 'kind': 'full', 'before': sha(body), 'after': sha(new_sm),
                 'content_b64': base64.b64encode(new_sm).decode('ascii')})
    for folder, content in (('backup', body), ('pkg', new_sm)):
        (OUT / folder / 'sitemap.xml').write_bytes(content)
    print('SITEMAP: %d → %d адресов' % (sm.count('<url>'), out.count('<url>')))

    payload = {'name': NAME, 'count': len(rows), 'files': rows}
    (OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file'])
                                              for r in rows), encoding='utf-8')
    shutil.copy2(str(ROOT / 'tools/deploy/publish_avto.py'), str(OUT / 'publish_avto.py'))
    run_once = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_avto.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_avto.py --check &&
  python3 publish_avto.py --publish &&
  python3 publish_avto.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_avto.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
    (OUT / 'run_once.sh').write_text(run_once, encoding='utf-8')
    (OUT / 'run_once.sh').chmod(0o755)
    print('Готово: %d файлов (новых %d, страниц %d, индекс и карта сайта). Пакет: %s'
          % (len(rows), len(new_files), len(pages), OUT))
    print('run_once.sh: ' + sha((OUT / 'run_once.sh').read_bytes()))


if __name__ == '__main__':
    main()
