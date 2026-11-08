# Журнал пест-контроля: образец заполнения и шаблон (форма ЖПК-01)

Образец и шаблон печатаются из одного HTML, поэтому совпадают лист в лист: шаблон — тот же документ
с `<body class="tpl">`, где записи, подписи, пометки маркером и отметка «Образец заполнения» скрыты
(`visibility:hidden`, геометрия листов не меняется).

На каждом листе: шапка с логотипом, крупными телефоном +7 (495) 104-35-70 и адресом пестконтроль-центр.рф;
подвал с реквизитами ООО «Центр дезинфекционных услуг», лицензией и графой «Лист №»; фиолетовый диагональный
водяной знак «пестконтроль-центр.рф» (векторный контур, не текст — не мешает копированию и поиску) поверх
таблиц и плашек (`.wm { z-index: 5 }`, с 08.11.2026; проверка — `python3 tools/docs_brand/check_watermark.py`).

| Файл | Что делает |
|---|---|
| `build_journal.py <fonts_dir> <out_dir>` | собирает `journal.html` (10 листов A4, данные образца) |
| `wm.py` | водяной знак: контур надписи из шрифта Inter (fontTools) |
| `render_journal.mjs <out_dir>` | печатает `obrazets.pdf` и `shablon.pdf` (Playwright/Chromium), добивает таблицы пустыми строками до подвала, выводит JSON-проверку переполнений |
| `finalize.py <out_dir> <repo_root>` | метаданные PDF, сжатие, копирование в `materialy/zhurnal-pest-kontrolya/`, превью WebP в `img/` |
| `og_image.mjs` | `img/zhurnal-og.jpg` 1200×630 |
| `build_zhurnal.py <repo_root>` | страница `/materialy/zhurnal-pest-kontrolya/` и карточка в `/materialy/`; затем `python3 tools/menu/apply_menu.py` |

```bash
python3 tools/zhurnal/build_journal.py fonts /tmp/zh && node tools/zhurnal/render_journal.mjs /tmp/zh
python3 tools/zhurnal/finalize.py /tmp/zh . && python3 tools/zhurnal/build_zhurnal.py . && python3 tools/menu/apply_menu.py
```

Цели Метрики (113675622) при скачивании: `zhurnal_obrazets`, `zhurnal_shablon`.
