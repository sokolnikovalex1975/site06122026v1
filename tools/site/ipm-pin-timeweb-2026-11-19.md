# Круг «IPM — цикл визита» закреплён при прокрутке — выкладка на Timeweb (19.11.2026)

Команды владельца 19.11.2026: «Схема справа… Нужно сделать так, чтобы эта сама схема замирала, пока прокручивается
контент слева» (главная), затем «Сделай на „Дератизации“ такое же закрепление круга, как на главной. И выложи обе
страницы с закреплённым кругом на Timeweb».

## Что сделано

- `tools/site/ipm_pin.py` — главная (#podhod «Пест-менеджмент по системе IPM») и «Дератизация» (#podhod «Четыре шага
  инженера на каждом визите»). Компьютер (от 1025 px): круг закреплён по центру экрана, шаги прокручиваются, точка идёт
  по кольцу от значка к значку, номер шага меняется. Планшет и телефон — прежнее поведение. app.min.js, style.css и
  другие страницы не менялись.
- Пакет `tools/deploy/ipm-pin-2026-11-19/` (`prepare-2026-11-19-ipm-pin.py`, `publish_ipm_pin.py`): страницы сняты с
  рабочего сайта по HTTPS, по 2 точные замены; Метрика, UIS, Radist, телефон и почта — без нарушений до и после,
  закон независимости соблюдён.

## Публикация

**Опубликовано 19.11.2026 в 20:16:19 МСК** через SSH-консоль панели Timeweb (сохранённый вход «Timeweb: основной аккаунт
cd59839»): папка `~/pestcontrol-ipm-pin-2026-11-19/` (вне `public_html`), четыре файла скачаны с GitHub по коммиту
`fb00ff1` и сверены (`publish_ipm_pin.py` `1a6884d2…`, `deploy_payload.json` `8542b493…`, `run_once.sh` `d7da2efc…`,
`MANIFEST.txt` `52833c5a…`); `--check` до запуска — PRECHECK OK 2/2. Запуск `LANG=C sh run_once.sh`. Задания «Crontab»
не создавались.

```
start: 2026-11-19 20:16:19 MSK
publish_ipm_pin.py: OK
deploy_payload.json: OK
Python 3.6.9
PRECHECK OK: 2/2 original and resulting checksums verified
PRECHECK OK: 2/2 original and resulting checksums verified
BACKUP OK: 2/2 outside public_html
PUBLISHED: 2/2 checksums verified
BACKUP: /home/c/cd59839/pestcontrol-ipm-pin-2026-11-19/backup
ALREADY PUBLISHED: 2/2 checksums match
exit: 0
end: 2026-11-19 20:16:19 MSK
```

Временных файлов `*-stage` в `public_html` нет.

- **HTTPS:** `/`, `/deratizatsiya/` и те же адреса с `?utm_source=check` — 4/4 HTTP 200, SHA-256 как в пакете;
  `tracking_laws` (Метрика 113675622, UIS, Radist, телефон и почта) и закон независимости — без нарушений.
- **Браузер на рабочем сайте** (счётчики в тесте заблокированы, чтобы не портить статистику): 1440 px — круг стоит на
  месте ~1100 px прокрутки на обеих страницах, шаги 01→04; 390 px — прежнее поведение; ошибок JS и прокрутки вбок нет.

## Откат

`python3 "$HOME/pestcontrol-ipm-pin-2026-11-19/publish_ipm_pin.py" --rollback`
