#!/bin/sh
# Разовая выкладка пакета home-mobile-2026-11-20 заданием Crontab панели Timeweb или из SSH-консоли.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    6b5d348b2ae7cee53978bfb28a19f32f6925aa2abc3f391567a2bffb932ecf8b publish_home_mobile.py \
    84bb44e2b9b281db425460876c81db70c70f686c33c6cd9b80464df93557014d deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_home_mobile.py --check &&
  python3 publish_home_mobile.py --publish &&
  python3 publish_home_mobile.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
