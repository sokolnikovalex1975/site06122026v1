#!/usr/bin/env python3
"""Образец и бланк акта (форма АПК-01) и чек-лист документов для страницы «Документы для Роспотребнадзора».

    python3 tools/akt/build_akt.py            → normativnaya-baza/dokumenty-dlya-rospotrebnadzora/*.pdf, img/akt-*.webp, img/dk-og.jpg

Акт «обследования объекта и выполненных работ по дезинсекции и дератизации» — продолжение образца журнала
пест-контроля (tools/zhurnal): тот же объект (хлебопекарный цех, г. о. Химки), договор № 0917-ПК/26, журнал № ПК-0917/26,
визит 14.10.2026 (в журнале — акт 0917-04: очаг рыжего таракана в моечной, точечная обработка гелем, замена приманки в КИК-05).
Заказчик обезличен (ООО «••••••••»), номера свидетельств о госрегистрации скрыты — как в журнале.

Образец и бланк печатаются из одного HTML: бланк — тот же документ с <body class="tpl">, записи (.ink), подписи (.sg)
и отметка «Образец заполнения» (.only-s) скрыты через visibility:hidden — листы совпадают геометрически.
Шапка на каждом листе — как в журнале: крупно телефон и пестконтроль-центр.рф; водяной знак — диагональная надпись
«пестконтроль-центр.рф» контурами букв (tools/zhurnal/wm.py).

Чек-лист — все документы перечня (tools/normativnaya-baza/dokumenty_data.py) с графами «Есть / Нет / Не требуется»
и таблица проверочных листов по типам объектов.

Нужны: Node.js с playwright (/home/user/node_modules или NODE_PATH), PyMuPDF, Pillow, fontTools.
"""
import html as H
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
FONTS = ROOT / 'fonts'
OUT = pathlib.Path(os.environ.get('AKT_OUT', '/tmp/akt-build'))
DST = ROOT / 'normativnaya-baza' / 'dokumenty-dlya-rospotrebnadzora'
IMG = ROOT / 'img'
sys.path.insert(0, str(ROOT / 'tools' / 'zhurnal'))
sys.path.insert(0, str(ROOT / 'tools' / 'normativnaya-baza'))
from wm import watermark_svg  # noqa: E402
import dokumenty_data as DK  # noqa: E402

NB = '\u00a0'
FORM = f'Форма АПК-01 · ред.{NB}11.2026'
CO = {
    'legal': 'ООО «Центр дезинфекционных услуг»', 'inn': '7714462211', 'kpp': '771401001', 'ogrn': '1207700257775',
    'addr': f'123007, г.{NB}Москва, 2-й Хорошёвский проезд, д.{NB}7, к.{NB}1, помещ.{NB}1',
    'lic': f'№{NB}Л064-00111-77/01942445', 'phone': '+7 (495) 104-35-70', 'mail': 'b2b@pestcontrol-center.ru',
    'site': 'пестконтроль-центр.рф',
}
LOGO = ('<svg class="lg" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#09090b"/>'
        '<g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round">'
        '<path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/>'
        '<circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/>'
        '<path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>')
IC_PHONE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 '
            '4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 '
            '1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
IC_GLOBE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 '
            '15.3 15.3 0 0 1 4-10z"/></svg>')
SIGS = {
    'smirnov': 'M2 14c3-9 6-11 7-6s-2 9 1 6 4-10 6-8-1 9 2 7 3-5 5-4 1 4 4 3 5-2 9-3',
    'ivanova': 'M2 9c4 0 4 7 6 5s2-9 4-8 0 9 3 8 3-7 5-6 0 6 3 5 4-5 6-4 1 3 6 1',
}


# ---------------------------------------------------------------- CSS: стили листа — из журнала (одна система форм)
def journal_css():
    src = (ROOT / 'tools' / 'zhurnal' / 'build_journal.py').read_text(encoding='utf-8')
    m = re.search(r'CSS = r"""(.*?)"""', src, re.S)
    assert m, 'нет CSS в tools/zhurnal/build_journal.py'
    return m.group(1).replace('__F__', FONTS.resolve().as_uri())


