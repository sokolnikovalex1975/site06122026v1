#!/usr/bin/env python3
"""Документы при очистке и дезинфекции систем вентиляции и кондиционирования — образцы форм для сайта.

python3 tools/ventilyatsiya/docs/build_vent_docs.py <out_dir> [--site]

В <out_dir> собираются файлы Word и PDF (PDF — через LibreOffice):
  * комплект: перечень документов (обязательные и рекомендованные, основания, кто оформляет, где хранится),
    данные для актов и журналов, нормы, порядок оформления и 9 форм ВНТ-01…ВНТ-09, каждая с новой страницы;
  * каждая форма отдельным файлом (нумерация «Стр. X из Y» — своя).
С ключом --site PDF копируются на страницу /ochistka-dezinfektsiya-ventilyatsii/ (публикуются только PDF),
а превью первых страниц — в img/vnt-*.webp.
Оформление — как у образцов на сайте: шапка с логотипом, крупно телефон и сайт (tools/docs_brand/brand.py),
водяной знак «пестконтроль-центр.рф» на каждой странице, шрифт Arial. Бланки — без записей.
"""
import io
import os
import pathlib
import re
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[3]  # корень репозитория
BRAND_DIR = REPO / 'tools' / 'docs_brand'
sys.path.insert(0, str(BRAND_DIR))
import brand  # noqa: E402

OUT = pathlib.Path(next((a for a in sys.argv[1:] if not a.startswith('--')), 'out')).resolve()
FRESH = set()  # документы, у которых первая секция ещё не занята
OUT.mkdir(parents=True, exist_ok=True)

NB = '\u00a0'
FONT = 'Arial'
INK = RGBColor(0x18, 0x18, 0x1B)
DARK = RGBColor(0x09, 0x09, 0x0B)
INDIGO = RGBColor(0x4F, 0x46, 0xE5)
NAVY = RGBColor(0x1E, 0x1B, 0x4B)
GREY = RGBColor(0x52, 0x52, 0x5B)
LIGHT = RGBColor(0x71, 0x71, 0x7A)
VIOLET = RGBColor(0x61, 0x5F, 0xFF)
RED = RGBColor(0xB9, 0x1C, 0x1C)
GREEN = RGBColor(0x15, 0x80, 0x3D)
EXBLUE = RGBColor(0x2A, 0x3A, 0xB0)

PORTRAIT = dict(w=210, h=297, left=18, right=12, top=25, bottom=14)
LANDSCAPE = dict(w=297, h=210, left=15, right=12, top=24, bottom=12)
TW = {'p': PORTRAIT['w'] - PORTRAIT['left'] - PORTRAIT['right'], 'l': LANDSCAPE['w'] - LANDSCAPE['left'] - LANDSCAPE['right']}
TAGLINE = 'Очистка и дезинфекция вентиляции · пест-контроль для организаций'
EDITION = f'ред.{NB}11.2026'

CO = {
    'legal': 'ООО «Центр дезинфекционных услуг» (ПЕСТКОНТРОЛЬ Центр)',
    'inn': '7714462211', 'kpp': '771401001', 'ogrn': '1207700257775',
    'addr': '123007, г. Москва, 2-й Хорошёвский проезд, д. 7, к. 1, помещ. 1',
    'lic': 'Л064-00111-77/01942445',
    'lic_full': ('лицензия на деятельность по оказанию услуг по дезинфекции, дезинсекции и дератизации в целях обеспечения '
                 'санитарно-эпидемиологического благополучия населения № Л064-00111-77/01942445 от 03.03.2025'),
    'phone': '+7 (495) 104-35-70', 'mail': 'b2b@pestcontrol-center.ru', 'site': 'пестконтроль-центр.рф',
}
EXEC_LINE = f'{CO["legal"]}, ИНН {CO["inn"]}, {CO["addr"]}; {CO["lic_full"]}; {CO["phone"]}'
EXEC_SHORT = (f'{CO["legal"]}, ИНН {CO["inn"]}; лицензия на деятельность по оказанию услуг по дезинфекции, дезинсекции '
              f'и дератизации № {CO["lic"]} от 03.03.2025')

URL = {
    'ppr': 'http://pravo.gov.ru/proxy/ips/?docbody&nd=102861524',
    'sanpin': 'http://pravo.gov.ru/proxy/ips/?docbody=&nd=602107773&rdk=0',
    'mr': 'https://www.consultant.ru/document/cons_doc_LAW_541253/',
    'sp': 'http://publication.pravo.gov.ru/document/0001202606020088',
    'pp1128': 'https://mchs.gov.ru/dokumenty/617',
    'mchs': 'https://www.consultant.ru/document/cons_doc_LAW_344105/',
    'cgon': 'https://cgon.rospotrebnadzor.ru/biznesu/articles/ventilyatsiya-ochistka-i-dezinfektsiya/',
    'lic': 'https://fp.rospotrebnadzor.ru/licen/?oper=search&numb_history=&numb=&firmget_name=&ogrn_inn_nza=7714462211',
    'pprnew': 'https://ssk.cntd.ru/news/read/mcs-razrabotalo-proekt-novyx-pravil-protivopozarnogo-rezima/novosti-po-pojarnoy-bezopasnosti',
}

SHORT = ('в', 'и', 'к', 'с', 'у', 'о', 'а', 'на', 'по', 'до', 'от', 'за', 'не', 'из', 'без', 'для', 'при', 'или', 'со', 'во',
         'об', 'ее', 'её', 'их', 'то')


def typo(s):
    s = s.replace(' - ', ' — ')
    s = re.sub(r'(?<=[\dА-ЯЁA-Z])-(?=\d)', '\u2011', s)  # 3.3686-21, ВНТ-01, Л064-00111-77, 104-35-70
    s = re.sub(r'(№|пп\.|п\.|ст\.|ч\.|прил\.|разд\.|подп\.|г\.|д\.|к\.|стр\.|т\. е\.|т\. ч\.|т\. д\.) ', lambda m: m.group(1) + NB, s)
    s = re.sub(r'(СанПиН|СП|ГОСТ|МУК|МР|ПП РФ|ППР) (?=[\d№])', lambda m: m.group(1) + NB, s)
    s = s.replace('ПП РФ', 'ПП' + NB + 'РФ')
    s = re.sub(r'(\d) (°C|°|мм|м²|см²|м|кг|л|мин|ч|с|%|шт\.|раз|раза|года|год|лет|мес\.)(?=[\s,.;:)»/]|$)',
               lambda m: m.group(1) + NB + m.group(2), s)
    s = re.sub(r'(\d{4}) (г\.)', lambda m: m.group(1) + NB + m.group(2), s)
    for _ in range(2):
        s = re.sub(r'(^|[\s(«])(' + '|'.join(SHORT) + r') ', lambda m: m.group(1) + m.group(2) + NB, s, flags=re.I)
    s = re.sub(r' (—|–) ', NB + r'\1 ', s)
    return s


# ---------------------------------------------------------------- низкоуровневые помощники python-docx

def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear')
    sh.set(qn('w:color'), 'auto')
    sh.set(qn('w:fill'), hex_)
    tcPr.append(sh)


def borders(table, color='D4D4D8', sz='4', none=False):
    tblPr = table._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:val'), 'nil' if none else 'single')
        if not none:
            e.set(qn('w:sz'), sz)
            e.set(qn('w:space'), '0')
            e.set(qn('w:color'), color)
        b.append(e)
    tblPr.append(b)


def cell_border(cell, **sides):
    """cell_border(c, bottom=('single', 4, 'A1A1AA'), top=None …) — границы одной ячейки."""
    tcPr = cell._tc.get_or_add_tcPr()
    tb = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        v = sides.get(side, 'nil')
        e = OxmlElement(f'w:{side}')
        if v == 'nil' or v is None:
            e.set(qn('w:val'), 'nil')
        else:
            e.set(qn('w:val'), v[0])
            e.set(qn('w:sz'), str(v[1]))
            e.set(qn('w:space'), '0')
            e.set(qn('w:color'), v[2])
        tb.append(e)
    tcPr.append(tb)


def cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblPr = table._tbl.tblPr
    m = OxmlElement('w:tblCellMar')
    for side, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:w'), str(v))
        e.set(qn('w:type'), 'dxa')
        m.append(e)
    tblPr.append(m)


def fixed_layout(table, widths_mm):
    tblPr = table._tbl.tblPr
    lay = OxmlElement('w:tblLayout')
    lay.set(qn('w:type'), 'fixed')
    tblPr.append(lay)
    tw = OxmlElement('w:tblW')
    tw.set(qn('w:w'), str(int(sum(widths_mm) * 56.7)))
    tw.set(qn('w:type'), 'dxa')
    for old in tblPr.findall(qn('w:tblW')):
        tblPr.remove(old)
    tblPr.append(tw)
    table.autofit = False
    for row in table.rows:
        for i, w in enumerate(widths_mm):
            if i < len(row.cells):
                row.cells[i].width = Mm(w)
    grid = table._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths_mm[i] * 56.7)))


def header_row(row):
    trPr = row._tr.get_or_add_trPr()
    h = OxmlElement('w:tblHeader')
    h.set(qn('w:val'), 'true')
    trPr.append(h)


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement('w:cantSplit')
    e.set(qn('w:val'), 'true')
    trPr.append(e)


def row_height(row, mm, exact=False):
    trPr = row._tr.get_or_add_trPr()
    h = OxmlElement('w:trHeight')
    h.set(qn('w:val'), str(int(mm * 56.7)))
    h.set(qn('w:hRule'), 'exact' if exact else 'atLeast')
    trPr.append(h)


def runs(p, text, size=None, bold=False, color=None, italic=False, typo_=True):
    """Разметка: **жирный**, ⟦значение⟧ — жёлтая заливка (проверить или заменить)."""
    if typo_:
        text = typo(text)
    parts = re.split(r'(\*\*|⟦|⟧)', text)
    b, v = bold, False
    for part in parts:
        if part == '**':
            b = not b
            continue
        if part == '⟦':
            v = True
            continue
        if part == '⟧':
            v = False
            continue
        if not part:
            continue
        pieces = part.split('\u2011')
        r = p.add_run(pieces[0])
        for piece in pieces[1:]:
            r._r.append(OxmlElement('w:noBreakHyphen'))
            t = OxmlElement('w:t')
            t.text = piece
            t.set(qn('xml:space'), 'preserve')
            r._r.append(t)
        if b:
            r.bold = True
        if italic:
            r.italic = True
        if size:
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
        if v:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return p


