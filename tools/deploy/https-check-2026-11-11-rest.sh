#!/bin/bash
# Сверка выложенных файлов по HTTPS с пакетом (MANIFEST.sha256) и счётчики на новых страницах.
cd /tmp/pestcontrol-deploy-2026-11-11-rest || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
ok=0; bad=0; : > https.txt
while read -r h f; do
  u="$f"; case "$f" in *index.php) u="${f%index.php}";; esac
  got=$(curl -sS --compressed --max-time 60 -H 'Cache-Control: no-cache' "$SITE$u?nc=$(date +%s)" | shasum -a 256 | cut -d' ' -f1)
  if [ "$got" = "$h" ]; then ok=$((ok+1)); else bad=$((bad+1)); echo "DIFF $f" >> https.txt; fi
done < MANIFEST.sha256
for p in dezinsektsiya/restorany-i-kafe/ deratizatsiya/restorany-i-kafe/; do
  b=$(curl -sS --compressed --max-time 60 "$SITE$p")
  echo "$p metrika=$(echo "$b" | grep -c "ym(113675622, 'init'") uis=$(echo "$b" | grep -c uiscom) radist=$(echo "$b" | grep -ci radist) noindex=$(echo "$b" | grep -c noindex)" >> https.txt
done
echo "https ok=$ok bad=$bad" >> https.txt; echo DONE >> https.txt
