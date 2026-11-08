#!/usr/bin/env python3
"""Опросный лист заказчика в PDF: «для ППК» и «для ППК по ХАССП» (содержание — content.py).

    NODE_PATH=/home/user/node_modules python3 tools/razrabotka-ppk/oprosnyy/build_pdf.py

Оформление — как у остальных документов сайта (tools/docs_brand): на первом листе полная шапка с логотипом,
телефоном и адресом сайта, на следующих — компактная строка; диагональный водяной знак «пестконтроль-центр.рф»
поверх содержимого на каждом листе (правило владельца 08.11.2026; проверка — tools/docs_brand/check_watermark.py).
Листы раскладывает render_pdf.mjs (Chromium): вопросы переносятся на следующий лист целыми строками, заголовок
раздела повторяется с пометкой «продолжение», в подвале — «Лист N из M».

Результат: razrabotka-ppk/oprosnyy-list-ppk.pdf, razrabotka-ppk/oprosnyy-list-ppk-po-haccp.pdf,
превью первого листа img/oprosnyy-{ppk,haccp}-p1-{240,360,720}.webp, сводка tools/razrabotka-ppk/oprosnyy/pdf.json
(число листов и размер — их показывает страница).
"""
import html
import io
import json
import os
import pathlib
import subprocess
import sys

import pymupdf as fitz
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'docs_brand'))
sys.path.insert(0, str(HERE))
import brand  # noqa: E402
from content import (COMMENT, DOCS_ALL, DOCS_HACCP, NB, OBJECT_TYPES, PROGRAMS, sections)  # noqa: E402

FONTS = ROOT / 'fonts'
TMP = pathlib.Path('/tmp/oprosnyy_build')
CO = {
    'legal': 'ООО «Центр дезинфекционных услуг»', 'inn': '7714462211',
    'lic': f'№{NB}Л064-00111-77/01942445', 'mail': 'b2b@pestcontrol-center.ru',
}
REV = f'ред.{NB}11.2026'

