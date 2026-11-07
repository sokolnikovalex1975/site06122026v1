#!/bin/bash
# Лаунчер выкладки 08.11.2026 (шаблон программы пест-контроля — PDF вместо Word): запускается один раз на Mac mini.
LOCK=/tmp/pc-shablon-deploy-2026-11-08.lock
mkdir "$LOCK" 2>/dev/null || { echo "уже запускался ($LOCK)"; exit 0; }
cd "$(dirname "$0")" || exit 1
DOCX="materialy/programma-pest-kontrolya/shablon-programmy-pest-kontrolya.docx"
DOCX_SHA="cdd23cb6f117093f2a15d52d65f918f5715d19eac6258fb654659b77901d1bdd"
[ -f .netrc ] || { echo "нет .netrc"; echo "deploy rc=10" > status.txt; exit 10; }
cp -p .netrc .netrc.del && chmod 600 .netrc.del
bash run_all.sh deploy; rc=$?
echo "deploy rc=$rc" > status.txt
if [ $rc -eq 0 ]; then
  mkdir -p deleted
  B="deleted/$(basename "$DOCX")"
  curl -sS --netrc-file .netrc.del --connect-timeout 20 --max-time 120 -o "$B" "ftp://vh402.timeweb.ru/public_html/$DOCX"; g=$?
  s=$(shasum -a 256 "$B" 2>/dev/null | cut -d' ' -f1)
  echo "docx copy rc=$g size=$(wc -c < "$B" 2>/dev/null | tr -d ' ') sha_ok=$([ "$s" = "$DOCX_SHA" ] && echo yes || echo no)" >> status.txt
  if [ $g -eq 0 ] && [ -s "$B" ]; then
    mkdir -p "$HOME/pestcontrol-deploy-2026-11-08-shablon/deleted" && cp -p "$B" "$HOME/pestcontrol-deploy-2026-11-08-shablon/deleted/"
    curl -sS --netrc-file .netrc.del --connect-timeout 20 --max-time 120 -Q "DELE /public_html/$DOCX" "ftp://vh402.timeweb.ru/" -o /dev/null; d=$?
    echo "docx delete rc=$d" >> status.txt
  fi
fi
rm -P .netrc.del 2>/dev/null || rm -f .netrc.del
rm -P .netrc 2>/dev/null || rm -f .netrc
[ -f run_all.sh ] && [ $rc -eq 0 ] && mv run_all.sh run_all.sh.done
echo DONE >> status.txt
cat status.txt
