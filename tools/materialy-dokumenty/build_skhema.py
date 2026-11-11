#!/usr/bin/env python3
"""Образец план-схемы точек пест-контроля (форма СТПК-01, 2 листа A4) для страницы /materialy/skhema-tochek-pest-kontrolya/.

    python3 tools/materialy-dokumenty/build_skhema.py
        → materialy/skhema-tochek-pest-kontrolya/obrazets-skhemy-tochek-pest-kontrolya.pdf
        → img/skhema-obrazets-p1-360.webp, img/skhema-obrazets-p1-720.webp (превью первого листа для страницы)
        и img/skhema-obrazets-p2-*.webp (второй лист — реестр); только превью: build_skhema.py --previews

Объект, номера и места 30 точек — как в образцах журнала (tools/zhurnal, журнал № ПК-0917/26, раздел 2) и акта
(tools/akt, акт 0917-04): данные — skhema_data.py, тот же план, что на странице сайта. Шапка, подвал, водяной знак
и стили листа — общие с актом и журналом (tools/akt/build_akt.py, tools/zhurnal); водяной знак проверяется
tools/docs_brand/check_watermark.py, как у акта. Нужны Node.js с playwright, PyMuPDF и Pillow.
"""
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tools' / 'akt'))
sys.path.insert(0, str(ROOT / 'tools' / 'zhurnal'))
import build_akt as A  # noqa: E402  шапка, подвал, стили и подписи — как в акте
import skhema_data as S  # noqa: E402
from wm import watermark_svg  # noqa: E402

NB = '\u00a0'
OUT = pathlib.Path(os.environ.get('SKHEMA_OUT', '/tmp/skhema-build'))
DST = ROOT / 'materialy' / 'skhema-tochek-pest-kontrolya'
PDF = 'obrazets-skhemy-tochek-pest-kontrolya.pdf'
FORM = f'Форма СТПК-01 · ред.{NB}11.2026'
NO, RED = 'ПК-0917/26-С', f'ред.{NB}2 от 21.10.2026'

CSS = r"""
.s-plan{border:.25mm solid #a1a1aa;border-radius:1.2mm;overflow:hidden;margin-top:1.2mm}
.s-plan svg{display:block;width:100%;height:auto}
.s-leg{display:grid;grid-template-columns:1.05fr 1fr;gap:4mm;margin-top:2.4mm}
.s-leg .box{padding:2.2mm 2.8mm}
.s-leg ul{list-style:none;margin:0;padding:0;display:grid;row-gap:1.1mm;font-size:7pt;line-height:1.3}
.s-leg li{display:flex;align-items:center;gap:2mm}
.s-leg li svg{flex:none;width:4.2mm;height:4.2mm}
.s-leg li b{font-weight:700;min-width:7.5mm}
.s-leg .ln{flex:none;width:9mm;height:0;border-top:.8mm solid;border-radius:.4mm}
.s-leg .ln.dot{border-top-style:dotted}
.s-leg .c{margin-left:auto;color:#52525b;white-space:nowrap}
.s-red td.d{white-space:nowrap}
.t td.code{font-weight:700;white-space:nowrap}
.t td.k1{color:#15803d}.t td.k2{color:#c2410c}.t td.k3{color:#1d4ed8}
"""


def legend():
    c = S.counts()
    types = ''.join(f'<li>{svg}<b>{t}</b>{name}</li>' for t, name, svg in S.legend_items())
    cont = ''.join(f'<li><span class="ln{" dot" if k == "К3" else ""}" style="border-color:{col}"></span><b>{k}</b>{name}'
                   f'<span class="c">{c[k]} ТПК</span></li>' for k, (name, col) in S.K.items())
    return (f'<div class="s-leg"><div class="box"><h3>Контуры защиты</h3><ul>{cont}'
            f'<li><span class="ln" style="border-color:#8a8f86;border-top-style:dashed;border-top-width:.4mm"></span>'
            f'<b></b>Ограждение территории<span class="c">всего 30 ТПК</span></li></ul></div>'
            f'<div class="box"><h3>Типы точек контроля</h3><ul>{types}</ul></div></div>')


