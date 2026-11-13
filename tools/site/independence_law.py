#!/usr/bin/env python3
"""ЗАКОН ВЛАДЕЛЬЦА: независимость сайта (с 13.11.2026).

Владелец (Алексей Симонов), 13.11.2026: сайт пестконтроль-центр.рф и другой проект владельца — раздельные проекты,
«они не должны быть никак связаны, они не должны быть похожи. Это правило, это главная задача, это закон».
Закон стоит рядом с законом счётчиков (tools/site/tracking_laws.py). Нарушать нельзя. Если правка требует нарушения —
сначала спросить владельца и прямо назвать нарушаемый пункт.

Нельзя — на страницах, в разметке, llms.txt, robots.txt, sitemap.xml, в файлах и папках сайта на хостинге и в этом
репозитории:
  1. ссылки, переадресации и упоминания другого проекта: бренд, домены, поддомены, папки с его именем;
  2. его телефоны, почта, реквизиты, адреса, мессенджеры, коды счётчиков, колл-трекинга и виджетов;
  3. общие тексты, фото, логотипы, оформление и структура блоков. Новые тексты сверять с сайтом другого проекта:
     общие фразы из 5 слов и длиннее допустимы только в юридических формулировках;
  4. файлы и данные другого проекта в папке сайта на хостинге, общие программы и папки.
Пересечение поисковых запросов допустимо, пересечение содержания — нет.

Признаки другого проекта хранятся ниже в закодированном виде, чтобы не публиковать их в открытом репозитории.
Открытый список и решения владельца — в закрытых файлах проекта «СЕО Пестконтроль-центр» (seo-agent/rules/independence.md).
Жёсткие признаки останавливают сборку. Общие идентификаторы (сейчас одинаковые на обоих сайтах, ждут решения владельца)
выводятся предупреждением: новых таких совпадений не добавлять.

Использование:
    python3 tools/site/independence_law.py --check            # файлы репозитория (страницы, server/, llms.txt, документы)
    python3 tools/site/independence_law.py --check-prod F…    # готовые файлы выкладки (index.php и др.)
    python3 tools/site/independence_law.py --check-live       # рабочий сайт: адреса sitemap.xml, robots.txt, llms.txt
Из других скриптов: violations(s) — жёсткие нарушения; shared(s) — общие идентификаторы (предупреждение).
Код выхода 1, если есть жёсткие нарушения.
"""
import base64
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai'
_CFG = json.loads(base64.b64decode(
    'eyJoYXJkIjogWyJhZ2VyaXMiLCAi0LDQs9C10YDQuNGBIiwgInhuLS04MGFnZ20zYmgiLCAiNzcxNDQ2MjI0MyIsICIyNDE0ODU3MyJdLCAiaGFyZF9k'
    'aWdpdHMiOiBbIjQ5NTEwNDM2MDEiLCAiNDk1MTA0MzYwMiJdLCAic2hhcmVkIjogeyLQutC70Y7RhyDRgdCw0LnRgtCwIFVJUyAoQ29NYWdpYyksINGC'
    '0LDQutC+0Lkg0LbQtSDQvdCwINC00YDRg9Cz0L7QvCDQv9GA0L7QtdC60YLQtSI6ICJJQ1d5Y1F4Nm0zTlNCZTNXbENlREFkQUtNVG1OaE1IQyIsICJU'
    'ZWxlZ3JhbSwg0YLQsNC60L7QuSDQttC1INC90LAg0LTRgNGD0LPQvtC8INC/0YDQvtC10LrRgtC1IjogInQubWUvQ2VudHJfRGV6aW5mZWN0aW9uIiwg'
    'Ik1BWCwg0YLQsNC60L7QuSDQttC1INC90LAg0LTRgNGD0LPQvtC8INC/0YDQvtC10LrRgtC1IjogIm1heC5ydS91L2Y5TEhvZEQwY09JbElVWEZrdDRL'
    'TUZQODhsRDhuNFRBckJpVGNWN1JJMVhNTDVjNG8zOVFmc0RCWFVjIn0sICJzaGFyZWRfcmUiOiB7ItCw0LTRgNC10YEsINGC0LDQutC+0Lkg0LbQtSDQ'
    'vdCwINC00YDRg9Cz0L7QvCDQv9GA0L7QtdC60YLQtSAoMi3QuSDQpdC+0YDQvtGI0ZHQstGB0LrQuNC5INC/0YDQvtC10LfQtCwgNykiOiAi0YXQvtGA'
    '0L7RiFvQtdGRXdCy0YHQulxcdypcXHMrKD860L/RgNC+0LXQt9C0fNC/0YAt0LQpfNC/0YAt0LRcXHMr0YXQvtGA0L7RiFvQtdGRXdCy0YHQunwyLT/Q'
    'uVxccyvRhdC+0YDQvtGIW9C10ZFd0LLRgdC6In19').decode('utf-8'))
