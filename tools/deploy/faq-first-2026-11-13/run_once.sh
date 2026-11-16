#!/bin/sh
# Разовая выкладка пакета faq-first-2026-11-13 заданием Crontab панели Timeweb (удалить задание после запуска).
# Пакет пересобран от рабочего сайта 17.11.2026. Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    bce81caf4563e23fc9c0f1dbff44b27da1a17c25d333c17dbd01ece84ebe85f4 publish_faq_first.py \
    f4eb26c9b3eaf08f121001e813fc6a0d9ad9187ae725bb6242100743eed01c6d deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_faq_first.py --check &&
  python3 publish_faq_first.py --publish &&
  python3 publish_faq_first.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
