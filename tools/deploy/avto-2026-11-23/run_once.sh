#!/bin/sh
# Разовая выкладка пакета avto-2026-11-23 на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    20e4376be94c655f304181be7caa64cb416299667cf2d05b6b4e46f65f98a34b publish_avto.py \
    cd6b1437f5f69771407ac2d055972d4452b40bc28c4d164451d8d33d3be06b71 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_avto.py --check &&
  python3 publish_avto.py --publish &&
  python3 publish_avto.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
