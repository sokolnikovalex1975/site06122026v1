#!/usr/bin/env python3
"""ЗАКОН ВЛАДЕЛЬЦА: счётчики, колл-трекинг и разметка телефона и почты (с 11.11.2026).

Основание — замечания программиста от 11.11.2026. Владелец (Алексей Симонов) сделал их законом для всех правок сайта,
GitHub и выкладок на Timeweb: «Вот эти комментарии… они являются законом… когда ты хочешь нарушить их, обязательно спроси
меня, что ты нарушаешь этот закон». Нарушать пункты ниже нельзя. Если правка требует нарушения — сначала спросить
владельца и прямо назвать нарушаемый пункт.

  1. Яндекс Метрика, UIS (CoMagic) и Radist загружаются сразу вместе со страницей, официальными кодами, без «ленивой»
     загрузки (после касания, прокрутки, таймера, requestIdleCallback и т. п.). Иначе: если посетитель закрыл страницу
     раньше загрузки счётчика и ничего не коснулся, хита нет; показатель отказов и длительность визитов искажаются;
     Вебвизор пишет только с момента загрузки; первые визиты рекламных ботов не попадают в обучение рекламы.
     Места кодов (server/counters.html):
       • Метрика 113675622 — в <head> сразу после <meta name="viewport"> («как можно ближе к началу страницы»);
       • UIS — перед </head> (так требует UIS);
       • <noscript> Метрики — сразу после <body> (в <head> картинка внутри noscript недопустима);
       • Radist — в конце <body> (так требует Radist) + код заявки в ссылках Telegram и MAX.
  2. Подмена номера UIS проверяется отдельно после любых правок счётчиков и разметки телефона.
  3. Почта в HTML — без лишних тегов: <a href="mailto:b2b@pestcontrol-center.ru">b2b@pestcontrol-center.ru</a>
     (без <wbr>, <span> и т. п. внутри: из-за лишнего тега код CoMagic не может прочитать и подменить адрес).
  4. Телефон в HTML — без лишних знаков и тегов: <a href="tel:+74951043570">+7 (495) 104-35-70</a>, внутри ссылки только номер
     обычными пробелами (без &nbsp; / U+00A0, <span>, <i>, <svg>, без копии номера в aria-label или data-t). Значок телефона
     в шапке рисуется стилями (::before), а не тегом внутри ссылки. Номер не должен разрываться — white-space:nowrap в CSS.

Использование:
    python3 tools/site/tracking_laws.py                  # разметка телефона и почты на страницах репозитория (шаг build_site.py)
    python3 tools/site/tracking_laws.py --check          # проверка страниц репозитория (без счётчиков — они только на Timeweb)
    python3 tools/site/tracking_laws.py --check-prod F…  # проверка готовых index.php (dist/timeweb, pkg/, копии с сайта)
Из других скриптов: normalize_contacts(s), install_counters(s), check_page(s, counters=True) — build_prod.py,
tools/qa/check_live.py, сборщики пакетов выкладки tools/deploy/prepare-*.py.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
COUNTERS_FILE = ROOT / 'server' / 'counters.html'
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php', 'privacy/index.html', 'soglasie/index.html'}

TEL_A = re.compile(r'<a\b(?P<attrs>[^>]*?\bhref="tel:(?P<num>[^"]*)"[^>]*)>(?P<inner>.*?)</a>', re.S)
MAIL_A = re.compile(r'<a\b(?P<attrs>[^>]*?\bhref="mailto:(?P<addr>[^"?]*)[^"]*"[^>]*)>(?P<inner>.*?)</a>', re.S)
NBSP = ('&nbsp;', '&#160;', '&#xa0;', '&#xA0;', '\u00a0', '\u202f', '\u2007')
SP = r'(?:\s|&nbsp;|&#160;|&#xa0;|&#xA0;|\u00a0|\u202f|\u2007)+'
TEXT_PHONE = re.compile(r'\+7' + SP + r'\((\d{3})\)' + SP + r'(\d{3})-(\d{2})-(\d{2})')
BROKEN_MAIL = re.compile(r'@(?:\s*<[^>]+>)+\s*[\w.-]+\.\w{2,}')  # b2b@<wbr><span>pestcontrol-center.ru
DEFERRED = ('Yandex.Metrika counter + UIS + Radist', 'waitForTrackViewAndRun', 'setTimeout(load', "ev = ['pointerdown'",
            'requestIdleCallback(load', 'addEventListener(e, load')

# Значок телефона в шапке — стилями, а не тегом в ссылке (закон, п. 4). Иконка та же, что была тегом <svg> в <i>.
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' "
        "stroke-width='2'%3E%3Cpath d='M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 "
        "2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 "
        "2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z'/%3E%3C/svg%3E")
STYLE_ID = 'tel-plain'
STYLE = (
    '<style id="tel-plain">/* Закон владельца 11.11.2026 (tools/site/tracking_laws.py): в ссылке телефона только номер — '
    'значок шапки рисуется здесь, номер не разрывается */'
    '.phone{position:relative}'
    '.phone::before{content:"";flex:none;box-sizing:border-box;width:36px;height:36px;border-radius:50%;'
    'background:var(--acc2) url("' + ICON + '") 50%/15px 15px no-repeat;transition:transform .4s var(--ease)}'
    '.phone::after{content:"";position:absolute;left:0;top:50%;box-sizing:border-box;width:36px;height:36px;margin-top:-18px;'
    'border-radius:50%;border:1px solid var(--acc);animation:ring 2.4s var(--ease) infinite;pointer-events:none}'
    '.phone:hover::before{transform:rotate(-14deg) scale(1.06)}'
    '@media (max-width:760px){.phone{font-size:0;gap:0}.phone::before,.phone::after{width:44px;height:44px}.phone::after{margin-top:-22px}}'
    '@media (max-width:400px){.phone::before,.phone::after{width:40px;height:40px}.phone::after{margin-top:-20px}}'
    '@media (max-width:360px){.phone::before,.phone::after{width:38px;height:38px}.phone::after{margin-top:-19px}}'
    'a[href^="tel:"]{white-space:nowrap!important}'
    '</style>'
)
STYLE_RE = re.compile(r'<style id="tel-plain">.*?</style>\n?', re.S)


# ---------- разметка телефона и почты (закон, пп. 3–4) ----------

def plain(inner):
    """Текст внутри ссылки без тегов, неразрывных пробелов и сущностей."""
    t = re.sub(r'<svg\b.*?</svg>', '', inner, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    for n in NBSP:
        t = t.replace(n, ' ')
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def digits(s):
    d = re.sub(r'\D', '', s)
    return '7' + d[1:] if len(d) == 11 and d[0] == '8' else d


def phone_text(num):
    """+74951043570 → «+7 (495) 104-35-70» (обычные пробелы)."""
    d = digits(num)
    if len(d) != 11 or d[0] != '7':
        raise ValueError('номер в ссылке tel: не российский из 11 цифр: ' + num)
    return f'+7 ({d[1:4]}) {d[4:7]}-{d[7:9]}-{d[9:]}'


def _tel(m):
    text = plain(m.group('inner'))
    if not re.search(r'\d', text):  # «Позвонить» в нижней панели телефона: номера в тексте нет — ссылку UIS подменит по href
        return m.group(0)
    want = phone_text(m.group('num'))
    if digits(text) != digits(want):
        raise ValueError(f'текст ссылки «{text}» не совпадает с номером в href «{m.group("num")}»')
    attrs = re.sub(r'\s+(?:aria-label|title|data-t)="[^"]*\d{3}[^"]*"', '', m.group('attrs'))  # копии номера UIS не обновит
    return f'<a{attrs}>{want}</a>'


def _mail(m):
    addr, text = m.group('addr'), plain(m.group('inner'))
    if '@' not in text:
        return m.group(0)
    if text.lower() != addr.lower():
        raise ValueError(f'текст ссылки «{text}» не совпадает с адресом в href «{addr}»')
    return f'<a{m.group("attrs")}>{addr}</a>'


def normalize_contacts(s):
    """Телефон и почта по закону (пп. 3–4): внутри ссылок только номер / адрес, обычные пробелы. Повторный запуск ничего не меняет."""
    s = TEL_A.sub(_tel, s)
    s = MAIL_A.sub(_mail, s)
    s = TEXT_PHONE.sub(lambda m: f'+7 ({m[1]}) {m[2]}-{m[3]}-{m[4]}', s)  # номер в обычном тексте — тоже обычными пробелами
    s = STYLE_RE.sub('', s)
    if 'class="phone"' in s:
        assert s.count('</head>') == 1, 'нет </head>'
        head = s.index('</head>')
        close = s.rfind('<!-- UIS -->', 0, head)  # если код UIS уже стоит прямо перед </head>, стиль — перед ним (закон, п. 1)
        start = s.rfind('<!-- UIS -->', 0, close) if close > 0 else -1
        at = start if start >= 0 and s[close + len('<!-- UIS -->'):head].strip() == '' else head
        s = s[:at] + STYLE + '\n' + s[at:]
    return s


# ---------- счётчики (закон, п. 1) ----------

def counter_parts():
    """Части server/counters.html: metrika, uis, noscript, radist — байт в байт, как их вставлять на страницы."""
    c = COUNTERS_FILE.read_text(encoding='utf-8')
    parts = {k: v.strip() for k, v in re.findall(r'<!-- @part (\w+)[^\n]*-->\n(.*?)(?=<!-- @part |\Z)', c, re.S)}
    assert set(parts) == {'metrika', 'uis', 'noscript', 'radist'}, 'server/counters.html: нужны части metrika, uis, noscript, radist'
    m, u, n, r = parts['metrika'], parts['uis'], parts['noscript'], parts['radist']
    assert m.startswith('<!-- Yandex.Metrika counter -->') and m.endswith('<!-- /Yandex.Metrika counter -->')
    assert "ym(113675622, 'init'" in m and 'https://mc.yandex.ru/metrika/tag.js?id=113675622' in m and '<noscript' not in m
    assert u.startswith('<!-- UIS -->') and u.endswith('<!-- UIS -->') and 'app.uiscom.ru/static/cs.min.js?k=' in u
    assert n.startswith('<!-- Yandex.Metrika counter: noscript -->') and 'mc.yandex.ru/watch/113675622' in n
    assert r.startswith('<!-- Radist -->') and r.endswith('<!-- /Radist -->') and 'track.radist.me/tracker.min.js' in r
    for p in parts.values():
        for bad in DEFERRED:
            assert bad not in p, 'server/counters.html: признак отложенной загрузки ' + bad
    return parts


STRIP = [
    re.compile(r'[ \t]*<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->\n?', re.S),  # 28.10–11.11.2026
    re.compile(r'[ \t]*<!-- Yandex\.Metrika counter(?:: noscript)? -->.*?<!-- /Yandex\.Metrika counter -->\n?', re.S),
    re.compile(r'[ \t]*<!-- UIS -->.*?<!-- UIS -->\n?', re.S),
    re.compile(r'[ \t]*<!-- Radist -->.*?<!-- /Radist -->\n?', re.S),
]
LEFTOVER = ('mc.yandex.ru/metrika/tag.js', "ym(113675622, 'init'", 'cs.min.js?k=', 'track.radist.me/tracker.min.js',
            'mc.yandex.ru/watch/113675622')


def strip_counters(s):
    for r in STRIP:
        s = r.sub('', s)
    for k in LEFTOVER:
        assert k not in s, 'счётчик в незнакомом виде (не по server/counters.html): ' + k
    return s


def install_counters(s, parts=None):
    """Официальные коды счётчиков на свои места (закон, п. 1); прежние блоки (в том числе отложенный) убираются."""
    p = parts or counter_parts()
    s = strip_counters(s)
    vp = re.search(r'<meta name="viewport"[^>]*>\n?', s)
    assert vp and vp.start() < s.index('</head>'), 'нет <meta name="viewport"> в <head>'
    s = s[:vp.end()] + ('' if s[vp.end() - 1] == '\n' else '\n') + p['metrika'] + '\n' + s[vp.end():]
    assert s.count('</head>') == 1 and s.count('</body>') == 1, 'ожидались один </head> и один </body>'
    s = s.replace('</head>', p['uis'] + '\n</head>', 1)
    body = re.search(r'<body\b[^>]*>\n?', s)
    s = s[:body.end()] + ('' if s[body.end() - 1] == '\n' else '\n') + p['noscript'] + '\n' + s[body.end():]
    s = s.replace('</body>', p['radist'] + '\n</body>', 1)
    return s


# ---------- проверка (для сборки, пакетов выкладки и сайта) ----------

def check_page(s, counters=True, parts=None):
    """Нарушения закона на странице: список строк (пустой — всё по закону)."""
    bad = []
    for m in TEL_A.finditer(s):
        inner, text = m.group('inner'), plain(m.group('inner'))
        if not re.search(r'\d', text):
            continue
        try:
            want = phone_text(m.group('num'))
        except ValueError as e:
            bad.append(str(e))
            continue
        if inner != want:
            bad.append(f'телефон: внутри ссылки {inner[:90]!r}, нужно ровно «{want}» (п. 4)')
        if re.search(r'(?:aria-label|title|data-t)="[^"]*\d{3}', m.group('attrs')):
            bad.append(f'телефон: копия номера в атрибуте ссылки {m.group("attrs")[:90]!r} (п. 4)')
    for m in MAIL_A.finditer(s):
        inner = m.group('inner')
        if '@' in plain(inner) and inner != m.group('addr'):
            bad.append(f'почта: внутри ссылки {inner[:90]!r}, нужно ровно «{m.group("addr")}» (п. 3)')
    for m in TEXT_PHONE.finditer(s):
        if m.group(0) != f'+7 ({m[1]}) {m[2]}-{m[3]}-{m[4]}':
            bad.append(f'телефон в тексте с неразрывными пробелами: {m.group(0)!r} (п. 4)')
    for m in BROKEN_MAIL.finditer(s):
        bad.append(f'почта разорвана тегом: {m.group(0)[:80]!r} (п. 3)')
    if 'class="phone"' in s and STYLE not in s:
        bad.append('нет стиля <style id="tel-plain"> для значка телефона в шапке')
    for k in DEFERRED:
        if k in s:
            bad.append(f'признак отложенной загрузки счётчиков: {k!r} (п. 1)')
    if not counters:
        for k in LEFTOVER:
            if k in s:
                bad.append(f'на странице без счётчиков есть {k!r}')
        return bad
    p = parts or counter_parts()
    head_end, body = s.find('</head>'), re.search(r'<body\b[^>]*>', s)
    for name in ('metrika', 'uis', 'noscript', 'radist'):
        n = s.count(p[name])
        if n != 1:
            bad.append(f'счётчики: часть «{name}» из server/counters.html на странице {n} раз (нужно ровно 1, байт в байт; п. 1)')
    for k in LEFTOVER:
        if s.count(k) != 1:
            bad.append(f'счётчики: {k!r} встречается {s.count(k)} раз (нужно 1; п. 1)')
    if bad:
        return bad
    im, iu, ino, ir = (s.index(p[k]) for k in ('metrika', 'uis', 'noscript', 'radist'))
    first_css = min([i for i in (s.find('<style'), s.find('rel="stylesheet"'), s.find('<script')) if i >= 0] or [head_end])
    vp = re.search(r'<meta name="viewport"[^>]*>\s*', s)
    if not (vp and im == vp.end() and im < first_css and im < head_end):
        bad.append('Метрика не сразу после <meta name="viewport"> в <head> (до стилей и скриптов; п. 1)')
    if not (iu < head_end and s[iu + len(p['uis']):head_end].strip() == ''):
        bad.append('UIS не прямо перед </head> (п. 1)')
    if not (body and ino > body.end() - 1 and s[body.end():ino].strip() == ''):
        bad.append('<noscript> Метрики не сразу после <body> (п. 1)')
    if not (ir > s.find('</footer>') and s[ir + len(p['radist']):s.find('</body>')].strip() == ''):
        bad.append('Radist не в конце <body> (п. 1)')
    return bad


def repo_pages():
    skip = ('tools', 'dist', 'node_modules', '.git', 'server')
    return sorted(p for p in ROOT.rglob('index.html')
                  if not any(x in p.relative_to(ROOT).parts for x in skip) and not p.relative_to(ROOT).parts[0].startswith('preview-'))


def main(argv):
    if argv[:1] == ['--check-prod']:
        files, fail = [pathlib.Path(a) for a in argv[1:]], 0
        parts = counter_parts()
        for f in files:
            rel = '/'.join(f.parts[-2:]) if f.parent.name in ('privacy', 'soglasie') else f.name
            bad = check_page(f.read_text(encoding='utf-8'), counters=rel not in NO_COUNTERS, parts=parts)
            for b in bad:
                print(f'НАРУШЕНИЕ ЗАКОНА {f}: {b}')
            fail |= bool(bad)
        print(('ЕСТЬ НАРУШЕНИЯ' if fail else 'OK: закон соблюдён') + f' — проверено страниц: {len(files)}')
        return 1 if fail else 0
    check = argv[:1] == ['--check']
    changed, fail = 0, 0
    for f in repo_pages():
        s = f.read_text(encoding='utf-8')
        if check:
            for b in check_page(s, counters=False):
                print(f'НАРУШЕНИЕ ЗАКОНА {f.relative_to(ROOT)}: {b}')
                fail = 1
            continue
        new = normalize_contacts(s)
        assert normalize_contacts(new) == new, f'{f}: повторный запуск меняет страницу'
        bad = check_page(new, counters=False)
        assert not bad, f'{f.relative_to(ROOT)}: ' + '; '.join(bad)
        if new != s:
            f.write_text(new, encoding='utf-8')
            changed += 1
    if check:
        print('ЕСТЬ НАРУШЕНИЯ' if fail else 'OK: разметка телефона и почты на страницах репозитория по закону')
        return fail
    print(f'tracking_laws: телефон и почта по закону — изменено страниц: {changed}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
