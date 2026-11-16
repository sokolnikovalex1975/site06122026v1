#!/bin/sh
# Разовая выкладка пакета mushki3-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    d79fa8d251edf8b2f7bea783489193afc41986699ed8b8a3e601a7db4e761061 publish_mushki3.py \
    998e7f38532d26de4ce9dbf73222c05dfa7665540baa5db423bb81417728c237 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki3.py --check &&
  python3 publish_mushki3.py --publish &&
  python3 publish_mushki3.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
