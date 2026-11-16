#!/bin/sh
# Разовая выкладка пакета zagolovok-2026-11-13 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    bc1b04b925aa2f3230d66cb42e67302ff31fb8bf9e76d303511fcb1e34128085 publish_zagolovok.py \
    dca5abdfc9d520da2298c060b0638f2113b16d494adcb5f1cab459801196d8fb deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zagolovok.py --check &&
  python3 publish_zagolovok.py --publish &&
  python3 publish_zagolovok.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