CSS = r"""
@page{size:A4 portrait;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:Inter,Arial,sans-serif;color:#18181b;font-size:8.6pt;line-height:1.35;-webkit-print-color-adjust:exact;print-color-adjust:exact}
#src{position:absolute;left:-10000px;top:0;width:182mm}
.pg{width:210mm;height:297mm;padding:9mm 12mm 8mm 16mm;position:relative;overflow:hidden;break-after:page;page-break-after:always;display:flex;flex-direction:column;background:#fff}
.pg:last-child{break-after:auto;page-break-after:auto}
.pg>.bd{flex:1;min-height:0;display:flex;flex-direction:column;margin-top:4mm}
.wm{position:absolute;left:50%;top:54%;transform:translate(-50%,-50%) rotate(-45deg);z-index:30;pointer-events:none}
.pg>*:not(.wm){position:relative;z-index:1}
/* подвал */
.ft{margin-top:3mm;padding-top:2mm;border-top:.25mm solid #d4d4d8;display:flex;justify-content:space-between;align-items:flex-end;gap:6mm;font-size:6pt;color:#71717a;line-height:1.45}
.ft b{color:#18181b;font-weight:600}
.ft .pn{text-align:right;white-space:nowrap;font-size:6.6pt}
.ft .pn b{font-size:8pt}
/* титул */
.tt{margin:5mm 0 2mm}
.kick{font-size:7.6pt;font-weight:650;letter-spacing:.16em;text-transform:uppercase;color:#615fff}
h1{font-size:19pt;line-height:1.12;letter-spacing:-.025em;font-weight:750;margin:2.4mm 0 2.6mm;color:#09090b}
.sub{font-size:9pt;color:#3f3f46;line-height:1.45;margin:0;max-width:168mm}
.how{display:grid;grid-template-columns:1fr 1.2fr 1fr;gap:3mm;margin:4.2mm 0 0}
.how>div{border:.3mm solid #c7c7f5;border-radius:1.6mm;padding:2.4mm 3mm;font-size:7.4pt;line-height:1.42;color:#3f3f46}
.how b{display:block;font-size:6.6pt;letter-spacing:.12em;text-transform:uppercase;color:#615fff;margin-bottom:1.2mm}
.how strong{color:#09090b;font-weight:650}
.nw{white-space:nowrap}
/* заголовок раздела */
.sh{display:grid;grid-template-columns:auto 1fr;column-gap:2.6mm;align-items:baseline;margin:3.8mm 0 1.4mm}
.sh .n{font-size:7.4pt;font-weight:700;color:#fff;background:#615fff;border-radius:1mm;padding:.5mm 1.9mm;position:relative;top:-.3mm}
.sh h2{font-size:11.6pt;font-weight:700;letter-spacing:-.01em;margin:0;line-height:1.2}
.sh h2 small{font-size:7.4pt;font-weight:500;color:#71717a;letter-spacing:0;margin-left:1.6mm}
.sh .why{grid-column:2;margin:.8mm 0 0;font-size:6.9pt;color:#71717a;line-height:1.35}
.sh .tag{display:inline-block;margin-left:2mm;font-size:6.2pt;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:#615fff;border:.25mm solid #615fff;border-radius:.8mm;padding:.2mm 1.4mm;vertical-align:.25em}
/* вопросы */
table.qt,table.dt{width:100%;border-collapse:collapse;table-layout:fixed}
.qt td{border-top:.2mm solid #b4b4bc;padding:1.3mm 1.4mm 1.4mm;vertical-align:top}
.qt tr:last-child td{border-bottom:.2mm solid #b4b4bc}
.qt td.no{color:#615fff;font-weight:650;font-size:8pt;padding-left:0}
.qt td.qq b{display:block;font-weight:600;font-size:8.6pt;line-height:1.3;color:#18181b}
.qt td.qq small{display:block;margin-top:.7mm;font-size:6.7pt;color:#71717a;line-height:1.3}
.qt td.aa{padding-right:0}
.ln{height:6.3mm;border-bottom:.22mm solid #8a8a94}
.ln+.ln{margin-top:0}
.opts{display:flex;flex-wrap:wrap;gap:1.5mm 4.2mm;padding-top:.6mm;font-size:8pt;line-height:1.3}
.o{display:inline-flex;align-items:flex-start;gap:1.5mm;white-space:nowrap}
.cb{flex:none;display:inline-block;width:3.2mm;height:3.2mm;border:.28mm solid #52525b;border-radius:.5mm;position:relative;top:.25mm}
.rd .cb{border-radius:50%}
.lx{display:flex;align-items:flex-end;gap:2mm;height:6.3mm;border-bottom:.22mm solid #8a8a94;margin-top:.4mm}
.lx small{font-size:6.6pt;color:#71717a;padding-bottom:.8mm;white-space:nowrap}
.types{display:grid;grid-template-columns:1fr 1.25fr;grid-auto-flow:column;grid-template-rows:repeat(5,auto);gap:1.3mm 3mm;padding-top:.6mm;font-size:8pt}
.types .o{white-space:normal}
/* документы и подпись */
.dt td{border-top:.2mm solid #d4d4d8;padding:1.25mm 1.4mm;vertical-align:top;font-size:8.2pt;line-height:1.35}
.dt tr:last-child td{border-bottom:.2mm solid #d4d4d8}
.dt td.c{width:7mm;padding-left:0}
.dt tr.sub td{border-top:.3mm solid #b4b4bc;padding-top:2.4mm;font-size:7pt;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:#615fff}
.note{font-size:7.2pt;color:#52525b;line-height:1.45;margin:2mm 0 0}
.sign{margin-top:4.4mm;border:.3mm solid #09090b;border-radius:1.4mm;padding:3mm 4mm}
.sign h3{margin:0 0 2.6mm;font-size:8.2pt;text-transform:uppercase;letter-spacing:.1em}
.sg{display:grid;grid-template-columns:1.35fr 1fr .9fr;gap:5mm;align-items:end}
.sg>div .ln{height:8mm}
.sign em{display:block;font-style:normal;font-size:6.2pt;color:#71717a;margin-top:.8mm}
.sg2{display:grid;grid-template-columns:1fr;margin-top:2.4mm}
"""


def esc(s):
    return html.escape(s, quote=False)


