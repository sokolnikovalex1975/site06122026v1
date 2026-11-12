#!/usr/bin/env python3
"""Метка «Вы здесь» — зелёная на всех страницах (решение владельца 13.11.2026).

    python3 tools/site/here_green.py            # правит страницы репозитория
    python3 tools/site/here_green.py --check    # только проверка

Запрос владельца: на главной плитка «Пест-контроль по системе IPM» получила зелёную метку «Вы здесь»; «это делай!» —
такая же зелёная метка везде: в общем прайсе (.pr-here, tools/site/price_block.py) и в каталоге «Все услуги Центра»
(.vu-here, tools/site/services_block.py). Меняются только эти CSS-правила внутри <style id="pr-st"> и <style id="vu-st">;
разметка, тексты, счётчики, телефон и почта не трогаются. Генераторы содержат уже новые правила, поэтому полная сборка
даёт тот же результат; скрипт нужен для точечной правки готовых страниц (и пакета для Timeweb). Повторный запуск
ничего не меняет.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
GRN = '#05df72'
DOT = ('{content:"";flex:none;width:7px;height:7px;border-radius:50%;background:' + GRN
       + ';box-shadow:0 0 0 3px rgba(5,223,114,.2)}')
PILL = ('display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:500;letter-spacing:.06em;'
        'text-transform:uppercase;color:' + GRN + ';border:1px solid rgba(5,223,114,.45);'
        'background:rgba(5,223,114,.1);border-radius:20px;padding:4px 10px 4px 8px;white-space:nowrap')
RULES = [  # прежнее правило → новое
    ('.pr-here{flex:none;font-size:11px;letter-spacing:.04em;text-transform:none;color:var(--acc);'
     'border:1px solid rgba(124,134,255,.4);border-radius:20px;padding:4px 10px}',
     '.pr-here{flex:none;' + PILL + '}.pr-here::before' + DOT),
    ('.vu-here{align-self:center;font-size:11px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;'
     'color:#a5abff;white-space:nowrap}',
     '.vu-here{align-self:center;' + PILL + '}.vu-here::before' + DOT),
]


def patch(s):
    for old, new in RULES:
        s = s.replace(old, new)
    return s


def pages():
    for p in sorted(ROOT.rglob('index.html')):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(('tools/', 'vendor/', 'node_modules/', 'dist/')):
            yield p


def main():
    check = '--check' in sys.argv[1:]
    changed, left = [], []
    for p in pages():
        s = p.read_text(encoding='utf-8')
        if any(old in s for old, _ in RULES):
            left.append(p)
            if not check:
                p.write_text(patch(s), encoding='utf-8')
                changed.append(p)
    if check:
        print('here_green: старая сиреневая метка на страницах:', len(left))
        sys.exit(1 if left else 0)
    print('here_green: зелёная метка «Вы здесь» — изменено страниц:', len(changed))


if __name__ == '__main__':
    main()
