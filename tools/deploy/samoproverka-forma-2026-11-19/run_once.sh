#!/bin/sh
# Разовая выкладка пакета samoproverka-forma-2026-11-19 (SSH-консоль или задание Crontab панели Timeweb; задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    4e979b4dbc6e28c282dbc7933f7ab8ca14790da56b4f1bcb5460374e45759cbc publish_samoproverka_forma.py \
    f268194e849243d7615c6f3cebd77d3ce97387915e171ef6c359fbd428de2ccc deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_samoproverka_forma.py --check &&
  python3 publish_samoproverka_forma.py --publish &&
  python3 publish_samoproverka_forma.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
