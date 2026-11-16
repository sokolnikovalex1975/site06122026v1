#!/bin/sh
# Разовая выкладка пакета mushki-2026-11-16 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    0046d731dd391e035e1595e13353c2a5c17326075afb0d27927a9d59084cafb5 publish_mushki.py \
    a396e291315f9e5c5d7a845e3eb46dbd6fccc5deb3dab84e617c85dcf4baf4b9 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki.py --check &&
  python3 publish_mushki.py --publish &&
  python3 publish_mushki.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
