# -*- coding: utf-8 -*-
"""DOCX-шаблон программы производственного контроля (тот же текст, что в PDF).

Значения для замены выделены жёлтым. Рисунки (план-схема, блок-схема) — PNG из render_pdf.mjs --figs.
"""
import pathlib
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Mm, Pt, RGBColor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402
from render_html import typo  # noqa: E402

FONT = 'Arial'
INK = RGBColor(0x18, 0x18, 0x1B)
DARK = RGBColor(0x09, 0x09, 0x0B)
INDIGO = RGBColor(0x4F, 0x46, 0xE5)
NAVY = RGBColor(0x1E, 0x1B, 0x4B)
GREY = RGBColor(0x52, 0x52, 0x5B)
LIGHT = RGBColor(0x71, 0x71, 0x7A)
RED = RGBColor(0xB9, 0x1C, 0x1C)
EXBLUE = RGBColor(0x2A, 0x3A, 0xB0)
TEXT_W = 178  # мм


def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
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


def cell_margins(table, top=45, bottom=45, left=85, right=85):
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
    table.autofit = False
    for row in table.rows:
        for i, w in enumerate(widths_mm):
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


def row_height(row, mm):
    trPr = row._tr.get_or_add_trPr()
    h = OxmlElement('w:trHeight')
    h.set(qn('w:val'), str(int(mm * 56.7)))
    h.set(qn('w:hRule'), 'atLeast')
    trPr.append(h)


def keep_next(p):
    p.paragraph_format.keep_with_next = True


def runs(p, text, size=None, bold=False, color=None, italic=False, typo_=True):
    """Разметка: **жирный**, ⟦значение⟧ → жёлтая заливка."""
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
        r = p.add_run(part)
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


def para(doc_or_cell, text='', size=9.5, bold=False, color=None, align=None, before=0, after=4, italic=False, line=1.15):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if align:
        p.alignment = align
    if text:
        runs(p, text, size=size, bold=bold, color=color, italic=italic)
    return p


def cell_text(cell, text, size=8, bold=False, color=None, italic=False):
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(cell.paragraphs[0].runs):
        r._element.getparent().remove(r._element)
    first = True
    for ln in text.split('\n'):
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        pf = p.paragraph_format
        pf.space_after = Pt(1)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.05
        if ln.startswith('• '):
            pf.left_indent = Mm(3)
            pf.first_line_indent = Mm(-3)
            ln = '•\u00a0' + ln[2:]
        runs(p, ln, size=size, bold=bold, color=color, italic=italic)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def table(doc, t):
    cols = t['cols']
    widths = [TEXT_W * c / sum(cols) for c in cols]
    size = 7.5 if t.get('small') else 8
    tb = doc.add_table(rows=1, cols=len(cols))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tb)
    cell_margins(tb)
    hr = tb.rows[0]
    header_row(hr)
    for i, h in enumerate(t['head']):
        cell_text(hr.cells[i], h, size=size, bold=True, color=NAVY)
        shade(hr.cells[i], 'EEF0FF')
    last = ''
    for r in t['rows']:
        row = tb.add_row()
        no_split(row)
        if r[0] == 'grp':
            m = row.cells[0].merge(row.cells[-1])
            cell_text(m, r[1], size=size, bold=True, color=RGBColor(0x3F, 0x3F, 0x46))
            shade(m, 'F4F4F5')
            continue
        for i, c in enumerate(r):
            if i == 0 and c == '':
                cell_text(row.cells[0], last, size=size - 1, color=RGBColor(0xA1, 0xA1, 0xAA))
                continue
            if i == 0:
                last = c
            cell_text(row.cells[i], c, size=size, bold=(t.get('kv') and i == 0))
            if t.get('kv') and i == 0:
                shade(row.cells[i], 'FAFAFA')
    fixed_layout(tb, widths)
    para(doc, '', after=2)
    return tb


def h1(doc, num, title, sp=''):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f'{num}. ')
    r.font.color.rgb = INDIGO
    runs(p, title, color=DARK)
    if sp:
        q = para(doc, sp, size=7.5, bold=True, color=INDIGO, after=4)
        keep_next(q)
    return p


def h2(doc, num, title):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(f'{num}. ')
    r.font.color.rgb = INDIGO
    runs(p, title, color=NAVY)
    return p


def bullet(doc, text):
    p = para(doc, '', after=2)
    p.paragraph_format.left_indent = Mm(5)
    p.paragraph_format.first_line_indent = Mm(-4)
    runs(p, '•\t' + text, size=9.5)
    p.paragraph_format.tab_stops.add_tab_stop(Mm(5))
    return p


