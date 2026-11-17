#!/bin/sh
# Разовая выкладка пакета samoproverka-2026-11-17 на Timeweb (SSH-консоль панели или разовое задание Crontab — удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    5fe013056e1d2ee771f526a3656a549eb48028cb90918e272b81d8ad5098a6de publish_samoproverka.py \
    d774315425a9b85653b4d85b5ed49c763a866b4facff05f09741c5ef96ce867b deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_samoproverka.py --check &&
  python3 publish_samoproverka.py --publish &&
  python3 publish_samoproverka.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