def para(where, text='', size=9.5, bold=False, color=None, align=None, before=0, after=4, italic=False, line=1.12,
         keep=False):
    p = where.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if keep:
        pf.keep_with_next = True
    if align is not None:
        p.alignment = align
    if text:
        runs(p, text, size=size, bold=bold, color=color, italic=italic)
    return p


def cell_text(cell, text, size=8, bold=False, color=None, italic=False, align=None):
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(cell.paragraphs[0].runs):
        r._element.getparent().remove(r._element)
    first = True
    for ln in str(text).split('\n'):
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        pf = p.paragraph_format
        pf.space_after = Pt(1)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.05
        if align is not None:
            p.alignment = align
        if ln.startswith('• '):
            pf.left_indent = Mm(2.8)
            pf.first_line_indent = Mm(-2.8)
            ln = '•' + NB + ln[2:]
        if ln:
            runs(p, ln, size=size, bold=bold, color=color, italic=italic)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def bullet(where, text, size=9.5, after=2, indent=4.5):
    p = para(where, '', after=after)
    p.paragraph_format.left_indent = Mm(indent)
    p.paragraph_format.first_line_indent = Mm(-indent)
    p.paragraph_format.tab_stops.add_tab_stop(Mm(indent))
    r = p.add_run('•\t')
    r.font.size = Pt(size)
    r.font.color.rgb = INDIGO
    runs(p, text, size=size)
    return p


def numbered(where, n, text, size=9.5, after=3, indent=6):
    p = para(where, '', after=after)
    p.paragraph_format.left_indent = Mm(indent)
    p.paragraph_format.first_line_indent = Mm(-indent)
    p.paragraph_format.tab_stops.add_tab_stop(Mm(indent))
    r = p.add_run(f'{n}.\t')
    r.bold = True
    r.font.size = Pt(size)
    r.font.color.rgb = INDIGO
    runs(p, text, size=size)
    return p


def hyperlink(p, url, text, size=8):
    part = p.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), r_id)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '4F46E5')
    rPr.append(c)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(size * 2)))
    rPr.append(sz)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    h.append(r)
    p._p.append(h)


def field(p, code, size=7, color=LIGHT):
    def run(el=None, text=None):
        r = p.add_run(text) if text else p.add_run()
        r.font.size = Pt(size)
        r.font.color.rgb = color
        if el is not None:
            r._r.append(el)
        return r
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    run(f1)
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = f' {code} '
    run(it)
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'separate')
    run(f2)
    run(text='1')
    f3 = OxmlElement('w:fldChar')
    f3.set(qn('w:fldCharType'), 'end')
    run(f3)


def spacer(where, mm):
    p = where.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = Pt(mm * 2.835)
    r = p.add_run('')
    r.font.size = Pt(2)
    return p


def page_break(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_break(WD_BREAK.PAGE)


# ---------------------------------------------------------------- шапка и подложка

def render_png(html, name, tmp):
    src = tmp / f'{name}.html'
    src.write_text(html, encoding='utf-8')
    env = {**os.environ, 'NODE_PATH': os.environ.get('NODE_PATH', '/home/user/node_modules')}
    subprocess.run(['node', str(BRAND_DIR / 'render.mjs'), 'header', str(src), str(tmp / f'{name}.pdf'), str(tmp / f'{name}.png')],
                   check=True, capture_output=True, text=True, env=env)
    im = Image.open(tmp / f'{name}.png').convert('RGBA')
    flat = Image.new('RGB', im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    out = tmp / f'{name}-q.png'
    flat.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out, optimize=True)
    return out


class Brand:
    def __init__(self, tmp):
        self.img = {}
        for k in ('p', 'l'):
            self.img[('hd', k)] = render_png(brand.header_doc(TW[k], s=0.9, tagline=TAGLINE), f'hd-{k}', tmp)
            self.img[('rh', k)] = render_png(brand.runner_doc(TW[k], s=1.0), f'rh-{k}', tmp)
        self.shape = 0

    def wm(self):
        self.shape += 1
        return parse_xml(brand.docx_watermark_run(with_ns=True, shape_id=self.shape))


def setup_section(sec, br, orient, footer_left):
    g = PORTRAIT if orient == 'p' else LANDSCAPE
    sec.orientation = WD_ORIENT.PORTRAIT if orient == 'p' else WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Mm(g['w']), Mm(g['h'])
    sec.left_margin, sec.right_margin = Mm(g['left']), Mm(g['right'])
    sec.top_margin, sec.bottom_margin = Mm(g['top']), Mm(g['bottom'])
    sec.header_distance, sec.footer_distance = Mm(6), Mm(6)
    sec.different_first_page_header_footer = True
    tw = TW[orient]
    for hdr, kind in ((sec.first_page_header, 'hd'), (sec.header, 'rh')):
        hdr.is_linked_to_previous = False
        p = hdr.paragraphs[0]
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.add_run().add_picture(str(br.img[(kind, orient)]), width=Mm(tw))
        p._p.append(br.wm())
    for ftr in (sec.first_page_footer, sec.footer):
        ftr.is_linked_to_previous = False
        p = ftr.paragraphs[0]
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CLEAR)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.CLEAR)
        p.paragraph_format.tab_stops.add_tab_stop(Mm(tw), WD_TAB_ALIGNMENT.RIGHT)
        runs(p, footer_left + '\tСтр. ', size=7, color=LIGHT, typo_=False)
        field(p, 'PAGE')
        runs(p, ' из ', size=7, color=LIGHT, typo_=False)
        field(p, 'NUMPAGES')


def new_section(doc, br, orient, footer_left):
    if id(doc) in FRESH:
        FRESH.discard(id(doc))
        sec = doc.sections[0]
    else:
        sec = doc.add_section(WD_SECTION.NEW_PAGE)
    setup_section(sec, br, orient, footer_left)
    return sec


def styles(doc):
    st = doc.styles['Normal']
    st.font.name = FONT
    st.font.size = Pt(9.5)
    st.font.color.rgb = INK
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.line_spacing = 1.1
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), FONT)
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'ru-RU')
    rpr.append(lang)
    for name, size, color in (('Heading 1', 13, DARK), ('Heading 2', 10.5, NAVY)):
        hs = doc.styles[name]
        hs.font.name = FONT
        hs.font.size = Pt(size)
        hs.font.bold = True
        hs.font.color.rgb = color
        hs.paragraph_format.keep_with_next = True
        r = hs.element.get_or_add_rPr()
        f = r.find(qn('w:rFonts'))
        if f is None:
            f = OxmlElement('w:rFonts')
            r.append(f)
        for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
            f.set(qn(a), FONT)
        for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:cstheme', 'w:eastAsiaTheme'):
            if f.get(qn(a)) is not None:
                del f.attrib[qn(a)]


# ---------------------------------------------------------------- блоки документа

def h1(doc, text, before=10, after=5):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    runs(p, text, color=DARK)
    return p


def h2(doc, text, before=8, after=3):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    runs(p, text, color=NAVY)
    return p


def table(doc, head, rows, cols, tw, size=7.8, head_fill='EEF0FF', grp_fill='F4F4F5', first_bold=False, colnums=False):
    widths = [tw * c / sum(cols) for c in cols]
    tb = doc.add_table(rows=1, cols=len(cols))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb)
    cell_margins(tb)
    header_row(tb.rows[0])
    for i, h in enumerate(head):
        cell_text(tb.rows[0].cells[i], h, size=size - 0.3, bold=True, color=NAVY)
        shade(tb.rows[0].cells[i], head_fill)
    if colnums:
        row = tb.add_row()
        header_row(row)
        for i in range(len(cols)):
            cell_text(row.cells[i], str(i + 1), size=6.5, color=LIGHT, align=WD_ALIGN_PARAGRAPH.CENTER)
            shade(row.cells[i], 'FAFAFA')
    for r in rows:
        row = tb.add_row()
        no_split(row)
        if r and r[0] == 'grp':
            m = row.cells[0].merge(row.cells[-1])
            cell_text(m, r[1], size=size, bold=True, color=RGBColor(0x3F, 0x3F, 0x46))
            shade(m, grp_fill)
            continue
        for i, c in enumerate(r):
            cell_text(row.cells[i], c, size=size, bold=(first_bold and i == 0))
    fixed_layout(tb, widths)
    return tb


def kv(doc, rows, tw, label_w=52, size=8.5, min_h=6.6, fill_label=True):
    """Поля «название — значение»: значение пустое (строка для записи) или заполненное."""
    tb = doc.add_table(rows=0, cols=2)
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb, color='D4D4D8')
    cell_margins(tb, top=30, bottom=30)
    for item in rows:
        lab, val = item[0], item[1]
        row = tb.add_row()
        no_split(row)
        row_height(row, item[2] if len(item) > 2 else min_h)
        cell_text(row.cells[0], lab, size=size - 0.5, bold=True, color=GREY)
        if fill_label:
            shade(row.cells[0], 'FAFAFA')
        cell_text(row.cells[1], val, size=size)
        va = WD_CELL_VERTICAL_ALIGNMENT.TOP if len(item) > 2 else WD_CELL_VERTICAL_ALIGNMENT.CENTER
        row.cells[1].vertical_alignment = va
        row.cells[0].vertical_alignment = va
    fixed_layout(tb, [label_w, tw - label_w])
    return tb


def grid(doc, head, cols, tw, nrows, size=7.3, example=None, formula=None, colnums=True, h=8.5, numbered_rows=True):
    """Бланк-таблица: шапка, номера граф, при необходимости строка формул и пример, пустые строки."""
    widths = [tw * c / sum(cols) for c in cols]
    tb = doc.add_table(rows=1, cols=len(cols))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb, color='A1A1AA')
    cell_margins(tb, left=50, right=50, top=30, bottom=30)
    header_row(tb.rows[0])
    for i, t in enumerate(head):
        cell_text(tb.rows[0].cells[i], t, size=size - 0.3, bold=True, color=NAVY)
        shade(tb.rows[0].cells[i], 'EEF0FF')
    if colnums:
        row = tb.add_row()
        header_row(row)
        for i in range(len(cols)):
            cell_text(row.cells[i], str(i + 1), size=6.3, color=LIGHT, align=WD_ALIGN_PARAGRAPH.CENTER)
            shade(row.cells[i], 'FAFAFA')
    if formula:
        row = tb.add_row()
        for i, c in enumerate(formula):
            cell_text(row.cells[i], c, size=6.6, italic=True, color=GREY)
            shade(row.cells[i], 'FFFBEB')
    if example:
        row = tb.add_row()
        no_split(row)
        for i, c in enumerate(example):
            cell_text(row.cells[i], c, size=size - 0.4, italic=True, color=EXBLUE)
    for k in range(nrows):
        row = tb.add_row()
        no_split(row)
        row_height(row, h)
        if numbered_rows:
            cell_text(row.cells[0], str(k + 1 + (1 if example else 0)), size=7, color=LIGHT)
    fixed_layout(tb, widths)
    return tb


