#!/usr/bin/env python3
"""Самопроверка → заявка: кнопка блока открывает короткую форму, отметки уходят в заявку (решение владельца 19.11.2026).

    python3 tools/site/samoproverka_forma.py              # правит страницы репозитория и собирает samoproverka-forma.min.js
    python3 tools/site/samoproverka_forma.py --check      # только проверка страниц репозитория

Запрос владельца 13.11.2026 (страница журнала пест-контроля): «…чтобы человек мог выбрать пункты, нажать кнопку, и после
этого лид должен уйти как заявка… либо должна какая-то форма открыться». Прототип — 13.11.2026; раскладку блока (кнопка
под пунктами, компактно на телефоне) 17.11.2026 выложила другая задача (tools/site/samoproverka.py). Решение владельца
19.11.2026: «Принимается, выкладывай на Timeweb» — форма поверх версии, которая на сайте.

Шаг идёт после tools/site/samoproverka.py и на 13 страницах с блоком #samoproverka:
  * кнопке в .f-check-f — data-chk-open и aria-haspopup="dialog"; под кнопкой строка .f-check-tip «Откроется короткая
    форма. Ваши отметки уйдут вместе с заявкой.»;
  * секции — data-chk-name (название формы в UIS), data-chk-title и data-chk-lead (заголовок и текст окна), у страницы
    «Пест-менеджмент или разовая обработка» — data-chk-mode="risk" (пункты — признаки риска);
  * сразу после style.css — стили окна (<style id="chk-css">) и <script src="…samoproverka-forma.min.js?v=…" defer>
    (код UIS остаётся прямо перед </head>, Radist — в конце <body>, ЗАКОН ВЛАДЕЛЬЦА 11.11.2026).
samoproverka-forma.min.js открывает окно (компьютер — по центру, телефон — шторка снизу без затемнения страницы, ЗАКОН
ВЛАДЕЛЬЦА 17.11.2026), отправляет имя, телефон, тип объекта и отметки в /send.php, после ответа — цель audit и UIS.
Без скрипта кнопка — прежняя ссылка на #zayavka. Раскладка блока, тексты, основная форма, app.js, счётчики, телефон и
почта не меняются. Повторный запуск ничего не меняет. transform() использует и пакет для Timeweb
(tools/deploy/prepare-2026-11-19-samoproverka-forma.py).
"""
import html as htmlmod
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools/legal'))
from typo import typo  # noqa: E402

VERSION = '20261120zv'  # 20.11.2026: в окне и в заявке — весь «Состав заявки» (tools/site/zayavka.py)
JS_NAME = 'samoproverka-forma'
TIP = 'Откроется короткая форма. Ваши отметки уйдут вместе с заявкой.'
VISIT = 'Приедем на объект в Москве или области, '

