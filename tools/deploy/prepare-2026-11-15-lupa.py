#!/usr/bin/env python3
"""«Лёгкая лупа» и облегчённый режим на всём сайте (15.11.2026): точечный пакет для Timeweb из актуального сайта.

    python3 tools/deploy/prepare-2026-11-15-lupa.py <новая папка>     # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-15-lupa.py <папка> --check   # пересобрать из <папка>/backup и сверить
    python3 tools/deploy/prepare-2026-11-15-lupa.py <папка> --resume  # продолжить: уже снятые файлы не снимать заново
                                                                      # (Timeweb иногда отвечает облаку ложным 502)

Решение владельца после превью preview-lupa/: «Перенеси этот вариант на главную и внутренние страницы, сохрани
счётчики и выложи на Timeweb».

Что меняется на рабочем сайте (остальное — байт в байт):
  * img/hero-dim.webp, img/hero-m-dim.webp, img/hero-lit.webp — новые файлы: фото первого экрана главной, заранее
    затемнённое (компьютер и телефон), и светлое фото для лупы (байт в байт из репозитория);
  * style.css — те же правки, что в style.css репозитория (tools/site/lupa.py: style_hunks): лупа главной вместо
    «фонаря», затемнённое фото, в конце — облегчённый режим (класс lowfx);
  * app.min.js — правится рабочий файл точными заменами, а не собирается из app.js репозитория: в GitHub есть ещё
    не опубликованные правки (переход к блоку по якорю и др.). Замены повторяют app.js репозитория: window.pcFx и
    замер кадров, лупа главной (готовый светлый круг, только transform), без параллакса, наклона, курсора и подсветки
    карточек в облегчённом режиме, лупа — после входа фото;
  * все страницы — правки tools/site/lupa.py (page_edits): скрипт в <head> (window.pcFx), вход первого экрана,
    лупа внутренних страниц и вентиляции, на главной — разметка лупы, предзагрузка и встроенные стили (те же правки
    в сжатом виде), версия ?v=20261113ekran → ?v=20261115lupa (у style.css и app.min.js кэш на год).
Счётчики — по закону владельца (tracking_laws) до и после: Метрика, UIS и Radist не меняются, каждый ровно один раз.
"""
import base64
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws  # noqa: E402
import lupa  # noqa: E402

NAME = 'lupa-2026-11-15'
OLD_V, NEW_V = '20261113ekran', lupa.NEW_V
LEGAL = ('privacy/', 'soglasie/')
IMAGES = ('img/hero-dim.webp', 'img/hero-m-dim.webp', 'img/hero-lit.webp')
JS = 'app.min.js'

