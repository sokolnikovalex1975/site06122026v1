#!/bin/sh
# Разовая выкладка пакета seo-2026-11-22 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    434a62675fd4a09128a3825ac2bd7a415d21f7e80c108295d4bf350ee19177a0 publish_seo.py \
    b5b1106834817fb5c208d604f917b2c01fcc2804495f5af18b8f6ad2567fa0bb deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_seo.py --check &&
  python3 publish_seo.py --publish &&
  python3 publish_seo.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