def ccp(doc, items):
    fields = [('hazard', 'Опасный фактор'), ('limit', 'Критический предел'), ('monitor', 'Мониторинг: как, когда, кто'),
              ('action', 'Корректирующие действия'), ('records', 'Записи и верификация')]
    for c in items:
        tb = doc.add_table(rows=1, cols=2)
        borders(tb, color='D4D4D8')
        cell_margins(tb)
        hc = tb.rows[0].cells[0].merge(tb.rows[0].cells[1])
        for extra in hc.paragraphs[1:]:
            extra._element.getparent().remove(extra._element)
        p = hc.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(f'{c["id"]}  ')
        r.bold = True
        r.font.color.rgb = RED
        r.font.size = Pt(9)
        runs(p, c['stage'], size=9, bold=True, color=DARK)
        runs(p, '   · ' + c['kind'].lower(), size=7.5, color=RED)
        shade(hc, 'FEF2F2')
        no_split(tb.rows[0])
        for k, lab in fields:
            row = tb.add_row()
            no_split(row)
            cell_text(row.cells[0], lab, size=8, bold=True, color=GREY)
            shade(row.cells[0], 'FAFAFA')
            cell_text(row.cells[1], c[k], size=8)
        fixed_layout(tb, [42, TEXT_W - 42])
        for row in tb.rows[:-1]:
            for cl in row.cells:
                for pp in cl.paragraphs:
                    pp.paragraph_format.keep_with_next = True
        para(doc, '', after=3)


def pest(doc, items):
    p = para(doc, 'РАЗДЕЛ ЗАПОЛНЯЕТ ИСПОЛНИТЕЛЬ ДДД · пример для хлебопекарного производства', size=7.5, bold=True, color=INDIGO, after=3)
    keep_next(p)
    for n, t in items:
        p = para(doc, '', after=3)
        p.paragraph_format.left_indent = Mm(14)
        p.paragraph_format.first_line_indent = Mm(-14)
        p.paragraph_format.tab_stops.add_tab_stop(Mm(14))
        r = p.add_run(n + '\t')
        r.bold = True
        r.font.color.rgb = INDIGO
        runs(p, t, size=9.5)


def signs2(doc, items):
    tb = doc.add_table(rows=0, cols=4)
    borders(tb, none=True)
    for role, pos, name in items:
        row = tb.add_row()
        cell_text(row.cells[0], role, size=9, bold=True)
        cell_text(row.cells[1], pos, size=9, color=GREY)
        cell_text(row.cells[2], '____________ /' + name + '/', size=9)
        cell_text(row.cells[3], '«___» __________ 2026 г.', size=9, color=GREY)
        row_height(row, 10)
        no_split(row)
        for c in row.cells:
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.BOTTOM
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True
    fixed_layout(tb, [34, 58, 48, 38])


def form(doc, f):
    p = para(doc, f['title'], size=11, bold=True, color=DARK, after=3)
    keep_next(p)
    if f.get('meta'):
        para(doc, f['meta'], size=8.5, color=GREY, after=4)
    cols = f['cols']
    widths = [TEXT_W * c / sum(cols) for c in cols]
    tb = doc.add_table(rows=1, cols=len(cols))
    borders(tb, color='A1A1AA')
    cell_margins(tb)
    header_row(tb.rows[0])
    for i, h in enumerate(f['head']):
        cell_text(tb.rows[0].cells[i], h, size=7.5, bold=True, color=NAVY)
        shade(tb.rows[0].cells[i], 'EEF0FF')
    if f.get('example'):
        row = tb.add_row()
        for i, c in enumerate(f['example']):
            cell_text(row.cells[i], c, size=7.5, italic=True, color=EXBLUE)
    for k in range(min(f['rows'], 22 if f.get('numbered') else 16)):
        row = tb.add_row()
        row_height(row, 8.2)
        if f.get('numbered'):
            cell_text(row.cells[0], str(k + 1), size=8)
    fixed_layout(tb, widths)
    if f.get('example'):
        para(doc, 'Первая строка — пример заполнения.', size=7.5, color=LIGHT, before=3)


def hyperlink(p, url, text):
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
    sz.set(qn('w:val'), '15')
    rPr.append(sz)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    h.append(r)
    p._p.append(h)


