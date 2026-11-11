#!/usr/bin/env python3
"""Два варианта блока «Образец план-схемы» страницы «Схема точек пест-контроля» — превью для выбора владельцем
(11.11.2026: «Делаю оба варианта и выкладываю на GitHub, я проверю и дам команду, какой уже выкладывать на хостинг»).

    preview-skhema/variant-a/index.html — А «плотная сетка»: план · обозначения · образец PDF (оба листа) вплотную,
                                          одной высоты; ниже 1600 px PDF — полосой под планом и обозначениями
    preview-skhema/variant-b/index.html — Б «просмотрщик с реестром»: фильтр контуров и кнопка PDF сверху, план слева,
                                          реестр всех 30 точек справа; до 1200 px реестр под планом (8 точек + «Показать все»)

Страница-основа — собранная materialy/skhema-tochek-pest-kontrolya/index.html (меню, крошки, форма — как на ней);
меняется только блок #obrazets: разметка, стили (variant-a.css / variant-b.css) и скрипт плана. Превью закрыты
от индексации (noindex, canonical — на настоящую страницу), в sitemap, поиск и сборку для Timeweb не входят.
После выбора владельца вариант переносится в skhema.html / page.css / build_pages.py, папка preview-skhema удаляется.

    python3 tools/materialy-dokumenty/build_previews.py   # после build_pages.py (или build_site.py)
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import skhema_data as S  # noqa: E402
import build_pages as BP  # noqa: E402  тексты порогов и цвета — как у скрипта плана на странице

PAGE = ROOT / 'materialy' / 'skhema-tochek-pest-kontrolya' / 'index.html'
PDF = '../../' + BP.SK_PDF
SHORT = {'К1': 'Территория', 'К2': 'Периметр', 'К3': 'Помещения'}
NOTE = {'К1': 'ограждение, отмостка, ТКО', 'К2': 'ворота, доки, входы', 'К3': 'цех, склады, АБК'}
TSHORT = {'КИК': 'станция с приманкой', 'МЛ': 'ловушка механическая / клеевая', 'ИМ': 'клеевой монитор насекомых',
          'ИЛ': 'световая УФ-ловушка', 'ФЛ': 'феромонная ловушка'}
CNT = S.counts()
NAMES = {'a': 'А · плотная сетка', 'b': 'Б · просмотрщик с реестром'}


def ico(t, size=16):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true">'
            f'{S.mark(S.T[t][1], 12, 12, S.TC[t], 7)}</svg>')


def sw(k):
    if not k:
        return '<span class="sk-sw" aria-hidden="true">' + ''.join(
            f'<i class="dt" style="background:{c}"></i>' for _, c in S.K.values()) + '</span>'
    return (f'<span class="sk-sw" aria-hidden="true"><i class="ln{" dot" if k == "К3" else ""}" '
            f'style="border-color:{S.K[k][1]}"></i></span>')


def tcount(t):
    return sum(1 for p in S.POINTS if p[0].startswith(t + '-'))


def fig_a(paper, caption):
    fs = [f'<button type="button" class="sk-f is-on" data-f="" aria-pressed="true">{sw("")}'
          f'<span class="sk-f-t"><b>Все точки</b></span><span class="sk-f-n">{len(S.POINTS)}</span></button>']
    for k in S.K:
        fs.append(f'<button type="button" class="sk-f" data-f="{k}" aria-pressed="false">{sw(k)}'
                  f'<span class="sk-f-t"><b>{k} · {SHORT[k]}</b><small>{NOTE[k]}</small></span>'
                  f'<span class="sk-f-n">{CNT[k]}</span></button>')
    types = ''.join(f'<li data-t="{t}"><span class="sk-ico">{ico(t, 18)}</span><span class="skg-ty"><b>{t}</b> — {TSHORT[t]}</span>'
                    f'<span class="skg-n">{tcount(t)}</span></li>' for t in S.T)
    side = ('<div class="skg-side card">'
            '<div class="skg-grp"><p class="sk-side-h">Контуры защиты</p><div class="sk-fs" role="group" '
            f'aria-label="Показать точки контура">{"".join(fs)}</div></div>'
            f'<div class="skg-grp"><p class="sk-side-h">Типы точек</p><ul class="sk-types">{types}</ul></div>'
            '<div class="sk-info" id="skInfo" aria-live="polite"><p class="sk-info-e">Нажмите на точку на плане — '
            'здесь появятся её тип, контур, место установки и порог из реестра.</p></div></div>')
    pdf = ('<div class="skg-pdf card">'
           f'<a class="skg-sheets" href="{PDF}" download data-dl="skhema" tabindex="-1" aria-hidden="true">'
           '<img src="../../img/skhema-obrazets-p1-360.webp" srcset="../../img/skhema-obrazets-p1-360.webp 360w, '
           '../../img/skhema-obrazets-p1-720.webp 720w" sizes="(max-width:1599px) 76px, 330px" width="360" height="509" '
           'alt="" loading="lazy" decoding="async">'
           '<img src="../../img/skhema-obrazets-p2-360.webp" srcset="../../img/skhema-obrazets-p2-360.webp 360w, '
           '../../img/skhema-obrazets-p2-720.webp 720w" sizes="(max-width:1599px) 76px, 330px" width="360" height="509" '
           'alt="" loading="lazy" decoding="async"></a>'
           '<div class="skg-t"><p class="skg-k">Образец план-схемы</p>'
           '<p class="skg-m">PDF · 2 листа: план и реестр 30 точек</p>'
           '<p class="skg-d">Контуры, легенда, редакции с подписями сторон. Форма СТПК-01, заказчик обезличен.</p></div>'
           f'<a class="btn btn-w btn-lg skg-dl" href="{PDF}" download data-dl="skhema"><span class="btn-t">Скачать PDF'
           '<span class="skg-x">-образец</span></span></a></div>')
    return (f'<figure class="nb-fig sk-fig" data-fade><div class="skg"><div class="skg-plan">{paper}'
            f'<p class="sk-scroll">План шире экрана — листайте его вбок.</p></div>{side}{pdf}</div>{caption}</figure>')


def fig_b(paper, caption):
    chips = [f'<button type="button" class="skv-f is-on" data-f="" aria-pressed="true">Все точки<span class="n">{len(S.POINTS)}</span></button>']
    for k in S.K:
        chips.append(f'<button type="button" class="skv-f" data-f="{k}" aria-pressed="false"><i class="ln{" dot" if k == "К3" else ""}" '
                     f'style="border-color:{S.K[k][1]}" aria-hidden="true"></i>{k} · {SHORT[k]}<span class="n">{CNT[k]}</span></button>')
    bar = (f'<div class="skv-bar"><div class="skv-fs" role="group" aria-label="Показать точки контура">{"".join(chips)}</div>'
           f'<a class="btn btn-w skv-dl" href="{PDF}" download data-dl="skhema"><svg viewBox="0 0 24 24" width="18" height="18" '
           'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg><span class="btn-t">Скачать <span class="skv-x">образец · </span>PDF'
           '<span class="skv-x">, 2 листа</span><span class="skv-y">-образец</span></span></a></div>')
    legend = ''.join(f'<li data-t="{t}">{ico(t, 16)}<b>{t}</b> {TSHORT[t]}</li>' for t in S.T)
    rows = []
    for i, (code, k, place, thr, *_rest) in enumerate(S.POINTS):
        t = code.split('-')[0]
        rows.append(f'<tr data-i="{i}" data-k="{k}" tabindex="0"><td class="skv-c">{ico(t, 14)}<b>{code}</b></td>'
                    f'<td class="skv-t">{S.T[t][0]}</td><td class="skv-k"><i style="background:{S.K[k][1]}"></i>{k}</td>'
                    f'<td>{place}</td><td class="skv-th">{thr}</td></tr>')
    reg = ('<div class="skv-reg"><div class="skv-reg-in"><div class="skv-reg-h"><b>Реестр точек</b><span>30 точек · как на втором листе PDF</span></div>'
           '<div class="skv-tbl"><table><colgroup><col class="skv-w-c"><col class="skv-t skv-w-t"><col class="skv-k skv-w-k"><col>'
           '<col class="skv-w-th"></colgroup><thead><tr><th scope="col">№ ТПК</th><th scope="col" class="skv-t">Устройство</th>'
           '<th scope="col" class="skv-k">Контур</th><th scope="col">Место установки</th><th scope="col" class="skv-th">Порог</th>'
           f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
           '<p class="skv-note">Порог: КИК — доля съеденной приманки, ИЛ и ФЛ — особей за 14 суток, остальные — любая находка.</p></div>'
           '<button type="button" class="skv-more">Показать все 30 точек</button></div>')
    return (f'<figure class="nb-fig sk-fig" data-fade><div class="skv card">{bar}<div class="skv-body"><div class="skv-left">{paper}'
            f'<p class="sk-scroll">План шире экрана — листайте его вбок.</p><ul class="skv-legend" aria-label="Типы точек">{legend}</ul>'
            f'<p class="skv-pick" id="skvPick" aria-live="polite"></p></div>{reg}</div></div>{caption}</figure>')


JS_B = """(function(){var P=%s,K=%s,T=%s,C=%s,root=document.getElementById('skPlan'),view=document.querySelector('.skv');
if(!root||!view)return;var pts=[].slice.call(root.querySelectorAll('.sk-pt')),rows=[].slice.call(view.querySelectorAll('.skv-tbl tbody tr')),
box=view.querySelector('.skv-tbl'),more=view.querySelector('.skv-more'),pick=document.getElementById('skvPick'),
fs=[].slice.call(view.querySelectorAll('.skv-f')),pin='',all=false,tIn=0,tOut=0,fine=window.matchMedia('(hover:hover) and (pointer:fine)');
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function stacked(){return getComputedStyle(more).display!=='none';}
function lay(){var n=0,vis=0;rows.forEach(function(r){var off=!!pin&&r.getAttribute('data-k')!==pin;r.classList.toggle('is-off',off);
if(!off){vis++;r.classList.toggle('is-more',!all&&n>=8);n++;}else r.classList.remove('is-more');});
more.hidden=all||vis<=8;more.textContent='Показать все '+vis+' '+(vis%%10===1&&vis%%100!==11?'точку':vis%%10>=2&&vis%%10<=4&&(vis%%100<12||vis%%100>14)?'точки':'точек');}
function dim(test){root.classList.toggle('is-filt',!!test);pts.forEach(function(g){g.classList.toggle('is-dim',!!test&&!test(g));});}
function byK(f){return f?function(g){return g.getAttribute('data-k')===f;}:null;}
function byT(t){return function(g){return P[+g.getAttribute('data-i')][0].split('-')[0]===t;};}
function look(test){clearTimeout(tOut);clearTimeout(tIn);tIn=setTimeout(function(){dim(test);},90);}
function back(d){clearTimeout(tIn);clearTimeout(tOut);tOut=setTimeout(function(){dim(byK(pin));},d);}
function sel(i,fromPlan){var p=P[i],t=p[0].split('-')[0];pts.forEach(function(g,j){g.classList.toggle('is-sel',j===i);});
rows.forEach(function(r,j){r.classList.toggle('is-sel',j===i);r.setAttribute('aria-selected',j===i?'true':'false');});
pick.innerHTML='<b style="color:'+C[t]+'">'+esc(p[0])+'</b> · '+esc(T[t])+' · <span style="color:'+K[p[1]][2]+'">'+esc(p[1])+'</span> · '+esc(p[2])+' · порог: '+esc(p[3]);
pick.classList.add('is-on');
if(fromPlan){if(pin&&p[1]!==pin){pin='';fs.forEach(function(x){var on=!x.getAttribute('data-f');x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});dim(null);}
if(rows[i].classList.contains('is-more')){all=true;}lay();
if(!stacked()){var r=rows[i];box.scrollTop=Math.max(0,r.offsetTop-box.clientHeight/2+r.offsetHeight/2);}}}
pts.forEach(function(g,i){g.addEventListener('click',function(){sel(i,true);});
g.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();sel(i,true);}});});
rows.forEach(function(r,i){r.addEventListener('click',function(){sel(i,false);});
r.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();sel(i,false);}});
r.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse'&&fine.matches)look(function(g){return g===pts[i];});});});
box.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')back(200);});
more.addEventListener('click',function(){all=true;lay();});
function fv(el){try{return el.matches(':focus-visible');}catch(_){return true;}}
fs.forEach(function(b){var f=b.getAttribute('data-f');
b.addEventListener('click',function(){clearTimeout(tIn);clearTimeout(tOut);pin=f;
fs.forEach(function(x){var on=x===b;x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});dim(byK(f));lay();});
b.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse'&&fine.matches)look(byK(f));});
b.addEventListener('focus',function(){if(fv(b)){clearTimeout(tOut);clearTimeout(tIn);dim(byK(f));}});
b.addEventListener('blur',function(){back(150);});
b.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')back(250);});});
[].forEach.call(view.querySelectorAll('.skv-legend li[data-t]'),function(li){var t=li.getAttribute('data-t');
li.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse'&&fine.matches)look(byT(t));});
li.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')back(250);});});
lay();})();"""


def js_b():
    src = BP.plan_js()  # те же данные, что у скрипта плана на странице: точки с порогами, контуры, типы, цвета
    data = re.match(r'\(function\(\)\{var P=(\[.*?\]),K=(\{.*?\}),T=(\{.*?\}),C=(\{.*?\}),root=', src, re.S)
    assert data, 'данные скрипта плана не найдены'
    return JS_B % data.groups()


def switcher(v):
    other = 'b' if v == 'a' else 'a'
    return ('<div class="pv-sw" role="note" style="position:fixed;left:16px;bottom:16px;z-index:150;display:flex;gap:6px;'
            'align-items:center;padding:6px 6px 6px 14px;border-radius:999px;background:rgba(9,9,11,.92);'
            'border:1px solid rgba(124,134,255,.5);font:500 13px/1.2 Inter,system-ui,sans-serif;color:#fff;'
            'box-shadow:0 10px 30px -10px rgba(0,0,0,.8)">'
            f'<span>Превью: вариант {NAMES[v]}</span>'
            f'<a href="../variant-{other}/#obrazets" style="padding:7px 12px;border-radius:999px;background:#fff;color:#09090b">'
            f'Вариант {NAMES[other].split(" ")[0]} →</a></div>')


def main():
    s = PAGE.read_text(encoding='utf-8')
    a = s.index('<figure class="nb-fig sk-fig"')
    b = s.index('</figure>', a) + len('</figure>')
    fig = s[a:b]
    paper = fig[fig.index('<div class="sk-paper">'):fig.index('\n          <p class="sk-scroll">')]
    caption = re.search(r'<figcaption.*?</figcaption>', fig, re.S).group(0)
    plan = BP.plan_js()
    assert s.count(plan) == 1, 'скрипт плана на странице не найден — сначала build_pages.py'
    for v, make, css in (('a', fig_a, 'variant-a.css'), ('b', fig_b, 'variant-b.css')):
        p = s[:a] + make(paper, caption) + s[b:]
        style = (HERE / css).read_text(encoding='utf-8').strip()
        p = p.replace('</head>', f'<style id="sk-variant">{style}</style>\n</head>', 1)
        if v == 'b':
            p = p.replace(plan, js_b(), 1)
        assert 'noindex' in p
        p = p.replace('</body>', switcher(v) + '\n</body>', 1)
        out = ROOT / 'preview-skhema' / f'variant-{v}' / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(p, encoding='utf-8')
        print('  превью', out.relative_to(ROOT), len(p.encode('utf-8')) // 1024, 'КБ')


if __name__ == '__main__':
    main()