# ---------------------------------------------------------------- app.min.js рабочего сайта: точные замены
# Имена в сжатом файле: I — <html>, a — $, y — мышь (fine), R — телефон (mobile), w — шире 1024 px, P — #hero,
# F — #heroMedia, A — лупа (#heroLit → #heroLens), k — панель, g — первый экран внутренних страниц, U — его фото,
# N — window.pcHero, Ut — запуск «фонаря» после входа, pt — «фонарь включён» (больше не нужен, объявление остаётся).
JS_PRELUDE = r'''
var __pcfx=window.pcFx||(window.pcFx={mode:"",lite:!1,hooks:[],set:function(){
  if(__pcfx.lite)return;__pcfx.lite=!0;I.classList.add("lowfx");
  __pcfx.hooks.forEach(function(f){try{f()}catch(e){}})}});
var __pcprobe=function(){
  if(__pcfx.lite||__pcfx.mode==="full"||__pcfx.mode==="lite")return;
  if(document.hidden){setTimeout(__pcprobe,2e3);return}
  var ts=[],t0=0,hid=!1,onv=function(){hid=!0};
  document.addEventListener("visibilitychange",onv);
  var step=function(t){
    if(!t0)t0=t;ts.push(t);
    if(t-t0<2e3&&!hid){requestAnimationFrame(step);return}
    document.removeEventListener("visibilitychange",onv);
    if(hid||document.hidden){setTimeout(__pcprobe,2e3);return}
    for(var q=[],j=1;j<ts.length;j++)q.push(ts[j]-ts[j-1]);
    q.sort(function(m,n){return m-n});
    var med=q.length?q[q.length>>1]:1e3;
    I.setAttribute("data-fps",Math.round(1e3/med));
    if(q.length<20||med>25)__pcfx.set(!0)};
  requestAnimationFrame(step)};
document.readyState==="complete"?setTimeout(__pcprobe,3e3):addEventListener("load",function(){setTimeout(__pcprobe,3e3)});
function __pclens(hero,media,lens,panel){
  var img=lens.firstElementChild,src=lens.getAttribute("data-src");
  var W=0,H=0,r=0,x=0,yy=0,tx=0,ty=0,hx=0,hy=0,raf=0,last=0,visible=!0,follow=!1,off=!1,ready=!1,want=!1,dts=[];
  var home=function(){
    var p=panel,px=0,py=0,el=p;
    if(p&&matchMedia("(min-width: 1281px)").matches)for(;el&&el!==hero;el=el.offsetParent){px+=el.offsetLeft;py+=el.offsetTop}
    if(p&&el===hero){var hdr=document.querySelector("#hdr"),hh=hdr?hdr.offsetHeight:0;hx=px+p.offsetWidth/2-media.offsetLeft;hy=(hh+py)/2-media.offsetTop}
    else{hx=W*.78;hy=H*.22}};
  var apply=function(){
    var X=Math.round((x-r)*10)/10,Y=Math.round((yy-r)*10)/10;
    lens.style.transform="translate3d("+X+"px,"+Y+"px,0)";
    img.style.transform="translate3d("+-X+"px,"+-Y+"px,0)"};
  var size=function(){
    if(off)return;
    var cs=getComputedStyle(media);W=parseFloat(cs.width)||media.offsetWidth;H=parseFloat(cs.height)||media.offsetHeight;
    r=Math.round(Math.max(240,Math.min(400,innerWidth*.21))*.72);
    lens.style.width=lens.style.height=2*r+"px";
    img.style.width=W+"px";img.style.height=H+"px";
    home();
    if(!follow){tx=hx;ty=hy;if(!raf){x=hx;yy=hy}}
    apply()};
  var tick=function(now){
    raf=0;
    if(off||!visible)return;
    var dt=last?Math.min(Math.max(now-last,0),100):16.67;
    if(last&&__pcfx.mode!=="full"){dts.push(now-last);if(dts.length>=40){dts.sort(function(m,n){return m-n});var med=dts[20];dts=[];
      if(med>25){I.setAttribute("data-fps",Math.round(1e3/med));__pcfx.set(!0);return}}}
    last=now;
    var kk=1-Math.pow(.94,dt/16.67);
    x+=(tx-x)*kk;yy+=(ty-yy)*kk;
    if(Math.abs(tx-x)<.3&&Math.abs(ty-yy)<.3){x=tx;yy=ty;apply();return}
    apply();
    raf=requestAnimationFrame(tick)};
  var go=function(){if(!raf&&!off&&visible){last=0;raf=requestAnimationFrame(tick)}};
  var reveal=function(){if(ready&&want&&!off)lens.classList.add("on")};
  hero.addEventListener("pointermove",function(e){
    if(e.pointerType!=="mouse"||off)return;
    var b=media.getBoundingClientRect();
    tx=(e.clientX-b.left)/b.width*W;ty=(e.clientY-b.top)/b.height*H;
    follow=!0;go()},{passive:!0});
  hero.addEventListener("pointerleave",function(){if(off)return;follow=!1;tx=hx;ty=hy;go()});
  new IntersectionObserver(function(en){visible=en[0].isIntersecting;if(visible)go()}).observe(hero);
  if(window.ResizeObserver)new ResizeObserver(function(){size()}).observe(media);
  addEventListener("resize",size);
  size();
  var loadLit=function(){var im=new Image();im.onload=function(){
    var set=function(){img.style.backgroundImage='url("'+src+'")';ready=!0;reveal()};
    if(im.decode)im.decode().then(set,set);else set()};im.src=src};
  if(document.readyState==="complete")loadLit();else addEventListener("load",loadLit);
  __pcfx.hooks.push(function(){off=!0;if(raf)cancelAnimationFrame(raf);raf=0;lens.classList.remove("on")});
  return function(){want=!0;reveal()}}
'''.replace('\n', '')

