#!/bin/bash
# Сверка выложенных файлов по HTTPS с пакетом и счётчики на страницах.
cd "$(dirname "$0")" || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
ok=0; bad=0; : > https.txt
while read -r h f; do
  u="$f"; case "$f" in *index.php) u="${f%index.php}";; esac
  got=$(curl -sS --compressed --max-time 60 -H 'Cache-Control: no-cache' "$SITE$u?nc=$(date +%s)" | shasum -a 256 | cut -d' ' -f1)
  if [ "$got" = "$h" ]; then ok=$((ok+1)); else bad=$((bad+1)); echo "DIFF $f" >> https.txt; fi
done < MANIFEST.sha256
for p in "" materialy/ materialy/akt-deratizatsii-i-dezinsektsii/ materialy/skhema-tochek-pest-kontrolya/ dezinfektsiya/; do
  b=$(curl -sS --compressed --max-time 60 "$SITE$p")
  echo "/$p metrika=$(echo "$b" | grep -c "ym(113675622, 'init'") uis=$(echo "$b" | grep -c 'cs.min.js?k=') radist=$(echo "$b" | grep -c 'tracker.min.js') noindex=$(echo "$b" | grep -c noindex) v=$(echo "$b" | grep -o 'v=20261111kursor' | wc -l | tr -d ' ')" >> https.txt
done
for f in app.min.js style.css img/skhema-obrazets-p2-360.webp img/skhema-obrazets-p2-720.webp img/skhema-obrazets-p1-360.webp materialy/skhema-tochek-pest-kontrolya/obrazets-skhemy-tochek-pest-kontrolya.pdf; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$SITE$f") $f" >> https.txt; done
echo "https ok=$ok bad=$bad" >> https.txt; echo DONE >> https.txt
