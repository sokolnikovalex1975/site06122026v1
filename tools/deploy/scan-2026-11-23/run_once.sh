#!/bin/sh
# Разовая выкладка пакета scan-2026-11-23 (SSH-консоль панели Timeweb).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    7c005d5d0b477c3ceff389d7898e196d6a65745878c7fd9dc4c1f37dfca855c4 publish_scan.py \
    0c6170f41910e9f5e1fb57ba7949cffdb9228db8c02bd05a0143ab77a67a04be deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_scan.py --check &&
  python3 publish_scan.py --publish &&
  python3 publish_scan.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