def field(p, code, size=7):
    r = p.add_run()
    r.font.size = Pt(size)
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    r._r.append(f1)
    r2 = p.add_run()
    r2.font.size = Pt(size)
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = f' {code} '
    r2._r.append(it)
    r3 = p.add_run()
    r3.font.size = Pt(size)
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'separate')
    r3._r.append(f2)
    r4 = p.add_run('1')
    r4.font.size = Pt(size)
    r5 = p.add_run()
    f3 = OxmlElement('w:fldChar')
    f3.set(qn('w:fldCharType'), 'end')
    r5._r.append(f3)


def cal(doc, rows):
    months = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    widths = [72] + [6.5] * 12 + [TEXT_W - 72 - 78]
    tb = doc.add_table(rows=1, cols=14)
    borders(tb)
    cell_margins(tb, left=50, right=50)
    header_row(tb.rows[0])
    for i, h in enumerate(['Мероприятие'] + months + ['Ответственный']):
        cell_text(tb.rows[0].cells[i], h, size=7, bold=True, color=NAVY)
        shade(tb.rows[0].cells[i], 'EEF0FF')
        if 0 < i < 13:
            tb.rows[0].cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name, ms, who in rows:
        row = tb.add_row()
        no_split(row)
        cell_text(row.cells[0], name, size=7.5)
        for k in range(1, 13):
            mark = '●' if ms == 'all' or (ms not in ('all', 'all2') and k in ms) else ('2×' if ms == 'all2' else '')
            cell_text(row.cells[k], mark, size=7.5, bold=True, color=INDIGO)
            row.cells[k].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell_text(row.cells[13], who, size=7.5)
    fixed_layout(tb, widths)
    para(doc, '', after=2)


def opt_png(src):
    from PIL import Image
    dst = src.with_name(src.stem + '-docx.png')
    im = Image.open(src).convert('RGB')
    if im.width > 1900:
        im = im.resize((1900, round(im.height * 1900 / im.width)), Image.LANCZOS)
    im = im.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(dst, optimize=True)
    return dst


def page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    p.paragraph_format.space_after = Pt(0)