CSS_AKT = r"""
.nw{white-space:nowrap}
.a-top{display:flex;align-items:flex-end;justify-content:space-between;gap:6mm;margin:4.6mm 0 1mm}
.a-kicker{font-size:7.2pt;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#615fff}
.a-h1{font-size:23pt;font-weight:800;letter-spacing:-.03em;line-height:1;margin:1.6mm 0 1.6mm}
.a-sub{font-size:10.2pt;color:#3f3f46;line-height:1.3;max-width:118mm}
.a-no{display:grid;grid-template-columns:auto auto;column-gap:2.4mm;row-gap:1.8mm;align-items:center;font-size:8.6pt;font-weight:600;white-space:nowrap}
.a-nobox{display:inline-block;width:36mm;height:8.6mm;line-height:8mm;border:.35mm solid #09090b;border-radius:1.2mm;padding:0 2.6mm;font-size:11pt;white-space:nowrap;overflow:hidden}
.kv2{display:grid;grid-template-columns:34mm 1fr 34mm 1fr;column-gap:3mm;row-gap:.6mm;align-items:end}
.kv2>.k{font-size:7pt;color:#71717a;line-height:1.2;padding-bottom:.9mm}
.kv2>.w{grid-column:2 / -1}
.kv2 .pr{font-size:7.6pt;line-height:1.35;padding-bottom:.9mm}
.t td.lb{font-weight:600;color:#27272a}
.t td.lb small{display:block;font-weight:400;color:#71717a;font-size:6.2pt;margin-top:.4mm}
.chk{list-style:none;margin:1.6mm 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;column-gap:5mm;row-gap:1.3mm;font-size:7pt;line-height:1.32}
.chk li{display:flex;gap:2mm;align-items:flex-start}
.cb{flex:none;width:3.5mm;height:3.5mm;border:.3mm solid #52525b;border-radius:.6mm;display:grid;place-items:center;margin-top:.15mm}
.cb .ink{font-style:normal;font-weight:700;font-size:8pt;line-height:1}
.chk em{font-style:normal;color:#71717a}
.res{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:1.6mm}
.res .box{padding:2mm 2.6mm}
.res .box h3{margin-bottom:1mm}
.acc{margin-top:3mm;display:flex;gap:2.4mm;align-items:flex-start;font-size:7.4pt;line-height:1.4}
.sgg{display:grid;grid-template-columns:1fr 1fr;gap:8mm;margin-top:3.2mm}
.sgg .sgb{border:.25mm solid #a1a1aa;border-radius:1.2mm;padding:2.4mm 3mm}
.sgg .mp{display:flex;align-items:center;justify-content:space-between;margin-top:1.6mm;font-size:6.6pt;color:#71717a}
.stamp-s{display:inline-grid;place-items:center;width:18mm;height:18mm;border:.3mm dashed #a1a1aa;border-radius:50%;color:#a1a1aa;font-size:6.4pt;letter-spacing:.1em}
.fine{font-size:6.3pt;color:#52525b;line-height:1.45;margin:2.6mm 0 0}
.fine b{color:#18181b;font-weight:600}
/* чек-лист документов */
.ck-h1{font-size:20pt;font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:4mm 0 1.4mm}
.ck-sub{font-size:8.6pt;color:#3f3f46;line-height:1.4;margin:0 0 2.6mm;max-width:165mm}
.ck-f{display:grid;grid-template-columns:28mm 1fr 24mm 1fr;column-gap:3mm;row-gap:1.4mm;align-items:end;margin-bottom:2mm}
.ck-f>.k{font-size:6.9pt;color:#71717a;padding-bottom:.7mm}
.ck-f .fld{line-height:5mm}
.ck-g{display:flex;align-items:baseline;gap:2.4mm;margin:3mm 0 1.2mm;break-after:avoid}
.ck-g .n{flex:none;font-size:6.6pt;font-weight:700;color:#fff;background:#615fff;border-radius:1mm;padding:.5mm 1.6mm}
.ck-g h2{font-size:9.6pt;font-weight:700;margin:0;letter-spacing:-.01em}
.ck th.c,.ck td.c{text-align:center;vertical-align:middle;padding-left:0;padding-right:0}
.ck td.c b{display:inline-block;width:3.4mm;height:3.4mm;border:.28mm solid #52525b;border-radius:.6mm;vertical-align:middle}
.ck td .bs{display:block;color:#71717a;font-size:5.9pt;line-height:1.3;margin-top:.4mm}
.ck td .for{display:block;color:#3f3dcc;font-size:5.9pt;line-height:1.3;margin-top:.4mm}
.ck td.who{font-size:6.3pt;color:#3f3f46}
.ck tr{break-inside:avoid}
.ck-leg{font-size:6.3pt;color:#52525b;margin:1.4mm 0 0;line-height:1.45}
.flow{flex:1 1 auto;min-height:0;overflow:hidden}
#src{position:absolute;left:-10000px;top:0;width:178mm}
"""


