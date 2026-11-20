#!/bin/sh
# Разовая выкладка пакета ppk-bez-vyezda-2026-11-20 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    30e6737911877692479c5cb477ed73743f94f47970e10f29e74a48a5376f5761 publish_ppk_bez_vyezda.py \
    6b3085ca0e92aa615ec83a14589c25954dd1c12dd5f887dcff89c355f4016875 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ppk_bez_vyezda.py --check &&
  python3 publish_ppk_bez_vyezda.py --publish &&
  python3 publish_ppk_bez_vyezda.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
