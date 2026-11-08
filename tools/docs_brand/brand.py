"""Фирменная шапка и водяной знак для документов-образцов ПЕСТКОНТРОЛЬ Центра.

Шапка — как в журнале пест-контроля (tools/zhurnal): логотип, «ПЕСТКОНТРОЛЬ ЦЕНТР», строка о компании и справа
крупно телефон и адрес сайта с фиолетовыми значками, под шапкой фиолетовая линия. Водяной знак — диагональная надпись
«пестконтроль-центр.рф» контурами букв Inter (tools/zhurnal/wm.py): цвет #7c4dff, прозрачность 12 %, −45°.

Используется в сборке образца ППК (tools/ppk/sample), в tools/docs_brand/brand_pdf.py (образец и пустой шаблон программы
пест-контроля, договор) и в tools/docs_brand/brand_docx.py (шаблон Word программы — только для файлов проекта, на сайте с 08.11.2026 нет).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONTS = ROOT / 'fonts'
sys.path.insert(0, str(ROOT / 'tools' / 'zhurnal'))
from wm import watermark_svg  # noqa: E402

CO = {
    'brand': 'ПЕСТКОНТРОЛЬ Центр',
    'phone': '+7 (495) 104-35-70',
    'site': 'пестконтроль-центр.рф',
    'mail': 'b2b@pestcontrol-center.ru',
}
VIOLET = '#615fff'
WM = dict(length_mm=232, color='#7c4dff', opacity=0.12, angle=-45)

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

_RANGES_RU = ('U+0020-007E,U+00A0,U+00A9,U+00AB,U+00AD,U+00B0,U+00B7,U+00BB,U+00D7,U+0401,U+0410-044F,U+0451,U+2009,'
              'U+2010-2015,U+2018-201E,U+2022,U+2026,U+202F,U+2116,U+20BD,U+2192,U+2212')
_RANGES_LAT = ('U+0000-001F,U+007F-009F,U+00A1-00A8,U+00AA,U+00AC,U+00AE-00AF,U+00B1-00B6,U+00B8-00BA,U+00BC-00D6,'
               'U+00D8-00FF,U+2000-2008,U+200A-200F,U+2016-2017,U+201F-2021,U+2023-2025,U+2027-202E,U+2030-206F,U+2122,U+2191,U+2193')


def font_css(fonts_dir=FONTS):
    f = pathlib.Path(fonts_dir).resolve().as_uri()
    return (f'@font-face{{font-family:Inter;font-style:normal;font-weight:100 900;src:url({f}/inter-ru-wght-normal.woff2) '
            f'format("woff2");unicode-range:{_RANGES_RU}}}'
            f'@font-face{{font-family:Inter;font-style:normal;font-weight:100 900;src:url({f}/inter-latin-wght-normal.woff2) '
            f'format("woff2");unicode-range:{_RANGES_LAT}}}')


def header_css(s=1.0):
    """CSS шапки журнала; s — масштаб (1.0 — как в журнале: телефон 17 pt, сайт 15,5 pt)."""
    def mm(v):
        return f'{v * s:.2f}mm'

    def pt(v):
        return f'{v * s:.2f}pt'
    return (f'.hd{{display:flex;align-items:center;justify-content:space-between;gap:{mm(6)};padding-bottom:{mm(2.6)};'
            f'border-bottom:{mm(.7)} solid {VIOLET};font-family:Inter,Arial,sans-serif;color:#18181b;'
            f'-webkit-print-color-adjust:exact;print-color-adjust:exact}}'
            f'.hd .brand{{display:flex;align-items:center;gap:{mm(3)};min-width:0}}'
            f'.hd .lg{{width:{mm(12.5)};height:{mm(12.5)};flex:none;display:block}}'
            f'.hd .bn{{font-weight:700;font-size:{pt(13.5)};letter-spacing:-.015em;line-height:1;white-space:nowrap;color:#09090b}}'
            f'.hd .bn small{{font-weight:600;font-size:{pt(7)};color:{VIOLET};letter-spacing:.16em;margin-left:{mm(1.6)};vertical-align:.2em}}'
            f'.hd .bt{{font-size:{pt(6.8)};color:#52525b;margin-top:{mm(1.4)};white-space:nowrap}}'
            f'.hd .hc{{display:grid;grid-template-columns:auto auto;align-items:center;column-gap:{mm(2.4)};row-gap:{mm(1.6)}}}'
            f'.hd .hc i{{width:{mm(6.4)};height:{mm(6.4)};border-radius:50%;background:{VIOLET};display:grid;place-items:center}}'
            f'.hd .hc i svg{{width:{mm(3.5)};height:{mm(3.5)};display:block}}'
            f'.hd .hc b{{display:block;line-height:1;white-space:nowrap}}'
            f'.hd .hc .ph{{font-size:{pt(17)};font-weight:750;letter-spacing:-.01em;color:#09090b}}'
            f'.hd .hc .st{{font-size:{pt(15.5)};font-weight:650;letter-spacing:-.01em;color:{VIOLET}}}')


def header_html(tagline='Пест-контроль для организаций · IPM / ХАССП'):
    return (f'<header class="hd"><div class="brand">{LOGO}<div><div class="bn">ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>'
            f'<div class="bt">{tagline}</div></div></div>'
            f'<div class="hc"><i>{IC_PHONE}</i><b class="ph">{CO["phone"]}</b><i>{IC_GLOBE}</i><b class="st">{CO["site"]}</b></div></header>')


def header_doc(width_mm, s=1.0, tagline='Пест-контроль для организаций · IPM / ХАССП', fonts_dir=FONTS):
    """Отдельная страница с одной шапкой шириной width_mm — для вставки в готовый PDF или картинкой в Word."""
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>' + font_css(fonts_dir) +
            f'html,body{{margin:0;padding:0;background:transparent}}body{{width:{width_mm}mm}}' + header_css(s) +
            '</style></head><body>' + header_html(tagline) + '</body></html>')


def watermark_doc(w_mm=210, h_mm=297, top_pct=54, fonts_dir=FONTS):
    """Страница с одним водяным знаком по центру (как на листах журнала) — накладывается на страницы PDF."""
    svg = watermark_svg(fonts_dir, length_mm=WM['length_mm'], color=WM['color'], opacity=WM['opacity'])
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>'
            f'@page{{size:{w_mm}mm {h_mm}mm;margin:0}}html,body{{margin:0;padding:0;background:transparent}}'
            f'.pg{{position:relative;width:{w_mm}mm;height:{h_mm}mm;overflow:hidden}}'
            f'.wm{{position:absolute;left:50%;top:{top_pct}%;transform:translate(-50%,-50%) rotate({WM["angle"]}deg)}}'
            '</style></head><body><div class="pg">' + svg + '</div></body></html>')


def runner_css(s=1.0):
    """Компактная шапка следующих страниц (одна строка): название слева, телефон и сайт справа, фиолетовая линия."""
    def mm(v):
        return f'{v * s:.2f}mm'

    def pt(v):
        return f'{v * s:.2f}pt'
    return (f'.rh{{display:flex;align-items:center;justify-content:space-between;gap:{mm(4)};padding-bottom:{mm(1.1)};'
            f'border-bottom:{mm(.4)} solid {VIOLET};font-family:Inter,Arial,sans-serif;line-height:1;'
            f'-webkit-print-color-adjust:exact;print-color-adjust:exact}}'
            f'.rh .bn{{font-weight:700;font-size:{pt(8.6)};letter-spacing:-.01em;white-space:nowrap;color:#09090b}}'
            f'.rh .bn small{{font-weight:600;font-size:{pt(5)};color:{VIOLET};letter-spacing:.16em;margin-left:{mm(1)};vertical-align:.15em}}'
            f'.rh .hc{{display:flex;align-items:center;gap:{mm(1.5)}}}'
            f'.rh .hc i{{width:{mm(3.6)};height:{mm(3.6)};border-radius:50%;background:{VIOLET};display:grid;place-items:center}}'
            f'.rh .hc i svg{{width:{mm(2)};height:{mm(2)};display:block}}'
            f'.rh .hc b{{display:block;white-space:nowrap}}'
            f'.rh .hc .ph{{font-size:{pt(9.6)};font-weight:750;color:#09090b;margin-right:{mm(2.6)}}}'
            f'.rh .hc .st{{font-size:{pt(9.2)};font-weight:650;color:{VIOLET}}}')


def runner_html():
    return (f'<header class="rh"><div class="bn">ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>'
            f'<div class="hc"><i>{IC_PHONE}</i><b class="ph">{CO["phone"]}</b><i>{IC_GLOBE}</i><b class="st">{CO["site"]}</b></div></header>')


def runner_doc(width_mm, s=1.0, fonts_dir=FONTS):
    """Отдельная страница с одной компактной шапкой шириной width_mm — для страниц 2+ готовых PDF."""
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>' + font_css(fonts_dir) +
            f'html,body{{margin:0;padding:0;background:transparent}}body{{width:{width_mm}mm}}' + runner_css(s) +
            '</style></head><body>' + runner_html() + '</body></html>')


# Водяной знак Word (VML WordArt, как создаёт «Конструктор → Подложка»): Calibri, 540 × 82 pt (пропорции надписи),
# цвет как в PDF, прозрачность 85 %, наклон 45°, по центру поля страницы, за текстом.
_NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:v="urn:schemas-microsoft-com:vml" '
       'xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w10="urn:schemas-microsoft-com:office:word"')


def docx_watermark_run(with_ns=False, text=None, w_pt=540, h_pt=82, opacity='.15', shape_id=1):
    """Прогон <w:r> с подложкой для вставки в абзац колонтитула (with_ns — с объявлениями пространств имён)."""
    text = text or CO['site']
    ns = (' ' + _NS) if with_ns else ''
    return (
        f'<w:r{ns}><w:rPr><w:noProof/></w:rPr><w:pict>'
        '<v:shapetype id="_x0000_t136" coordsize="21600,21600" o:spt="136" adj="10800" path="m@7,l@8,m@5,21600l@6,21600e">'
        '<v:formulas><v:f eqn="sum #0 0 10800"/><v:f eqn="prod #0 2 1"/><v:f eqn="sum 21600 0 @1"/><v:f eqn="sum 0 0 @2"/>'
        '<v:f eqn="sum 21600 0 @3"/><v:f eqn="if @0 @3 0"/><v:f eqn="if @0 21600 @1"/><v:f eqn="if @0 0 @2"/>'
        '<v:f eqn="if @0 @4 21600"/><v:f eqn="mid @5 @6"/><v:f eqn="mid @8 @5"/><v:f eqn="mid @7 @8"/><v:f eqn="mid @6 @7"/>'
        '<v:f eqn="sum @6 0 @5"/></v:formulas>'
        '<v:path textpathok="t" o:connecttype="custom" o:connectlocs="@9,0;@10,10800;@11,21600;@12,10800" o:connectangles="270,180,90,0"/>'
        '<v:textpath on="t" fitshape="t"/><v:handles><v:h position="#0,bottomRight" xrange="6629,14971"/></v:handles>'
        '<o:lock v:ext="edit" text="t" shapetype="t"/></v:shapetype>'
        f'<v:shape id="PowerPlusWaterMarkObject{shape_id}" o:spid="_x0000_s{2048 + shape_id}" type="#_x0000_t136" '
        f'style="position:absolute;margin-left:0;margin-top:0;width:{w_pt}pt;height:{h_pt}pt;rotation:315;z-index:-251657216;'
        'mso-position-horizontal:center;mso-position-horizontal-relative:margin;mso-position-vertical:center;'
        f'mso-position-vertical-relative:margin" o:allowincell="f" fillcolor="{WM["color"]}" stroked="f">'
        f'<v:fill opacity="{opacity}"/><v:textpath style="font-family:&quot;Calibri&quot;;font-size:1pt" string="{text}"/>'
        '<w10:wrap anchorx="margin" anchory="margin"/></v:shape></w:pict></w:r>')
