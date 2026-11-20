#!/bin/sh
# Разовая выкладка пакета galochka-2026-11-20 (SSH-консоль панели Timeweb). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    0373ce999ec39ff13cb2fc0cc7218031ef1fad160e5219e995c039b46ee5299b publish_galochka.py \
    fe6dc6e4895debca1f748a6d107606cdf027f163b1297ca6d5a51d32beac2bea deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_galochka.py --check &&
  python3 publish_galochka.py --publish &&
  python3 publish_galochka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
