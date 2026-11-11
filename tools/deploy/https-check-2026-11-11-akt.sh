#!/bin/bash
# Сверка выложенных файлов по HTTPS с пакетом (MANIFEST.sha256), счётчики на новых и правленых страницах,
# доступность файлов, на которые ссылаются страницы пакета (ASSETS-CHECK.txt).
cd /tmp/pestcontrol-deploy-2026-11-11-akt || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
ok=0; bad=0; : > https.txt
while read -r h f; do
  u="$f"; case "$f" in *index.php) u="${f%index.php}";; esac
  got=$(curl -sS --compressed --max-time 60 -H 'Cache-Control: no-cache' "$SITE$u?nc=$(date +%s)" | shasum -a 256 | cut -d' ' -f1)
  if [ "$got" = "$h" ]; then ok=$((ok+1)); else bad=$((bad+1)); echo "DIFF $f" >> https.txt; fi
done < MANIFEST.sha256
for p in "" materialy/ materialy/akt-deratizatsii-i-dezinsektsii/ materialy/skhema-tochek-pest-kontrolya/ materialy/zhurnal-pest-kontrolya/; do
  b=$(curl -sS --compressed --max-time 60 "$SITE$p")
  echo "/$p metrika=$(echo "$b" | grep -c "ym(113675622, 'init'") uis=$(echo "$b" | grep -c 'cs.min.js?k=') radist=$(echo "$b" | grep -c 'tracker.min.js') noindex=$(echo "$b" | grep -c noindex) akt=$(echo "$b" | grep -o 'akt-deratizatsii-i-dezinsektsii/"' | wc -l | tr -d ' ') skhema=$(echo "$b" | grep -o 'skhema-tochek-pest-kontrolya/"' | wc -l | tr -d ' ')" >> https.txt
done
na=0; while read -r f; do [ -z "$f" ] && continue; c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 -I "$SITE$f"); [ "$c" = 200 ] || { na=$((na+1)); echo "ASSET $c $f" >> https.txt; }; done < ASSETS-CHECK.txt
echo "assets not 200: $na" >> https.txt
echo "https ok=$ok bad=$bad" >> https.txt; echo DONE >> https.txt
