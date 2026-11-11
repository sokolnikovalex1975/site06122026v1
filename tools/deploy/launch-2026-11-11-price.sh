#!/bin/bash
# Общий прайс на услуги: выкладка 42 index.php на Timeweb (подготовка — prepare-2026-11-11-price.py).
# FTP-доступ берётся из существующего netrc, не копируется и не печатается.
# Порядок: проверка резервных копий → сверка с сайтом → загрузка во временные файлы и сверка → переименование →
# сверка по FTP и HTTPS. При любой ошибке после переименования все уже заменённые страницы возвращаются из backup/.
set -u
D="${1:?package directory required}"
AUTH="${2:?existing netrc path required}"
cd "$D" || exit 1
FTP="ftp://vh402.timeweb.ru"
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
SUF="price-2026-11-11.tmp"
PROMOTED=()
ftp() { curl --fail --silent --show-error --netrc-file "$AUTH" --connect-timeout 15 --max-time 90 "$@"; }
# загрузки и скачивания — с повторами (Timeweb иногда не принимает соединение с первого раза)
ftpr() { ftp --retry 5 --retry-delay 4 --retry-all-errors "$@"; }
hash() { shasum -a 256 "$1" | awk '{print $1}'; }
rollback() {
  echo "Verification failed: restoring ${#PROMOTED[@]} page(s) from backup"
  for p in "${PROMOTED[@]}"; do
    if ftpr -T "backup/${p}index.php" "$FTP/public_html/${p}index.php"; then echo "restored [$p]"; else echo "ROLLBACK FAILED [$p]: restore backup/${p}index.php manually"; fi
  done
}
die() { echo "ERROR: $*"; [ "${#PROMOTED[@]}" -gt 0 ] && rollback; echo 1 > deploy.status; echo "EXIT CODE 1"; exit 1; }
mkdir -p verify
# 1. резервные копии и пакет совпадают с манифестом, сайт не менялся после снятия копий
while read -r before after file; do
  p="${file%index.php}"
  [ "$(hash "backup/$file")" = "$before" ] || die "backup checksum [$p]"
  [ "$(hash "pkg/$file")" = "$after" ] || die "package checksum [$p]"
  mkdir -p "verify/before/$p"
  ftpr "$FTP/public_html/$file" -o "verify/before/$file" || die "download current [$p]"
  cmp -s "backup/$file" "verify/before/$file" || die "live page changed since backup [$p]"
done < MANIFEST.txt
rm -f before-price_2026-11-11_ftp.zip; zip -qr before-price_2026-11-11_ftp.zip backup
echo "Backups verified: $(wc -l < MANIFEST.txt) pages"
# 2. загрузка во временные файлы и сверка
while read -r before after file; do
  p="${file%index.php}"
  ftpr -T "pkg/$file" "$FTP/public_html/$file.$SUF" || die "staged upload [$p]"
  mkdir -p "verify/staged/$p"
  ftpr "$FTP/public_html/$file.$SUF" -o "verify/staged/$file" || die "staged download [$p]"
  cmp -s "pkg/$file" "verify/staged/$file" || die "staged checksum [$p]"
done < MANIFEST.txt
echo "Staged files verified"
# 3. замена и сверка по FTP и HTTPS
while read -r before after file; do
  p="${file%index.php}"
  dir="public_html/${p}"
  PROMOTED+=("$p")
  ftp --quote "RNFR /public_html/$file.$SUF" --quote "RNTO /public_html/$file" --list-only "$FTP/$dir" -o /dev/null || echo "rename reported an error [$p], checking file"
  mkdir -p "verify/ftp/$p" "verify/https/$p"
  ftpr "$FTP/public_html/$file" -o "verify/ftp/$file" || die "ftp after [$p]"
  cmp -s "pkg/$file" "verify/ftp/$file" || die "ftp checksum after [$p]"
  ok=0
  for i in 1 2 3; do
    curl --fail --silent --show-error --connect-timeout 15 --max-time 60 "$SITE$p?v=$after" -o "verify/https/$file" && cmp -s "pkg/$file" "verify/https/$file" && { ok=1; break; }
    sleep 2
  done
  [ "$ok" = 1 ] || die "https checksum after [$p]"
  echo "published [$p]"
done < MANIFEST.txt
echo "FTP and public HTTPS checksums verified: ${#PROMOTED[@]} pages"
date '+Published: %Y-%m-%d %H:%M:%S %Z'
echo 0 > deploy.status
echo "EXIT CODE 0"
