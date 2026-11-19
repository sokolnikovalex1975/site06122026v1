#!/bin/sh
# Разовая выкладка 19.11.2026 заданием «Crontab» панели Timeweb (удалить задание после запуска):
# пакет zashchita-2026-11-19 — страница «Защита от проникновения грызунов» (решение владельца 19.11.2026).
# Файлы скачиваются с GitHub по коммиту fad6dec62820d07c9a4aaa4f0f1c789b36971f39 в ~/pestcontrol-zashchita-2026-11-19/ (вне public_html);
# сумма run_once.sh проверяется здесь, publish_zashchita.py и deploy_payload.json — в run_once.sh.
cd "$HOME" || exit 1
L="$HOME/pestcontrol-boot-zashchita-2026-11-19.log"
[ -e "$HOME/pestcontrol-boot-zashchita-2026-11-19.done" ] && exit 0
date > "$HOME/pestcontrol-boot-zashchita-2026-11-19.done"
B="https://raw.githubusercontent.com/sokolnikovalex1975/site06122026v1/fad6dec62820d07c9a4aaa4f0f1c789b36971f39/tools/deploy/zashchita-2026-11-19"
D="$HOME/pestcontrol-zashchita-2026-11-19"
get() { curl -fsSL --retry 3 -o "$2" "$1" || wget -q -O "$2" "$1"; }
{
  echo "boot start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  { [ -e "$D" ] || { mkdir "$D" && get "$B/publish_zashchita.py" "$D/publish_zashchita.py" &&
      get "$B/deploy_payload.json" "$D/deploy_payload.json" && get "$B/run_once.sh" "$D/run_once.sh"; }; } &&
  printf '%s  %s\n' ab8fc6c3014789532c9703bfe03453d1f0ea02da59c9f80e95dbbca16bc84e60 "$D/run_once.sh" | sha256sum -c - &&
  sh "$D/run_once.sh"; cat "$D/run_once.log"
  echo "boot end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > "$L" 2>&1