def note_box(doc, text, tw, fill='F5F3FF', color=NAVY, size=8.3, bar='615FFF'):
    tb = doc.add_table(rows=1, cols=1)
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb, none=True)
    cell_margins(tb, top=70, bottom=70, left=120, right=120)
    c = tb.rows[0].cells[0]
    lines = text if isinstance(text, list) else [text]
    cell_text(c, lines[0], size=size, color=color)
    for ln in lines[1:]:
        p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(2)
        if ln.startswith('• '):
            p.paragraph_format.left_indent = Mm(3)
            p.paragraph_format.first_line_indent = Mm(-3)
            ln = '•' + NB + ln[2:]
        runs(p, ln, size=size, color=color)
    shade(c, fill)
    cell_border(c, left=('single', 18, bar))
    fixed_layout(tb, [tw])
    return tb


def form_head(doc, code, title, basis, status, tw):
    """Код формы и статус справа, крупное название, основание мелко."""
    tb = doc.add_table(rows=1, cols=2)
    borders(tb, none=True)
    cell_margins(tb, top=0, bottom=0, left=0, right=0)
    a, b = tb.rows[0].cells
    cell_text(a, f'Форма {code} · {EDITION}', size=7.5, bold=True, color=INDIGO)
    cell_text(b, status, size=7.5, bold=True, color=GREEN if status.startswith('Обязател') else GREY,
              align=WD_ALIGN_PARAGRAPH.RIGHT)
    fixed_layout(tb, [tw * 0.45, tw * 0.55])
    para(doc, title, size=13.5, bold=True, color=DARK, before=4, after=2, line=1.05, keep=True)
    if basis:
        para(doc, basis, size=8, color=GREY, after=6, keep=True)


def act_no(doc, tw, label='Акт', city='г. ____________'):
    tb = doc.add_table(rows=1, cols=2)
    borders(tb, none=True)
    cell_margins(tb, top=0, bottom=0, left=0, right=0)
    a, b = tb.rows[0].cells
    cell_text(a, f'{label} № ________', size=9.5, bold=True)
    cell_text(b, f'{city}   «____» ______________ 20____ г.', size=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT)
    fixed_layout(tb, [tw * 0.4, tw * 0.6])
    spacer(doc, 2)


def lines_block(doc, label, n, tw, size=8.5):
    para(doc, label, size=size, bold=True, color=GREY, before=4, after=1, keep=True)
    tb = doc.add_table(rows=n, cols=1)
    borders(tb, none=True)
    cell_margins(tb, top=0, bottom=0, left=0, right=0)
    for row in tb.rows:
        row_height(row, 7)
        no_split(row)
        cell_border(row.cells[0], bottom=('single', 4, 'A1A1AA'))
    fixed_layout(tb, [tw])
    return tb


def checks(doc, items, tw, cols=1, size=8.5):
    rows = (len(items) + cols - 1) // cols
    tb = doc.add_table(rows=rows, cols=cols)
    borders(tb, none=True)
    cell_margins(tb, top=10, bottom=10, left=0, right=60)
    for i, it in enumerate(items):
        r, c = i % rows, i // rows
        cell_text(tb.rows[r].cells[c], '□ ' + it, size=size)
    fixed_layout(tb, [tw / cols] * cols)
    return tb


def signs(doc, tw, left=('Исполнитель', 'ООО «Центр дезинфекционных услуг»'), right=('Заказчик', '______________________'),
          extra=None, mp=True, parties=None):
    """Подписи сторон: две колонки (по умолчанию) или три (parties). «М. П.» — у каждой стороны при mp=True;
    в трёхколоночном варианте — отдельной строкой у сторон из mp_roles."""
    spacer(doc, 3)
    parties = parties or [left, right]
    n = len(parties)
    tb = doc.add_table(rows=1, cols=n)
    borders(tb, none=True)
    cell_margins(tb, top=0, bottom=0, left=0, right=200 if n == 2 else 110)
    for cell, party in zip(tb.rows[0].cells, parties):
        role, org = party[0], party[1]
        stamp = party[2] if len(party) > 2 else mp
        if n == 2:
            cell_text(cell, f'**{role}:** {org}', size=8.8, color=DARK)
        else:  # три колонки: роль и организация — двумя строками у всех, чтобы строки подписей шли вровень
            cell_text(cell, f'**{role}:**', size=8.2, color=DARK)
            p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            runs(p, org, size=8.2, color=DARK)
        if n == 2:
            lines = ['Должность, ФИО ________________________________',
                     'Подпись ______________   Дата ______________' + ('   М. П.' if stamp else '')]
        else:
            lines = ['Должность, ФИО ___________________', 'Подпись ___________   Дата __________']
            if stamp:
                lines.append('М. П.')
        for ln in lines:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(7)
            p.paragraph_format.space_after = Pt(0)
            runs(p, ln, size=8.5 if n == 2 else 8)
    fixed_layout(tb, [tw / n] * n)
    for row in tb.rows:
        no_split(row)
        for c in row.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True
    if extra:
        para(doc, extra, size=7.2, color=LIGHT, before=5)


# ---------------------------------------------------------------- часть 1: перечень, данные, вопросы

