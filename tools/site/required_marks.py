#!/usr/bin/env python3
"""Звёздочка у обязательных полей во всех формах заявки — правило владельца сайта для всех страниц.

    python3 tools/site/required_marks.py

Запрос владельца 10.11.2026: «Задание со звёздочками вдоль обязательных полей внеси во все формы всех страниц сайта.
Только это задание. А редизайн не делай».

Что делает правило (без редизайна: подписи полей на сайте скрыты, видимый текст поля — подсказка внутри него):
  • в формах заявки (<form ... data-form>) у полей с атрибутом required к подсказке добавляется « *»:
    «Ваше имя *», «+7 (___) ___-__-__ *»;
  • у обязательного списка (тип или вид объекта — сфера деятельности) « *» добавляется к первому пункту-подсказке:
    «Тип объекта *»;
  • скрытая подпись для экранных дикторов не меняется — они и так объявляют поле обязательным по атрибуту required.
Дополнение владельца: тип объекта обязателен во всех формах. Вместо скрытого фиксированного типа добавляется
обычный список после телефона. На отраслевых страницах тип автоматически выбран по отрасли (последнее указание
владельца); на остальных страницах выбор пустой. Проверка type уже есть в общем JS и send.php.
Опросный лист на /razrabotka-ppk/ (в <template>, без data-form) не трогается — звёздочки там уже есть в подписях.

Скрипт идемпотентен. Запускается из tools/site/build_site.py после hero_fold.py; та же функция apply() используется
для точечной правки страниц, взятых с сайта.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit'}
MARK = ' *'

FORM_RE = re.compile(r'<form\b[^>]*\bdata-form\b[^>]*>.*?</form>', re.S)
FIELD_RE = re.compile(r'<input\b[^>]*>|<select\b[^>]*>.*?</select>', re.S)
REQ_RE = re.compile(r'\srequired(?=[\s>/=])')
PH_RE = re.compile(r'(\splaceholder=")([^"]*)(")')
OPT_RE = re.compile(r'(<option\b[^>]*\bvalue=""[^>]*>)([^<]*)(</option>)')
TYPE_HIDDEN_RE = re.compile(r'<div class="field" hidden><input type="hidden" name="type" value="[^"]*"></div>')
TYPE_OPTIONS = (
    'Пищевое производство', 'Магазин или торговая сеть', 'Ресторан или кафе',
    'Склад, логистика', 'Фармацевтическое производство', 'Гостиница', 'Другое',
)
INDUSTRY_TYPES = {
    'pishchevoe-proizvodstvo': 'Пищевое производство',
    'magaziny-i-torgovye-seti': 'Магазин или торговая сеть',
    'restorany-i-kafe': 'Ресторан или кафе',
    'sklady-i-logistika': 'Склад, логистика',
    'farmatsevticheskie-proizvodstva': 'Фармацевтическое производство',
    'gostinitsy': 'Гостиница',
}
TYPE_FIELD = (
    '<div class="field full"><label class="sr-only" for="f-type">Тип объекта</label>'
    '<select id="f-type" name="type" required><option value="" disabled selected>Тип объекта *</option>'
    + ''.join('<option>' + value + '</option>' for value in TYPE_OPTIONS)
    + '</select><small class="ferr">Выберите тип объекта</small></div>'
)


def _ensure_type(s):
    if TYPE_HIDDEN_RE.search(s):
        s = TYPE_HIDDEN_RE.sub('', s)
        s, count = re.subn(
            r'(<div class="field"><label\b[^>]*for="phone"[^>]*>.*?</div>)',
            lambda m: m.group(0) + '\n' + TYPE_FIELD, s, count=1, flags=re.S,
        )
        assert count == 1, 'Не найдена строка телефона для размещения типа объекта'
    return s


def _mark(text):
    return text if text.rstrip().endswith('*') else text.rstrip() + MARK


def _industry_default(s):
    canonical = re.search(r'<link\b[^>]*rel="canonical"[^>]*href="[^"]*/([^/"]+)/"', s)
    value = INDUSTRY_TYPES.get(canonical.group(1)) if canonical else None
    if not value:
        return s

    def select(m):
        t = re.sub(r'(<option\b[^>]*?)\sselected(?:="[^"]*")?', r'\1', m.group(0))
        found = [0]

        def option(o):
            attrs, text = o.group(1), o.group(2)
            explicit = re.search(r'\bvalue="([^"]*)"', attrs)
            option_value = explicit.group(1) if explicit else text
            if option_value != value:
                return o.group(0)
            found[0] += 1
            if not explicit:
                attrs += ' value="' + value + '"'
            return '<option' + attrs + ' selected>' + _mark(text) + '</option>'

        t = re.sub(r'<option([^>]*)>([^<]*)</option>', option, t)
        assert found[0] == 1, ('Не найден единственный тип отрасли', value)
        return t

    return re.sub(r'<select\b[^>]*name="type"[^>]*>.*?</select>', select, s, flags=re.S)


def _field(m, n):
    t = m.group(0)
    head = re.match(r'<(input|select)\b[^>]*>', t).group(0)
    if not REQ_RE.search(head) or re.search(r'type="(hidden|checkbox|radio)"', head):
        return t
    if t.startswith('<input'):
        new = PH_RE.sub(lambda p: p.group(1) + _mark(p.group(2)) + p.group(3), t, count=1)
    else:
        if re.search(r'\bname="type"', head):
            # Общая форма пустая; отраслевой выбор восстанавливается в _industry_default().
            t = re.sub(r'(<option\b[^>]*?)\sselected(?:="[^"]*")?', r'\1', t)
            t = re.sub(r'(<option\b[^>]*\bvalue=""[^>]*)(>)', r'\1 selected\2', t, count=1)
        new = OPT_RE.sub(lambda p: p.group(1) + _mark(p.group(2)) + p.group(3), t, count=1)
    if new != t:
        n[0] += 1
    return new


def apply(s):
    """Возвращает (новый текст, число отмеченных полей, число форм заявки)."""
    n = [0]
    forms = [0]

    def form(m):
        forms[0] += 1
        return FIELD_RE.sub(lambda f: _field(f, n), _ensure_type(m.group(0)))

    return _industry_default(FORM_RE.sub(form, s)), n[0], forms[0]


def main():
    total = 0
    for p in sorted(ROOT.rglob('index.html')):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        s = p.read_text(encoding='utf-8')
        new, n, forms = apply(s)
        if forms and new != s:
            p.write_text(new, encoding='utf-8')
        if forms:
            print(f'{p.relative_to(ROOT).parent}: форм {forms}, отмечено полей {n}')
            total += 1
    print('страниц с формами:', total)


if __name__ == '__main__':
    sys.exit(main())