TEXT_EXT = {'.html', '.htm', '.php', '.txt', '.xml', '.json', '.js', '.mjs', '.css', '.md', '.py', '.sh', '.svg', '.csv',
            '.htaccess', ''}
SKIP_DIRS = {'.git', 'vendor', 'dist', 'node_modules', '__pycache__'}


def violations(s):
    """Жёсткие нарушения: признаки другого проекта в тексте."""
    low = s.lower()
    out = []
    for i, k in enumerate(_CFG['hard'], 1):
        if k in low:
            out.append(f'признак другого проекта №{i} ({low.count(k)} раз)')
    digits = re.sub(r'\D', '', s)
    for i, k in enumerate(_CFG['hard_digits'], 1):
        if k in digits:
            out.append(f'телефон другого проекта №{i}')
    return out


def shared(s):
    """Общие с другим проектом идентификаторы (ждут решения владельца): предупреждение."""
    low = s.lower()
    out = [name for name, k in _CFG['shared'].items() if k.lower() in low]
    out += [name for name, rx in _CFG['shared_re'].items() if re.search(rx, low)]
    return out


def _repo_files():
    me = pathlib.Path(__file__).resolve()
    for f in sorted(ROOT.rglob('*')):
        if not f.is_file() or f.resolve() == me or any(p in SKIP_DIRS for p in f.relative_to(ROOT).parts):
            continue
        if f.suffix.lower() in TEXT_EXT or f.name.startswith('.'):
            yield f


def _name_violation(rel):
    return [f'имя файла или папки: признак №{i}' for i, k in enumerate(_CFG['hard'], 1) if k in rel.lower()]


def check_files(files, base=None):
    hard, warn = 0, {}
    for f in files:
        rel = str(f.relative_to(base)) if base else str(f)
        try:
            s = pathlib.Path(f).read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        bad = violations(s) + _name_violation(rel)
        if bad:
            hard += 1
            print('НАРУШЕНИЕ:', rel, '—', '; '.join(bad))
        for w in shared(s):
            warn.setdefault(w, []).append(rel)
    for w, where in warn.items():
        print(f'предупреждение: {w} — {len(where)} файл(ов), например {where[0]}')
    return hard


def _get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (independence_law)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code != 502:
                return e.code, ''
        except Exception:  # noqa: BLE001 — сеть хостинга иногда отвечает с перебоями
            pass
        time.sleep(3)
    return 0, ''


def check_live():
    code, sm = _get(SITE + '/sitemap.xml')
    urls = re.findall(r'<loc>(.*?)</loc>', sm) + [SITE + '/robots.txt', SITE + '/llms.txt', SITE + '/sitemap.xml']
    hard, warn = 0, {}
    for u in urls:
        code, s = _get(u)
        if code != 200:
            print('не открылась:', u, code)
            continue
        bad = violations(s)
        if bad:
            hard += 1
            print('НАРУШЕНИЕ:', u, '—', '; '.join(bad))
        for w in shared(s):
            warn.setdefault(w, []).append(u)
    for w, where in warn.items():
        print(f'предупреждение: {w} — {len(where)} адрес(ов)')
    print('проверено адресов:', len(urls))
    return hard


def main(argv):
    if argv[:1] == ['--check-live']:
        hard = check_live()
    elif argv[:1] == ['--check-prod']:
        hard = check_files([pathlib.Path(a) for a in argv[1:]])
    else:
        hard = check_files(_repo_files(), base=ROOT)
    print('закон независимости:', 'нарушен' if hard else 'соблюдён')
    return 1 if hard else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
