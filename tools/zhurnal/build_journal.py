#!/usr/bin/env python3
"""Журнал пест-контроля ПЕСТКОНТРОЛЬ Центр (форма ЖПК-01): один HTML для образца заполнения и шаблона.

python3 build_journal.py <fonts_dir> <out_dir>  ->  out_dir/journal.html

Образец и шаблон печатаются из одного и того же документа (render_journal.mjs):
- образец = journal.html как есть;
- шаблон  = тот же документ с <body class="tpl">: записи (.ink), подписи (.sg), пометки маркером (.mk-*)
  и отметка «Образец заполнения» (.only-s) скрыты через visibility:hidden, поэтому листы совпадают геометрически.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wm import watermark_svg  # noqa: E402

FONTS = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

NB = '\u00a0'
CO = {
    'brand': 'ПЕСТКОНТРОЛЬ Центр',
    'legal': 'ООО «Центр дезинфекционных услуг»',
    'inn': '7714462211', 'kpp': '771401001', 'ogrn': '1207700257775',
    'addr': f'123007, г.{NB}Москва, 2-й Хорошёвский проезд, д.{NB}7, к.{NB}1, помещ.{NB}1',
    'lic': f'№{NB}Л064-00111-77/01942445',
    'phone': '+7 (495) 104-35-70', 'mail': 'b2b@pestcontrol-center.ru', 'site': 'пестконтроль-центр.рф',
}
FORM = f'Форма ЖПК-01 · ред.{NB}11.2026'

LOGO = ('<svg class="lg" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#09090b"/>'
        '<g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round">'
        '<path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/>'
        '<circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/>'
        '<path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>')
IC_PHONE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
IC_GLOBE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>')

SIGS = {
    'smirnov': 'M2 14c3-9 6-11 7-6s-2 9 1 6 4-10 6-8-1 9 2 7 3-5 5-4 1 4 4 3 5-2 9-3',
    'orlov': 'M3 12c2-6 7-8 8-3s-5 7-3 6 6-9 8-7-2 6 1 6 4-4 6-4 2 3 5 2 6-3 8-3',
    'ivanova': 'M2 9c4 0 4 7 6 5s2-9 4-8 0 9 3 8 3-7 5-6 0 6 3 5 4-5 6-4 1 3 6 1',
    'kozlov': 'M2 13c3-7 5-9 6-5s-3 6 0 5 5-8 7-6-2 7 2 5 4-3 7-3 4 2 8 0',
    'petrova': 'M2 10c3-4 6-5 6-1s-4 5-1 4 4-6 7-5-1 6 2 4 5-4 7-3 2 3 7 1',
}


def sig(who, h=4.0):
    if not who:
        return ''
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


# ---------------------------------------------------------------- данные образца
J_NO = 'ПК-0917/26'
OBJ_SHORT = f'Хлебопекарный цех, г.{NB}о.{NB}Химки'  # без наименования юрлица заказчика
TITLE_FIELDS = [
    ('Объект (наименование)', 'Производство хлебобулочных изделий'),
    ('Адрес объекта', f'Московская обл., г.{NB}о. Химки, ул.{NB}Примерная, д.{NB}1, стр.{NB}2'),
    ('Заказчик', 'ООО «••••••••», ИНН 50••••••••'),
    ('Договор на пест-контроль (№, дата)', f'№{NB}0917-ПК/26 от 28.08.2026'),
    ('Ответственный от Заказчика (ФИО, должность, приказ)', f'Иванова Е.{NB}В., менеджер по качеству, приказ №{NB}41-П от 01.09.2026'),
    ('Ответственный специалист Исполнителя', f'Смирнов А.{NB}Н., инженер пест-менеджер'),
]
TOC = [('1', 'Паспорт объекта, порядок ведения, график визитов', '2'), ('2', 'Реестр точек пест-контроля (ТПК)', '3'),
       ('3', 'Перечень применяемых средств и материалов', '4'), ('4', 'Ведомость визитов и расхода средств', '5'),
       ('5', 'Поточечный лист осмотра ТПК', '6'), ('6', 'Учёт насекомых по видам и динамика', '7'),
       ('7', 'Замечания, предписания и корректирующие действия', '8'), ('8', 'Сигнальный лист персонала · инструктажи', '9'),
       ('9', 'Ежемесячная сводка · заверительная надпись', '10')]

PASSPORT = [
    ('Вид деятельности', 'Производство хлебобулочных и мучных кондитерских изделий', 1),
    ('Площадь здания / территории', '1 850 м² / 3 200 м²', 1),
    ('Режим работы', 'Круглосуточно, 3 смены; приёмка сырья 7:00–15:00', 1),
    ('Зоны (контуры защиты)', 'К1 — территория; К2 — периметр здания (ворота, доки, входы); К3 — склад сырья, цех, упаковка, бытовые помещения', 2),
    ('Целевые вредители', 'Мышь домовая, серая крыса; рыжий таракан; мухи; пищевые огнёвки', 1),
    ('Кратность визитов', f'2 раза в месяц (не реже, п.{NB}101 СанПиН 3.3686-21) + внеплановые по сигналу', 1),
    ('Метод', 'Мониторинг по ТПК; истребительные меры — только по показаниям', 1),
]
CONTACTS = [
    ('Ответственный Заказчика (ФИО, телефон)', f'Иванова Е.{NB}В., +7 (9••) •••-••-12'),
    ('Замещающее лицо', f'Козлов И.{NB}А., мастер смены, +7 (9••) •••-••-48'),
    ('Специалист Исполнителя', f'Смирнов А.{NB}Н., инженер пест-менеджер'),
]
SCHEDULE = [
    ('Сентябрь 2026', '02.09 · 16.09 · 30.09', '02.09 · 16.09 · 30.09 — по графику', 'ivanova'),
    ('Октябрь 2026', '14.10 · 28.10', f'14.10 · 28.10; внеплановый 21.10 (сигнал №{NB}2)', 'ivanova'),
    ('Ноябрь 2026', '11.11 · 25.11', '', None),
    ('Декабрь 2026', '09.12 · 23.12', '', None),
]

POINTS = [
    ('КИК-01', 'Станция с приманкой, запираемая', 'К1', 'Территория, северный забор у КПП', '25 %'),
    ('КИК-02', 'Станция с приманкой, запираемая', 'К1', 'Территория, северо-восточный угол забора', '25 %'),
    ('КИК-03', 'Станция с приманкой, запираемая', 'К1', 'Контейнерная площадка ТКО', '25 %'),
    ('КИК-04', 'Станция с приманкой, запираемая', 'К1', f'Рампа экспедиции, слева от дока №{NB}1', '25 %'),
    ('КИК-05', 'Станция с приманкой, запираемая', 'К1', 'Отмостка восточной стены здания', '25 %'),
    ('КИК-06', 'Станция с приманкой, запираемая', 'К1', 'Ворота приёмки склада сырья, снаружи', '25 %'),
    ('КИК-07', 'Станция с приманкой, запираемая', 'К1', 'Южная стена, у вентшахты', '25 %'),
    ('КИК-08', 'Станция с приманкой, запираемая', 'К1', 'Вход в АБК, справа', '25 %'),
    ('МЛ-01', 'Ловушка механическая / клеевая', 'К2', f'Экспедиция, док №{NB}1, справа от ворот', '0'),
    ('МЛ-02', 'Ловушка механическая / клеевая', 'К2', f'Экспедиция, док №{NB}1, слева от ворот', '0'),
    ('МЛ-03', 'Ловушка механическая / клеевая', 'К2', 'Экспедиция, вдоль северной стены', '0'),
    ('МЛ-04', 'Ловушка механическая / клеевая', 'К2', f'Экспедиция, у ворот №{NB}2', '0'),
    ('МЛ-05', 'Ловушка механическая / клеевая', 'К2', 'Склад сырья, ворота приёмки, справа', '0'),
    ('МЛ-06', 'Ловушка механическая / клеевая', 'К2', 'Склад сырья, ворота приёмки, слева', '0'),
    ('МЛ-07', 'Ловушка механическая / клеевая', 'К2', 'Коридор АБК у входа в цех', '0'),
    ('МЛ-08', 'Ловушка механическая / клеевая', 'К2', 'Электрощитовая', '0'),
    ('МЛ-09', 'Ловушка механическая / клеевая', 'К3', 'Склад сырья, стеллаж А-1', '0'),
    ('МЛ-10', 'Ловушка механическая / клеевая', 'К3', 'Склад сырья, стеллаж А-2', '0'),
    ('ИМ-01', 'Клеевой монитор насекомых', 'К3', 'Склад сырья, у просеивателя муки', '0'),
    ('ИМ-02', 'Клеевой монитор насекомых', 'К3', 'Цех, тестомесильное отделение', '0'),
    ('ИМ-03', 'Клеевой монитор насекомых', 'К3', 'Цех, моечное отделение, за ванной', '0'),
    ('ИМ-04', 'Клеевой монитор насекомых', 'К3', 'Цех, зона печей', '0'),
    ('ИМ-05', 'Клеевой монитор насекомых', 'К3', 'Упаковка, у стола фасовки', '0'),
    ('ИМ-06', 'Клеевой монитор насекомых', 'К3', 'Комната приёма пищи персонала', '0'),
    ('ИЛ-01', 'Световая УФ-ловушка', 'К3', 'Экспедиция, над входом из цеха', '20 / 14 сут'),
    ('ИЛ-02', 'Световая УФ-ловушка', 'К3', 'Цех, у входа из коридора', '10 / 14 сут'),
    ('ИЛ-03', 'Световая УФ-ловушка', 'К3', 'Упаковка', '5 / 14 сут'),
    ('ИЛ-04', 'Световая УФ-ловушка', 'К3', 'Склад сырья', '10 / 14 сут'),
    ('ФЛ-01', 'Феромонная (пищевые огнёвки)', 'К3', 'Склад муки, стеллаж Б-1', '2 / 14 сут'),
    ('ФЛ-02', 'Феромонная (пищевые огнёвки)', 'К3', 'Склад сухих ингредиентов', '2 / 14 сут'),
]
REG_CHANGES = [(f'21.10.2026', 'МЛ-10', 'Перенесена на 0,5 м к углу стеллажа А-2, ближе к вводу кабеля', 'да, ред. 2', 'orlov')]

AGENTS = [
    (f'Родентицидная приманка, парафинированный брикет 20{NB}г, с горьким веществом', f'бродифакум 0,005{NB}%', 'Только станции К1 (территория), запираемые и закреплённые. В помещениях с пищевой продукцией не применяется'),
    ('Клеевые пластины для грызунов (без действующего вещества)', '—', 'Механические и клеевые ловушки МЛ, контуры К2–К3'),
    ('Инсектицидный гель от тараканов', f'имидаклоприд 2,15{NB}%', 'Точечно в щели и полости по показаниям; не на поверхности, контактирующие с продукцией'),
    ('Клеевые мониторы для ползающих насекомых', '—', f'ИМ-01…06, замена не реже 1{NB}раза в месяц и при загрязнении'),
    ('Сменные клеевые экраны световых ловушек', '—', f'ИЛ-01…04, замена 1{NB}раз в месяц; лампы — 1{NB}раз в год'),
    ('Феромонные диспенсеры для пищевых огнёвок', 'феромон (аттрактант)', f'ФЛ-01…02, замена капсулы 1{NB}раз в 6–8{NB}недель'),
    ('Дезинфицирующее средство для мойки корпусов станций', 'ЧАС + амины', 'Мойка корпусов КИК и МЛ; рабочий раствор по инструкции'),
]
SGR_MASK = 'RU.77.99.••.•••.Е.••••••.••.••'

LOG = [
    ('02.09.2026', '09:30–12:40', 'Плановый, первичный', f'Обследование объекта. Установка и маркировка 30 ТПК по план-схеме (прил.{NB}1). Заправка КИК-01…08. Инструктаж персонала.',
     f'№1 — 320 г (8×40 г); №2 — 10 шт.; №4 — 6 шт.; №5 — 4 шт.; №6 — 2 шт.', '0917-01', 'smirnov'),
    ('16.09.2026', '10:00–11:35', 'Плановый', f'Осмотр 30 ТПК. КИК-03 — поедаемость 25 %, приманка заменена. ФЛ-01 — 2 огнёвки (пр.{NB}№{NB}3).',
     '№1 — 40 г', '0917-02', 'smirnov'),
    ('30.09.2026', '10:10–12:05', 'Плановый', f'Осмотр 30 ТПК. КИК-05 — 50 %, норы у отмостки (пр.{NB}№{NB}4). МЛ-04 — нет доступа (пр.{NB}№{NB}5). Замена экранов ИЛ и мониторов ИМ, мойка станций.',
     '№1 — 40 г; №4 — 6 шт.; №5 — 4 шт.; №7 — 0,5 л р-ра', '0917-03', 'smirnov'),
    ('14.10.2026', '09:40–12:20', 'Плановый + дезинсекция по показаниям', f'Осмотр 30 ТПК. ИМ-03 — рыжий таракан, 2 особи (сигнал №{NB}1). Точечная обработка моечной гелем: шов за ванной, кабель-канал, 12 м².',
     '№3 — 6 г; №1 — 40 г', '0917-04', 'smirnov'),
    ('21.10.2026', '08:50–10:10', f'Внеплановый (сигнал №{NB}2)', f'Осмотр склада сырья и ворот приёмки, 9 ТПК. МЛ-10 — мышь домовая, 1 особь. Негерметичный ввод кабеля в стене (пр.{NB}№{NB}7).',
     '№2 — 1 шт.', '0917-05', 'orlov'),
    ('28.10.2026', '10:00–11:50', 'Плановый, контроль эффективности', 'Осмотр 30 ТПК. ИМ-03 — 0: дезинсекция эффективна. МЛ-10 — 0. Замена экранов ИЛ и мониторов ИМ.',
     '№4 — 6 шт.; №5 — 4 шт.; №7 — 0,5 л р-ра', '0917-06', 'smirnov'),
]

VISITS = [('02.09', 'план'), ('16.09', 'план'), ('30.09', 'план'), ('14.10', 'план'), ('21.10', 'внепл.'), ('28.10', 'план'), ('', ''), ('', '')]
V5_SCOPE = {'КИК-06', 'МЛ-05', 'МЛ-06', 'МЛ-09', 'МЛ-10', 'ИМ-01', 'ИЛ-04', 'ФЛ-01', 'ФЛ-02'}
OVR = {
    1: {'КИК-03': 'П25/З', 'ИЛ-01': 'Н14', 'ИЛ-02': 'Н6', 'ИЛ-03': 'Н3', 'ИЛ-04': 'Н5', 'ФЛ-01': 'Н2'},
    2: {'КИК-03': 'П10', 'КИК-05': 'П50/З', 'МЛ-04': 'Д', 'ИЛ-01': 'Н11/З', 'ИЛ-02': 'Н4/З', 'ИЛ-03': 'Н2/З', 'ИЛ-04': 'Н3/З', 'ФЛ-01': 'Н1',
        **{f'ИМ-0{i}': '0/З' for i in range(1, 7)}},
    3: {'КИК-05': 'П20/З', 'ИМ-03': 'Н2', 'ИЛ-01': 'Н7', 'ИЛ-02': 'Н3', 'ИЛ-03': 'Н1', 'ИЛ-04': 'Н2'},
    4: {'МЛ-10': 'М1/З', 'ИЛ-04': 'Н1'},
    5: {'КИК-05': 'П5', 'ИЛ-01': 'Н4/З', 'ИЛ-02': 'Н2/З', 'ИЛ-03': '0/З', 'ИЛ-04': 'Н1/З', **{f'ИМ-0{i}': '0/З' for i in range(1, 7)}},
}
MARK = {(1, 'КИК-03'): 'mk-y', (2, 'КИК-05'): 'mk-r', (2, 'МЛ-04'): 'mk-y', (1, 'ФЛ-01'): 'mk-y', (3, 'ИМ-03'): 'mk-r', (4, 'МЛ-10'): 'mk-r'}
MX_NOTES = {'КИК-03': f'ТКО — пр.{NB}8', 'КИК-05': f'норы — пр.{NB}4', 'МЛ-04': f'доступ — пр.{NB}5',
            'МЛ-10': f'мышь — пр.{NB}7', 'ИМ-03': f'таракан — пр.{NB}6', 'ФЛ-01': f'огнёвка — пр.{NB}3'}
MX_PLACE = {'КИК-01': 'Сев. забор у КПП', 'КИК-02': 'Северо-восточный угол забора', 'КИК-03': 'Площадка ТКО', 'КИК-04': f'Рампа, слева от дока №{NB}1',
            'КИК-05': 'Отмостка восточной стены', 'КИК-06': 'Ворота приёмки сырья, снаружи', 'КИК-07': 'Южная стена, у вентшахты', 'КИК-08': 'Вход в АБК, справа',
            'МЛ-01': f'Док №{NB}1, справа от ворот', 'МЛ-02': f'Док №{NB}1, слева от ворот', 'МЛ-03': 'Экспедиция, северная стена', 'МЛ-04': f'Экспедиция, у ворот №{NB}2',
            'МЛ-05': 'Приёмка сырья, справа', 'МЛ-06': 'Приёмка сырья, слева', 'МЛ-07': 'Коридор АБК у входа в цех', 'МЛ-08': 'Электрощитовая',
            'МЛ-09': 'Склад сырья, стеллаж А-1', 'МЛ-10': 'Склад сырья, стеллаж А-2', 'ИМ-01': 'Склад сырья, у просеивателя', 'ИМ-02': 'Цех, тестомесильное отд.',
            'ИМ-03': 'Цех, моечная, за ванной', 'ИМ-04': 'Цех, зона печей', 'ИМ-05': 'Упаковка, стол фасовки', 'ИМ-06': 'Комната приёма пищи',
            'ИЛ-01': 'Экспедиция, вход из цеха', 'ИЛ-02': 'Цех, вход из коридора', 'ИЛ-03': 'Упаковка', 'ИЛ-04': 'Склад сырья',
            'ФЛ-01': 'Склад муки, стеллаж Б-1', 'ФЛ-02': 'Склад сухих ингредиентов'}


def mx_cell(vi, code):
    if vi == 0:
        return 'У'
    if vi >= 6:
        return ''
    if vi == 4 and code not in V5_SCOPE:
        return '—'
    return OVR.get(vi, {}).get(code, '0')


INSECTS = [
    ('16.09', 'ИЛ-01…04', 'Мухи комнатные — 22; плодовые мушки — 6', '28', 'норма', '', 'Плановая замена экранов 30.09'),
    ('16.09', 'ФЛ-01', 'Огнёвка южная амбарная, имаго — 2', '2', 'на пороге', 'mk-y', f'Пр.{NB}№{NB}3: уборка просыпей, проверка партий'),
    ('30.09', 'ИЛ-01…04', 'Мухи комнатные — 16; плодовые мушки — 4', '20', 'норма', '', 'Экраны заменены'),
    ('30.09', 'ФЛ-01', 'Огнёвка южная амбарная, имаго — 1', '1', 'норма', '', 'Контроль на следующем визите'),
    ('14.10', 'ИМ-03', 'Рыжий таракан (Blattella germanica), имаго — 2', '2', 'превышение', 'mk-r', f'Дезинсекция гелем, акт 0917-04; пр.{NB}№{NB}6'),
    ('14.10', 'ИЛ-01…04', 'Мухи комнатные — 10; плодовые мушки — 3', '13', 'норма', '', '—'),
    ('21.10', 'ИЛ-04', 'Муха комнатная — 1', '1', 'норма', '', '—'),
    ('28.10', 'ИЛ-01…04', 'Мухи комнатные — 6; плодовые мушки — 1', '7', 'норма', '', 'Экраны заменены'),
    ('28.10', 'ИМ-03', 'Не обнаружено (контроль через 14 сут)', '0', 'норма', '', 'Эффективность подтверждена'),
]
DYNAMICS = [
    ('02.09', '—', '—', '—', 'установка ТПК', 'исходный осмотр'),
    ('16.09', '28', '2', '0', f'КИК-03 — 25{NB}%', 'огнёвка на пороге'),
    ('30.09', '20', '1', '0', f'КИК-05 — 50{NB}%', 'грызуны на К1: рост'),
    ('14.10', '13', '0', '2 (ИМ-03)', f'КИК-05 — 20{NB}%', 'очаг тараканов в моечной'),
    ('21.10 внепл.', '1 (ИЛ-04)', '0', '0', 'МЛ-10 — мышь, 1', 'вход через ввод кабеля'),
    ('28.10', '7', '0', '0', f'КИК-05 — 5{NB}%', 'снижение по всем группам'),
]
CONCLUSION = (f'Отлов летающих насекомых снижается от визита к визиту (28 → 7) — сезонное снижение и замена уплотнителя ворот дока №{NB}1. '
              'Пищевые огнёвки после уборки просыпей не выявляются с 14.10. Очаг рыжего таракана в моечной ликвидирован: на контроле 28.10 — 0. '
              'Рекомендация: сохранить кратность 2 раза в месяц, ИМ-03 оставить в зоне особого внимания.')

ACTIONS = [
    ('02.09', 'МЛ-01', f'Док №{NB}1: износ нижнего уплотнителя ворот, зазор около 10{NB}мм', 'Заменить уплотнитель, до ремонта держать ПВХ-завесу закрытой', 'Гл. инженер, до 16.09', 'Выполнено 15.09', 'ivanova', '16.09'),
    ('02.09', 'ИЛ-04', 'Склад сырья: разрыв защитной сетки приточной решётки', 'Заменить сетку на приточной решётке', 'Гл. инженер, до 30.09', 'Выполнено 25.09', 'ivanova', '30.09'),
    ('16.09', 'ФЛ-01', 'Склад муки: просыпи под стеллажом Б-1, огнёвка в ловушке', 'Уборка просыпей, осмотр партий муки, соблюдение FIFO', 'Нач. склада, до 18.09', 'Выполнено 17.09', 'petrova', '30.09'),
    ('30.09', 'КИК-05', 'Территория: 2 норы у отмостки, строительный мусор', 'Засыпать и утрамбовать норы, вывезти мусор', 'АХО, до 07.10', 'Выполнено 06.10', 'ivanova', '14.10'),
    ('30.09', 'МЛ-04', 'Экспедиция: ловушка заставлена паллетами', 'Освободить доступ, сохранять проход вдоль стены', 'Нач. экспедиции, сразу', 'Выполнено 30.09', 'kozlov', '14.10'),
    ('14.10', 'ИМ-03', 'Моечная: отслоение герметика за ванной, влага, остатки теста', 'Санобработка за ванной, герметизация шва', 'Нач. цеха, до 21.10', 'Выполнено 20.10', 'kozlov', '28.10'),
    ('21.10', 'МЛ-10', f'Склад сырья: ввод кабеля в стене не загерметизирован, отверстие ~15{NB}мм', 'Заделать металлической сеткой и герметиком', 'Гл. инженер, до 28.10', 'Выполнено 27.10', 'ivanova', '28.10'),
    ('28.10', 'КИК-03', 'Площадка ТКО: крышки контейнеров не закрываются', 'Заменить контейнеры или крышки, держать закрытыми', 'АХО, до 11.11', 'В работе', None, ''),
]
SIGNALS = [
    ('13.10.2026 19:40', 'Цех, моечное отделение', 'Таракан у моечной ванны', f'Козлов И.{NB}А., мастер смены', 'kozlov', f'Ивановой Е.{NB}В. 14.10, 08:15', f'14.10, визит №{NB}4: ИМ-03 — Н2, обработка, пр.{NB}№{NB}6', 'smirnov'),
    ('20.10.2026 14:30', 'Склад сырья, стеллаж А-2', 'Помёт мыши на полу у поддона', f'Петрова О.{NB}С., кладовщик', 'petrova', f'Ивановой Е.{NB}В. 14:45; заявка Исполнителю 15:05', f'21.10, визит №{NB}5: МЛ-10 — М1, пр.{NB}№{NB}7', 'orlov'),
]
BRIEF = [('02.09.2026', f'Персонал склада, экспедиции и цеха, 14 чел. (прил.{NB}5)', 'Назначение ТПК; ловушки не перемещать; сигнальный лист', f'Смирнов А.{NB}Н.', 'smirnov')]
MONTHS = [
    ('Сентябрь 2026', '3 / 0', '90', 'К1: поедаемость в 2 осмотрах (КИК-03, КИК-05). К2–К3: 0', 'ИЛ — 48; ФЛ — 3 огнёвки; ИМ — 0', '5 / 3', 'Умеренный: норы у КИК-05, огнёвка на складе муки'),
    ('Октябрь 2026', '2 / 1', '69', 'К1: КИК-05 20 % → 5 %. К3: мышь в МЛ-10 (21.10), вход закрыт', 'ИЛ — 21; ИМ-03 — 2 таракана → 0; ФЛ — 0', '3 / 4', f'Снижается. Открыто пр.{NB}№{NB}8'),
]

# ---------------------------------------------------------------- CSS
CSS = r"""
@font-face{font-family:Inter;font-style:normal;font-weight:100 900;src:url(__F__/inter-ru-wght-normal.woff2) format("woff2");unicode-range:U+0020-007E,U+00A0,U+00A9,U+00AB,U+00AD,U+00B0,U+00B7,U+00BB,U+00D7,U+0401,U+0410-044F,U+0451,U+2009,U+2010-2015,U+2018-201E,U+2022,U+2026,U+202F,U+2116,U+20BD,U+2192,U+2212}
@font-face{font-family:Inter;font-style:normal;font-weight:100 900;src:url(__F__/inter-latin-wght-normal.woff2) format("woff2");unicode-range:U+0000-001F,U+007F-009F,U+00A1-00A8,U+00AA,U+00AC,U+00AE-00AF,U+00B1-00B6,U+00B8-00BA,U+00BC-00D6,U+00D8-00FF,U+2000-2008,U+200A-200F,U+2016-2017,U+201F-2021,U+2023-2025,U+2027-202E,U+2030-206F,U+2122,U+2191,U+2193}
@font-face{font-family:Inter;font-style:italic;font-weight:100 900;src:url(__F__/inter-ru-wght-italic.woff2) format("woff2");unicode-range:U+0020-007E,U+00A0,U+00A9,U+00AB,U+00AD,U+00B0,U+00B7,U+00BB,U+00D7,U+0401,U+0410-044F,U+0451,U+2009,U+2010-2015,U+2018-201E,U+2022,U+2026,U+202F,U+2116,U+20BD,U+2192,U+2212}
@font-face{font-family:Inter;font-style:italic;font-weight:100 900;src:url(__F__/inter-latin-wght-italic.woff2) format("woff2");unicode-range:U+0000-001F,U+007F-009F,U+00A1-00A8,U+00AA,U+00AC,U+00AE-00AF,U+00B1-00B6,U+00B8-00BA,U+00BC-00D6,U+00D8-00FF,U+2000-206F}
@page{size:A4 portrait;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:Inter,Arial,sans-serif;color:#18181b;font-size:8.4pt;line-height:1.35;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{width:210mm;height:297mm;padding:9mm 12mm 8mm 20mm;position:relative;overflow:hidden;break-after:page;page-break-after:always;display:flex;flex-direction:column;background:#fff}
.pg:last-child{break-after:auto;page-break-after:auto}
.wm{position:absolute;left:50%;top:54%;transform:translate(-50%,-50%) rotate(-45deg);z-index:0;pointer-events:none}
.pg>*:not(.wm){position:relative;z-index:1}
/* шапка: крупно телефон и сайт на каждом листе */
.hd{display:flex;align-items:center;justify-content:space-between;gap:6mm;padding-bottom:2.6mm;border-bottom:.7mm solid #615fff}
.brand{display:flex;align-items:center;gap:3mm;min-width:0}
.lg{width:12.5mm;height:12.5mm;flex:none}
.bn{font-weight:700;font-size:13.5pt;letter-spacing:-.015em;line-height:1;white-space:nowrap}
.bn small{font-weight:600;font-size:7pt;color:#615fff;letter-spacing:.16em;margin-left:1.6mm;vertical-align:.2em}
.bt{font-size:6.8pt;color:#71717a;margin-top:1.4mm;white-space:nowrap}
.hc{display:grid;grid-template-columns:auto auto;align-items:center;column-gap:2.4mm;row-gap:1.6mm}
.hc i{width:6.4mm;height:6.4mm;border-radius:50%;background:#615fff;display:grid;place-items:center}
.hc i svg{width:3.5mm;height:3.5mm}
.hc b{display:block;line-height:1;white-space:nowrap}
.hc .ph{font-size:17pt;font-weight:750;letter-spacing:-.01em;color:#09090b}
.hc .st{font-size:15.5pt;font-weight:650;letter-spacing:-.01em;color:#615fff}
.meta{display:flex;justify-content:space-between;align-items:flex-end;gap:4mm;margin-top:2.2mm;font-size:7pt;color:#52525b;white-space:nowrap}
.meta-l,.meta-r{display:flex;align-items:flex-end;gap:1.6mm}
.meta-r{align-items:center;gap:2.4mm}
.meta-r b{color:#18181b;font-weight:600}
.badge{display:inline-block;font-size:6.3pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:.8mm 2.2mm;border-radius:1mm;background:#fdc700;color:#09090b}
/* поля для записей */
.sl{display:inline-block;border-bottom:.2mm solid #71717a;height:4.5mm;line-height:4.3mm;padding:0 1mm;vertical-align:bottom;white-space:nowrap;overflow:hidden}
.ink{font-style:italic;color:#1d3fb8;font-weight:500}
.sg{display:inline-block;vertical-align:middle}
.fld{position:relative;display:block;line-height:5mm;font-size:7.8pt;overflow:hidden}
.fld .ul{position:absolute;left:0;right:0;height:0;border-top:.2mm solid #8a8a94}
.fld .ink{position:relative;display:block;padding:0 .6mm}
/* подвал */
.ft{margin-top:auto;padding-top:2mm;border-top:.25mm solid #d4d4d8;display:flex;justify-content:space-between;align-items:flex-end;gap:6mm;font-size:6pt;color:#71717a;line-height:1.45}
.ft b{color:#18181b;font-weight:600}
.pn{display:grid;grid-template-columns:auto auto;align-items:end;column-gap:1.4mm;row-gap:.8mm;font-size:8pt;font-weight:600;color:#18181b;white-space:nowrap;justify-items:end}
.pn .sl{text-align:center;font-size:9pt}
.pn .fm{grid-column:1 / -1;font-size:6pt;font-weight:400;color:#71717a}
/* разделы */
.sec{display:flex;align-items:baseline;gap:2.6mm;margin:3.8mm 0 1.4mm}
.sec .n{flex:none;font-size:7pt;font-weight:700;color:#fff;background:#615fff;border-radius:1mm;padding:.6mm 1.8mm;position:relative;top:-.3mm}
.sec h2{font-size:11.5pt;font-weight:700;letter-spacing:-.01em;margin:0;line-height:1.2}
.lead{font-size:7.2pt;color:#52525b;margin:0 0 2mm;line-height:1.4}
.note{font-size:6.6pt;color:#52525b;line-height:1.4;margin:1.6mm 0 0}
.note b{color:#18181b}
/* таблицы */
table.t{width:100%;border-collapse:collapse;table-layout:fixed}
.t th,.t td{border:.2mm solid #a1a1aa;padding:.8mm 1.2mm;vertical-align:top;text-align:left;font-size:6.9pt;line-height:1.28;overflow-wrap:anywhere}
.t th{background:rgba(97,95,255,.11);font-weight:600;font-size:6.5pt;color:#27272a;vertical-align:middle;line-height:1.2}
.t .c{text-align:center}
.t td.num{color:#52525b;text-align:center}
.t td .sg{margin-left:.6mm}
.mk-y{background:rgba(253,199,0,.40)}
.mk-r{background:rgba(255,92,92,.24)}
.box{border:.25mm solid #a1a1aa;border-radius:1.2mm;padding:2.6mm 3mm}
.box h3{font-size:7.3pt;text-transform:uppercase;letter-spacing:.08em;color:#615fff;margin:0 0 1.6mm;font-weight:700}
.kv{display:grid;grid-template-columns:38mm 1fr;column-gap:3mm;row-gap:1mm;align-items:end}
.kv>.k{font-size:7.1pt;color:#71717a;line-height:1.25;padding-bottom:.8mm}
.kv>.pr{font-size:7.6pt;padding-bottom:.8mm;line-height:1.35}
.rules{margin:0;padding-left:4.4mm;font-size:7.2pt;line-height:1.42}
.rules li{margin-bottom:.5mm}
/* подписи */
.sgb{font-size:7pt}
.sgb-t{font-weight:600;color:#27272a;margin-bottom:1mm}
.sgb-n{margin-bottom:1.4mm}
.sgb-r{display:grid;grid-template-columns:1fr 1fr;gap:4mm;align-items:start}
.sgc{display:flex;flex-direction:column;gap:.6mm;min-width:0}
.sgc .sl{width:100%;font-size:7.6pt}
.sgc em{font-style:normal;font-size:5.6pt;color:#8a8a94;text-align:center}
/* титульный лист */
.t-main{margin:11mm 0 6mm}
.t-top{display:flex;align-items:center;gap:3mm}
.t-kicker{font-size:8pt;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#615fff}
.t-form{margin-left:auto;font-size:7pt;color:#71717a}
.t-title{font-size:36pt;font-weight:800;letter-spacing:-.035em;line-height:1;margin:3.5mm 0 2.5mm}
.t-sub{font-size:12pt;color:#3f3f46;line-height:1.3}
.t-no{display:flex;align-items:center;gap:3mm;margin-top:5mm;font-size:11pt;font-weight:600}
.t-nobox{display:inline-block;width:52mm;height:10mm;line-height:9.4mm;border:.35mm solid #09090b;border-radius:1.2mm;padding:0 3.4mm;font-size:12.5pt;white-space:nowrap;overflow:hidden}
.t-fields{display:grid;grid-template-columns:52mm 1fr;column-gap:3mm;row-gap:2.6mm;align-items:end;margin-top:2mm}
.t-fields>.k{font-size:7.4pt;color:#71717a;padding-bottom:1mm;line-height:1.25}
.t-fields .fld{font-size:8.6pt;line-height:5mm}
.t-dates{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6mm;margin-top:8mm}
.t-dates>div{border:.3mm solid #09090b;border-radius:1.2mm;padding:2.2mm 3mm;height:15mm}
.t-dates>div>span{display:block;font-size:6.6pt;letter-spacing:.1em;text-transform:uppercase;color:#71717a;margin-bottom:1.6mm}
.t-dates .ink{font-size:11pt}
.t-exec{margin-top:8mm;display:grid;grid-template-columns:1.15fr 1fr;gap:5mm}
.exec p{margin:0;font-size:7.4pt;line-height:1.5}
.toc{list-style:none;margin:0;padding:0;font-size:7.3pt;line-height:1.25;display:grid;gap:.9mm}
.toc li{display:flex;align-items:flex-end;gap:1.4mm}
.toc li b{color:#615fff;width:4mm;flex:none}
.toc li .tt{flex:1}
.toc li em{font-style:normal;color:#71717a;white-space:nowrap}
.toc .sl{width:8mm;height:4mm;line-height:3.8mm;text-align:center}
.t-foot{margin-top:auto;font-size:6.7pt;color:#52525b;line-height:1.45;padding-top:2.6mm;border-top:.25mm solid #d4d4d8}
.pg.title .ft{margin-top:2.6mm}
/* поточечный лист */
.mx th,.mx td{font-size:6.4pt;padding:.4mm .9mm;line-height:1.12}
.mx td.v{text-align:center;font-weight:600}
.mx td.hv{padding:.4mm .8mm;vertical-align:top}
.mx td.hv small{display:block;font-size:5pt;color:#8a8a94;line-height:1;text-transform:uppercase;letter-spacing:.06em}
.mx td.hv .ink{display:block;text-align:center;font-size:6.6pt;line-height:1.15}
.mx tfoot td{font-weight:600;font-size:6.3pt;vertical-align:middle}
.legend{display:flex;flex-wrap:wrap;gap:1.2mm 3.6mm;font-size:6.4pt;color:#3f3f46;margin-top:1.8mm}
.legend span{white-space:nowrap}
.legend b{display:inline-block;min-width:5.4mm;text-align:center;border:.2mm solid #a1a1aa;border-radius:.8mm;margin-right:1mm;font-weight:700;color:#3f3dcc}
/* заверительная надпись */
.cert{margin-top:4mm;border:.35mm solid #09090b;border-radius:1.4mm;padding:3.6mm 4.4mm}
.cert h3{margin:0 0 2.4mm;font-size:8.6pt;text-transform:uppercase;letter-spacing:.1em}
.cert-t{font-size:8pt;line-height:1.6}
.cert-g{display:grid;grid-template-columns:1fr 1fr;gap:8mm;margin-top:4mm}
.stamp{display:inline-grid;place-items:center;width:26mm;height:26mm;border:.3mm dashed #a1a1aa;border-radius:50%;color:#a1a1aa;font-size:7pt;letter-spacing:.1em;margin-top:3mm}
.dyn td{vertical-align:middle}
/* шаблон: тот же лист без записей */
body.tpl .ink,body.tpl .sg,body.tpl .only-s{visibility:hidden}
body.tpl .mk-y,body.tpl .mk-r{background:transparent}
"""


def header():
    return f"""<header class="hd"><div class="brand">{LOGO}<div><div class="bn">ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>
<div class="bt">Пест-контроль для организаций · IPM / ХАССП</div></div></div>
<div class="hc"><i>{IC_PHONE}</i><b class="ph">{CO['phone']}</b><i>{IC_GLOBE}</i><b class="st">{CO['site']}</b></div></header>"""


def meta(section):
    return (f'<div class="meta"><div class="meta-l"><span>Журнал пест-контроля №</span>{sl(ink(J_NO), 24)}'
            f'<span>Объект</span>{sl(ink(OBJ_SHORT), 60)}</div>'
            f'<div class="meta-r"><span class="badge only-s">Образец заполнения</span><b>Раздел {section}</b></div></div>')


def footer(n):
    return (f'<div class="ft"><div><b>{CO["brand"]}</b> · {CO["legal"]} · ИНН {CO["inn"]} · КПП {CO["kpp"]} · ОГРН {CO["ogrn"]}<br>'
            f'Лицензия Роспотребнадзора <span style="white-space:nowrap">{CO["lic"]}</span> · {CO["addr"]}</div>'
            f'<div class="pn"><span class="fm">{FORM}</span><span>Лист №</span>{sl(ink(str(n)), 11)}</div></div>')


def sec(n, title, lead=''):
    s = f'<div class="sec"><span class="n">{n}</span><h2>{title}</h2></div>'
    return s + (f'<p class="lead">{lead}</p>' if lead else '')


def page(body, n, title=False):
    cls = 'pg title' if title else 'pg'
    return f'<section class="{cls}">{WM}{header()}{body}{footer(n)}</section>'


def table(cols, head, rows, rh, fill=False, num=False, cls='t'):
    colg = '<colgroup>' + ''.join(f'<col style="width:{w}mm">' if w else '<col>' for w in cols) + '</colgroup>'
    data = f' data-rh="{rh}"' + (' data-num="1"' if num else '')
    c = cls + (' fill' if fill else '')
    return f'<table class="{c}"{data}>{colg}<thead>{head}</thead><tbody>{rows}</tbody></table>'


def tr(cells, rh):
    out = ''
    for i, c in enumerate(cells):
        if isinstance(c, tuple):
            val, klass = c
        else:
            val, klass = c, ''
        st = f' style="height:{rh}mm"' if i == 0 else ''
        k = f' class="{klass}"' if klass else ''
        out += f'<td{k}{st}>{val}</td>'
    return f'<tr>{out}</tr>'


def sigblock(title, name, who, date):
    return (f'<div class="sgb"><div class="sgb-t">{title}</div>'
            f'<div class="sgb-n"><span class="sgc">{sl(ink(name), 0)}<em>должность, ФИО</em></span></div>'
            f'<div class="sgb-r"><span class="sgc">{sl(sig(who, 3.8), 0)}<em>подпись</em></span>'
            f'<span class="sgc">{sl(ink(date), 0)}<em>дата</em></span></div></div>')


# ---------------------------------------------------------------- листы

def p1():
    fields = ''.join(f'<span class="k">{k}</span>{fld(v)}' for k, v in TITLE_FIELDS)
    toc = ''.join(f'<li><b>{a}</b><span class="tt">{b}</span><em>лист</em>{sl(ink(c), 8)}</li>' for a, b, c in TOC)
    body = f"""<div class="t-main"><div class="t-top"><span class="t-kicker">Объектовый журнал · IPM / ХАССП</span><span class="badge only-s">Образец заполнения</span><span class="t-form">{FORM}</span></div>
<div class="t-title">ЖУРНАЛ<br>ПЕСТ-КОНТРОЛЯ</div>
<div class="t-sub">учёта мониторинга вредителей, дератизации и дезинсекции на объекте</div>
<div class="t-no"><span>Журнал №</span><span class="t-nobox">{ink(J_NO)}</span></div></div>
<div class="t-fields">{fields}</div>
<div class="t-dates"><div><span>Журнал начат</span>{ink('02.09.2026')}</div><div><span>Журнал окончен</span></div><div><span>Листов в журнале</span>{ink('10 (десять)')}</div></div>
<div class="t-exec"><div class="box exec"><h3>Исполнитель</h3>
<p><b>{CO['brand']}</b> — {CO['legal']}</p>
<p>ИНН {CO['inn']} · КПП {CO['kpp']} · ОГРН {CO['ogrn']}</p>
<p>{CO['addr']}</p>
<p>Лицензия на дезинфекционную деятельность (Роспотребнадзор) <span style="white-space:nowrap">{CO['lic']}</span></p>
<p>{CO['phone']} · {CO['mail']}</p>
<p>{CO['site']} · Пн–Пт 8:00–20:00 · срочные выезды 24/7</p></div>
<div class="box"><h3>Состав журнала</h3><ul class="toc">{toc}</ul></div></div>
<div class="t-foot">Журнал хранится на объекте у ответственного за пест-контроль и предъявляется при проверках Роспотребнадзора, аудитах ХАССП, ISO 22000 / FSSC 22000 и торговых сетей. Основание ведения: СанПиН 3.3686-21 (раздел III, пп.{NB}82, 98–124), МР 3.5.3.0374-25, ТР ТС 021/2011 (ст.{NB}10), ГОСТ Р 54762-2011 (раздел 12), программа пест-контроля объекта. Листы разделов 4–8 печатают в нужном количестве; при прошивке листы нумеруют, последняя страница — заверительная надпись.</div>"""
    return page(body, 1, title=True)


def p2():
    kv = ''.join(f'<span class="k">{k}</span>{fld(v, n)}' for k, v, n in PASSPORT)
    kv += f'<span class="k">Приложения к журналу</span><div class="pr">Прил.{NB}1 — план-схема ТПК; 2 — программа пест-контроля; 3 — договор; 4 — копии СГР и инструкций к средствам; 5 — листы инструктажа</div>'
    ct = ''.join(f'<span class="k">{k}</span>{fld(v)}' for k, v in CONTACTS)
    ct += f'<span class="k">Срочная заявка Исполнителю</span><div class="pr"><b>{CO["phone"]}</b> · Telegram t.me/Centr_Dezinfection · {CO["mail"]}</div>'
    rules = ''.join(f'<li>{r}</li>' for r in [
        'Записи вносит специалист Исполнителя в день визита, до ухода с объекта. Представитель Заказчика подтверждает визит подписью в разделах 4 и 5.',
        'Каждая ТПК записывается отдельно под своим номером с план-схемы. Пустые клетки не допускаются: при отсутствии находок ставится «0», при отсутствии доступа — «Д» с записью в раздел 7.',
        'Для каждого применённого средства указываются номер по перечню (раздел 3), место применения и расход. Родентициды в помещениях с открытой пищевой продукцией не применяются.',
        'Исправления: зачеркнуть одной линией, рядом — верная запись, дата, подпись. Подчистки, корректор и вклейка листов не допускаются.',
        'Персонал объекта записывает наблюдения вредителей между визитами в сигнальный лист (раздел 8) и сообщает ответственному.',
        'Ежемесячно специалист Исполнителя заполняет сводку (раздел 9) и передаёт отчёт с анализом тенденций службе качества.',
        'Заполненный журнал хранится на объекте вместе с актами и план-схемой; срок хранения устанавливается внутренним порядком Заказчика.'])
    rows = ''.join(tr([ink(m), ink(pd), ink(fd), (sig(s), 'c')], 7) for m, pd, fd, s in SCHEDULE)
    sched = table([28, 44, None, 30], '<tr><th>Месяц</th><th>Плановые даты</th><th>Фактические даты, отклонения</th><th class="c">Подпись Заказчика</th></tr>', rows, 7, fill=True)
    body = f"""{meta('1')}
{sec('1', 'Паспорт объекта', 'Заполняется при заведении журнала и обновляется при перепланировке, смене зон хранения или ответственных лиц.')}
<div class="box"><div class="kv">{kv}</div></div>
{sec('1.1', 'Контакты и порядок связи')}
<div class="box"><div class="kv">{ct}</div></div>
{sec('1.2', 'Порядок ведения журнала')}
<ol class="rules">{rules}</ol>
{sec('1.3', 'График плановых визитов')}
{sched}"""
    return page(body, 2)


def p3():
    rows = ''.join(tr([ink(c), ink(t), (ink(k), 'c'), ink(pl), (ink('02.09.26'), 'c'), (ink(th), 'c')], 5.2) for c, t, k, pl, th in POINTS)
    reg = table([15, 49, 13, None, 16, 20], '<tr><th>№ ТПК</th><th>Тип устройства</th><th class="c">Контур</th><th>Место установки (по план-схеме)</th><th class="c">Уста&shy;нов&shy;лена</th><th class="c">Порог</th></tr>', rows, 5.2)
    ch = ''.join(tr([ink(d), ink(c), ink(t), (ink(u), 'c'), (sig(s), 'c')], 7) for d, c, t, u, s in REG_CHANGES)
    chg = table([22, 16, None, 26, 24], '<tr><th>Дата</th><th>№ ТПК</th><th>Изменение (установлена, перенесена, снята) и причина</th><th class="c">План-схема обновлена</th><th class="c">Подпись</th></tr>', ch, 7, fill=True)
    body = f"""{meta('2')}
{sec('2', 'Реестр точек пест-контроля (ТПК)', 'Номера совпадают с план-схемой (прил. 1) и настенными указателями. Порог — уровень, при котором Исполнитель назначает корректирующие действия; устанавливается программой пест-контроля.')}
{reg}
<p class="note"><b>Типы:</b> КИК — станция контроля грызунов с приманкой; МЛ — механическая или клеевая ловушка; ИМ — клеевой монитор насекомых; ИЛ — световая ловушка; ФЛ — феромонная ловушка. <b>Контуры:</b> К1 — территория, К2 — периметр здания, К3 — внутренние помещения. <b>Порог:</b> для КИК — доля съеденной приманки, для ИЛ и ФЛ — особей за 14 суток.</p>
{sec('2.1', 'Изменения расстановки ТПК')}
{chg}"""
    return page(body, 3)


def p4():
    rows = ''.join(tr([(str(i), 'num'), ink(n), ink(dv), (ink(SGR_MASK if dv != '—' else f'декларация / сертификат (прил.{NB}4)'), ''), ink(u)], 12) for i, (n, dv, u) in enumerate(AGENTS, 1))
    rows += tr([(str(len(AGENTS) + 1), 'num'), '', '', '', ''], 12)
    ag = table([7, 47, 24, 39, None], '<tr><th class="c">№</th><th>Наименование, препаративная форма</th><th>Действующее вещество</th><th>СГР / декларация, срок годности</th><th>Где и как применяется, ограничения</th></tr>', rows, 12)
    chg = table([22, None, 40, 24, 24], '<tr><th>Дата</th><th>Что изменено (добавлено, исключено, замена партии)</th><th>Основание</th><th class="c">Исполнитель</th><th class="c">Заказчик</th></tr>', '', 9, fill=True)
    body = f"""{meta('3')}
{sec('3', 'Перечень применяемых средств и материалов', 'Согласуется с Заказчиком до начала работ. Средство вне перечня на объекте не применяется.')}
{ag}
<p class="note">Указывают торговое наименование, действующее вещество и концентрацию, полный номер свидетельства о государственной регистрации (СГР) по реестру ЕАЭС и срок годности партии. Копии свидетельств и инструкций хранятся в папке объекта (прил.{NB}4).</p>
{sec('3.1', 'Согласование перечня')}
<div class="grid2" style="display:grid;grid-template-columns:1fr 1fr;gap:6mm">{sigblock('Исполнитель', 'инженер пест-менеджер Смирнов А. Н.', 'smirnov', '02.09.2026')}{sigblock('Заказчик', 'менеджер по качеству Иванова Е. В.', 'ivanova', '02.09.2026')}</div>
{sec('3.2', 'Изменения перечня средств')}
{chg}"""
    return page(body, 4)


def p5():
    rows = ''.join(tr([ink(d), ink(t), ink(k), ink(w), ink(a), (ink(act), 'c'), (sig(who), 'c'), (sig('ivanova'), 'c')], 14.6) for d, t, k, w, a, act, who in LOG)
    tb = table([17, 12, 22, None, 30, 12.5, 17.5, 16], '<tr><th>Дата</th><th>Время</th><th>Вид визита</th><th>Выполненные работы, результаты</th><th>Средства (№ по разд. 3) и расход</th><th class="c">№ акта</th><th class="c">Специалист</th><th class="c">Заказчик</th></tr>', rows, 14.6, fill=True)
    body = f"""{meta('4')}
{sec('4', 'Ведомость визитов и расхода средств', 'Одна строка — один выезд. Номер акта выполненных работ совпадает с актом в бухгалтерии и ЭДО.')}
{tb}"""
    return page(body, 5)


def p6():
    hv1 = ''.join(f'<td class="hv"><small>дата</small>{ink(d)}</td>' for d, k in VISITS)
    hv2 = ''.join(f'<td class="hv"><small>вид</small>{ink(k)}</td>' for d, k in VISITS)
    head = (f'<tr><th rowspan="2">№ ТПК</th><th rowspan="2">Место установки</th>{hv1}<th rowspan="2">Примечание</th></tr>'
            f'<tr>{hv2}</tr>')
    rows = ''
    for code, typ, ct, place, thr in POINTS:
        cells = [ink(code), ink(MX_PLACE[code])]
        for vi in range(8):
            cells.append((ink(mx_cell(vi, code)), 'v ' + MARK.get((vi, code), '')))
        cells.append(ink(MX_NOTES.get(code, '')))
        rows += tr(cells, 5.5)
    s1 = ''.join(f'<td class="c">{sig(("orlov" if i == 4 else "smirnov") if i < 6 else None, 3.4)}</td>' for i in range(8))
    s2 = ''.join(f'<td class="c">{sig("ivanova" if i < 6 else None, 3.4)}</td>' for i in range(8))
    foot = (f'<tfoot><tr><td colspan="2" style="height:6.4mm">Подпись специалиста Исполнителя</td>{s1}<td></td></tr>'
            f'<tr><td colspan="2" style="height:6.4mm">Подпись представителя Заказчика</td>{s2}<td></td></tr></tfoot>')
    colg = '<colgroup><col style="width:14mm"><col style="width:45mm">' + '<col style="width:12mm">' * 8 + '<col></colgroup>'
    mx = f'<table class="t mx fill" data-rh="5.5">{colg}<thead>{head}</thead><tbody>{rows}</tbody>{foot}</table>'
    legend = ''.join(f'<span><b>{c}</b>{t}</span>' for c, t in [
        ('0', 'осмотрена, находок нет'), ('П%', 'поедаемость приманки, %'), ('М / К', 'отлов: мышь / крыса'), ('С', 'следы (помёт, погрызы)'),
        ('Н', 'насекомые, особей'), ('З', 'замена приманки / пластины'), ('Д', 'нет доступа → разд. 7'), ('Р', 'повреждена, заменена'),
        ('У', 'установлена'), ('—', 'вне объёма визита')])
    body = f"""{meta('5')}
{sec('5', 'Поточечный лист осмотра точек пест-контроля', 'Отметка ставится по каждой ТПК на каждом визите, через «/» — выполненное действие. Маркером выделяют: жёлтым — достигнут порог, красным — превышение порога или отлов внутри здания.')}
{mx}
<div class="legend">{legend}</div>"""
    return page(body, 6)


def p7():
    rows = ''.join(tr([ink(d), ink(t), ink(sp), (ink(n), 'c'), (ink(ev), 'c ' + mk), ink(act)], 8.2) for d, t, sp, n, ev, mk, act in INSECTS)
    tb = table([13, 17, None, 12, 20, 50], '<tr><th>Дата</th><th>ТПК</th><th>Вид (группа), стадия, число особей</th><th class="c">Всего</th><th class="c">Оценка к порогу</th><th>Принятые меры</th></tr>', rows, 8.2, fill=True)
    dr = ''.join(tr([ink(v), (ink(a), 'c'), (ink(b), 'c'), (ink(c), 'c'), ink(r), ink(t)], 5.8) for v, a, b, c, r, t in DYNAMICS)
    dr += tr(['', '', '', '', '', ''], 5.8) * 2
    dyn = table([22, 24, 24, 24, 36, None], '<tr><th>Визит</th><th class="c">ИЛ-01…04, особей</th><th class="c">ФЛ-01…02, особей</th><th class="c">ИМ-01…06, особей</th><th>Грызуны: поедаемость, отлов</th><th>Тенденция</th></tr>', dr, 5.8, cls='t dyn')
    body = f"""{meta('6')}
{sec('6', 'Учёт насекомых по видам и динамика', 'Расшифровка находок с клеевых мониторов, световых и феромонных ловушек. Вид определяет специалист Исполнителя (СанПиН 3.3686-21, п.\u00a099).')}
{tb}
{sec('6.1', 'Динамика по визитам')}
{dyn}
<div class="box" style="margin-top:3mm"><h3>Вывод специалиста по динамике</h3>{fld(CONCLUSION, 4)}<div style="margin-top:2mm">{sigblock('Специалист Исполнителя', 'инженер пест-менеджер Смирнов А. Н.', 'smirnov', '28.10.2026')}</div></div>"""
    return page(body, 7)


def p8():
    rows = ''
    for i, (d, tpk, found, rec, resp, done, who, chk) in enumerate(ACTIONS, 1):
        mk = 'mk-y' if done == 'В работе' else ''
        rows += tr([(str(i), 'num'), ink(d), ink(tpk), ink(found), ink(rec), ink(resp), (ink(done) + sig(who, 3.2), mk), (ink(chk) + (sig('smirnov', 3.2) if chk else ''), 'c')], 11.6)
    tb = table([7, 11, 14, None, 38, 23, 25, 18], '<tr><th class="c">№</th><th>Дата</th><th>ТПК / зона</th><th>Выявлено (причина риска)</th><th>Рекомендация Исполнителя</th><th>Ответственный, срок</th><th>Отметка Заказчика о выполнении</th><th class="c">Проверено Исполни&shy;телем</th></tr>', rows, 11.6, fill=True, num=True)
    body = f"""{meta('7')}
{sec('7', 'Замечания, предписания и корректирующие действия', 'Санитарно-технические причины находок: щели, уплотнители, сетки, просыпи, влага, захламлённость. Запись закрывается только после проверки Исполнителем на объекте.')}
{tb}"""
    return page(body, 8)


def p9():
    rows = ''
    for i, (dt, pl, what, who, s1, to, mark, s2) in enumerate(SIGNALS, 1):
        rows += tr([(str(i), 'num'), ink(dt), ink(pl), ink(what), ink(who) + sig(s1, 3.2), ink(to), ink(mark) + sig(s2, 3.2)], 13)
    for i in range(len(SIGNALS) + 1, 10):
        rows += tr([(str(i), 'num'), '', '', '', '', '', ''], 13)
    sg = table([7, 19, 24, None, 30, 28, 38], '<tr><th class="c">№</th><th>Дата, время</th><th>Место</th><th>Что обнаружено</th><th>Кто сообщил (ФИО, должность), подпись</th><th>Кому передано, когда</th><th>Отметка Исполнителя</th></tr>', rows, 13)
    br = ''.join(tr([ink(d), ink(w), ink(t), ink(by), (sig(s), 'c')], 9.5) for d, w, t, by, s in BRIEF)
    brt = table([20, None, 52, 28, 20], '<tr><th>Дата</th><th>Кто проинструктирован</th><th>Тема</th><th>Провёл</th><th class="c">Подпись</th></tr>', br, 9.5, fill=True)
    body = f"""{meta('8')}
{sec('8', 'Сигнальный лист персонала объекта', 'Заполняют сотрудники Заказчика, если между визитами увидели грызуна, насекомое или следы. Сразу сообщить ответственному; срочная заявка Исполнителю — ' + CO['phone'] + '.')}
{sg}
{sec('8.1', 'Инструктажи персонала по пест-контролю')}
{brt}"""
    return page(body, 9)


def p10():
    rows = ''.join(tr([ink(m[0]), (ink(m[1]), 'c'), (ink(m[2]), 'c'), ink(m[3]), ink(m[4]), (ink(m[5]), 'c'), ink(m[6])], 12) for m in MONTHS)
    tb = table([21, 15, 13, None, 38, 18, 30], '<tr><th>Месяц</th><th class="c">Визиты план / внепл.</th><th class="c">Осмот&shy;ров ТПК</th><th>Грызуны</th><th>Насекомые</th><th class="c">Предпи&shy;сания выдано / закрыто</th><th>Оценка риска, тенденция</th></tr>', rows, 12, fill=True)
    cert = f"""<div class="cert"><h3>Заверительная надпись</h3>
<div class="cert-t">В настоящем журнале пронумеровано, прошнуровано и скреплено печатью {sl(ink('10 (десять)'), 34)} листов.</div>
<div class="cert-g"><div>{sigblock('Исполнитель', 'инженер пест-менеджер Смирнов А. Н.', 'smirnov', '02.09.2026')}<span class="stamp">М. П.</span></div>
<div>{sigblock('Заказчик', 'менеджер по качеству Иванова Е. В.', 'ivanova', '02.09.2026')}<span class="stamp">М. П.</span></div></div></div>"""
    body = f"""{meta('9')}
{sec('9', 'Ежемесячная сводка и анализ тенденций', 'Заполняет Исполнитель по итогам месяца. Подробный отчёт с графиками по зонам передаётся службе качества и хранится вместе с журналом.')}
{tb}
{cert}
<p class="note" style="margin-top:3mm">Форма ЖПК-01 {CO['brand']} для объектов пищевой промышленности, общественного питания, торговли и хранения пищевой продукции. Форма не является утверждённой государственной: СанПиН 3.3686-21 не устанавливает единого бланка, но требует учёта численности вредителей, контроля эффективности и производственного контроля за дезинфекционными мероприятиями.</p>"""
    return page(body, 10)


WM = watermark_svg(FONTS, length_mm=232, color='#7c4dff', opacity=0.12)


def build():
    pages = [p1(), p2(), p3(), p4(), p5(), p6(), p7(), p8(), p9(), p10()]
    css = CSS.replace('__F__', FONTS.as_uri())
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Журнал пест-контроля — ПЕСТКОНТРОЛЬ Центр</title>'
            f'<style>{css}</style></head><body>{"".join(pages)}</body></html>')


(OUT / 'journal.html').write_text(build(), encoding='utf-8')
print('ok', OUT / 'journal.html')
