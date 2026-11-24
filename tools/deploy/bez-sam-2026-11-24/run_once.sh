#!/bin/sh
# Razovaya vykladka paketa bez-sam-2026-11-24 (SSH-konsol paneli Timeweb): 14 stranic + search-index.json + sitemap.xml.
# Povtornyj zapusk nichego ne delaet: metka run_once.done sozdaetsya do vykladki.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    a55fda2f8e81c152f7e697249dd6f6208152462f890aec52fbe7d9224b25f2bc publish_bez_sam.py \
    000dc53dfd4f84086e5c67c82999fcf85c04b52a0e9f755900c23bd1f3b7da12 deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_bez_sam.py --check &&
  python3 publish_bez_sam.py --publish &&
  python3 publish_bez_sam.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
