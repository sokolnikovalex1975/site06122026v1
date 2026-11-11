#!/bin/bash
# Запуск выкладки 11.11.2026 (хлебные крошки первого экрана над заголовком): рядом лежат run_all.sh, deploy.conf, pkg/,
# MANIFEST.sha256 и временный netrc.tmp (доступ FTP); после работы .netrc удаляется.
cd "$(dirname "$0")" || exit 1
[ -f netrc.tmp ] && mv netrc.tmp .netrc
[ -f .netrc ] || { echo "deploy rc=10" > status.txt; exit 10; }
chmod 600 .netrc
bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
rm -P .netrc 2>/dev/null || rm -f .netrc
echo DONE >> status.txt
cat status.txt