def page1():
    top = (f'<div class="a-top"><div><div class="a-kicker">Пест-контроль · ГОСТ Р 54762-2011, п.{NB}12.5</div>'
           f'<div class="a-h1">ПЛАН-СХЕМА</div><div class="a-sub">точек пест-контроля (ТПК) объекта · приложение 1 к журналу '
           f'пест-контроля №{NB}ПК-0917/26</div></div>'
           f'<div class="a-no"><span>№</span><span class="a-nobox">{A.ink(NO)}</span><span>ред.</span>'
           f'<span class="a-nobox">{A.ink("2 · 21.10.2026")}</span></div></div>')
    plan = A.sec(1, 'План объекта: хлебопекарный цех, 1 850 м² здания, 3 200 м² территории') + \
        f'<div class="s-plan">{S.plan_svg(web=False)}</div>' + legend()
    red = (A.sec(2, 'Редакции схемы') +
           '<table class="t s-red"><colgroup><col style="width:22mm"><col style="width:16mm"><col><col style="width:30mm"></colgroup>'
           '<tr><th>Дата</th><th>Ред.</th><th>Что изменено и почему</th><th>Подписи сторон</th></tr>'
           f'<tr><td class="d">{A.ink("02.09.2026")}</td><td class="c">{A.ink("1")}</td><td>{A.ink("Установлены 30 ТПК по итогам первичного обследования 28.08.2026: К1 — 8, К2 — 8, К3 — 14")}</td>'
           f'<td>{A.sig("smirnov", 3.2)} {A.sig("ivanova", 3.2)}</td></tr>'
           f'<tr><td class="d">{A.ink("21.10.2026")}</td><td class="c">{A.ink("2")}</td><td>{A.ink(f"МЛ-10 перенесена на 0,5{NB}м к углу стеллажа А-2, ближе к вводу кабеля (журнал, раздел 2.1)")}</td>'
           f'<td>{A.sig("smirnov", 3.2)} {A.sig("ivanova", 3.2)}</td></tr>'
           '<tr><td>&nbsp;</td><td></td><td></td><td></td></tr></table>')
    sg = ('<div class="sgg">'
          f'<div class="sgb"><div class="k" style="font-size:6.6pt;color:#71717a">Схему составил — Исполнитель</div>'
          f'<div style="margin-top:1.4mm">{A.ink(f"Смирнов А.{NB}Н., инженер пест-менеджер")} {A.sig("smirnov")}</div></div>'
          f'<div class="sgb"><div class="k" style="font-size:6.6pt;color:#71717a">Согласовано — Заказчик</div>'
          f'<div style="margin-top:1.4mm">{A.ink(f"Иванова Е.{NB}В., менеджер по качеству")} {A.sig("ivanova")}</div></div></div>')
    return meta() + top + plan + red + sg


def meta():
    return (f'<div class="meta"><div class="meta-l"><span>Схема №</span>{A.sl(A.ink(NO), 26)}<span>Объект</span>'
            f'{A.sl(A.ink(A.OBJ_SHORT), 47)}</div>'
            f'<div class="meta-r"><span class="badge only-s">Образец заполнения</span><b>{FORM}</b></div></div>')


def page2():
    rows = ''.join(
        f'<tr><td class="code k{k[-1]}">{code}</td><td>{S.T[code.split("-")[0]][0]}</td><td class="c k{k[-1]}">{k}</td>'
        f'<td>{place}</td><td class="c">{thr}</td></tr>'
        for code, k, place, thr, *_ in S.POINTS)
    reg = (A.sec(3, 'Реестр точек к схеме') +
           '<p class="lead">Номера совпадают с настенными указателями и разделом 2 журнала пест-контроля. Порог для КИК — доля '
           'съеденной приманки, для ИЛ и ФЛ — особей за 14 суток, для остальных точек — любая находка.</p>'
           '<table class="t"><colgroup><col style="width:16mm"><col style="width:50mm"><col style="width:13mm"><col>'
           '<col style="width:19mm"></colgroup><tr><th>№ ТПК</th><th>Тип устройства</th><th class="c">Контур</th>'
           f'<th>Место установки</th><th class="c">Порог</th></tr>{rows}</table>')
    rules = (A.sec(4, 'Как применять схему') + '<ol class="rules">'
             '<li>Схема — приложение к программе пест-контроля и журналу. Экземпляры есть у Заказчика (в папке объекта) и у '
             'Исполнителя; на проверке её сверяют с журналом и с точками на месте.</li>'
             '<li>У каждой точки уникальный номер: префикс типа и порядковый номер. Номер на схеме, на настенном указателе и в '
             'журнале один и тот же; повторно номер не используют.</li>'
             '<li>При переносе, установке или снятии точки специалист Исполнителя делает запись в разделе 2.1 журнала, '
             'а схема получает новую редакцию с датой и подписями сторон. Старая редакция хранится вместе с новой.</li>'
             '<li>Станции с родентицидами — только запираемые и закреплённые, на территории. В помещениях с пищевой продукцией '
             'применяют ловушки и мониторы без ядов.</li>'
             '<li>Масштаб плана условный. Для точного размещения используйте поэтажные планы БТИ или технический план объекта.</li>'
             '</ol>'
             '<p class="fine"><b>Форма СТПК-01</b> — форма ПЕСТКОНТРОЛЬ Центра, а не утверждённая государственная. План '
             'размещения датчиков обнаружения и ловушек требует п.&nbsp;12.5 ГОСТ Р 54762-2011 (ISO/TS 22002-1), на него '
             'опираются аудиты ХАССП, FSSC 22000 и торговых сетей. Образец выполнен для вымышленного объекта, '
             'заказчик обезличен.</p>')
    return meta() + reg + rules


