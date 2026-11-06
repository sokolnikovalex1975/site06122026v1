"""Векторный водяной знак (контуры букв Inter, не текст): не мешает извлечению текста из PDF и не удаляется как текстовый слой."""
import pathlib

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer


def text_path(fonts_dir, text='пестконтроль-центр.рф', wght=600):
    fonts_dir = pathlib.Path(fonts_dir)
    fonts = []
    for fn in ('inter-ru-wght-normal.woff2', 'inter-latin-wght-normal.woff2'):
        f = TTFont(str(fonts_dir / fn))
        if 'fvar' in f:
            f = instancer.instantiateVariableFont(f, {'wght': wght})
        fonts.append((f, f.getBestCmap(), f.getGlyphSet()))
    x = 0
    parts = []
    bp_all = None
    xmin = ymin = 10 ** 9
    xmax = ymax = -10 ** 9
    for ch in text:
        for f, cm, gs in fonts:
            if ord(ch) in cm:
                g = cm[ord(ch)]
                pen = SVGPathPen(gs)
                gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
                parts.append(pen.getCommands())
                bp = BoundsPen(gs)
                gs[g].draw(TransformPen(bp, (1, 0, 0, -1, x, 0)))
                if bp.bounds:
                    a, b, c, d = bp.bounds
                    xmin, ymin, xmax, ymax = min(xmin, a), min(ymin, b), max(xmax, c), max(ymax, d)
                x += f['hmtx'][g][0]
                break
        else:
            raise ValueError(f'Нет глифа для {ch!r}')
    import re
    d = re.sub(r'-?\d+\.\d+', lambda m: str(round(float(m.group()))), ' '.join(parts))
    return d, (xmin, ymin, xmax - xmin, ymax - ymin)


def watermark_svg(fonts_dir, length_mm=232, color='#7c4dff', opacity=0.12):
    d, (x, y, w, h) = text_path(fonts_dir)
    pad = h * 0.1
    vb = f'{x - pad:.0f} {y - pad:.0f} {w + 2 * pad:.0f} {h + 2 * pad:.0f}'
    hmm = length_mm * (h + 2 * pad) / (w + 2 * pad)
    return (f'<svg class="wm" viewBox="{vb}" style="width:{length_mm}mm;height:{hmm:.1f}mm" aria-hidden="true">'
            f'<path d="{d}" fill="{color}" fill-opacity="{opacity}"/></svg>')


if __name__ == '__main__':
    import sys
    s = watermark_svg(sys.argv[1])
    print(len(s), s[:200])
