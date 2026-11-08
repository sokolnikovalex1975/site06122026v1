#!/usr/bin/env python3
"""Выкладка 08.11.2026 (вторая): «Разработка ППК» — одна страница для ППК и ППК по ХАССП — и ссылка на неё
со страницы образца ППК по ХАССП. Переносит правки в файлы, как их отдаёт сайт перед выкладкой (08.11.2026 ~02:20 МСК,
после выкладок водяных знаков 02:03 и «шаблон программы пест-контроля в PDF»), и собирает пакет pkg/.

  python3 patch-2026-11-08-rppk2.py <папка с файлами с сайта> <dist/timeweb> <pkg>

Файлы с сайта: razrabotka-ppk_index.php, materialy_programma-proizvodstvennogo-kontrolya-haccp_index.php, sitemap.xml.
1. razrabotka-ppk/index.php — страница пересобрана целиком (tools/razrabotka-ppk), берётся из dist/timeweb;
   меню, подвал и блок счётчиков сверяются с файлом с сайта.
2. Образец ППК по ХАССП — в файл с сайта вставляются только два фрагмента: строка со ссылкой на «Разработку ППК»
   под кнопкой «Скачать образец» и карточка «Разработка ППК» первой в «Смотрите также» вместо «Журнала пест-контроля».
3. sitemap.xml — дата изменения образца ППК 2026-11-08.
Блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) в обоих файлах — байт в байт как на сайте.
"""
import pathlib, sys
LIVE, DIST, OUT = (pathlib.Path(a) for a in sys.argv[1:4])
MARK = '<!-- Yandex.Metrika counter + UIS + Radist'
META = '        <p class="p-obr-meta">Нужна программа под\xa0ваш объект целиком? <a href="../../razrabotka-ppk/">Разработаем ППК по\xa0ХАССП</a>\xa0— от\xa019&nbsp;900&nbsp;₽ за\xa03\xa0рабочих дня; ППК для\xa0объекта без\xa0производства\xa0— от\xa05&nbsp;900&nbsp;₽ за\xa01\xa0рабочий день.</p>\n'
CARD = '      <a class="card rel-card" href="../../razrabotka-ppk/"><span class="rel-k">Услуга</span><span class="rel-t">Разработка ППК</span><span class="rel-d">ППК под\xa0ваш объект\xa0— от\xa05\xa0900\xa0₽ за\xa01\xa0рабочий день, ППК по\xa0ХАССП для\xa0общепита и\xa0пищевых производств\xa0— от\xa019\xa0900\xa0₽ за\xa03\xa0рабочих дня.</span><span class="rel-a" aria-hidden="true"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span></a>\n'
ZHUR = '      <a class="card rel-card" href="../../materialy/zhurnal-pest-kontrolya/"><span class="rel-k">Материал</span><span class="rel-t">Журнал <span class="nw">пест-контроля</span></span><span class="rel-d">Образец заполнения и\xa0шаблон в\xa0PDF: 9\xa0разделов на\xa010\xa0листах\xa0— точки контроля, ловушки, предписания.</span><span class="rel-a" aria-hidden="true"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span></a>\n'
ANCHOR = ' 2.3.6.4281-26</span>. Раздел о\xa0дезинсекции и\xa0дератизации и\xa0схему точек заполним после бесплатного обследования.</p>\n'
PROG = '      <a class="card rel-card" href="../../materialy/programma-pest-kontrolya/">'
SM_OLD = ('<loc>https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/materialy/programma-proizvodstvennogo-kontrolya-haccp/</loc>\n'
          '    <lastmod>2026-11-06</lastmod>')
SM_NEW = SM_OLD.replace('2026-11-06', '2026-11-08')


def counters(s):
    assert s.count(MARK) == 1
    return s[s.index(MARK):]


def tail_counters(s):
    """блок счётчиков: от метки до конца файла без скриптов страницы (они идут до метки)"""
    return counters(s)


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode('utf-8'))
    print('ok', rel, len(text.encode('utf-8')))


# 1. «Разработка ППК»
live = (LIVE / 'razrabotka-ppk_index.php').read_text(encoding='utf-8')
new = (DIST / 'razrabotka-ppk' / 'index.php').read_text(encoding='utf-8')
assert counters(new) == counters(live), 'razrabotka-ppk: блок счётчиков отличается от сайта'
write('razrabotka-ppk/index.php', new)

# 2. Образец ППК по ХАССП
live = (LIVE / 'materialy_programma-proizvodstvennogo-kontrolya-haccp_index.php').read_text(encoding='utf-8')
assert live.count(ANCHOR) == 1 and live.count(ZHUR) == 1 and live.count(PROG) == 1
assert 'razrabotka-ppk' not in live.split('<main', 1)[1].split('</main>', 1)[0], 'правка уже есть на сайте'
new = live.replace(ANCHOR, ANCHOR + META, 1)
new = new.replace(ZHUR, '', 1)
new = new.replace(PROG, CARD + PROG, 1)
# обратное преобразование даёт файл с сайта — значит, кроме двух фрагментов, ничего не изменилось
back = new.replace(CARD + PROG, PROG, 1)
i = back.index(PROG)
j = back.index('</a>\n', i) + 5
back = back[:j] + ZHUR + back[j:]
back = back.replace(ANCHOR + META, ANCHOR, 1)
assert back == live, 'образец: лишние изменения'
assert counters(new) == counters(live), 'образец: блок счётчиков отличается от сайта'
write('materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', new)

# 3. sitemap.xml
sm = (LIVE / 'sitemap.xml').read_text(encoding='utf-8')
assert sm.count(SM_OLD) == 1
write('sitemap.xml', sm.replace(SM_OLD, SM_NEW, 1))
