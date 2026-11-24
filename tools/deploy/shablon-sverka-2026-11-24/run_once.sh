#!/bin/sh
# Razovaya vykladka paketa shablon-sverka-2026-11-24 (SSH-konsol paneli Timeweb): programma pest-kontrolya + search-index.json.
# Povtornyj zapusk nichego ne delaet: metka run_once.done sozdaetsya do vykladki.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    f158e48452de99dfdf247ef1042bd68de52c4ffc5e175c93a4c6e08fa6528125 publish_bez_sam.py \
    ea174d76546982b9981a0800a61a0073f85fd6cad9efc54afddf06707bcd4590 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_bez_sam.py --check &&
  python3 publish_bez_sam.py --publish &&
  python3 publish_bez_sam.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
