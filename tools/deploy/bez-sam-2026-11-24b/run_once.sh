#!/bin/sh
# Razovaya vykladka paketa bez-sam-2026-11-24b (SSH-konsol paneli Timeweb): 6 stranic, nerazryvnye probely.
# Povtornyj zapusk nichego ne delaet: metka run_once.done sozdaetsya do vykladki.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done
{
  echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf '%s  %s\n%s  %s\n' \
    f99d58868276db2664fbf138a960154a5cabe54792f310a60e26c2f7b63f2f48 publish_bez_sam.py \
    ec1afb7a1f86b5c53d6ecde5b40606bf5e2d1c48139a00e5adb68b2bcb720bdb deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_bez_sam.py --check &&
  python3 publish_bez_sam.py --publish &&
  python3 publish_bez_sam.py --check
  echo "exit: $?"
  echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > run_once.log 2>&1
