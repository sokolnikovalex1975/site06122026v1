#!/usr/bin/env python3
"""Сборка страниц «услуга + сфера» для общепита (11.11.2026):

  dezinsektsiya/restorany-i-kafe/index.html  — «Дезинсекция кафе, ресторанов и столовых»
  deratizatsiya/restorany-i-kafe/index.html  — «Дератизация ресторанов и кафе»

    python3 tools/restorany-uslugi/build_pages.py   # build_site.py запускает его сам
    python3 tools/site/build_site.py

Тексты — черновики, утверждённые владельцем 11.11.2026 (файлы проекта: «Страница Дезинсекция кафе и ресторанов/
Черновик контента v1.md» и «Страница Дератизация ресторанов и кафе/Черновик контента v1.md»). Ответы владельца:
H1 со столовыми; контрольный визит в цене разовой дезинсекции не упоминаем; разовая дератизация — один выезд;
в договоре — «визиты по графику» (без «2 раз в месяц»); выезд без договора — 4 часа; мелкие ходы заделываем сами,
капитальную заделку делает техслужба; договор с УК на общие зоны предлагаем; контрольно-учётную карту по
МР 3.5.3.0374-25 ведём. Цены по площади — предложение по медиане рынка (SEO/Цены по площади — рынок 2026-11-11.md),
нижняя граница — наш минимум 3 500 ₽; до утверждения владельцем страница остаётся только в превью.

Шаблон — pishchevoe-proizvodstvo/index.html (шапка, меню, подвал, плавающие кнопки, анимации), как у страниц
«Лабораторных исследований»; страницы на втором уровне — пути шаблона '../' меняются на '../../' (deeper()).
В main-файлах корень сайта — метка '@/'.

Форма: send.php принимает только name, company, phone, email, type и msg. Тип «Ресторан или кафе» выбран заранее,
формат заведения, «Что беспокоит», адрес и страница уходят в msg (скрипт страницы) — как на /restorany-i-kafe/.
Цель Метрики (113675622) — «audit» после отправки заявки, как на всех страницах (app.js).
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(HERE))
from textlib import typeset, plain, cut  # noqa: E402
import blocks  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
DATE = '2026-11-11'
LIC = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
FORMATS = ('Ресторан', 'Кафе или кофейня', 'Бар', 'Столовая или пищеблок', 'Кафе в ТЦ или на фуд-корте', 'Сеть заведений', 'Другое')
TYPES = ('Пищевое производство', 'Магазин или торговая сеть', 'Ресторан или кафе', 'Склад, логистика',
         'Фармацевтическое производство', 'Гостиница', 'Другое')

# ---------------------------------------------------------------- цены по площади (предложение владельцу, 11.11.2026)
# Указание владельца: «не по средней цене по Москве … нижний сегмент взять, и середину этого нижнего сегмента».
# Нижний сегмент — цены 11 прайсов не выше медианы; берём его медиану, округляем до 500 ₽ (половина — вниз),
# нижняя граница — наш минимум 3 500 ₽. Расчёт и источники — файлы проекта, «SEO/Цены по площади — рынок 2026-11-11.md».
AREAS = ('до 100 м²', '100–200 м²', '200–300 м²', '300–500 м²', '500–1000 м²')
AREA_PRICES = {
    'dzr': [(3500, 3500), (3500, 3500), (6000, 4500), (8500, 7000), (10500, 8000)],
    'drr': [(3500, 3500), (4000, 3500), (6000, 3500), (7000, 4500), (9000, 8000)],
}

PAGES = {
    'dzr': dict(
        slug='dezinsektsiya/restorany-i-kafe/', main='dezinsektsiya.html', hero='dzr', og='dzr-og',
        title='Дезинсекция кафе, ресторанов и столовых в Москве и МО — ПЕСТКОНТРОЛЬ Центр',
        og_title='Дезинсекция кафе, ресторанов и столовых — от 3 500 ₽',
        desc=('Дезинсекция общепита по СанПиН: тараканы, мухи, дрозофилы. Гели без закрытия кухни или ночная '
              'обработка без наценки, акт и журнал. От 3 500 ₽.'),
        name='Дезинсекция кафе, ресторанов и столовых', service_type='Дезинсекция',
        alt_names=['Дезинсекция общепита', 'Дезинсекция предприятий общественного питания', 'Дезинсекция ресторана',
                   'Дезинсекция кафе', 'Дезинсекция столовой', 'Уничтожение тараканов в кафе и ресторане'],
        crumbs=[('Главная', ''), ('Дезинсекция', 'dezinsektsiya/'), ('Кафе, рестораны и столовые', 'dezinsektsiya/restorany-i-kafe/')],
        hero_alt=('Ночью на кухне ресторана после закрытия специалист в тёмно-синей форме и синих перчатках наносит гель '
                  'в щель у пароконвектомата и подсвечивает её фонариком'),
        page_name='Дезинсекция кафе, ресторанов и столовых',
        offers=[('Разовая дезинсекция кафе или ресторана', 3500, None), ('Дезинсекция по договору', 3500, 'MON'),
                ('Дезинсекция и дератизация по одному договору', 4900, 'MON')],
        faq_h2='Вопросы о <em>дезинсекции общепита</em>', area_h='Дезинсекция по площади заведения',
        tasks=('Тараканы', 'Мухи, дрозофилы или мошки', 'Муравьи', 'Моль или жуки на складе', 'Нужен договор и журнал к проверке'),
        form_h='Заявка на бесплатное обследование',
        faq=[
            ('Как часто нужно проводить дезинсекцию в общепите?',
             'Норма задаёт обследования: на объектах общественного питания — не реже 2 раз в месяц (пп. 98 и 101 '
             'СанПиН 3.3686-21). Обработку проводят, когда обследование нашло насекомых. По договору кратность визитов '
             'закрепляем в графике, а по сигналу приезжаем внепланово.'),
            ('Сколько обработок нужно, чтобы вывести тараканов из ресторана?',
             'Одной обработки обычно мало: через 10–14 дней из яиц выходит молодняк, поэтому нужна повторная проверка, '
             'а при необходимости — повторная обработка. Если тараканов много или они приходят от соседей, нужен '
             'регулярный контроль по договору: по журналу видно, когда находки прекратились.'),
            ('Через сколько можно готовить после обработки?',
             'После гелей — сразу. После распыления — когда пройдут проветривание и влажная уборка по инструкции к '
             'средству. Время называем заранее, когда согласуем окно.'),
            ('Почему после обработки тараканов стало больше?',
             'В первые дни средство выгоняет их из укрытий, поэтому они чаще попадаются на глаза. Если через 10–14 дней '
             'живые тараканы остаются, повторяем обработку средством из другой химической группы (п. 99 СанПиН 3.3686-21).'),
            ('Безопасна ли дезинсекция для гостей и персонала?',
             'Применяем только средства с государственной регистрацией и по инструкции. Гель наносим точками в '
             'недоступных местах. Распыляемые средства — только когда в заведении нет людей, продукция при этом убрана.'),
            ('Можно провести дезинсекцию кафе срочно, этой же ночью?',
             'Да. Срочные выезды — круглосуточно, ночью и в выходные — без наценки. До приезда уберите продукты и посуду '
             'по <a href="#podgotovka">списку подготовки кухни</a>. Утром кафе открывается в обычное время, если не '
             'понадобилось распыление. Если понадобилось — время называем заранее по инструкции к средству.'),
            ('Обрабатываете кофемашины, посудомоечные машины и ледогенераторы?',
             'Да, это частые укрытия рыжих тараканов: там тепло и есть вода. Гель наносим в полости корпуса и моторные '
             'отсеки, мест контакта с продуктами и водой не касаемся. Если для доступа нужно снять панели, это делает '
             'ваша техслужба или сервисная компания оборудования.'),
            ('Работаете со столовыми и пищеблоками?',
             'Да — со столовыми предприятий и бизнес-центров, пищеблоками и фабриками-кухнями. Обработку назначаем на '
             'санитарный день или после последней смены, чтобы не останавливать линию раздачи. Документы оформляем на '
             'организацию, которая заключает договор: владельца столовой или оператора питания.'),
            ('Работаете с кафе в торговых центрах и на фуд-кортах?',
             'Да. Работаем в часы, которые разрешает управляющая компания центра, — обычно до открытия или после '
             'закрытия. Если тараканы приходят по общим коммуникациям, пишем об этом в акте: общие зоны обычно '
             'обслуживает управляющая компания, и одной обработки своего кафе тогда мало. Общие зоны центра можно передать нам по '
             'договору с управляющей компанией — <a href="@/biznes-tsentry-torgovye-tsentry-predpriyatiya/">пест-контроль бизнес-центров и ТЦ</a>.'),
            ('Чем дезинсекция отличается от пест-контроля?',
             'Дезинсекция — работа с насекомыми: обследование, обработка и контроль результата. Пест-контроль — система '
             'по договору против насекомых и грызунов: точки контроля, график визитов, журнал и документы для проверок. '
             'Подробно — на странице <a href="@/restorany-i-kafe/">«Пест-контроль ресторанов и кафе»</a>.'),
        ],
    ),
    'drr': dict(
        slug='deratizatsiya/restorany-i-kafe/', main='deratizatsiya.html', hero='drr', og='drr-og',
        title='Дератизация ресторанов, кафе и общепита в Москве и МО — ПЕСТКОНТРОЛЬ Центр',
        og_title='Дератизация ресторанов и кафе — от 3 500 ₽/мес',
        desc=('Дератизация общепита по СанПиН: мыши и крысы на кухне, складе, в подвале. У продуктов — ловушки без яда, '
              'снаружи — станции на ключ, журнал. От 3 500 ₽/мес.'),
        name='Дератизация ресторанов и кафе', service_type='Дератизация',
        alt_names=['Дератизация общепита', 'Дератизация предприятий общественного питания', 'Дератизация кафе',
                   'Дератизация ресторана', 'Уничтожение мышей и крыс в ресторане'],
        crumbs=[('Главная', ''), ('Дератизация', 'deratizatsiya/'), ('Рестораны и кафе', 'deratizatsiya/restorany-i-kafe/')],
        hero_alt=('На складе сухих продуктов ресторана специалист в тёмно-синей форме присел у стеллажа с мешками и с '
                  'фонариком проверяет чёрную пронумерованную ловушку для грызунов у стены'),
        page_name='Дератизация ресторанов и кафе',
        offers=[('Дератизация ресторана или кафе по договору', 3500, 'MON'), ('Разовая дератизация', 3500, None),
                ('Дератизация и дезинсекция по одному договору', 4900, 'MON')],
        faq_h2='Вопросы о <em>дератизации ресторанов и кафе</em>', area_h='Дератизация по площади заведения',
        tasks=('Мыши', 'Крысы', 'Следы: помёт, погрызы, запах', 'Нужен договор и журнал к проверке', 'Предписание Роспотребнадзора'),
        form_h='Заявка на бесплатное обследование',
        faq=[
            ('Опасна ли мышь в ресторане?',
             'Да. Мыши переносят возбудителей инфекций, портят продукты и упаковку, грызут кабели. Для заведения это ещё и '
             'нарушение санитарных правил: в помещениях общепита грызунов быть не должно (п. 26 СанПиН 2.3/2.4.4282-26), '
             'а на проверке это оценивают по следам — помёту и погрызам.'),
            ('Нужна ли дератизация, если мышей и крыс в ресторане нет?',
             'Да. Общепит — объект особого эпидемиологического значения: заселённость грызунами оценивают каждый месяц и '
             'по её результатам проводят дератизацию (пп. 98 и 110 СанПиН 3.3686-21). Когда грызунов нет, это контроль '
             'точек и защита здания, а не раскладка яда.'),
            ('Работаете со столовыми и пищеблоками?',
             'Да — со столовыми предприятий и бизнес-центров, пищеблоками и фабриками-кухнями. Точки проверяем до начала '
             'смены или в санитарный день, чтобы не мешать раздаче. Документы оформляем на организацию, которая заключает '
             'договор: владельца столовой или оператора питания.'),
            ('Как быстро уйдут мыши?',
             'Зависит от того, откуда они заходят и закрыты ли эти пути. Ловушки начинают работать сразу после установки. '
             'Но пока открыты щели и вводы коммуникаций, на место пойманных придут новые. Поэтому вместе с отловом '
             'передаём техслужбе список работ и проверяем его выполнение.'),
            ('Можно ли использовать продукты, которые погрызли мыши?',
             'В ресторане — нет. Продукцию с погрызами, помётом или другими следами грызунов в работу не берут: её убирают '
             'отдельно, а решение о списании принимает ответственный за производственный контроль по правилам заведения.'),
            ('Кто заделывает щели и вводы коммуникаций?',
             'Ходы и небольшие отверстия закрываем сами во время визита. Капитальную заделку — металлом, раствором, '
             'сетками, а также доводчики и уплотнители — делает ваша техслужба или управляющая компания по нашему списку '
             'с фото (п. 111 СанПиН 3.3686-21).'),
            ('Помогают ли ультразвуковые отпугиватели?',
             'Мы на них не рассчитываем. Если рядом еда и укрытие, грызуны часто привыкают к прибору. А на проверке '
             'смотрят не на прибор, а на результат: журнал, акты и отсутствие следов.'),
            ('Ресторан в торговом центре: кто отвечает за дератизацию?',
             'За свои помещения — кухню, склад, бар и зал — отвечает заведение (п. 88 СанПиН 3.3686-21). Общие зоны — '
             'технические этажи, шахты, мусорную камеру — обычно обслуживает управляющая компания центра. Если грызуны '
             'идут оттуда, пишем это в акте и согласуем с ней работы.'),
            ('Запах есть, а грызуна не видно — что делать?',
             'Скорее всего, зверёк погиб в полости — под оборудованием, в стене или над потолком. Позвоните нам: найдём и '
             'извлечём его, обеззаразим место и уберём запах. Если для доступа нужно вскрыть панель или потолок, это '
             'делает ваша техслужба.'),
        ],
    ),
}


def deeper(s):
    """Относительные пути шаблона ('../') для страницы на уровень глубже."""
    return re.sub(r'(?<=["\'(,\s])\.\./', '../../', s)


def rub(n):
    return f'{n:,}'.replace(',', '&nbsp;') + '&nbsp;₽'


def area_html(key, p):
    rows = ''.join(f'<tr><td data-l="Площадь">{a}</td><td data-l="Разовая работа">от {rub(o)}</td>'
                   f'<td data-l="Договор, в месяц">от {rub(m)}</td></tr>'
                   for a, (o, m) in zip(AREAS, AREA_PRICES[key]))
    rows += ('<tr><td data-l="Площадь">больше 1000 м²</td><td data-l="Разовая работа">по расчёту</td>'
             '<td data-l="Договор, в месяц">по расчёту</td></tr>')
    return (f'    <div class="rk-ptbl-w">\n      <p class="rk-h3">{p["area_h"]}</p>\n'
            f'      <table class="d-table rk-ptbl"><caption class="sr-only">{p["area_h"]}: цены от</caption>'
            '<thead><tr><th scope="col">Площадь</th><th scope="col">Разовая работа</th><th scope="col">Договор, в месяц</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>\n'
            '      <p class="rk-pnote">Цены «от» — для заведения без активного очага. Площадь — вся площадь заведения: кухня, '
            'склад, бар, зал и подсобки. Точную цену называем после бесплатного обследования.</p>\n    </div>')


def faq_section(p):
    def qa(i, q, a):
        # развёрнут только первый вопрос, остальные свёрнуты (решение владельца 13.11.2026, tools/site/faq_first.py)
        cls, exp = (' open', 'true') if i == 1 else ('', 'false')
        return (f'        <div class="card qa{cls}"><button aria-expanded="{exp}" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    faq = p['faq']
    half = (len(faq) + 1) // 2
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            f'    <div class="head"><div class="eyebrow">Вопросы</div><h2>{p["faq_h2"]}</h2></div>',
            '    <div class="faq">']
    n = 0
    for col in (faq[:half], faq[half:]):
        html.append('      <div class="faq-col">')
        for q, a in col:
            n += 1
            html.append(qa(n, q, a))
        html.append('      </div>')
    html += ['    </div>', '  </div>', '</section>']
    return '\n'.join(html)


def form_html(p):
    types = ''.join(f'<option value="{t}" selected>{t} *</option>' if t == 'Ресторан или кафе' else f'<option>{t}</option>' for t in TYPES)
    fmts = ''.join(f'<option>{f}</option>' for f in FORMATS)
    tasks = ''.join(f'<option>{t}</option>' for t in p['tasks'])
    return f'''    <form class="form" id="form" novalidate data-form>
      <div class="fbody">
        <h3>{p['form_h']}</h3>
        <p class="fs">Заполнение займёт меньше минуты</p>
        <div class="fg">
<div class="field"><label class="sr-only" for="f-name">Ваше имя</label><input id="f-name" name="name" placeholder="Ваше имя *" required autocomplete="name"><small class="ferr">Укажите имя</small></div>
<div class="field"><label class="sr-only" for="phone">Телефон</label><input name="phone" id="phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__ *" required autocomplete="tel"><small class="ferr">Укажите телефон полностью</small></div>
<div class="field full"><label class="sr-only" for="f-type">Тип объекта</label><select id="f-type" name="type" required><option value="" disabled>Тип объекта *</option>{types}</select><small class="ferr">Выберите тип объекта</small></div>
<div class="field full"><label class="sr-only" for="f-fmt">Формат заведения</label><select id="f-fmt" name="format"><option value="" selected>Формат заведения</option>{fmts}</select></div>
<div class="field full"><label class="sr-only" for="f-task">Что беспокоит</label><select id="f-task" name="task"><option value="" selected>Что беспокоит</option>{tasks}</select></div>
<div class="field full"><label class="sr-only" for="f-cmt">Адрес и удобное время</label><textarea id="f-cmt" name="comment" placeholder="Адрес, площадь, удобное время визита"></textarea></div>
<div class="field" hidden><input type="hidden" name="email" value=""></div>
<input type="hidden" name="msg" id="fmsg" value="">
</div>
        <button type="submit" class="btn btn-w btn-lg" id="submitBtn"><span class="btn-t">Заказать обследование</span><svg class="btn-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg><i class="spin" aria-hidden="true"></i></button>
        <p class="legal">Нажимая кнопку, вы даёте <a href="@/soglasie/" target="_blank" rel="noopener">согласие на обработку персональных данных</a> и подтверждаете, что ознакомились с <a href="@/privacy/" target="_blank" rel="noopener">политикой конфиденциальности</a>.</p>
      </div>
      <div class="ok" role="status" aria-live="polite">
        <svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>
        <h3>Заявка отправлена</h3><p>Перезвоним в ближайшее рабочее время, чтобы согласовать день обследования.</p>
      </div>
    </form>'''


def page_js(p):
    return ("<script>/* Форма: формат заведения, «Что беспокоит», адрес и страница — в поле msg, которое читает send.php */\n"
            "(function(){var f=document.getElementById('form');if(!f)return;f.addEventListener('submit',function(){"
            "var v=function(n){var el=f.elements[n];return el?String(el.value||'').replace(/\\u00a0/g,' ').trim():''},rows=[];"
            "if(v('format'))rows.push('Формат заведения: '+v('format'));if(v('task'))rows.push('Что беспокоит: '+v('task'));"
            "if(v('comment'))rows.push('Адрес и комментарий: '+v('comment').slice(0,2500));"
            f"rows.push('Страница: {p['page_name']} (/{p['slug']})');f.elements.msg.value=rows.join('\\n')}},true)}})();</script>\n")


def json_ld(p):
    url = SITE + p['slug']
    org = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
           'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
           'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}

    def offer(name, price, unit):
        o = {'@type': 'Offer', 'name': name, 'priceCurrency': 'RUB', 'price': price}
        if unit:
            o['priceSpecification'] = {'@type': 'UnitPriceSpecification', 'minPrice': price, 'priceCurrency': 'RUB',
                                       'unitText': 'в месяц', 'unitCode': unit}
        else:
            o['priceSpecification'] = {'@type': 'PriceSpecification', 'minPrice': price, 'priceCurrency': 'RUB'}
        return o
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': t, 'item': SITE + s} for i, (t, s) in enumerate(p['crumbs'])]},
        {'@type': 'Service', '@id': url + '#service', 'name': p['name'], 'alternateName': p['alt_names'],
         'serviceType': p['service_type'], 'description': p['desc'], 'url': url, 'provider': org,
         'category': 'Общественное питание',
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Рестораны, кафе, бары, столовые и пищеблоки'},
         'offers': offer(*p['offers'][0]),
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Цены: ' + p['name'].lower(),
                             'itemListElement': [offer(*o) for o in p['offers']]}},
        {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': p['title'], 'description': p['desc'],
         'inLanguage': 'ru', 'datePublished': DATE, 'dateModified': DATE, 'about': {'@id': url + '#service'},
         'isPartOf': {'@type': 'WebSite', 'url': SITE, 'name': 'ПЕСТКОНТРОЛЬ Центр'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + f'img/{p["hero"]}-hero.webp', 'width': 1920, 'height': 1072}},
        {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in p['faq']]},
    ]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def build(key, p, tpl, icons):
    url = SITE + p['slug']
    n = p['hero'] + '-hero'
    head = tpl[:tpl.index('<style>')]
    rep = [
        (r'<title>[^<]*</title>', f'<title>{p["title"]}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{p["desc"]}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{p["og_title"]}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{p["desc"]}">\n'
         f'<meta property="og:image" content="{SITE}img/{p["og"]}.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{p["hero_alt"]}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         f'<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/{n}-1440.webp 1440w, ../img/{n}.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         f'<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/{n}-mob-760.webp 760w, ../img/{n}-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, k = re.subn(pat, lambda m: new, head, count=1)
        assert k == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', f'<body class="d-page rk-page rk-{key}">', 1)
    assert 'rk-page' in top
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    pjs = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', pjs, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    pjs = '<script>\n' + pv.group(1) + '\n</script>'
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False).replace(' data-fade', '')
    head, top, bottom, pjs, loader, contacts = (deeper(x) for x in (head, top, bottom, pjs, loader, contacts))

    main = (HERE / p['main']).read_text(encoding='utf-8')
    main = (main.replace('<!--FAQ-->', faq_section(p)).replace('<!--FORM-->', form_html(p))
                .replace('<!--AREA_PRICES-->', area_html(key, p))
                .replace('<!--ZONES-->\n', blocks.zones_html(key)).replace('<!--TIMELINE-->\n', blocks.timeline_html() + '\n')
                .replace('<!--SIZES-->\n', blocks.sizes_html() + '\n').replace('<!--CONTOURS-->\n', blocks.contours_html() + '\n')
                .replace('<!--CALC-->\n', blocks.calc_html(key, AREAS, AREA_PRICES[key]) + '\n')
                .replace('<!--DOCS-->\n', blocks.docs_html(key)).replace('<!--SAMPLES-->\n', blocks.samples_html(key, LIC)).replace('<!--MORE-->\n', blocks.more_html(key, icons)))
    main = main.replace('href="https://fp.rospotrebnadzor.ru/licen/"', f'href="{LIC}"')
    main = typeset(main)
    main = re.sub(r'<!--ICON:([a-z0-9-]+)-->', lambda m: icons[m.group(1)], main)
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    main = main.replace('"@/', '"../../').replace(' @/', ' ../../')
    assert '@/' not in main, p['slug'] + ': остались метки @/'
    assert '<!--' not in main.replace('<!-- ', ''), p['slug'] + ': остались метки'

    html = (head + '<style>' + css + '</style>\n' + json_ld(p).replace('"@/', '"' + SITE) + '\n' + top + main + bottom + pjs + '\n'
            + loader + page_js(p) + blocks.ZONE_JS + blocks.CALC_JS + '</body>\n</html>\n')
    out = ROOT / p['slug'] / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    words = len(re.findall(r'[А-Яа-яЁёA-Za-z0-9]+', plain(main)))
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ,', words, 'слов')


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    for key, p in PAGES.items():
        build(key, p, tpl, icons)


if __name__ == '__main__':
    main()
