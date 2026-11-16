#!/bin/sh
# Разовая выкладка пакета nodim-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    21fce751d712201e5b05cb90a0f09274eb224acbcc2a61ce177cf2daff4abb81 publish_nodim.py \
    c31eab1a0a52de0d0f85d66ae067267ca8af25d57133c04c031fb5bf40803b62 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_nodim.py --check &&
  python3 publish_nodim.py --publish &&
  python3 publish_nodim.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