def sig(who, h=3.8):
    w = h * 3
    return (f'<svg class="sg" viewBox="0 0 54 18" style="width:{w:.1f}mm;height:{h:.1f}mm" aria-hidden="true">'
            f'<path d="{SIGS[who]}" fill="none" stroke="#1d3fb8" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def ink(v):
    return f'<i class="ink">{v}</i>' if v else ''


def sl(v='', w=30, cls=''):
    st = f' style="width:{w}mm"' if w else ''
    return f'<span class="sl {cls}"{st}>{v}</span>'


def fld(v='', n=1):
    lines = ''.join(f'<b class="ul" style="top:{(k + 1) * 5 - 0.25:.2f}mm"></b>' for k in range(n))
    return f'<span class="fld" style="height:{n * 5}mm">{lines}{ink(v)}</span>'


def cb(on=True):
    return f'<span class="cb">{ink("✓") if on else ""}</span>'


def header():
    return (f'<header class="hd"><div class="brand">{LOGO}<div><div class="bn">ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>'
            f'<div class="bt">Пест-контроль для организаций · IPM / ХАССП</div></div></div>'
            f'<div class="hc"><i>{IC_PHONE}</i><b class="ph">{CO["phone"]}</b><i>{IC_GLOBE}</i><b class="st">{CO["site"]}</b></div></header>')


def footer(n, total, form=FORM):
    return (f'<footer class="ft"><div><b>ПЕСТКОНТРОЛЬ Центр</b> · {CO["legal"]} · ИНН {CO["inn"]} · КПП {CO["kpp"]} · ОГРН {CO["ogrn"]}<br>'
            f'Лицензия Роспотребнадзора {CO["lic"]} · {CO["addr"]}<br>{CO["phone"]} · {CO["mail"]} · {CO["site"]}</div>'
            f'<div class="pn"><span class="fm">{form}</span><span>Лист</span><span>{n} из {total}</span></div></footer>')


WM = None


def page(body, n, total, cls=''):
    return f'<section class="pg{(" " + cls) if cls else ""}">{WM}{header()}{body}{footer(n, total)}</section>'


def sec(n, title):
    return f'<div class="sec"><span class="n">{n}</span><h2>{title}</h2></div>'


# ---------------------------------------------------------------- данные образца (визит 14.10.2026, журнал ПК-0917/26)
A_NO, A_DATE = '0917-04', '14.10.2026'
OBJ_SHORT = f'Хлебопекарный цех, г.{NB}о.{NB}Химки'
SGR = 'RU.77.99.••.•••.Е.••••••.••.••'


def meta():
    return (f'<div class="meta"><div class="meta-l"><span>Акт №</span>{sl(ink(A_NO), 15)}<span>от</span>{sl(ink(A_DATE), 17)}'
            f'<span>Объект</span>{sl(ink(OBJ_SHORT), 47)}</div>'
            f'<div class="meta-r"><span class="badge only-s">Образец заполнения</span><b>{FORM}</b></div></div>')


def akt_page1():
    top = (f'<div class="a-top"><div><div class="a-kicker">Пест-контроль · СанПиН 3.3686-21</div>'
           f'<div class="a-h1">АКТ</div><div class="a-sub">обследования объекта и выполненных работ по дезинсекции и дератизации</div></div>'
           f'<div class="a-no"><span>№</span><span class="a-nobox">{ink(A_NO)}</span><span>от</span><span class="a-nobox">{ink(A_DATE)}</span></div></div>')
    rows = (f'<div class="k">Дата, время, вид визита</div><div class="w">'
            f'{fld(f"{A_DATE}, 09:40–12:20 · плановый + дезинсекция по показаниям (сигнал №{NB}1 от 13.10.2026)")}</div>')
    one = [
        ('Объект, адрес', f'Хлебопекарный цех, Московская обл., г.{NB}о.{NB}Химки, ул.{NB}Примерная, д.{NB}1, стр.{NB}2'),
        ('Заказчик', f'ООО «••••••••», ИНН 50••••••••'),
        ('Договор, журнал', f'договор №{NB}0917-ПК/26 от 28.08.2026 · журнал пест-контроля №{NB}ПК-0917/26'),
    ]
    for k, v in one:
        rows += f'<div class="k">{k}</div><div class="w">{fld(v)}</div>'
    rows += (f'<div class="k">Специалист Исполнителя</div><div class="w">{fld(f"Смирнов А.{NB}Н., инженер пест-менеджер")}</div>'
             f'<div class="k">Представитель Заказчика</div><div class="w">{fld(f"Иванова Е.{NB}В., менеджер по качеству (приказ №{NB}41-П от 01.09.2026)")}</div>')
    rows += (f'<div class="k">Исполнитель</div><div class="w pr"><b>{CO["legal"]}</b> (ПЕСТКОНТРОЛЬ Центр), ИНН {CO["inn"]}, '
             f'лицензия <span class="nw">{CO["lic"]}</span></div>')
    s1 = sec(1, 'Общие сведения') + f'<div class="kv2">{rows}</div>'

    obs = [
        ('К1 — территория', 'станции с приманкой', 'КИК-01…08', '8 / 8',
         f'КИК-05 (отмостка) — поедаемость 20{NB}%, приманка заменена; нор нет — засыпаны 06.10 (пр.{NB}№{NB}4). Остальные — 0',
         f'ниже порога 25{NB}%, снижение (30.09 — 50{NB}%)', ''),
        ('К2 — периметр', 'ворота, доки, входы', 'МЛ-01…08', '8 / 8',
         f'Находок нет; МЛ-04 — доступ восстановлен (пр.{NB}№{NB}5)', 'норма', ''),
        ('К3 — помещения', 'склад, цех, упаковка, АБК', '<span class="nw">МЛ-09…10</span>, <span class="nw">ИМ-01…06</span>, '
         '<span class="nw">ИЛ-01…04</span>, <span class="nw">ФЛ-01…02</span>', '14 / 14',
         f'ИМ-03 (моечная) — рыжий таракан, имаго, 2{NB}особи. ИЛ — мухи 10, плодовые мушки 3. МЛ, ФЛ — 0',
         'ИМ-03 — превышение (порог 0); ИЛ — норма', 'mk-r'),
    ]
    trs = ''.join(
        f'<tr><td class="lb">{lb}<small>{sm}</small></td><td>{ink(pts)}</td><td class="c">{ink(cnt)}</td><td>{ink(find)}</td>'
        f'<td class="{mk}">{ink(ev)}</td></tr>' for lb, sm, pts, cnt, find, ev, mk in obs)
    t2 = ('<table class="t"><colgroup><col style="width:29mm"><col style="width:27mm"><col style="width:16mm"><col><col style="width:32mm"></colgroup>'
          '<thead><tr><th>Контур защиты</th><th>Точки контроля (ТПК)</th><th class="c">Осмотр</th><th>Находки, признаки вредителей</th>'
          '<th>Оценка к порогу</th></tr></thead><tbody>' + trs +
          f'<tr><td class="lb">Итого</td><td>{ink("30 ТПК по план-схеме")}</td><td class="c">{ink("30 / 30")}</td>'
          f'<td colspan="2">{ink("Все точки доступны и исправны; отметки — в поточечном листе (раздел 5 журнала)")}</td></tr></tbody></table>')
    s2 = (sec(2, 'Обследование объекта') +
          '<p class="lead">Учёт численности и заселённости по точкам контроля — пп.&nbsp;99, 101, 109–111 СанПиН 3.3686-21; '
          'признаки заселённости грызунами — п.&nbsp;117.</p>' + t2 +
          '<div class="res">'
          f'<div class="box"><h3>Санитарно-техническое состояние</h3>{fld("Моечная: отслоение герметика за ванной, влага, остатки теста — риск для тараканов (рек. 1)", 2)}</div>'
          f'<div class="box"><h3>Заселённость грызунами (п.{NB}117)</h3>{fld("Здание (К2–К3) — признаков нет. Территория (К1) — поедание приманки в КИК-05, снижается", 2)}</div>'
          '</div>')

    works = [
        ('1', 'Дезинсекция по показаниям (рыжий таракан)', f'Моечное отделение: шов за ванной, кабель-канал; 12{NB}м²',
         f'Инсектицидный гель (№{NB}3 по журналу), имидаклоприд 2,15{NB}%, СГР {SGR}', 'точечно, каплями в щели и полости', f'6{NB}г'),
        ('2', 'Дератизация: замена приманки', 'К1, КИК-05 — отмостка восточной стены',
         f'Приманка-брикет (№{NB}1 по журналу), бродифакум 0,005{NB}%, СГР {SGR}', f'в запираемой станции (п.{NB}120)', f'40{NB}г'),
        ('3', 'Мониторинг', '30 ТПК, контуры К1–К3', '—', 'осмотр, учёт по видам', '—'),
    ]
    trs = ''.join(f'<tr><td class="num" style="height:10mm">{n}</td><td>{ink(a)}</td><td>{ink(b)}</td><td>{ink(c)}</td><td>{ink(d)}</td>'
                  f'<td class="c">{ink(e)}</td></tr>' for n, a, b, c, d, e in works)
    t3 = ('<table class="t"><colgroup><col style="width:6mm"><col style="width:32mm"><col style="width:38mm"><col><col style="width:31mm"><col style="width:12mm"></colgroup>'
          '<thead><tr><th class="c">№</th><th>Вид работ, цель</th><th>Место, площадь</th><th>Средство: наименование, действующее вещество, '
          'концентрация, номер СГР</th><th>Способ применения</th><th class="c">Расход</th></tr></thead><tbody>' + trs + '</tbody></table>')
    conds = [
        ('Сотрудники предупреждены, помещение подготовлено', '102'),
        ('Персонала в зоне нет, продукция убрана или упакована', '105'),
        ('Окна закрыты, проветривание — по инструкции', '103'),
        ('Средство — по инструкции, в недоступных местах', '104, 106'),
        ('После обработки — влажная уборка силами Заказчика', '107'),
        ('Приманки — в закрытых пронумерованных станциях', '120'),
    ]
    lis = ''.join(f'<li>{cb()}<span>{t} <em>(п.{NB}{p})</em></span></li>' for t, p in conds)
    s3 = (sec(3, 'Выполненные работы') + t3 +
          f'<p class="note"><b>Условия проведения обработки</b> — отметки специалиста Исполнителя, в скобках — пункты СанПиН 3.3686-21:</p><ul class="chk">{lis}</ul>')
    return meta() + top + s1 + s2 + s3


def akt_page2():
    eff = [
        (f'Дератизация К1, КИК-05: замена приманки 30.09 (антикоагулянт — учёт через 10–30 дней, п.{NB}114)',
         f'30.09 — поедаемость 50{NB}%, 2 жилые норы', f'20{NB}%, нор нет', 'численность снижается; продолжить, контроль 28.10'),
        (f'Пищевые огнёвки, склад муки (ФЛ-01): уборка просыпей 17.09 (пр.{NB}№{NB}3)', '16.09 — 2 особи; 30.09 — 1', '0',
         'эффективно; ловушки сохранить'),
        (f'Дезинсекция в моечной — по п.{NB}3.1 этого акта', 'ИМ-03 — 2 особи', 'контроль 28.10.2026',
         f'при отсутствии эффекта — повтор средством другой химической группы (п.{NB}99)'),
    ]
    trs = ''.join(f'<tr><td>{ink(a)}</td><td>{ink(b)}</td><td>{ink(c)}</td><td>{ink(d)}</td></tr>' for a, b, c, d in eff)
    s4 = (sec(4, 'Контроль эффективности') +
          '<p class="lead">Контроль эффективности истребительных мероприятий — пп.&nbsp;99, 114, 116 и 122 СанПиН 3.3686-21. '
          'Объект свободен от грызунов, если нет ни одного признака из п.&nbsp;117.</p>'
          '<table class="t"><colgroup><col style="width:58mm"><col style="width:36mm"><col style="width:28mm"><col></colgroup>'
          '<thead><tr><th>Мероприятие, дата</th><th>Было</th><th>Сейчас</th><th>Вывод</th></tr></thead><tbody>' + trs + '</tbody></table>')

    rec = [('1', 'Моечная: отслоение герметика за ванной, влага, остатки теста', 'Санобработка за ванной, герметизация шва',
            f'Начальник цеха, до 21.10.2026', f'пр.{NB}№{NB}6'),
           ('2', '', '', '', ''), ('3', '', '', '', '')]
    trs = ''.join(f'<tr><td class="num" style="height:9mm">{n}</td><td>{ink(a)}</td><td>{ink(b)}</td><td>{ink(c)}</td><td class="c">{ink(d)}</td></tr>'
                  for n, a, b, c, d in rec)
    s5 = (sec(5, 'Рекомендации Заказчику') +
          '<p class="lead">Меры, которые не дают вредителям проникать и размножаться (п.&nbsp;111 СанПиН 3.3686-21). '
          'Выполнение проверяет Исполнитель на следующем визите и отмечает в разделе 7 журнала.</p>'
          '<table class="t"><colgroup><col style="width:6mm"><col><col style="width:46mm"><col style="width:36mm"><col style="width:16mm"></colgroup>'
          '<thead><tr><th class="c">№</th><th>Что выявлено (причина риска)</th><th>Что сделать</th><th>Ответственный, срок</th><th class="c">В журнале</th></tr></thead>'
          '<tbody>' + trs + '</tbody></table>')

    concl = ('Обследование выполнено в полном объёме: осмотрено 30 из 30 ТПК. В моечном отделении выявлен очаг рыжего таракана '
             '(ИМ-03 — 2 особи), проведена точечная дезинсекция гелем. На территории (К1) поедаемость приманки в КИК-05 снизилась '
             'с 50 до 20 %, в здании признаков грызунов нет.')
    s6 = (sec(6, 'Заключение') + fld(concl, 3) +
          f'<div class="kv2" style="margin-top:1.6mm"><div class="k">Следующий плановый визит</div><div class="w">{fld("28.10.2026 — плановый, с контролем эффективности дезинсекции в моечной")}</div>'
          f'<div class="k">Приложения к акту</div><div class="w">{fld("фото ИМ-03 до обработки и места нанесения геля (2 шт.)")}</div></div>')

    sg = (f'<div class="acc">{cb()}<span>Работы выполнены в полном объёме. Заказчик с результатами обследования и рекомендациями ознакомлен, '
          'претензий по объёму, качеству и срокам не имеет.</span></div>'
          '<div class="sgg">'
          f'<div class="sgb"><div class="sgb-t">Исполнитель — {CO["legal"]}</div>'
          f'<div class="sgb-r"><div class="sgc">{sl(ink("инженер пест-менеджер"), 0)}<em>должность</em></div>'
          f'<div class="sgc">{sl(ink(f"Смирнов А.{NB}Н."), 0)}<em>ФИО</em></div></div>'
          f'<div class="sgb-r" style="margin-top:1.6mm"><div class="sgc">{sl(sig("smirnov"), 0)}<em>подпись</em></div>'
          f'<div class="sgc">{sl(ink(A_DATE), 0)}<em>дата</em></div></div>'
          '<div class="mp"><span>М.&nbsp;П.</span><span class="stamp-s">ПЕЧАТЬ</span></div></div>'
          f'<div class="sgb"><div class="sgb-t">Заказчик</div>'
          f'<div class="sgb-r"><div class="sgc">{sl(ink("менеджер по качеству"), 0)}<em>должность</em></div>'
          f'<div class="sgc">{sl(ink(f"Иванова Е.{NB}В."), 0)}<em>ФИО</em></div></div>'
          f'<div class="sgb-r" style="margin-top:1.6mm"><div class="sgc">{sl(sig("ivanova"), 0)}<em>подпись</em></div>'
          f'<div class="sgc">{sl(ink(A_DATE), 0)}<em>дата</em></div></div>'
          '<div class="mp"><span>М.&nbsp;П. (при наличии)</span><span class="stamp-s">ПЕЧАТЬ</span></div></div>'
          '</div>')
    fine = ('<p class="fine"><b>Как применять форму.</b> Акт составляют по каждому визиту в двух экземплярах; номер акта совпадает с записью '
            'в ведомости визитов (раздел 4 журнала пест-контроля) и с актом в ЭДО. Акт вместе с журналом, договором и программой '
            'пест-контроля подтверждает проверяющему кратность обследований, обработки по показаниям и контроль их эффективности. '
            'Форма АПК-01 — форма ПЕСТКОНТРОЛЬ Центра, а не утверждённая государственная: СанПиН 3.3686-21 не устанавливает единого '
            'бланка акта, но требует учёта численности вредителей, контроля эффективности и производственного контроля за '
            'дезинфекционными мероприятиями (пп.&nbsp;82, 99, 114).</p>')
    return meta() + s4 + s5 + s6 + sg + fine


def akt_html():
    body = page(akt_page1(), 1, 2) + page(akt_page2(), 2, 2)
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Акт обследования и выполненных работ по дезинсекции и '
            f'дератизации — образец</title><style>{journal_css()}{CSS_AKT}</style></head><body>{body}</body></html>')


