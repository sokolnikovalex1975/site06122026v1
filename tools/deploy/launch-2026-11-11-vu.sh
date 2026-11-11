#!/bin/bash
# Выкладка 11.11.2026 «Все услуги»: обычные проверки run_all.sh (EXPECTED_BEFORE, закон владельца, суммы, сверка после загрузки)
cd "$(dirname "$0")" || exit 1
[ -f .netrc ] || { echo "deploy rc=10" > status.txt; exit 10; }
bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
rm -P .netrc 2>/dev/null || rm -f .netrc
echo DONE >> status.txt
cat status.txt
