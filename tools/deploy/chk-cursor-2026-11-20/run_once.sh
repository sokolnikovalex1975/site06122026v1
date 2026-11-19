#!/bin/sh
# Разовая выкладка пакета chk-cursor-2026-11-20 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    5d72be6fd7f02a7bcc99d3d08827e7a1bbdd9ab9b57f3eced4d9f7ce6946804a publish_chk_cursor.py \
    9b72627ec6ab366fdc22e6e8eaba09b0960be502ae942f70c04ffa98bf5287fd deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_chk_cursor.py --check &&
  python3 publish_chk_cursor.py --publish &&
  python3 publish_chk_cursor.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
