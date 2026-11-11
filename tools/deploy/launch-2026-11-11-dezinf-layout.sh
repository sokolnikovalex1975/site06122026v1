#!/bin/bash
# One-file deployment. Existing FTP auth is used in place, never copied or printed.
set -eu
D="${1:?package directory required}"
AUTH="${2:?existing netrc path required}"
cd "$D"
FTP="ftp://vh402.timeweb.ru"
REL="public_html/dezinfektsiya/index.php"
TMP="$REL.layout-718eef57484a.tmp"
URL="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/dezinfektsiya/"
BEFORE="b394cf43d844d5c237a4336341a9b29e28743549313b27e509baf3030cd0c8f4"
AFTER="718eef57484a141067cbd29c304d4196847f58ead3a7cbc9c1f6702ad5cce802"
PROMOTED=0
ftp() { curl --fail --silent --show-error --netrc-file "$AUTH" --connect-timeout 15 --max-time 90 "$@"; }
hash() { shasum -a 256 "$1" | awk '{print $1}'; }
finish() {
  rc=$?
  trap - EXIT
  if [ "$rc" != 0 ] && [ "$PROMOTED" = 1 ]; then
    echo "Verification failed: restoring original page"
    if ftp -T backup/dezinfektsiya/index.php "$FTP/$REL"; then
      echo "Original page restored from backup"
    else
      echo "ROLLBACK FAILED: restore backup/dezinfektsiya/index.php manually"
    fi
  fi
  printf '%s\n' "$rc" > deploy.status
  echo "EXIT CODE $rc"
  exit "$rc"
}
trap finish EXIT
[ "$(hash backup/dezinfektsiya/index.php)" = "$BEFORE" ]
[ "$(hash pkg/dezinfektsiya/index.php)" = "$AFTER" ]
mkdir -p verify
ftp "$FTP/$REL" -o verify/current-before.php
cmp backup/dezinfektsiya/index.php verify/current-before.php
zip -q before-dezinf-layout_2026-11-11_ftp.zip backup/dezinfektsiya/index.php
echo "Backup checksum verified"
ftp -T pkg/dezinfektsiya/index.php "$FTP/$TMP"
ftp "$FTP/$TMP" -o verify/staged.php
cmp pkg/dezinfektsiya/index.php verify/staged.php
echo "Staged file checksum verified"
PROMOTED=1
ftp --quote "RNFR /$TMP" --quote "RNTO /$REL" --list-only "$FTP/public_html/dezinfektsiya/" -o /dev/null
ftp "$FTP/$REL" -o verify/ftp-after.php
cmp pkg/dezinfektsiya/index.php verify/ftp-after.php
curl --fail --silent --show-error --connect-timeout 15 --max-time 60 "$URL" -o verify/https-after.php
cmp pkg/dezinfektsiya/index.php verify/https-after.php
echo "FTP and public HTTPS checksums verified"
date '+Published: %Y-%m-%d %H:%M:%S %Z'
shasum -a 256 backup/dezinfektsiya/index.php verify/https-after.php