# ---------------------------------------------------------------- чек-лист документов
def plain(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return H.unescape(s).replace('официальный перечень сведений', 'Официальный перечень сведений').strip()


OBJ_LABEL = {code: lab for code, lab, _s, _g in DK.OBJECTS}
WHO_SHORT = {'my': 'Исполнитель пест-контроля', 'org': 'Организация', 'lab': 'Лаборатория', 'ext': 'Подрядчик'}


def ck_rows(gid, start):
    out, n = [], start
    for rw in DK.ROWS:
        if rw['g'] != gid:
            continue
        n += 1
        bs = plain(rw.get('basis', ''))
        if len(bs) > 150:
            bs = bs[:150].rsplit(' ', 1)[0].rstrip(',;:') + '…'
        only = ''
        if rw['obj'] != DK.ALL:
            only = '<span class="for">Для: ' + ', '.join(OBJ_LABEL[o].lower() if i else OBJ_LABEL[o] for i, o in enumerate(rw['obj'])) + '</span>'
        who = plain(rw.get('who_text') or DK.WHO[rw['who']])
        out.append(f'<tr><td class="num">{n}</td><td><b style="font-weight:600">{H.escape(plain(rw["name"]))}</b>{only}'
                   f'<span class="bs">{H.escape(bs)}</span></td><td class="who">{H.escape(who)}</td>'
                   '<td class="c"><b></b></td><td class="c"><b></b></td><td class="c"><b></b></td></tr>')
    return out, n


def ck_table(rows):
    return ('<table class="t ck"><colgroup><col style="width:6mm"><col><col style="width:38mm"><col style="width:10mm"><col style="width:10mm">'
            '<col style="width:13mm"></colgroup><thead><tr><th class="c">№</th><th>Документ и основание</th><th>Кто готовит</th>'
            '<th class="c">Есть</th><th class="c">Нет</th><th class="c">Не треб.</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


# раскладка по листам — в браузере (render_akt.mjs ждёт window.__done): группа, не поместившаяся на лист, продолжается
# на следующем с пометкой «(продолжение)» и повтором шапки таблицы; номера листов проставляются после раскладки
PAGINATE = r"""<script>(function(){
var mm=96/25.4,tpl=document.getElementById('pgt'),src=document.getElementById('src'),pages=[];
function np(){var pg=tpl.content.firstElementChild.cloneNode(true);document.body.insertBefore(pg,src);pages.push(pg);return pg.querySelector('.flow');}
function ok(f){var l=f.lastElementChild;return !l||l.getBoundingClientRect().bottom<=f.getBoundingClientRect().bottom-1.5*mm;}
var flow=np();
[].slice.call(src.children).forEach(function(blk){
  if(blk.getAttribute('data-k')!=='g'){flow.appendChild(blk);if(!ok(flow)){flow=np();flow.appendChild(blk);}return;}
  var head=blk.querySelector('.ck-g'),table=blk.querySelector('table'),rows=[].slice.call(table.tBodies[0].rows);
  function mk(cont){var h=head.cloneNode(true);if(cont)h.querySelector('h2').textContent+=' (продолжение)';
    var t=table.cloneNode(false);t.innerHTML=table.querySelector('colgroup').outerHTML+table.tHead.outerHTML+'<tbody></tbody>';
    flow.appendChild(h);flow.appendChild(t);return t.tBodies[0];}
  var tb=mk(false),started=false;
  rows.forEach(function(r){
    tb.appendChild(r);
    if(ok(flow))return;
    tb.removeChild(r);
    if(!tb.rows.length){var t=tb.parentNode;t.previousElementSibling.remove();t.remove();flow=np();tb=mk(started);}
    else{flow=np();tb=mk(true);}
    tb.appendChild(r);
  });
  started=true;
});
src.remove();
pages.forEach(function(p,i){p.querySelector('.pno').textContent=(i+1)+' из '+pages.length;});
window.__pages=pages.length;window.__done=true;
})();</script>"""


def ck_html():
    gt = {g[0]: (g[1], g[2]) for g in DK.GROUPS}
    meta_ck = ('<div class="meta"><div class="meta-l"><span>Чек-лист документов к проверке Роспотребнадзора</span></div>'
               f'<div class="meta-r"><b>{DK_FORM}</b></div></div>')
    foot = (f'<footer class="ft"><div><b>ПЕСТКОНТРОЛЬ Центр</b> · {CO["legal"]} · ИНН {CO["inn"]} · КПП {CO["kpp"]} · ОГРН {CO["ogrn"]}<br>'
            f'Лицензия Роспотребнадзора {CO["lic"]} · {CO["addr"]}<br>{CO["phone"]} · {CO["mail"]} · {CO["site"]}</div>'
            f'<div class="pn"><span class="fm">{DK_FORM}</span><span>Лист</span><span class="pno"></span></div></footer>')
    tpl = f'<template id="pgt"><section class="pg">{WM}{header()}{meta_ck}<div class="flow"></div>{foot}</section></template>'
    blocks = ['<div class="blk" data-k="intro">'
              '<div class="ck-h1">Чек-лист документов для проверки Роспотребнадзора</div>'
              '<p class="ck-sub">Отметьте, что уже есть в папке объекта. Документы с пометкой «Для:» нужны только перечисленным '
              'объектам, остальные — всем, кто ведёт деятельность в помещении. Перечень составлен по официальному перечню сведений, '
              'которые запрашивает Роспотребнадзор, СанПиН 3.3686-21 и проверочным листам 2026 года (приказы №&nbsp;578 и №&nbsp;580). '
              'Онлайн-версия со сборщиком папки для 14 типов объектов — на сайте пестконтроль-центр.рф, раздел «Нормативная база».</p>'
              '<div class="ck-f"><div class="k">Объект, адрес</div>' + fld('', 1) + '<div class="k">Тип объекта</div>' + fld('', 1) +
              '<div class="k">Ответственный</div>' + fld('', 1) + '<div class="k">Дата сверки</div>' + fld('', 1) + '</div></div>']
    n = 0
    for gid, num, title, _ in DK.GROUPS:
        rows, n = ck_rows(gid, n)
        blocks.append(f'<div class="blk" data-k="g"><div class="ck-g"><span class="n">{num}</span><h2>{H.escape(title)}</h2></div>'
                      + ck_table(rows) + '</div>')
    rows = ''
    for code, lab, _s, _g in DK.OBJECTS:
        kit = DK.KITS.get(code)
        form = kit[0] if kit else ''
        q = kit[2] if kit and kit[2] else '—'
        rows += f'<tr><td>{H.escape(lab)}</td><td>{H.escape(form)}</td><td>{H.escape(q)}</td></tr>'
    blocks.append('<div class="blk" data-k="obj"><div class="ck-g"><span class="n">+</span><h2>Проверочные листы по типам объектов</h2></div>'
                  '<table class="t"><colgroup><col style="width:62mm"><col style="width:46mm"><col></colgroup>'
                  '<thead><tr><th>Объект</th><th>Форма проверочного листа</th><th>Вопросы о насекомых и грызунах</th></tr></thead>'
                  '<tbody>' + rows + '</tbody></table>'
                  '<p class="ck-leg">Если отдельной формы нет, инспектор проверяет по общим требованиям: дезинсекция и дератизация — '
                  'раздел III СанПиН 3.3686-21, для пищевых производств — ещё и ТР ТС 021/2011 (ст. 10). '
                  'Срок ответа на требование документов — 10 рабочих дней.</p></div>')
    body = tpl + '<div id="src">' + ''.join(blocks) + '</div>' + PAGINATE
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Чек-лист документов для проверки Роспотребнадзора</title>'
            f'<style>{journal_css()}{CSS_AKT}</style></head><body>{body}</body></html>')


DK_FORM = f'Чек-лист ЧДР-01 · ред.{NB}11.2026'

# ---------------------------------------------------------------- сборка
META = {
    'akt': (DK.AKT_PDF, 'Образец акта обследования и выполненных работ по дезинсекции и дератизации — ПЕСТКОНТРОЛЬ Центр',
            'Образец заполнения акта (форма АПК-01, 2 листа): обследование по контурам, работы со средствами, контроль эффективности, рекомендации'),
    'blank': (DK.AKT_BLANK, 'Бланк акта обследования и выполненных работ по дезинсекции и дератизации — ПЕСТКОНТРОЛЬ Центр',
              'Бланк акта (форма АПК-01, 2 листа) для печати; совпадает с образцом заполнения лист в лист'),
    'ck': (DK.CHECKLIST_PDF, 'Чек-лист документов для проверки Роспотребнадзора — ПЕСТКОНТРОЛЬ Центр',
           'Все документы к проверке Роспотребнадзора с отметками «есть / нет / не требуется» и проверочные листы по типам объектов'),
}
AUTHOR = 'ПЕСТКОНТРОЛЬ Центр (ООО «Центр дезинфекционных услуг»)'
KEYS = ('акт дезинсекции, акт дератизации, акт выполненных работ, образец, бланк, документы для Роспотребнадзора, '
        'чек-лист, проверочный лист, СанПиН 3.3686-21, пестконтроль-центр.рф')


def node(*args):
    env = dict(os.environ)
    env['NODE_PATH'] = env.get('NODE_PATH', '') + os.pathsep + '/home/user/node_modules'
    r = subprocess.run(['node', str(HERE / 'render_akt.mjs'), *map(str, args)], capture_output=True, text=True, env=env)
    if r.returncode:
        raise SystemExit('render_akt.mjs: ' + r.stderr[-2000:])
    return r.stdout


def finalize():
    import pymupdf
    from PIL import Image
    DST.mkdir(parents=True, exist_ok=True)
    for key, (fn, title, subject) in META.items():
        d = pymupdf.open(OUT / f'{key}.pdf')
        d.set_metadata({'title': title, 'author': AUTHOR, 'subject': subject, 'keywords': KEYS,
                        'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
        d.save(DST / fn, garbage=4, deflate=True)
        print(f'  {fn}: {d.page_count} стр., {os.path.getsize(DST / fn)} байт')

    def preview(fn, pg, name, widths):
        pix = pymupdf.open(DST / fn)[pg].get_pixmap(dpi=200)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        for w in widths:
            out = (IMG if name.startswith('akt-') else OUT) / f'{name}-{w}.webp'
            h = round(w * 509 / 360)  # пропорции A4, как в разметке страницы (360 × 509)
            im.resize((w, h), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6)
            print('  ', out.name)
    preview(DK.AKT_PDF, 0, 'akt-obrazets-p1', [360, 720])
    preview(DK.CHECKLIST_PDF, 0, 'ck-p1', [720])


def main():
    global WM
    OUT.mkdir(parents=True, exist_ok=True)
    WM = watermark_svg(FONTS, length_mm=232, color='#7c4dff', opacity=0.12)
    (OUT / 'akt.html').write_text(akt_html(), encoding='utf-8')
    (OUT / 'cheklist.html').write_text(ck_html(), encoding='utf-8')
    qa = node('pdf', OUT)
    print(qa.strip())
    finalize()
    print(node('og', OUT, IMG / 'akt-obrazets-p1-720.webp', OUT / 'ck-p1-720.webp', IMG / 'dk-og.jpg').strip())


if __name__ == '__main__':
    main()
