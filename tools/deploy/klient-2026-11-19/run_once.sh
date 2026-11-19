#!/bin/sh
# Разовая выкладка пакета klient-2026-11-18 заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    3c6cda400cc316a08eba941bdf435cfa70adb4f1a0d01acf92dc576e2a0f2b94 publish_klient.py \
    647bd72df1bdfb666462dccfbef19ae1c527958897b9444c2b349e6b61b918f3 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_klient.py --check &&
  python3 publish_klient.py --publish &&
  python3 publish_klient.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
