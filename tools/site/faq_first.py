#!/usr/bin/env python3
"""Вопросы внизу страницы: при открытии страницы развёрнут только первый вопрос (решение владельца 13.11.2026).

    python3 tools/site/faq_first.py                        # правит страницы репозитория
    python3 tools/site/faq_first.py --check                # только проверка страниц репозитория
    python3 tools/site/faq_first.py --check-prod <файлы>   # проверка готовых index.php пакета для Timeweb

Запрос владельца 13.11.2026: «Сразу развёрнуты вопросы в самом низу страницы… должен быть развёрнут только первый
вопрос; все остальные должны быть свёрнуты». На семи страницах генераторы ставили всем вопросам класс open и
aria-expanded="true" (так ответы «проще прочитать роботу и ИИ-ассистентам»). Ответы и разметка FAQPage остаются
в коде страницы, роботы их читают и в свёрнутом виде.

Что делает скрипт: в блоке вопросов у всех вопросов, кроме первого, убирает класс open и ставит
aria-expanded="false". Первый вопрос не трогается — его и так открывает app.js при загрузке страницы
(«firstQa»), на страницах с заранее открытыми ответами он открыт и в разметке. Тексты, ссылки, стили, скрипты,
счётчики, телефон и почта не меняются. Повторный запуск ничего не меняет.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# карточка вопроса: <div class="card qa …"> и сразу за ней кнопка с aria-expanded
QA = re.compile(r'<div class="(?P<cls>[^"]*)">(?P<sp>\s*)<button (?P<pre>[^>]*?)aria-expanded="(?P<exp>true|false)"')


def is_qa(cls):
    tokens = cls.split()
    return 'card' in tokens and 'qa' in tokens


def items(s):
    return [m for m in QA.finditer(s) if is_qa(m.group('cls'))]


def extra_open(s):
    """Номера вопросов (с 1), которые открыты при загрузке, кроме первого."""
    bad = []
    for n, m in enumerate(items(s), 1):
        if n > 1 and ('open' in m.group('cls').split() or m.group('exp') == 'true'):
            bad.append(n)
    return bad


def patch(s):
    out, last = [], 0
    for n, m in enumerate(items(s), 1):
        if n == 1:
            continue
        cls = ' '.join(t for t in m.group('cls').split() if t != 'open')
        new = f'<div class="{cls}">{m.group("sp")}<button {m.group("pre")}aria-expanded="false"'
        out.append(s[last:m.start()])
        out.append(new)
        last = m.end()
    out.append(s[last:])
    return ''.join(out)


def pages():
    for p in sorted(ROOT.rglob('index.html')):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(('tools/', 'vendor/', 'node_modules/', 'dist/')):
            yield p


def main():
    args = sys.argv[1:]
    if args[:1] == ['--check-prod']:
        files = [pathlib.Path(a) for a in args[1:]]
        bad = 0
        for f in files:
            e = extra_open(f.read_text(encoding='utf-8'))
            if e:
                bad += 1
                print(f'faq_first: {f}: открыты при загрузке вопросы {e}')
        print(f'faq_first --check-prod: файлов {len(files)}, с лишними открытыми вопросами: {bad}')
        sys.exit(1 if bad else 0)
    check = '--check' in args
    changed = []
    for p in pages():
        s = p.read_text(encoding='utf-8')
        e = extra_open(s)
        if not e:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if check:
            print(f'faq_first: {rel}: открыты при загрузке вопросы {e}')
        else:
            p.write_text(patch(s), encoding='utf-8')
        changed.append(rel)
    if check:
        print('faq_first: страниц, где при загрузке открыт не только первый вопрос:', len(changed))
        sys.exit(1 if changed else 0)
    print('faq_first: развёрнут только первый вопрос — изменено страниц:', len(changed))
    for rel in changed:
        print('  ', rel)


if __name__ == '__main__':
    main()