def q_row(no, label, kind, p):
    hint = p.get('hint') or p.get('ph') or ''
    qq = f'<b>{esc(label)}</b>' + (f'<small>{esc(hint)}</small>' if hint else '')
    if kind in ('text',):
        aa = '<div class="ln"></div>'
    elif kind == 'area':
        aa = '<div class="ln"></div>' * p.get('lines', 2)
    elif kind == 'type':
        aa = '<div class="types">' + ''.join(f'<span class="o rd"><i class="cb"></i>{esc(t)}</span>' for t, _ in OBJECT_TYPES) + '</div>'
    else:
        cls = 'o rd' if kind == 'radio' else 'o'
        aa = '<div class="opts">' + ''.join(f'<span class="{cls}"><i class="cb"></i>{esc(o)}</span>' for o in p['opts']) + '</div>'
        if p.get('extra'):
            aa += f'<div class="lx"><small>{esc(p["extra"])}:</small></div>'
    return f'<tr data-q="{no}"><td class="no">{no}</td><td class="qq">{qq}</td><td class="aa">{aa}</td></tr>'


def colgroup():
    return '<colgroup><col style="width:9mm"><col style="width:66mm"><col></colgroup>'


def section_blocks(s):
    tag = '<span class="tag">ППК по ХАССП</span>' if s.get('haccp') else ''
    head = (f'<div class="blk sh" data-sec="{s["n"]}" data-title="{esc(s["title"])}"><span class="n">{s["n"]}</span>'
            f'<h2>{esc(s["title"])}{tag}</h2><p class="why">Для чего: {esc(s["why"])}</p></div>')
    rows = ''.join(q_row(no, label, kind, p) for no, label, kind, p in s['q'])
    return head + f'<table class="blk qt" data-sec="{s["n"]}">{colgroup()}<tbody>{rows}</tbody></table>'


def build_html(prog):
    P = PROGRAMS[prog]
    secs = sections(prog)
    title = P['title']
    price = (f'<strong>ППК по ХАССП — от 19{NB}900{NB}₽</strong>, срок — 3{NB}рабочих дня' if prog == 'haccp'
             else f'<strong>ППК — от 5{NB}900{NB}₽</strong>, срок — 1{NB}рабочий день')
    n_extra, n_docs = str(len(secs) + 1), str(len(secs) + 2)
    tt = (f'<div class="blk tt"><div class="kick">Опросный лист заказчика · {esc(P["short"])}</div><h1>{esc(title)}</h1>'
          '<p class="sub">Ответы нужны, чтобы программа описывала именно ваш объект: помещения, персонал, оборудование'
          + (', продукцию и технологические процессы' if prog == 'haccp' else '') +
          '. По заполненному листу назовём точную стоимость и срок. Отвечайте на то, что знаете, — остальное уточним по телефону.</p>'
          '<div class="how">'
          f'<div><b>Куда отправить</b><strong>{CO["mail"]}</strong><br>в теме письма — название организации; документы из раздела{NB}{n_docs} — к этому же письму</div>'
          f'<div><b>Или заполните онлайн</b><strong class="nw">пестконтроль-центр.рф/razrabotka-ppk</strong><br>блок «Опросный лист заказчика» — ответы придут нам вместе с вашими контактами</div>'
          f'<div><b>Цена и срок</b>{price} после получения ответов. Вопросы — по телефону <strong class="nw">{brand.CO["phone"]}</strong></div>'
          '</div></div>')
    blocks = [tt] + [section_blocks(s) for s in secs]
    _, label, kind, p = COMMENT
    blocks.append(f'<div class="blk sh" data-sec="{n_extra}" data-title="Дополнительно"><span class="n">{n_extra}</span><h2>Дополнительно</h2>'
                  '<p class="why">Для чего: всё, что поможет учесть особенности объекта</p></div>')
    blocks.append(f'<table class="blk qt" data-sec="{n_extra}">{colgroup()}<tbody>{q_row(n_extra + ".1", label, kind, p)}</tbody></table>')
    # документы
    dn = n_docs
    rows = ''.join(f'<tr><td class="c"><i class="cb"></i></td><td>{esc(d)}</td></tr>' for d in DOCS_ALL)
    if prog == 'haccp':
        rows += '<tr class="sub"><td colspan="2">Для ППК по ХАССП — ещё</td></tr>'
        rows += ''.join(f'<tr><td class="c"><i class="cb"></i></td><td>{esc(d)}</td></tr>' for d in DOCS_HACCP)
    blocks.append(f'<div class="blk sh" data-sec="{dn}" data-title="Документы, которые пригодятся"><span class="n">{dn}</span>'
                  '<h2>Документы, которые пригодятся</h2><p class="why">Отметьте и приложите к письму то, что есть. '
                  'Без документов тоже можно начать — по ответам выше.</p></div>')
    blocks.append(f'<table class="blk dt" data-sec="{dn}"><colgroup><col style="width:7mm"><col></colgroup><tbody>{rows}</tbody></table>')
    blocks.append('<div class="blk sign"><h3>Опросный лист заполнил</h3>'
                  '<div class="sg"><div><div class="ln"></div><em>должность, фамилия, имя, отчество</em></div>'
                  '<div><div class="ln"></div><em>подпись</em></div><div><div class="ln"></div><em>дата</em></div></div>'
                  '<div class="sg2"><div><div class="ln"></div><em>телефон и e-mail для связи</em></div></div></div>')
    wm = brand.watermark_svg(FONTS, length_mm=brand.WM['length_mm'], color=brand.WM['color'], opacity=brand.WM['opacity'])
    foot_l = (f'<div><b>ПЕСТКОНТРОЛЬ Центр</b> · {CO["legal"]} · ИНН {CO["inn"]} · лицензия Роспотребнадзора '
              f'<span style="white-space:nowrap">{CO["lic"]}</span><br>{brand.CO["phone"]} · {CO["mail"]} · пестконтроль-центр.рф</div>')
    tpl = (f'<template id="t-hd">{brand.header_html()}</template><template id="t-rh">{brand.runner_html()}</template>'
           f'<template id="t-wm">{wm}</template>'
           f'<template id="t-ft"><div class="ft">{foot_l}<div class="pn">Форма {P["code"]} · {REV}<br><b>Лист <span class="pi"></span> из <span class="pc"></span></b></div></div></template>')
    css = brand.font_css(FONTS) + brand.header_css() + brand.runner_css() + CSS
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{esc(title)} — ПЕСТКОНТРОЛЬ Центр</title>'
            f'<style>{css}</style></head><body>{tpl}<div id="src">{"".join(blocks)}</div><div id="pages"></div></body></html>')


