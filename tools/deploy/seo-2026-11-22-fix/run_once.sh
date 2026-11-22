#!/bin/sh
# Разовая выкладка пакета seo-2026-11-22-fix на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    05b2ec6716b9e2b891f03dff0f2eabd35ba7ab5d47e7ad4577c63bb15db4aeb5 fix_htaccess.py \
    60ac35c80f19875fc7fa924f783b9778e2dd51d9123376c7a31127ca0c3c6fc6 htaccess.new | sha256sum -c - &&
  python3 fix_htaccess.py --check &&
  python3 fix_htaccess.py --publish &&
  python3 fix_htaccess.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
