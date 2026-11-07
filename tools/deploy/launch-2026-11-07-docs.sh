#!/bin/bash
# Лаунчер выкладки 07.11.2026 (образцы документов): запускается один раз из «Терминала» на Mac mini.
LOCK=/tmp/pc-docs-deploy-2026-11-07.lock
mkdir "$LOCK" 2>/dev/null || { echo "уже запускался ($LOCK)"; exit 0; }
W=/tmp/pcdeploy/pestcontrol-deploy-work-2026-11-07-docs
cd "$W" || { echo "нет папки $W"; exit 1; }
DOCX="materialy/programma-proizvodstvennogo-kontrolya-haccp/shablon-programmy-proizvodstvennogo-kontrolya.docx"
[ -f .netrc ] || { echo "нет .netrc"; echo "deploy rc=10" > status.txt; exit 10; }
cp -p .netrc .netrc.del && chmod 600 .netrc.del
bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
if [ $rc -eq 0 ]; then
  mkdir -p deleted
  curl -sS --netrc-file .netrc.del --connect-timeout 20 --max-time 120 -o "deleted/$(basename "$DOCX")" "ftp://vh402.timeweb.ru/public_html/$DOCX"; g=$?
  echo "docx copy rc=$g size=$(wc -c < "deleted/$(basename "$DOCX")" 2>/dev/null | tr -d ' ')" >> status.txt
  if [ $g -eq 0 ] && [ -s "deleted/$(basename "$DOCX")" ]; then
    curl -sS --netrc-file .netrc.del --connect-timeout 20 --max-time 120 -Q "DELE /public_html/$DOCX" "ftp://vh402.timeweb.ru/" -o /dev/null; d=$?
    echo "docx delete rc=$d" >> status.txt
    mkdir -p "$HOME/pestcontrol-deploy-2026-11-07-docs/deleted" && cp -p "deleted/$(basename "$DOCX")" "$HOME/pestcontrol-deploy-2026-11-07-docs/deleted/"
  fi
fi
rm -P .netrc.del 2>/dev/null || rm -f .netrc.del
rm -P .netrc 2>/dev/null || rm -f .netrc
[ -f run_all.sh ] && [ $rc -eq 0 ] && mv run_all.sh run_all.sh.done
echo DONE >> status.txt
cat status.txt
