#!/bin/sh
# Разовая выкладка пакета ppk-haccp-bez-vyezda-2026-11-20 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    3899275b7991224da3520fb542cb4c205e0aa3975e204484d043dfefae4c2d22 publish_ppk_haccp_bez_vyezda.py \
    f35a80bef050f5ddf6f0fe9d5a74475073095c5e9cf4d1724236481c7ba68660 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ppk_haccp_bez_vyezda.py --check &&
  python3 publish_ppk_haccp_bez_vyezda.py --publish &&
  python3 publish_ppk_haccp_bez_vyezda.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
