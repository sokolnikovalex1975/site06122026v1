#!/bin/bash
# Снимок рабочего сайта по HTTPS перед выкладкой 11.11.2026 («Дератизация и дезинсекция»): 24 страницы, sitemap.xml, search-index.json.
# Запуск из «Терминала» на Mac mini; повторный запуск безопасен (папка live/ пересоздаётся).
cd /tmp/pc-live-dd || exit 1
SITE="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
PAGES="index.php deratizatsiya/index.php dezinfektsiya/index.php dezinsektsiya/index.php dogovor-deratizatsiya-dezinsektsiya/index.php farmatsevticheskie-proizvodstva/index.php gostinitsy/index.php laboratornye-issledovaniya/index.php magaziny-i-torgovye-seti/index.php materialy/index.php materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php materialy/programma-pest-kontrolya/index.php materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php materialy/zhurnal-pest-kontrolya/index.php normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php normativnaya-baza/index.php normativnaya-baza/proverochnye-listy/index.php ochistka-dezinfektsiya-ventilyatsii/index.php pishchevoe-proizvodstvo/index.php privacy/index.php razrabotka-ppk/index.php restorany-i-kafe/index.php sanitarnyy-audit/index.php sklady-i-logistika/index.php soglasie/index.php"
rm -rf live live.zip fetch-status.txt; mkdir -p live
bad=0
get() { # get <путь на сайте> <файл>
  local url="$SITE$1" out="live/$2" i code
  mkdir -p "$(dirname "$out")"
  for i in 1 2 3 4 5; do
    code=$(curl -sS -o "$out" -w '%{http_code}' --compressed --connect-timeout 20 --max-time 90 -H 'Cache-Control: no-cache' "$url?nocache=$(date +%s)$i" 2>/dev/null)
    if [ "$code" = 200 ] && [ -s "$out" ]; then echo "ok $code $(wc -c < "$out" | tr -d ' ') $2"; return 0; fi
    echo "retry $i: $code $2"; sleep 3
  done
  echo "FAIL $2"; bad=1
}
for p in $PAGES; do get "${p%index.php}" "$p"; sleep 1; done
get sitemap.xml sitemap.xml
get search-index.json search-index.json
# проверка: не прокси-страница ошибки и есть закрывающий тег
for p in $PAGES; do tail -c 200 "live/$p" | grep -q '</html>' || { echo "NO </html>: $p"; bad=1; }; done
curl -sS -o /dev/null -w 'new page now: %{http_code}\n' --max-time 30 "${SITE}deratizatsiya-i-dezinsektsiya/"
(cd live && zip -q -r -X ../live.zip .)
echo "rc=$bad files=$(find live -type f | wc -l | tr -d ' ') $(date '+%F %T %Z')" > fetch-status.txt
cat fetch-status.txt
