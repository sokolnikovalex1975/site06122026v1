#!/bin/sh
# Разовая выкладка пакета mushki2-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    249d8d65c083011f6ca4755351ba437b1d45bc40bf45017a271ba0dd89b8e954 publish_mushki2.py \
    abd7f773f84d9574397d312bade9fa2d6d8cf8e2fb54f3eca307c2ab5ca335be deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki2.py --check &&
  python3 publish_mushki2.py --publish &&
  python3 publish_mushki2.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
