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
    'home': '', 'derat': 'deratizatsiya/', 'dezins': 'dezinsektsiya/',
    'dogovor': 'dogovor-deratizatsiya-dezinsektsiya/', 'food': 'pishchevoe-proizvodstvo/',
    'seti': 'magaziny-i-torgovye-seti/', 'hotel': 'gostinitsy/',
    'mat': 'materialy/', 'prog': 'materialy/programma-pest-kontrolya/',
    'zhur': 'materialy/zhurnal-pest-kontrolya/', 'pm': 'materialy/pest-menedzhment-ili-razovaya-obrabotka/',
    'vent': 'ochistka-dezinfektsiya-ventilyatsii/',
    'farma': 'farmatsevticheskie-proizvodstva/', 'sklady': 'sklady-i-logistika/',
    'ppk': 'materialy/programma-proizvodstvennogo-kontrolya-haccp/',
    'rest': 'restorany-i-kafe/',
    'san': 'sanitarnyy-audit/',
    'dezinf': 'dezinfektsiya/',
    'nb': 'normativnaya-baza/', 'pl': 'normativnaya-baza/proverochnye-listy/',
}
# карточки «Смотрите также»: (вид, заголовок, описание)
CARD = {
    'derat': ('Услуга', 'Дератизация для организаций',
              'Три контура защиты от крыс и мышей, контейнеры КИК и ловушки без яда в цехах, схема точек и акты.'),
    'dezins': ('Услуга', 'Дезинсекция для организаций',
               'Контроль насекомых по IPM без остановки работы, ротация средств, журнал и акты по СанПиН.'),
    'dogovor': ('Обслуживание', 'Договор на дератизацию и дезинсекцию',
                'Одно или оба направления в одном договоре: график визитов, акт после выезда, цена до подписания.'),
    'food': ('Отрасль', 'Пест-контроль на пищевом производстве',
             'Точки контроля, визиты по графику смен и документы для Роспотребнадзора, аудиторов и торговых сетей.'),
    'seti': ('Отрасль', 'Пест-контроль магазинов и торговых сетей',
             'Ночные визиты без закрытия зала, журнал и схема точек в каждом магазине, сводный отчёт по сети.'),
    'hotel': ('Отрасль', 'Пест-контроль гостиниц и отелей',
              'Осмотры номерного фонда, протокол при жалобе гостя на клопов и журнал по проверочному листу Роспотребнадзора.'),
    'rest': ('Отрасль', 'Пест-контроль ресторанов и кафе',
             'Визиты после закрытия, гели и ловушки на кухне, журнал и акты по СанПиН для заведений и сетей.'),
    'prog': ('Материал', 'Программа пест-контроля',
             'Образец в PDF и шаблон Word: 7 разделов, оценка пест-риска по зонам и план мероприятий.'),
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
            'Полный образец ППК для пищевого производства (PDF и Word) и раздел о дезинсекции и дератизации по правилам 2026 года.'),
    'san': ('Услуга', 'Санитарный аудит (СЭС-аудит)',
            'Проверка по проверочным листам и СанПиН 2026 года, смывы и пробы воздуха, акт с реестром нарушений.'),
    'dezinf': ('Услуга', 'Дезинфекция для организаций',
               'Плановая и внеплановая дезинфекция, смывы, периодичность по правилам 2026 года и все санитарные услуги в одной программе.'),
    'nb': ('Нормативная база', 'СанПиН и требования к дезинсекции и дератизации',
           'Действующие документы 2026 года, периодичность обследований, лицензия исполнителя и отменённые СП и СанПиН.'),
    'pl': ('Разбор', 'Проверочные листы Роспотребнадзора 2026',
           'Вопросы о насекомых и грызунах по приказам № 578 и № 580 — по видам объектов и с документами для ответа.'),
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
    'deratizatsiya/index.html': dict(key='derat', root='../', related=['dezins', 'dogovor', 'prog', 'san']),
    'dezinsektsiya/index.html': dict(key='dezins', root='../', related=['derat', 'dogovor', 'prog', 'san'], strip=(
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
            ('lucide-clock', 'Ночные визиты', 'без закрытия зала'),
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
    'restorany-i-kafe/index.html': dict(key='rest', root='../', related=['dezins', 'derat', 'dogovor', 'zhur'], strip=(
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
            ('lucide-file-signature', 'Программа', 'пест-контроля — образец PDF и шаблон Word'),
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
            ('lucide-notebook-pen', 'Шаблон', 'в Word (DOCX)'),
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
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html': dict(key='ppk', root='../../', related=['prog', 'zhur', 'food', 'dogovor'], strip=(
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
    if 'vendor/gsap.min.js' not in s:
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
         'description': 'Практические руководства и образцы документов по системе IPM и ХАССП для предприятий Москвы и области: программа пест-контроля, журнал пест-контроля, пест-менеджмент или разовая обработка, образец программы производственного контроля по ХАССП (PDF и Word) и её раздел пест-контроля, нормативная база дезинсекции и дератизации и разбор проверочных листов Роспотребнадзора 2026 года.',
         'isPartOf': {'@type': 'WebSite', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': SITE},
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [
             {'@type': 'ListItem', 'position': 1, 'url': SITE + 'materialy/programma-pest-kontrolya/', 'name': 'Программа пест-контроля на предприятии: образец PDF, шаблон Word и пример заполнения'},
             {'@type': 'ListItem', 'position': 2, 'url': SITE + 'materialy/pest-menedzhment-ili-razovaya-obrabotka/', 'name': 'Пест-менеджмент или разовая обработка'},
             {'@type': 'ListItem', 'position': 3, 'url': SITE + 'materialy/zhurnal-pest-kontrolya/', 'name': 'Журнал пест-контроля: образец заполнения, бланк и шаблон'},
             {'@type': 'ListItem', 'position': 4, 'url': SITE + 'materialy/programma-proizvodstvennogo-kontrolya-haccp/', 'name': 'Программа производственного контроля по ХАССП: образец и раздел пест-контроля'},
             {'@type': 'ListItem', 'position': 5, 'url': SITE + 'normativnaya-baza/', 'name': 'Нормативная база: СанПиН и требования к дезинсекции и дератизации'},
             {'@type': 'ListItem', 'position': 6, 'url': SITE + 'normativnaya-baza/proverochnye-listy/', 'name': 'Проверочные листы Роспотребнадзора 2026: вопросы о дезинсекции и дератизации'}]},
         'publisher': {'@type': 'Organization', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': SITE, 'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru'}},
    ]}, ensure_ascii=False) + '</script>'


HOTEL_LINKS = {  # карточки гостиниц на страницах услуг ведут на отраслевую страницу (раньше — к блоку «Отрасли» на главной)
    'dezinsektsiya/index.html': ('<h3><a href="../#otrasli">Гостиницы, отели и&nbsp;общежития</a></h3>', '<h3><a href="../gostinitsy/">Гостиницы, отели и&nbsp;общежития</a></h3>'),
    'dogovor-deratizatsiya-dezinsektsiya/index.html': ('<h3><a href="../#otrasli">Гостиницы</a></h3>', '<h3><a href="../gostinitsy/">Гостиницы</a></h3>'),
}


SAN_REL = ('deratizatsiya/index.html', 'dezinsektsiya/index.html', 'pishchevoe-proizvodstvo/index.html')


def rel_card(root, k):
    kind, title, desc = CARD[k]
    return (f'<a class="card rel-card" href="{root}{URL[k]}">'
            f'<span class="rel-k">{kind}</span><span class="rel-t">{tp(title)}</span>'
            f'<span class="rel-d">{tp(desc)}</span><span class="rel-a" aria-hidden="true">{ARR}</span></a>')


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


def process_inner(rel, cfg):
    f = ROOT / rel
    s = f.read_text(encoding='utf-8')
    root = cfg['root']
    s = page_specific(rel, s)
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
    f.write_text(s, encoding='utf-8')
    print('ok', rel)


# ---------------------------------------------------------------- главная
OTRASL_IDS = [  # карточки блока «Отрасли» на главной — якоря для меню (по началу заголовка карточки)
    ('Пищев', 'otrasl-pishchevye'), ('Торгов', 'otrasl-seti'), ('Ресторан', 'otrasl-restorany'),
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
        ('dokumenty', more_html('Образцы документов', [('materialy/programma-pest-kontrolya/', 'Программа пест-контроля'),
                                                       ('materialy/zhurnal-pest-kontrolya/', 'Журнал пест-контроля'),
                                                       ('dogovor-deratizatsiya-dezinsektsiya/', 'Договор на обслуживание')])),
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
    f.write_text(s, encoding='utf-8')
    print('ok index.html')


def main():
    process_home()
    for rel, cfg in PAGES.items():
        process_inner(rel, cfg)


if __name__ == '__main__':
    main()