def setup(doc):
    s = doc.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.top_margin, s.bottom_margin = Mm(18), Mm(16)
    s.left_margin, s.right_margin = Mm(20), Mm(12)
    s.header_distance, s.footer_distance = Mm(8), Mm(7)
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
    s.different_first_page_header_footer = True
    hp = s.header.paragraphs[0]
    for pp in (hp, s.footer.paragraphs[0]):
        pp.paragraph_format.tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CLEAR)
        pp.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.CLEAR)
    hp.paragraph_format.tab_stops.add_tab_stop(Mm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
    runs(hp, 'Программа производственного контроля\t⟦' + C.ORG + '⟧', size=7.5, color=LIGHT)
    fp = s.footer.paragraphs[0]
    fp.paragraph_format.tab_stops.add_tab_stop(Mm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
    runs(fp, 'Шаблон ПЕСТКОНТРОЛЬ Центра · пестконтроль-центр.рф · +7 (495) 104-35-70\tСтр. ', size=7, color=LIGHT)
    field(fp, 'PAGE')
    runs(fp, ' из ', size=7, color=LIGHT)
    field(fp, 'NUMPAGES')


def cover(doc):
    c = C.COVER
    para(doc, 'ПЕСТКОНТРОЛЬ ЦЕНТР · дератизация, дезинсекция и пест-контроль для организаций', size=8, bold=True, color=INDIGO, after=2)
    para(doc, 'Шаблон документа: значения, выделенные жёлтым, замените данными своего объекта', size=8, color=GREY, after=18)
    tb = doc.add_table(rows=1, cols=2)
    borders(tb, none=True)
    for i, (title, lines) in enumerate(((c['agree_title'], c['agree']), (c['approve_title'], c['approve']))):
        cl = tb.rows[0].cells[i]
        cell_text(cl, title, size=9.5, bold=True, color=DARK)
        for ln in lines:
            p = cl.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            runs(p, ln, size=9.5)
    fixed_layout(tb, [89, 89])
    para(doc, '', after=60)
    para(doc, c['kicker'].upper(), size=28, bold=True, color=DARK, after=0, line=1.0)
    para(doc, c['title'], size=20, bold=True, color=INDIGO, after=10, line=1.0)
    para(doc, c['subtitle'], size=11, color=INK, after=6)
    para(doc, c['basis'], size=8.5, color=GREY, after=22)
    tb = doc.add_table(rows=0, cols=2)
    borders(tb, color='E4E4E7')
    cell_margins(tb, top=70, bottom=70)
    for a, b in c['rows']:
        row = tb.add_row()
        cell_text(row.cells[0], a, size=8.5, bold=True, color=GREY)
        cell_text(row.cells[1], b, size=8.5)
    fixed_layout(tb, [38, TEXT_W - 38])
    para(doc, '', after=30)
    note = c['sample_note'].replace('выделенные синим', 'выделенные жёлтым')
    tb = doc.add_table(rows=1, cols=1)
    borders(tb, color='DCDCFB')
    cell_margins(tb, top=110, bottom=110, left=150, right=150)
    cell_text(tb.rows[0].cells[0], note, size=8.5)
    shade(tb.rows[0].cells[0], 'F5F5FF')
    fixed_layout(tb, [TEXT_W])
    page_break(doc)


def toc(doc):
    para(doc, 'Содержание', size=15, bold=True, color=DARK, after=8)
    for num, title in C.TOC:
        lab = f'Приложение {num[1:]}' if num.startswith('П') else num + '.'
        p = para(doc, '', after=2)
        p.paragraph_format.tab_stops.add_tab_stop(Mm(26 if num.startswith('П') else 10))
        r = p.add_run(lab + '\t')
        r.bold = True
        r.font.color.rgb = INDIGO if not num.startswith('П') else GREY
        runs(p, title, size=9.5)
    para(doc, '', after=10)
    para(doc, 'Как пользоваться шаблоном', size=10, bold=True, color=NAVY, after=3)
    for x in [
        'Значения, выделенные жёлтым, — пример для хлебопекарного производства: замените их данными своего объекта и снимите выделение.',
        'Периодичность исследований и критические пределы установите по результатам анализа опасностей и согласуйте с испытательной лабораторией.',
        'Для кафе, столовой или магазина замените разделы 2, 5 и 6 и ссылки в разделе 3 (СанПиН 2.3/2.4.4282-26, СП 2.3.6.4281-26).',
        'Раздел 11.3 «Дезинсекция и дератизация» и схему точек (приложение 1) заполнит исполнитель ДДД после обследования.',
        'Автоматическое оглавление с номерами страниц: «Ссылки» → «Оглавление» (заголовки разделов оформлены стилями «Заголовок 1» и «Заголовок 2»).',
    ]:
        bullet(doc, x)
    page_break(doc)


def build(out_path, tmp_dir):
    tmp_dir = pathlib.Path(tmp_dir)
    doc = Document()
    setup(doc)
    cover(doc)
    toc(doc)
    for b in C.DOC:
        k = b[0]
        if k == 'h1':
            h1(doc, b[1], b[2], b[3])
        elif k == 'h2':
            h2(doc, b[1], b[2])
        elif k == 'p':
            para(doc, b[1], after=5)
        elif k == 'ul':
            for x in b[1]:
                bullet(doc, x)
        elif k == 'table':
            table(doc, b[1])
        elif k == 'ccp':
            ccp(doc, b[1])
        elif k == 'pest':
            pest(doc, b[1])
        elif k == 'signs2':
            para(doc, '', after=8)
            signs2(doc, b[1])
        elif k == 'cal':
            cal(doc, b[1])
    for b in C.APPX:
        k = b[0]
        if k == 'appendix':
            page_break(doc)
            para(doc, f'ПРИЛОЖЕНИЕ {b[1]}', size=8.5, bold=True, color=INDIGO, after=1)
            p = doc.add_paragraph(style='Heading 1')
            runs(p, b[2], color=DARK)
            p.paragraph_format.space_after = Pt(8)
        elif k == 'plan':
            doc.add_picture(str(opt_png(tmp_dir / 'plan.png')), width=Mm(TEXT_W))
        elif k == 'flow':
            doc.add_picture(str(opt_png(tmp_dir / 'flow.png')), width=Mm(TEXT_W))
        elif k == 'form':
            form(doc, b[1])
        elif k == 'sources':
            for t, u in b[1]:
                p = para(doc, '', after=1)
                runs(p, t, size=9, bold=True)
                q = para(doc, '', after=5)
                hyperlink(q, u, u)
    cp = doc.core_properties
    cp.title = 'Шаблон программы производственного контроля (ППК) для пищевого производства с процедурами ХАССП'
    cp.author = 'ПЕСТКОНТРОЛЬ Центр (пестконтроль-центр.рф)'
    cp.subject = 'Программа производственного контроля по СП 1.1.1058-01 и ТР ТС 021/2011'
    cp.keywords = 'программа производственного контроля, ППК, шаблон, ХАССП, ККТ, пищевое производство'
    cp.comments = 'Значения, выделенные жёлтым, заменяются данными объекта. Образец PDF: пестконтроль-центр.рф'
    cp.last_modified_by = 'ПЕСТКОНТРОЛЬ Центр'
    doc.save(str(out_path))
    return out_path


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2]))
