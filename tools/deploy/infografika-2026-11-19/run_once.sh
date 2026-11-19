#!/bin/sh
# Разовая выкладка пакета infografika-2026-11-19 заданием Crontab панели Timeweb или из SSH-консоли (задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    c8ce64ff3d27ff6c009c3722e58b29941749a515d3ed5e650e6792d0c1622f4c publish_infografika.py \
    0d2a96626c851242c6c2e3abb7fd9b1563b6edd478bb7a8e0ab3cd286cf02bf7 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_infografika.py --check &&
  python3 publish_infografika.py --publish &&
  python3 publish_infografika.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
