#!/bin/sh
# Разовая выкладка пакета kamera-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    b4fba44b75899f601c24dee225ded8fcc0acdb90e6d0bb49df9983836975fab8 publish_kamera.py \
    0eea92294de13871fb12c1038263e926c2f76180a6807b7a703ee88711e1b24b deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_kamera.py --check &&
  python3 publish_kamera.py --publish &&
  python3 publish_kamera.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
