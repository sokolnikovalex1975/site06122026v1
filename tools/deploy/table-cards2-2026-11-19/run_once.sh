#!/bin/sh
# Разовая выкладка пакета table-cards2-2026-11-19 на Timeweb (SSH-консоль панели или разовое задание Crontab — удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    198a920d62917e0a3a838e659a91c2734736e4e61abf830dce878ef4a4f0d852 publish_table_cards2.py \
    60a3fbff1802a87a1a7ee0b9ad105ea17f898cd07e932afbd86accbdeab90b60 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_table_cards2.py --check &&
  python3 publish_table_cards2.py --publish &&
  python3 publish_table_cards2.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
