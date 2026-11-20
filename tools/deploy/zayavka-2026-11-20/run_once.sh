#!/bin/sh
# Разовая выкладка пакета zayavka-2026-11-20 (SSH-консоль или задание Crontab панели Timeweb; задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    7c2b262cc22d25125f1ed46185bd572833405969c1cd5715c517b0ae66346def publish_zayavka.py \
    0158f00593f0cbde07476d570ed27dba85ddbcd4c95da3359ed5c3009dbf3eda deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zayavka.py --check &&
  python3 publish_zayavka.py --publish &&
  python3 publish_zayavka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
