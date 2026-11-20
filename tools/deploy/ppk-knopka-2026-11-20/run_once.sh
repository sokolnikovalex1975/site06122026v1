#!/bin/sh
# Разовая выкладка пакета ppk-knopka-2026-11-20 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    69e50904eeaf8a92b42572814806427feb513f26f683c679e4fc9342f6fea7de publish_ppk_knopka.py \
    733b23f05730a19d528f2d93c6da347b665f35affa4006fe0327ec1f793b0c7d deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ppk_knopka.py --check &&
  python3 publish_ppk_knopka.py --publish &&
  python3 publish_ppk_knopka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
