#!/bin/sh
# Разовая выкладка пакета zashchita-2026-11-19 заданием Crontab панели Timeweb (удалить задание после запуска).
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    ac8243d265058f11fe1db43ae5b1f0a52866538629f9ecf0a0f1d45ad7a73898 publish_zashchita.py \
    d3c77449525e999165710edebbb4a4e5909cfd76a6383fda37abfe24fd580b54 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zashchita.py --check &&
  python3 publish_zashchita.py --publish &&
  python3 publish_zashchita.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
