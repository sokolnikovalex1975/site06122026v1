# -*- coding: utf-8 -*-
"""HTML образца ППК для печати в PDF (Chromium) + шаблоны колонтитулов.

Запуск: python3 tools/ppk/sample/render_html.py <out_dir> [pages.json]
pages.json — номера страниц разделов после первого прохода (для оглавления).
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tools' / 'zhurnal'))
sys.path.insert(0, str(ROOT / 'tools' / 'docs_brand'))
import brand  # noqa: E402
import content as C  # noqa: E402
from wm import watermark_svg  # noqa: E402

NB = '\u00a0'
LOGO = ('<svg class="lg" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#09090b"/>'
        '<g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round">'
        '<path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/>'
        '<circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/>'
        '<path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>')

SHORT = ('в', 'и', 'к', 'с', 'у', 'о', 'а', 'на', 'по', 'до', 'от', 'за', 'не', 'из', 'без', 'для', 'при', 'или', 'со', 'во', 'об')
CODE_RE = re.compile(r'(?:ТР ТС|ТР ЕАЭС|СанПиН|СП|ГОСТ Р ИСО|ГОСТ Р|ГОСТ|МУК|МР|ОКВЭД|RA\.RU)\s?[\d.\-/]+[\d]|'
                     r'№\s?[\wА-Яа-я\-/]+|[\d.]+-\d{2,4}(?:-\d{2})?')


def typo(s):
    s = s.replace(' - ', ' — ')
    # неразрывные пробелы после сокращений и номеров
    s = re.sub(r'(№|пп\.|п\.|ст\.|ч\.|прил\.|разд\.|изм\.|инв\.|г\. о\.|д\.|стр\.|т\. е\.|т\. ч\.|т\. д\.) ', lambda m: m.group(1) + NB, s)
    s = re.sub(r'(ТР|ТС|ЕАЭС|СанПиН|СП|ГОСТ|Р|ИСО|МУК|МР|ОКВЭД) (?=[\d])', lambda m: m.group(1) + NB, s)
    s = s.replace('ТР ТС', 'ТР' + NB + 'ТС').replace('ГОСТ Р', 'ГОСТ' + NB + 'Р').replace('Р ИСО', 'Р' + NB + 'ИСО')
    # число + единица
    s = re.sub(r'(\d) (°C|°|мм|м²|м|кг|т/сут|т|ч|мин|%|га|лет|года|год|суток|сутки|раз|раза|смены|смен|мес|человек|чел\.)(?=[\s,.;:)»]|$)',
               lambda m: m.group(1) + NB + m.group(2), s)
    s = re.sub(r'(\d) ([×±—–]) (\d)', lambda m: m.group(1) + NB + m.group(2) + NB + m.group(3), s)
    s = re.sub(r'([+−-]\d+) ± (\d)', lambda m: m.group(1) + NB + '±' + NB + m.group(2), s)
    s = re.sub(r'(\d) (\d{3})(?!\d)', lambda m: m.group(1) + NB + m.group(2), s)  # 1 450
    s = re.sub(r'(\d{4}) (г\.)', lambda m: m.group(1) + NB + m.group(2), s)
    # короткие слова не висят в конце строки
    for _ in range(2):
        s = re.sub(r'(^|[\s(«])(' + '|'.join(SHORT) + r') ', lambda m: m.group(1) + m.group(2) + NB, s, flags=re.I)
    s = re.sub(r' (—|–) ', NB + r'\1 ', s)
    return s


def inline(s):
    s = typo(s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'⟦(.+?)⟧', r'<span class="v">\1</span>', s)
    # коды документов не переносить по дефису
    s = re.sub(r'((?:ТР|СанПиН|СП|ГОСТ|МУК|МР)(?:\u00a0[А-ЯA-Z]+)*\u00a0[\d.]+[\-/][\d.\-/]+|[\d.]+-\d{2}(?:-\d{2})?|\d{2}\.\d{2}\.\d{4}|Л064-[\d\-/]+|RA\.RU\.[_\d]+)',
               r'<span class="nw">\1</span>', s)
    return s


def cell(s):
    lines = [x for x in s.split('\n')]
    out, ul = [], []
    for ln in lines:
        if ln.startswith('• '):
            ul.append('<li>' + inline(ln[2:]) + '</li>')
            continue
        if ul:
            out.append('<ul>' + ''.join(ul) + '</ul>')
            ul = []
        out.append(('<div>' + inline(ln) + '</div>') if len(lines) > 1 else inline(ln))
    if ul:
        out.append('<ul>' + ''.join(ul) + '</ul>')
    return ''.join(out)


def table(t):
    cols = ''.join(f'<col style="width:{w}%">' for w in t['cols'])
    cls = ['t']
    if t.get('small'):
        cls.append('sm')
    if t.get('kv'):
        cls.append('kv')
    head = ''.join(f'<th>{inline(h)}</th>' for h in t['head'])
    rows = []
    n = len(t['cols'])
    last = ''
    for r in t['rows']:
        if r[0] == 'grp':
            rows.append(f'<tr class="grp"><td colspan="{n}">{inline(r[1])}</td></tr>')
            continue
        tds = []
        for i, c in enumerate(r):
            if c == '' and i == 0:
                tds.append(f'<td class="cont"><span>{inline(last)}</span></td>')
            else:
                if i == 0:
                    last = c
                tds.append(f'<td>{cell(c)}</td>')
        rows.append('<tr>' + ''.join(tds) + '</tr>')
    return (f'<table class="{" ".join(cls)}"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def form(f):
    cols = ''.join(f'<col style="width:{w}%">' for w in f['cols'])
    head = ''.join(f'<th>{inline(h)}</th>' for h in f['head'])
    rows = []
    if f.get('example'):
        rows.append('<tr class="ex">' + ''.join(f'<td>{inline(c)}</td>' for c in f['example']) + '</tr>')
    for i in range(f['rows']):
        tds = []
        for j in range(len(f['cols'])):
            tds.append(f'<td>{i + 1 if (f.get("numbered") and j == 0) else ""}</td>')
        rows.append('<tr class="blank">' + ''.join(tds) + '</tr>')
    meta = f'<p class="fmeta">{inline(f["meta"])}</p>' if f.get('meta') else ''
    ex = '<p class="fnote">Первая строка — пример заполнения.</p>' if f.get('example') else ''
    return (f'<div class="form"><div class="ftitle">{inline(f["title"])}</div>{meta}'
            f'<table class="t frm"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>{ex}</div>')


# ───────────── План-схема (приложение 1) ─────────────
ROOMS = [
    # id, x, y, w, h, подпись (строки), зона
    ('A1', 0, 0, 9, 12, ['Склад бестарного', 'хранения муки'], 'store'),
    ('A2', 9, 0, 9, 12, ['Склад тарного', 'хранения муки'], 'store'),
    ('A3', 18, 0, 6, 12, ['Просеива-', 'тельное'], 'prod'),
    ('A4', 24, 0, 14, 12, ['Тестоприготовительное', 'и тесторазделочное'], 'prod'),
    ('A5', 38, 0, 6, 12, ['Расстойное'], 'prod'),
    ('A6', 44, 0, 16, 12, ['Пекарное отделение', '(2 ротационные,', '1 тоннельная печь)'], 'prod'),
    ('B', 0, 12, 60, 3, [], 'corr'),
    ('C1', 0, 15, 6, 10, ['Приёмка', 'сырья'], 'store'),
    ('C2', 6, 15, 12, 10, ['Склад сырья,', 'холодильные камеры'], 'store'),
    ('C3', 18, 15, 5, 10, ['Обра-', 'ботка', 'яиц'], 'cream'),
    ('C4', 23, 15, 11, 10, ['Кремовый цех'], 'cream'),
    ('C5', 34, 15, 8, 10, ['Охлаждение,', 'упаковка конд.', 'изделий'], 'cream'),
    ('C6', 42, 15, 9, 10, ['Остывочное'], 'prod'),
    ('C7', 51, 15, 9, 10, ['Упаковка', 'хлеба'], 'prod'),
    ('D1', 0, 25, 12, 11, ['Гардеробные,', 'душевые, санузлы'], 'aux'),
    ('D2', 12, 25, 6, 5, ['Санпро-', 'пускник'], 'aux'),
    ('D3', 12, 30, 6, 6, ['Кладовая', 'дезсредств'], 'aux'),
    ('D4', 18, 25, 8, 11, ['Моечная', 'инвентаря', 'и тары'], 'aux'),
    ('D5', 26, 25, 7, 11, ['Лабора-', 'тория'], 'aux'),
    ('D6', 33, 25, 7, 11, ['Комната', 'приёма', 'пищи'], 'aux'),
    ('D7', 40, 25, 20, 11, ['Экспедиция'], 'store'),
]
ZONE_FILL = {'store': '#f4f4f5', 'prod': '#eef0ff', 'cream': '#fdf2f8', 'aux': '#ffffff', 'corr': '#fafafa'}


def plan_svg():
    S = 3.0  # мм на метр
    ox, oy = 17, 13  # отступ здания внутри рисунка, мм
    W, H = 60 * S + 2 * ox, 36 * S + 2 * oy + 3
    o = [f'<svg class="plan" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}mm" height="{H:.0f}mm" font-family="Inter" xmlns="http://www.w3.org/2000/svg">']
    o.append('<defs><marker id="ar" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M0 0L5 2.5L0 5z" fill="#4f46e5"/></marker></defs>')
    o.append(f'<rect x="{ox - 8}" y="{oy - 8}" width="{60 * S + 16}" height="{36 * S + 16}" rx="3" fill="none" stroke="#c4c4cc" stroke-width=".35" stroke-dasharray="1.4 1.2"/>')
    for rid, x, y, w, h, lab, z in ROOMS:
        X, Y = ox + x * S, oy + y * S
        o.append(f'<rect x="{X:.1f}" y="{Y:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" fill="{ZONE_FILL[z]}" stroke="#3f3f46" stroke-width=".45"/>')
        if lab:
            n = len(lab)
            cyy = Y + h * S / 2 - (1.2 if rid in ('C2', 'D7') else 0)
            for k, t in enumerate(lab):
                ty = cyy + (k - (n - 1) / 2) * 2.9 + 0.9
                o.append(f'<text x="{X + w * S / 2:.1f}" y="{ty:.1f}" font-size="2.35" text-anchor="middle" fill="#27272a">{html.escape(t)}</text>')
    o.append(f'<rect x="{ox}" y="{oy}" width="{60 * S}" height="{36 * S}" fill="none" stroke="#09090b" stroke-width="1.1"/>')
    cy = oy + 13.5 * S
    o.append(f'<text x="{ox + 2}" y="{cy + 0.9:.1f}" font-size="2.2" fill="#71717a">Технологический коридор</text>')
    o.append(f'<path d="M{ox + 25 * S:.1f} {cy:.1f} H{ox + 50 * S:.1f}" stroke="#4f46e5" stroke-width=".6" marker-end="url(#ar)"/>')
    o.append(f'<text x="{ox + 37.5 * S:.1f}" y="{cy - 1.3:.1f}" font-size="2.1" text-anchor="middle" fill="#4f46e5">поток: сырьё → готовая продукция</text>')
    for k in range(2):
        o.append(f'<circle cx="{ox + (2.5 + k * 4) * S:.1f}" cy="{oy + 9.1 * S:.1f}" r="{1.45 * S:.1f}" fill="#fff" stroke="#71717a" stroke-width=".35"/>')
    o.append(f'<text x="{ox + 4.5 * S:.1f}" y="{oy + 11.55 * S:.1f}" font-size="1.9" text-anchor="middle" fill="#52525b">силосы 2 × 30 т</text>')
    # проёмы
    o.append(f'<rect x="{ox - .8:.1f}" y="{oy + 18 * S:.1f}" width="1.6" height="{3 * S:.1f}" fill="#fff" stroke="#09090b" stroke-width=".4"/>')
    o.append(f'<text x="{ox - 1.8:.1f}" y="{oy + 19.5 * S + .8:.1f}" font-size="2.2" font-weight="600" text-anchor="end" fill="#09090b">Приёмка →</text>')
    o.append(f'<rect x="{ox + 60 * S - .8:.1f}" y="{oy + 30 * S:.1f}" width="1.6" height="{3.5 * S:.1f}" fill="#fff" stroke="#09090b" stroke-width=".4"/>')
    o.append(f'<text x="{ox + 60 * S + 1.8:.1f}" y="{oy + 31.75 * S + .8:.1f}" font-size="2.2" font-weight="600" fill="#09090b">→ Отгрузка</text>')
    o.append(f'<rect x="{ox + 6 * S - 2:.1f}" y="{oy + 36 * S - .8:.1f}" width="4" height="1.6" fill="#fff" stroke="#09090b" stroke-width=".4"/>')
    o.append(f'<text x="{ox + 6 * S:.1f}" y="{oy + 36 * S + 4.4:.1f}" font-size="2.2" font-weight="600" text-anchor="middle" fill="#09090b">Вход персонала</text>')
    for (x, y, w, h, t) in [(6.4, 21.2, 3.6, 3.4, 'ХК-1'), (10.2, 21.2, 3.6, 3.4, 'ХК-2'), (14, 21.2, 3.6, 3.4, 'МК'), (55, 25.5, 4.6, 3.6, 'ХК-3')]:
        o.append(f'<rect x="{ox + x * S:.1f}" y="{oy + y * S:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" fill="#e0f2fe" stroke="#0369a1" stroke-width=".35"/>')
        o.append(f'<text x="{ox + (x + w / 2) * S:.1f}" y="{oy + (y + h / 2) * S + .8:.1f}" font-size="2.1" text-anchor="middle" fill="#0c4a6e">{t}</text>')

    def P(x, y):
        return ox + x * S, oy + y * S

    def lab(X, Y, t, col, side='b'):
        if side == 'b':
            o.append(f'<text x="{X:.1f}" y="{Y + 3.7:.1f}" font-size="1.8" text-anchor="middle" fill="{col}">{t}</text>')
        elif side == 'r':
            o.append(f'<text x="{X + 2.6:.1f}" y="{Y + .7:.1f}" font-size="1.8" fill="{col}">{t}</text>')
        elif side == 'l':
            o.append(f'<text x="{X - 2.6:.1f}" y="{Y + .7:.1f}" font-size="1.8" text-anchor="end" fill="{col}">{t}</text>')
        elif side == 't':
            o.append(f'<text x="{X:.1f}" y="{Y - 2.4:.1f}" font-size="1.8" text-anchor="middle" fill="{col}">{t}</text>')

    # К-01…К-14 — наружный периметр
    ks = [(5, -3, 't'), (17, -3, 't'), (31, -3, 't'), (45, -3, 't'), (56, -3, 't'),
          (63, 6, 'r'), (63, 20, 'r'),
          (55, 39, 'b'), (40, 39, 'b'), (26, 39, 'b'), (14, 39, 'b'), (2, 39, 'b'),
          (-3, 30, 'l'), (-3, 6, 'l')]
    for i, (x, y, sd) in enumerate(ks, 1):
        X, Y = P(x, y)
        o.append(f'<rect x="{X - 1.5:.1f}" y="{Y - 1.5:.1f}" width="3" height="3" fill="#09090b"/>')
        lab(X, Y, f'К-{i:02d}', '#27272a', sd)
    # Л-01…Л-26 — внутренние ловушки без родентицидов
    ls = [(0.8, 0.8), (8.2, 0.8), (9.8, 0.8), (17.2, 0.8), (18.8, 11.2), (24.8, 0.8), (37.2, 11.2), (38.8, 0.8), (44.8, 11.2), (59.2, 0.8),
          (0.8, 24.2), (6.8, 15.8), (17.2, 15.8), (18.8, 24.2), (23.8, 24.2), (33.2, 24.2), (34.8, 24.2), (41.2, 24.2), (42.8, 15.8), (59.2, 24.2),
          (0.8, 35.2), (17.2, 25.8), (18.8, 35.2), (26.8, 35.2), (40.8, 35.2), (59.2, 35.2)]
    for (x, y) in ls:
        X, Y = P(x, y)
        o.append(f'<rect x="{X - 1.05:.1f}" y="{Y - 1.05:.1f}" width="2.1" height="2.1" fill="#fff" stroke="#09090b" stroke-width=".45"/>')
    # И-01…И-06 — УФ-ловушки
    for i, (x, y, sd) in enumerate([(3, 16.7, 'b'), (40.5, 23.6, 't'), (49.3, 23.7, 'l'), (53.3, 16.7, 'b'), (22, 34.6, 'r'), (44, 34.6, 'r')], 1):
        X, Y = P(x, y)
        o.append(f'<rect x="{X - 2:.1f}" y="{Y - 1:.1f}" width="4" height="2" rx=".5" fill="#7c3aed"/>')
        lab(X, Y, f'И-{i:02d}', '#5b21b6', sd)
    # Ф-01…Ф-06 — феромонные ловушки
    for i, (x, y) in enumerate([(7.6, 2.4), (10.8, 2.4), (16.4, 2.4), (21, 2.4), (8.2, 16.9), (15.6, 16.9)], 1):
        X, Y = P(x, y)
        o.append(f'<path d="M{X:.1f} {Y - 1.7:.1f}L{X + 1.7:.1f} {Y + 1.2:.1f}H{X - 1.7:.1f}z" fill="#d97706"/>')
        lab(X, Y, f'Ф-{i:02d}', '#92400e', 'b')

    def dot(x, y, col, t):
        X, Y = P(x, y)
        o.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="1.9" fill="{col}"/><text x="{X:.1f}" y="{Y + .8:.1f}" font-size="2.05" font-weight="700" text-anchor="middle" fill="#fff">{t}</text>')

    dot(3, 23.4, '#0284c7', 'В1')
    dot(26.2, 10.2, '#0284c7', 'В2')
    for (x, y) in [(25.4, 23.2), (20.5, 23.4), (35.4, 23.4), (36, 10.2), (58.2, 16.9), (44.6, 23.4)]:
        dot(x, y, '#16a34a', 'С')
    for (x, y) in [(32, 23.2), (37.6, 23.4)]:
        dot(x, y, '#0d9488', 'В')

    def kkt(x, y, t):
        X, Y = P(x, y)
        o.append(f'<rect x="{X - 5.2:.1f}" y="{Y - 1.9:.1f}" width="10.4" height="3.8" rx="1.9" fill="#dc2626"/><text x="{X:.1f}" y="{Y + .8:.1f}" font-size="2.2" font-weight="700" text-anchor="middle" fill="#fff">{t}</text>')

    kkt(21, 10.1, 'ККТ-1')
    kkt(52, 10.1, 'ККТ-2')
    kkt(38, 16.9, 'ККТ-3')
    kkt(57.3, 31.2, 'ККТ-3')
    kkt(55.5, 23.4, 'ККТ-4')
    o.append('</svg>')
    return ''.join(o)


LEGEND = [
    ('<svg viewBox="0 0 6 6"><rect x="1.5" y="1.5" width="3" height="3" fill="#09090b"/></svg>', 'К-01…К-14 — защищённые приманочные станции по наружному периметру (родентициды только здесь)'),
    ('<svg viewBox="0 0 6 6"><rect x="1.8" y="1.8" width="2.4" height="2.4" fill="#fff" stroke="#09090b" stroke-width=".5"/></svg>', 'Л-01…Л-26 — ловушки для грызунов без родентицидов в помещениях; нумерация по часовой стрелке от склада муки'),
    ('<svg viewBox="0 0 6 6"><rect x="1" y="2" width="4" height="2" rx=".5" fill="#7c3aed"/></svg>', 'И-01…И-06 — ловушки для летающих насекомых с УФ-лампами (не над открытой продукцией)'),
    ('<svg viewBox="0 0 6 6"><path d="M3 1.2L4.8 4.4H1.2z" fill="#d97706"/></svg>', 'Ф-01…Ф-06 — феромонные ловушки для пищевой моли (склады муки и сырья)'),
    ('<svg viewBox="0 0 6 6"><circle cx="3" cy="3" r="2.2" fill="#0284c7"/></svg>', 'В1, В2 — отбор проб питьевой воды (раздел 5.4)'),
    ('<svg viewBox="0 0 6 6"><circle cx="3" cy="3" r="2.2" fill="#16a34a"/></svg>', 'С — зоны отбора смывов (раздел 5.3)'),
    ('<svg viewBox="0 0 6 6"><circle cx="3" cy="3" r="2.2" fill="#0d9488"/></svg>', 'В (бирюзовый) — отбор проб воздуха (раздел 5.3)'),
    ('<svg viewBox="0 0 6 6"><rect x=".4" y="1.6" width="5.2" height="2.8" rx="1.4" fill="#dc2626"/></svg>', 'ККТ-1…ККТ-4 — критические контрольные точки (раздел 6.3)'),
    ('<svg viewBox="0 0 6 6"><rect x="1" y="1" width="4" height="4" fill="#e0f2fe" stroke="#0369a1" stroke-width=".5"/></svg>', 'ХК-1 молочная продукция, ХК-2 яйцо (+2…+6 °C), МК (−18 °C), ХК-3 изделия с кремом (+4 ± 2 °C)'),
    ('<svg viewBox="0 0 6 6"><rect x=".6" y=".6" width="4.8" height="4.8" rx="1" fill="none" stroke="#a1a1aa" stroke-width=".5" stroke-dasharray="1 .8"/></svg>', 'Пунктир — ограждение территории (условно)'),
]


def plan_block():
    zones = (''.join(f'<span class="zn"><i style="background:{c}"></i>{t}</span>' for c, t in
                     [('#eef0ff', 'производство хлеба'), ('#fdf2f8', 'кремовый цех и кондитерский участок'), ('#f4f4f5', 'склады, приёмка, экспедиция'), ('#ffffff', 'вспомогательные и бытовые помещения')]))
    leg = ''.join(f'<div class="lg-i">{ic}<span>{inline(t)}</span></div>' for ic, t in LEGEND)
    return (f'<figure class="planfig">{plan_svg()}<div class="zones">{zones}</div>'
            f'<div class="legend">{leg}</div>'
            f'<figcaption>{inline("Схема условная, без масштаба. Номера и места точек пест-контроля уточняются исполнителем ДДД при обследовании и утверждаются ответственным; изменения вносятся в схему и в журнал учёта.")}</figcaption></figure>')


# ───────────── Блок-схема (приложение 2) ─────────────
FLOW_L = [('Приёмка сырья и упаковки', ''), ('Хранение сырья', ''), ('Просеивание и магнитная очистка муки', 'ККТ-1'),
          ('Приготовление теста: дозирование, замес, брожение', ''), ('Разделка и формование', ''), ('Расстойка', ''),
          ('Выпечка', 'ККТ-2'), ('Остывание', ''), ('Упаковка и маркировка', ''), ('Металлодетекция', 'ККТ-4'),
          ('Хранение и отгрузка', '')]
FLOW_R = [('Приёмка яиц и молочной продукции (ВСД «Меркурий»)', ''), ('Хранение при +2…+6 °C', ''), ('Санитарная обработка яиц', ''),
          ('Выпечка полуфабрикатов (бисквит, заварное тесто)', 'ККТ-2'), ('Приготовление крема', ''), ('Отделка изделий кремом', ''),
          ('Охлаждение и хранение при +4 ± 2 °C', 'ККТ-3'), ('Упаковка и маркировка', ''), ('Отгрузка в изотермическом транспорте', '')]


def flow_col(title, items):
    out = [f'<div class="fl-col"><div class="fl-h">{inline(title)}</div>']
    for i, (t, k) in enumerate(items):
        cls = 'fl-b kkt' if k else 'fl-b'
        badge = f'<span class="kb">{k}</span>' if k else ''
        out.append(f'<div class="{cls}">{badge}<span>{inline(t)}</span></div>')
        if i < len(items) - 1:
            out.append('<div class="fl-a"></div>')
    out.append('</div>')
    return ''.join(out)


def flow_block():
    return (f'<div class="flow">{flow_col("Хлеб и хлебобулочные изделия", FLOW_L)}{flow_col("Мучные кондитерские изделия с кремом", FLOW_R)}</div>'
            f'<div class="flow-notes"><div><span class="kb">ККТ</span>{inline(" — критические контрольные точки, пределы и мониторинг — в разделе 6.3.")}</div>'
            f'<div>{inline("На всех этапах действуют ПОПМ (раздел 6.4): уборка и дезинфекция, личная гигиена, пест-контроль, управление аллергенами, контроль стекла и хрупкого пластика. Схемы подтверждаются на месте рабочей группой ХАССП.")}</div></div>')


def sources_block(items):
    lis = ''.join(f'<li><span>{inline(t)}</span><a href="{html.escape(u)}">{html.escape(u)}</a></li>' for t, u in items)
    return f'<ol class="src">{lis}</ol>'


def pest_block(items):
    rows = ''.join(f'<div class="pi"><span class="pn">{n}</span><p>{inline(t)}</p></div>' for n, t in items)
    return (f'<div class="pest"><div class="pest-h"><span>Раздел заполняет исполнитель ДДД</span><span>пример для хлебопекарного производства</span></div>{rows}</div>')


CCP_F = [('hazard', 'Опасный фактор'), ('limit', 'Критический предел'), ('monitor', 'Мониторинг: как, когда, кто'),
         ('action', 'Корректирующие действия'), ('records', 'Записи и верификация')]


def ccp_block(items):
    out = []
    for c in items:
        rows = ''.join(f'<div class="l">{lab}</div><div class="r">{inline(c[k])}</div>' for k, lab in CCP_F)
        out.append(f'<div class="ccp"><div class="ccp-h"><span class="kb">{c["id"]}</span><b>{inline(c["stage"])}</b>'
                   f'<span class="hz">{inline(c["kind"])}</span></div><div class="ccp-g">{rows}</div></div>')
    return '<div class="ccps">' + ''.join(out) + '</div>'


def signs2_block(items):
    rows = ''.join(f'<div class="s2"><div class="s2-r">{inline(r)}</div><div class="s2-p">{inline(p)}</div>'
                   f'<div class="s2-l">________________ /{inline(n)}/</div><div class="s2-d">«___» ____________ 2026 г.</div></div>'
                   for r, p, n in items)
    return f'<div class="signs2">{rows}</div>'


MONTHS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']


def cal_block(rows):
    head = '<th>Мероприятие</th>' + ''.join(f'<th class="m">{m}</th>' for m in MONTHS) + '<th>Ответственный</th>'
    body = []
    for name, months, who in rows:
        tds = []
        for k in range(1, 13):
            if months == 'all':
                mark = '●'
            elif months == 'all2':
                mark = '2×'
            else:
                mark = '●' if k in months else ''
            tds.append(f'<td class="m">{mark}</td>')
        body.append(f'<tr><td>{inline(name)}</td>{"".join(tds)}<td>{inline(who)}</td></tr>')
    cols = '<col style="width:44%">' + '<col style="width:3.5%">' * 12 + '<col style="width:14%">'
    return f'<table class="t cal"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def render_blocks(blocks):
    out = []
    for b in blocks:
        k = b[0]
        if k == 'h1':
            _, num, title, sp = b
            spx = f'<span class="sp">{inline(sp)}</span>' if sp else ''
            out.append(f'<h1 class="sec" id="s{num}"><span class="no">{num}</span><span class="tt">{inline(title)}</span>{spx}</h1>')
        elif k == 'h2':
            out.append(f'<h2><span class="n2">{b[1]}.</span> {inline(b[2])}</h2>')
        elif k == 'p':
            out.append(f'<p>{inline(b[1])}</p>')
        elif k == 'ul':
            out.append('<ul class="ul">' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + '</ul>')
        elif k == 'note':
            out.append(f'<div class="note">{inline(b[1])}</div>')
        elif k == 'table':
            out.append(table(b[1]))
        elif k == 'pest':
            out.append(pest_block(b[1]))
        elif k == 'ccp':
            out.append(ccp_block(b[1]))
        elif k == 'signs2':
            out.append(signs2_block(b[1]))
        elif k == 'cal':
            out.append(cal_block(b[1]))
        elif k == 'appendix':
            out.append(f'<section class="appx" id="sA{b[1]}"><div class="ax-k">Приложение {b[1]}</div><h1 class="ax-t">{inline(b[2])}</h1>')
        elif k == 'plan':
            out.append(plan_block() + '</section>')
        elif k == 'flow':
            out.append(flow_block() + '</section>')
        elif k == 'form':
            out.append(form(b[1]) + '</section>')
        elif k == 'sources':
            out.append(sources_block(b[1]) + '</section>')
    return '\n'.join(out)


def cover():
    c = C.COVER
    agree = ''.join(f'<div>{inline(x)}</div>' for x in c['agree'])
    appr = ''.join(f'<div>{inline(x)}</div>' for x in c['approve'])
    rows = ''.join(f'<tr><th>{inline(a)}</th><td>{inline(b)}</td></tr>' for a, b in c['rows'])
    return f'''<section class="cover">
  {brand.header_html('Дератизация, дезинсекция и пест-контроль для организаций · ХАССП')}
  <div class="signs">
    <div class="sg"><div class="sg-h">{c['agree_title']}</div>{agree}</div>
    <div class="sg"><div class="sg-h">{c['approve_title']}</div>{appr}</div>
  </div>
  <div class="cv-title">
    <div class="cv-badge">Образец документа<span>реквизиты условные</span></div>
    <div class="k">{inline(c['kicker'])}</div>
    <div class="t">{inline(c['title'])}</div>
    <div class="s">{inline(c['subtitle'])}</div>
    <div class="b">{inline(c['basis'])}</div>
  </div>
  <table class="cv-rows">{rows}</table>
  <div class="cv-note">{inline(c['sample_note'])}</div>
  <div class="cv-foot"><span>{inline(C.CITY + ' · 2026')}</span><span>{inline('Подготовлено: ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф · +7 (495) 104-35-70 · b2b@pestcontrol-center.ru')}</span></div>
</section>'''


def toc(pages):
    items = []
    for num, title in C.TOC:
        pg = pages.get(num, '')
        lab = f'Приложение {num[1:]}' if num.startswith('П') else num
        cls = 'ax' if num.startswith('П') else ''
        anchor = ('A' + num[1:]) if num.startswith('П') else num
        items.append(f'<li class="{cls}"><a href="#s{anchor}"><span class="tn">{lab}</span><span class="tt">{inline(title)}</span><span class="dots"></span><span class="tp">{pg}</span></a></li>')
    how = [
        'Значения, выделенные **синим**, — пример для хлебопекарного производства: замените их данными своего объекта.',
        'Периодичность исследований и критические пределы установите по результатам анализа опасностей и согласуйте с испытательной лабораторией.',
        'Для кафе, столовой или магазина замените разделы 2, 5 и 6 и ссылки в разделе 3 (СанПиН 2.3/2.4.4282-26, СП 2.3.6.4281-26).',
        'Раздел 11.3 «Дезинсекция и дератизация» и схему точек (приложение 1) заполнит исполнитель ДДД после обследования.',
    ]
    howh = ''.join(f'<li>{inline(x)}</li>' for x in how)
    return f'''<section class="toc"><h1 class="toc-h">Содержание</h1><ol class="toc-l">{"".join(items)}</ol>
<div class="how"><div class="how-h">Как пользоваться образцом</div><ul>{howh}</ul></div></section>'''


CSS = r'''
@page { size: A4; margin: 20mm 13mm 15mm 17mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: 'Inter', sans-serif; font-size: 8.5pt; line-height: 1.45; color: #18181b; font-feature-settings: 'cv11' 1, 'ss03' 1; }
.nw { white-space: nowrap; }
.v { color: #2a3ab0; }
b { font-weight: 700; }
p { margin: 0 0 5pt; }
.wm { position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-45deg); z-index: -1; pointer-events: none; }

/* обложка */
.cover { height: 261mm; display: flex; flex-direction: column; break-after: page; position: relative; }
''' + brand.header_css(1.0) + r'''
.cv-badge { display: inline-flex; align-items: baseline; gap: 2mm; font-size: 7pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; padding: 1mm 2.6mm; border-radius: 1mm; background: #fdc700; color: #09090b; margin-bottom: 4mm; }
.cv-badge span { font-weight: 600; letter-spacing: .02em; text-transform: none; font-size: 6.8pt; }
.signs { display: grid; grid-template-columns: 1fr 1fr; gap: 14mm; margin-top: 9mm; font-size: 8.4pt; line-height: 1.75; }
.sg:last-child { padding-left: 12mm; }
.sg-h { font-weight: 800; letter-spacing: .1em; font-size: 8.6pt; margin-bottom: 1mm; color: #09090b; }
.cv-title { margin-top: 19mm; }
.cv-title .k { font-size: 30pt; font-weight: 800; letter-spacing: .01em; line-height: 1.05; color: #09090b; text-transform: uppercase; }
.cv-title .t { font-size: 22pt; font-weight: 700; line-height: 1.1; color: #4f46e5; margin-top: 1mm; }
.cv-title .s { font-size: 10.4pt; line-height: 1.45; color: #27272a; margin-top: 5mm; max-width: 165mm; }
.cv-title .b { font-size: 8pt; color: #52525b; margin-top: 3mm; padding-left: 3mm; border-left: 2pt solid #615fff; }
.cv-rows { width: 100%; border-collapse: collapse; margin-top: 11mm; font-size: 8.3pt; }
.cv-rows th { width: 34mm; text-align: left; font-weight: 600; color: #52525b; padding: 2.2mm 3mm 2.2mm 0; border-top: .5pt solid #e4e4e7; vertical-align: top; }
.cv-rows td { padding: 2.2mm 0; border-top: .5pt solid #e4e4e7; }
.cv-rows tr:last-child th, .cv-rows tr:last-child td { border-bottom: .5pt solid #e4e4e7; }
.cv-note { margin-top: auto; font-size: 7.8pt; line-height: 1.5; background: #f5f5ff; border: .6pt solid #dcdcfb; border-radius: 3mm; padding: 3.4mm 4mm; color: #27272a; }
.cv-foot { display: flex; justify-content: space-between; margin-top: 5mm; padding-top: 3mm; border-top: .5pt solid #e4e4e7; font-size: 7pt; color: #71717a; }

/* оглавление */
.toc { break-after: page; }
.toc-h { font-size: 15pt; font-weight: 800; margin: 2mm 0 5mm; color: #09090b; }
.toc-l { list-style: none; margin: 0; padding: 0; font-size: 9pt; }
.toc-l li a { display: flex; align-items: baseline; gap: 2.4mm; color: inherit; text-decoration: none; padding: 1.55mm 0; }
.toc-l .tn { width: 9mm; font-weight: 700; color: #4f46e5; flex: none; }
.toc-l li.ax .tn { width: 23mm; font-weight: 600; color: #52525b; }
.toc-l li.ax { font-size: 8.4pt; }
.toc-l li.ax:first-of-type, .toc-l li:nth-child(15) { margin-top: 3mm; }
.toc-l .dots { flex: 1; border-bottom: .7pt dotted #a1a1aa; transform: translateY(-1mm); }
.toc-l .tp { width: 7mm; text-align: right; font-weight: 600; flex: none; }
.how { margin-top: 9mm; background: #f5f5ff; border-radius: 3mm; padding: 4mm 5mm; border: .6pt solid #dcdcfb; }
.how-h { font-weight: 800; font-size: 9pt; margin-bottom: 1.6mm; color: #1e1b4b; }
.how ul { margin: 0; padding-left: 4.4mm; font-size: 8.1pt; }
.how li { margin: 1mm 0; }

/* разделы */
h1.sec { display: flex; align-items: center; gap: 3mm; font-size: 12pt; font-weight: 800; color: #09090b; margin: 7mm 0 3mm; break-after: avoid; line-height: 1.2; }
h1.sec .no { flex: none; min-width: 7.6mm; height: 7.6mm; padding: 0 1.6mm; border-radius: 2mm; background: #4f46e5; color: #fff; font-size: 9.6pt; display: inline-flex; align-items: center; justify-content: center; }
h1.sec .sp { margin-left: auto; flex: none; font-size: 6.6pt; font-weight: 700; color: #4f46e5; background: #f0f0ff; border-radius: 1.6mm; padding: 1mm 2mm; letter-spacing: .02em; max-width: 62mm; text-align: right; line-height: 1.3; }
#s1 { margin-top: 0; }
h2 { font-size: 9.4pt; font-weight: 700; color: #1e1b4b; margin: 4.6mm 0 2mm; break-after: avoid; }
h2 .n2 { color: #4f46e5; }
.ul { margin: 0 0 5pt; padding-left: 4.4mm; }
.ul li { margin: 0 0 2.4pt; }
.note { border-left: 2.4pt solid #4f46e5; background: #f5f5ff; padding: 2.4mm 3.4mm; margin: 2mm 0 4mm; }

table.t { width: 100%; border-collapse: collapse; margin: 1.6mm 0 4.4mm; font-size: 7.5pt; line-height: 1.36; table-layout: fixed; }
table.t.sm { font-size: 7.1pt; }
table.t thead { display: table-header-group; }
table.t th { background: #eef0ff; color: #1e1b4b; font-weight: 700; text-align: left; vertical-align: bottom; padding: 1.5mm 1.8mm; border: .5pt solid #c9cbea; }
table.t td { padding: 1.35mm 1.8mm; border: .5pt solid #d9d9de; vertical-align: top; overflow-wrap: break-word; }
table.t td.cont { border-top-color: transparent; }
table.t td.cont span { color: #b4b4bb; font-size: 6.6pt; }
table.t tr { break-inside: avoid; }
table.t tr.grp td { background: #f4f4f5; font-weight: 700; color: #3f3f46; padding: 1.2mm 1.8mm; }
table.t.kv td:first-child { font-weight: 600; color: #3f3f46; background: #fafafa; }
table.t ul { margin: 0; padding-left: 3.4mm; }
table.t li { margin: 0 0 .6mm; }
table.t td div + div { margin-top: .8mm; }

.pest { border: .8pt solid #c7c9f5; border-radius: 3mm; padding: 3mm 4mm 1.4mm; margin: 2mm 0 5mm; background: linear-gradient(#f7f7ff, #fff 22mm); }
.pest-h { break-after: avoid; display: flex; justify-content: space-between; gap: 6mm; font-size: 6.8pt; color: #4f46e5; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 2.4mm; }
.pest-h span:last-child { text-transform: none; font-weight: 500; color: #71717a; letter-spacing: 0; text-align: right; }
.pi { display: flex; gap: 2.6mm; break-inside: avoid; }
.pi .pn { flex: none; width: 11mm; font-weight: 700; color: #4f46e5; }
.pi p { margin: 0 0 2.2mm; }

h2 + .pest { break-before: avoid; }
.ccps { display: grid; gap: 3mm; margin: 2mm 0 5mm; break-before: avoid; }
.ccp { border: .7pt solid #d4d4d8; border-radius: 2.4mm; break-inside: avoid; overflow: hidden; }
.ccp-h { display: flex; align-items: center; gap: 2.6mm; padding: 1.8mm 3mm; background: #fef2f2; border-bottom: .6pt solid #fecaca; font-size: 9pt; }
.ccp-h .hz { margin-left: auto; font-size: 6.8pt; font-weight: 700; color: #b91c1c; text-transform: uppercase; letter-spacing: .04em; }
.ccp-g { display: grid; grid-template-columns: 38mm 1fr; font-size: 7.8pt; line-height: 1.4; }
.ccp-g .l { padding: 1.4mm 3mm; color: #52525b; font-weight: 600; border-top: .5pt solid #ececf0; background: #fafafa; }
.ccp-g .r { padding: 1.4mm 3mm; border-top: .5pt solid #ececf0; }
.ccp-g .l:first-child, .ccp-g .l:first-child + .r { border-top: 0; }
.signs2 { margin-top: 5mm; display: grid; gap: 3.2mm; font-size: 7.9pt; break-inside: avoid; border-top: .5pt solid #e4e4e7; padding-top: 3.4mm; }
.s2 { display: grid; grid-template-columns: 33mm 1fr 47mm 35mm; gap: 2.4mm; align-items: end; line-height: 1.3; }
.s2-r { font-weight: 700; }
.s2-p { color: #3f3f46; }
.s2-d { color: #52525b; text-align: right; }

table.cal { font-size: 7pt; }
table.cal th.m, table.cal td.m { text-align: center; padding-left: 0; padding-right: 0; color: #4f46e5; font-weight: 700; }
table.cal td.m { font-size: 7.4pt; }

/* приложения */
.appx { break-before: page; }
.ax-k { font-size: 7.6pt; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: .08em; }
.ax-t { font-size: 12pt; font-weight: 800; margin: 1mm 0 4mm; color: #09090b; }
.planfig { margin: 0; }
.plan { display: block; width: 100%; height: auto; }
.zones { display: flex; flex-wrap: wrap; gap: 2mm 5mm; font-size: 7.2pt; color: #3f3f46; margin: 2mm 0 3mm; }
.zn i { display: inline-block; width: 3.4mm; height: 3.4mm; border: .5pt solid #71717a; vertical-align: -.6mm; margin-right: 1.4mm; }
.legend { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6mm 6mm; font-size: 7.2pt; }
.lg-i { display: flex; gap: 2mm; align-items: flex-start; }
.lg-i svg { width: 4.6mm; height: 4.6mm; flex: none; }
.planfig figcaption { font-size: 7pt; color: #71717a; margin-top: 3mm; }
.flow { display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; margin-top: 2mm; }
.fl-col { display: flex; flex-direction: column; align-items: stretch; }
.fl-h { font-weight: 800; font-size: 8.6pt; color: #1e1b4b; text-align: center; padding: 2mm; border-bottom: 1.2pt solid #615fff; margin-bottom: 3mm; }
.fl-b { position: relative; border: .7pt solid #a1a1aa; border-radius: 2mm; padding: 2mm 3mm; font-size: 7.8pt; text-align: center; background: #fff; min-height: 9mm; display: flex; align-items: center; justify-content: center; gap: 2mm; }
.fl-b.kkt { border: 1.1pt solid #dc2626; background: #fef2f2; font-weight: 600; }
.kb { display: inline-block; background: #dc2626; color: #fff; font-weight: 800; font-size: 6.8pt; border-radius: 1.6mm; padding: .6mm 1.6mm; white-space: nowrap; }
.fl-a { height: 4.6mm; position: relative; }
.fl-a::before { content: ''; position: absolute; left: 50%; top: 0; bottom: 1.2mm; border-left: .8pt solid #71717a; }
.fl-a::after { content: ''; position: absolute; left: calc(50% - 1.3mm); bottom: 0; border: 1.3mm solid transparent; border-top: 1.6mm solid #71717a; border-bottom: 0; }
.flow-notes { margin-top: 6mm; font-size: 7.6pt; color: #3f3f46; display: grid; gap: 2mm; }
.form .ftitle { font-weight: 800; font-size: 10pt; color: #09090b; margin-bottom: 1.6mm; }
.fmeta { font-size: 7.8pt; color: #3f3f46; }
table.frm { font-size: 7.2pt; }
table.frm th { vertical-align: middle; }
table.frm tr.blank td { height: 8.6mm; }
table.frm tr.ex td { color: #2a3ab0; font-style: italic; background: #fafaff; }
.fnote { font-size: 7pt; color: #71717a; }
.src { font-size: 7.8pt; padding-left: 5mm; }
.src li { margin: 0 0 2.4mm; }
.src li > span { display: block; font-weight: 600; }
.src a { color: #4f46e5; text-decoration: none; word-break: break-all; font-size: 7.2pt; }
'''


def header_template():
    """Верхний колонтитул страниц 2+: логотип и название слева, справа крупно телефон и сайт (как в журнале)."""
    ic = 'width:4.6mm;height:4.6mm;border-radius:50%;background:#615fff;display:inline-flex;align-items:center;justify-content:center;flex:none'
    svg = 'style="width:2.6mm;height:2.6mm;display:block"'
    return ('<div style="width:100%;margin:0 13mm 0 17mm;padding:0 0 1.5mm;font-family:Inter;line-height:1;'
            'display:flex;align-items:center;justify-content:space-between;border-bottom:.7pt solid #615fff;-webkit-print-color-adjust:exact;">'
            '<div style="display:flex;align-items:center;gap:1.8mm;">'
            + LOGO.replace('class="lg"', 'style="width:6mm;height:6mm"') +
            '<span style="font-weight:800;color:#09090b;font-size:8.4pt;letter-spacing:.01em">ПЕСТКОНТРОЛЬ</span>'
            '<span style="font-weight:700;color:#615fff;font-size:5.6pt;letter-spacing:.14em">ЦЕНТР</span></div>'
            '<div style="display:flex;align-items:center;gap:1.6mm;">'
            f'<i style="{ic}">' + brand.IC_PHONE.replace('<svg ', f'<svg {svg} ', 1) + '</i>'
            f'<b style="font-size:10pt;font-weight:750;color:#09090b;margin-right:3mm;white-space:nowrap">{brand.CO["phone"]}</b>'
            f'<i style="{ic}">' + brand.IC_GLOBE.replace('<svg ', f'<svg {svg} ', 1) + '</i>'
            f'<b style="font-size:9.6pt;font-weight:650;color:#615fff;white-space:nowrap">{brand.CO["site"]}</b></div></div>')


def footer_template():
    return ('<div style="width:100%;margin:0 13mm 0 17mm;font-family:Inter;font-size:6.2pt;color:#71717a;'
            'display:flex;justify-content:space-between;align-items:center;">'
            '<span>ПЕСТКОНТРОЛЬ Центр · образец программы производственного контроля для хлебопекарного и кондитерского производства · ' + C.REV + '</span>'
            '<span style="font-weight:600;color:#3f3f46">Стр. <span class="pageNumber"></span> из <span class="totalPages"></span></span></div>')


def build(out_dir, pages=None):
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = pages or {}
    wm = watermark_svg(ROOT / 'fonts', length_mm=brand.WM['length_mm'], color=brand.WM['color'], opacity=brand.WM['opacity'])
    body = cover() + toc(pages) + '<main>' + render_blocks(C.DOC) + render_blocks(C.APPX) + '</main>'
    doc = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Образец программы производственного контроля — ПЕСТКОНТРОЛЬ Центр</title>'
           f'<style>{CSS}</style></head><body>{wm}{body}</body></html>')
    (out_dir / 'ppk.html').write_text(doc, encoding='utf-8')
    (out_dir / 'templates.json').write_text(json.dumps({'header': header_template(), 'footer': footer_template()}, ensure_ascii=False), encoding='utf-8')
    # отдельные рисунки для DOCX
    for name, svg in (('plan', plan_block()), ('flow', flow_block())):
        (out_dir / f'{name}.html').write_text(
            f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS} body{{width:178mm;padding:4mm;}}</style></head><body><div id="fig">{svg}</div></body></html>',
            encoding='utf-8')
    return out_dir / 'ppk.html'


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ppk_sample'
    pg = json.loads(pathlib.Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {}
    print(build(out, pg))
