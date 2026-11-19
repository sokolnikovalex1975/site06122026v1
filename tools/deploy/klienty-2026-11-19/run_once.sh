#!/bin/sh
# Разовая выкладка пакета klienty-2026-11-19 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    2e471579d902e1cc83ff08d8d63b307749b6bb5882d2761ee7dcb37b048f64ea publish_klienty.py \
    ec267e7af2486993f4b034ff9d82b842d26f43a7e9725664af5724ee6b4ae6b0 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_klienty.py --check &&
  python3 publish_klienty.py --publish &&
  python3 publish_klienty.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