def html():
    body = A.page(page1(), 1, 2).replace(A.FORM, FORM) + A.page(page2(), 2, 2).replace(A.FORM, FORM)
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>План-схема точек пест-контроля — образец'
            f'</title><style>{A.journal_css()}{A.CSS_AKT}{CSS}</style></head><body>{body}</body></html>')


def render():
    js = r"""
import { chromium } from 'playwright';
const dir = process.argv[2];
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
await pg.goto('file://' + dir + '/skhema.html', { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
const qa = await pg.evaluate(() => [...document.querySelectorAll('.pg')].map((p, i) => {
  const ft = p.querySelector('.ft'), prev = ft.previousElementSibling;
  const over = [...p.querySelectorAll('td,.sl,.a-nobox')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.innerText.slice(0, 40));
  return { page: i + 1, gap_mm: Math.round((ft.getBoundingClientRect().top - prev.getBoundingClientRect().bottom) * 25.4 / 96), over };
}));
console.log(JSON.stringify(qa));
await pg.pdf({ path: dir + '/skhema.pdf', preferCSSPageSize: true, printBackground: true });
await b.close();
"""
    (OUT / 'render.mjs').write_text(js, encoding='utf-8')
    env = dict(os.environ)
    env['NODE_PATH'] = env.get('NODE_PATH', '') + os.pathsep + '/home/user/node_modules'
    # ESM не видит NODE_PATH — запускаем из каталога с node_modules через ссылку
    nm = OUT / 'node_modules'
    if not nm.exists():
        nm.symlink_to('/home/user/node_modules')
    r = subprocess.run(['node', str(OUT / 'render.mjs'), str(OUT)], capture_output=True, text=True, env=env, cwd=OUT)
    if r.returncode:
        raise SystemExit('render: ' + r.stderr[-2000:])
    print(r.stdout.strip())


def finalize():
    import pymupdf
    from PIL import Image
    sys.path.insert(0, str(ROOT / 'tools' / 'docs_brand'))
    from check_watermark import audit
    bad = [r for r in audit(str(OUT / 'skhema.pdf')) if r[1] != 'поверх']
    if bad:
        raise SystemExit(f'{PDF}: водяной знак закрыт или отсутствует {bad}')
    print('  водяной знак поверх содержимого на всех листах')
    DST.mkdir(parents=True, exist_ok=True)
    d = pymupdf.open(OUT / 'skhema.pdf')
    d.set_metadata({'title': 'Образец план-схемы точек пест-контроля — ПЕСТКОНТРОЛЬ Центр', 'author': A.AUTHOR,
                    'subject': 'Образец заполнения план-схемы ТПК (форма СТПК-01, 2 листа): план объекта с контурами защиты, '
                               '30 точек контроля, редакции, реестр точек',
                    'keywords': 'схема точек пест-контроля, план-схема ТПК, схема расположения ловушек, образец, '
                                'ГОСТ Р 54762-2011, ХАССП, пестконтроль-центр.рф',
                    'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
    d.save(DST / PDF, garbage=4, deflate=True)
    print(f'  {PDF}: {d.page_count} стр., {os.path.getsize(DST / PDF)} байт')
    previews()


def previews():
    """Превью листов PDF для страницы: лист 1 (план) и лист 2 (реестр точек; с 11.11.2026 — для варианта блока
    с двумя листами). Только картинки из готового PDF: python3 tools/materialy-dokumenty/build_skhema.py --previews"""
    import pymupdf
    from PIL import Image
    doc = pymupdf.open(DST / PDF)
    for n in (1, 2):
        pix = doc[n - 1].get_pixmap(dpi=200)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        for w in (360, 720):
            out = ROOT / 'img' / f'skhema-obrazets-p{n}-{w}.webp'
            im.resize((w, round(w * 509 / 360)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6)
            print('  ', out.name, os.path.getsize(out) // 1024, 'КБ')


def main():
    if '--previews' in sys.argv:
        return previews()
    OUT.mkdir(parents=True, exist_ok=True)
    A.WM = watermark_svg(A.FONTS, length_mm=232, color='#7c4dff', opacity=0.18)
    (OUT / 'skhema.html').write_text(html(), encoding='utf-8')
    render()
    finalize()


if __name__ == '__main__':
    main()
