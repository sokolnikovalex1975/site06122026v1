#!/bin/sh
# Разовая выкладка пакета shapka-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    117a3d2e2ead9d5b601e2e5f08ea7b63e7ba52001e703a9cc48d97f31df851d6 publish_shapka.py \
    8b38c4857a57d709548f9a2125dad12bca0786880d64d74bd3c6064f37bfa223 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_shapka.py --check &&
  python3 publish_shapka.py --publish &&
  python3 publish_shapka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
