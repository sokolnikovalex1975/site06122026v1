#!/bin/bash
# Выкладка «Закон владельца 11.11.2026»: счётчики меняются намеренно (отложенный блок → официальные коды), поэтому
# ALLOW_COUNTERS_CHANGE=1; все остальные проверки run_all.sh (EXPECTED_BEFORE, закон, суммы, сверка после загрузки) — как обычно.
cd "$(dirname "$0")" || exit 1
[ -f .netrc ] || { echo "deploy rc=10" > status.txt; exit 10; }
ALLOW_COUNTERS_CHANGE=1 bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
rm -P .netrc 2>/dev/null || rm -f .netrc
echo DONE >> status.txt
cat status.txt
