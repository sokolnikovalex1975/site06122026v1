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
13.11.2026 владелец решил убрать с сайта мессенджеры и строку «Адрес склада» (tools/site/no_messengers.py): ссылки
Telegram и MAX, общие с другим проектом, с этого дня — нарушение на страницах и в пакетах выкладки; в исходниках
генераторов и документах репозитория — предупреждение (со страниц их убирает сборка).

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
    '0LDQutC+0Lkg0LbQtSDQvdCwINC00YDRg9Cz0L7QvCDQv9GA0L7QtdC60YLQtSI6ICJJQ1d5Y1F4Nm0zTlNCZTNXbENlREFkQUtNVG1OaE1IQyJ9LCAi'
    'c2hhcmVkX3JlIjogeyLQsNC00YDQtdGBLCDRgtCw0LrQvtC5INC20LUg0L3QsCDQtNGA0YPQs9C+0Lwg0L/RgNC+0LXQutGC0LUgKDIt0Lkg0KXQvtGA'
    '0L7RiNGR0LLRgdC60LjQuSDQv9GA0L7QtdC30LQsIDcpIjogItGF0L7RgNC+0Yhb0LXRkV3QstGB0LpcXHcqXFxzKyg/OtC/0YDQvtC10LfQtHzQv9GA'
    'LdC0KXzQv9GALdC0XFxzK9GF0L7RgNC+0Yhb0LXRkV3QstGB0Lp8Mi0/0LlcXHMr0YXQvtGA0L7RiFvQtdGRXdCy0YHQuiJ9LCAicmVtb3ZlZCI6IHsi'
    '0YHRgdGL0LvQutCwIFRlbGVncmFtICjRg9Cx0YDQsNC90LAg0YEg0YHQsNC50YLQsCDQv9C+INGA0LXRiNC10L3QuNGOINCy0LvQsNC00LXQu9GM0YbQ'
    'sCAxMy4xMS4yMDI2KSI6ICJ0Lm1lL2NlbnRyX2RlemluZmVjdGlvbiIsICLRgdGB0YvQu9C60LAgTUFYICjRg9Cx0YDQsNC90LAg0YEg0YHQsNC50YLQ'
    'sCDQv9C+INGA0LXRiNC10L3QuNGOINCy0LvQsNC00LXQu9GM0YbQsCAxMy4xMS4yMDI2KSI6ICJtYXgucnUvdS9mOWxob2RkMGNvaWxpdXhma3Q0a21m'
    'cDg4bGQ4bjR0YXJiaXRjdjdyaTF4bWw1YzRvMzlxZnNkYnh1YyJ9fQ==').decode('utf-8'))
TEXT_EXT = {'.html', '.htm', '.php', '.txt', '.xml', '.json', '.js', '.mjs', '.css', '.md', '.py', '.sh', '.svg', '.csv',
            '.htaccess', ''}
SKIP_DIRS = {'.git', 'vendor', 'dist', 'node_modules', '__pycache__'}


def violations(s, removed_hard=True):
    """Жёсткие нарушения: признаки другого проекта в тексте.

    removed_hard — ссылки, убранные с сайта по решению владельца (Telegram и MAX, 13.11.2026), тоже нарушение.
    Для исходников генераторов и документов репозитория (не страниц) — False: там они только предупреждение,
    со страниц их убирает tools/site/no_messengers.py при сборке.
    """
    low = s.lower()
    out = []
    for i, k in enumerate(_CFG['hard'], 1):
        if k in low:
            out.append(f'признак другого проекта №{i} ({low.count(k)} раз)')
    if removed_hard:
        out += [f'{name} ({low.count(k)} раз)' for name, k in _CFG['removed'].items() if k in low]
    digits = re.sub(r'\D', '', s)
    for i, k in enumerate(_CFG['hard_digits'], 1):
        if k in digits:
            out.append(f'телефон другого проекта №{i}')
    return out


def shared(s, removed=False):
    """Общие с другим проектом идентификаторы (ждут решения владельца): предупреждение.

    removed — добавить ссылки, убранные с сайта (для исходников и документов репозитория, где они не нарушение).
    """
    low = s.lower()
    out = [name for name, k in _CFG['shared'].items() if k.lower() in low]
    if removed:
        out += [name + ' — в исходниках, со страниц убирается при сборке' for name, k in _CFG['removed'].items()
                if k in low]
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
        # файлы сайта (страницы, разметка, данные) — убранные ссылки тоже нарушение; исходники генераторов
        # (tools/) и документы (.md, .py) — только предупреждение: со страниц их убирает no_messengers.py
        site_file = base is None or (not rel.startswith('tools/') and not rel.endswith(('.md', '.py', '.sh')))
        bad = violations(s, removed_hard=site_file) + _name_violation(rel)
        if bad:
            hard += 1
            print('НАРУШЕНИЕ:', rel, '—', '; '.join(bad))
        for w in shared(s, removed=not site_file):
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


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: D401 — переадресацию не выполняем, нужен сам ответ
        return None


def _status_noredirect(url):
    opener = urllib.request.build_opener(_NoRedirect)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (independence_law)'})
            with opener.open(req, timeout=30) as r:
                return r.status, r.headers.get('Location', '')
        except urllib.error.HTTPError as e:
            if e.code != 502:
                return e.code, e.headers.get('Location', '') if e.headers else ''
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3)
    return 0, ''


def check_removed_paths():
    """Служебные адреса другого проекта на сайте должны отвечать 404 (без переадресаций)."""
    word = _CFG['hard'][0]
    hard = 0
    for path in (f'/scripts-{word}/', f'/scripts-{word}', f'/scripts-{word}/index.php'):
        code, loc = _status_noredirect(SITE + path)
        if code == 404:
            continue
        if code == 0:
            print('не открылась:', SITE + path, code)
            continue
        hard += 1
        print('НАРУШЕНИЕ: служебный адрес другого проекта отвечает', code, SITE + path, loc)
    return hard


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
    hard += check_removed_paths()
    print('проверено адресов:', len(urls) + 3)
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
