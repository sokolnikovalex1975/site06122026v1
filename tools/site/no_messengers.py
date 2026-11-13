#!/usr/bin/env python3
"""На сайте нет мессенджеров и строки «Адрес склада» в подвале (решение владельца 13.11.2026).

    python3 tools/site/no_messengers.py            # правит страницы репозитория
    python3 tools/site/no_messengers.py --check    # только проверка (код 1, если что-то осталось)

Владелец (Алексей Симонов), 13.11.2026: «Убери строку «Адрес склада» из подвала» и «Нужно убрать полностью иконки
мессенджеров с сайта». Ссылки Telegram и MAX и адрес склада совпадали с другим проектом владельца — см. закон
независимости (tools/site/independence_law.py): ссылки Telegram и MAX теперь — жёсткое нарушение, сборка с ними
останавливается.

Что делает (шаг tools/site/build_site.py перед tracking_laws.py; patch() применим и к живым index.php с Timeweb):
  * убирает блоки <div class="msg">…</div> — значки Max и Telegram в шапке, у контактов перед формой и в подвале;
  * убирает плавающие кнопки <div class="fab">…</div> справа внизу;
  * убирает из подвала строку <p>Адрес склада: …</p> (строка с названием, ИНН, КПП и ОГРН остаётся);
  * в текстах, где посетителя звали в мессенджер, — почта: «напишите в мессенджер» → «напишите на почту» и т. п.
    (страницы и разметка FAQ, точные замены — TEXTS).
Код Radist в server/counters.html не меняется (закон счётчиков, tools/site/tracking_laws.py); без ссылок на
мессенджеры ему просто нечего размечать. Стили .msg и .fab остаются в CSS и ни на что не влияют.
Политика конфиденциальности и согласие (юридические тексты) не меняются. Повторный запуск ничего не меняет.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
NB = '\u00a0'
MSG = re.compile(r'^[ \t]*<div\b[^>]*\bclass="msg"[^>]*>.*?</div>[ \t]*\n', re.S | re.M)
FAB = re.compile(r'^[ \t]*<div\b[^>]*\bclass="fab"[^>]*>.*?</div>[ \t]*\n', re.S | re.M)
ADDR = re.compile(r'<p>Адрес склада:[^<]*</p>')
LINK = re.compile(r'<a\b[^>]*\bhref="https://(?:t\.me|max\.ru)/[^"]*"[^>]*>.*?</a>', re.S)
TEXTS = [  # было → стало (как на сайте, с неразрывными пробелами)
    ('Позвоните или напишите в' + NB + 'мессенджер.', 'Позвоните или напишите на' + NB + 'почту.'),
    ('Позвоните или напишите в мессенджер.', 'Позвоните или напишите на почту.'),
    ('Позвоните или напишите в мессенджер —', 'Позвоните или напишите на почту —'),
    ('Позвоните нам или' + NB + 'напишите в' + NB + 'Telegram / MAX.', 'Позвоните нам или' + NB + 'напишите на' + NB + 'почту.'),
    ('Позвоните нам или напишите в Telegram / MAX.', 'Позвоните нам или напишите на почту.'),
    ('По телефону, в мессенджере или через форму.', 'По телефону, по почте или через форму.'),
    ('По телефону, в' + NB + 'мессенджере или через форму.', 'По телефону, по' + NB + 'почте или через форму.'),
    ('сканы можно отправить почтой или' + NB + 'в' + NB + 'мессенджер.', 'сканы можно отправить почтой.'),
    ('сканы можно отправить почтой или в мессенджер.', 'сканы можно отправить почтой.'),
]


def _drop_block(m):
    block = m.group(0)
    inner = LINK.sub('', block)
    inner = re.sub(r'<div\b[^>]*\bclass="(?:msg|fab)"[^>]*>|</div>|\s', '', inner)
    assert inner == '', 'в блоке мессенджеров есть что-то кроме ссылок Telegram и MAX: ' + block[:120]
    assert LINK.search(block), 'блок без ссылок мессенджеров: ' + block[:120]
    return ''


def patch(s):
    s = MSG.sub(_drop_block, s)
    s = FAB.sub(_drop_block, s)
    s = ADDR.sub('', s)
    for old, new in TEXTS:
        s = s.replace(old, new)
    return s


def left(s):
    """Что осталось: ссылки мессенджеров, строка адреса склада, тексты из TEXTS."""
    out = []
    if LINK.search(s):
        out.append('ссылки Telegram / MAX: %d' % len(LINK.findall(s)))
    if ADDR.search(s):
        out.append('строка «Адрес склада»')
    out += ['текст: ' + old for old, _ in TEXTS if old in s]
    return out


def pages():
    for p in sorted(ROOT.rglob('*.html')):  # страницы сайта и превью на GitHub Pages (preview-*.html)
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(('tools/', 'vendor/', 'node_modules/', 'dist/', 'server/', '.git/')):
            yield p


def main():
    check = '--check' in sys.argv[1:]
    changed, bad = [], []
    for p in pages():
        s = p.read_text(encoding='utf-8')
        new = patch(s)
        assert patch(new) == new, '%s: повторный запуск меняет страницу' % p
        if new != s:
            if check:
                bad.append((p.relative_to(ROOT).as_posix(), left(s)))
            else:
                p.write_text(new, encoding='utf-8')
                changed.append(p)
    if check:
        for rel, what in bad:
            print('no_messengers:', rel, '—', '; '.join(what))
        print('no_messengers: страниц с мессенджерами или адресом склада:', len(bad))
        sys.exit(1 if bad else 0)
    print('no_messengers: мессенджеры и строка «Адрес склада» убраны — изменено страниц:', len(changed))


if __name__ == '__main__':
    main()
