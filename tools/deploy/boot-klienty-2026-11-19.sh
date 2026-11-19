#!/bin/sh
# Разовая выкладка 19.11.2026 заданием «Crontab» панели Timeweb (удалить задание после запуска):
#   1) klient-2026-11-19 — «Правки для клиента и без затемнения на внутренних страницах телефона» (согласовано 18.11.2026);
#   2) klienty-2026-11-19 — блок «Наши клиенты» (согласовано 19.11.2026), только если пакет 1 закончился с exit: 0.
# Файлы пакетов скачиваются с GitHub по коммиту a35a70a8629b11f72476a60b01116bcda9cb4a66 в папки вне public_html;
# суммы run_once.sh проверяются здесь, суммы publish_*.py и deploy_payload.json — в run_once.sh.
# Повторный запуск ничего не делает (метка ~/pestcontrol-boot-klienty-2026-11-19.done).
cd "$HOME" || exit 1
L="$HOME/pestcontrol-boot-klienty-2026-11-19.log"
[ -e "$HOME/pestcontrol-boot-klienty-2026-11-19.done" ] && exit 0
date > "$HOME/pestcontrol-boot-klienty-2026-11-19.done"
B="https://raw.githubusercontent.com/sokolnikovalex1975/site06122026v1/a35a70a8629b11f72476a60b01116bcda9cb4a66/tools/deploy"
get() { curl -fsSL --retry 3 -o "$2" "$1" || wget -q -O "$2" "$1"; }
step() {
  k="$1"; sum="$2"; D="$HOME/pestcontrol-$k-2026-11-19"
  [ -e "$D" ] && { echo "$k: folder exists, skip download"; } || {
    mkdir "$D" &&
    get "$B/$k-2026-11-19/publish_$k.py" "$D/publish_$k.py" &&
    get "$B/$k-2026-11-19/deploy_payload.json" "$D/deploy_payload.json" &&
    get "$B/$k-2026-11-19/run_once.sh" "$D/run_once.sh" || return 1; }
  printf '%s  %s\n' "$sum" "$D/run_once.sh" | sha256sum -c - || return 1
  sh "$D/run_once.sh"
  cat "$D/run_once.log"
  grep -q '^exit: 0$' "$D/run_once.log"
}
{
  echo "boot start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  step klient 5580d7d256f12876172e7dc34544a42e45548b3fdd225f7442d6f733a28ab27e && step klienty 15400afd8743e152e37b2d46920952992a277b8b2152705a8e05b1f8f1bc9c8f
  echo "boot exit: $?"
  echo "boot end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > "$L" 2>&1