# страница: название формы для UIS, заголовок и текст окна
PAGES = {
    'materialy/zhurnal-pest-kontrolya': dict(
        name='журнал пест-контроля', title='Проверим журнал на вашем объекте бесплатно',
        lead=VISIT + 'сверим журнал со схемой и точками контроля и покажем, что исправить до проверки.'),
    'materialy/programma-pest-kontrolya': dict(
        name='программа пест-контроля', title='Проверим папку пест-контроля на объекте бесплатно',
        lead=VISIT + 'проверим программу, схему точек и журналы и покажем, что доработать до аудита.'),
    'materialy/pest-menedzhment-ili-razovaya-obrabotka': dict(
        name='пест-менеджмент или разовая обработка', mode='risk',
        title='Подберём формат защиты для вашего объекта',
        lead=VISIT + 'оценим риски и скажем, хватит ли разовой обработки или нужен постоянный пест-менеджмент.'),
    'deratizatsiya': dict(
        name='дератизация', title='Бесплатное обследование объекта',
        lead=VISIT + 'проверим защиту от грызунов, точки контроля и журнал и покажем, что поправить.'),
    'dezinsektsiya': dict(
        name='дезинсекция', title='Бесплатное обследование объекта',
        lead=VISIT + 'проверим ловушки, УФ-лампы и журнал пест-контроля и покажем уязвимые зоны.'),
    'dezinfektsiya/avtotransport': dict(
        name='дезинфекция автотранспорта', title='Посчитаем дезинфекцию для вашего автопарка',
        lead='Приедем на вашу стоянку в Москве или области, обработаем машины и выдадим акт на каждую. '
             'Пришлите список машин — посчитаем цену и окно.'),
    'ochistka-dezinfektsiya-ventilyatsii': dict(
        name='вентиляция', title='Бесплатный осмотр вентиляции',
        lead=VISIT + 'осмотрим систему и документы и скажем, что нужно сделать до проверки.'),
    'pishchevoe-proizvodstvo': dict(
        name='пищевое производство', title='Бесплатное обследование производства',
        lead=VISIT + 'проверим папку пест-контроля и точки в цехах и покажем, что добавить и в каком порядке.'),
    'restorany-i-kafe': dict(
        name='рестораны и кафе', title='Бесплатное обследование ресторана',
        lead=VISIT + 'проверим кухню, склад и документы и покажем, что добавить до проверки.'),
    'magaziny-i-torgovye-seti': dict(
        name='магазины и торговые сети', title='Бесплатное обследование магазина',
        lead=VISIT + 'сверим журнал со схемой и проверим точки контроля на рампе, складе и площадке ТКО.'),
    'sklady-i-logistika': dict(
        name='склады и логистика', title='Бесплатное обследование склада',
        lead=VISIT + 'проверим ворота, точки контроля и журнал и покажем, что доработать до проверки или аудита.'),
    'farmatsevticheskie-proizvodstva': dict(
        name='фармацевтические производства', title='Бесплатное обследование предприятия',
        lead=VISIT + 'сверим схему с объектом, проверим записи и покажем, что добавить в программу и документы.'),
    'gostinitsy': dict(
        name='гостиницы', title='Бесплатное обследование гостиницы',
        lead=VISIT + 'проверим номерной фонд, кухню и документы и покажем, что добавить и в каком порядке.'),
    'biznes-tsentry-torgovye-tsentry-predpriyatiya': dict(
        name='бизнес-центры, ТЦ и предприятия', title='Бесплатное обследование здания',
        lead=VISIT + 'проверим паркинг, подвал, мусорокамеры и документы и покажем, что добавить.'),
}