def part_overview(doc, br):
    tw = TW['p']
    para(doc, f'ПЕРЕЧЕНЬ ДОКУМЕНТОВ И ОБРАЗЦЫ ФОРМ · РЕД.{NB}11.2026', size=8, bold=True, color=INDIGO, after=3)
    para(doc, 'Документы при очистке и дезинфекции систем вентиляции и кондиционирования воздуха', size=18, bold=True,
         color=DARK, after=4, line=1.0)
    para(doc, 'Что обязательно по действующим нормам, что рекомендовано, какие данные нужны для актов и журналов и что '
              'остаётся на объекте. Образцы 9 форм (ВНТ-01 — ВНТ-09) — в этом файле, каждая с новой страницы.',
         size=10, color=INK, after=8)
    note_box(doc, [
        '**Коротко**',
        '• **Обязательны по нормам:** акт очистки вентиляционных камер, циклонов, фильтров и воздуховодов от горючих отходов '
        'и отложений не реже 1 раза в год (п. 43 ППР); проверка огнезадерживающих устройств с записью в журнал эксплуатации '
        'систем противопожарной защиты (п. 42 ППР); профилактическая дезинфекция централизованных систем вентиляции '
        'и кондиционирования не реже 1 раза в год и исследование систем кондиционирования и увлажнения на легионеллы '
        'не реже 2 раз в год (п. 132 СанПиН 3.3686-21) — подтверждаем актом дезинфекции и протоколом лаборатории.',
        '• **Рекомендованы МР 3.5.0396-25:** журнал учёта работ на объекте (прил. 3), журнал расчёта потребности '
        'в дезсредствах (прил. 2), обследование перед работами (прил. 1), оповещение и таблички на выключателях (пп. 3.14–3.15).',
        '• **Как мы оформляем:** очистку и дезинфекцию — двумя отдельными актами (ВНТ-02 и ВНТ-03); смывы отбирает '
        'специалист аккредитованной лаборатории (ВНТ-05); огнезадерживающие клапаны проверяем вместе с ответственным '
        'заказчика (ВНТ-04), техническое обслуживание и ремонт выполняет организация с лицензией МЧС России. '
        'Акты подписывают стороны, исполнитель заверяет их печатью.',
    ], tw)

    h1(doc, '1. Перечень документов', before=12)
    head = ['Код', 'Документ', 'Статус', 'Основание', 'Кто оформляет и подписывает', 'Где остаётся']
    O, R = '**Обязателен**', 'Рекомендован'
    rows = [
        ['ВНТ-01', 'Акт обследования систем перед работами (осмотр, видеоинспекция, объём работ)', R,
         'МР 3.5.0396-25, прил. 1: подготовительный этап — обследование визуально и видеоинспекцией',
         'Наш специалист; подпись представителя заказчика', 'У нас (основа сметы), копия заказчику'],
        ['ВНТ-02', 'Акт очистки вентиляционных камер, циклонов, фильтров и воздуховодов от горючих отходов и отложений '
                   '+ приложение: фото до и после', O,
         'п. 43 ППР: не реже 1 раза в год, «с составлением соответствующего акта»; п. 124 ППР — вытяжные устройства '
         'и трубопроводы в производственных и складских помещениях: А и Б — раз в квартал, В1–В4 — раз в полугодие',
         'Мастер бригады и ответственный заказчика за эксплуатацию вентиляции', '2 экз.: заказчику (папка пожарной '
                                                                                  'безопасности) и нам'],
        ['ВНТ-03', 'Акт профилактической дезинфекции систем вентиляции и кондиционирования', O + ' (форма свободная)',
         'п. 132 СанПиН 3.3686-21: дезинфекция централизованных систем не реже 1 раза в год; МР 3.5.0396-25 '
         'пп. 3.12–3.15, 5.4 (средство с СГР, отключение, таблички, присутствие представителя)',
         'Наш специалист-дезинфектор и представитель заказчика', '2 экз.: заказчику и нам'],
        ['ВНТ-04', 'Акт проверки огнезадерживающих устройств (клапанов, заслонок, шиберов) с готовым текстом записи '
                   'в журнал эксплуатации СПЗ', '**Обязательны** проверка и запись в журнал',
         'п. 42 ППР — проверка по документации изготовителя с записью в журнал; п. 17(1) — форму журнала определяет '
         'руководитель; ТО и ремонт — лицензия МЧС (п. 54 ППР, ПП РФ № 1128)',
         'Наш специалист и ответственный заказчика за пожарную безопасность; запись в журнал вносит заказчик',
         'Оригинал заказчику, копия нам'],
        ['ВНТ-05', 'Акт отбора проб (смывов) + протокол аккредитованной лаборатории',
         '**Протокол обязателен**; акт отбора рекомендован',
         'п. 132 СанПиН 3.3686-21: легионеллы не реже 2 раз в год; МР 3.5.0396-25 пп. 2.6, 4.1–4.3; '
         'МУК 4.2.2217-07', 'Пробы отбирает специалист аккредитованной лаборатории, протокол выдаёт лаборатория; '
                            'подписи нашего специалиста и представителя заказчика',
         'Акт и протокол — заказчику; копии акта — лаборатории и нам'],
        ['ВНТ-06', 'Журнал учёта работ по проведению очистки и дезинфекции систем вентиляции и кондиционирования '
                   'воздуха на объекте', R + ' (форма МР)',
         'МР 3.5.0396-25 п. 4.2, прил. 3 — результаты контроля вносятся в журнал',
         'Ведёт заказчик; запись после каждой работы — наш специалист, подпись руководителя объекта',
         'Постоянно на объекте: вкладыш в папке заказчика'],
        ['ВНТ-07', 'Журнал расчёта потребности в дезинфицирующих средствах (на год)', R,
         'МР 3.5.0396-25 п. 3.13, прил. 2 — расчёт ведёт специалист организации, которая проводит работы',
         'Наш специалист', 'У нас; выписка заказчику по запросу'],
        ['ВНТ-08', 'Приказ о порядке и сроках очистки и дезинфекции, ответственных и графике работ (шаблон для заказчика)',
         O + ' для заказчика',
         'п. 43 ППР — порядок и сроки определяет руководитель; МР 3.5.0396-25 п. 2.7 — ответственный приказом, '
         'п. 2.8 — графики работ', 'Руководитель заказчика', 'У заказчика'],
        ['ВНТ-09', 'Оповещение о работах и табличка «Не включать» на выключатели', R,
         'МР 3.5.0396-25 п. 3.14 — оповещение о сроках и мерах предосторожности; п. 3.15 — предупреждающие надписи',
         'Наш специалист вместе с администрацией объекта', 'Табличка — на время работ; оповещение — у заказчика'],
        ['—', 'Договор, акт выполненных работ или УПД', O, 'ГК РФ; 402-ФЗ (первичные документы)', 'Бухгалтерия сторон',
         'У обеих сторон'],
        ['—', 'Копии: лицензия на ДДД, СГР или декларация и инструкция дезсредства, удостоверения специалистов',
         'Предъявляются проверяющим',
         'ПП РФ от 20.03.2024 № 337 (лицензирование ДДД); МР 3.5.0396-25 пп. 3.3, 3.12; 412-ФЗ', 'Мы',
         'В папке у заказчика'],
    ]
    table(doc, head, rows, [14, 36, 23, 43, 34, 30], tw, size=7.4, first_bold=True)
    para(doc, 'ППР — Правила противопожарного режима в РФ (ПП РФ от 16.09.2020 № 1479); СПЗ — системы противопожарной защиты; '
              'ДДД — дезинфекция, дезинсекция, дератизация; СГР — свидетельство о государственной регистрации.',
         size=7.3, color=LIGHT, before=3, after=2)

    h1(doc, '2. Что остаётся на объекте и что у нас', before=12)
    tb = table(doc, ['Папка заказчика — для МЧС и Роспотребнадзора', 'Остаётся у нас'], [[
        '• Акт очистки ВНТ-02 с фото до и после (оригинал)\n'
        '• Акт дезинфекции ВНТ-03 (оригинал)\n'
        '• Акт проверки клапанов ВНТ-04 — и сделанная по нему запись в журнале эксплуатации СПЗ\n'
        '• Протокол лаборатории на легионеллы и акт отбора проб ВНТ-05\n'
        '• Журнал ВНТ-06 — вкладыш в папке, новая запись после каждой работы\n'
        '• Приказ и график ВНТ-08 (если заказчик утвердил по нашему шаблону)\n'
        '• Договор, акт выполненных работ (УПД)\n'
        '• Копии: лицензия на ДДД, СГР или декларация и инструкция средства, удостоверения специалистов',
        '• Акт обследования ВНТ-01 и смета\n'
        '• Вторые экземпляры актов ВНТ-02 — ВНТ-04\n'
        '• Журнал расчёта дезсредств ВНТ-07\n'
        '• Исходные фото и видео до и после, схема мест съёмки\n'
        '• Копии акта отбора проб ВНТ-05 и протокола лаборатории\n'
        '• Копии записей в журналах заказчика (фото страницы)',
    ]], [1, 1], tw, size=8)

    h1(doc, '3. Какие данные нужны для актов и журналов', before=12)
    rows = [
        ['grp', 'До выезда — от заказчика'],
        ['Реквизиты и объект', 'Полное наименование, ИНН, адрес объекта, количество строений, основной вид деятельности '
                               '(графы журнала по прил. 3 МР)'],
        ['Категории помещений', 'Категории по взрывопожарной и пожарной опасности (А, Б, В1–В4, Г, Д) — от них зависят '
                                'периодичность по п. 124 ППР и взрывопожаробезопасный способ очистки (п. 43 ППР)'],
        ['Системы', 'Перечень систем с обозначениями из проекта или паспорта (П1, В1, ПВ1…), обслуживаемые помещения, '
                    'схемы; есть ли централизованные системы кондиционирования и увлажнения; число местных '
                    'кондиционеров и сплит-систем'],
        ['Огнезадерживающие устройства', 'Перечень и места установки (проект или исполнительная документация), тип '
                                         'и привод, паспорт или руководство изготовителя, подключение к пожарной '
                                         'сигнализации, кто обслуживает СПЗ'],
        ['Ответственные', 'ФИО и должность ответственного за эксплуатацию вентиляции (приказ № и дата) и ответственного '
                          'за пожарную безопасность; кто будет присутствовать при работах (п. 5.4 МР)'],
        ['Условия работ', 'Окна отключения систем, доступ (высота, подвесные потолки, лючки), укрытие оборудования, '
                          'пропуска'],
        ['grp', 'На объекте — измеряем и фиксируем'],
        ['Объём работ', 'Сечения и длины воздуховодов → площадь внутренней поверхности, м² (прямоугольный: 2 × (a + b) × L, '
                        'круглый: 3,14 × d × L), и длина, п. м — для сметы; число решёток, диффузоров, зонтов, фильтров, '
                        'теплообменников'],
        ['Состояние', 'Вид отложений (пыль, жир, волокна, строительный мусор, влага, плесень), степень загрязнения до '
                      'и после, повреждения; номера фото и видео, места съёмки'],
        ['Результаты', 'Объём удалённых отложений, кг; места и время отбора смывов; результат проверки каждого клапана'],
        ['grp', 'С нашей стороны'],
        ['Исполнитель', 'Реквизиты, лицензия на ДДД № Л064-00111-77/01942445 от 03.03.2025 (в реестре Роспотребнадзора — '
                        'действует); ФИО и удостоверения специалистов (п. 3.3 МР)'],
        ['Дезсредство', 'Наименование, номер СГР или декларации, концентрация рабочего раствора, норма расхода л/м², '
                        'количество, способ обработки, экспозиция — по инструкции к средству (п. 3.12 МР)'],
        ['Лаборатория', 'Аккредитованная испытательная лаборатория; пробы отбирает её специалист. В акты и журнал вносим '
                        'номер и дату протокола и показатели (Legionella pneumophila по МУК 4.2.2217-07)'],
    ]
    table(doc, ['Данные', 'Что именно и зачем'], rows, [40, 140], tw, size=7.8, first_bold=True)

    h1(doc, '4. Нормы, на которые опираются формы', before=12)
    refs = [
        ('Правила противопожарного режима в РФ (ПП РФ от 16.09.2020 № 1479): пп. 17(1), 42, 43, 54, 124', 'ppr'),
        ('СанПиН 3.3686-21 «Санитарно-эпидемиологические требования по профилактике инфекционных болезней»: п. 132', 'sanpin'),
        ('МР 3.5.0396-25 «Методические рекомендации по организации и контролю проведения очистки и дезинфекции систем '
         'вентиляции и кондиционирования воздуха» (утв. 27.10.2025)', 'mr'),
        ('СП 2.1.4284-26 (с 01.09.2026): п. 8 — обследование технического состояния вентиляции; п. 24 — требования '
         'для медицинских организаций', 'sp'),
        ('ПП РФ от 28.07.2020 № 1128 — лицензирование монтажа, ТО и ремонта средств обеспечения пожарной безопасности', 'pp1128'),
        ('Письмо МЧС России от 20.09.2016 № 19-16-1468 — проверки работоспособности и лицензия', 'mchs'),
        ('ЦГОН Роспотребнадзора: «Вентиляция. Очистка и дезинфекция»', 'cgon'),
        ('Реестр лицензий Роспотребнадзора: ООО «Центр дезинфекционных услуг»', 'lic'),
    ]
    for text, key in refs:
        p = para(doc, '', after=2)
        p.paragraph_format.left_indent = Mm(4.5)
        p.paragraph_format.first_line_indent = Mm(-4.5)
        p.paragraph_format.tab_stops.add_tab_stop(Mm(4.5))
        r = p.add_run('•\t')
        r.font.color.rgb = INDIGO
        r.font.size = Pt(8.5)
        runs(p, text + ' — ', size=8.5)
        hyperlink(p, URL[key], URL[key].replace('https://', '').replace('http://', ''), size=7.5)
    p = para(doc, '', before=4, after=2)
    runs(p, 'ППР 2020 года действуют до 31.12.2026; МЧС подготовило проект новых правил. Когда их утвердят, номера '
            'пунктов в формах сверим и обновим — ', size=8, color=GREY)
    hyperlink(p, URL['pprnew'], 'новость о проекте', size=8)
    runs(p, '.', size=8, color=GREY)

    h1(doc, '5. Как оформляем документы', before=12)
    for t in (
        'Формы заполняет наш специалист на объекте в день работ; объём — в м² внутренней поверхности и в п. м.',
        'Акты подписывают исполнитель и представитель заказчика, исполнитель заверяет их печатью; экземпляры '
        'заказчика — в папку документов к проверкам.',
        'Журнал ВНТ-06 ведётся вкладышами в папке заказчика: листы нумеруются по порядку, запись — после каждой работы.',
        'Запись о проверке огнезадерживающих устройств в журнал эксплуатации систем противопожарной защиты вносит '
        'ответственный заказчика по акту ВНТ-04 — готовый текст записи есть в форме.',
        'Смывы на легионеллы отбирает и исследует аккредитованная лаборатория; протокол хранится вместе с актами.',
    ):
        bullet(doc, t, size=9)


