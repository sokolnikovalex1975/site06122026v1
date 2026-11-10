#!/usr/bin/env python3
"""Перелинковка отраслевых плиток (11.11.2026).

Применяется к файлам страниц, снятым с сайта (production), и к превью в корне репозитория:
    python3 patch-2026-11-11-indlinks.py <корень сайта>
Каждая замена обязана сработать ровно один раз, иначе скрипт останавливается.
Блок счётчиков, формы, шапка и подвал не затрагиваются.
"""
import sys, pathlib

ROOT = pathlib.Path(sys.argv[1])

CARD_CSS = ('<style id="ind-links">'
            '.ind .ind-more::after,.ind .ind-link::after{content:"";position:absolute;inset:0;z-index:3;transform:translateZ(1px)}'
            '.ind:has(.ind-more,.ind-link){cursor:pointer}'
            '.ind:hover .ind-more{color:var(--acc);border-color:var(--acc)}'
            '.ind:hover .ind-link{color:var(--acc)}'
            '.ind:has(.ind-more:focus-visible,.ind-link:focus-visible){outline:2px solid var(--acc);outline-offset:3px}'
            '.ind .ind-more:focus-visible,.ind .ind-link:focus-visible{outline:none}'
            '</style>\n</head>')

XLIST_CSS = ('<style id="ind-links">'
             '.ind-xlist{color:var(--t2);margin:24px 0 0;line-height:1.7;font-size:clamp(14px,.9vw,16px)}'
             '.ind-xlist a{color:var(--t1);border-bottom:1px solid var(--line2);transition:color .25s,border-color .25s}'
             '.ind-xlist a:hover,.ind-xlist a:focus-visible{color:var(--acc);border-color:var(--acc)}'
             '.d-card .ind-x{display:inline-block;margin-top:14px;color:var(--t1);font-weight:500;border-bottom:1px solid var(--line2);transition:color .25s,border-color .25s}'
             '.d-card .ind-x:hover,.d-card .ind-x:focus-visible{color:var(--acc);border-color:var(--acc)}'
             '</style>\n</head>')

HEAD = ('</head>', None)  # placeholder marker


def zhurnal_link(after_ul_of, href, label):
    return (after_ul_of, after_ul_of.replace('</ul></article>',
            '</ul><a class="ind-x" href="%s">%s →</a></article>' % (href, label)))