CSS = """<style id="chk-css">
/* самопроверка → заявка (19.11.2026, tools/site/samoproverka_forma.py): кнопка открывает форму, отметки — в заявке */
#samoproverka .f-check-tip{margin:12px 0 0;font-size:13px;line-height:1.5;color:var(--t2);max-width:420px}
@media (max-width:600px){#samoproverka .f-check-tip{text-align:center;margin-left:auto;margin-right:auto}}
.chk-dlg{padding:0;border:0;margin:auto;width:min(560px,calc(100vw - 32px));max-width:none;max-height:calc(100dvh - 48px);background:transparent;color:var(--t1);overflow:visible}
.chk-dlg::backdrop{background:rgba(3,3,5,.74);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.chk-dlg[open]{animation:chkIn .45s var(--ease)}
html.chk-lock,html.chk-lock body{overflow:hidden}
html.chk-lock{scrollbar-gutter:stable}
.chk-box{position:relative;max-height:calc(100dvh - 48px);overflow-y:auto;overscroll-behavior:contain;border-radius:24px;background:#0f0f12;border:1.4px solid var(--line2);box-shadow:0 40px 120px -30px rgba(0,0,0,.95);padding:clamp(24px,3vw,36px);outline:none}
.chk-box::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;background:radial-gradient(420px circle at 85% -10%,rgba(124,134,255,.14),transparent 60%)}
.chk-x{position:absolute;top:14px;right:14px;z-index:2;width:44px;height:44px;border-radius:50%;border:1px solid var(--line2);background:rgba(255,255,255,.04);color:var(--t2);display:grid;place-items:center;cursor:pointer;transition:color .3s,border-color .3s}
.chk-x:hover,.chk-x:focus-visible{color:#fff;border-color:var(--acc3)}
.chk-x svg{width:18px;height:18px}
.chk-body,.chk-ok{position:relative;z-index:1}
.chk-kicker{font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin:4px 56px 12px 0}
.chk-sum{padding:16px 18px;border-radius:14px;background:rgba(255,255,255,.03);border:1px solid var(--line2)}
.chk-score{margin:0;font-size:15px;color:var(--t2)}
.chk-score b{font-size:34px;font-weight:300;letter-spacing:-.04em;color:var(--acc);margin-right:4px;line-height:1}
.chk-score.full b{color:var(--grn)}
.chk-score.risk b{color:var(--yel)}
.chk-bar{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:4px;margin:12px 0 0}
.chk-bar i{height:6px;border-radius:3px;background:rgba(255,255,255,.09)}
.chk-bar i.on{background:var(--acc2)}
.chk-score.full~.chk-bar i.on{background:var(--grn)}
.chk-score.risk~.chk-bar i.on{background:var(--yel)}
.chk-score.risk~.chk-miss li::before{border-color:var(--yel)}
.chk-miss-t{margin:14px 0 6px;font-size:13.5px;font-weight:500;line-height:1.45;color:var(--t1)}
.chk-miss{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.chk-miss li{position:relative;padding-left:20px;font-size:14px;line-height:1.45;color:var(--t2)}
.chk-miss li::before{content:"";position:absolute;left:2px;top:.35em;width:10px;height:10px;border-radius:3px;border:1.4px solid var(--red)}
.chk-miss[hidden],.chk-err[hidden],.chk-ok[hidden]{display:none}
.chk-body h3{font-size:clamp(21px,1.5vw,26px);font-weight:400;line-height:1.2;letter-spacing:-.02em;margin:22px 0 8px}
.chk-lead{margin:0 0 18px;color:var(--t2);font-size:15px;line-height:1.55}
.chk-fg{display:grid;gap:12px}
.chk-fg .field input,.chk-fg .field select{height:56px}
.chk-send{width:100%;margin-top:16px}
.chk-err{margin:12px 0 0;padding:12px 14px;border-radius:12px;background:rgba(255,100,103,.08);border:1px solid rgba(255,100,103,.35);color:#ffd5d6;font-size:14px;line-height:1.5}
.chk-err a{color:#fff;text-decoration:underline;text-underline-offset:2px}
.chk-body .legal{margin-top:12px}
.chk-ok{text-align:center;padding:28px 6px 6px}
.chk-ok h3{font-size:24px;font-weight:400;margin:0 0 10px}
.chk-ok p{color:var(--t2);line-height:1.6;margin:0 auto;max-width:420px}
.chk-ok .ok-ic circle,.chk-ok .ok-ic path{animation:draw .6s var(--ease) forwards}
.chk-ok .ok-ic path{animation-delay:.45s}
.chk-back{margin-top:22px;height:52px;padding:0 26px;font-size:15px}
.chk-box.sent .chk-body{display:none}
@keyframes chkIn{from{opacity:0;transform:translateY(18px) scale(.98)}}
@keyframes chkUp{from{transform:translateY(100%)}}
/* телефон: шторка снизу; страница за шторкой не затемняется и не размывается (ЗАКОН ВЛАДЕЛЬЦА 17.11.2026) */
@media (max-width:760px){
  .chk-dlg{margin:auto 0 0;width:100%;max-height:calc(100dvh - 10px)}
  .chk-dlg::backdrop{background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none}
  .chk-box{max-height:calc(100dvh - 10px);border-radius:22px 22px 0 0;border-bottom:0;box-shadow:none;padding:26px 18px calc(18px + env(safe-area-inset-bottom))}
  .chk-box::before{content:"";position:absolute;top:8px;left:50%;width:40px;height:4px;margin-left:-20px;border-radius:2px;background:rgba(255,255,255,.18)}
  .chk-x{top:12px;right:10px}
  .chk-dlg[open]{animation:chkUp .5s var(--ease)}
  .chk-body h3{margin-top:18px}
  .chk-lead{font-size:14px;margin-bottom:14px}
}
@media (prefers-reduced-motion:reduce){.chk-dlg[open]{animation:none}}
</style>
"""


SEC_RE = re.compile(r'<section class="f-checks" id="samoproverka"[^>]*>.*?</section>', re.S)
FOOT_RE = re.compile(r'<div class="f-check-f">.*?</div>', re.S)
BTN_RE = re.compile(r'<a href="#zayavka" class="btn [^"]*"[^>]*>.*?</a>', re.S)
LINK_RE = re.compile(r'<link rel="stylesheet" href="(?:\.\./)+style\.css\?v=[0-9a-z]+">')


def one(rx, s, what):
    found = list(rx.finditer(s))
    assert len(found) == 1, '%s: найдено %d' % (what, len(found))
    return found[0]


def attr(s):
    return htmlmod.escape(s, quote=True)


def rel_root(page):
    return '../' * (page.count('/') + 1)


def script_tag(page):
    return '<script src="%s%s.min.js?v=%s" defer></script>' % (rel_root(page), JS_NAME, VERSION)


