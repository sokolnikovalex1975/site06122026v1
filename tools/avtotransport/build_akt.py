#!/usr/bin/env python3
"""Образец и бланк акта дезинфекции автотранспорта (форма АДТ-01) для страницы /dezinfektsiya/avtotransport/.

    python3 tools/avtotransport/build_akt.py   → dezinfektsiya/avtotransport/*.pdf, img/avto-akt-obrazets-360/720.webp

Решение владельца 20.11.2026: образец акта в PDF — «сразу» (запросы Keys.so «акт дезинфекции автомобиля»,
«акт санобработки кузова», «бланк санобработки грузового автомобиля»). Один лист A4 на одну машину: машина с госномером,
восемь зон кузова и кабины (как на схеме страницы), средство и режим, условия, замечания, следующая обработка, подписи.

Система форм — та же, что у акта АПК-01 и журнала пест-контроля (tools/akt/build_akt.py, tools/zhurnal/build_journal.py):
стили листа, шапка с телефоном и сайтом, водяной знак «пестконтроль-центр.рф» поверх содержимого (проверка —
tools/docs_brand/check_watermark.py), образец и бланк печатаются из одного HTML (бланк — body.tpl, записи скрыты).
Отличие: в подвале нет адреса — он совпадает с адресом другого проекта владельца (закон независимости,
tools/site/independence_law.py, «новых таких совпадений не добавлять»). Заказчик обезличен, номер свидетельства скрыт.

Нужны: Node.js с playwright (/home/user/node_modules или NODE_PATH), PyMuPDF, Pillow, fontTools с brotli (шрифты woff2).
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'akt'))
import build_akt as A  # noqa: E402  стили, шапка, поля, подписи — общие с актом АПК-01
from wm import watermark_svg  # noqa: E402  (tools/zhurnal/wm.py, путь добавляет build_akt)

OUT = pathlib.Path(os.environ.get('AVTO_AKT_OUT', '/tmp/avto-akt-build'))
DST = ROOT / 'dezinfektsiya' / 'avtotransport'
IMG = ROOT / 'img'
NB = '\u00a0'
PDF_SAMPLE = 'obrazets-akta-dezinfektsii-avtotransporta.pdf'  # ссылки — tools/avtotransport/main.html и build_page.py
PDF_BLANK = 'blank-akta-dezinfektsii-avtotransporta.pdf'
FORM = f'Форма АДТ-01 · ред.{NB}11.2026'
CO = A.CO
ink, sl, fld, cb, sec, sig = A.ink, A.sl, A.fld, A.cb, A.sec, A.sig

CSS = r"""
.a-top{margin:3mm 0 .4mm}
.a-no{row-gap:1.2mm}
.a-nobox{width:34mm;height:7.4mm;line-height:6.8mm;font-size:10pt}
.mp{margin-top:.8mm}
.stamp-s{width:14mm;height:14mm;font-size:5.8pt}
.sgb{padding:2mm 3mm}
.a-h1s{font-size:15.5pt;font-weight:800;letter-spacing:-.02em;line-height:1.12;margin:1.4mm 0 0;max-width:118mm}
.a-h1s span{display:block;font-size:10pt;font-weight:500;letter-spacing:0;color:#3f3f46;margin-top:1mm}
.sec{margin:2.6mm 0 1.1mm}
.kv4{display:grid;grid-template-columns:27mm 1fr 27mm 1fr;column-gap:3mm;row-gap:.5mm;align-items:end}
.kv4>.k{font-size:6.8pt;color:#71717a;line-height:1.2;padding-bottom:.9mm}
.kv4>.wide{grid-column:2 / -1}
.kv4 .pr{font-size:7.4pt;line-height:1.35;padding-bottom:.9mm}
.t2 td{height:7mm;vertical-align:middle}
.zones{grid-template-columns:repeat(4,1fr);column-gap:3mm;row-gap:1.5mm;margin-top:.4mm}
.res2{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.res2 .box{padding:2mm 2.6mm}
.res2 .box h3{margin-bottom:1mm}
.res2 .chk{grid-template-columns:1fr;margin-top:.4mm;row-gap:1.1mm}
.sgg{margin-top:2.6mm}
.acc{margin-top:2.4mm}
.fine{margin-top:2.2mm}
"""

A_NO, A_DATE = 'АТ-1107-11', '20.11.2026'
PLATE = f'Х•••ХХ{NB}750'
SGR = 'RU.77.99.••.•••.Е.••••••.••.••'


def footer(n, total):
    return (f'<footer class="ft"><div><b>ПЕСТКОНТРОЛЬ Центр</b> · {CO["legal"]} · ИНН {CO["inn"]} · КПП {CO["kpp"]} · '
            f'ОГРН {CO["ogrn"]}<br>Лицензия Роспотребнадзора {CO["lic"]}<br>{CO["phone"]} · {CO["mail"]} · {CO["site"]}</div>'
            f'<div class="pn"><span class="fm">{FORM}</span><span>Лист</span><span>{n} из {total}</span></div></footer>')


def page(body, n, total, wm):
    return f'<section class="pg">{wm}{A.header()}{body}{footer(n, total)}</section>'


def meta():
    return (f'<div class="meta"><div class="meta-l"><span>Госномер</span>{sl(ink(PLATE), 26)}'
            f'<span>Тип кузова</span>{sl(ink("рефрижератор"), 30)}</div>'
            f'<div class="meta-r"><span class="badge only-s">Образец заполнения</span><b>{FORM}</b></div></div>')


def kv(pairs):
    out = ''
    for k, v in pairs:
        out += f'<div class="k">{k}</div><div>{fld(v)}</div>'
    return out


def akt_body():
    top = (f'<div class="a-top"><div><div class="a-kicker">Дезинфекция транспорта · ТР ТС 021/2011, ст.{NB}17</div>'
           f'<div class="a-h1s">АКТ<span>дезинфекции (санитарной обработки) транспортного средства</span></div></div>'
           f'<div class="a-no"><span>№</span><span class="a-nobox">{ink(A_NO)}</span><span>от</span>'
           f'<span class="a-nobox">{ink(A_DATE)}</span></div></div>')
    body = kv([('Дата и время', f'{A_DATE}, 05:40–05:55'), ('Вид работ', 'плановая, график 1 раз в месяц'),
               ('Место обработки', f'г.{NB}о.{NB}Мытищи, ул.{NB}Примерная, вл.{NB}3'), ('Заказчик', 'ООО «••••••••», ИНН 50••••••••'),
               ('Договор', f'№{NB}1107-ДТ/26 от 07.11.2026'), ('Представитель', f'Иванова Е.{NB}В., механик')])
    body += (f'<div class="k">Исполнитель</div><div class="wide pr"><b>{CO["legal"]}</b> (ПЕСТКОНТРОЛЬ Центр), ИНН {CO["inn"]}, '
             f'лицензия <span class="nw">{CO["lic"]}</span>; специалист {sl(ink(f"Смирнов А.{NB}Н., дезинфектор"), 56)}</div>')
    s1 = sec(1, 'Общие сведения') + f'<div class="kv4">{body}</div>'

    t2 = ('<table class="t t2"><colgroup><col style="width:24mm"><col style="width:36mm"><col><col style="width:46mm">'
          '<col style="width:24mm"></colgroup><thead><tr><th>Госномер</th><th>Тип кузова, объём</th><th>Что перевозит</th>'
          '<th>Холодильная установка</th><th>Кузов вымыт</th></tr></thead><tbody>'
          f'<tr><td>{ink(PLATE)}</td><td>{ink(f"рефрижератор 5{NB}т, 24{NB}м³")}</td>'
          f'<td>{ink(f"молочная продукция, +2…+6{NB}°C")}</td>'
          f'<td>{ink(f"выключена в 04:30, наледи нет, +8{NB}°C")}</td><td>{ink("Заказчиком, 05:10")}</td></tr>'
          '</tbody></table>')
    s2 = sec(2, 'Транспортное средство') + t2

    zones = [('Потолок, светильники', True), ('Стены, стыки панелей', True), ('Испаритель снаружи', True),
             ('Двери, уплотнители', True), ('Пол, трапы, сливы', True), ('Крепёж груза', True),
             ('Тара — по заявке', False), ('Кабина водителя', True)]
    lis = ''.join(f'<li>{cb(on)}<span>{i}. {t}</span></li>' for i, (t, on) in enumerate(zones, 1))
    s3 = sec(3, 'Что обработано — по порядку, сверху вниз и к дверям') + f'<ul class="chk zones">{lis}</ul>'

    t4 = ('<table class="t"><colgroup><col><col style="width:21mm"><col style="width:27mm"><col style="width:17mm">'
          '<col style="width:16mm"><col style="width:33mm"></colgroup><thead><tr><th>Средство: наименование, '
          'действующее вещество, номер СГР</th><th class="c">Концентрация</th><th>Способ</th><th class="c">Расход</th>'
          '<th class="c">Выдержка</th><th>Смыв после выдержки</th></tr></thead><tbody>'
          f'<tr><td style="height:9mm">{ink(f"Средство №{NB}2 по журналу: ЧАС и третичный амин, СГР {SGR}")}</td>'
          f'<td class="c">{ink(f"0,5{NB}%")}</td><td>{ink("орошение; кабина — протирание")}</td>'
          f'<td class="c">{ink(f"150{NB}мл/м²")}</td><td class="c">{ink(f"30{NB}мин")}</td>'
          f'<td>{ink("питьевой водой, где касается продукция")}</td></tr></tbody></table>')
    s4 = sec(4, 'Средство и режим — по инструкции по применению') + t4

    conds = ['Кузов разгружен и вымыт, остатков продукции нет', 'Установка выключена, кузов отогрет и сухой',
             'После выдержки — проветривание, двери открыты', 'Наклейка с датой следующей обработки — в кабине',
             f'Загрузка разрешена с {sl(ink("06:40"), 14)}']
    clis = ''.join(f'<li>{cb()}<span>{t}</span></li>' for t in conds)
    remark = ('Уплотнитель левой створки надорван у нижней петли — держит влагу, рекомендуем заменить. '
              'Следов насекомых и грызунов нет.')
    s5 = (sec(5, 'Условия и замечания') + '<div class="res2">'
          f'<div class="box"><h3>Условия обработки</h3><ul class="chk">{clis}</ul></div>'
          f'<div class="box"><h3>Замечания специалиста</h3>{fld(remark, 3)}</div></div>')

    s6 = (sec(6, 'Заключение') + '<div class="kv4">' +
          kv([('Следующая обработка', '20.12.2026, по графику договора'), ('Запись в журнале', f'журнал ТС {PLATE}, №{NB}4')]) +
          '</div>')

    sg = (f'<div class="acc">{cb()}<span>Дезинфекция выполнена в полном объёме. Заказчик с результатом '
          'и замечаниями ознакомлен, претензий по объёму, качеству и срокам не имеет.</span></div>'
          '<div class="sgg">'
          f'<div class="sgb"><div class="sgb-t">Исполнитель — {CO["legal"]}</div>'
          f'<div class="sgb-r"><div class="sgc">{sl(ink("дезинфектор"), 0)}<em>должность</em></div>'
          f'<div class="sgc">{sl(ink(f"Смирнов А.{NB}Н."), 0)}<em>ФИО</em></div></div>'
          f'<div class="sgb-r" style="margin-top:1.6mm"><div class="sgc">{sl(sig("smirnov"), 0)}<em>подпись</em></div>'
          f'<div class="sgc">{sl(ink(A_DATE), 0)}<em>дата</em></div></div>'
          '<div class="mp"><span>М.&nbsp;П.</span><span class="stamp-s">ПЕЧАТЬ</span></div></div>'
          f'<div class="sgb"><div class="sgb-t">Заказчик</div>'
          f'<div class="sgb-r"><div class="sgc">{sl(ink("механик автоколонны"), 0)}<em>должность</em></div>'
          f'<div class="sgc">{sl(ink(f"Иванова Е.{NB}В."), 0)}<em>ФИО</em></div></div>'
          f'<div class="sgb-r" style="margin-top:1.6mm"><div class="sgc">{sl(sig("ivanova"), 0)}<em>подпись</em></div>'
          f'<div class="sgc">{sl(ink(A_DATE), 0)}<em>дата</em></div></div>'
          '<div class="mp"><span>М.&nbsp;П. (при наличии)</span><span class="stamp-s">ПЕЧАТЬ</span></div></div>'
          '</div>')
    fine = ('<p class="fine"><b>Как применять форму.</b> Акт — на каждую машину, в двух экземплярах; копия — в кабине '
            'или в телефоне водителя, номер акта совпадает с записью в журнале. АДТ-01 — форма ПЕСТКОНТРОЛЬ Центра: единого '
            'бланка нормы не устанавливают, но требуют регулярной очистки, мойки и дезинфекции (ТР ТС 021/2011, ст.&nbsp;17, '
            'п.&nbsp;6), средств III–IV класса по инструкции (СанПиН 3.3686-21, п.&nbsp;131), для мяса — обработки после '
            'каждой перевозки (ТР ТС 034/2013, п.&nbsp;101).</p>')
    return meta() + top + s1 + s2 + s3 + s4 + s5 + s6 + sg + fine


def akt_html(wm):
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Акт дезинфекции (санитарной обработки) '
            f'транспортного средства — образец</title><style>{A.journal_css()}{A.CSS_AKT}{CSS}</style></head>'
            f'<body>{page(akt_body(), 1, 1, wm)}</body></html>')


META = {
    'akt': (PDF_SAMPLE, 'Образец акта дезинфекции автотранспорта — ПЕСТКОНТРОЛЬ Центр',
            'Образец заполнения акта дезинфекции (санитарной обработки) транспортного средства, форма АДТ-01, 1 лист'),
    'blank': (PDF_BLANK, 'Бланк акта санобработки транспортного средства — ПЕСТКОНТРОЛЬ Центр',
              'Бланк акта дезинфекции транспортного средства (форма АДТ-01, 1 лист) для печати; совпадает с образцом'),
}
AUTHOR = 'ПЕСТКОНТРОЛЬ Центр (ООО «Центр дезинфекционных услуг»)'
KEYS = ('акт дезинфекции автотранспорта, акт санобработки кузова, бланк санобработки грузового автомобиля, '
        'дезинфекция автотранспорта, санобработка транспортных средств, образец, бланк, пестконтроль-центр.рф')


def node(*args):
    env = dict(os.environ)
    env['NODE_PATH'] = env.get('NODE_PATH', '') + os.pathsep + '/home/user/node_modules'
    r = subprocess.run(['node', str(ROOT / 'tools' / 'akt' / 'render_akt.mjs'), *map(str, args)],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        raise SystemExit('render_akt.mjs: ' + r.stderr[-2000:])
    return r.stdout


def check_wm():
    sys.path.insert(0, str(ROOT / 'tools' / 'docs_brand'))
    from check_watermark import audit
    for key, (fn, _, _) in META.items():
        bad = [r for r in audit(str(OUT / f'{key}.pdf')) if r[1] != 'поверх']
        if bad:
            raise SystemExit(f'{fn}: водяной знак закрыт или отсутствует {bad} — знак должен лежать поверх содержимого')
    print('  водяной знак поверх содержимого (tools/docs_brand/check_watermark.py)')


def finalize():
    import pymupdf
    from PIL import Image
    check_wm()
    DST.mkdir(parents=True, exist_ok=True)
    for key, (fn, title, subject) in META.items():
        d = pymupdf.open(OUT / f'{key}.pdf')
        assert d.page_count == 1, f'{fn}: {d.page_count} стр. — форма должна умещаться на 1 лист'
        d.set_metadata({'title': title, 'author': AUTHOR, 'subject': subject, 'keywords': KEYS,
                        'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
        d.save(DST / fn, garbage=4, deflate=True)
        print(f'  {fn}: {d.page_count} стр., {os.path.getsize(DST / fn)} байт')
    pix = pymupdf.open(DST / PDF_SAMPLE)[0].get_pixmap(dpi=200)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    for w in (360, 720):
        out = IMG / f'avto-akt-obrazets-{w}.webp'
        im.resize((w, round(w * 509 / 360)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6)
        print('  ', out.name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wm = watermark_svg(A.FONTS, length_mm=232, color='#7c4dff', opacity=0.18)
    (OUT / 'akt.html').write_text(akt_html(wm), encoding='utf-8')
    print(node('pdf', OUT).strip())
    finalize()


if __name__ == '__main__':
    main()
