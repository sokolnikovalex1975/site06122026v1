#!/usr/bin/env python3
"""Сборка сайта site06122026v1: единые анимации, заголовки и перелинковка на всех страницах.

Что делает (повторный запуск ничего не дублирует):
  * в <head> каждой страницы — одинаковый ранний скрипт (заставка один раз за посещение,
    страховка анимаций через 4 с), одна версия style.css и app.min.js;
  * подключает GSAP, ScrollTrigger и Lenis (локальные файлы vendor/) на всех страницах с анимациями —
    вместе с app.min.js они грузятся сразу после первой отрисовки (LOADER), чтобы не задерживать первый экран;
  * добавляет заставку, курсор и зерно, как на главной;
  * размечает анимации в стиле главной: надзаголовки (data-eyebrow), заголовки H2 по словам (data-split),
    подзаголовки и блоки (data-fade), группы карточек (data-group), наклон карточек с фото (data-tilt),
    «магнитные» кнопки (data-magnet), свечение и параллакс в блоке заявки;
  * первый экран внутренних страниц входит так же, как на главной (элементы data-h);
  * бегущая строка после первого экрана на каждой странице;
  * перелинковка: блок «Смотрите также» на внутренних страницах, ссылки «Подробнее» на главной.
  * эффекты под курсором, как на главной (tools/site/fx.py): «фонарь» на фото первого экрана, подсветка рамки
    карточек, появление формы, параллакс фото в карточках отраслей.

Меню в шапке, мобильное меню и подвал ставит tools/menu/apply_menu.py (запускается после этого скрипта).
Запуск из корня репозитория:  python3 tools/site/build_site.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import htmldom  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402  неразрывный пробел после коротких слов, как в остальных текстах сайта
import fx  # noqa: E402  эффекты под курсором, как на главной: фонарь на фото первого экрана, подсветка карточек


def nw(text):
    """Слова через дефис (пест-контроль, пест-риск) не переносим — класс nw, как в текстах страниц."""
    return re.sub(r'(?<![\w>-])([А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])', r'<span class="nw">\1</span>', text)


def tp(text):
    return typo(nw(text))

VERSION = '20261106s2'  # общая версия style.css и app.min.js для сброса кэша

HEAD_SCRIPT = (
    "<script>\n"
    "  /* начальные состояния анимаций — только при работающем JS; страховка — через 4 с всё показывается.\n"
    "     Заставка — один раз за посещение: при переходе по ссылке с якорем и между страницами сайта её нет */\n"
    "  (function (d) {\n"
    "    d.classList.add('js');\n"
    "    try { if (location.hash || sessionStorage.getItem('pc-intro')) d.classList.add('no-intro'); else sessionStorage.setItem('pc-intro', '1'); }\n"
    "    catch (e) { if (location.hash) d.classList.add('no-intro'); }\n"
    "    setTimeout(function () { if (!d.classList.contains('anim-ready')) d.classList.add('anim-fail'); }, 4000);\n"
    "  })(document.documentElement);\n"
    "</script>"
)
# Скрипты анимаций (GSAP, ScrollTrigger, Lenis) и app.min.js подключаются сразу после первой отрисовки, а не через defer:
# с defer первый кадр ждал выполнения ~160 КБ скриптов, и на телефонах фото и заголовок первого экрана появлялись на 0,8–1 с позже.
# Порядок выполнения сохраняется (async = false); в фоновой вкладке — без ожидания кадра.
LOADER = (
    "<script>\n"
    "  /* скрипты анимаций подключаются сразу после первой отрисовки: фото и заголовок первого экрана не ждут их загрузки */\n"
    "  (function (r, l) {\n"
    "    var go = function () { l.forEach(function (u) { var e = document.createElement('script'); e.src = r + u; e.async = false; document.body.appendChild(e); }); };\n"
    "    if (document.visibilityState === 'hidden' || !window.requestAnimationFrame) setTimeout(go, 0);\n"
    "    else requestAnimationFrame(function () { setTimeout(go, 0); });\n"
    "  })('{root}', ['vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', 'app.min.js?v={version}']);\n"
    "</script>"
)
SCRIPTS_RE = re.compile(
    r'<script src="((?:\.\./)*)vendor/gsap\.min\.js" defer></script>\n'
    r'<script src="\1vendor/ScrollTrigger\.min\.js" defer></script>\n'
    r'<script src="\1vendor/lenis\.min\.js" defer></script>\n'
    r'<script src="\1app\.min\.js\?v=[^"]*" defer></script>')
FOOD_FORM_JS = (
    "<script>/* Форма: вид производства, ближайшая проверка, комментарий и страница — в поле msg, которое читает send.php */\n"
    "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
    "p=e.production.value||'не выбран',i=e.inspection.value||'не выбрана',c=e.comment.value.trim();"
    "e.msg.value='Вид производства: '+p+'\\nБлижайшая проверка: '+i+(c?'\\nКомментарий: '+c:'')"
    "+'\\nСтраница: Пест-контроль на пищевом производстве (/pishchevoe-proizvodstvo/)';},true);</script>"
)
HEAD_SCRIPT_RE = re.compile(
    r"<script>\s*(?:/\*[^*]*\*/\s*)?(?:document\.documentElement\.className\+=' js anim-fail no-intro';"
    r"|document\.documentElement\.classList\.add\('js'\);.*?4000\);"
    r"|\(function \(d\) \{\s*d\.classList\.add\('js'\);.*?\}\)\(document\.documentElement\);)\s*</script>",
    re.S)

INTRO = (
    '<!-- ============ INTRO ============ -->\n'
    '<div class="intro" id="intro" aria-hidden="true">\n'
    '  <div class="intro-in">\n'
    '    <svg class="intro-mark" viewBox="0 0 24 24" fill="none" stroke-width="1" stroke-linejoin="round"><path class="im-shield" pathLength="100" d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/><circle class="im-c" pathLength="100" cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/><path class="im-x" pathLength="100" d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></svg>\n'
    '    <div class="intro-word"><span>ПЕСТКОНТРОЛЬ</span><b>Центр</b></div>\n'
    '    <div class="intro-bar"><i></i></div>\n'
    '  </div>\n'
    '</div>\n\n'
)
CURSOR = '<div class="cursor" aria-hidden="true"><i class="cursor-dot"></i><i class="cursor-ring"></i></div>\n'
GRAIN = '<div class="grain" aria-hidden="true"></div>\n'
ARR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

ICONS = json.loads((pathlib.Path(__file__).resolve().parent / 'icons.json').read_text(encoding='utf-8'))

# ---------------------------------------------------------------- страницы
# адрес страницы -> файл
URL = {
    'home': '', 'derat': 'deratizatsiya/', 'proof': 'zashchita-ot-proniknoveniya-gryzunov/', 'dezins': 'dezinsektsiya/',
    'dogovor': 'dogovor-deratizatsiya-dezinsektsiya/', 'food': 'pishchevoe-proizvodstvo/',
    'seti': 'magaziny-i-torgovye-seti/', 'hotel': 'gostinitsy/',
    'mat': 'materialy/', 'prog': 'materialy/programma-pest-kontrolya/',
    'zhur': 'materialy/zhurnal-pest-kontrolya/', 'pm': 'materialy/pest-menedzhment-ili-razovaya-obrabotka/',
    'vent': 'ochistka-dezinfektsiya-ventilyatsii/',
    'farma': 'farmatsevticheskie-proizvodstva/', 'sklady': 'sklady-i-logistika/',
    'ppk': 'materialy/programma-proizvodstvennogo-kontrolya-haccp/',
    'rest': 'restorany-i-kafe/',
    'san': 'sanitarnyy-audit/',
    'rppk': 'razrabotka-ppk/',
    'lab': 'laboratornye-issledovaniya/',
    # страницы направлений и статьи раздела «Лабораторные исследования» (tools/laboratornye-issledovaniya/build_subpages.py), с 11.11.2026
    'lab-smyvy': 'laboratornye-issledovaniya/analiz-smyvov/', 'lab-mikroklimat': 'laboratornye-issledovaniya/izmerenie-mikroklimata/',
    'lab-svet': 'laboratornye-issledovaniya/zamer-osveshchennosti/', 'lab-vrz': 'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/',
    'lab-pishcha': 'laboratornye-issledovaniya/analiz-pishchevykh-produktov/', 'lab-voda': 'laboratornye-issledovaniya/analiz-vody/',
    'lab-steril': 'laboratornye-issledovaniya/kontrol-sterilizatorov/',
    'mat-smyvy': 'materialy/kak-berut-smyvy/', 'mat-zamery': 'materialy/zamer-osveshchennosti-i-mikroklimata/',
    'mat-steril': 'materialy/kontrol-raboty-sterilizatorov/',
    'dd': 'deratizatsiya-i-dezinsektsiya/',
    # страницы «услуга + сфера» для общепита (tools/restorany-uslugi/build_pages.py), с 11.11.2026
    'dzr': 'dezinsektsiya/restorany-i-kafe/', 'drr': 'deratizatsiya/restorany-i-kafe/',
    'ppkobr': 'materialy/programma-proizvodstvennogo-kontrolya-haccp/',  # та же страница, что 'ppk', — карточка «Образец ППК» для страницы услуги
    'dezinf': 'dezinfektsiya/',
    'nb': 'normativnaya-baza/', 'pl': 'normativnaya-baza/proverochnye-listy/',
    'dok': 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/',
    'ef': 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/',  # с 11.11.2026 — превью
    'akt': 'materialy/akt-deratizatsii-i-dezinsektsii/', 'skhema': 'materialy/skhema-tochek-pest-kontrolya/',  # tools/materialy-dokumenty, с 11.11.2026 — превью
}
# карточки «Смотрите также»: (вид, заголовок, описание)
CARD = {
    'derat': ('Услуга', 'Дератизация для организаций',
              'Три контура защиты от крыс и мышей, контейнеры КИК и ловушки без яда в цехах, схема точек и акты.'),
    'proof': ('Услуга', 'Защита от проникновения грызунов',
              'Обследование путей доступа, герметизация проходок, защита дверей и ворот, фотофиксация выполненных работ.'),
    'dezins': ('Услуга', 'Дезинсекция для организаций',
               'Контроль насекомых по IPM без остановки работы, ротация средств, журнал и акты по СанПиН.'),
    'dd': ('Услуга', 'Дератизация и дезинсекция комплексом',
           'Грызуны и насекомые по одному договору: общий график визитов и один комплект документов. От 4\u00a0900\u00a0₽/мес.'),
    'dzr': ('Услуга', 'Дезинсекция кафе, ресторанов и столовых',
            'Тараканы, мухи и дрозофилы: что делать при находке, гели без закрытия кухни и ночная обработка без наценки.'),
    'drr': ('Услуга', 'Дератизация ресторанов и кафе',
            'Мыши и крысы: ловушки без яда на кухне, станции на ключ снаружи, пути захода и журнал по точкам.'),
    'dogovor': ('Обслуживание', 'Договор на дератизацию и дезинсекцию',
                'Одно или оба направления в одном договоре: график визитов, акт после выезда, цена до подписания.'),
    'food': ('Отрасль', 'Пест-контроль на пищевом производстве',
             'Точки контроля, визиты по графику смен и документы для Роспотребнадзора, аудиторов и торговых сетей.'),
    'seti': ('Отрасль', 'Пест-контроль магазинов и торговых сетей',
             'Большая часть работ без остановки магазина, журнал и схема точек в каждом магазине, сводный отчёт по сети.'),
    'hotel': ('Отрасль', 'Пест-контроль гостиниц и отелей',
              'Осмотры номерного фонда, протокол при жалобе гостя на клопов и журнал по проверочному листу Роспотребнадзора.'),
    'rest': ('Отрасль', 'Пест-контроль ресторанов и кафе',
             'Визиты после закрытия, гели и ловушки на кухне, журнал и акты по СанПиН для заведений и сетей.'),
    'prog': ('Материал', 'Программа пест-контроля',
             'Образец и шаблон в PDF: 7 разделов, оценка пест-риска по зонам и план мероприятий.'),
    'zhur': ('Материал', 'Журнал пест-контроля',
             'Образец заполнения и шаблон в PDF: 9 разделов на 10 листах — точки контроля, ловушки, предписания.'),
    'pm': ('Материал', 'Пест-менеджмент или разовая обработка',
           'Чем системный контроль по IPM отличается от обработок по вызову и когда хватит одного выезда.'),
    'vent': ('Услуга', 'Очистка и дезинфекция вентиляции',
             'Воздуховоды, кухонные вытяжки и кондиционеры: видео до и после, акт по п. 43 ППР, журнал по МР 3.5.0396-25.'),
    'farma': ('Отрасль', 'Пест-контроль фармацевтического производства',
              'Контуры защиты до чистых зон, без яда в помещениях, тренды и документы для GMP-инспекции.'),
    'sklady': ('Отрасль', 'Пест-контроль для складов и логистики',
               'Схема точек по зонам склада, визиты без остановки приёмки и отгрузки, журнал и отчёт для аудитов.'),
    'ppk': ('Материал', 'Программа производственного контроля по ХАССП',
            'Полный образец ППК для пищевого производства (PDF, 27 страниц) и раздел о дезинсекции и дератизации по правилам 2026 года.'),
    'rppk': ('Услуга', 'Разработка ППК',
             'ППК под ваш объект — от 5\u00a0900\u00a0₽ за 1 рабочий день, ППК по ХАССП для общепита и пищевых производств — от 19\u00a0900\u00a0₽ за 3 рабочих дня.'),
    'ppkobr': ('Материал', 'Образец ППК по ХАССП',
               'Полная программа для пищевого производства в PDF, 27 страниц, и разбор раздела о дезинсекции и дератизации.'),
    'lab': ('Услуга', 'Лабораторные исследования',
            'Смывы, воздух, вода, продукция и замеры по ППК — своя лаборатория, прайс и расчёт онлайн. От 2\u00a0600\u00a0₽.'),
    'lab-smyvy': ('Услуга', 'Анализ смывов',
                  'Смывы с поверхностей, оборудования и рук на БГКП, S. aureus и ОМЧ по МР 4.2.0220-20 — от 310\u00a0₽ за точку.'),
    'lab-mikroklimat': ('Услуга', 'Измерение микроклимата',
                        'Температура, влажность и скорость движения воздуха на рабочих местах по МУК 4.3.4120-25 — от 350\u00a0₽ за точку.'),
    'lab-svet': ('Услуга', 'Замер освещённости',
                 'Освещённость рабочих мест поверенным люксметром по ГОСТ 24940-2016 и нормам СанПиН — от 350\u00a0₽ за точку.'),
    'lab-vrz': ('Услуга', 'Анализ воздуха рабочей зоны',
                'Отбор проб в зоне дыхания по ГОСТ 12.1.005-88 и сравнение с ПДК — от 600\u00a0₽ за вещество.'),
    'lab-pishcha': ('Услуга', 'Анализ пищевых продуктов',
                    'Микробиология, химия и пищевая ценность сырья, продукции и готовых блюд по ТР ТС 021/2011 — от 194\u00a0₽.'),
    'lab-voda': ('Услуга', 'Анализ воды',
                 'Водопровод, скважина, горячая вода, бассейн и стоки: микробиология от 2\u00a0350\u00a0₽, химия от 737\u00a0₽.'),
    'lab-steril': ('Услуга', 'Контроль работы стерилизаторов',
                   'Бактериологический контроль автоклавов и сухожаровых шкафов, стерильность и облучатели — от 1\u00a0003\u00a0₽.'),
    'mat-smyvy': ('Материал', 'Как берут смывы с поверхностей и рук',
                  'Порядок по МР 4.2.0220-20: время, площадь, руки и спецодежда, доставка и типичные ошибки.'),
    'mat-zamery': ('Материал', 'Как проходит замер освещённости и микроклимата',
                   'Периодичность по СП 2.2.4285-26, подготовка помещений, число точек и отличие от спецоценки.'),
    'mat-steril': ('Материал', 'Контроль работы стерилизаторов',
                   'Три метода, периодичность, записи о циклах и хранение инструментов в салоне красоты.'),
    'san': ('Услуга', 'Санитарный аудит (СЭС-аудит)',
            'Проверка по проверочным листам и СанПиН 2026 года, смывы и пробы воздуха, акт с реестром нарушений.'),
    'dezinf': ('Услуга', 'Дезинфекция для организаций',
               'Плановая и внеплановая дезинфекция, смывы, периодичность по правилам 2026 года и все санитарные услуги в одной программе.'),
    'nb': ('Нормативная база', 'СанПиН и требования к дезинсекции и дератизации',
           'Действующие документы 2026 года, периодичность обследований, лицензия исполнителя и отменённые СП и СанПиН.'),
    'pl': ('Разбор', 'Проверочные листы Роспотребнадзора 2026',
           'Вопросы о насекомых и грызунах по приказам № 578 и № 580 — по видам объектов и с документами для ответа.'),
    'dok': ('Перечень', 'Документы для Роспотребнадзора',
            'Что должно быть в папке к проверке: 41 общий документ, разделы по видам объектов, конструктор и чек-лист PDF.'),
    'ef': ('Разбор', 'Оценка эффективности дератизации и дезинсекции',
           'Когда проверять результат обработки, чем считают вредителей и что считается эффектом по СанПиН 3.3686-21.'),
    'akt': ('Образец', 'Акт дератизации и дезинсекции',
            'Что указать в акте по каждому визиту: реквизиты, средства с СГР, результаты по точкам, подписи. Образец и бланк PDF.'),
    'skhema': ('Образец', 'Схема точек пест-контроля',
               'Три контура защиты, нумерация и обозначения точек, реестр и редакции схемы. Интерактивный план и PDF.'),
}

STRIP_LABELS = {}
PAGES = {
    'dezinfektsiya/index.html': dict(key='dezinf', root='../', related=['vent', 'san', 'dezins', 'derat'], strip=(
        'Коротко о дезинфекции', [
            ('lucide-spray-can', 'Плановая', 'и внеплановая дезинфекция'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и правила 2026 года'),
            ('lucide-shield-check', 'Лицензия', 'Роспотребнадзора'),
            ('lucide-notebook-pen', 'Акт и журнал', 'после каждого выезда'),
            ('lucide-flask-conical', 'Смывы', 'через аккредитованную лабораторию'),
            ('lucide-clipboard-check', 'Санитарный аудит', 'до проверки'),
            ('lucide-crosshair', 'Пест-контроль', 'по системе IPM'),
            ('lucide-clock', 'Ночью и в выходные', 'без наценки'),
        ])),
    'deratizatsiya/index.html': dict(key='derat', root='../', related=['dd', 'dezins', 'dogovor', 'san']),
    'zashchita-ot-proniknoveniya-gryzunov/index.html': dict(key='proof', root='../', related=['derat', 'sklady', 'prog', 'san']),
    'dezinsektsiya/index.html': dict(key='dezins', root='../', related=['dd', 'derat', 'dogovor', 'san'], strip=(
        'Коротко о дезинсекции', [
            ('lucide-crosshair', 'IPM', 'контроль насекомых'),
            ('lucide-scan-search', 'Бесплатный осмотр', 'и расчёт до договора'),
            ('lucide-ban', 'Без остановки', 'работы цехов и кухонь'),
            ('lucide-activity', 'Ротация', 'действующих веществ разных групп'),
            ('lucide-map-pinned', 'Ловушки и УФ-лампы', 'на схеме точек'),
            ('lucide-notebook-pen', 'Журнал и акт', 'после каждого визита'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и ХАССП'),
            ('lucide-clock', 'Ночной выезд', 'без наценки'),
        ])),
    'ochistka-dezinfektsiya-ventilyatsii/index.html': dict(key='vent', root='../', related=['dezins', 'food', 'dogovor', 'derat'], strip=(
        'Коротко об очистке и дезинфекции вентиляции', [
            ('lucide-scan-search', 'Видео до и после', 'по каждому участку'),
            ('lucide-file-badge', 'Акт по п. 43 ППР', 'для пожарной проверки'),
            ('lucide-notebook-pen', 'Журнал', 'по МР 3.5.0396-25'),
            ('lucide-spray-can', 'Дезсредства с СГР', 'и режимом для вентиляции'),
            ('lucide-utensils', 'Кухонные вытяжки', 'зонты, фильтры, короба'),
            ('lucide-flask-conical', 'Смывы', 'на легионеллы и микрофлору'),
            ('lucide-clock', 'Ночью и в выходные', 'без остановки смены'),
            ('lucide-shield-check', 'Лицензия', 'Роспотребнадзора'),
        ])),
    'dogovor-deratizatsiya-dezinsektsiya/index.html': dict(key='dogovor', root='../', related=['derat', 'dezins', 'prog', 'zhur'], strip=(
        'Коротко о договоре', [
            ('lucide-file-signature', 'Один договор', 'на дератизацию и дезинсекцию'),
            ('lucide-map-pinned', 'Несколько адресов', '— общий график'),
            ('lucide-scan-search', 'Бесплатный выезд', 'и расчёт до заключения'),
            ('lucide-activity', 'График визитов', 'по программе'),
            ('lucide-notebook-pen', 'Акт', 'после каждого выезда'),
            ('lucide-shield-check', 'Точки контроля', 'на схеме объекта'),
            ('lucide-file-badge', 'Документы', 'для Роспотребнадзора и аудитов'),
            ('lucide-crosshair', 'IPM', 'в основе программы'),
        ])),
    'pishchevoe-proizvodstvo/index.html': dict(key='food', root='../', related=['derat', 'dezins', 'prog', 'san'], strip=(
        'Коротко о пест-контроле на производстве', [
            ('lucide-crosshair', 'IPM', 'на пищевом производстве'),
            ('lucide-scan-search', 'Бесплатное обследование', 'производства'),
            ('lucide-activity', 'Визиты', 'по графику смен'),
            ('lucide-ban', 'Химия', '— только по результатам мониторинга'),
            ('lucide-map-pinned', 'Точки контроля', 'на плане цехов'),
            ('lucide-notebook-pen', 'Журнал и акты', 'для Роспотребнадзора'),
            ('lucide-file-badge', 'ХАССП', 'аудиты сертификации и сетей'),
            ('lucide-clock', 'Срочные выезды', '24/7'),
        ])),
    # своя бегущая строка — в tools/sklady/main.html
    'sklady-i-logistika/index.html': dict(key='sklady', root='../', related=['derat', 'dezins', 'dogovor', 'prog']),
    'magaziny-i-torgovye-seti/index.html': dict(key='seti', root='../', related=['derat', 'dezins', 'dogovor', 'zhur'], strip=(
        'Коротко о пест-контроле магазинов', [
            ('lucide-shopping-cart', 'Магазины и сети', 'Москва и область'),
            ('lucide-scan-search', 'Бесплатное обследование', 'магазина'),
            ('lucide-clock', 'Без остановки', 'работы магазина'),
            ('lucide-map-pinned', 'Точки контроля', 'на схеме каждого магазина'),
            ('lucide-notebook-pen', 'Журнал и акты', 'по каждому адресу'),
            ('lucide-chart-column', 'Сводный отчёт', 'по всей сети'),
            ('lucide-file-badge', 'СП 2.3.6.4281-26', 'и СанПиН 3.3686-21'),
            ('lucide-file-signature', 'Один договор', 'на все адреса'),
        ])),
    'gostinitsy/index.html': dict(key='hotel', root='../', related=['dezins', 'derat', 'dogovor', 'zhur'], strip=(
        'Коротко о пест-контроле гостиниц', [
            ('lucide-crosshair', 'IPM', 'для гостиниц и отелей'),
            ('lucide-scan-search', 'Бесплатное обследование', 'гостиницы'),
            ('lucide-bed-double', 'Номер и соседние', '— осмотр по сигналу'),
            ('lucide-clock', 'Выезд за 3 часа', '24/7'),
            ('lucide-lock', 'Без огласки', '— конфиденциальный выезд'),
            ('lucide-activity', 'Осмотры', 'не реже 2 раз в месяц'),
            ('lucide-notebook-pen', 'Журнал и акты', 'по проверочному листу'),
            ('lucide-ban', 'Без порошков', 'и ядов острого действия'),
        ])),
    'farmatsevticheskie-proizvodstva/index.html': dict(key='farma', root='../', related=['derat', 'dezins', 'prog', 'zhur'], strip=(
        'Коротко о пест-контроле на фармпроизводстве', [
            ('lucide-crosshair', 'IPM', 'по Правилам GMP ЕАЭС'),
            ('lucide-scan-search', 'Бесплатное обследование', 'площадки'),
            ('lucide-ban', 'Без яда', 'внутри здания'),
            ('lucide-shield-check', 'Шесть контуров', 'от периметра до чистых зон'),
            ('lucide-chart-line', 'Тренды', 'и уровни действия'),
            ('lucide-notebook-pen', 'Отчёты', 'для инспекции и аудита'),
            ('lucide-pill', 'ТЛФ, стерильные, АФС', 'и фитопрепараты'),
            ('lucide-clock', 'Выезд за 3 часа', 'по сигналу'),
        ])),
    'restorany-i-kafe/index.html': dict(key='rest', root='../', related=['dzr', 'drr', 'dogovor', 'zhur'], strip=(
        'Коротко о пест-контроле ресторанов', [
            ('lucide-clock', 'После закрытия', 'визиты ночью и до открытия'),
            ('lucide-map-pinned', 'Точки контроля', 'на кухне, в баре и на складе'),
            ('lucide-ban', 'Без распыления', 'там, где открытый продукт'),
            ('lucide-notebook-pen', 'Журнал и акт', 'после каждого визита'),
            ('lucide-file-badge', 'СанПиН 2.3/2.4.4282-26', 'и СанПиН 3.3686-21'),
            ('lucide-utensils', 'Рестораны, кафе, бары', 'столовые и фуд-корты'),
            ('lucide-scan-search', 'Бесплатное обследование', 'и расчёт'),
            ('lucide-shield-check', 'Сети', '— общий график и сводный отчёт'),
        ])),
    'materialy/index.html': dict(key='mat', root='../', related=['derat', 'dezins', 'dogovor', 'food'], strip=(
        'Документы и практика IPM', [
            ('lucide-file-signature', 'Программа', 'пест-контроля — образец и шаблон в PDF'),
            ('lucide-notebook-pen', 'Журнал', 'пест-контроля — 9 разделов'),
            ('lucide-activity', 'Пест-менеджмент', 'или разовая обработка'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и ТР ТС 021/2011'),
            ('lucide-shield-check', 'ГОСТ Р 54762-2011', '(FSSC 22000)'),
            ('lucide-map-pinned', 'Точки контроля', 'и план-схема'),
            ('lucide-scan-search', 'Аудиты', 'ХАССП и торговых сетей'),
            ('lucide-crosshair', 'IPM', 'для предприятий'),
        ])),
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html': dict(key='pm', root='../../', related=['prog', 'zhur', 'derat', 'dezins'], strip=(
        'Коротко о пест-менеджменте', [
            ('lucide-crosshair', 'IPM', 'вместо разовых обработок'),
            ('lucide-activity', 'Мониторинг', 'по пронумерованным точкам'),
            ('lucide-lock', 'Пути проникновения', 'закрываем, а не травим'),
            ('lucide-ban', 'Химия', '— по показаниям'),
            ('lucide-notebook-pen', 'Журнал и акты', 'для проверок'),
            ('lucide-scan-search', 'Бесплатное обследование', 'объекта'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и ХАССП'),
            ('lucide-map-pinned', 'Схема точек', 'на плане объекта'),
        ])),
    'materialy/programma-pest-kontrolya/index.html': dict(key='prog', root='../../', related=['zhur', 'pm', 'derat', 'dezins'], strip=(
        'Коротко о программе пест-контроля', [
            ('lucide-file-signature', 'Образец программы', '— PDF на 6 страниц'),
            ('lucide-notebook-pen', 'Шаблон', 'в PDF для заполнения'),
            ('lucide-crosshair', '7 разделов', 'программы'),
            ('lucide-activity', 'Пест-риск', 'по зонам объекта'),
            ('lucide-map-pinned', 'Точки контроля', 'на план-схеме'),
            ('lucide-shield-check', 'ПОПМ и ПРПО', 'в плане ХАССП'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и ТР ТС 021/2011'),
            ('lucide-scan-search', 'Разработка', 'под ваш объект'),
        ])),
    'materialy/zhurnal-pest-kontrolya/index.html': dict(key='zhur', root='../../', related=['prog', 'pm', 'derat', 'dezins'], strip=(
        'Коротко о журнале пест-контроля', [
            ('lucide-notebook-pen', '9 разделов', 'на 10 листах'),
            ('lucide-file-signature', 'Образец и шаблон', '— в PDF, лист в лист'),
            ('lucide-map-pinned', 'Реестр точек', 'контроля'),
            ('lucide-scan-search', 'Поточечный лист', 'осмотра ловушек'),
            ('lucide-activity', 'Учёт насекомых', 'и грызунов'),
            ('lucide-shield-check', 'Предписания', 'и сигнальный лист персонала'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', 'и ХАССП'),
            ('lucide-crosshair', 'ISO 22000', 'и FSSC 22000'),
        ])),
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html': dict(key='ppk', root='../../', related=['rppk', 'prog', 'food', 'dogovor'], strip=(
        'Коротко о программе производственного контроля', [
            ('lucide-file-signature', 'ППК', '— в произвольной форме, утверждает руководитель'),
            ('lucide-shield-check', 'Дезинсекция и дератизация', '— процедура ХАССП'),
            ('lucide-file-badge', 'ТР ТС 021/2011', 'ст. 10 и 11'),
            ('lucide-scan-search', 'Насекомые', '— обследования не реже 2 раз в месяц'),
            ('lucide-activity', 'Грызуны', '— ежемесячная оценка'),
            ('lucide-clipboard-check', 'С 1 сентября 2026', '— новые санитарные правила'),
            ('lucide-notebook-pen', 'Образец раздела', 'для ППК'),
            ('lucide-list-checks', 'Подтверждение', '— договор и акты'),
        ])),    # раздел «Нормативная база» (tools/normativnaya-baza): у хаба свой блок «Разборы и образцы» вместо «Смотрите также»
    'normativnaya-baza/index.html': dict(key='nb', root='../', strip=(
        'Коротко о нормативной базе', [
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— до 1 сентября 2027 года'),
            ('lucide-scan-search', 'Насекомые', '— обследования не реже 2 раз в месяц'),
            ('lucide-activity', 'Грызуны', '— ежемесячная оценка'),
            ('lucide-shield-check', 'Лицензия', '— с 1 марта 2025 года'),
            ('lucide-clipboard-check', 'Проверочные листы', '— приказы № 578 и № 580'),
            ('lucide-list-checks', 'Правила 2026 года', '— с 1 сентября'),
            ('lucide-ban', 'Отменённые документы', '— СП 3.5.3.3223-14 и другие'),
            ('lucide-notebook-pen', 'Образцы', 'программы, журнала и договора'),
        ])),
    'normativnaya-baza/proverochnye-listy/index.html': dict(key='pl', root='../../', related=['nb', 'san', 'zhur', 'dogovor'], strip=(
        'Коротко о проверочных листах', [
            ('lucide-clipboard-check', '37 форм', '— приказы № 578 и № 580'),
            ('lucide-list-checks', '20 форм', '— с вопросами о вредителях'),
            ('lucide-clock', 'С 4–5 октября', '2026 года'),
            ('lucide-scan-search', 'Обследования', '— не реже 2 раз в месяц'),
            ('lucide-activity', 'Грызуны', '— ежемесячная оценка'),
            ('lucide-shield-check', 'Исполнитель', '— организация с лицензией'),
            ('lucide-notebook-pen', 'Ответ', '— договор, акты, журнал'),
            ('lucide-search', 'Проверка шире листа', '— п. 2 приказов'),
        ])),
    'razrabotka-ppk/index.html': dict(key='rppk', root='../', related=['ppkobr', 'san', 'dogovor', 'nb'], strip=(
        'Коротко о разработке ППК', [
            ('lucide-file-badge', 'СП 1.1.1058-01', '— все 9 пунктов раздела 3'),
            ('lucide-calculator', 'ППК от 5 900 ₽', '— за 1 рабочий день'),
            ('lucide-list-checks', 'ППК по ХАССП', '— от 19 900 ₽ за 3 рабочих дня'),
            ('lucide-clipboard-check', 'Опросный лист', '— онлайн или в PDF'),
            ('lucide-flask-conical', 'План-график', '— лабораторных исследований'),
            ('lucide-clock', 'Правила 2026 года', '— в перечне норм программы'),
            ('lucide-notebook-pen', 'Приказ и журналы', '— в комплекте'),
            ('lucide-file-signature', 'Утверждает руководитель', '— без согласования с Роспотребнадзором'),
            ('lucide-shield-check', 'Дезинсекция и дератизация', '— пишет исполнитель с лицензией'),
        ])),
    # «Документы для Роспотребнадзора» (tools/normativnaya-baza/dokumenty.html), с 08.11.2026 — превью
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html': dict(key='dok', root='../../', related=['pl', 'prog', 'zhur', 'san'], strip=(
        'Коротко о документах для Роспотребнадзора', [
            ('lucide-list-checks', '41 документ', '— общий список для любого объекта'),
            ('lucide-factory', '15 видов объектов', '— свои дополнения'),
            ('lucide-notebook-pen', 'Кто готовит', '— у каждого документа'),
            ('lucide-clipboard-check', 'Конструктор', '— отметки «Есть», «Нет», «Не нужно»'),
            ('lucide-file-down', 'Чек-лист PDF', '— 14 страниц'),
            ('lucide-clock', '10 рабочих дней', '— при документарной проверке'),
            ('lucide-file-signature', 'Договоры и акты', '— по дезинсекции и дератизации'),
            ('lucide-shield-check', 'Сверка папки', '— бесплатно, дистанционно'),
        ])),
    # «Оценка эффективности дератизации и дезинсекции» (tools/normativnaya-baza/effektivnost.html), с 11.11.2026 — превью
    'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.html': dict(key='ef', root='../../', related=['nb', 'derat', 'dezins', 'san'], strip=(
        'Коротко об оценке эффективности', [
            ('lucide-clock', '1–2 дня', '— учёт после острых родентицидов'),
            ('lucide-chart-line', '10–30 дней', '— после антикоагулянтов'),
            ('lucide-scan-search', '10–14 дней', '— контроль по тараканам'),
            ('lucide-shield-check', '3 месяца без грызунов', '— критерий п. 116'),
            ('lucide-list-checks', 'Клеевые ловушки', '— 3–5 на 10 м²'),
            ('lucide-map-pinned', 'Пылевые площадки', '— 20×30 см'),
            ('lucide-notebook-pen', 'Учёт до и после', '— в журнале и акте'),
            ('lucide-ban', 'Нет эффекта', '— другая группа инсектицидов'),
        ])),
    # «Акт дератизации и дезинсекции» и «Схема точек пест-контроля» (tools/materialy-dokumenty), с 11.11.2026 — превью
    'materialy/akt-deratizatsii-i-dezinsektsii/index.html': dict(key='akt', root='../../', related=['zhur', 'skhema', 'dok', 'ef'], strip=(
        'Коротко об акте дератизации и дезинсекции', [
            ('lucide-clipboard-check', 'Акт', '— по каждому визиту'),
            ('lucide-clock', 'Не реже 2 раз в месяц', '— на объектах из п. 98'),
            ('lucide-file-badge', 'Средства', '— с номером СГР'),
            ('lucide-map-pinned', 'Результаты', '— по точкам контроля'),
            ('lucide-file-signature', 'Подписи', '— исполнитель и заказчик'),
            ('lucide-notebook-pen', 'Номер акта', '— в журнале'),
            ('lucide-file-down', 'Образец и бланк', '— в PDF'),
            ('lucide-shield-check', '5 лет', '— срок хранения'),
        ])),
    'materialy/skhema-tochek-pest-kontrolya/index.html': dict(key='skhema', root='../../', related=['zhur', 'akt', 'prog', 'derat'], strip=(
        'Коротко о схеме точек пест-контроля', [
            ('lucide-map-pinned', '3 контура', '— территория, периметр, помещения'),
            ('lucide-crosshair', '30 точек', '— в образце на 1 850 м²'),
            ('lucide-list-checks', 'Нумерация', '— КИК-01, МЛ-10, ИМ-03'),
            ('lucide-notebook-pen', 'Реестр', '— место и порог каждой точки'),
            ('lucide-file-badge', 'ГОСТ Р 54762-2011', '— п. 12.5'),
            ('lucide-scan-search', 'Сверка', '— схема, указатель, журнал'),
            ('lucide-file-signature', 'Новая редакция', '— при каждом переносе'),
            ('lucide-file-down', 'Образец', '— PDF на 2 листа'),
        ])),
    # «Лабораторные исследования» (tools/laboratornye-issledovaniya), с 10.11.2026 — превью
    'laboratornye-issledovaniya/index.html': dict(key='lab', root='../', related=['san', 'rppk', 'dok', 'vent'], strip=(
        'Коротко о лабораторных исследованиях', [
            ('lucide-flask-conical', 'Своя лаборатория', '— 14 направлений'),
            ('lucide-calculator', 'Лабораторный контроль по ППК', '— от 2\u00a0600\u00a0₽'),
            ('lucide-scan-search', 'Смывы', '— от 310\u00a0₽ за точку'),
            ('lucide-list-checks', 'Прайс и расчёт', '— онлайн'),
            ('lucide-map-pinned', 'Отбор проб', '— на вашем объекте'),
            ('lucide-file-badge', 'Протоколы', '— для папки к проверке'),
            ('lucide-clipboard-check', 'По плану ППК', '— СП 1.1.1058-01'),
            ('lucide-factory', 'Наборы', '— по видам объектов'),
        ])),
    # страницы направлений и статьи раздела «Лабораторные исследования» (build_subpages.py), с 11.11.2026
    'laboratornye-issledovaniya/analiz-smyvov/index.html': dict(key='lab-smyvy', root='../../', related=['mat-smyvy', 'lab', 'dezinf', 'san'], strip=(
        'Коротко об анализе смывов', [
            ('lucide-flask-conical', 'Анализ смывов', '— от 310\u00a0₽ за точку'),
            ('lucide-file-badge', 'МР 4.2.0220-20', '— порядок отбора'),
            ('lucide-scan-search', 'БГКП, S. aureus, ОМЧ', '— основные показатели'),
            ('lucide-map-pinned', 'Отбор на объекте', '— специалист лаборатории'),
            ('lucide-clock', 'Доставка', '— не позднее 6 часов'),
            ('lucide-utensils', 'Общепит и производства', '— по плану ХАССП'),
            ('lucide-clipboard-check', 'По плану ППК', '— точки и кратность'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/izmerenie-mikroklimata/index.html': dict(key='lab-mikroklimat', root='../../', related=['mat-zamery', 'lab-svet', 'lab', 'vent'], strip=(
        'Коротко об измерении микроклимата', [
            ('lucide-activity', 'Микроклимат', '— от 350\u00a0₽ за точку'),
            ('lucide-file-badge', 'МУК 4.3.4120-25', '— методика замеров'),
            ('lucide-clock', 'Не реже 1 раза в год', '— п. 15 СП 2.2.4285-26'),
            ('lucide-list-checks', 'Нормы СанПиН 1.2.3685-21', '— по категориям работ'),
            ('lucide-map-pinned', 'Замеры на рабочих местах', '— на нужных высотах'),
            ('lucide-factory', 'Офисы, цеха, склады', '— кухни и салоны'),
            ('lucide-clipboard-check', 'По плану ППК', '— условия труда'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.html': dict(key='lab-svet', root='../../', related=['mat-zamery', 'lab-mikroklimat', 'lab', 'rppk'], strip=(
        'Коротко о замере освещённости', [
            ('lucide-lightbulb', 'Освещённость', '— от 350\u00a0₽ за точку'),
            ('lucide-file-badge', 'ГОСТ 24940-2016', '— методы измерения'),
            ('lucide-badge-check', 'Поверенный люксметр', '— погрешность до 10\u00a0%'),
            ('lucide-clock', 'Вечером', '— или при зашторенных окнах'),
            ('lucide-list-checks', '300\u00a0лк в офисе', '— при общем освещении'),
            ('lucide-map-pinned', 'План точек', '— под светильниками и между ними'),
            ('lucide-clipboard-check', 'По плану ППК', '— условия труда'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/index.html': dict(key='lab-vrz', root='../../', related=['lab-mikroklimat', 'lab', 'vent', 'rppk'], strip=(
        'Коротко об анализе воздуха рабочей зоны', [
            ('lucide-flask-conical', 'Воздух рабочей зоны', '— от 600\u00a0₽ за вещество'),
            ('lucide-file-badge', 'ГОСТ 12.1.005-88', '— порядок контроля'),
            ('lucide-crosshair', 'Зона дыхания', '— пробы у рабочего места'),
            ('lucide-list-checks', 'ПДК', '— СанПиН 1.2.3685-21'),
            ('lucide-clock', 'Периодичность', '— по классу опасности'),
            ('lucide-factory', 'Цеха и склады', '— лаборатории, автосервисы'),
            ('lucide-clipboard-check', 'По плану ППК', '— пп. 13–14 СП 2.2.4285-26'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.html': dict(key='lab-pishcha', root='../../', related=['lab-smyvy', 'lab', 'rppk', 'ppk'], strip=(
        'Коротко об анализе пищевых продуктов', [
            ('lucide-utensils', 'Пищевые продукты', '— химия от 194\u00a0₽ за показатель'),
            ('lucide-flask-conical', 'Микробиология', '— от 690\u00a0₽'),
            ('lucide-file-badge', 'ТР ТС 021/2011', '— нормативы по группам'),
            ('lucide-chart-column', 'Пищевая ценность', '— от 980\u00a0₽'),
            ('lucide-shield-check', 'ХАССП', '— п. 4 СанПиН 2.3/2.4.4282-26'),
            ('lucide-map-pinned', 'Отбор проб', '— на вашем объекте'),
            ('lucide-factory', 'Общепит и производства', '— школы, больницы'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/analiz-vody/index.html': dict(key='lab-voda', root='../../', related=['lab-smyvy', 'lab', 'rppk', 'dok'], strip=(
        'Коротко об анализе воды', [
            ('lucide-flask-conical', 'Химия воды', '— от 737\u00a0₽ за показатель'),
            ('lucide-activity', 'Микробиология', '— от 2\u00a0350\u00a0₽'),
            ('lucide-file-badge', 'СанПиН 1.2.3685-21', '— нормативы питьевой воды'),
            ('lucide-map-pinned', 'Скважина', '— 4 раза в год по сезонам'),
            ('lucide-shield-check', 'Бассейн', '— прил. 6 СП 2.1.4284-26'),
            ('lucide-badge-check', 'Отбор проб', '— по ГОСТ 31942-2012'),
            ('lucide-factory', 'Общепит, производства', '— гостиницы'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.html': dict(key='lab-steril', root='../../', related=['mat-steril', 'lab-smyvy', 'lab', 'dezinf'], strip=(
        'Коротко о контроле стерилизаторов', [
            ('lucide-shield-check', 'Стерилизатор', '— от 1\u00a0600\u00a0₽'),
            ('lucide-flask-conical', 'Биологические индикаторы', '— под ваши режимы'),
            ('lucide-clock', 'Не реже 2 раз в год', '— и после ремонта'),
            ('lucide-scan-search', 'Анализ на стерильность', '— от 1\u00a0003\u00a0₽ за точку'),
            ('lucide-lightbulb', 'Облучатели', '— эффективность от 1\u00a0600\u00a0₽'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— п. 125'),
            ('lucide-pill', 'Салоны, клиники', '— стоматологии'),
            ('lucide-notebook-pen', 'Протоколы', '— для папки к проверке'),
        ])),
    'materialy/kak-berut-smyvy/index.html': dict(key='mat-smyvy', root='../../', related=['lab-smyvy', 'lab', 'dezinf', 'rppk'], strip=(
        'Коротко о том, как берут смывы', [
            ('lucide-file-badge', 'МР 4.2.0220-20', '— простыми словами'),
            ('lucide-clock', 'До работы', '— или после обработки'),
            ('lucide-map-pinned', '10×10 см', '— площадь смыва'),
            ('lucide-crosshair', 'Руки', '— ладони не менее 5 раз'),
            ('lucide-clock', '6 часов', '— на доставку'),
            ('lucide-scan-search', 'БГКП и стафилококк', '— что означает находка'),
            ('lucide-ban', 'Ошибки', '— из-за которых результат ложный'),
            ('lucide-flask-conical', 'Анализ смывов', '— от 310\u00a0₽ за точку'),
        ])),
    'materialy/zamer-osveshchennosti-i-mikroklimata/index.html': dict(key='mat-zamery', root='../../', related=['lab-mikroklimat', 'lab-svet', 'lab', 'rppk'], strip=(
        'Коротко о замерах на рабочих местах', [
            ('lucide-clock', 'Микроклимат', '— не реже 1 раза в год'),
            ('lucide-lightbulb', 'Освещённость', '— по программе ППК'),
            ('lucide-file-badge', 'СП 2.2.4285-26', '— пп. 10–15'),
            ('lucide-list-checks', 'Чек-лист', '— подготовки к замерам'),
            ('lucide-map-pinned', 'До 100\u00a0м²', '— 4 участка микроклимата'),
            ('lucide-scan-search', 'Спецоценка', '— зачёт за 6 месяцев'),
            ('lucide-notebook-pen', 'Протокол', '— что в нём будет'),
            ('lucide-flask-conical', 'Замеры', '— от 350\u00a0₽ за точку'),
        ])),
    'materialy/kontrol-raboty-sterilizatorov/index.html': dict(key='mat-steril', root='../../', related=['lab-steril', 'lab', 'dezinf', 'san'], strip=(
        'Коротко о контроле стерилизаторов', [
            ('lucide-list-checks', 'Три метода', '— физический, химический, бактериологический'),
            ('lucide-clock', 'Не реже 2 раз в год', '— бактериологический контроль'),
            ('lucide-notebook-pen', 'Записи', '— по каждому циклу'),
            ('lucide-lock', 'Упаковка', '— с датой стерилизации'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— п. 125'),
            ('lucide-shield-check', 'СП 2.1.4284-26', '— п. 99.38'),
            ('lucide-ban', 'Ошибки', '— и что делать при росте'),
            ('lucide-flask-conical', 'Контроль стерилизатора', '— от 1\u00a0600\u00a0₽'),
        ])),
    # «Дератизация и дезинсекция для организаций» (tools/deratizatsiya-i-dezinsektsiya), с 11.11.2026
    'deratizatsiya-i-dezinsektsiya/index.html': dict(key='dd', root='../', related=['derat', 'dezins', 'dogovor', 'san'], strip=(
        'Коротко о дератизации и дезинсекции', [
            ('lucide-file-signature', 'Один договор', '— грызуны и насекомые'),
            ('lucide-calculator', 'Комплекс', '— от 4\u00a0900\u00a0₽/мес'),
            ('lucide-scan-search', 'Бесплатный выезд', 'и расчёт'),
            ('lucide-activity', 'Общий график', 'визитов на год'),
            ('lucide-notebook-pen', 'Журнал и акт', 'после каждого визита'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— пп. 101 и 110'),
            ('lucide-shield-check', 'Лицензия', 'Роспотребнадзора'),
            ('lucide-list-checks', 'Документы', 'для отдела закупок'),
        ])),
    # страницы «услуга + сфера» для общепита (tools/restorany-uslugi/build_pages.py), с 11.11.2026
    'dezinsektsiya/restorany-i-kafe/index.html': dict(key='dzr', root='../../', related=['rest', 'drr', 'dezins', 'zhur'], strip=(
        'Коротко о дезинсекции общепита', [
            ('lucide-clock', 'Ночью и в выходные', '— без наценки'),
            ('lucide-utensils', 'Гели', '— кухня не останавливается'),
            ('lucide-map-pinned', 'Мониторы', 'на схеме точек'),
            ('lucide-ban', 'Без распыления', 'при гостях и персонале'),
            ('lucide-notebook-pen', 'Акт и журнал', 'после каждого визита'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— пп. 98 и 101'),
            ('lucide-shield-check', 'Лицензия', 'Роспотребнадзора'),
            ('lucide-calculator', 'От 3\u00a0500\u00a0₽', '— обследование бесплатно'),
        ])),
    'deratizatsiya/restorany-i-kafe/index.html': dict(key='drr', root='../../', related=['rest', 'dzr', 'derat', 'zhur'], strip=(
        'Коротко о дератизации ресторанов', [
            ('lucide-ban', 'Без яда', 'на кухне и у продуктов'),
            ('lucide-lock', 'Станции на ключ', 'снаружи и в подвале'),
            ('lucide-map-pinned', 'Точки с номерами', 'на схеме'),
            ('lucide-door-open', 'Пути захода', '— список для техслужбы'),
            ('lucide-notebook-pen', 'Журнал и карта', 'по каждой точке'),
            ('lucide-file-badge', 'СанПиН 3.3686-21', '— пп. 110 и 111'),
            ('lucide-clock', 'Выезд за 3 часа', 'по договору'),
            ('lucide-calculator', 'От 3\u00a0500\u00a0₽/мес', '— обследование бесплатно'),
        ])),
    'sanitarnyy-audit/index.html': dict(key='san', root='../', related=['derat', 'dezins', 'prog', 'zhur'], strip=(
        'Коротко о санитарном аудите', [
            ('lucide-clipboard-check', 'Проверочные листы', '— приказы № 578 и № 580'),
            ('lucide-file-badge', 'СанПиН 2026', '— нормы с 1 сентября 2026'),
            ('lucide-flask-conical', 'Смывы и пробы воздуха', '— в стоимости'),
            ('lucide-notebook-pen', 'Реестр нарушений', '— с фото и пунктом нормы'),
            ('lucide-clock', 'Выезд 2–6 часов', '— акт через 3 рабочих дня'),
            ('lucide-crosshair', 'Пест-контроль', '— проверяем глубже всего'),
            ('lucide-shield-check', 'Лицензия', '№ Л064-00111-77/01942445'),
            ('lucide-lock', 'Конфиденциально', '— результат только у заказчика'),
        ])),
}


def strip_html(label, items):
    def one(it):
        ico, b, rest = it
        return f'<div class="strip-item">{ICONS[ico]}<b>{tp(b)}</b> {tp(rest)}</div>'
    row = '\n      '.join(one(it) for it in items)
    return (
        f'\n<div class="strip" role="group" aria-label="{label}">\n'
        '  <div class="strip-track" id="stripTrack">\n'
        f'    <div class="strip-set">\n      {row}\n    </div>\n'
        f'    <div class="strip-set" aria-hidden="true">\n      {row}\n    </div>\n'
        '  </div>\n</div>\n'
    )


def related_html(root, keys):
    cards = []
    for k in keys:
        kind, title, desc = CARD[k]
        cards.append(
            f'      <a class="card rel-card" href="{root}{URL[k]}">'
            f'<span class="rel-k">{kind}</span><span class="rel-t">{tp(title)}</span>'
            f'<span class="rel-d">{tp(desc)}</span><span class="rel-a" aria-hidden="true">{ARR}</span></a>')
    return (
        '\n<!-- ============ СМОТРИТЕ ТАКЖЕ (перелинковка) ============ -->\n'
        '<section class="s s-rel" id="smotrite-takzhe">\n'
        '  <div class="wrap">\n'
        '    <div class="head">\n'
        '      <div class="eyebrow" data-eyebrow>Смотрите также</div>\n'
        '      <h2 data-split>Связанные услуги <em>и материалы</em></h2>\n'
        '    </div>\n'
        '    <div class="rel-grid" data-group="cards">\n' + '\n'.join(cards) + '\n'
        '    </div>\n'
        '  </div>\n'
        '</section>\n'
    )


def more_html(label, links):
    a = ''.join(f'<a href="{href}"><span>{tp(text)}</span>{ARR}</a>' for href, text in links)
    return f'\n    <nav class="more" aria-label="{label}" data-fade><span class="more-k">{label}</span>{a}</nav>'


# ---------------------------------------------------------------- разметка анимаций
BLOCK = {'div', 'p', 'ul', 'ol', 'table', 'figure', 'article', 'aside', 'details', 'blockquote', 'dl', 'h3', 'h4', 'nav', 'section'}
ANIM_ATTRS = ('data-group', 'data-fade', 'data-split', 'data-eyebrow', 'data-form', 'data-h', 'data-scrub')
GROUP_BY_CLASS = [('faq-col', 'faq'), ('cta-list', 'ctalist'), ('pests', 'pests'),
                  ('inds', 'inds'), ('tasks', 'tasks'), ('docs', 'docs'), ('kpis', 'kpis')]  # блоки как на главной — их анимации
STEP_CLASSES = ('d-steps', 'steps', 'f-steps', 'p-steps', 'd-terms', 'f-rules', 'p-fill-steps', 'f-zlist')  # нумерованные шаги — выезжают слева
LIST_CLASSES = ('d-ticks', 'p-legend', 'd-chips')  # списки с отметками — по пунктам, как список в блоке заявки
NO_FADE = ('tl', 'cycle', 'strip')  # у этих блоков своя анимация (этапы, цикл IPM, бегущая строка)
CARDLIKE = ('p-sec', 'f-req', 'pm-scen', 'p-duty-box', 'd-obj', 'ind', 'pest')


def is_cardlike(c):
    return c.tag == 'article' or any('card' in k for k in c.classes) or c.has_class(*CARDLIKE)


def is_anim(n):
    return any(a in n.attrs for a in ANIM_ATTRS)


def has_anim_desc(n):
    return any(is_anim(d) for d in n.iter())


def in_group(n):
    return any('data-group' in a.attrs for a in n.ancestors())


def el_children(n):
    return [c for c in n.children if c.tag not in ('#root',)]


def mark_fades(ed, node, depth=0):
    """Блоки без своих анимаций плавно проявляются; в контейнеры с анимированными потомками — спускаемся глубже."""
    for c in el_children(node):
        if c.tag not in BLOCK or 'hidden' in c.attrs or c.attrs.get('aria-hidden') == 'true':
            continue
        if c.has_class('eyebrow', 'sr-only', 'head', *NO_FADE) or c.tag == 'form' or c.has_class('form'):
            continue
        if is_anim(c):
            continue
        if has_anim_desc(c):
            if depth < 4:
                mark_fades(ed, c, depth + 1)
            continue
        ed.add_attr(c, 'data-fade')


def mark_section(ed, sec):
    nodes = list(sec.iter())
    for n in nodes:
        if n.has_class('eyebrow') and not in_group(n):
            ed.add_attr(n, 'data-eyebrow')
        if n.tag == 'h2' and not n.has_class('p-sec-h', 'sr-only') and not n.closest(lambda a: a.has_class('qa', 'card', 'form')):
            ed.add_attr(n, 'data-split')
    # группы карточек
    for n in nodes:
        if is_anim(n) or in_group(n) or n.closest(lambda a: a.tag == 'form'):
            continue
        name = next((g for cls, g in GROUP_BY_CLASS if n.has_class(cls)), None)
        if not name and n.tag in ('ol', 'ul') and n.has_class(*STEP_CLASSES):
            name = 'steps'
        if not name and n.tag == 'ul' and n.has_class(*LIST_CLASSES) and len(el_children(n)) >= 2:
            name = 'ctalist'
        if not name:
            kids = [c for c in el_children(n) if c.tag not in ('script', 'style')]
            if len(kids) >= 2 and all(is_cardlike(c) for c in kids):
                name = 'cards'
        if name:
            ed.add_attr(n, 'data-group', name)
            if name in ('cards', 'inds'):
                for c in el_children(n):
                    if any(d.has_class('ind-img', 'd-obj-img', 'd-kind-img') for d in c.iter()) and 'data-tilt' not in c.attrs:
                        ed.add_attr(c, 'data-tilt')
    # подзаголовки в шапке блока
    for n in nodes:
        if n.has_class('head'):
            for c in n.iter():
                if c.tag == 'p' and not is_anim(c) and not in_group(c):
                    ed.add_attr(c, 'data-fade')
    # панели самопроверки целиком
    for n in nodes:
        if n.has_class('panel') and not is_anim(n) and not in_group(n):
            ed.add_attr(n, 'data-fade')
    wrap = next((c for c in el_children(sec) if c.has_class('wrap')), sec)
    mark_fades(ed, wrap)


def mark_hero(ed, hero):
    for n in hero.iter():
        if n.tag == 'nav' and n.has_class('d-crumbs', 'f-crumbs'):
            ed.add_attr(n, 'data-h')
        elif n.has_class('badge', 'sub', 'p-def', 'lead', 'p-hero-note', 'p-files', 'f-urgent', 'p-stack-cap', 'p-toc', 'd-btns', 'hero-ctas') \
                and not in_group(n) and not n.closest(lambda a: a.has_class('p-secs', 'p-stack')):
            ed.add_attr(n, 'data-h')
        elif n.tag == 'li' and n.parent is not None and n.parent.has_class('d-ticks'):
            ed.add_attr(n, 'data-h')
    for n in hero.iter():
        if n.tag == 'a' and n.has_class('btn') and n.parent is not None and n.parent.has_class('d-btns', 'hero-ctas'):
            ed.add_attr(n, 'data-magnet')
        if n.has_class('p-secs') and 'data-group' not in n.attrs:
            ed.add_attr(n, 'data-group', 'cards')


# ---------------------------------------------------------------- правки страниц
def fix_head(s, root):
    s, n = HEAD_SCRIPT_RE.subn(lambda m: HEAD_SCRIPT, s, count=1)
    assert n == 1, 'нет раннего скрипта в <head>'
    s = re.sub(r'(href="(?:\.\./)*style\.css)\?v=[^"]*"', rf'\1?v={VERSION}"', s)
    s = re.sub(r'(src="(?:\.\./)*app\.min\.js)\?v=[^"]*"', rf'\1?v={VERSION}"', s)
    # Страница уже на загрузчике (setTimeout(go, 0)) без GSAP, ScrollTrigger и Lenis — так задумано: с 08.11.2026
    # «Документы для Роспотребнадзора» (tools/normativnaya-baza/build_pages.py, p['dok']) грузят только app.min.js.
    # Библиотеки добавляются лишь страницам, где ещё стоят defer-подключения.
    if 'vendor/gsap.min.js' not in s and 'setTimeout(go, 0)' not in s:
        s, n = re.subn(r'(<script src="(?:\.\./)*app\.min\.js\?v=[^"]*" defer></script>)',
                       lambda m: (f'<script src="{root}vendor/gsap.min.js" defer></script>\n'
                                  f'<script src="{root}vendor/ScrollTrigger.min.js" defer></script>\n'
                                  f'<script src="{root}vendor/lenis.min.js" defer></script>\n' + m.group(1)), s, count=1)
        assert n == 1, 'нет подключения app.min.js'
    return use_loader(s)


def use_loader(s):
    """defer-подключение GSAP, ScrollTrigger, Lenis и app.min.js → загрузчик после первой отрисовки (LOADER)"""
    if 'setTimeout(go, 0)' not in s:
        s, n = SCRIPTS_RE.subn(lambda m: LOADER.replace('{root}', m.group(1)).replace('{version}', VERSION), s, count=1)
        assert n == 1, 'нет подключения скриптов анимаций'
    s = re.sub(r"('(?:\.\./)*app\.min\.js\?v=)[^']*'", rf"\g<1>{VERSION}'", s)
    return s


def fix_body_start(s):
    if 'id="intro"' not in s:
        s, n = re.subn(r'(<a class="skip" href="#main">[^<]*</a>\n)', lambda m: m.group(1) + '\n' + INTRO, s, count=1)
        assert n == 1
    if 'class="cursor"' not in s:
        s, n = re.subn(r'(<div class="progress" aria-hidden="true"><i id="progress"></i></div>\n)', lambda m: m.group(1) + CURSOR + GRAIN, s, count=1)
        assert n == 1
    return s


SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
MAT_LD = '<script type="application/ld+json">' + json.dumps({
    '@context': 'https://schema.org',
    '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Материалы', 'item': SITE + 'materialy/'}]},
        {'@type': 'CollectionPage', 'name': 'Материалы о пест-контроле для предприятий', 'url': SITE + 'materialy/', 'inLanguage': 'ru-RU',
         'description': 'Практические руководства и образцы документов по системе IPM и ХАССП для предприятий Москвы и области: программа пест-контроля, журнал пест-контроля, схема точек пест-контроля, акт дератизации и дезинсекции, пест-менеджмент или разовая обработка, образец программы производственного контроля по ХАССП (PDF) и её раздел пест-контроля, нормативная база дезинсекции и дератизации, разбор проверочных листов Роспотребнадзора 2026 года, перечень документов для Роспотребнадзора, а также порядок лабораторного контроля: как берут смывы, как проходят замеры освещённости и микроклимата, как контролируют работу стерилизаторов, как оценивают эффективность дератизации и дезинсекции.',
         'isPartOf': {'@type': 'WebSite', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': SITE},
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [
             {'@type': 'ListItem', 'position': 1, 'url': SITE + 'materialy/programma-pest-kontrolya/', 'name': 'Программа пест-контроля на предприятии: образец и шаблон в PDF, пример заполнения'},
             {'@type': 'ListItem', 'position': 2, 'url': SITE + 'materialy/pest-menedzhment-ili-razovaya-obrabotka/', 'name': 'Пест-менеджмент или разовая обработка'},
             {'@type': 'ListItem', 'position': 3, 'url': SITE + 'materialy/zhurnal-pest-kontrolya/', 'name': 'Журнал пест-контроля: образец заполнения, бланк и шаблон'},
             {'@type': 'ListItem', 'position': 4, 'url': SITE + 'materialy/programma-proizvodstvennogo-kontrolya-haccp/', 'name': 'Программа производственного контроля по ХАССП: образец и раздел пест-контроля'},
             {'@type': 'ListItem', 'position': 5, 'url': SITE + 'normativnaya-baza/', 'name': 'Нормативная база: СанПиН и требования к дезинсекции и дератизации'},
             {'@type': 'ListItem', 'position': 6, 'url': SITE + 'normativnaya-baza/proverochnye-listy/', 'name': 'Проверочные листы Роспотребнадзора 2026: вопросы о дезинсекции и дератизации'},
             {'@type': 'ListItem', 'position': 7, 'url': SITE + 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', 'name': 'Документы для Роспотребнадзора: полный перечень для проверки'},
             {'@type': 'ListItem', 'position': 8, 'url': SITE + 'materialy/kak-berut-smyvy/', 'name': 'Как берут смывы с поверхностей и рук: порядок по МР 4.2.0220-20'},
             {'@type': 'ListItem', 'position': 9, 'url': SITE + 'materialy/zamer-osveshchennosti-i-mikroklimata/', 'name': 'Как проходит замер освещённости и микроклимата на рабочих местах'},
             {'@type': 'ListItem', 'position': 10, 'url': SITE + 'materialy/kontrol-raboty-sterilizatorov/', 'name': 'Контроль работы стерилизаторов: методы, периодичность, журнал'},
             # с 11.11.2026 (tools/materialy-dokumenty)
             {'@type': 'ListItem', 'position': 11, 'url': SITE + 'materialy/skhema-tochek-pest-kontrolya/', 'name': 'Схема точек пест-контроля: образец и правила'},
             {'@type': 'ListItem', 'position': 12, 'url': SITE + 'materialy/akt-deratizatsii-i-dezinsektsii/', 'name': 'Акт дератизации и дезинсекции: образец и что в нём указать'},
             {'@type': 'ListItem', 'position': 13, 'url': SITE + 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/', 'name': 'Оценка эффективности дератизации и дезинсекции: сроки и критерии'}]},
         'publisher': {'@type': 'Organization', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': SITE, 'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru'}},
    ]}, ensure_ascii=False) + '</script>'


HOTEL_LINKS = {  # карточки гостиниц на страницах услуг ведут на отраслевую страницу (раньше — к блоку «Отрасли» на главной)
    'dezinsektsiya/index.html': ('<h3><a href="../#otrasli">Гостиницы, отели и&nbsp;общежития</a></h3>', '<h3><a href="../gostinitsy/">Гостиницы, отели и&nbsp;общежития</a></h3>'),
    'dogovor-deratizatsiya-dezinsektsiya/index.html': ('<h3><a href="../#otrasli">Гостиницы</a></h3>', '<h3><a href="../gostinitsy/">Гостиницы</a></h3>'),
}


SAN_REL = ('deratizatsiya/index.html', 'dezinsektsiya/index.html', 'pishchevoe-proizvodstvo/index.html')
# с 11.11.2026 у дератизации и дезинсекции первая карточка «Смотрите также» — комплекс «Дератизация и дезинсекция»
# (вместо «Программы пест-контроля»): уже собранный блок пересобирается по related страницы
DD_REL = ('deratizatsiya/index.html', 'dezinsektsiya/index.html')

# ссылка «Для проверки → Полный перечень документов для Роспотребнадзора» в конце блока документов (id="dokumenty");
# с отраслевых страниц — с параметром ?obekt=: конструктор на странице документов откроется с этим видом объекта
DOK_LINKS = {
    'pishchevoe-proizvodstvo/index.html': 'pishchevoe-proizvodstvo', 'restorany-i-kafe/index.html': 'restorany',
    'magaziny-i-torgovye-seti/index.html': 'magaziny', 'sklady-i-logistika/index.html': 'sklady',
    'farmatsevticheskie-proizvodstva/index.html': 'farmproizvodstvo', 'gostinitsy/index.html': 'gostinitsy',
    'dezinfektsiya/index.html': '', 'ochistka-dezinfektsiya-ventilyatsii/index.html': '',
}


def dok_link(rel, s, root):
    if rel not in DOK_LINKS or 'data-more="dok"' in s:
        return s
    q = DOK_LINKS[rel]
    href = root + URL['dok'] + (f'?obekt={q}' if q else '')
    html = more_html('Для проверки', [(href, 'Полный перечень документов для Роспотребнадзора')])
    html = html.replace('<nav class="more"', '<nav class="more" data-more="dok"', 1)
    i = s.find('id="dokumenty"')
    assert i > 0, rel + ': нет блока документов'
    j = s.find('\n</section>', i)
    k = s.rfind('\n  </div>', i, j)  # закрытие .wrap
    assert k > i, rel + ': нет .wrap в блоке документов'
    return s[:k] + html + s[k:]


def rel_card(root, k):
    kind, title, desc = CARD[k]
    return (f'<a class="card rel-card" href="{root}{URL[k]}">'
            f'<span class="rel-k">{kind}</span><span class="rel-t">{tp(title)}</span>'
            f'<span class="rel-d">{tp(desc)}</span><span class="rel-a" aria-hidden="true">{ARR}</span></a>')


def dd_related(rel, s):
    """Карточки уже собранного «Смотрите также» — как в related страницы (DD_REL); повторный запуск ничего не меняет."""
    if rel not in DD_REL or 'id="smotrite-takzhe"' not in s:
        return s
    i = s.index('id="smotrite-takzhe"')
    j = s.index('</section>', i)
    if f'href="../{URL["dd"]}"' in s[i:j]:
        return s
    a = s.index('<div class="rel-grid" data-group="cards">\n', i, j) + len('<div class="rel-grid" data-group="cards">\n')
    b = s.index('\n    </div>\n  </div>\n', a, j)
    assert s[a:b].count('<a class="card rel-card"') == 4, rel + ': в «Смотрите также» не 4 карточки'
    cards = '\n'.join('      ' + rel_card('../', k) for k in PAGES[rel]['related'])
    return s[:a] + cards + s[b:]


def page_specific(rel, s):
    if rel in SAN_REL and 'id="smotrite-takzhe"' in s and 'class="card rel-card" href="../sanitarnyy-audit/"' not in s:
        # «Смотрите также» уже собран: карточку журнала меняем на санитарный аудит (как в related у страницы)
        i = s.index('id="smotrite-takzhe"')
        j = s.index('</section>', i)
        block, n = re.subn(r'<a class="card rel-card" href="\.\./materialy/zhurnal-pest-kontrolya/">.*?</a>',
                           lambda m: rel_card('../', 'san'), s[i:j], count=1, flags=re.S)
        assert n == 1, rel + ': нет карточки журнала в «Смотрите также»'
        s = s[:i] + block + s[j:]
    if rel in HOTEL_LINKS:
        old, new = HOTEL_LINKS[rel]
        if new not in s:
            assert old in s, rel + ': нет карточки гостиниц'
            s = s.replace(old, new, 1)
    if rel == 'deratizatsiya/index.html':
        # Новая услуга раскрывается отдельно; шапка, формы и существующие блоки не меняются.
        s = re.sub(r'\n<div class="wrap" id="proof-service-link">.*?</div>\n', '\n', s, count=1, flags=re.S)
        if 'id="proof-service-link"' not in s:
            link = (
                ' <span id="proof-service-link">Инженерные работы можно обсудить отдельно: '
                '<a href="../zashchita-ot-proniknoveniya-gryzunov/" style="color:var(--acc);text-decoration:underline;text-underline-offset:4px">'
                'защита от проникновения грызунов</a>.</span>')
            s, n = re.subn(
                r'(<h3>Предписания по[\s\u00a0]+грызунонепроницаемости здания</h3><p>.*?)(</p>)',
                lambda m: m[1] + link + m[2], s, count=1, flags=re.S)
            assert n == 1, 'дератизация: не найден абзац об инженерном барьере'
        # переключатель вариантов фото первого экрана был нужен только для выбора — в сайте оставляем вариант 1
        s = re.sub(r'\n\s*<div class="hero-vbar".*?</div>\n', '\n', s, count=1, flags=re.S)
        s = re.sub(r'\n?/\* Переключатель 4 вариантов Hero-фото \*/\n\(function\(\)\{\n  var img=document\.getElementById\(\'hero-img\'\).*?\n\}\)\(\);', '', s, count=1, flags=re.S)
        s = re.sub(r'\n?/\* Переключатель 4 вариантов Hero-фото \*/\n(?:\.hero-v[^\n]*\n)+', '\n', s, count=1)
        s = re.sub(r'\n\s*\.hero-vbar\{order:3;[^}]*\}', '', s)
        # «Услуги» в цепочке вели на эту же страницу; отдельной страницы услуг нет — цепочка как у остальных услуг
        s = s.replace('<a href="../">Главная</a><span aria-hidden="true">→</span><a href="./">Услуги</a><span aria-hidden="true">→</span>',
                      '<a href="../">Главная</a><span aria-hidden="true">→</span>')
    if rel == 'dezinsektsiya/index.html':
        # перелинковка: дезинфекция вентиляции — отдельная страница услуги
        if 'href="../ochistka-dezinfektsiya-ventilyatsii/" style' not in s:
            s = s.replace('поверхностях пищеблоков, в системах вентиляции, холодильных',
                          'поверхностях пищеблоков, <a href="../ochistka-dezinfektsiya-ventilyatsii/" style="color:inherit;border-bottom:1px solid var(--line2)">в системах вентиляции</a>, холодильных')
        # номер МР уточнён на странице журнала: «МР 3.5.2.0373-25» не существует (0373-25 — МР 1.2 о косметике);
        # для дезинсекции основа — СанПиН 3.3686-21
        s = s.replace('Определение и нормативы · СанПиН 3.3686-21 и МР 3.5.2.0373-25', 'Определение и нормативы · СанПиН 3.3686-21')
    if rel in ('dezinsektsiya/index.html', 'dogovor-deratizatsiya-dezinsektsiya/index.html'):
        # отраслевая карточка общепита — на страницу «Рестораны и кафе» (раньше вела к блоку «Отрасли» на главной)
        s = re.sub(r'<a href="\.\./#otrasli">(Рестораны(?:,| и)[^<]*)</a>', r'<a href="../restorany-i-kafe/">\1</a>', s)
    # страницы «услуга + сфера» для общепита (tools/restorany-uslugi), с 11.11.2026: отраслевые карточки услуг ведут на них,
    # страница ресторанов — на обе страницы (карточки вредителей и «Смотрите также»)
    if rel == 'dezinsektsiya/index.html':
        s = s.replace('<h3><a href="../restorany-i-kafe/">Рестораны, кафе и&nbsp;столовые</a></h3>',
                      '<h3><a href="restorany-i-kafe/">Рестораны, кафе и&nbsp;столовые</a></h3>')
    if rel == 'deratizatsiya/index.html':
        s = s.replace('<a class="ind-more" href="../restorany-i-kafe/">Пест-контроль ресторанов и\u00a0кафе',
                      '<a class="ind-more" href="restorany-i-kafe/">Дератизация ресторанов и\u00a0кафе')
    if rel == 'restorany-i-kafe/index.html':
        if 'id="smotrite-takzhe"' in s and f'href="../{URL["dzr"]}"><span class="rel-k">' not in s:
            i = s.index('id="smotrite-takzhe"')
            j = s.index('</section>', i)
            block = s[i:j]
            for old, new in (('dezins', 'dzr'), ('derat', 'drr')):
                block, n = re.subn(r'<a class="card rel-card" href="\.\./' + re.escape(URL[old]) + r'">.*?</a>',
                                   lambda m, k=new: rel_card('../', k), block, count=1, flags=re.S)
                assert n == 1, rel + ': нет карточки ' + old + ' в «Смотрите также»'
            s = s[:i] + block + s[j:]
        # ответы владельца 11.11.2026: вопрос о кратности — про пест-контроль (кратность дезинсекции разобрана на
        # /dezinsektsiya/restorany-i-kafe/, страницы не спорят за один запрос); контрольный осмотр в разовой цене не упоминаем
        s = re.sub(r'Как часто нужно проводить дезинсекцию в[ \xa0]ресторане\?', 'Как часто нужен пест-контроль ресторана?', s)
        s = re.sub(r'(Истребительная дезинсекция при[ \xa0]очаге: ночью), с[ \xa0]контрольным осмотром через 10–14[ \xa0]дней', r'\1, без гостей и' + '\xa0' + 'персонала', s)
        more = ('<a class="pest-more" href="../{0}" style="display:inline-block;margin-top:12px;font-size:14px;color:var(--t1);'
                'border-bottom:1px solid rgba(124,134,255,.45)">{1}&nbsp;→</a>')
        for h3, k, text in (('Рыжие тараканы', 'dzr', 'Подробнее о дезинсекции'), ('Мыши', 'drr', 'Подробнее о дератизации'),
                            ('Крысы', 'drr', 'Подробнее о дератизации')):
            a = s.find('<h3>' + h3 + '</h3>')
            assert a > 0, rel + ': нет карточки «' + h3 + '»'
            b = s.index('</div></article>', a)
            if 'class="pest-more"' not in s[a:b]:
                s = s[:b] + more.format(URL[k], text) + s[b:]
    if rel == 'dogovor-deratizatsiya-dezinsektsiya/index.html':
        s = s.replace('<div class="d-kind-b"><h3>Дезинсекция</h3>',
                      '<div class="d-kind-b"><h3><a href="../dezinsektsiya/" style="color:inherit;border-bottom:1px solid var(--line2)">Дезинсекция</a></h3>')
    if rel == 'materialy/index.html':
        # в разделе были структурированные данные страницы программы (TechArticle, документы, FAQ) — ставим данные раздела
        s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: MAT_LD, s, count=1, flags=re.S)
        # раздел без фото на первом экране: предзагрузка фото страницы программы (скопирована вместе с шаблоном) только мешала
        s = re.sub(r'\n<link rel="preload" as="image"[^>]*programma-hero[^>]*>', '', s)
        # пометки для превью убираем; число зон — как на странице программы (план мероприятий по 6 зонам A_1…F_6)
        s = re.sub(r' · Опубликован в[\s\xa0]превью</span>', '</span>', s)
        s = re.sub(r'Материал 04 · В[\s\xa0]плане</span>', 'Материал 04 · Готовится</span>', s)
        s = re.sub(r'образец таблицы мероприятий по([\s\xa0])5([\s\xa0])зонам', r'образец таблицы мероприятий по\g<1>6\g<2>зонам', s)
        # заявка с раздела подписывалась как со страницы программы (раздел собран из её шаблона)
        s = s.replace("\\nСтраница: Программа пест-контроля (/materialy/programma-pest-kontrolya/)'",
                      "\\nСтраница: Материалы о пест-контроле (/materialy/)'")
        # карточки материалов — H3 сразу после H1; невидимый H2 восстанавливает порядок заголовков (доступность, Lighthouse)
        if '<h2 class="sr-only">' not in s:
            s, n = re.subn(r'\n(    <div class="p-secs" style="margin-top:36px")', '\n    <h2 class="sr-only">Материалы и образцы документов</h2>\n\\1', s, count=1)
            assert n == 1, 'materialy: нет списка материалов'
    if rel == 'pishchevoe-proizvodstvo/index.html' and 'name="comment"' not in s:
        # send.php читает только name, company, phone, email, type и msg: вид производства и ближайшая проверка
        # терялись. Комментарий посетителя — отдельное поле, в msg перед отправкой собирается всё вместе
        s, n = re.subn(r'<textarea id="f-msg" name="msg"', '<textarea id="f-msg" name="comment"', s, count=1)
        assert n == 1, 'food: нет поля комментария'
        s, n = re.subn(r'(<input type="hidden" name="page" value="[^"]*">)', r'\1\n<input type="hidden" name="msg" value="">', s, count=1)
        assert n == 1, 'food: нет поля page'
        s, n = re.subn(r'\n</body>', lambda m: '\n' + FOOD_FORM_JS + '\n</body>', s, count=1)
        assert n == 1
    if rel == 'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html':
        if 'class="cta-bg' not in s:
            s = s.replace('<section class="cta" id="zayavka">\n', '<section class="cta" id="zayavka"><div class="cta-bg f-lazy" aria-hidden="true"></div>\n', 1)
    # заголовки самопроверки — с курсивным акцентом, как остальные H2
    s = s.replace('>Проверьте папку <span class="nw">пест-контроля</span></h2>', '>Проверьте папку <em><span class="nw">пест-контроля</span></em></h2>')
    s = s.replace('Пройдёт ли ваша программа <span class="nw">пест-контроля</span> аудит</h2>', 'Пройдёт ли ваша программа <em><span class="nw">пест-контроля</span> аудит</em></h2>')
    s = s.replace('Пройдёт ли ваш журнал <span class="nw">пест-контроля</span> проверку</h2>', 'Пройдёт ли ваш журнал <em><span class="nw">пест-контроля</span> проверку</em></h2>')
    return s


def proof_performance(s):
    """Локальная экономия анимаций новой услуги; применяется после общего загрузчика.

    Повторная общая сборка не должна возвращать тяжёлые библиотеки на телефон.
    Общий app.min.js со всеми формами и интеграциями остаётся неизменным.
    """
    s = re.sub(r'<script id="proof-mobile-performance">.*?</script>\n?', '', s, flags=re.S)
    early = (
        '<script id="proof-mobile-performance">'
        '(function(d){if(matchMedia("(max-width:860px), (prefers-reduced-motion:reduce)").matches)'
        'd.classList.add("anim-fail","anim-ready","no-intro")})(document.documentElement)'
        '</script>\n'
    )
    marker = '<script>\n  /* начальные состояния анимаций'
    assert marker in s
    s = s.replace(marker, early + marker, 1)
    desktop = "['vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', 'app.min.js?v=" + VERSION + "']"
    mobile = ('matchMedia("(max-width:860px), (prefers-reduced-motion:reduce)").matches'
              " ? ['app.min.js?v=" + VERSION + "'] : " + desktop)
    s = s.replace(mobile, desktop)
    assert desktop in s
    s = s.replace(desktop, mobile, 1)
    return s.replace("if(lit&&!mm('(prefers-reduced-motion: reduce)').matches){",
                     "if(lit&&!mm('(prefers-reduced-motion: reduce)').matches&&!mm('(max-width:860px)').matches){", 1)


def process_inner(rel, cfg):
    f = ROOT / rel
    s = f.read_text(encoding='utf-8')
    root = cfg['root']
    s = page_specific(rel, s)
    s = dd_related(rel, s)
    s = dok_link(rel, s, root)
    s = fix_head(s, root)
    s = fix_body_start(s)
    # бегущая строка после первого экрана
    if 'id="stripTrack"' not in s and cfg.get('strip'):
        label, items = cfg['strip']
        s, n = re.subn(r'(<section class="[^"]*\b(?:d-hero|p-hero|f-hero)\b[^"]*" id="hero">.*?</section>\n)',
                       lambda m: m.group(1) + strip_html(label, items), s, count=1, flags=re.S)
        assert n == 1, rel + ': нет первого экрана'
    # «Смотрите также» — перед вопросами (или перед заявкой)
    if 'id="smotrite-takzhe"' not in s and cfg.get('related'):
        block = related_html(root, cfg['related'])
        m = re.search(r'\n(?:<!-- =+[^\n]*-->\n)?<section class="[^"]*" id="voprosy">', s) or re.search(r'\n(?:<!-- =+[^\n]*-->\n)?<section class="cta[^"]*" id="zayavka">', s)
        assert m, rel + ': некуда вставить «Смотрите также»'
        s = s[:m.start()] + '\n' + block + s[m.start():]
    # разметка анимаций
    ed = htmldom.Editor(s)
    main = next(n for n in ed.root.iter() if n.tag == 'main')
    for sec in el_children(main):
        if sec.tag != 'section':
            continue
        if sec.attrs.get('id') == 'hero':
            mark_hero(ed, sec)
        else:
            mark_section(ed, sec)
        if sec.attrs.get('id') == 'zayavka':
            for n in sec.iter():
                if n.has_class('cta-bg'):
                    ed.add_attr(n, 'data-parallax-bg')
                if n.has_class('cta-contacts'):
                    ed.add_attr(n, 'data-fade')
    for n in ed.root.iter():
        if n.tag == 'a' and n.has_class('btn-sm') and n.closest(lambda a: a.tag == 'header'):
            ed.add_attr(n, 'data-magnet')
    s = ed.result()
    if 'id="orb"' not in s:
        s, n = re.subn(r'(<section class="cta" id="zayavka">\s*<div class="cta-bg[^>]*></div>)',
                       lambda m: m.group(1) + '<div class="cta-orb" id="orb" aria-hidden="true"></div>', s, count=1)
        assert n == 1, rel + ': нет фона блока заявки'
    s, fxinfo = fx.apply(s)  # фонарь на фото первого экрана, подсветка рамки карточек, data-form, параллакс фото
    if rel == 'zashchita-ot-proniknoveniya-gryzunov/index.html':
        s = proof_performance(s)
    f.write_text(s, encoding='utf-8')
    print('ok', rel)


# ---------------------------------------------------------------- главная
OTRASL_IDS = [  # карточки блока «Отрасли» на главной — якоря для меню (по началу заголовка карточки)
    ('Пищев', 'otrasl-pishchevye'), ('Торгов', 'otrasl-seti'), ('Магазин', 'otrasl-seti'), ('Ресторан', 'otrasl-restorany'),  # «Магазины и торговые сети» — с 11.11.2026
    ('Склад', 'otrasl-sklady'), ('Фармацевт', 'otrasl-farma'), ('Гостиниц', 'otrasl-gostinitsy'),
]


def process_home():
    f = ROOT / 'index.html'
    s = f.read_text(encoding='utf-8')
    s, n = HEAD_SCRIPT_RE.subn(lambda m: HEAD_SCRIPT, s, count=1)
    assert n == 1
    s = re.sub(r'(src="app\.min\.js)\?v=[^"]*"', rf'\1?v={VERSION}"', s)
    s = use_loader(s)
    # якоря карточек отраслей
    ed = htmldom.Editor(s)
    sec = next(n for n in ed.root.iter() if n.tag == 'section' and n.attrs.get('id') == 'otrasli')
    cards = [n for n in sec.iter() if n.tag == 'article' and n.has_class('ind')]
    titles = []
    for c in cards:
        h3 = next(d for d in c.iter() if d.tag == 'h3')
        end = s.find('</h3>', h3.end_open)
        titles.append(re.sub(r'<[^>]+>', '', s[h3.end_open:end]).replace('\xa0', ' ').strip())
    for c, t in zip(cards, titles):
        sid = next((i for name, i in OTRASL_IDS if t.startswith(name)), None)
        assert sid, 'нет якоря для карточки ' + t
        ed.add_attr(c, 'id', sid)
    s = ed.result()
    # карточка пищевых производств ведёт на отраслевую страницу
    if 'class="ind-more"' not in s:
        a = s.find('id="otrasl-pishchevye"')
        b = s.find('</article>', a)
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка пищевых производств'
        s = s[:b - 6] + f'<a class="ind-more" href="pishchevoe-proizvodstvo/">Подробнее об обслуживании производств{ARR}</a>' + s[b - 6:]
    # карточка торговых сетей ведёт на страницу «Магазины и торговые сети»
    a = s.find('id="otrasl-seti"')
    b = s.find('</article>', a)
    if 'href="magaziny-i-torgovye-seti/"' not in s[a:b]:
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка торговых сетей'
        s = s[:b - 6] + f'<a class="ind-more" href="magaziny-i-torgovye-seti/">Подробнее об обслуживании магазинов{ARR}</a>' + s[b - 6:]
    if 'href="gostinitsy/"' not in s:
        a = s.find('id="otrasl-gostinitsy"')
        b = s.find('</article>', a)
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка гостиниц'
        s = s[:b - 6] + f'<a class="ind-more" href="gostinitsy/">Подробнее об обслуживании гостиниц{ARR}</a>' + s[b - 6:]
    # карточка фармацевтических производств ведёт на отраслевую страницу
    a = s.find('id="otrasl-farma"')
    b = s.find('</article>', a)
    if 'href="farmatsevticheskie-proizvodstva/"' not in s[a:b]:
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка фармацевтических производств'
        s = s[:b - 6] + f'<a class="ind-more" href="farmatsevticheskie-proizvodstva/">Подробнее о <span class="nw">пест-контроле</span> по GMP{ARR}</a>' + s[b - 6:]
    # карточка складов и логистики ведёт на отраслевую страницу
    if 'class="ind-more" href="sklady-i-logistika/"' not in s:
        a = s.find('id="otrasl-sklady"')
        b = s.find('</article>', a)
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка складов и логистики'
        s = s[:b - 6] + f'<a class="ind-more" href="sklady-i-logistika/">Подробнее о <span class="nw">пест-контроле</span> складов{ARR}</a>' + s[b - 6:]
    # карточка ресторанов ведёт на страницу «Рестораны и кафе»
    a = s.find('id="otrasl-restorany"')
    b = s.find('</article>', a)
    if 'href="restorany-i-kafe/"' not in s[a:b]:
        assert a > 0 and s[b - 6:b] == '</div>', 'карточка ресторанов'
        s = s[:b - 6] + f'<a class="ind-more" href="restorany-i-kafe/">Подробнее об обслуживании ресторанов{ARR}</a>' + s[b - 6:]
    # ссылки «Подробнее» в блоках главной
    adds = [
        ('podhod', more_html('Подробнее', [('materialy/pest-menedzhment-ili-razovaya-obrabotka/', 'Пест-менеджмент или разовая обработка')])),
        # с 11.11.2026 плитки блока сами ведут на образцы (программа, схема, журнал, акт), под ними — перечень и договор
        ('dokumenty', more_html('Образцы документов', [('dogovor-deratizatsiya-dezinsektsiya/', 'Договор на обслуживание')])),
        ('vrediteli', more_html('Подробнее', [('deratizatsiya/', 'Дератизация для организаций'), ('dezinsektsiya/', 'Дезинсекция для организаций')])),
        ('usloviya', more_html('Условия', [('dogovor-deratizatsiya-dezinsektsiya/', 'Договор на дератизацию и дезинсекцию')])),
    ]
    for sid, html in adds:
        if f'data-more="{sid}"' in s:
            continue
        html = html.replace('<nav class="more"', f'<nav class="more" data-more="{sid}"', 1)
        i = s.find(f'id="{sid}"')
        assert i > 0, sid
        j = s.find('\n</section>', i)
        k = s.rfind('\n  </div>', i, j)  # закрытие .wrap
        assert k > i, sid
        s = s[:k] + html + s[k:]
    # «Документы» на главной: первой — ссылка на полный перечень для Роспотребнадзора (страница с 08.11.2026)
    i = s.find('<nav class="more" data-more="dokumenty"')
    assert i > 0, 'главная: нет ссылок блока «Документы»'
    if f'href="{URL["dok"]}"' not in s[i:s.find('</nav>', i)]:
        k = s.index('</span>', i) + len('</span>')  # после подписи «Образцы документов»
        s = s[:k] + f'<a href="{URL["dok"]}"><span>{tp("Полный перечень для Роспотребнадзора")}</span>{ARR}</a>' + s[k:]
    f.write_text(s, encoding='utf-8')
    print('ok index.html')


def main():
    process_home()
    for rel, cfg in PAGES.items():
        process_inner(rel, cfg)


if __name__ == '__main__':
    main()
