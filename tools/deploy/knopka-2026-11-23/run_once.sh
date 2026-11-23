#!/bin/sh
# Разовая выкладка пакета knopka-2026-11-23 (SSH-консоль панели Timeweb).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    902bbd5ace144e3b1ee93f79b0c72a5b292d08c13082a35566d32211bb02f0b2 publish_knopka.py \
    10f901cf0d594f1bc7f4aeb46badbbc731d2b7fd1fa832e02d3e4f19a0df5441 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_knopka.py --check &&
  python3 publish_knopka.py --publish &&
  python3 publish_knopka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