JS_LIT_OLD = ('if(A&&F&&P){A.style.setProperty("--sr",R?"190px":"clamp(240px, 21vw, 400px)"),new IntersectionObserver(function(t){'
              'Rt=t[0].isIntersecting}).observe(P),P.addEventListener("pointermove",function(t){if(t.pointerType==="mouse"){'
              'var e=F.getBoundingClientRect();ut=(t.clientX-e.left)/e.width,lt=(t.clientY-e.top)/e.height,Ht=performance.now()}});'
              'var Xt=0;if(gsap.ticker.add(function(){if(!(!Rt||!pt)){var t=performance.now(),e=t-Xt;if(!(!y&&e<30)){if(Xt=t,'
              't-Ht>2600){var o=t/1e3;ut=.66+.2*Math.sin(o*.33),lt=.46+.17*Math.sin(o*.47+1.3)}var r=1-Math.pow(.94,Math.min(e,100)'
              '/16.67);ct+=(ut-ct)*r,ft+=(lt-ft)*r,A.style.setProperty("--sx",(ct*100).toFixed(2)+"%"),A.style.setProperty("--sy",'
              '(ft*100).toFixed(2)+"%")}}}),y&&k){')
JS_EDITS = [
    # window.pcFx, замер кадров и лупа главной — в начале анимаций (до размытия при появлении)
    ['if(!yt)return;var w=matchMedia("(min-width: 1025px)").matches,', 'if(!yt)return;' + JS_PRELUDE + 'var w=matchMedia("(min-width: 1025px)").matches,'],
    ['ae=y&&!R,', 'ae=y&&!R&&!__pcfx.lite,'],
    # нарисованный курсор — не в облегчённом режиме (и снимается при его включении)
    ['if(y){I.classList.add("has-cursor");', 'if(y&&!__pcfx.lite){I.classList.add("has-cursor"),__pcfx.hooks.push(function(){I.classList.remove("has-cursor")});'],
    # подсветка карточек за курсором
    ['y&&document.addEventListener("pointermove",function(t){var e=t.target.closest&&t.target.closest(".card,.form");',
     'y&&document.addEventListener("pointermove",function(t){if(__pcfx.lite)return;var e=t.target.closest&&t.target.closest(".card,.form");'],
    # лупа главной вместо «фонаря»: прежний пересчёт маски в каждом кадре (gsap.ticker) убран
    ['A=a("#heroLit")', 'A=a("#heroLens")'],
    ['Rt=!0,pt=!1;' + JS_LIT_OLD, 'Rt=!0,pt=!1,__pcshow=function(){};if(A&&F&&P){y&&!R&&!__pcfx.lite&&(__pcshow=__pclens(P,F,A,k));if(y&&k){'],
    ['P.addEventListener("pointermove",function(t){var e=t.clientX/innerWidth-.5,o=t.clientY/innerHeight-.5;Ft(-e*30)',
     'P.addEventListener("pointermove",function(t){if(__pcfx.lite)return;var e=t.clientX/innerWidth-.5,o=t.clientY/innerHeight-.5;Ft(-e*30)'],
    ['P.addEventListener("pointerleave",function(){Ft(0),Wt(0),Dt(0),Nt(0)})}',
     'P.addEventListener("pointerleave",function(){Ft(0),Wt(0),Dt(0),Nt(0)}),__pcfx.hooks.push(function(){Ft(0),Wt(0),Dt(0),Nt(0)})}'],
    # параллакс фото и блик панели внутренних страниц
    ['g.addEventListener("pointermove",function(t){var e=t.clientX/innerWidth-.5,o=t.clientY/innerHeight-.5;$t(-e*22),zt(-o*14)}),'
     'g.addEventListener("pointerleave",function(){$t(0),zt(0)})}',
     'g.addEventListener("pointermove",function(t){if(__pcfx.lite)return;var e=t.clientX/innerWidth-.5,o=t.clientY/innerHeight-.5;$t(-e*22),zt(-o*14)}),'
     'g.addEventListener("pointerleave",function(){$t(0),zt(0)}),__pcfx.hooks.push(function(){$t(0),zt(0)})}'],
    ['W.addEventListener("pointermove",function(t){var e=W.getBoundingClientRect();',
     'W.addEventListener("pointermove",function(t){if(__pcfx.lite)return;var e=W.getBoundingClientRect();'],
    # вход первого экрана: фото без прежнего слоя, лупа — после входа фото (2,6 с)
    ['gsap.set(".hero-bg,.hero-lit",{scale:1.18})', 'gsap.set(".hero-bg",{scale:1.18})'],
    ['pt=!0;var s=gsap.timeline({defaults:{ease:"expo.out"}});s.fromTo(".hero-bg,.hero-lit",{scale:1.18},{scale:1,duration:2.6},0).to(A,{opacity:1,duration:2},.4)',
     'var s=gsap.timeline({defaults:{ease:"expo.out"}});s.fromTo(".hero-bg",{scale:1.18},{scale:1,duration:2.6},0).add(__pcshow,2.65)'],
    ['var Ut=function(){g||!A||(pt=!0,gsap.to(A,{opacity:1,duration:2,ease:"expo.out",delay:Math.max(0,N.t0+400-performance.now())/1e3}))};',
     'var Ut=function(){g||setTimeout(__pcshow,Math.max(0,N.t0+2650-performance.now()))};'],
]


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    out_dir = pathlib.Path(sys.argv[1]).resolve()
    check = '--check' in sys.argv[2:]
    resume = '--resume' in sys.argv[2:]
    live = module('check_live', 'tools/qa/check_live.py')
    site = live.SITE
    if check:
        assert (out_dir / 'backup').is_dir()
    elif resume:
        assert (out_dir / 'backup').is_dir() and not (out_dir / 'deploy_payload.json').exists(), 'нечего продолжать'
    else:
        assert not out_dir.exists(), 'используйте новую папку: прежние копии не перезаписываются'
        (out_dir / 'backup').mkdir(parents=True)

    def fetch(rel_url, rel_file):
        f = out_dir / 'backup' / rel_file
        if check or (resume and f.is_file()):
            return f.read_bytes()
        status, body = live.get(site + rel_url, tries=12)  # ложные 502 из облака — больше повторов
        assert status == 200, rel_url + ': HTTP ' + str(status)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(body)
        return body

    # страницы — как в sitemap.xml рабочего сайта + политика и согласие
    smap = fetch('sitemap.xml', 'sitemap.xml')
    paths = []
    for node in ET.fromstring(smap).iter():
        if node.tag.endswith('}loc') or node.tag == 'loc':
            url = node.text.strip()
            assert url.startswith(site), url
            p = urllib.parse.urlsplit(url).path.lstrip('/')
            if p.endswith('/') or p == '':
                paths.append(p)
    paths = sorted(set(paths) | set(LEGAL))
    assert 30 <= len(paths) <= 60, 'неожиданное число страниц: %d' % len(paths)
    assert 'zashchita-ot-proniknoveniya-gryzunov/' not in paths, 'страница защиты от проникновения — только в превью'

    if not check and not resume:  # новых фото на сайте ещё нет
        for rel in IMAGES:
            status, _ = live.get(site + rel, tries=8)
            assert status == 404, rel + ': на сайте уже есть (HTTP %s)' % status

    parts = tracking_laws.counter_parts()
    home_css = lupa.home_css_hunks()

    def page(path):
        original = fetch(path, path + 'index.php')
        text = original.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text, path + ': PHP в HTML'
        counters = path not in LEGAL
        bad = tracking_laws.check_page(text, counters=counters, parts=parts)
        assert not bad, path + ': живая страница нарушает закон о счётчиках: ' + str(bad[:3])
        refs = re.findall(r'[^"\' ]*\?v=' + OLD_V, text)
        assert refs and all(r.endswith(('style.css?v=' + OLD_V, 'app.min.js?v=' + OLD_V, 'legal.css?v=' + OLD_V)) for r in refs), path + ': ' + str(refs)
        # legal.css у политики и согласия на сайте — своей версии (?v=20261108), она не меняется
        assert not re.search(r'(?:style\.css|app\.min\.js)\?v=(?!' + OLD_V + r')', text), path + ': другая версия стилей и скрипта'
        replace = lupa.page_edits(text, OLD_V, NEW_V, home_css=home_css)
        result = lupa.apply(text, replace)
        assert not lupa.problems(result), path + ': ' + '; '.join(lupa.problems(result))
        assert lupa.revert(result, replace) == text, path + ': изменения вне согласованных мест'
        bad = tracking_laws.check_page(result, counters=counters, parts=parts)
        assert not bad, path + ': правка нарушает закон о счётчиках: ' + str(bad[:3])
        for k, p in parts.items():
            if counters:
                assert text.count(p) == result.count(p) == 1, path + ': часть счётчиков ' + k
            else:
                assert text.count(p) == result.count(p) == 0, path + ': счётчики на юридической странице'
        res = result.encode('utf-8')
        f = out_dir / 'pkg' / (path + 'index.php')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(res)
        return {'file': path + 'index.php', 'before': sha(original), 'after': sha(res), 'replace': replace}

    (out_dir / 'pkg').mkdir(parents=True, exist_ok=True)
    # стили: те же правки, что в style.css репозитория
    css_old = fetch('style.css?v=' + OLD_V, 'style.css')
    css = css_old.decode('utf-8')
    assert '.lowfx ' not in css and '.hero-lens' not in css, 'style.css: правка уже на сайте'
    css_edits = []
    for variants in lupa.style_hunks():
        css_edits.append(list(lupa.choose(css, variants, 'style.css')) + [1])
    css_new_text = lupa.apply(css, css_edits)
    assert lupa.revert(css_new_text, css_edits) == css
    assert not re.search(r'\.hero-lit\b', css_new_text) and css_new_text.count('.lowfx .hero-lens') == 1
    css_new = css_new_text.encode('utf-8')
    (out_dir / 'pkg/style.css').write_bytes(css_new)

    # скрипт: точные замены в рабочем app.min.js
    js_old = fetch(JS + '?v=' + OLD_V, JS)
    js = js_old.decode('utf-8')
    assert '__pcfx' not in js and 'heroLens' not in js, 'app.min.js: правка уже на сайте'
    js_edits = [[a, b, 1] for a, b in JS_EDITS]
    js_new_text = lupa.apply(js, js_edits)
    assert lupa.revert(js_new_text, js_edits) == js
    for w in ('heroLit', '.hero-lit', 'gsap.to(A,', '.to(A,', 'A.style.setProperty'):
        assert w not in js_new_text, 'app.min.js: осталось ' + w
    js_new = js_new_text.encode('utf-8')
    (out_dir / 'pkg' / JS).write_bytes(js_new)
    node = subprocess.run(['node', '--check', str(out_dir / 'pkg' / JS)], capture_output=True, cwd=ROOT)
    assert node.returncode == 0, 'app.min.js: синтаксис ' + node.stderr.decode()

    # новые фото — байт в байт из репозитория
    img_rows = []
    for rel in IMAGES:
        b = (ROOT / rel).read_bytes()
        assert b[:4] == b'RIFF' and b[8:12] == b'WEBP', rel
        f = out_dir / 'pkg' / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b)
        img_rows.append({'file': rel, 'before': None, 'after': sha(b), 'content_b64': base64.b64encode(b).decode('ascii')})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pages = sorted(pool.map(page, paths), key=lambda r: r['file'])

    # порядок выкладки: новые фото, стили, скрипт, затем страницы
    rows = img_rows + [{'file': 'style.css', 'before': sha(css_old), 'after': sha(css_new), 'replace': css_edits},
                       {'file': JS, 'before': sha(js_old), 'after': sha(js_new), 'replace': js_edits}] + pages
    payload = {'name': NAME, 'old_version': OLD_V, 'new_version': NEW_V, 'pages': len(pages), 'images': len(img_rows), 'files': rows}
    data = json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8') + b'\n'
    manifest = ''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows)
    if check:
        assert (out_dir / 'deploy_payload.json').read_bytes() == data, 'пакет не совпадает'
        assert (out_dir / 'MANIFEST.txt').read_text(encoding='utf-8') == manifest
        print('пакет совпадает: %d файлов' % len(rows))
        return
    (out_dir / 'deploy_payload.json').write_bytes(data)
    (out_dir / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print('Готово: %d файлов (3 фото, style.css, app.min.js и %d страниц). Пакет: %s' % (len(rows), len(pages), out_dir))


if __name__ == '__main__':
    main()