# ---------------------------------------------------------------- формы

MORE = 'Если систем больше — продолжить на обороте или в приложении к акту.'


def f01(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-01 · Акт обследования систем вентиляции · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-01', 'Акт обследования систем вентиляции и кондиционирования воздуха перед очисткой и дезинфекцией',
              'Подготовительный этап по прил. 1 к МР 3.5.0396-25: осмотр и видеоинспекция, выбор способа очистки '
              'и метода дезинфекции, объём работ.', 'Рекомендован', tw)
    act_no(doc, tw)
    kv(doc, [
        ('Заказчик, объект, адрес', ''), ('Основной вид деятельности', ''),
        ('Представитель заказчика', 'ФИО, должность:'),
        ('Исполнитель', EXEC_SHORT + '; специалист (ФИО):'),
        ('Метод обследования', '□ визуальный осмотр   □ видеоинспекция (участков ___, файлы № ________)   □ фото'),
    ], tw, label_w=44)
    h2(doc, 'Обследованные системы')
    grid(doc, ['№', 'Система (обозначение), тип¹', 'Помещения, категория²', 'Воздуховоды: сечение; длина, п. м; площадь, м²',
               'Доступ: лючки, высота, потолки', 'Загрязнение: вид, степень³', 'Рекомендация'],
         [6, 26, 30, 30, 26, 30, 32], tw, 5, h=9.5)
    para(doc, '¹ П — приточная, В — вытяжная, ПВ — приточно-вытяжная, МО — местный отсос, К — кухонная вытяжка, '
              'КВ — кондиционирование.  ² Категория по взрывопожарной и пожарной опасности (А, Б, В1–В4, Г, Д), если '
              'установлена.  ³ Пыль, жир, волокна, мусор, влага, плесень; нет / слабое / среднее / сильное.  ' + MORE,
         size=6.7, color=LIGHT, before=2, after=3)
    h2(doc, 'Объём работ по результатам обследования', before=5)
    checks(doc, [
        'Очистка (п. 43 ППР): систем ___, ___ м², ___ п. м',
        'Профилактическая дезинфекция: систем ___, ___ м², ___ п. м',
        'Смывы на легионеллы: □ до  □ после, проб ___',
        'Проверка огнезадерживающих устройств: ___ шт.',
        'Инспекционные люки (по согласованию): ___ шт.',
        'Демонтаж решёток и диффузоров: ___ шт.',
        'Замена фильтров: ___ шт.',
        'Взрывопожаробезопасный способ (А, Б, В1–В4)',
    ], tw, cols=2, size=8)
    lines_block(doc, 'Условия работ (окно отключения систем, доступ, укрытие оборудования)', 1, tw)
    lines_block(doc, 'Замечания (повреждения, нет доступа, неисправности — в объём работ не входят)', 2, tw)
    signs(doc, tw, extra='Акт — основание для сметы и плана работ; оригинал у исполнителя, копия заказчику.')


def f02(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-02 · Акт очистки от горючих отходов и отложений · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-02', 'Акт очистки вентиляционных камер, циклонов, фильтров и воздуховодов от горючих отходов и отложений',
              'По п. 43 Правил противопожарного режима в РФ (ПП РФ от 16.09.2020 № 1479): очистка не реже 1 раза в год '
              'в порядке и сроки, установленные руководителем организации, с составлением акта.',
              'Обязателен · п. 43 ППР', tw)
    act_no(doc, tw)
    kv(doc, [
        ('Заказчик, ИНН', ''), ('Объект, адрес', ''),
        ('Исполнитель', EXEC_SHORT),
        ('Основание', 'Договор № ______ от __________; приказ заказчика о порядке и сроках очистки № ______ от __________'),
        ('Сроки работ', 'с ___ ч ___ мин «___» ________ 20___ г. по ___ ч ___ мин «___» ________ 20___ г.'),
        ('Присутствовал', 'Ответственный за эксплуатацию вентиляции (ФИО, должность):'),
    ], tw, label_w=36)
    h2(doc, 'Очищенные системы и элементы')
    grid(doc, ['№', 'Система (обозначение), помещения', 'Катего\u00adрия¹', 'Очищенные элементы²', 'Объём: м² / п. м',
               'Вид отложений', 'Способ очистки³', 'Результат⁴'],
         [6, 34, 13, 34, 17, 22, 26, 22], tw, 5, h=9.5)
    para(doc, '¹ А, Б, В1–В4, Г, Д.  ² ВК — венткамера, Ц — циклон, Ф — фильтр, ВД — воздуховод, ВН — вентилятор, '
              'Р — решётки и диффузоры, З — зонт, ЖФ — жироулавливающий фильтр.  ³ М — механический сухой (щётки, ерши), '
              'П — промышленный пылесос или ПФУ, Р — ручной; во взрывопожароопасных и пожароопасных помещениях — '
              'взрывопожаробезопасным способом (п. 43 ППР).  ⁴ «Видимых горючих отложений нет» или замечание.  ' + MORE,
         size=6.7, color=LIGHT, before=2, after=3)
    kv(doc, [
        ('Удалено отложений', '______ кг (______ мешков); отходы □ вывезены исполнителем  □ переданы заказчику'),
        ('Фото и видео', 'До и после — файлы № ______________; переданы заказчику ______________; схема — приложение 1'),
        ('Замечания', 'Повреждения, нет люков, неисправности (в рамках работ не устранялись):', 15),
    ], tw, label_w=36)
    spacer(doc, 2)
    note_box(doc, [
        '**Заключение.** Системы, указанные в таблице, очищены от горючих отходов и отложений. Следующая очистка — '
        'не позднее «___» ____________ 20___ г. (не реже 1 раза в год — п. 43 ППР; вытяжные устройства, аппараты '
        'и трубопроводы в производственных и складских помещениях: А и Б — раз в квартал, В1–В4 — раз в полугодие, '
        'прочие — раз в год — п. 124 ППР).',
        'Результат принят заказчиком: □ без замечаний   □ с замечаниями: ______________________________',
    ], tw, fill='F0FDF4', color=RGBColor(0x14, 0x53, 0x2D), bar='16A34A', size=8)
    signs(doc, tw, extra='2 экземпляра: заказчику (хранить с документацией по пожарной безопасности) и исполнителю. '
                         'Запись о работе — в журнал ВНТ-06.')
    # приложение — фото
    page_break(doc)
    para(doc, 'Приложение 1 к акту № ________ от «___» __________ 20___ г.', size=8, bold=True, color=INDIGO, after=2)
    para(doc, 'Фотофиксация до и после очистки и схема мест съёмки', size=12, bold=True, color=DARK, after=6)
    tb = doc.add_table(rows=6, cols=2)
    borders(tb, color='D4D4D8')
    cell_margins(tb, top=40, bottom=40)
    for r in range(6):
        row = tb.rows[r]
        no_split(row)
        if r % 2 == 0:
            row_height(row, 58, exact=True)
            for c, lab in zip(row.cells, ('ДО', 'ПОСЛЕ')):
                cell_text(c, lab + ' — место для фото', size=7.5, color=LIGHT)
                shade(c, 'FAFAFA')
        else:
            row_height(row, 8)
            for c in row.cells:
                cell_text(c, 'Система ______  участок ____________  файл № ________', size=7.5, color=GREY)
    fixed_layout(tb, [tw / 2, tw / 2])
    lines_block(doc, 'Схема мест съёмки (номера точек на схеме = номера файлов) или ссылка на видео', 3, tw)


