#!/bin/sh
# Разовая выкладка пакета mukhi-2026-11-13 заданием Crontab панели Timeweb (SSH-консоль недоступна из облака).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    8cbf823752a7f459addf84e8376c789b075902245ae111f2898c4d278c6e164d publish_mukhi.py \
    9fe77d63ff2243f85017fa1f39127c444db92189fc98ffcae8981df57af94ce2 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mukhi.py --check &&
  python3 publish_mukhi.py --publish &&
  python3 publish_mukhi.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
