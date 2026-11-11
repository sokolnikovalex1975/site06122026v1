#!/usr/bin/env python3
"""Общий прайс на услуги для Timeweb: правит только свежие копии живых index.php (backup/<page>/index.php).

Меняет: блок прайса (главная #tseny, услуги и отрасли вместо #vse-uslugi), цены в каталоге «Один подрядчик»,
ссылку пункта «Цена» (#usloviya → #tseny), заголовок #usloviya на главной, строку минимальной стоимости на дезинфекции
и вентиляции, один <style id="pr-st">. Всё остальное, особенно счётчики (Метрика, UIS, Radist), скрипты, прочие стили,
телефон и почта, остаётся байт в байт — иначе сборка пакета останавливается.

Запуск: python3 tools/deploy/prepare-2026-11-11-price.py <рабочая папка с backup/ и pages.txt>
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

SCRIPT = r'<script\b.*?</script>'
STYLE = r'<style\b.*?</style>'
CONTACT = r'<a\b[^>]*href="(?:tel:|mailto:)[^"]*"[^>]*>.*?</a>'
PR_SEC = r'<section class="s s-pr[^"]*" id="[^"]*".*?</section>'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    work = pathlib.Path(sys.argv[1]).resolve()
    pages = (work / 'pages.txt').read_text(encoding='utf-8').split('\n')[:-1]
    report, manifest = [], []
    for p in pages:
        src = work / 'backup' / p / 'index.php'
        original = src.read_bytes()
        text = original.decode('utf-8')
        cnt = p not in ('privacy/', 'soglasie/')  # документы — без счётчиков по закону (tracking_laws.NO_COUNTERS)
        assert not tracking_laws.check_page(text, counters=cnt), p + ': живая страница уже нарушает закон о счётчиках'
        result = price_block.patch(text, p)
        if result == text:
            report.append({'page': p, 'changed': False})
            continue
        assert not tracking_laws.check_page(result, counters=cnt), p + ': правка нарушает закон о счётчиках'
        assert re.findall(SCRIPT, text, re.S) == re.findall(SCRIPT, result, re.S), p + ': изменились скрипты'
        assert re.findall(CONTACT, text, re.S) == re.findall(CONTACT, result, re.S), p + ': изменились телефон/почта'
        st_old = re.findall(STYLE, text, re.S)
        st_new = [x for x in re.findall(STYLE, result, re.S) if not x.startswith('<style id="pr-st">')]
        assert st_old == st_new, p + ': изменились прочие стили'
        head = result[:result.index('</head>')]
        if 'pr-st' in head:
            assert not re.search(r'<style id="pr-st">.*?</style></head>', result, re.S), p + ': стили вплотную к </head>'
        assert 'noindex' not in result or 'noindex' in text, p + ': появился noindex'
        assert 'github.io' not in result or 'github.io' in text, p + ': ссылка на превью'
        # блок прайса должен совпадать с проверенным в GitHub-превью
        repo = ROOT / p / 'index.html'
        if repo.exists():
            a = re.findall(PR_SEC, result, re.S)
            b = re.findall(PR_SEC, repo.read_text(encoding='utf-8'), re.S)
            assert a == b, p + ': блок прайса отличается от превью'
        # вне изменяемых мест — ни одного лишнего отличия
        strip = lambda s: re.sub(r'\s+', ' ', re.sub(PR_SEC + r'|<section class="s s-vu" id="vse-uslugi".*?</section>'
                                 r'|<style id="pr-st">.*?</style>|<p class="d-note pr-min".*?</p>'
                                 r'|<span class="vu-p">[^<]*</span>|#usloviya|#tseny'
                                 r'|<div class="eyebrow"[^>]*>(?:Цена|Примеры работ)</div>\s*<h2[^>]*>(?:Стоимость <em>под ваш объект</em>|Типовые задачи <em>наших клиентов</em>)</h2>\s*<p class="sub"[^>]*>.*?</p>', '', s, flags=re.S))
        assert strip(text) == strip(result), p + ': изменения вне согласованных мест'
        out = work / 'pkg' / p / 'index.php'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(result.encode('utf-8'))
        manifest.append(f'{sha(original)}  {sha(out.read_bytes())}  {p}index.php')
        report.append({'page': p, 'changed': True, 'before': sha(original), 'after': sha(out.read_bytes()),
                       'price_block': bool(re.search(PR_SEC, result, re.S)),
                       'menu_links': result.count('#tseny"'), 'left_usloviya_links': len(re.findall(r'href="[^"]*#usloviya"', result))})
    (work / 'MANIFEST.txt').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
    (work / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    ch = [r for r in report if r['changed']]
    print('изменено', len(ch), 'из', len(report), '; с прайсом', sum(r['price_block'] for r in ch))
    for r in report:
        if not r['changed'] or r['left_usloviya_links']:
            print('  внимание', r)


if __name__ == '__main__':
    main()
