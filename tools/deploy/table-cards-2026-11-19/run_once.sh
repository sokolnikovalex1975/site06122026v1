#!/bin/sh
# Разовая выкладка пакета table-cards-2026-11-19 на Timeweb (SSH-консоль панели или разовое задание Crontab — удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    7d9336b4bcf76f3c05b340cdb6c453797ab5f04b35db305d2aacd390f63f1b02 publish_table_cards.py \
    51b337d735f21c545afc11f845382061729b0966ab84ffd68dc300b995463955 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_table_cards.py --check &&
  python3 publish_table_cards.py --publish &&
  python3 publish_table_cards.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
