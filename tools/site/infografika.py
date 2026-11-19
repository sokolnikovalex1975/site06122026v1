#!/usr/bin/env python3
"""Инфографика в стиле страницы «Лабораторные исследования» на всём сайте (команда владельца 19.11.2026).

    python3 tools/site/infografika.py                    # правит страницы репозитория
    python3 tools/site/infografika.py --check            # только проверка, код 1, если нужно поправить
    python3 tools/site/infografika.py --check-prod <файлы>  # проверка готовых index.php пакета для Timeweb

Команда владельца 19.11.2026 (чат согласований): «ПЕСТКОНТРОЛЬ Центр: … 2 делай вариант а» — иконка «Пест-контроль»
вариант A (щит с тараканом) и выкладка всего согласованного набора иконок на рабочий сайт. Доски 00–12 согласования —
в файлах проекта «Инфографика в стиле лаборатории/v1 — варианты для согласования», дезинсекция — вариант A
(генератор холодного тумана, решение владельца 19.11.2026), в круге IPM на шаге «Осмотр» остаётся планшет со схемой.

Мелкие значки в квадратах и фото вредителей заменяются предметными иконками без фона (белый матовый предмет
с фиолетовыми деталями, img/ig-<ключ>-128.webp и -240.webp, собираются tools/site/infografika_tiles.py из
мастер-файлов 2048×2048):
  01 «Все услуги Центра» (.s-vu, 24 страницы) — иконка 64 px, на экранах до 900 px 56 px;
  02 «Цены на услуги» (.s-pr, 18 страниц) — 112 px в карточках (до 900 px 84 px справа), 60 px в «Других услугах»;
  03 «Порядок работы» — над каждым шагом 120 px, на телефоне 72 px слева от текста, как в лаборатории;
  04 карточки «Документы по программе» — 100 px, на экранах до 900 px 72 px слева от названия;
  05 вентиляция, «Что чистим в системе» — 120 px, номер карточки в правом углу;
  06 отрасли без фото (санаудит, дезинфекция, вентиляция, разработка ППК) — 104 px, на телефоне 76 px;
  07 таблицы «Документ — кому нужен» (5 страниц, где строки — документы) — 60 px слева от названия;
  08 круг «Цикл визита» (главная, дератизация) — 104 px, на телефоне 64 px, анимация круга сохраняется;
  09 «Кого контролируем» (10 страниц) — макеты вредителей вместо фото, подписи alt не меняются;
  10 «Документы для Роспотребнадзора», восемь групп — 96 px, на телефоне 64 px.

Стили — одна строка <style id="ig"> сразу после строки <style id="mob-fit"> (только правила блоков этой страницы):
не перед </head>, где по закону стоит UIS. Счётчики Метрики, UIS и Radist, телефоны и почта не меняются,
ссылок и упоминаний другого проекта нет. Ничего не затемняется (закон владельца 17.11.2026): иконки без подложек
и затемнений, тексты прежних цветов. Картинки с width/height и loading="lazy" — без сдвигов вёрстки.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EASE = 'transition:transform .35s cubic-bezier(.2,.7,.2,1)'

# ---------------------------------------------------------------- соответствия «подпись → иконка»
VU = {
    'Пест-контроль для бизнеса': 'ipm', 'Дератизация': 'deratizatsiya', 'Дезинсекция': 'dezinsektsiya',
    'Дератизация и дезинсекция': 'kompleks', 'Дезинфекция': 'dezinfektsiya',
    'Очистка и дезинфекция вентиляции': 'ventilyatsiya', 'Санитарный аудит (СЭС-аудит)': 'sanaudit',
    'Лабораторные исследования': 'lab-i-ppk', 'Разработка ППК': 'razrabotka-ppk',
    'Документы для Роспотребнадзора': 'dokumenty-rpn',
}
PR_MINI = {
    'Дезинфекция помещений': 'dezinfektsiya', 'Санитарный аудит': 'sanaudit',
    'Очистка и дезинфекция вентиляции': 'ventilyatsiya', 'Лабораторный контроль по ППК': 'lab-i-ppk',
}
DOCS = {
    'Договор и программа': 'dogovor', 'Схема точек контроля': 'doc-skhema', 'План-схема точек': 'doc-skhema',
    'Журнал осмотров': 'doc-zhurnal', 'Журнал дератизации': 'doc-zhurnal', 'Журнал пест-контроля': 'doc-zhurnal',
    'Акты выполненных работ': 'doc-akt', 'Акты и УПД': 'doc-akt', 'Акты': 'doc-akt',
    'СГР и инструкции': 'doc-sgr', 'СГР и лицензия': 'doc-sgr', 'Лицензия и СГР': 'doc-sgr',
    'Отчёт за месяц': 'doc-otchet', 'Ежемесячный отчёт': 'doc-otchet',
}
VENT = {
    'Воздуховоды': 'vent-vozdukhovody', 'Зонты и жироуловители': 'vent-zonty', 'Вентиляторы': 'vent-ventilyatory',
    'Приточные установки': 'vent-pritochnye', 'Решётки, диффузоры, клапаны': 'vent-reshetki',
    'Кондиционеры и фанкойлы': 'vent-konditsionery',
}
IND = {
    'Пищевые производства': 'ind-pishchevoe', 'Пищевое производство': 'ind-pishchevoe',
    'Магазины и торговые сети': 'ind-magaziny', 'Торговые сети': 'ind-magaziny',
    'Торговые центры и магазины': 'ind-magaziny', 'Магазин, торговая сеть': 'ind-magaziny',
    'Рестораны и кафе': 'ind-restorany', 'Рестораны, кафе, фуд-корты': 'ind-restorany',
    'Ресторан, кафе, столовая': 'ind-restorany',
    'Склады и логистика': 'ind-sklady', 'Склады и производства': 'ind-sklady', 'Склад, логистика': 'ind-sklady',
    'Фармацевтические производства': 'ind-farma', 'Фармацевтика': 'ind-farma',
    'Фармацевтическое производство': 'ind-farma',
    'Гостиницы': 'ind-gostinitsy', 'Гостиница': 'ind-gostinitsy',
    'Офисы и бизнес-центры': 'ind-ofisy', 'Медицинские организации': 'ind-medicina',
    'Школы и детские сады': 'ind-shkoly',
}
IND_PAGES = {  # отрасли без фото (доска 06)
    'sanitarnyy-audit/index.html': 'sa', 'dezinfektsiya/index.html': 'card',
    'ochistka-dezinfektsiya-ventilyatsii/index.html': 'card', 'razrabotka-ppk/index.html': 'rp',
}
NODES = {  # круг «Цикл визита»: главная и дератизация
    'Осмотр': 'osmotr', 'Санитария': 'obsledovanie', 'Учёт': 'doc-otchet', 'Действие': 'dezinsektsiya',
    'Ревизия': 'osmotr', 'Барьер': 'zashchita', 'Защита': 'deratizatsiya',
}
PESTS = {
    'p-cockroach.webp': 'pest-tarakan', 'p-rat.webp': 'pest-krysa', 'p-black-rat.webp': 'pest-krysa-chernaya',
    'p-mouse.webp': 'pest-mysh', 'p-fly.webp': 'pest-mukha', 'p-moth.webp': 'pest-mol',
    'p-bedbug-macro.webp': 'pest-klop', 'p-pigeon.webp': 'pest-golub', 'p-ant.webp': 'pest-muravey',
    'p-silverfish.webp': 'pest-cheshuynitsa', 'p-mosquito.webp': 'pest-komar',
    'p-drugstore-beetle.webp': 'pest-tochilshchik',
}
DK_GROUPS = ['razrabotka-ppk', 'dogovor', 'doc-akt', 'lab-i-ppk', 'doc-zhurnal', 'doc-personal', 'doc-sgr',
             'doc-produkciya']
# 03 «Порядок работы»: страница → (id блока, иконки шагов по порядку во всех списках блока)
STEPS = {
    'sanitarnyy-audit/index.html': ('kak-prohodit', ['lab-s1', 'dokumenty-rpn', 'obsledovanie', 'doc-akt', 'doc-otchet']),
    'razrabotka-ppk/index.html': ('kak-rabotaem', ['lab-s1', 'sanaudit', 'razrabotka-ppk', 'dogovor', 'doc-akt']),
    'dogovor-deratizatsiya-dezinsektsiya/index.html': ('etapy', ['lab-s1', 'obsledovanie', 'dogovor', 'doc-akt', 'kompleks']),
    'ochistka-dezinfektsiya-ventilyatsii/index.html': ('etapy', ['obsledovanie', 'doc-otchet', 'vent-reshetki',
                                                                 'ventilyatsiya', 'dezinfektsiya', 'doc-akt']),
    'dezinsektsiya/index.html': ('etapy', ['obsledovanie', 'doc-skhema', 'dezinsektsiya', 'doc-zhurnal', 'osmotr']),
    'magaziny-i-torgovye-seti/index.html': ('zapusk', ['obsledovanie', 'razrabotka-ppk', 'dogovor', 'ind-magaziny',
                                                       'doc-otchet']),
    'farmatsevticheskie-proizvodstva/index.html': ('reglament', ['obsledovanie', 'doc-skhema', 'kompleks', 'osmotr',
                                                                 'doc-otchet']),
    'pishchevoe-proizvodstvo/index.html': ('mesyac', ['osmotr', 'kompleks', 'doc-otchet', 'lab-s1']),
    'gostinitsy/index.html': ('mesyac', ['osmotr', 'kompleks', 'doc-otchet', 'lab-s1']),
    'restorany-i-kafe/index.html': ('vizit', ['razrabotka-ppk', 'osmotr', 'kompleks', 'doc-zhurnal',
                                              'lab-s1', 'dezinsektsiya', 'dezinfektsiya', 'obsledovanie']),
    'dezinsektsiya/restorany-i-kafe/index.html': ('noch-obrabotki', ['sanaudit', 'obsledovanie', 'dezinsektsiya',
                                                                     'dezinfektsiya', 'osmotr']),
    'deratizatsiya/restorany-i-kafe/index.html': ('kak-prokhodit', ['obsledovanie', 'doc-skhema', 'deratizatsiya',
                                                                    'osmotr', 'doc-otchet', 'lab-s1']),
    'materialy/akt-deratizatsii-i-dezinsektsii/index.html': ('zakazat', ['lab-s1', 'osmotr', 'obsledovanie', 'doc-akt']),
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html': ('kak-gotovim', [
        'obsledovanie', 'sanaudit', 'razrabotka-ppk', 'dogovor', 'doc-zhurnal']),
    'normativnaya-baza/proverochnye-listy/index.html': ('podgotovka', ['dokumenty-rpn', 'sanaudit', 'dogovor', 'lab-s5',
                                                                       'obsledovanie', 'doc-personal']),
    'zashchita-ot-proniknoveniya-gryzunov/index.html': ('podhod', ['obsledovanie', 'dogovor', 'zashchita', 'doc-akt']),
}
# 07 таблицы, где строки — документы папки (в остальных таблицах строки — нормы или вопросы проверяющего)
TABLE_DOCS = {
    'pishchevoe-proizvodstvo/index.html': {
        'Программа пест-контроля для плана ХАССП': 'razrabotka-ppk', 'Оценка пест-риска по зонам': 'sanaudit',
        'Схема точек контроля с номерами': 'doc-skhema', 'Журнал осмотров и учёта численности': 'doc-zhurnal',
        'Акты выполненных работ': 'doc-akt', 'Перечень средств с СГР и зонами применения': 'doc-sgr',
        'Ежемесячный отчёт с трендами': 'doc-otchet', 'Лицензия и удостоверения специалистов': 'doc-personal'},
    'restorany-i-kafe/index.html': {
        'Договор и лицензия исполнителя': 'dogovor', 'Программа пест-контроля': 'razrabotka-ppk',
        'Схема точек контроля': 'doc-skhema', 'Журнал пест-контроля': 'doc-zhurnal', 'Акт после визита': 'doc-akt',
        'СГР и инструкции на средства': 'doc-sgr', 'Отчёт по сети за месяц': 'doc-otchet'},
    'magaziny-i-torgovye-seti/index.html': {
        'Договор и перечень магазинов': 'dogovor', 'Программа пест-контроля': 'razrabotka-ppk',
        'Схема точек контроля магазина': 'doc-skhema', 'Журнал учёта с записью каждого визита': 'doc-zhurnal',
        'Акты выполненных работ': 'doc-akt', 'Копия лицензии исполнителя': 'doc-personal',
        'СГР и инструкции на средства': 'doc-sgr', 'Ежемесячный сводный отчёт': 'doc-otchet'},
    'gostinitsy/index.html': {
        'Договор с лицензированной организацией': 'dogovor', 'Программа пест-контроля гостиницы': 'razrabotka-ppk',
        'Схема точек контроля с номерами': 'doc-skhema', 'Журнал обследований и учёта численности': 'doc-zhurnal',
        'График осмотра номерного фонда': 'osmotr', 'Акты выполненных работ': 'doc-akt',
        'Перечень средств с СГР и инструкциями': 'doc-sgr', 'Ежемесячный отчёт': 'doc-otchet',
        'Лицензия и удостоверения специалистов': 'doc-personal'},
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html': {
        'ППК с разделом «Дезинсекция и дератизация»': 'razrabotka-ppk',
        'Договор на дезинсекцию и дератизацию': 'dogovor', 'Лицензия Роспотребнадзора исполнителя': 'doc-personal',
        'Акты выполненных работ': 'doc-akt', 'Журнал учёта и схема точек контроля': 'doc-zhurnal',
        'Перечень средств с документами о регистрации': 'doc-sgr',
        'Ежемесячный отчёт и корректирующие действия': 'doc-otchet'},
}

# ---------------------------------------------------------------- стили блоков
CSS = {
    'vu': ('.s-vu .vu-i{grid-template-columns:64px minmax(0,1fr) auto;align-items:center}'
           '.s-vu .vu-ic{width:64px;height:64px;background:none;border-radius:0}'
           '.s-vu .vu-ic img{width:64px;height:64px;display:block;' + EASE + '}'
           '.s-vu .vu-i:hover .vu-ic img{transform:scale(1.06)}'
           '.s-vu .vu-i+.vu-i::before{left:94px}'
           '@media (max-width:900px){.s-vu .vu-i{grid-template-columns:56px minmax(0,1fr) auto}'
           '.s-vu .vu-ic,.s-vu .vu-ic img{width:56px;height:56px}.s-vu .vu-i+.vu-i::before{left:86px}}'
           '@media (max-width:760px){.s-vu .vu-i+.vu-i::before{left:80px}}'),
    'pr': ('.s-pr .pr-card{min-height:0}.s-pr .pr-num{margin-bottom:6px}'
           '.s-pr .ig-pr{display:block;width:112px;height:112px;margin:0 0 10px -10px;' + EASE + '}'
           '.s-pr .pr-card:hover .ig-pr{transform:scale(1.06)}'
           '.s-pr .pr-mini{display:grid;grid-template-columns:60px minmax(0,1fr) auto;column-gap:18px;align-items:center}'
           '.s-pr .ig-prm{width:60px;height:60px;display:block}'
           '@media (max-width:900px){.s-pr .pr-card{position:relative}'
           '.s-pr .ig-pr{position:absolute;right:14px;top:40px;width:84px;height:84px;margin:0}'
           '.s-pr .pr-card h3,.s-pr .pr-card p{padding-right:92px}'
           '.s-pr .pr-mini{grid-template-columns:52px minmax(0,1fr);row-gap:6px}'
           '.s-pr .ig-prm{grid-row:1/3;width:52px;height:52px}.s-pr .pr-mini .pr-price{grid-column:2}}'),
    'steps': ('.ig-steps>li{display:flex;flex-direction:column;border-top:0;padding-top:0}'
              '.ig-steps>li>.ig-step-ic{order:0;display:block;width:120px;height:120px;margin:0 0 14px -6px}'
              '.ig-steps>li::before{order:1;border-top:2px solid rgba(124,134,255,.35);padding-top:14px}'
              '.ig-steps>li.f-alert::before{border-top-color:var(--yel)}'
              '.ig-steps>li>b{order:2}.ig-steps>li>span{order:3}'
              '@media (max-width:600px){.ig-steps>li{display:grid;grid-template-columns:72px minmax(0,1fr);'
              'column-gap:14px;align-content:start}'
              '.ig-steps>li>.ig-step-ic{grid-row:1/4;grid-column:1;width:72px;height:72px;margin:0}'
              '.ig-steps>li::before{grid-column:2;border-top:0;padding-top:0;margin-bottom:4px}'
              '.ig-steps>li>b,.ig-steps>li>span{grid-column:2}}'),
    'steps-r': ('.r-steps.ig-steps>li::after{top:132px}'
                '@media (max-width:600px){.r-steps.ig-steps>li::after{display:none}}'),
    'steps-nb': ('.nb-page .nb-steps.ig-steps>li::before{display:block;margin:0 0 12px}'
                 '@media (max-width:600px){.nb-page .nb-steps.ig-steps>li::before{margin:0 0 4px}}'),
    'steps-md': ('.md-check.ig-steps>li{display:grid;grid-template-columns:72px minmax(0,1fr);column-gap:16px;'
                 'align-content:start;padding:18px 0;border-top:1px solid var(--line2)}'
                 '.md-check.ig-steps>li>.ig-step-ic{grid-row:1/4;grid-column:1;width:72px;height:72px;margin:0}'
                 '.md-check.ig-steps>li::before{position:static;grid-column:2;border-top:0;padding-top:0;margin:0 0 4px}'
                 '.md-check.ig-steps>li>b,.md-check.ig-steps>li>span{grid-column:2}'),
    'steps-proof': ('.proof-steps.ig-cards .d-card{position:relative}'
                    '.proof-steps.ig-cards .ig-step-ic{display:block;width:120px;height:120px;margin:-10px 0 6px -10px}'
                    '.proof-steps.ig-cards .d-card>.f-lbl{position:absolute;right:clamp(22px,2vw,34px);'
                    'top:clamp(22px,2vw,34px)}'
                    '@media (max-width:600px){.proof-steps.ig-cards .d-card{display:grid;'
                    'grid-template-columns:80px minmax(0,1fr);column-gap:14px}'
                    '.proof-steps.ig-cards .ig-step-ic{grid-row:1/3;width:80px;height:80px;margin:0}'
                    '.proof-steps.ig-cards .d-card>h3{grid-column:2;align-self:center;padding-right:28px;margin:0 0 6px}'
                    '.proof-steps.ig-cards .d-card>p{grid-column:1/3}}'),
    'docs': ('.docs .doc .ico{width:100px;height:100px;border-radius:0;background:none!important;border:0!important;'
             'box-shadow:none!important;margin:-12px 0 12px -12px}'
             '.docs .doc .ico img{width:100px;height:100px;display:block;' + EASE + '}'
             '.docs .doc:hover .ico{transform:none}.docs .doc:hover .ico img{transform:scale(1.06)}'
             '@media (max-width:900px){.docs .doc{display:grid;grid-template-columns:72px minmax(0,1fr);'
             'column-gap:14px;align-items:center}.docs .doc .ico{grid-row:1;width:72px;height:72px;margin:0}'
             '.docs .doc .ico img{width:72px;height:72px}.docs .doc h3{grid-column:2;margin:0;padding-right:24px}'
             '.docs .doc p,.docs .doc .doc-go{grid-column:1/3}.docs .doc p{margin-top:10px}}'),
    'vparts': ('.v-parts .d-card{position:relative}'
               '.v-parts .ig-v{display:block;width:120px;height:120px;margin:-10px 0 6px -10px;' + EASE + '}'
               '.v-parts .d-card:hover .ig-v{transform:scale(1.06)}'
               '.v-parts .dz-lbl{position:absolute;right:clamp(22px,2vw,34px);top:clamp(22px,2vw,34px)}'
               '@media (max-width:600px){.v-parts .d-card{display:grid;grid-template-columns:80px minmax(0,1fr);'
               'column-gap:14px}.v-parts .ig-v{grid-row:1/3;width:80px;height:80px;margin:0}'
               '.v-parts .d-card h3,.v-parts .d-card p{grid-column:2}'
               '.v-parts .d-card h3{align-self:center;padding-right:28px;margin:0 0 6px}.v-parts .d-card p{grid-column:1/3}}'),
    'ind-sa': ('.sa-inds .sa-ico{margin:-12px 0 10px -12px}'
               '.sa-inds .sa-ico img{width:104px;height:104px;display:block;' + EASE + '}'
               '.sa-inds .d-card:hover .sa-ico img{transform:scale(1.06)}'
               '@media (max-width:600px){.sa-inds .d-card{display:grid;grid-template-columns:76px minmax(0,1fr);'
               'column-gap:14px;align-items:center}.sa-inds .sa-ico{grid-row:1;margin:0}'
               '.sa-inds .sa-ico img{width:76px;height:76px}.sa-inds .d-card h3{grid-column:2;margin:0}'
               '.sa-inds .d-card>p:not(.sa-ico),.sa-inds .sa-more{grid-column:1/3}'
               '.sa-inds .d-card>p:not(.sa-ico){margin-top:12px}}'),
    'ind-card': ('.ig-c>.ig-ind{display:block;width:104px;height:104px;margin:-12px 0 0 -12px;' + EASE + '}'
                 '.ig-c:hover>.ig-ind{transform:scale(1.06)}'
                 '@media (max-width:600px){.ig-c{display:grid;grid-template-columns:76px minmax(0,1fr);'
                 'column-gap:14px;row-gap:0;align-items:center}.ig-c>.ig-ind{grid-row:1;width:76px;height:76px;margin:0}'
                 '.ig-c>h3{grid-column:2;margin:0}.ig-c>p{grid-column:1/3;margin-top:12px}}'),
    'ind-rp': ('.rp-obj .rp-ico{margin:-6px 0 8px -6px}.rp-obj .rp-ico img{width:56px;height:56px;display:block}'
               '@media (max-width:900px){.rp-obj .rp-ico img{width:52px;height:52px}}'),
    'table': ('.ig-row{display:flex;align-items:center;gap:18px}.ig-row>img{width:60px;height:60px;flex:none;margin:-8px 0}'
              '@media (max-width:900px){.ig-row{gap:12px}.ig-row>img{width:52px;height:52px;margin:-4px 0}}'),
    'cycle': ('.cycle .node>i{width:clamp(72px,6vw,104px)!important;height:clamp(72px,6vw,104px)!important;'
              'background:radial-gradient(circle,var(--bg) 58%,transparent 72%)!important;border:0!important;'
              'box-shadow:none!important;border-radius:50%!important}'
              '.cycle .node>i img{width:100%;height:100%;display:block}'
              '.cycle .node.on>i{transform:scale(1.12);filter:drop-shadow(0 0 22px rgba(124,134,255,.6))}'
              '@media (max-width:600px){.cycle .node>i{width:64px!important;height:64px!important}}'),
    'pest': ('.pest-img.ig-pi{background:none;overflow:visible;border-radius:0}'
             '.pest-img.ig-pi img{object-fit:contain;transform:none!important}.pest-img.ig-pi .scan{display:none}'),
    'dkg': ('.dk-g{position:relative}'
            '.dk-g>.ig-g{display:block;width:96px;height:96px;margin:-8px 0 8px -10px;' + EASE + '}'
            '.dk-g:hover>.ig-g{transform:scale(1.06)}.dk-g>.dk-g-n{position:absolute;right:20px;top:18px}'
            '@media (max-width:600px){.dk-g{display:grid;grid-template-columns:64px minmax(0,1fr);column-gap:14px;'
            'align-items:center}.dk-g>.ig-g{grid-row:1;width:64px;height:64px;margin:0}'
            '.dk-g>b{grid-column:2;padding-right:26px}.dk-g-d,.dk-g-c{grid-column:1/3}.dk-g-d{margin-top:8px}}'),
}
ORDER = ['vu', 'pr', 'steps', 'steps-r', 'steps-nb', 'steps-md', 'steps-proof', 'docs', 'vparts', 'ind-sa', 'ind-card',
         'ind-rp', 'table', 'cycle', 'pest', 'dkg']

OLD = re.compile(r'<style id="ig">.*?</style>\n?', re.S)
MOBFIT = re.compile(r'<style id="mob-fit">.*?</style>\n?', re.S)
SVG_OR_IMG = r'(?:<svg\b.*?</svg>|<img [^>]*>)'


def text(h):
    h = re.sub(r'<[^>]+>', ' ', h).replace('&nbsp;', ' ').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', h).strip()


def src(pre, key, px):
    if key.startswith('lab-'):
        return '%simg/%s.webp' % (pre, key)
    return '%simg/ig-%s-%d.webp' % (pre, key, 128 if px <= 64 else 240)


def img(pre, key, px, cls=None):
    c = ' class="%s"' % cls if cls else ''
    return ('<img%s src="%s" width="%d" height="%d" alt="" loading="lazy" decoding="async">'
            % (c, src(pre, key, px), px, px))


class Page:
    def __init__(self, rel, s):
        self.rel, self.s = rel, s
        self.pre = '../' * rel.count('/')
        self.kinds = set()
        self.n = 0

    def fail(self, msg):
        raise SystemExit('infografika: %s: %s' % (self.rel, msg))

    def section(self, pattern, fn, need=True):
        """Применяет fn к содержимому каждого совпадения pattern (группа 1 — содержимое)."""
        hits = 0

        def one(m):
            nonlocal hits
            hits += 1
            inner = fn(m.group(1))
            return m.group(0)[:m.start(1) - m.start(0)] + inner + m.group(0)[m.end(1) - m.start(0):]
        self.s = re.sub(pattern, one, self.s, flags=re.S)
        if need and not hits:
            self.fail('нет блока ' + pattern[:60])
        return hits

    def sub(self, body, pattern, fn, kind, expect=None):
        hits = [0]

        def one(m):
            hits[0] += 1
            return fn(m)
        out = re.sub(pattern, one, body, flags=re.S)
        if expect is not None and hits[0] != expect:
            self.fail('%s: найдено %d из %d' % (kind, hits[0], expect))
        if hits[0]:
            self.kinds.add(kind)
            self.n += hits[0]
        return out, hits[0]

    def key(self, table, title, what):
        k = table.get(title)
        if not k:
            self.fail('%s: нет иконки для «%s»' % (what, title))
        return k


# ---------------------------------------------------------------- блоки
def b01_vu(p):
    def fn(body):
        total = len(re.findall(r'class="vu-ic"', body))
        out, n = p.sub(body, r'(<span class="vu-ic" aria-hidden="true">)' + SVG_OR_IMG
                       + r'(</span><span class="vu-b"><span class="vu-t">)(.*?)(</span>)',
                       lambda m: m.group(1) + img(p.pre, p.key(VU, text(m.group(3)), 'все услуги'), 64)
                       + m.group(2) + m.group(3) + m.group(4), 'vu', expect=total)
        return out
    p.section(r'<section class="s s-vu"[^>]*>(.*?)</section>', fn, need=False)


def b02_pr(p):
    def card_key(h3):
        t = text(h3)
        return 'ipm' if 'IPM' in t else 'kompleks' if '+' in t else 'dezinsektsiya' if t.startswith('Дезинсекция') \
            else 'deratizatsiya' if t.startswith('Дератизация') else p.fail('цены: карточка «%s»' % t)

    def fn(body):
        nc = len(re.findall(r'<div class="pr-num">', body))
        out, _ = p.sub(body, r'(<div class="pr-num">.*?</div>)(?:<img class="ig-pr"[^>]*>)?(<h3>)(.*?)(</h3>)',
                       lambda m: m.group(1) + img(p.pre, card_key(m.group(3)), 112, 'ig-pr')
                       + m.group(2) + m.group(3) + m.group(4), 'pr', expect=nc)
        nm = len(re.findall(r'class="pr-mini"', body))
        out, _ = p.sub(out, r'(<(?:a|div) class="pr-mini"[^>]*>)(?:<img class="ig-prm"[^>]*>)?(<span><b>)(.*?)(</b>)',
                       lambda m: m.group(1) + img(p.pre, p.key(PR_MINI, text(m.group(3).split('<span class="pr-here"')[0]),
                                                               'другие услуги'), 60, 'ig-prm')
                       + m.group(2) + m.group(3) + m.group(4), 'pr', expect=nm)
        return out
    p.section(r'<section class="s s-pr[^"]*"[^>]*>(.*?)</section>', fn, need=False)


def b03_steps(p):
    if p.rel not in STEPS:
        return
    sid, keys = STEPS[p.rel]
    it = iter(keys)
    used = [0]

    def nxt():
        used[0] += 1
        try:
            return next(it)
        except StopIteration:
            p.fail('шагов больше, чем иконок')

    def li_fn(m):
        rest = m.group(2)
        rest = re.sub(r'^<img class="ig-step-ic"[^>]*>', '', rest)
        rest = re.sub(r'^<span class="nb-ic" aria-hidden="true"><svg\b.*?</svg></span>', '', rest, flags=re.S)
        return m.group(1) + img(p.pre, nxt(), 120, 'ig-step-ic') + rest

    def ol_fn(m):
        cls = m.group(2).split()
        if 'ig-steps' not in cls:
            cls.append('ig-steps')
        if 'r-steps' in cls:
            p.kinds.add('steps-r')
        if 'nb-steps' in cls:
            p.kinds.add('steps-nb')
        if 'md-steps' in cls:
            p.kinds.add('steps-md')
        body, _ = p.sub(m.group(4), r'(<li(?: [^>]*)?>)(.*?)(?=</li>)', li_fn, 'steps')
        return m.group(1) + ' '.join(cls) + m.group(3) + body + m.group(5)

    def card_fn(m):
        return m.group(1) + img(p.pre, nxt(), 120, 'ig-step-ic') + m.group(2)

    # первый список блока — шаги (в «Визите после закрытия» ресторанов — два сценария); другие списки раздела
    # («что подготовить», «что входит») не трогаем
    def first_lists(body):
        if 'class="proof-steps' in body:
            body = re.sub(r'class="proof-steps(?: ig-cards)?"', 'class="proof-steps ig-cards"', body, count=1)
            out, _ = p.sub(body, r'(<article class="d-card">)(?:<img class="ig-step-ic"[^>]*>)?(<span class="f-lbl">)',
                           card_fn, 'steps-proof')
            return out
        lists = 2 if p.rel == 'restorany-i-kafe/index.html' else 1
        parts = re.split(r'(<ol class="[^"]*"[^>]*>.*?</ol>)', body, flags=re.S)
        done, out = 0, []
        for part in parts:
            if done < lists and part.startswith('<ol class="'):
                part, _ = p.sub(part, r'(<ol class=")([^"]*)("[^>]*>)(.*?)(</ol>)', ol_fn, 'steps-ol', expect=1)
                done += 1
            out.append(part)
        if done < lists:
            p.fail('порядок работы: списков %d' % done)
        return ''.join(out)
    p.section(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % sid, first_lists)
    p.kinds.discard('steps-ol')
    if 'steps-proof' not in p.kinds:
        p.kinds.add('steps')
    if used[0] != len(keys):
        p.fail('порядок работы: шагов %d, иконок %d' % (used[0], len(keys)))


def b04_docs(p):
    total = len(re.findall(r'<article class="card doc">', p.s))
    if not total:
        return
    p.s, _ = p.sub(p.s, r'(<article class="card doc"><span class="num">\d+</span><span class="ico">)' + SVG_OR_IMG
                   + r'(</span><h3>)(.*?)(</h3>)',
                   lambda m: m.group(1) + img(p.pre, p.key(DOCS, text(m.group(3)), 'документы'), 100)
                   + m.group(2) + m.group(3) + m.group(4), 'docs', expect=total)


def b05_vent(p):
    if p.rel != 'ochistka-dezinfektsiya-ventilyatsii/index.html':
        return

    def fn(body):
        out, _ = p.sub(body, r'(<article class="d-card">)(?:<img class="ig-v"[^>]*>)?(<span class="dz-lbl">\d+</span><h3>)(.*?)(</h3>)',
                       lambda m: m.group(1) + img(p.pre, p.key(VENT, text(m.group(3)), 'вентиляция'), 120, 'ig-v')
                       + m.group(2) + m.group(3) + m.group(4), 'vparts', expect=6)
        return out
    p.section(r'<section[^>]*id="sostav"[^>]*>(.*?)</section>', fn)


def b06_ind(p):
    kind = IND_PAGES.get(p.rel)
    if kind == 'sa':
        def fn(body):
            out, _ = p.sub(body, r'(<article class="d-card"><p class="sa-ico">)' + SVG_OR_IMG + r'(</p><h3>)(.*?)(</h3>)',
                           lambda m: m.group(1) + img(p.pre, p.key(IND, text(m.group(3)), 'отрасли'), 104)
                           + m.group(2) + m.group(3) + m.group(4), 'ind-sa', expect=6)
            return out
        p.section(r'<section[^>]*id="otrasli"[^>]*>(.*?)</section>', fn)
    elif kind == 'card':
        def fn(body):
            total = len(re.findall(r'<article class="card (?:dzf-ind|v-ind)(?: ig-c)?" data-tilt>' + SVG_OR_IMG, body, re.S))
            out, _ = p.sub(body, r'<article class="card (dzf-ind|v-ind)(?: ig-c)?" data-tilt>' + SVG_OR_IMG + r'(<h3>)(.*?)(</h3>)',
                           lambda m: '<article class="card %s ig-c" data-tilt>' % m.group(1)
                           + img(p.pre, p.key(IND, text(m.group(3)), 'отрасли'), 104, 'ig-ind')
                           + m.group(2) + m.group(3) + m.group(4), 'ind-card', expect=total)
            if total < 7:
                p.fail('отрасли: карточек с иконкой %d' % total)
            return out
        p.section(r'<section[^>]*id="otrasli"[^>]*>(.*?)</section>', fn)
    elif kind == 'rp':
        def fn(body):
            out, _ = p.sub(body, r'(<td data-l="Объект"><span class="rp-ico">)' + SVG_OR_IMG + r'(</span>)([^<]*)',
                           lambda m: m.group(1) + img(p.pre, p.key(IND, text(m.group(3)), 'объекты ППК'), 56)
                           + m.group(2) + m.group(3), 'ind-rp', expect=6)
            return out
        p.section(r'<section[^>]*id="obekty"[^>]*>(.*?)</section>', fn)


def b07_tables(p):
    table = TABLE_DOCS.get(p.rel)
    if not table:
        return

    def td_fn(m):
        inner = m.group(2)
        old = re.match(r'<span class="ig-row"><img [^>]*><span>(.*)</span></span>$', inner, re.S)
        if old:
            inner = old.group(1)
        k = p.key(table, text(inner), 'папка документов')
        return m.group(1) + '<span class="ig-row">' + img(p.pre, k, 60) + '<span>' + inner + '</span></span></td>'

    def fn(body):
        tb = re.search(r'<tbody>(.*?)</tbody>', body, re.S)
        if not tb:
            p.fail('папка документов: нет таблицы')
        rows, n = p.sub(tb.group(1), r'(<tr><td(?: data-l="[^"]*")?>)(.*?)</td>', td_fn, 'table', expect=len(table))
        return body[:tb.start(1)] + rows + body[tb.end(1):]
    p.section(r'<section[^>]*id="dokumenty"[^>]*>(.*?)</section>', fn)


def b08_cycle(p):
    if 'class="cycle"' not in p.s:
        return
    p.s, _ = p.sub(p.s, r'(<div class="node n\d" data-i="\d"><i>)' + SVG_OR_IMG + r'(</i><b>)(.*?)(</b>)',
                   lambda m: m.group(1) + img(p.pre, p.key(NODES, text(m.group(3)), 'круг IPM'), 104)
                   + m.group(2) + m.group(3) + m.group(4), 'cycle', expect=4)


def b09_pests(p):
    def fn(m):
        attrs = m.group(1)
        s = re.search(r'src="([^"]+)"', attrs).group(1)
        name = s.split('/')[-1]
        if name.startswith('ig-pest-'):
            key = name[3:-9]
        else:
            key = PESTS.get(name) or p.fail('вредители: нет макета для ' + name)
        attrs = attrs.replace('src="%s"' % s, 'src="%simg/ig-%s-240.webp"' % (p.pre, key))
        assert 'srcset' not in attrs
        return '<div class="pest-img ig-pi"><img ' + attrs + '>'
    p.s, _ = p.sub(p.s, r'<div class="pest-img(?: ig-pi)?"><img ([^>]*)>', fn, 'pest')


def b10_groups(p):
    if p.rel != 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html':
        return

    def fn(body):
        out, _ = p.sub(body, r'(<a class="card dk-g" href="[^"]*">)(?:<img class="ig-g"[^>]*>)?(<span class="dk-g-n">(\d+)</span>)',
                       lambda m: m.group(1) + img(p.pre, DK_GROUPS[int(m.group(3)) - 1], 96, 'ig-g') + m.group(2),
                       'dkg', expect=8)
        return out
    p.section(r'<section[^>]*id="gruppy"[^>]*>(.*?)</section>', fn)


BLOCKS = [b01_vu, b02_pr, b03_steps, b04_docs, b05_vent, b06_ind, b07_tables, b08_cycle, b09_pests, b10_groups]


def style(kinds):
    return ('<style id="ig">/* инфографика в стиле лаборатории: предметные иконки без фона'
            ' (tools/site/infografika.py, 19.11.2026) */' + ''.join(CSS[k] for k in ORDER if k in kinds) + '</style>\n')


def apply(rel, s, report=None):
    p = Page(rel, OLD.sub('', s))
    for b in BLOCKS:
        b(p)
    if p.kinds:
        m = MOBFIT.search(p.s)
        if not m:
            p.fail('нет строки <style id="mob-fit">')
        line = m.group(0) if m.group(0).endswith('\n') else m.group(0) + '\n'
        p.s = p.s[:m.start()] + line + style(p.kinds) + p.s[m.end():]
    if report is not None:
        report[rel] = (sorted(p.kinds), p.n)
    return p.s


def pages():
    sys.path.insert(0, str(ROOT / 'tools/site'))
    import build_prod  # noqa: E402
    return list(build_prod.PAGES)


def used_images(s, rel):
    pre = '../' * rel.count('/')
    return sorted(set(m[len(pre):] for m in re.findall(r'src="(%simg/ig-[a-z0-9-]+-(?:128|240)\.webp)"' % re.escape(pre), s)))


def main():
    args = sys.argv[1:]
    if args[:1] == ['--check-prod']:
        bad = 0
        files = args[1:]
        for f in files:
            path = pathlib.Path(f)
            parts = path.parts
            rel = '/'.join(parts[parts.index('pkg') + 1:]) if 'pkg' in parts else path.name
            rel = rel[:-len('index.php')] + 'index.html' if rel.endswith('index.php') else rel
            s = path.read_text(encoding='utf-8')
            if apply(rel, s) != s:
                bad += 1
                print('infografika --check-prod: не применено', f)
        print('infografika --check-prod: файлов %d, без инфографики %d' % (len(files), bad))
        sys.exit(1 if bad else 0)
    check = '--check' in args
    changed, report, imgs = [], {}, set()
    for rel in pages():
        f = ROOT / rel
        if not f.exists():
            continue
        s = f.read_text(encoding='utf-8')
        new = apply(rel, s, report)
        imgs.update(used_images(new, rel))
        if new != s:
            changed.append(rel)
            if not check:
                f.write_text(new, encoding='utf-8')
    missing = [i for i in sorted(imgs) if not (ROOT / i).exists()]
    for i in missing:
        print('infografika: нет файла', i)
    with_ig = [r for r in report if report[r][0]]
    if check:
        for rel in changed:
            print('infografika: нужно поправить', rel)
    print('infografika: страниц %d, с инфографикой %d, иконок на страницах %d, файлов иконок %d, %s %d'
          % (len(report), len(with_ig), sum(n for k, n in report.values()), len(imgs),
             'нужно поправить' if check else 'исправлено', len(changed)))
    sys.exit(1 if (check and changed) or missing else 0)


if __name__ == '__main__':
    main()