def transform_section(sec, page):
    cfg = PAGES[page]
    if 'data-chk-open' in sec:
        return sec
    foot = one(FOOT_RE, sec, page + ': .f-check-f (раскладка tools/site/samoproverka.py)')
    btn = one(BTN_RE, foot.group(0), page + ': кнопка в .f-check-f')
    b = btn.group(0)
    new_b = b.replace('<a href="#zayavka" ', '<a href="#zayavka" data-chk-open aria-haspopup="dialog" ', 1)
    new_foot = foot.group(0).replace(b, new_b + '\n          <p class="f-check-tip">' + typo(TIP) + '</p>', 1)
    out = sec[:foot.start()] + new_foot + sec[foot.end():]
    extra = ' data-chk-name="%s" data-chk-title="%s" data-chk-lead="%s"' % (
        attr(cfg['name']), attr(typo(cfg['title'])), attr(typo(cfg['lead'])))
    if cfg.get('mode'):
        extra += ' data-chk-mode="%s"' % cfg['mode']
    head = out[:out.index('>') + 1]
    assert 'data-chk-name' not in head
    return head[:-1] + extra + '>' + out[len(head):]


def transform(s, page):
    """Возвращает (новый текст, список замен [старое, новое, 1]) для страницы page (адрес без / в начале и конце)."""
    reps = []
    sec = one(SEC_RE, s, page + ': блок самопроверки').group(0)
    new_sec = transform_section(sec, page)
    if new_sec != sec:
        reps.append([sec, new_sec, 1])
    css_m = re.search(r'<style id="chk-css">.*?</style>\n', s, re.S)
    if not css_m:
        link = one(LINK_RE, s, page + ': style.css').group(0)
        reps.append([link, link + '\n' + CSS + script_tag(page), 1])
    elif css_m.group(0) != CSS:  # стили обновлены — заменить прежний блок
        reps.append([css_m.group(0), CSS, 1])
    tag_m = re.search(r'<script src="(?:\.\./)*' + JS_NAME + r'\.min\.js\?v=[0-9a-z]+" defer></script>', s)
    if tag_m and tag_m.group(0) != script_tag(page):  # новая версия скрипта — новая метка ?v=
        reps.append([tag_m.group(0), script_tag(page), 1])
    out = s
    for a, b, c in reps:
        assert out.count(a) == c, page + ': ' + a[:60]
        out = out.replace(a, b)
    return out, reps


def problems(s, page):
    m = SEC_RE.search(s)
    if not m:
        return ['нет блока самопроверки']
    sec, bad = m.group(0), []
    foot = FOOT_RE.search(sec)
    if not foot or 'data-chk-open' not in foot.group(0) or 'f-check-tip' not in foot.group(0):
        bad.append('кнопка в .f-check-f без формы')
    if sec.count('data-chk-open') != 1 or 'data-chk-name' not in sec[:sec.index('>')]:
        bad.append('настройки формы')
    if s.count('<style id="chk-css">') != 1:
        bad.append('стили окна: %d' % s.count('<style id="chk-css">'))
    if s.count(script_tag(page)) != 1 or s.count(JS_NAME + '.min.js') != 1:
        bad.append('скрипт формы: %d' % s.count(JS_NAME + '.min.js'))
    elif s.index(script_tag(page)) > s.index('</head>'):
        bad.append('скрипт формы не в <head>')
    return bad


def minify():
    subprocess.run(['npx', '--yes', 'esbuild@0.24.2', JS_NAME + '.js', '--minify', '--target=es2015', '--charset=utf8',
                    '--outfile=' + JS_NAME + '.min.js', '--log-level=warning'], cwd=ROOT, check=True)


def main():
    check = '--check' in sys.argv[1:]
    total = 0
    for page in PAGES:
        f = ROOT / page / 'index.html'
        s = f.read_text(encoding='utf-8')
        if not check:
            new, reps = transform(s, page)
            if new != s:
                f.write_text(new, encoding='utf-8')
                total += 1
            s = new
        bad = problems(s, page)
        if bad:
            sys.exit('%s: %s' % (page, '; '.join(bad)))
    if not check:
        minify()
        print('samoproverka_forma: изменено страниц %d из %d, %s.min.js собран' % (total, len(PAGES), JS_NAME))
    else:
        print('samoproverka_forma: %d страниц — кнопка открывает форму, отметки уходят в заявку' % len(PAGES))


if __name__ == '__main__':
    main()
