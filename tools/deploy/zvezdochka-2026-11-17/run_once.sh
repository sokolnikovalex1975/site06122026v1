#!/bin/sh
# Разовая выкладка пакета zvezdochka-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    5a90e990cce0192a9a849f6bff6b1f5ed556c113abf5fba748d01a7d91311896 publish_zvezdochka.py \
    9404ea6baebbbf8f417bef55db14b3085dac52e2fb8caf3f41944020b778f59f deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zvezdochka.py --check &&
  python3 publish_zvezdochka.py --publish &&
  python3 publish_zvezdochka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