PATCHES = {
    'index.php': [
        ('</head>', CARD_CSS),
        ('</svg>Торговые сети</h3>', '</svg>Магазины и&nbsp;торговые сети</h3>'),
    ],
    'deratizatsiya/index.php': [
        ('</head>', CARD_CSS),
        ('<span class="tag">ISO 22000</span></div>',
         '<span class="tag">ISO 22000</span></div><a class="ind-more" href="../pishchevoe-proizvodstvo/">Пест-контроль пищевых производств<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'),
        ('<span class="tag">Доки и~рампы</span></div>',
         '<span class="tag">Доки и~рампы</span></div><a class="ind-more" href="../sklady-i-logistika/">Пест-контроль складов и~логистики<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'),
        ('<span class="tag">Сводный отчёт</span></div>',
         '<span class="tag">Сводный отчёт</span></div><a class="ind-more" href="../magaziny-i-torgovye-seti/">Пест-контроль магазинов и~сетей<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'),
        ('<span class="tag">СанПиН</span></div>',
         '<span class="tag">СанПиН</span></div><a class="ind-more" href="../restorany-i-kafe/">Пест-контроль ресторанов и~кафе<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'),
        ('<span class="tag">Чистые зоны</span></div>',
         '<span class="tag">Чистые зоны</span></div><a class="ind-more" href="../farmatsevticheskie-proizvodstva/">Пест-контроль фармпредприятий<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'),
    ],
    'dogovor-deratizatsiya-dezinsektsiya/index.php': [
        ('<a href="../#otrasli">Торговые сети', '<a href="../magaziny-i-torgovye-seti/">Торговые сети'),
    ],
    'magaziny-i-torgovye-seti/index.php': [
        ('<a href="../#otrasl-sklady">Распределительные центры сети',
         '<a href="../sklady-i-logistika/">Распределительные центры сети'),
    ],
    'materialy/zhurnal-pest-kontrolya/index.php': [
        ('</head>', XLIST_CSS),
        ('<li>Сигнальный лист для~поваров и~вечерней смены</li></ul></article>',
         '<li>Сигнальный лист для~поваров и~вечерней смены</li></ul><a class="ind-x" href="../../restorany-i-kafe/"><span class="nw">Пест-контроль</span> ресторанов и&nbsp;кафе →</a></article>'),
        ('<li>Отчёт по~форме торговой сети</li></ul></article>',
         '<li>Отчёт по~форме торговой сети</li></ul><a class="ind-x" href="../../magaziny-i-torgovye-seti/"><span class="nw">Пест-контроль</span> магазинов и&nbsp;сетей →</a></article>'),
        ('<li>Изменения расстановки после перепланировки</li></ul></article>',
         '<li>Изменения расстановки после перепланировки</li></ul><a class="ind-x" href="../../sklady-i-logistika/"><span class="nw">Пест-контроль</span> складов и&nbsp;логистики →</a></article>'),
        ('<li>Ежемесячная сводка для~службы качества</li></ul></article>',
         '<li>Ежемесячная сводка для~службы качества</li></ul><a class="ind-x" href="../../pishchevoe-proizvodstvo/"><span class="nw">Пест-контроль</span> пищевых производств →</a></article>'),
    ],
    'razrabotka-ppk/index.php': [
        ('</head>', XLIST_CSS),
        ('требует указать ответственных, факторы и~точки измерений с~периодичностью (пп.~10~и~13).</p>\n',
         'требует указать ответственных, факторы и~точки измерений с~периодичностью (пп.~10~и~13).</p>\n'
         '    <p class="ind-xlist" data-fade>Раздел о&nbsp;дезинсекции и&nbsp;дератизации в&nbsp;ППК выполняем сами по&nbsp;договору — '
         '<span class="nw">пест-контроль</span> по&nbsp;отраслям: '
         '<a href="../restorany-i-kafe/">рестораны и&nbsp;кафе</a>, '
         '<a href="../magaziny-i-torgovye-seti/">магазины и&nbsp;торговые сети</a>, '
         '<a href="../pishchevoe-proizvodstvo/">пищевые производства</a>, '
         '<a href="../sklady-i-logistika/">склады и&nbsp;логистика</a>, '
         '<a href="../gostinitsy/">гостиницы</a>, '
         '<a href="../farmatsevticheskie-proizvodstva/">фармацевтические производства</a>.</p>\n'),
    ],
    'ochistka-dezinfektsiya-ventilyatsii/index.php': [
        ('акт для~пожарной проверки и~управляющей компании.</p></article>',
         'акт для~пожарной проверки и~управляющей компании. <a href="../restorany-i-kafe/"><span class="nw">Пест-контроль</span> ресторанов</a></p></article>'),
        ('вытяжки фуд-кортов~— по~участкам, в~ночные окна.</p></article>',
         'вытяжки фуд-кортов~— по~участкам, в~ночные окна. <a href="../magaziny-i-torgovye-seti/"><span class="nw">Пест-контроль</span> магазинов</a></p></article>'),
        ('дезинфекция, смывы, работы по~этажам.</p></article>',
         'дезинфекция, смывы, работы по~этажам. <a href="../gostinitsy/"><span class="nw">Пест-контроль</span> гостиниц</a></p></article>'),
        ('горючей пыли с~актом по~п.~43~ППР.</p></article>',
         'горючей пыли с~актом по~п.~43~ППР. <a href="../sklady-i-logistika/"><span class="nw">Пест-контроль</span> складов</a></p></article>'),
    ],
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php': [
        ('</head>', XLIST_CSS),
        ('<span class="pm-link-more">Смотреть состав папки →</span>\n      </a>\n    </div>\n',
         '<span class="pm-link-more">Смотреть состав папки →</span>\n      </a>\n    </div>\n'
         '    <p class="ind-xlist" data-fade><span class="nw">Пест-менеджмент</span> на&nbsp;других объектах: '
         '<a href="../../restorany-i-kafe/">рестораны и&nbsp;кафе</a>, '
         '<a href="../../magaziny-i-torgovye-seti/">магазины и&nbsp;торговые сети</a>, '
         '<a href="../../sklady-i-logistika/">склады и&nbsp;логистика</a>, '
         '<a href="../../farmatsevticheskie-proizvodstva/">фармацевтические производства</a>, '
         '<a href="../../gostinitsy/">гостиницы</a>.</p>\n'),
    ],
    'dezinsektsiya/index.php': [
        ('<h3><a href="../farmatsevticheskie-proizvodstva/">Фармацевтические объекты и&nbsp;БЦ</a></h3>',
         '<h3><a href="../farmatsevticheskie-proizvodstva/">Фармацевтические объекты</a> и&nbsp;БЦ</h3>'),
    ],
}

COUNTERS_START = '<!-- Yandex.Metrika counter + UIS + Radist'
COUNTERS_END = '<!-- /Yandex.Metrika counter -->'


def counters(s):
    a = s.find(COUNTERS_START)
    b = s.find(COUNTERS_END, a)
    return s[a:b] if a >= 0 and b > a else None


bad = 0
for rel, reps in PATCHES.items():
    p = ROOT / rel
    if not p.exists() and (ROOT / rel.replace('index.php', 'index.html')).exists():
        p = ROOT / rel.replace('index.php', 'index.html')  # превью в репозитории
    if not p.exists():
        print('SKIP (нет файла)', rel); continue
    s = p.read_text(encoding='utf-8')
    if 'id="ind-links"' in s or all(new.replace('~', '\u00a0') in s for old, new in reps if old != '</head>'):
        print('ALREADY', rel); continue
    before = counters(s)
    for old, new in reps:
        old, new = old.replace('~', '\u00a0'), new.replace('~', '\u00a0')
        n = s.count(old)
        if n != 1:
            print('ERROR', rel, 'вхождений', n, ':', old[:70]); bad = 1; break
        s = s.replace(old, new)
    else:
        if counters(s) != before:
            print('ERROR', rel, 'блок счётчиков изменился'); bad = 1; continue
        p.write_text(s, encoding='utf-8')
        print('OK', rel, len(reps), 'правок')
sys.exit(bad)
