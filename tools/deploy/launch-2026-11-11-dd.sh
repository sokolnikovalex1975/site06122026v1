#!/bin/bash
# Лаунчер выкладки 11.11.2026 («Дератизация и дезинсекция» и пункт меню на всех страницах): один раз из «Терминала» на Mac mini.
LOCK=/tmp/pc-dd-deploy-2026-11-11.lock
mkdir "$LOCK" 2>/dev/null || { echo "уже запускался ($LOCK)"; exit 0; }
cd "$(dirname "$0")" || exit 1
[ -f .netrc ] || { echo "нет .netrc"; echo "deploy rc=10" > status.txt; exit 10; }
bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
rm -P .netrc 2>/dev/null || rm -f .netrc
[ $rc -eq 0 ] && mv run_all.sh run_all.sh.done
echo DONE >> status.txt
cat status.txt
