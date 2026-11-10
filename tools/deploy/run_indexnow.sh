#!/bin/bash
# Выкладка ключа IndexNow на пестконтроль-центр.рф, 11.11.2026.
# Запрос владельца: «Делай всё, что предложил, и выкладывай на хостинг» (подключить IndexNow для Яндекса).
# Добавляется ОДИН новый файл в корень сайта: /public_html/<KEY>.txt — содержимое: сам ключ (UTF-8, без перевода строки).
# Существующие файлы сайта не заменяются и не удаляются; index.php, .htaccess, robots.txt, sitemap.xml и счётчики
# (Метрика 113675622, UIS/CoMagic, Radist) не затрагиваются.
# Запуск — в «Терминале» на Mac (в песочнице Perplexity нет доступа к сети). Рядом со скриптом: pkg/<KEY>.txt,
# MANIFEST.sha256 (shasum -a 256 по pkg/) и временный .netrc с доступом FTP (chmod 600, удаляется в deploy/rollback/cleanup).
#   bash run_indexnow.sh check     — подключение, список корня сайта, есть ли уже файл ключа
#   bash run_indexnow.sh deploy    — загрузка файла ключа (если его ещё нет) + сверка по FTP и HTTPS
#   bash run_indexnow.sh rollback  — удалить с сервера только файл ключа
#   bash run_indexnow.sh cleanup   — удалить временный .netrc
# Работает с curl и bash 3.2 (macOS).
set -u
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D" || exit 1
MODE="${1:-check}"
NAME="pestcontrol-deploy-2026-11-11-indexnow"
KEY="6e3f9d70b48c34299ede4719e3b5e4a1"
F="$KEY.txt"
SITE="public_html"
SITE_URL="https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai"
KEEP="$HOME/$NAME"
HOST="${FTP_HOST:-vh402.timeweb.ru}"
NETRC="$D/.netrc"
LOG="$D/deploy.log"
TLS=""
exec > >(tee -a "$LOG") 2>&1

keep_copy() {
  mkdir -p "$KEEP/pkg"
  cp -p run_indexnow.sh MANIFEST.sha256 "$KEEP/" 2>/dev/null
  cp -p "pkg/$F" "$KEEP/pkg/" 2>/dev/null
  [ -d verify ] && rm -rf "$KEEP/verify" && cp -Rp verify "$KEEP/verify"
  cp -p "$LOG" "$KEEP/deploy.log" 2>/dev/null
}
finish() {
  rc=$?
  case "$MODE" in deploy|rollback|cleanup)
    rm -P "$NETRC" 2>/dev/null || rm -f "$NETRC"
    echo "== netrc removed" ;;
  esac
  keep_copy
  echo "== script, key file and log kept in: $KEEP"
  echo "== EXIT CODE $rc"
}
trap finish EXIT

echo "== $(date '+%Y-%m-%d %H:%M:%S %Z') mode=$MODE host=$HOST"
[ "$MODE" = cleanup ] && exit 0
[ -f "$NETRC" ] || { echo "ERROR: .netrc not found"; exit 10; }
chmod 600 "$NETRC"

c() { curl -sS --netrc-file "$NETRC" $TLS --connect-timeout 20 --max-time 120 "$@"; }

# 1. Подключение (FTP с TLS, потом без него) — как в run_all.sh
ok=0
for opts in "--ssl-reqd" "--ssl-reqd -k" ""; do
  TLS="$opts"
  OUT=$(c --list-only "ftp://$HOST/" 2>&1); rc=$?
  echo "probe opts=[$opts] rc=$rc"
  if [ $rc -eq 0 ]; then ok=1; break; else echo "$OUT" | tail -1; fi
done
[ $ok = 1 ] || { echo "ERROR: FTP connection failed"; exit 11; }
echo "== connected, TLS opts: [${TLS:-none}]"

# 2. Папка сайта: в /public_html должны быть index.php и send.php
PH=$(c --list-only "ftp://$HOST/$SITE/" 2>&1) || { echo "ERROR: list /$SITE failed: $(echo "$PH" | tail -1)"; exit 12; }
PH=$(echo "$PH" | tr -d '\r' | sed 's|.*/||')
if ! { echo "$PH" | grep -qx 'index.php' && echo "$PH" | grep -qx 'send.php'; }; then
  echo "ERROR: site folder with index.php and send.php not found"; echo "/$SITE: $(echo $PH)"; exit 12
fi
echo "== site folder: /$SITE ($(echo "$PH" | grep -c .) entries)"
echo "--- *.txt in site root: $(echo "$PH" | grep -E '\.txt$' | tr '\n' ' ')"
HAS=0; echo "$PH" | grep -qx "$F" && HAS=1
echo "== key file on server before: $([ $HAS = 1 ] && echo yes || echo no)"

verify() {
  rm -rf verify && mkdir -p verify
  c -o "verify/$F" "ftp://$HOST/$SITE/$F" || { echo "ERROR: verify download failed"; return 1; }
  (cd verify && shasum -a 256 -c ../MANIFEST.sha256) || { echo "ERROR: verify mismatch (FTP)"; return 1; }
  echo "== VERIFY FTP OK"
  HT=$(curl -sS -o verify/https.txt -w '%{http_code} %{content_type}' --connect-timeout 20 --max-time 30 "$SITE_URL/$F" 2>&1)
  echo "HTTPS $SITE_URL/$F -> $HT"
  if cmp -s verify/https.txt "pkg/$F"; then echo "== VERIFY HTTPS OK"; else echo "WARNING: HTTPS response differs from the key file"; fi
  return 0
}

case "$MODE" in
  check) ;;
  deploy)
    (cd pkg && shasum -a 256 -c ../MANIFEST.sha256 > /dev/null) || { echo "ERROR: package checksum mismatch"; exit 15; }
    echo "== package checksum OK"
    if [ $HAS = 1 ]; then
      echo "== $F already on server — not overwriting, only verifying"
    else
      echo "== upload: 1 new file ($F), existing site files untouched"
      c -T "pkg/$F" "ftp://$HOST/$SITE/$F" || { echo "ERROR: upload failed"; exit 16; }
      echo "up $F OK"
    fi
    verify || exit 17
    echo "== DEPLOY DONE"
    ;;
  rollback)
    [ $HAS = 1 ] || { echo "== $F not on server, nothing to delete"; exit 0; }
    c -Q "DELE $SITE/$F" --list-only "ftp://$HOST/" > /dev/null || { echo "ERROR: delete failed"; exit 18; }
    echo "== deleted $SITE/$F (only the key file)"
    ;;
  *) echo "usage: $0 check|deploy|rollback|cleanup"; exit 2 ;;
esac
exit 0
