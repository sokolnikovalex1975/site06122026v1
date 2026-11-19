#!/bin/sh
# Разовая выкладка пакета ipm-pin-2026-11-19 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    1a6884d2bd85bebbcb7ef3e70f70e631b02487971ea9936fadfa386038443147 publish_ipm_pin.py \
    8542b49365a68fdf6e6a7e444ea50d66e868c704f97bb0ce28ed87ef08778006 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ipm_pin.py --check &&
  python3 publish_ipm_pin.py --publish &&
  python3 publish_ipm_pin.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
