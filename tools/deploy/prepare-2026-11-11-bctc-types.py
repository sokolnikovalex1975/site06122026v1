#!/usr/bin/env python3
"""Отдельное обновление: пять типов объекта в send.php и форме отраслевой страницы.

Запуск на Mac в папке выкладки с live/send.php и live/<SLUG>/index.php:
  python3 prepare.py
Рабочий send.php не переносить в репозиторий: он содержит SMTP-пароль и адрес получателя.
Меняется только allowedTypes, все остальные байты обработчика сохраняются.
"""
import hashlib
import pathlib
import re
import sys

SLUG = 'biznes-tsentry-torgovye-tsentry-predpriyatiya'
TYPES = [
    'Бизнес-центр или офисное здание',
    'Офис арендатора',
    'Торговый центр',
    'Промышленное предприятие',
    'Несколько объектов',
]
OLD_COMMENT = '   Обработчик заявок принимает фиксированный список типов, поэтому серверу в поле type уходит «Другое», а выбранный вид объекта — первой строкой сообщения */'
NEW_COMMENT = '   С 11.11.2026 пять видов объекта добавлены в send.php: выбранный вид передаётся в type и дублируется в сообщении */'
EXPECTED = {
    'send.php': '92653f3fd35caae487180246be23e0275dead16f18ccfb29b5dfe52d60fd035c',
    SLUG + '/index.php': '4dae3f06889a3c683a29d4feecb5d2cb09a3d3caf6434de27a782fef2816ec97',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def handler(data):
    s = data.decode('utf-8')
    m = re.search(r'\$allowedTypes\s*=\s*\[.*?\];', s, re.S)
    assert m and s.count(m[0]) == 1
    old = m[0]
    anchor = "    'Другое',"
    assert old.count(anchor) == 1
    assert not any("'" + t + "'" in old for t in TYPES)
    addition = ''.join("    '" + t + "',\n" for t in TYPES)
    new = old.replace(anchor, addition + anchor)
    result = s[:m.start()] + new + s[m.end():]
    assert result.replace(new, old, 1) == s
    return result.encode('utf-8')


def page(data):
    s = data.decode('utf-8')
    old = s
    for t in TYPES:
        # Typography changes visible text only. The value attribute must have normal spaces.
        visible = t.replace('или ', 'или\u00a0')
        a = '<option value="Другое">' + visible + '</option>'
        b = '<option value="' + t + '">' + visible + '</option>'
        assert s.count(a) == 1, t
        s = s.replace(a, b, 1)
    assert s.count(OLD_COMMENT) == 1
    s = s.replace(OLD_COMMENT, NEW_COMMENT, 1)
    block = r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->'
    assert re.findall(block, s, re.S) == re.findall(block, old, re.S)
    reverse = s.replace(NEW_COMMENT, OLD_COMMENT, 1)
    for t in TYPES:
        reverse = reverse.replace('value="' + t + '"', 'value="Другое"', 1)
    assert reverse == old
    return s.encode('utf-8')


def main():
    d = pathlib.Path.cwd()
    order = ['send.php', SLUG + '/index.php']  # compatible server first, then client
    funcs = [handler, page]
    manifest, before = [], []
    for rel, patch in zip(order, funcs):
        original = (d / 'live' / rel).read_bytes()
        assert sha(original) == EXPECTED[rel], 'Live file changed: ' + rel
        updated = patch(original)
        target = d / 'pkg' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(updated)
        manifest.append(sha(updated) + '  ' + rel)
        before.append(sha(original) + '  ' + rel)
    (d / 'MANIFEST.sha256').write_text('\n'.join(manifest) + '\n')
    conf = (
        '# Отдельная выкладка 11.11.2026: пять типов объекта; SMTP и счётчики не меняются.\n'
        '# Рабочий send.php и backup.zip содержат секреты: хранить только на Mac, не в GitHub.\n'
        'NAME="pestcontrol-deploy-2026-11-11-bctc-types"\n'
        'BK="before-bctc-types_2026-11-11_ftp.zip"\n'
        'ORDER="' + '\n'.join(order) + '"\n'
        'REPLACED="' + ' '.join(order) + '"\n'
        'EXPECTED_BEFORE="' + '\n'.join(before) + '"\n'
    )
    (d / 'deploy.conf').write_text(conf)
    print('PREPARE OK: only 5 allowlist additions and 5 option values; SMTP/counters unchanged')
    print('\n'.join(manifest))


if __name__ == '__main__':
    main()
