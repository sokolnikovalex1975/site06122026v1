#!/bin/bash
# Пересборка только страницы /dezinfektsiya/avtotransport/ в копии репозитория (20.11.2026).
# Шаги сборки правят все страницы и при повторном прогоне переставляют блоки <style> в <head>, а полная сборка
# tools/site/build_site.py сейчас останавливается на tools/sklady/assemble.py (мессенджеров в шаблоне нет с 13.11.2026).
# Поэтому страница собирается в копии, порядок блоков <head> выравнивается по «Дезинсекции» (оболочка страницы),
# и в репозиторий возвращается только dezinfektsiya/avtotransport/index.html.
# Стили и скрипты «Состава заявки» (tools/site/zayavka.py) приходят с оболочкой; после выравнивания <head> шаг
# zayavka.transform ставит их на место (перед tel-plain) и проверяет, как на остальных страницах.
#   bash tools/avtotransport/rebuild_in_copy.sh
set -e
SRC=$(cd "$(dirname "$0")/../.." && pwd)
CP=/tmp/sitecopy
rm -rf $CP && mkdir -p $CP
tar -C $SRC --exclude=./.git --exclude=./dist -cf - . | tar -C $CP -xf -
cd $CP
python3 tools/avtotransport/build_page.py
for st in tools/site/unify.py tools/menu/apply_menu.py tools/site/services_block.py tools/site/price_block.py tools/site/clients_block.py tools/site/here_green.py tools/site/price_laws.py tools/site/mobile_crumbs.py tools/site/table_inset.py tools/site/table_cards.py tools/site/chk_cursor.py tools/site/hero_fold.py tools/site/required_marks.py tools/site/industry_links.py tools/site/menu_anchors.py tools/site/hero_in.py tools/site/focal_points.py tools/site/flex_text.py tools/site/mob_fit.py tools/site/samoproverka.py tools/site/samoproverka_forma.py tools/site/faq_first.py tools/site/no_messengers.py tools/site/meta_titles.py tools/site/h1_core.py tools/site/infografika.py tools/site/ipm_pin.py tools/site/tracking_laws.py tools/site/chk_cursor.py; do
  python3 $st > /tmp/step.log 2>&1 || { echo "FAIL $st"; tail -20 /tmp/step.log; exit 1; }
done
SRC=$SRC python3 - <<'PY'
import os, re
rel='dezinfektsiya/avtotransport/index.html'
s=open(rel,encoding='utf-8').read()
# стили «Состава заявки» и два его скрипта (оболочка «Дезинсекции» уже с ними) — одним блоком
pat=re.compile(r'<style id="zv-css">.*?</style>(?:\n<script src="[^"]*(?:zayavka|mob-bloki)\.min\.js\?v=[0-9a-z]+" defer></script>)*'
               r'|<style\b[^>]*>.*?</style>|<script id="srch-js">.*?</script>', re.S)
def bid(t):
    m=re.match(r'<(style|script)(?: id="([^"]*)")?(?: (data-fx))?',t); return m.group(2) or m.group(3) or 'anon'
def region(x):
    ld=x.index('<script type="application/ld+json">'); a=x.index('</script>',ld)+9; return a, x.index('</head>')
ref=open(os.environ['SRC'] + '/dezinsektsiya/index.html',encoding='utf-8').read()
ra,rb=region(ref); order={k:i for i,k in enumerate(bid(m.group(0)) for m in pat.finditer(ref[ra:rb]))}
a,b=region(s); reg=s[a:b]; bl=list(pat.finditer(reg))
gaps=[]; pos=0
for m in bl: gaps.append(reg[pos:m.start()]); pos=m.end()
gaps.append(reg[pos:])
assert sorted(bid(m.group(0)) for m in bl)==sorted(order), 'другой набор блоков'
assert all(g in ('\n','') for g in gaps[1:-1]), gaps
nb=sorted(bl,key=lambda m: order[bid(m.group(0))])
s=s[:a]+gaps[0]+'\n'.join(m.group(0) for m in nb)+gaps[-1]+s[b:]
# «Состав заявки» и длинные блоки на телефоне (tools/site/zayavka.py, 20.11.2026) — после выравнивания, как на всех
# страницах: стили zv-css и два скрипта прямо перед <style id="tel-plain">
import sys
sys.path.insert(0, 'tools/site')
import zayavka
s=zayavka.transform(s, rel)
bad=zayavka.problems(s, rel)
assert not bad, bad
open(rel,'w',encoding='utf-8').write(s)
print('порядок блоков <head> — как на «Дезинсекции», состав заявки на месте')
PY
python3 tools/site/tracking_laws.py --check > /tmp/step.log 2>&1 || { echo "FAIL tracking_laws --check"; tail -20 /tmp/step.log; exit 1; }
cp $CP/dezinfektsiya/avtotransport/index.html $SRC/dezinfektsiya/avtotransport/index.html
echo "ok: dezinfektsiya/avtotransport/index.html"