def thumbs(pdf_path, prog):
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=200, alpha=False)
    im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
    out = []
    for w in (240, 360, 720):
        h = round(im.height * w / im.width)
        t = im.resize((w, h), Image.LANCZOS)
        p = ROOT / 'img' / f'oprosnyy-{prog}-p1-{w}.webp'
        t.save(p, 'WEBP', quality=82, method=6)
        out.append((p.name, p.stat().st_size, w, h))
    return out


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.setdefault('NODE_PATH', '/home/user/node_modules')
    summary = {}
    for prog, P in PROGRAMS.items():
        src = TMP / f'{prog}.html'
        src.write_text(build_html(prog), encoding='utf-8')
        raw = TMP / f'{prog}.pdf'
        r = subprocess.run(['node', str(HERE / 'render_pdf.mjs'), str(src), str(raw)], capture_output=True, text=True, env=env)
        if r.returncode:
            print(r.stdout, r.stderr)
            raise SystemExit('render_pdf.mjs: ошибка')
        qa = json.loads(r.stdout.strip().splitlines()[-1])
        assert not qa['overflow'], f'{prog}: содержимое не помещается на лист {qa["overflow"]}'
        doc = fitz.open(str(raw))
        doc.set_metadata({'title': P['title'], 'author': 'ООО «Центр дезинфекционных услуг» (ПЕСТКОНТРОЛЬ Центр)',
                          'subject': f'Опросный лист заказчика для разработки {P["short"]} — пестконтроль-центр.рф',
                          'keywords': 'опросный лист, анкета, разработка ППК, программа производственного контроля'
                                      + (', ХАССП' if prog == 'haccp' else ''),
                          'creator': 'пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
        out = ROOT / 'razrabotka-ppk' / P['file']
        doc.save(str(out), garbage=4, deflate=True, clean=True)
        pages = len(fitz.open(str(out)))
        summary[prog] = dict(file=P['file'], pages=pages, bytes=out.stat().st_size, title=P['title'],
                             thumbs=thumbs(str(out), prog), qa=qa)
        print(prog, P['file'], pages, 'стр.', out.stat().st_size // 1024, 'КБ', qa)
    (HERE / 'pdf.json').write_text(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'qa'} for k, v in summary.items()},
                                              ensure_ascii=False, indent=1), encoding='utf-8')
    files = [str(ROOT / 'razrabotka-ppk' / P['file']) for P in PROGRAMS.values()]
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'docs_brand' / 'check_watermark.py'), *files], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        raise SystemExit('водяной знак: проверка не пройдена')


if __name__ == '__main__':
    main()
