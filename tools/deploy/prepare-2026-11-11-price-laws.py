#!/usr/bin/env python3
"""Единые цены (пест-контроль от 3 900 ₽, дератизация/дезинсекция/дезинфекция от 3 500 ₽) для Timeweb.

Правит только свежие копии живых index.php (backup/<page>/index.php): tools/site/price_laws.patch + снятие строки
минимальной стоимости на дезинфекции (tools/site/price_block.patch). В пакет попадают только изменённые страницы.
Проверки: закон о счётчиках до и после, обычные скрипты, стили и tel:/mailto: байт в байт, без цифр и слов
«м²/обработку» страница не отличается ничем, кроме строки .pr-min.
Запуск: python3 tools/deploy/prepare-2026-11-11-price-laws.py <папка с backup/ и pages.txt>
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import tracking_laws  # noqa: E402
import price_block  # noqa: E402
import price_laws  # noqa: E402

SCRIPT = r'<script(?![^>]*ld\+json)\b.*?</script>'
STYLE = r'<style\b.*?</style>'
CONTACT = r'<a\b[^>]*href="(?:tel:|mailto:)[^"]*"[^>]*>.*?</a>'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def norm(s):
    s = re.sub(r'\n    <p class="d-note pr-min"[^>]*>.*?</p>', '', s)
    return re.sub(r'(?:\d|м²|обработку|[ \u00a0]|&nbsp;)+', ' ', s)


def main():
    work = pathlib.Path(sys.argv[1]).resolve()
    pages = (work / 'pages.txt').read_text(encoding='utf-8').split('\n')[:-1]
    report, manifest = [], []
    for p in pages:
        original = (work / 'backup' / p / 'index.php').read_bytes()
        text = original.decode('utf-8')
        cnt = p not in ('privacy/', 'soglasie/')
        assert not tracking_laws.check_page(text, counters=cnt), p + ': живая страница нарушает закон о счётчиках'
        result = price_laws.patch(text, p)
        if 'class="d-note pr-min"' in result:
            result = price_block.patch(result, p)  # снимает строку на дезинфекции, остальное не меняет
        if result == text:
            continue
        assert not tracking_laws.check_page(result, counters=cnt), p + ': правка нарушает закон о счётчиках'
        for tag in (SCRIPT, STYLE, CONTACT):
            assert re.findall(tag, text, re.S) == re.findall(tag, result, re.S), p + ': изменилось ' + tag
        assert norm(text) == norm(result), p + ': изменения вне цен'
        out = work / 'pkg' / p / 'index.php'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(result.encode('utf-8'))
        manifest.append(f'{sha(original)}  {sha(out.read_bytes())}  {p}index.php')
        report.append({'page': p, 'before': sha(original), 'after': sha(out.read_bytes()),
                       '3900': len(re.findall(r'3(?:[ \u00a0]|&nbsp;)?900', result)) - len(re.findall(r'3(?:[ \u00a0]|&nbsp;)?900', text))})
    (work / 'MANIFEST.txt').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
    (work / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    for r in report:
        print(r['page'], '+3 900:', r['3900'])
    print('изменено страниц:', len(report))


if __name__ == '__main__':
    main()
