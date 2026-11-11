#!/bin/bash
# Снимок рабочего сайта по HTTPS перед выкладкой курсора (11.11.2026): все страницы, style.css, app.js, app.min.js.
cd /tmp/pc-live-kursor || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
rm -rf live live.zip fetch-status.txt fetch.log; mkdir -p live
get() {
  local url="$SITE$1" out="live/$2" i code
  mkdir -p "$(dirname "$out")"
  for i in 1 2 3; do
    code=$(curl -sS -o "$out" -w '%{http_code}' --compressed --connect-timeout 20 --max-time 90 -H 'Cache-Control: no-cache' "$url?nocache=$(date +%s)$i" 2>/dev/null)
    if [ "$code" = 200 ] && [ -s "$out" ]; then echo "ok $code $2"; return 0; fi
    if [ "$code" = 404 ]; then rm -f "$out"; echo "404 $2"; return 0; fi
    sleep 2
  done
  rm -f "$out"; echo "FAIL $code $2"
}
for p in $(cat pages.txt); do get "${p%index.php}" "$p"; done > fetch.log 2>&1
for f in app.min.js app.js style.css img/skhema-obrazets-p2-360.webp img/skhema-obrazets-p2-720.webp; do get $f $f >> fetch.log; done
(cd live && zip -q -r -X ../live.zip .)
echo "files=$(find live -type f | wc -l | tr -d ' ') $(date '+%F %T %Z')" > fetch-status.txt
echo DONE >> fetch-status.txt
