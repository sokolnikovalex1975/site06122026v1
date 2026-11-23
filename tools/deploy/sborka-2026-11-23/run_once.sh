#!/bin/sh
# Разовая выкладка пакета sborka-2026-11-23 (SSH-консоль панели Timeweb): сайт = сборка GitHub, 112 файлов.
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    8acd9603606fb734d9cd59f7e8eebecd39b93b708d96180ee29a6923ee8fd0a8 publish_sborka.py \
    14492449ebcd87f94535523e1417cf355fa2d184e5368efad668161da9f763d4 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_sborka.py --check &&
  python3 publish_sborka.py --publish &&
  python3 publish_sborka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
