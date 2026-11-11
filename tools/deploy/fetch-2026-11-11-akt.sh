#!/bin/bash
# Снимок рабочего сайта по HTTPS перед выкладкой 11.11.2026 (акт и схема точек): все страницы меню, sitemap, поиск, статусы.
cd /tmp/pc-live-akt || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
PAGES="$(cat pages.txt)"
rm -rf live live.zip fetch-status.txt status-urls.txt; mkdir -p live
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
for p in $PAGES; do get "${p%index.php}" "$p"; done > fetch.log 2>&1
get sitemap.xml sitemap.xml >> fetch.log
get search-index.json search-index.json >> fetch.log
for f in app.min.js app.js style.css search.min.js; do get $f $f >> fetch.log; done
for u in $(cat urls.txt); do echo "$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$SITE$u") $u"; done > status-urls.txt
(cd live && zip -q -r -X ../live.zip .)
echo "files=$(find live -type f | wc -l | tr -d ' ') $(date '+%F %T %Z')" > fetch-status.txt
echo DONE >> fetch-status.txt
