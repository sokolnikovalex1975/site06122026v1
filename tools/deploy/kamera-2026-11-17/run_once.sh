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
    3f8e7c7715af80109984a7be707d2cdf1e02d62a8bd1e2f1b68b39b4b4a1396d deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_kamera.py --check &&
  python3 publish_kamera.py --publish &&
  python3 publish_kamera.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
