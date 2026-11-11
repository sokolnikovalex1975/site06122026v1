#!/bin/bash
# Package is prepared ON THE MAC from its live/ backup. It contains the production SMTP secret.
# Do not copy pkg/send.php or the backup zip into GitHub or shared project files.
set -u
cd "$(dirname "$0")" || exit 1
[ -f netrc.tmp ] && mv netrc.tmp .netrc
[ -f .netrc ] || exit 10
chmod 600 .netrc
bash run_all.sh deploy
rc=$?
printf 'deploy rc=%s\nDONE\n' "$rc" > status.txt
rm -f .netrc
exit "$rc"