def f03(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-03 · Акт дезинфекции систем вентиляции и кондиционирования · ПЕСТКОНТРОЛЬ Центр · '
                + CO['site'])
    form_head(doc, 'ВНТ-03', 'Акт профилактической дезинфекции систем вентиляции и кондиционирования воздуха',
              'Подтверждает выполнение п. 132 СанПиН 3.3686-21 (профилактическая дезинфекция централизованных систем — '
              'не реже 1 раза в год); порядок работ — МР 3.5.0396-25, пп. 3.12–3.15, 5.4.',
              'Обязателен · п. 132 СанПиН 3.3686-21', tw)
    act_no(doc, tw)
    kv(doc, [
        ('Заказчик, ИНН', ''), ('Объект, адрес; вид деятельности', ''),
        ('Исполнитель', EXEC_SHORT + '; специалист (ФИО, № удостоверения о подготовке — п. 3.3 МР):'),
        ('Вид дезинфекции', '□ профилактическая плановая   □ профилактическая внеплановая (причина: ________________)'),
        ('Очистка перед дезинфекцией', 'Акт ВНТ-02 № ______ от __________;  дата и время работ: «___» ________ 20___ г., '
                                       'с ___ ч ___ мин до ___ ч ___ мин'),
    ], tw, label_w=40)
    spacer(doc, 2)
    checks(doc, [
        'Работники оповещены о сроках и мерах (п. 3.14 МР)',
        'Системы выключены, таблички «Не включать» (п. 3.15)',
        'Решётки, диффузоры и сетки сняты (п. 3.15)',
        'Присутствовал представитель заказчика (п. 5.4)',
    ], tw, cols=2, size=8)
    h2(doc, 'Обработанные системы и элементы', before=5)
    grid(doc, ['№', 'Система (обозначение)', 'Обработанные элементы¹', 'Объём: м² / п. м', 'Способ²', 'Время обработки',
               'Примечание'], [6, 30, 50, 20, 22, 22, 30], tw, 5, h=8.5)
    para(doc, '¹ Воздуховоды, решётки и диффузоры, фильтры, теплообменники, дренажные поддоны и трубопроводы, увлажнители, '
              'корпус и секции кондиционера, вентилятор, шумоглушители.  ² О — орошение, А — аэрозоль, П — протирание.  '
              + MORE, size=6.7, color=LIGHT, before=2, after=3)
    tb = doc.add_table(rows=4, cols=4)
    borders(tb, color='D4D4D8')
    cell_margins(tb, top=30, bottom=30)
    cells = [('Дезсредство', ''), ('СГР / декларация №', ''), ('Концентрация, %', ''), ('Норма расхода, л/м²', ''),
             ('Израсходовано раствора, л', ''), ('Израсходовано препарата', ''), ('Экспозиция, мин', ''),
             ('Расчёт потребности', 'ВНТ-07, строка № ___')]
    for i, (lab, val) in enumerate(cells):
        row = tb.rows[i // 2]
        row_height(row, 6.6)
        no_split(row)
        c1, c2 = row.cells[(i % 2) * 2], row.cells[(i % 2) * 2 + 1]
        cell_text(c1, lab, size=8, bold=True, color=GREY)
        shade(c1, 'FAFAFA')
        cell_text(c2, val, size=8)
    fixed_layout(tb, [38, 52, 38, 52])
    spacer(doc, 2)
    kv(doc, [
        ('Включение систем', 'После экспозиции и полной просушки: «___» ________ в ___ ч ___ мин; включил ответственный '
                             'за эксплуатацию ______________________ (п. 3.15 МР)'),
        ('Контроль эффективности', 'Визуально загрязнений и зон увлажнения: □ нет  □ есть: ________________\n'
                                   'Смывы на легионеллы: □ отобраны — акт ВНТ-05 № ______  □ не требуются (нет систем '
                                   'с увлажнением, сплит-системы). Результат — по протоколу, запись в ВНТ-06 (п. 4.2 МР)'),
    ], tw, label_w=40)
    signs(doc, tw, extra='2 экземпляра: заказчику и исполнителю. Неудовлетворительный результат — повторная обработка '
                         'и контроль (п. 4.3 МР).')


def f04(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-04 · Акт проверки огнезадерживающих устройств · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-04', 'Акт проверки огнезадерживающих устройств (клапанов, заслонок, шиберов) в воздуховодах',
              'Проверка по технической документации изготовителя с записью в журнал эксплуатации систем противопожарной '
              'защиты — п. 42 ППР. Техническое обслуживание и ремонт в объём проверки не входят: их выполняет организация '
              'с лицензией МЧС России по отдельной заявке (п. 54 ППР, ПП РФ от 28.07.2020 № 1128).',
              'Обязательны проверка и запись · п. 42 ППР', tw)
    act_no(doc, tw)
    kv(doc, [
        ('Заказчик, объект, адрес', ''),
        ('Исполнитель', EXEC_SHORT),
        ('Присутствовал', 'Ответственный заказчика за пожарную безопасность (ФИО, должность):'),
        ('Документация изготовителя', 'Паспорт или руководство по эксплуатации, тип клапанов: ____________________'),
        ('Объём проверки', '□ внешний осмотр  □ закрытие от привода или кнопки  □ сигнал положения на приёмно-контрольный '
                           'прибор  □ возврат в рабочее положение'),
    ], tw, label_w=40)
    h2(doc, 'Результаты проверки')
    grid(doc, ['№', 'Обозначение клапана, место установки (система, помещение, преграда)', 'Тип, привод, огнестойкость (EI)',
               'Внешний осмотр¹', 'Закрытие, время, с', 'Сигнал на прибор', 'Возврат', 'Итог²'],
         [6, 46, 30, 20, 17, 17, 16, 18], tw, 6, h=8.5)
    para(doc, '¹ Целостность корпуса и заслонки, крепление, доступ для обслуживания, отсутствие отложений.  '
              '² И — исправен, Н — неисправен (описание — в замечаниях).  ' + MORE, size=6.7, color=LIGHT, before=2, after=3)
    kv(doc, [
        ('Отключение вентиляции по сигналу АПС', '□ проверено совместно с организацией, обслуживающей СПЗ: ______________\n'
                                                 '□ не проверялось'),
        ('Итого', 'проверено ___ шт., исправны ___ шт., неисправны ___ шт. (№ __________)'),
        ('Замечания', 'Неисправности (ремонт и ТО — по отдельной заявке, организация с лицензией МЧС России):', 14),
    ], tw, label_w=40)
    spacer(doc, 2)
    note_box(doc, [
        '**Текст для записи в журнал эксплуатации систем противопожарной защиты** (форму журнала определяет руководитель — '
        'п. 17(1) ППР):',
        '«___» ________ 20___ г. проведена проверка огнезадерживающих устройств в воздуховодах систем __________ '
        '(___ шт.) по технической документации изготовителя (п. 42 ППР). Исправны ___ шт., неисправны ___ шт. '
        '(№ ________). Основание — акт № ______ от ________, исполнитель ООО «Центр дезинфекционных услуг». '
        'Ответственный ________________ (подпись).',
    ], tw, size=8)
    signs(doc, tw, extra='Оригинал заказчику (вместе с журналом эксплуатации СПЗ), копия исполнителю.')


def f05(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-05 · Акт отбора проб (смывов) · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-05', 'Акт отбора проб (смывов) с поверхностей систем вентиляции и кондиционирования воздуха',
              'Легионеллы — не реже 2 раз в год для систем кондиционирования и увлажнения (п. 132 СанПиН 3.3686-21); '
              'оценка эффективности — пп. 4.1–4.3 МР 3.5.0396-25; метод — МУК 4.2.2217-07. Пробы отбирает специалист '
              'аккредитованной испытательной лаборатории, исследования — в этой лаборатории (п. 2.6 МР).',
              'Рекомендован · протокол обязателен', tw)
    act_no(doc, tw)
    kv(doc, [
        ('Заказчик, объект, адрес', ''),
        ('Цель', '□ плановый контроль на легионеллы   □ эффективность дезинфекции (акт ВНТ-03 № ____)\n'
                 '□ повторный контроль после повторной обработки (п. 4.3 МР)'),
        ('Этап', '□ до дезинфекции   □ после дезинфекции'),
        ('Лаборатория', 'Аккредитованная испытательная лаборатория: ________________________; заявка № ______'),
        ('Пробы отобрал', 'Специалист лаборатории (ФИО, должность):'),
        ('Исполнитель работ', 'ООО «Центр дезинфекционных услуг», специалист (ФИО):'),
        ('Присутствовал', 'Представитель заказчика (ФИО, должность):'),
    ], tw, label_w=40)
    h2(doc, 'Отобранные пробы')
    grid(doc, ['№', 'Шифр пробы', 'Система, элемент, точное место отбора¹', 'Площадь смыва, см²', 'Время отбора',
               'Показатель²', 'Примечание'], [6, 18, 60, 18, 16, 30, 32], tw, 7, h=8)
    para(doc, '¹ Поддон и дренаж, увлажнитель, теплообменник, решётка или диффузор, сетка, внутренняя поверхность '
              'воздуховода.  ² Legionella pneumophila; другие показатели — по заявке.', size=6.7, color=LIGHT, before=2,
         after=3)
    kv(doc, [
        ('Доставка в лабораторию', 'Специалистом лаборатории: «___» ________ в ___ ч ___ мин; условия: ______________'),
        ('Результат', 'Протокол № ______ от __________ → запись в журнале ВНТ-06 № ______'),
    ], tw, label_w=40)
    spacer(doc, 2)
    note_box(doc, 'Критерий эффективности — отсутствие легионелл в смывах (подп. 2 п. 3215 СанПиН 3.3686-21; п. 4.1 '
                  'МР 3.5.0396-25). При положительном результате — повторная очистка и дезинфекция и повторный контроль '
                  '(п. 4.3 МР).', tw, fill='FFF7ED', color=RGBColor(0x7C, 0x2D, 0x12), bar='EA580C', size=8)
    signs(doc, tw, parties=[('Пробы отобрал', 'специалист лаборатории', False),
                            ('Исполнитель', 'ООО «Центр дезинфекционных услуг»', True),
                            ('Заказчик', '____________________', True)],
          extra='Экземпляры: заказчику (вместе с протоколом), лаборатории и исполнителю. Если лаборатория оформляет отбор '
                'своим актом, его копия хранится вместе с протоколом.')


def f06(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-06 · Журнал учёта работ по очистке и дезинфекции · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-06', 'Журнал учёта работ по проведению очистки и дезинфекции систем вентиляции и кондиционирования '
                             'воздуха на объекте',
              'По рекомендуемому образцу прил. 3 к МР 3.5.0396-25; графы результатов контроля добавлены по п. 4.2 МР. '
              'Ведётся вкладышами в папке документов заказчика и хранится на объекте.', 'Рекомендован · форма МР', tw)
    para(doc, 'Начат «____» ______________ 20___ г.          Окончен «____» ______________ 20___ г.', size=9.5,
         before=2, after=8)
    kv(doc, [
        ('Наименование юридического лица или ИП', ''), ('Адрес объекта', ''), ('Количество строений', ''),
        ('Основной вид деятельности', ''), ('Тип вентиляционной системы', ''),
        ('Наличие и виды систем кондиционирования воздуха', ''),
        ('Ответственный за техническое обслуживание', 'ФИО, должность, приказ № ______ от ____________:'),
    ], tw, label_w=62, min_h=8.5)
    tb = doc.add_table(rows=1, cols=2)
    borders(tb, none=True)
    cell_margins(tb, top=60, bottom=0, left=0, right=0)
    cell_text(tb.rows[0].cells[0], 'М. П.', size=8.5, color=GREY)
    cell_text(tb.rows[0].cells[1], 'Руководитель объекта  ______________________  ______________\n'
                                   '                                          ФИО                              подпись',
              size=8.5)
    fixed_layout(tb, [30, tw - 30])
    h2(doc, 'Сведения об организации, осуществляющей очистку и дезинфекцию систем вентиляции и кондиционирования', before=12)
    kv(doc, [
        ('Наименование', CO['legal']),
        ('Адрес', CO['addr']),
        ('Лицензия', 'На осуществление деятельности по оказанию услуг по дезинфекции, дезинсекции и дератизации в целях '
                     'обеспечения санитарно-эпидемиологического благополучия населения № Л064-00111-77/01942445 '
                     'от 03.03.2025; действует бессрочно'),
        ('Телефон, сайт', f'{CO["phone"]} · {CO["site"]} · {CO["mail"]}'),
    ], tw, label_w=40)
    para(doc, 'Журнал ведётся вкладышами в папке документов заказчика; листы нумеруются по порядку. Лист № 1.',
         size=8.5, color=GREY, before=10)
    # записи — альбомный лист
    new_section(doc, br, 'l', 'Форма ВНТ-06 · Журнал учёта работ по очистке и дезинфекции · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    tl = TW['l']
    tb = doc.add_table(rows=1, cols=2)
    borders(tb, none=True)
    cell_margins(tb, top=0, bottom=0, left=0, right=0)
    cell_text(tb.rows[0].cells[0], 'Учёт проведённых работ', size=12, bold=True, color=DARK)
    cell_text(tb.rows[0].cells[1], 'Лист № ______', size=9, color=GREY, align=WD_ALIGN_PARAGRAPH.RIGHT)
    fixed_layout(tb, [tl * 0.7, tl * 0.3])
    spacer(doc, 1.5)
    grid(doc, ['№', 'Дата', 'Вид работ, № акта', 'Системы: обозначения; обработано, шт.', 'Объём: м² / п. м',
               'Системы конд., шт. / местные конд., шт.', 'Дезсредство: наименование, концентрация, количество',
               'Способ обработки', 'Визуальная оценка', 'Лаб. контроль: протокол №, дата, результат', 'Повторная обработка',
               'Исполнитель: ФИО, подпись', 'Руководитель объекта: ФИО, подпись'],
         [6, 15, 21, 23, 17, 17, 29, 16, 20, 26, 16, 22, 22], tl, 10, h=11.5)
    para(doc, 'Вид работ: очистка, дезинфекция, отбор проб, повторная обработка. Объём — площадь внутренней поверхности, м², '
              'и длина воздуховодов, п. м.', size=7, color=LIGHT, before=3)


def f07(doc, br):
    tl = TW['l']
    new_section(doc, br, 'l', 'Форма ВНТ-07 · Журнал расчёта потребности в дезинфицирующих средствах · ПЕСТКОНТРОЛЬ Центр · '
                + CO['site'])
    form_head(doc, 'ВНТ-07', 'Журнал для расчёта потребности в дезинфицирующих средствах при дезинфекции систем вентиляции '
                             'и кондиционирования способом орошения на год',
              'По рекомендуемой форме прил. 2 к МР 3.5.0396-25; расчёт ведёт специалист организации, которая проводит '
              'работы (п. 3.13 МР). Норма расхода и концентрация — по инструкции к средству.', 'Рекомендован · форма МР', tl)
    para(doc, f'Организация: {CO["legal"]}      Год: 20____      Ответственный специалист: ______________________',
         size=8.5, after=5)
    grid(doc, ['№', 'Адрес объекта', 'Наименование объекта обеззара\u00adживания*', 'Число объектов обеззара\u00adживания',
               'Поверхность одного объекта, м²', 'Общая площадь обработки, м²', 'Расход рабочего раствора, л на 1 м²',
               'Концентра\u00adция рабочего раствора, %', 'Количество исходного препарата в 1 л рабочего раствора',
               'Количество рабочего раствора на 1 обработку, л', 'Количество препарата в общем объёме раствора',
               'Число обработок в год', 'Количество исходного препарата в год'],
         [6, 27, 30, 18, 17, 17, 17, 19, 22, 20, 21, 15, 21], tl, 10, h=9,
         formula=['', '', '', '', '', 'гр. 4 × гр. 5', 'по инструкции', 'по инструкции', 'по инструкции', 'гр. 6 × гр. 7',
                  'гр. 10 × гр. 9', 'по графику', 'гр. 11 × гр. 12'])
    para(doc, 'Примечание: * — система вентиляции и (или) система кондиционирования воздуха. Строка под номерами граф — '
              'порядок расчёта по прил. 2 МР 3.5.0396-25.', size=7, color=LIGHT, before=3)


def f08(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-08 · Приказ о порядке и сроках очистки и дезинфекции (шаблон) · ПЕСТКОНТРОЛЬ Центр · '
                + CO['site'])
    form_head(doc, 'ВНТ-08', 'Приказ о порядке и сроках очистки и дезинфекции систем вентиляции и кондиционирования воздуха',
              'Шаблон для заказчика: п. 43 ППР (порядок и сроки определяет руководитель), п. 42 ППР, п. 132 СанПиН 3.3686-21, '
              'МР 3.5.0396-25 пп. 2.7–2.8, 3.14–3.15, 4.2. Оформляется на бланке организации-заказчика.',
              'Обязанность заказчика · шаблон', tw)
    para(doc, '____________________________________________________________', size=10, align=WD_ALIGN_PARAGRAPH.CENTER,
         after=0)
    para(doc, '(полное наименование организации)', size=7.5, color=LIGHT, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
    para(doc, 'ПРИКАЗ', size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    act_no(doc, tw, label='')
    para(doc, '**О порядке и сроках очистки и дезинфекции систем вентиляции и кондиционирования воздуха**', size=10, after=6)
    para(doc, 'В целях выполнения пп. 42, 43 Правил противопожарного режима в Российской Федерации (утв. постановлением '
              'Правительства РФ от 16.09.2020 № 1479), п. 132 СанПиН 3.3686-21 и с учётом МР 3.5.0396-25 ПРИКАЗЫВАЮ:',
         size=9.5, after=4, line=1.15)
    items = [
        'Назначить ответственным за эксплуатацию систем вентиляции и кондиционирования воздуха '
        '______________________________ (должность, ФИО) (п. 2.7 МР 3.5.0396-25).',
        'Утвердить график работ по очистке и дезинфекции систем вентиляции и кондиционирования воздуха и проверке '
        'огнезадерживающих устройств (приложение 1). Очистку вентиляционных камер, циклонов, фильтров и воздуховодов '
        'от горючих отходов и отложений проводить не реже 1 раза в год (п. 43 ППР), вытяжных устройств, аппаратов '
        'и трубопроводов в производственных и складских помещениях — в сроки п. 124 ППР; очистку вентиляционных систем '
        'взрывопожароопасных и пожароопасных помещений — взрывопожаробезопасными способами.',
        'По результатам очистки составлять акт (п. 43 ППР); результаты проверки огнезадерживающих устройств вносить '
        'в журнал эксплуатации систем противопожарной защиты (п. 42 ППР); сведения о работах и результатах контроля — '
        'в журнал учёта работ по очистке и дезинфекции систем вентиляции и кондиционирования (п. 4.2 МР 3.5.0396-25).',
        'Перед работами оповещать работников о сроках и мерах предосторожности; на время работ отключать системы '
        'и размещать у выключателей предупреждающие таблички; включать системы после работ и полной просушки — только '
        'ответственному за эксплуатацию (пп. 3.14, 3.15 МР).',
        'Для систем кондиционирования и увлажнения воздуха организовать исследование на легионеллы в аккредитованной '
        'лаборатории не реже 2 раз в год (п. 132 СанПиН 3.3686-21).',
        'Акты, протоколы и журналы хранить в ______________________ (место хранения); ответственный за хранение — '
        '______________________.',
        'Контроль исполнения приказа оставляю за собой.',
    ]
    for i, t in enumerate(items, 1):
        numbered(doc, i, t, size=9.3, after=3)
    para(doc, 'Руководитель   ______________________   ______________________ (ФИО)', size=9.5, before=10, after=8)
    para(doc, 'С приказом ознакомлены:   ______________________   ______________________   «____» __________ 20___ г.',
         size=8.5, color=GREY, after=4)
    page_break(doc)
    para(doc, 'Приложение 1 к приказу № ________ от «____» __________ 20___ г.', size=8, bold=True, color=INDIGO, after=2)
    para(doc, 'График работ по очистке и дезинфекции систем вентиляции и кондиционирования воздуха', size=12, bold=True,
         color=DARK, after=6)
    head = ['Системы и оборудование', 'Вид работ', 'Периодичность', 'Основание', 'Срок (месяц)', 'Исполнитель']
    rows = [
        ['Все системы вентиляции: вентиляционные камеры, циклоны, фильтры, воздуховоды', 'Очистка от горючих отходов '
         'и отложений, акт', 'Не реже 1 раза в год', 'п. 43 ППР', '', ''],
        ['Вытяжные устройства (шкафы, окрасочные и сушильные камеры и др.), аппараты и трубопроводы в производственных '
         'и складских помещениях', 'Очистка от пожароопасных отложений', 'А, Б — раз в квартал; В1–В4 — раз в полугодие; '
                                                                         'прочие — раз в год', 'п. 124 ППР', '', ''],
        ['Централизованные системы вентиляции и кондиционирования (медицина, образование, гостиницы, офисы '
         'и производство, торговля, транспорт)', 'Профилактическая дезинфекция, акт', 'Не реже 1 раза в год '
                                                                                     '(или чаще по документации '
                                                                                     'производителя)',
         'п. 132 СанПиН 3.3686-21; п. 2.4 МР', '', ''],
        ['Системы кондиционирования и увлажнения воздуха (кроме небольших установок без увлажнения и сплит-систем)',
         'Смывы на легионеллы, протокол', 'Не реже 2 раз в год', 'п. 132 СанПиН 3.3686-21', '', ''],
        ['Огнезадерживающие устройства в воздуховодах, блокировка с пожарной сигнализацией', 'Проверка, запись в журнал СПЗ',
         'По документации изготовителя', 'п. 42 ППР', '', ''],
        ['grp', '**Только для медицинских организаций**'],
        ['Системы механической приточно-вытяжной вентиляции и кондиционирования', 'Проверка эффективности, очистка '
         'и дезинфекция', '1 раз в год', 'подп. 2 п. 24 СП 2.1.4284-26', '', ''],
        ['Сплит-системы (теплообменник и съёмные фильтры)', 'Очистка и дезинфекция', 'Не реже 1 раза в 3 месяца',
         'подп. 22 п. 24 СП 2.1.4284-26', '', ''],
    ]
    table(doc, head, rows, [44, 28, 30, 30, 18, 30], tw, size=7.6)
    para(doc, 'Сроки и исполнителей заполняет заказчик. Строки, которые к объекту не относятся, вычёркиваются.', size=7.3,
         color=LIGHT, before=3)


def f09(doc, br):
    tw = TW['p']
    new_section(doc, br, 'p', 'Форма ВНТ-09 · Оповещение и табличка · ПЕСТКОНТРОЛЬ Центр · ' + CO['site'])
    form_head(doc, 'ВНТ-09', 'Оповещение о проведении работ и табличка «Не включать»',
              'Оповещение работников о сроках и мерах предосторожности — п. 3.14 МР 3.5.0396-25; предупреждающая надпись '
              'в местах выключателей на время работ — п. 3.15 МР.', 'Рекомендован', tw)
    para(doc, 'ОПОВЕЩЕНИЕ', size=12, bold=True, color=DARK, after=3)
    para(doc, '«____» ______________ 20___ г. с ____ ч ____ мин до ____ ч ____ мин в помещениях '
              '______________________________________ проводятся очистка и дезинфекция систем вентиляции и кондиционирования '
              'воздуха. На это время системы ______________ будут отключены.', size=9.5, after=4, line=1.25)
    para(doc, 'Меры предосторожности:', size=9.5, bold=True, after=2)
    for t in ('не находиться в обрабатываемых помещениях во время работ и ______ мин после их окончания;',
              'не включать вентиляцию и кондиционеры самостоятельно — их включит ответственный за эксплуатацию;',
              'убрать из зоны работ продукты, посуду, документы и личные вещи или накрыть их;',
              'при попадании средства на кожу или в глаза — промыть водой и сообщить ответственному.'):
        bullet(doc, t, size=9.2)
    para(doc, 'Дезинфицирующее средство: ______________________________ (по инструкции к средству).', size=9, before=4,
         after=2, line=1.25)
    para(doc, 'Ответственный: ______________________________, тел. ____________________', size=9, after=10, line=1.25)
    # табличка
    tb = doc.add_table(rows=1, cols=1)
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb, color='B91C1C', sz='24')
    cell_margins(tb, top=200, bottom=200, left=200, right=200)
    c = tb.rows[0].cells[0]
    cell_text(c, 'ВНИМАНИЕ', size=26, bold=True, color=RED, align=WD_ALIGN_PARAGRAPH.CENTER)
    for t, sz, b, col in (('Проводится очистка и дезинфекция вентиляции', 15, True, DARK), ('НЕ ВКЛЮЧАТЬ', 38, True, RED),
                          ('Система ____________   с ____ ч «____» ________ до ____ ч «____» ________', 11, False, DARK),
                          ('Включает только ответственный: ______________________  тел. ______________', 11, False, DARK)):
        p = c.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        runs(p, t, size=sz, bold=b, color=col)
    fixed_layout(tb, [tw])
    para(doc, 'Табличку распечатать по числу выключателей и щитов управления; снять после включения систем.', size=7.5,
         color=LIGHT, before=4)


ORDER = {
    'tblPr': ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize', 'tblW', 'jc',
              'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption',
              'tblDescription', 'tblPrChange'],
    'tcPr': ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap', 'tcMar', 'textDirection',
             'tcFitText', 'vAlign', 'hideMark', 'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'],
}


def finish(doc):
    """Порядок дочерних элементов tblPr и tcPr — по схеме OOXML; между соседними таблицами — пустой абзац
    (иначе Word и LibreOffice склеивают их в одну таблицу)."""
    W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    for name, order in ORDER.items():
        for el in doc.element.body.iter(W + name):
            kids = list(el)
            kids.sort(key=lambda k: order.index(k.tag[len(W):]) if k.tag[len(W):] in order else len(order))
            for k in kids:
                el.remove(k)
            for k in kids:
                el.append(k)
    body = doc.element.body
    for tbl in list(body.iter(W + 'tbl')):
        nxt = tbl.getnext()
        if nxt is not None and nxt.tag == W + 'tbl':
            p = OxmlElement('w:p')
            pPr = OxmlElement('w:pPr')
            sp = OxmlElement('w:spacing')
            sp.set(qn('w:before'), '0')
            sp.set(qn('w:after'), '0')
            sp.set(qn('w:line'), '120')
            sp.set(qn('w:lineRule'), 'exact')
            pPr.append(sp)
            p.append(pPr)
            tbl.addnext(p)


FORMS = [
    ('ВНТ-01', 'vnt-01-akt-obsledovaniya-ventilyatsii', f01,
     'Акт обследования систем вентиляции и кондиционирования воздуха перед очисткой и дезинфекцией'),
    ('ВНТ-02', 'vnt-02-akt-ochistki-ventilyatsii', f02,
     'Акт очистки вентиляционных камер, циклонов, фильтров и воздуховодов от горючих отходов и отложений'),
    ('ВНТ-03', 'vnt-03-akt-dezinfektsii-ventilyatsii', f03,
     'Акт профилактической дезинфекции систем вентиляции и кондиционирования воздуха'),
    ('ВНТ-04', 'vnt-04-akt-proverki-ognezaderzhivayushchikh-klapanov', f04,
     'Акт проверки огнезадерживающих устройств (клапанов, заслонок, шиберов) в воздуховодах'),
    ('ВНТ-05', 'vnt-05-akt-otbora-smyvov-ventilyatsii', f05,
     'Акт отбора проб (смывов) с поверхностей систем вентиляции и кондиционирования воздуха'),
    ('ВНТ-06', 'vnt-06-zhurnal-ochistki-i-dezinfektsii-ventilyatsii', f06,
     'Журнал учёта работ по проведению очистки и дезинфекции систем вентиляции и кондиционирования воздуха на объекте'),
    ('ВНТ-07', 'vnt-07-zhurnal-rascheta-dezsredstv', f07,
     'Журнал для расчёта потребности в дезинфицирующих средствах при дезинфекции систем вентиляции и кондиционирования'),
    ('ВНТ-08', 'vnt-08-prikaz-ob-ochistke-i-dezinfektsii-ventilyatsii', f08,
     'Приказ о порядке и сроках очистки и дезинфекции систем вентиляции и кондиционирования воздуха (шаблон) и график работ'),
    ('ВНТ-09', 'vnt-09-opoveshchenie-i-tablichka-ne-vklyuchat', f09,
     'Оповещение о проведении работ и табличка «Не включать»'),
]
SET_SLUG = 'dokumenty-ochistka-dezinfektsiya-ventilyatsii'
SET_TITLE = 'Документы при очистке и дезинфекции систем вентиляции и кондиционирования воздуха — перечень и образцы форм'
PAGE_DIR = 'ochistka-dezinfektsiya-ventilyatsii'


def props(doc, title, subject):
    cp = doc.core_properties
    cp.author = 'ПЕСТКОНТРОЛЬ Центр'
    cp.last_modified_by = 'ПЕСТКОНТРОЛЬ Центр'
    cp.title = title
    cp.subject = subject
    cp.keywords = 'очистка вентиляции, дезинфекция вентиляции, акт, журнал, МР 3.5.0396-25, ППР, СанПиН 3.3686-21'
    cp.comments = f'ПЕСТКОНТРОЛЬ Центр · {CO["site"]} · {CO["phone"]}'
    cp.language = 'ru-RU'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        br = Brand(tmp)
        # комплект: перечень + все формы
        doc = Document()
        styles(doc)
        setup_section(doc.sections[0], br, 'p', 'Документы по вентиляции · перечень и образцы форм · ПЕСТКОНТРОЛЬ Центр · '
                      + CO['site'])
        part_overview(doc, br)
        for _, _, f, _ in FORMS:
            f(doc, br)
        props(doc, SET_TITLE, 'Перечень документов и формы ВНТ-01 — ВНТ-09')
        finish(doc)
        files.append(OUT / f'{SET_SLUG}.docx')
        doc.save(files[-1])
        # каждая форма — отдельным файлом
        for code, slug, f, title in FORMS:
            doc = Document()
            styles(doc)
            FRESH.add(id(doc))
            f(doc, br)
            props(doc, f'{title} — форма {code}', f'Форма {code} · {EDITION.replace(NB, " ")} · бланк')
            finish(doc)
            files.append(OUT / f'{slug}.docx')
            doc.save(files[-1])
    for f in files:
        print('docx', f.name, f.stat().st_size)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(OUT)] + [str(f) for f in files],
                   check=True, capture_output=True, timeout=900)
    return [f.with_suffix('.pdf') for f in files]


