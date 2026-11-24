#!/bin/sh
# Razovaya vykladka paketa stati-2026-11-24 (SSH-konsol paneli Timeweb): 2 stati, 10 kartinok, materialy, pishchevoe-proizvodstvo, sitemap.xml, search-index.json.
# Povtornyj zapusk nichego ne delaet: metka run_once.done sozdaetsya do vykladki.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    8d43385ae6cf18b864da4e703663dd35599f3c20ff76f5b21e924580beec05d4 publish_stati.py \
    76501ce2ec4fbc2e4a3b1143b57982f1fcdaee3288d2c0babcc064b51f88a770 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_stati.py --check &&
  python3 publish_stati.py --publish &&
  python3 publish_stati.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
