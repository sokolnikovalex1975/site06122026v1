# Широкие таблицы на планшете — выкладка на Timeweb (19.11.2026)

Команда владельца 19.11.2026: «Исправь прокрутку вбок на вентиляции и дезинсекции в превью, потом покажи мне» — сделано
на GitHub в коммите `d3f6cfb` (`tools/site/table_cards.py`, `CHANGES.md`). Команда на выкладку 19.11.2026: «Выкладывай эту
правку на TimeWeb».

## Что выкладывается

2 страницы: `/ochistka-dezinfektsiya-ventilyatsii/` и `/dezinsektsiya/`. Стили встроены в страницы, поэтому `style.css`,
скрипты, версии `?v=` и другие страницы не меняются. В каждой странице одна точная замена: строка `<style id="t-inset">`
→ та же строка и сразу после неё строка `<style id="t-cards">` (та же, что в превью GitHub): на 601–760 px таблицы
`.v-freq` (вентиляция), `.dz-methods` и `#sanpin .d-table` (дезинсекция) — карточками, как на телефоне. Остальное — байт
в байт как на рабочем сайте (после выкладки `samoproverka-forma-2026-11-19`: вентиляция `634babbc…`, дезинсекция
`e767c2b2…`).

## Пакет

- Сборка: `python3 tools/deploy/prepare-2026-11-19-table-cards.py <новая папка>` — страницы снимаются с рабочего сайта по
  HTTPS. Проверки: участок ровно один раз, результат совпадает с `table_cards.apply()`, строка стилей — как в превью,
  обратная замена даёт исходник байт в байт, `tracking_laws` (Метрика 113675622, UIS, Radist, телефон и почта) и закон
  независимости — без нарушений до и после.
- `tools/deploy/table-cards-2026-11-19/`: `MANIFEST.txt`, `deploy_payload.json`, `run_once.sh`; серверный скрипт
  `tools/deploy/publish_table_cards.py` (только стили, без скриптов, счётчиков и контактов; сверка SHA-256 до и после,
  резервные копии вне `public_html`, при ошибке — возврат файлов; Python 3.6, сообщения ASCII).
- Суммы: вентиляция `634babbc…` → `999ebe99…` (+654 байт), дезинсекция `e767c2b2…` → `851ee700…` (+884 байт).

## Проверка пакета до выкладки

- Скрипт выкладки на копии `public_html` (`LANG=C`): PRECHECK, BACKUP, PUBLISHED 2/2, повтор — ALREADY PUBLISHED, файлы
  совпали с `pkg/` байт в байт; `--rollback` вернул исходники байт в байт; на изменённом файле — остановка без изменений.
- `table_cards_test.mjs` на страницах пакета (стили и скрипты с рабочего сайта, счётчики на время проверки убраны):
  2 страницы × 24 ширины (320–1920 px) — прокрутки вбок нет, на 601–760 px карточки, до 600 px и от 761 px размеры таблиц
  и высота страницы как на текущем сайте (±1 px). Нарушений 0.

## Публикация на рабочем сайте

**Опубликовано 19.11.2026 в 15:48:22 МСК** через SSH-консоль панели Timeweb (`hosting.timeweb.ru/console`, сохранённый вход
«Timeweb: основной аккаунт cd59839»): папка `~/pestcontrol-table-cards-2026-11-19/` (вне `public_html`), четыре файла
скачаны с GitHub по коммиту `914577d` и сверены (`publish_table_cards.py` `7d9336b4…`, `deploy_payload.json` `51b337d7…`,
`run_once.sh` `c46b4075…`, `MANIFEST.txt` `5bc80061…`); `--check` до запуска — PRECHECK OK 2/2. Запуск `LANG=C sh
run_once.sh`. Задания «Crontab» не создавались и не менялись.

```
start: 2026-11-19 15:48:22 MSK
publish_table_cards.py: OK
deploy_payload.json: OK
Python 3.6.9
PRECHECK OK: 2/2 original and resulting checksums verified
PRECHECK OK: 2/2 original and resulting checksums verified
BACKUP OK: 2/2 outside public_html
PUBLISHED: 2/2 checksums verified
BACKUP: /home/c/cd59839/pestcontrol-table-cards-2026-11-19/backup
ALREADY PUBLISHED: 2/2 checksums match
exit: 0
end: 2026-11-19 15:48:22 MSK
```

Временных файлов `*-stage` в `public_html` нет.

- **HTTPS**: обе страницы (`/<страница>/` и `?utm_source=check`) — HTTP 200, SHA-256 как в пакете; `tracking_laws` — без
  нарушений (Метрика 113675622, UIS, Radist, телефон и почта), закон независимости — без нарушений.
- **`table_cards_test.mjs` на рабочем сайте** (запросы к счётчикам отменяются): 2 страницы × 24 ширины — прокрутки вбок
  нет, на 601–760 px карточки, шире — таблица; нарушений 0 (ложные 502 Timeweb из облака — повтор по одной странице и
  ширине, `ONLY=…`, со 2–5-й попытки — 0).

## Откат

```sh
python3 "$HOME/pestcontrol-table-cards-2026-11-19/publish_table_cards.py" --rollback
```
