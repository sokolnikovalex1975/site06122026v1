"""Блоки страниц общепита (tools/restorany-uslugi), добавлены 11.11.2026 по замечанию владельца «страницы получились
скучными»: схема зон ресторана (как на /restorany-i-kafe/, но только про насекомых или только про грызунов),
инфографика, калькулятор цены по площади, образцы документов, нормы и «что ещё нужно ресторану к проверке».

Корень сайта в разметке — метка '@/' (build_pages.py меняет её на '../../').
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

SANPIN = 'http://pravo.gov.ru/proxy/ips/?docbody=&amp;nd=602107773'
SANPIN_OP = 'https://www.consultant.ru/document/cons_doc_LAW_535846/010c7df02bdb9fef4537221a54f49682945c7fcd/'
KOAP = 'https://www.consultant.ru/document/cons_doc_LAW_34661/dceffcf2617aa8cbad91f46398ce0beab3d0ea76/'
CGON = ('https://cgon.rospotrebnadzor.ru/biznesu/profilaktika-nadzor-uslsugi/nadzornie-meropriatiya/'
        'litsenzirovanie-dezinfektsionnoy-deyatelnosti/')
WIND = ('<svg aria-hidden="true" focusable="false" class="lucide lucide-wind" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12.8 19.6A2 2 0 1 0 14 16H2"/>'
        '<path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></svg>')


# ---------------------------------------------------------------- схема зон
ZONES = {
    'dzr': [
        ('Приёмка и склад', 'Тараканы приезжают в коробках и возвратной таре, моль и жуки — в муке, крупах и специях. Клеевые мониторы, феромонные ловушки, проверка партий на приёмке.'),
        ('Горячий цех', 'Тепло под плитами, пароконвектоматами и фритюрницами — главное место рыжих тараканов. Гель в щели, мониторы под оборудованием.'),
        ('Холодный цех и заготовка', 'Здесь открытый продукт, поэтому без распыления: мониторы и гель только в недоступных местах.'),
        ('Мойка и трапы', 'Тараканы — в посудомоечных машинах, мошки-бабочницы — в налёте трапов и жироуловителей. Ищем места выплода, чистку трапа записываем в акт.'),
        ('Бар и кофейная станция', 'Дрозофилы — в сиропах, фруктах и пивных линиях, тараканы — в кофемашинах и ледогенераторах. Приманочные ловушки и гель в полости корпуса.'),
        ('Зал и веранда', 'Мухи у входа и на летней веранде. УФ-ловушки — вне линии раздачи и мест, где стоят блюда.'),
        ('Мусорная площадка и подвал', 'Мухи выводятся у отходов, тараканы поднимаются по стоякам. В акте — рекомендации: закрытые баки, вывоз отходов, сетки и завесы.'),
    ],
    'drr': [
        ('Приёмка и склад', 'Мыши приезжают в коробках и мешках с поставкой и живут за стеллажами. Ловушки вдоль стен, продукты — на стеллажах и подтоварниках.'),
        ('Горячий цех', 'Тёплые полости за плитами и под оборудованием. Ловушки и клеевые туннели в закрытых корпусах — без яда.'),
        ('Холодный цех и заготовка', 'Открытый продукт рядом — только ловушки без яда, вдоль стен и под столами.'),
        ('Мойка', 'Вводы труб и канализации за мойкой — частый путь мышей. Мелкие ходы заделываем сами, остальное — в список для техслужбы с фото.'),
        ('Бар', 'Склад напитков и закусок, полости под стойкой. Ловушки в незаметных местах.'),
        ('Зал и веранда', 'Мыши живут в подвесных потолках и за декоративными панелями. Ловушки над потолком и вдоль стен.'),
        ('Мусорная площадка и подвал', 'Отходы и коммуникации — путь крыс. Станции на ключ с приманкой снаружи и в подвале, замечания по площадке — в акте.'),
    ],
}
ZONE_HEAD = {
    'dzr': ('Зоны риска', 'Где в ресторане <em>прячутся насекомые</em>',
            'Выберите зону на схеме или в списке — покажем, какие насекомые там заводятся и что мы там ставим.'),
    'drr': ('Зоны риска', 'Где в ресторане <em>прячутся мыши и крысы</em>',
            'Выберите зону на схеме или в списке — покажем, откуда приходят грызуны и какие точки мы там ставим.'),
}
LEGEND = {
    'dzr': '<span><i class="lg-tr"></i>Клеевой монитор</span><span><i class="lg-uv"></i>УФ-ловушка для мух</span><span><i class="lg-gel"></i>Гелевая приманка</span><span><i class="lg-fl"></i>Путь продуктов</span>',
    'drr': '<span><i class="lg-st"></i>Станция на ключ с приманкой — снаружи</span><span><i class="lg-tr"></i>Ловушка без яда — внутри</span><span><i class="lg-fl"></i>Путь продуктов</span>',
}
ZONE_JS = ("<script>/* схема зон: подсветка зоны по наведению и нажатию — как на /restorany-i-kafe/ */\n"
           "(function(){var map=document.querySelector('.f-zmap');if(!map)return;var plan=map.querySelector('.f-plan'),items=map.querySelectorAll('.f-zlist li');"
           "function set(z){plan.querySelectorAll('[data-z]').forEach(function(g){g.classList.toggle('on',g.getAttribute('data-z')===z)});"
           "items.forEach(function(li){li.classList.toggle('on',li.getAttribute('data-z')===z)})}"
           "items.forEach(function(li){var z=li.getAttribute('data-z');li.addEventListener('mouseenter',function(){set(z)});li.addEventListener('focus',function(){set(z)});li.addEventListener('click',function(){set(z)})});"
           "plan.querySelectorAll('.zf,.bdg').forEach(function(el){var g=el.closest('[data-z]');el.addEventListener('mouseenter',function(){set(g.getAttribute('data-z'))});"
           "el.addEventListener('click',function(){set(g.getAttribute('data-z'))})});map.addEventListener('mouseleave',function(){set(null)})})();</script>\n")


def plan_svg(key):
    """SVG схемы со страницы ресторанов (tools/restorany/main.html) — без чужих обозначений."""
    src = (ROOT / 'tools' / 'restorany' / 'main.html').read_text(encoding='utf-8')
    a = src.index('<svg viewBox="0 0 960 600"')
    svg = src[a:src.index('</svg>', a) + 6]
    title = {'dzr': 'Схема ресторана: семь зон риска по насекомым, клеевые мониторы, УФ-ловушки, гелевые приманки и путь продуктов от приёмки до зала',
             'drr': 'Схема ресторана: семь зон риска по грызунам, станции на ключ снаружи, ловушки без яда внутри и путь продуктов от приёмки до зала'}[key]
    svg, n = re.subn(r'<title id="plan-t">[^<]*</title>', f'<title id="plan-t">{title}</title>', svg)
    assert n == 1
    drop = {'dzr': ['<g fill="#fdc700"'], 'drr': ['<g fill="#c4b5fd"', '<g fill="#4ade80"']}[key]
    for start in drop:
        i = svg.index(start)
        svg = svg[:i] + svg[svg.index('</g>', i) + 4:]
    return svg


def zones_html(key):
    eb, h2, sub = ZONE_HEAD[key]
    lis = '\n'.join(f'        <li data-z="{i}" tabindex="0"><b>{t}</b><span>{d}</span></li>' for i, (t, d) in enumerate(ZONES[key], 1))
    return f'''<section class="s" id="zony">
  <div class="wrap">
    <div class="head"><div class="eyebrow">{eb}</div><h2>{h2}</h2><p class="sub">{sub}</p></div>
    <div class="f-zmap">
      <figure class="card f-plan">
        {plan_svg(key)}
        <figcaption class="f-legend">{LEGEND[key]}</figcaption>
        <p class="rk-zdoc">Так точки выглядят в ваших документах — <a href="@/materialy/skhema-tochek-pest-kontrolya/">образец схемы точек пест-контроля</a> (<a href="@/materialy/skhema-tochek-pest-kontrolya/obrazets-skhemy-tochek-pest-kontrolya.pdf">PDF</a>).</p>
      </figure>
      <ol class="f-zlist">
{lis}
      </ol>
    </div>
  </div>
</section>
'''


# ---------------------------------------------------------------- инфографика: дезинсекция
TIMELINE = [
    ('День 0', 'Обработка', 'Гель в щели и полости оборудования, клеевые мониторы по схеме.'),
    ('Первые дни', 'Тараканов «стало больше»', 'Средство выгоняет их из укрытий, поэтому они чаще попадаются на глаза.'),
    ('10–14 дней', 'Выходит молодняк', 'Капсулу с яйцами — оотеку — средство почти не пробивает: молодняк выходит уже после обработки.'),
    ('Повторная проверка', 'Мониторы и журнал', 'Смотрим мониторы. Если живые остались — обработка средством другой химической группы (п. 99 СанПиН 3.3686-21).'),
    ('Дальше', 'Визиты по графику', 'По журналу видно, когда находки прекратились и откуда приходят новые.'),
]


def timeline_html():
    lis = '\n'.join(f'        <li><span class="rk-tl-d">{d}</span><b>{b}</b><span class="rk-tl-t">{t}</span></li>' for d, b, t in TIMELINE)
    return f'''    <div class="rk-tl-w">
      <p class="rk-h3">Почему одной обработки против тараканов мало</p>
      <ol class="rk-tl">
{lis}
      </ol>
    </div>'''


# ---------------------------------------------------------------- инфографика: дератизация
SIZES = [  # подпись, мм от, мм до, класс
    ('Помёт мыши', 3, 6, 'm'),
    ('Помёт крысы', 10, 20, 'r'),
    ('Щель, в которую пролезает мышь', 6, 8, 'g'),
]


def sizes_html():
    """Линейка в мм — HTML, а не SVG: текст остаётся читаемым и на 375 px, полосы ставятся в процентах шкалы 0–22 мм."""
    full = 22
    pc = lambda v: f'{v / full * 100:.3f}'.rstrip('0').rstrip('.') + '%'
    rows = ''.join(f'<li class="rk-sz-{c}"><span class="rk-sz-l">{lab} — <b>{a}–{b}&nbsp;мм</b></span>'
                   f'<span class="rk-sz-tr"><span class="rk-sz-min" style="width:{pc(a)}"></span>'
                   f'<span class="rk-sz-rng" style="left:{pc(a)};width:{pc(b - a)}"></span></span></li>'
                   for lab, a, b, c in SIZES)
    ticks = ''.join(f'<span class="{"rk-sz-tb" if mm % 5 == 0 else "rk-sz-ts"}" style="left:{pc(mm)}">'
                    + (f'<i>{mm}</i>' if mm % 5 == 0 else '') + '</span>' for mm in range(0, full + 1))
    return f'''    <figure class="card rk-sz">
      <p class="rk-h3">Размеры, по которым узнают грызунов, — в масштабе линейки, мм</p>
      <ul class="rk-sz-rows" role="list">{rows}</ul>
      <div class="rk-sz-ruler" aria-hidden="true">{ticks}</div>
      <figcaption>Мыши достаточно щели примерно в толщину карандаша, поэтому вводы труб и зазоры под дверями закрывают сеткой, металлом или раствором — монтажную пену грызуны прогрызают.</figcaption>
    </figure>'''


CONTOURS = [
    ('Снаружи', 'Мусорная площадка, двор, вход в подвал', 'Станции на ключ с приманкой, закреплённые и с номером', 'st'),
    ('Граница здания', 'Приёмка, чёрный ход, вводы коммуникаций', 'Ловушки вдоль стен, заделка ходов, уплотнители и доводчики — в списке для техслужбы', 'b'),
    ('Внутри', 'Кухня, склад продуктов, бар и зал', 'Только ловушки и клеевые туннели — без яда', 'in'),
]


def contours_html():
    items = '\n'.join(f'        <li class="rk-ct-{c}"><span class="rk-ct-n">{i}</span><b>{t}</b><span class="rk-ct-z">{z}</span><span class="rk-ct-d">{d}</span></li>'
                      for i, (t, z, d, c) in enumerate(CONTOURS, 1))
    return f'''    <div class="rk-ct">
      <div class="rk-ct-pic" aria-hidden="true"><div class="rk-ct-o"><span>1 · снаружи</span><div class="rk-ct-m"><span>2 · граница здания</span><div class="rk-ct-i"><span>3 · внутри</span><b>без яда</b></div></div></div></div>
      <ol class="rk-ct-l">
{items}
      </ol>
    </div>'''


# ---------------------------------------------------------------- калькулятор по площади
def calc_html(key, areas, prices):
    bands = [{'to': int(re.search(r'(\d+)\s*м²', a).group(1)), 'o': o, 'm': m} for a, (o, m) in zip(areas, prices)]
    data = json.dumps(bands, separators=(',', ':'))
    what = {'dzr': 'дезинсекции', 'drr': 'дератизации'}[key]
    return f'''    <div class="card rk-calc" data-bands='{data}'>
      <div class="rk-calc-in">
        <label class="rk-h3" for="rk-area">Площадь заведения: <output id="rk-area-v" for="rk-area">150</output> м²</label>
        <input type="range" id="rk-area" min="20" max="1200" step="10" value="150" aria-describedby="rk-calc-n">
        <div class="rk-calc-sc" aria-hidden="true"><span>20</span><span>300</span><span>600</span><span>900</span><span>1200 м²</span></div>
      </div>
      <div class="rk-calc-out" aria-live="polite">
        <div><span>Разовая работа</span><b id="rk-c-o">от 3&nbsp;500&nbsp;₽</b></div>
        <div><span>Договор, в месяц</span><b id="rk-c-m">от 3&nbsp;500&nbsp;₽</b></div>
        <a href="#zayavka" class="btn btn-w btn-lg" id="rk-c-go"><span class="btn-t">Точный расчёт бесплатно</span></a>
      </div>
      <p class="rk-pnote" id="rk-calc-n">Ориентир цены {what} по таблице ниже. Точную цену называем после бесплатного обследования.</p>
    </div>'''


CALC_JS = ("<script>/* калькулятор по площади: цена «от» по таблице; площадь уходит в комментарий заявки */\n"
           "(function(d){var c=d.querySelector('.rk-calc');if(!c)return;var b=JSON.parse(c.getAttribute('data-bands')),r=d.getElementById('rk-area'),"
           "v=d.getElementById('rk-area-v'),o=d.getElementById('rk-c-o'),m=d.getElementById('rk-c-m');"
           "function f(n){return 'от\\u00a0'+String(n).replace(/\\B(?=(\\d{3})+(?!\\d))/g,'\\u00a0')+'\\u00a0₽'}"
           "function u(){var a=+r.value,x=null;for(var i=0;i<b.length;i++){if(a<=b[i].to){x=b[i];break}}v.textContent=a>1000?'больше 1000':a;"
           "o.textContent=x?f(x.o):'по расчёту';m.textContent=x?f(x.m):'по расчёту'}"
           "r.addEventListener('input',u);u();d.getElementById('rk-c-go').addEventListener('click',function(){var t=d.getElementById('f-cmt');"
           "if(t&&!t.value)t.value='Площадь: '+(+r.value>1000?'больше 1000':r.value)+' м²'})})(document);</script>\n")


# ---------------------------------------------------------------- образцы документов и нормы
SAMPLES = [
    ('Образец акта дезинсекции и дератизации', 'что записываем после каждого визита', 'akt-obrazets-p1-360', 360, 509,
     '@/materialy/akt-deratizatsii-i-dezinsektsii/', '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/obrazets-akta-dezinsektsii-i-deratizatsii.pdf'),
    ('Журнал пест-контроля', 'образец заполнения: точки, находки, предписания', 'zhurnal-obrazets-p1-360', 360, 509,
     '@/materialy/zhurnal-pest-kontrolya/', '@/materialy/zhurnal-pest-kontrolya/obrazets-zhurnala-pest-kontrolya.pdf'),
    ('Программа пест-контроля', 'зоны, точки контроля, пест-риск и план', 'programma-sample-p1-360', 360, 509,
     '@/materialy/programma-pest-kontrolya/', '@/materialy/programma-pest-kontrolya/obrazets-programmy-pest-kontrolya.pdf'),
    ('Договор на дератизацию и дезинсекцию', 'перечень работ, график, стоимость', 'dogovor-sample-p1-360', 360, 509,
     '@/dogovor-deratizatsiya-dezinsektsiya/', '@/dogovor-deratizatsiya-dezinsektsiya/obrazets-dogovora-pestkontrol-tsentr.pdf'),
    ('Программа производственного контроля по ХАССП', 'раздел о дезинсекции и дератизации', 'ppk-sample-p1-360', 360, 509,
     '@/materialy/programma-proizvodstvennogo-kontrolya-haccp/', '@/materialy/programma-proizvodstvennogo-kontrolya-haccp/obrazets-programmy-proizvodstvennogo-kontrolya.pdf'),
    ('Документы для Роспотребнадзора', 'чек-лист папки к проверке', 'dok-cover-360', 360, 509,
     '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/chek-list-dokumentov-dlya-rospotrebnadzora.pdf'),
]
NORMS = {
    'dzr': [
        ('СанПиН 3.3686-21, пп. 98–102', 'общепит — объект особого эпидемиологического значения: обследования на насекомых не реже 2 раз в месяц, смена средств при устойчивости, предупреждение персонала',
         [('Текст на pravo.gov.ru', SANPIN, 1), ('Разбор в нормативной базе', '@/normativnaya-baza/', 0)]),
        ('СанПиН 2.3/2.4.4282-26, пп. 26 и 45', 'насекомых в помещениях общепита быть не должно; распыляемые и рассыпаемые средства при посетителях и персонале запрещены',
         [('Текст в КонсультантПлюс', SANPIN_OP, 1)]),
        ('Проверочный лист для общепита, приказ № 580', 'вопросы 11, 58, 108 и 109 — о производственном контроле, насекомых и правилах обработки',
         [('Разбор проверочных листов', '@/normativnaya-baza/proverochnye-listy/', 0)]),
        ('Оценка эффективности', 'по каким критериям проверяют, что дезинсекция дала результат',
         [('Критерии эффективности', '@/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/', 0)]),
        ('Лицензия с 1 марта 2025 года', 'дезинсекцию для организаций оказывают только по лицензии; наша — <span class="nw">№ Л064-00111-77/01942445</span>',
         [('О лицензировании — ЦГОН Роспотребнадзора', CGON, 1), ('Проверить в реестре', 'LIC', 1)]),
    ],
    'drr': [
        ('СанПиН 3.3686-21, пп. 88, 98, 110, 111', 'кто обеспечивает дератизацию, ежемесячная оценка заселённости грызунами, работы по защите здания',
         [('Текст на pravo.gov.ru', SANPIN, 1), ('Разбор в нормативной базе', '@/normativnaya-baza/', 0)]),
        ('СанПиН 2.3/2.4.4282-26, п. 26', 'грызунов в помещениях общепита быть не должно — проверку оценивают по следам',
         [('Текст в КонсультантПлюс', SANPIN_OP, 1)]),
        ('МР 3.5.3.0374-25', 'организация дератизации: контрольно-учётная карта объекта и учёт по точкам',
         [('Что требуют методические рекомендации', '@/normativnaya-baza/', 0)]),
        ('Проверочный лист для общепита, приказ № 580', 'вопросы 11, 58 и 108 — о производственном контроле, грызунах и правилах работ',
         [('Разбор проверочных листов', '@/normativnaya-baza/proverochnye-listy/', 0)]),
        ('Оценка эффективности', 'по каким критериям проверяют, что дератизация дала результат',
         [('Критерии эффективности', '@/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/', 0)]),
        ('КоАП РФ, ст. 6.6', 'штраф организации 30–50 тыс. ₽ или приостановление деятельности до 90 суток',
         [('Текст в КонсультантПлюс', KOAP, 1)]),
    ],
}


def samples_html(key, lic):
    cards = []
    for t, d, img, w, h, page, pdf in SAMPLES:
        cards.append(f'        <div class="card rk-smp"><img src="@/img/{img}.webp" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">'
                     f'<div class="rk-smp-t"><a href="{page}"><b>{t}</b></a><span>{d}</span><a class="rk-smp-pdf" href="{pdf}" download>Скачать PDF</a></div></div>')
    rows = []
    for name, what, links in NORMS[key]:
        ln = ' · '.join(f'<a href="{lic if u == "LIC" else u}"' + (' target="_blank" rel="noopener"' if ext else '') + f'>{t}</a>' for t, u, ext in links)
        rows.append(f'        <li><b>{name}</b><span>{what}</span><span class="rk-nl">{ln}</span></li>')
    head = {'dzr': 'Образцы документов и нормы <em>по дезинсекции общепита</em>', 'drr': 'Образцы документов и нормы <em>по дератизации общепита</em>'}[key]
    return f'''<section class="s" id="obraztsy">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Образцы и нормы</div><h2>{head}</h2><p class="sub">Так выглядят документы, которые остаются у вас после визитов, и нормы, на которые смотрит инспектор. Образцы можно скачать.</p></div>
    <div class="rk-smps">
{chr(10).join(cards)}
    </div>
    <p class="rk-h3 rk-norms-h">Нормы и где их прочитать</p>
    <ul class="rk-norms">
{chr(10).join(rows)}
    </ul>
  </div>
</section>
'''


# ---------------------------------------------------------------- что ещё нужно ресторану
MORE = [
    ('lucide-clipboard-check', 'sanitarnyy-audit/', 'Санитарный аудит перед проверкой', 'Проверяем заведение по проверочному листу № 580 и СанПиН 2026, берём смывы и пробы воздуха, отдаём реестр нарушений с фото.'),
    ('lucide-flask-conical', 'laboratornye-issledovaniya/analiz-smyvov/', 'Анализ смывов', 'Смывы с поверхностей, оборудования и рук на БГКП, S.&nbsp;aureus и ОМЧ — по программе производственного контроля, от 310&nbsp;₽ за точку.'),
    ('lucide-file-signature', 'razrabotka-ppk/', 'Разработка ППК по ХАССП', 'Программа производственного контроля для общепита с разделом о дезинсекции и дератизации — от 19&nbsp;900&nbsp;₽ за 3 рабочих дня.'),
    ('WIND', 'ochistka-dezinfektsiya-ventilyatsii/', 'Очистка кухонных вытяжек', 'Жир в кухонной вытяжке — пожарный риск. Очистка и дезинфекция воздуховодов и вытяжек, видео до и после, акт по п. 43 ППР.'),
    ('lucide-spray-can', 'dezinfektsiya/', 'Дезинфекция', 'Плановая и внеплановая дезинфекция кухни, санузлов и зала по правилам 2026 года.'),
    ('lucide-shield-check', 'deratizatsiya-i-dezinsektsiya/', 'Дезинсекция и дератизация вместе', 'Насекомые и грызуны по одному договору и графику — от 4&nbsp;900&nbsp;₽ в месяц.'),
]


def more_html(key, icons):
    cards = '\n'.join(f'        <a class="card rk-x" href="@/{href}"><span class="rk-x-i">{WIND if ic == "WIND" else icons[ic]}</span><b>{t}</b><span>{d}</span></a>'
                      for ic, href, t, d in MORE)
    return f'''<section class="s" id="eshchyo">
  <div class="wrap">
    <div class="head"><div class="eyebrow">К проверке</div><h2>Что ещё нужно ресторану <em>к проверке Роспотребнадзора</em></h2><p class="sub">Инспектор смотрит не только насекомых и грызунов. Эти услуги закрывают остальные вопросы проверочного листа — у одного исполнителя и в одной папке документов.</p></div>
    <div class="rk-xs">
{cards}
    </div>
  </div>
</section>
'''
