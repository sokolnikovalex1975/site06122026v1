#!/usr/bin/env python3
"""Линия сканирования (.panel-scan) проходит весь блок до нижнего края (23.11.2026): точные замены для style.css,
встроенных стилей главной и версии style.css на страницах.

Замечание владельца 23.11.2026: «Анимированная горизонтальная фиолетовая линия, которая проходит через весь блок,
останавливается… Это не правильно. Нужно исправить и посмотреть, где ещё на сайте этот эффект тоже останавливается
раньше времени».

Было: слой высотой 120 px сдвигался от translateY(-130%) до translateY(520%) — это проценты своей высоты, линия
проходила 780 px и останавливалась в 744 px от верха блока (до конца цикла, 2,5 с). Блоки самопроверки (.panel.f-check)
выше 744 px — линия замирает внутри (автотранспорт, «Программа» и «Журнал пест-контроля» на компьютере, все 15 блоков
на планшете и телефоне); 624–744 px — у нижнего края остаётся полоса свечения. Блок на главной (aside.panel) — ниже 624 px.
Стало: слой во всю высоту блока (top:0; bottom:0), полоса 120 px — фоном у его нижнего края; сдвиг от
translateY(calc(-100% - 40px)) (линия и её свечение выше блока) до translateY(130px) (полоса целиком ниже блока) —
линия проходит блок любой высоты от верхнего края до нижнего и уходит за него. Время, задержка и повтор те же
(5,5 с, 2,4 с, бесконечно), «облегчённый режим» (.lowfx) и «уменьшить движение» по-прежнему её скрывают.
"""

OLD_V, NEW_V = '20261118klient', '20261123scan'

RULE_OLD = ('.panel-scan{position:absolute;left:0;right:0;top:0;height:120px;z-index:0;pointer-events:none;'
            'background:linear-gradient(180deg,transparent,rgba(124,134,255,.12) 85%,rgba(124,134,255,.55) 100%);'
            'transform:translateY(-130%);animation:scan 5.5s var(--ease-io) 2.4s infinite}')
RULE_NEW = ('.panel-scan{position:absolute;left:0;right:0;top:0;bottom:0;z-index:0;pointer-events:none;'
            'background:linear-gradient(180deg,transparent,rgba(124,134,255,.12) 85%,rgba(124,134,255,.55) 100%) '
            '0 100%/100% 120px no-repeat;transform:translateY(calc(-100% - 40px));'
            'animation:scan 5.5s var(--ease-io) 2.4s infinite}')
COMMENT = ('/* линия сканирования проходит блок любой высоты до нижнего края (23.11.2026): слой во всю высоту блока,'
           ' полоса 120 px — у его нижнего края */\n')
KF_OLD = '@keyframes scan{0%{transform:translateY(-130%)}55%{transform:translateY(520%)}100%{transform:translateY(520%)}}'
KF_NEW = ('@keyframes scan{0%{transform:translateY(calc(-100% - 40px))}55%{transform:translateY(130px)}'
          '100%{transform:translateY(130px)}}')
KF_OLD_MIN = '@keyframes scan{0%{transform:translateY(-130%)}55%{transform:translateY(520%)}to{transform:translateY(520%)}}'
KF_NEW_MIN = ('@keyframes scan{0%{transform:translateY(calc(-100% - 40px))}55%{transform:translateY(130px)}'
              'to{transform:translateY(130px)}}')

CSS_PAIRS = [(RULE_OLD, COMMENT + RULE_NEW), (KF_OLD, KF_NEW)]       # style.css (строки как в репозитории)
HOME_CSS_PAIRS = [(RULE_OLD, RULE_NEW), (KF_OLD_MIN, KF_NEW_MIN)]    # главная: встроенные стили (сжатые)
VERSION_PAIRS = [('style.css?v=' + OLD_V, 'style.css?v=' + NEW_V)]   # страницы со ссылкой на style.css


def _edits(s, pairs, what):
    out = []
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, '%s: «%s» найдено %d раз' % (what, a[:70], n)
        assert s.count(b) == 0 or b in a, '%s: новое уже есть' % what
        out.append([a, b, 1])
    return out


def style_edits(css):
    return _edits(css, CSS_PAIRS, 'style.css')


def page_edits(html, rel='страница'):
    """Главная — встроенные стили (ссылки на style.css у неё нет); остальные — только версия style.css."""
    if 'style.css?v=' not in html:
        assert rel in ('index.php', 'index.html'), rel + ': нет ссылки на style.css'
        return _edits(html, HOME_CSS_PAIRS, rel)
    assert '@keyframes scan{' not in html, rel + ': свои стили линии сканирования'
    return _edits(html, VERSION_PAIRS, rel)


def apply(s, edits):
    for a, b, c in edits:
        assert s.count(a) == c, a[:70]
        s = s.replace(a, b)
    return s


def revert(s, edits):
    for a, b, c in reversed(edits):
        assert s.count(b) == c, b[:70]
        s = s.replace(b, a)
    return s


def repo(root):
    """Те же правила в репозитории: style.css и встроенные стили главной (index.html). Версии ?v= в исходниках
    репозитория не меняются (как и при прошлых выкладках, на сайте своя метка версии)."""
    import pathlib
    root = pathlib.Path(root)
    changed = []
    for rel, fn in (('style.css', style_edits), ('index.html', lambda s: _edits(s, HOME_CSS_PAIRS, 'index.html'))):
        f = root / rel
        s = f.read_text(encoding='utf-8')
        if RULE_NEW in s:
            continue
        f.write_text(apply(s, fn(s)), encoding='utf-8')
        changed.append(rel)
    return changed


if __name__ == '__main__':
    import pathlib
    import sys
    print('изменено:', repo(pathlib.Path(__file__).resolve().parents[2]) or 'ничего (правка уже есть)', file=sys.stderr)
