#!/bin/sh
# Разовая выкладка пакета title-h1-2026-11-19 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    ef0fa56c586ca9030da5c514484946f18ca91308e0e4027904d790f29354e6b5 publish_title_h1.py \
    6327c9429e763fd8adbabfaf6a4c4475a07b8a94f8670d329e77c639608efcef deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_title_h1.py --check &&
  python3 publish_title_h1.py --publish &&
  python3 publish_title_h1.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