def pdf_pages(pdf):
    out = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r'^Pages:\s+(\d+)', out, re.M).group(1))


def preview(pdf, page, widths, stem):
    """Превью страницы PDF в img/: webp нужной ширины (рендер в 4 раза крупнее и уменьшение — чётче мелкий текст)."""
    img_dir = REPO / 'img'
    with tempfile.TemporaryDirectory() as t:
        base = pathlib.Path(t) / 'p'
        subprocess.run(['pdftoppm', '-r', '200', '-f', str(page), '-l', str(page), '-png', '-singlefile', str(pdf), str(base)],
                       check=True)
        im = Image.open(str(base) + '.png').convert('RGB')
    if im.width > im.height:  # альбомный лист — для превью берём левую часть в пропорции A4 (шапка и начало таблицы)
        im = im.crop((0, 0, round(im.height * 210 / 297), im.height))
    made = []
    for w in widths:
        h = round(im.height * w / im.width)
        dst = img_dir / f'{stem}-{w}.webp'
        im.resize((w, h), Image.LANCZOS).save(dst, 'WEBP', quality=82, method=6)
        made.append((dst.name, w, h, dst.stat().st_size))
    return made


def publish(pdfs):
    """PDF — на страницу вентиляции, превью первых страниц — в img/."""
    page = REPO / PAGE_DIR
    for pdf in pdfs:
        dst = page / pdf.name
        dst.write_bytes(pdf.read_bytes())
        print('pdf', dst.relative_to(REPO), dst.stat().st_size, 'байт,', pdf_pages(dst), 'стр.')
    by = {p.stem: p for p in pdfs}
    for code, slug, _, _ in FORMS:
        n = code[-2:]
        for name, w, h, size in preview(by[slug], 1, (120, 240), f'vnt-{n}-p1'):
            print('img', name, f'{w}x{h}', size)
    for name, w, h, size in preview(by[SET_SLUG], 1, (360, 720), 'vnt-komplekt-p1'):
        print('img', name, f'{w}x{h}', size)
    for name, w, h, size in preview(by['vnt-02-akt-ochistki-ventilyatsii'], 1, (360, 720), 'vnt-02-p1'):
        print('img', name, f'{w}x{h}', size)


if __name__ == '__main__':
    pdfs = build()
    for p in pdfs:
        print('pdf', p.name, p.stat().st_size, 'байт,', pdf_pages(p), 'стр.')
    if '--site' in sys.argv:
        publish(pdfs)
