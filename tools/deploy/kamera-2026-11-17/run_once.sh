#!/bin/sh
# Разовая выкладка пакета kamera-2026-11-17 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    503bd6b6b1aaadc512fcfa8cdb33342e67ab47dbe9f46609a06b11944e7acd02 publish_kamera.py \
    19da98246cc1e5a5722e9767566cf82e9bea1f4847c8cc2ae0bc0cdb0219c316 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_kamera.py --check &&
  python3 publish_kamera.py --publish &&
  python3 publish_kamera.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
