#!/usr/bin/env python3
"""Тестовые страницы курсора для белых объектов (запрос владельца 11.11.2026: «мышки не видно на белом фоне… Сделай оба
варианта, я посмотрю, как это будет работать… Тестовых страницы нужно для этого»).

    preview-kursor/variant-a/ — А «Инверсия»: курсор меняет цвет на противоположный фону (mix-blend-mode: difference)
    preview-kursor/variant-b/ — Б «Обводка»: белая точка и кольцо с тонкой тёмной обводкой, видно на любом фоне
    preview-kursor/variant-v/ — В «Фирменный прицел»: на тёмном — как сейчас; на светлом (план, документ, светлая картинка)
                                — фиолетовый прицел как в логотипе; на ссылке-документе — фиолетовый круг «Скачать PDF» / «Открыть»

Основа — собранная страница materialy/skhema-tochek-pest-kontrolya/ (план на белом бланке, листы PDF). Меняется только
курсор: стили и небольшой скрипт поверх курсора app.min.js; Метрика, UIS, Radist — как на странице. Превью закрыты noindex
и в sitemap, поиск, меню и сборку для Timeweb не входят. После выбора вариант переносится в style.css / app.js для всего сайта.

    python3 tools/kursor-preview/build.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGE = ROOT / 'materialy' / 'skhema-tochek-pest-kontrolya' / 'index.html'
NAMES = {'a': ('А', 'Инверсия'), 'b': ('Б', 'Обводка'), 'v': ('В', 'Фирменный прицел')}

# общее для всех вариантов: точки плана — без системной «руки», курсор показывает их как ссылку
COMMON_CSS = '@media (hover:hover) and (pointer:fine){html.has-cursor .sk-pt{cursor:none}}'
COMMON_JS = """(function(){var cur=document.querySelector('.cursor'),hot=false;if(!cur)return;
addEventListener('pointermove',function(e){var t=e.target;hot=!!(t.closest&&t.closest('.sk-pt'));
 if(hot)requestAnimationFrame(function(){if(hot)cur.classList.add('link');});},{passive:true});})();  /* после курсора app.min.js — он снимает link */"""

CSS = {
    'a': """@media (hover:hover) and (pointer:fine){
.has-cursor .cursor{mix-blend-mode:difference}
.cursor-dot{width:8px;height:8px;margin:-4px 0 0 -4px;background:#fff}
.cursor-ring{border:1.5px solid #fff;opacity:.9}
.cursor.link .cursor-ring{width:58px;height:58px;margin:-29px 0 0 -29px;background:none;border:2px solid #fff;opacity:1}
.cursor.link .cursor-dot{opacity:1}}""",
    'b': """@media (hover:hover) and (pointer:fine){
.cursor-dot{width:8px;height:8px;margin:-4px 0 0 -4px;background:#fff;box-shadow:0 0 0 1.5px rgba(9,9,11,.9),0 1px 4px rgba(0,0,0,.45)}
.cursor-ring{border:1.5px solid rgba(255,255,255,.8);box-shadow:0 0 0 1px rgba(9,9,11,.45),inset 0 0 0 1px rgba(9,9,11,.45)}
.cursor.link .cursor-ring{background:rgba(97,95,255,.16);border:2px solid #fff;box-shadow:0 0 0 1px rgba(9,9,11,.55),inset 0 0 0 1px rgba(9,9,11,.4)}}""",
    'v': """@media (hover:hover) and (pointer:fine){
.cursor-dot{box-shadow:0 0 0 1px rgba(9,9,11,.5)}
.cursor-ring{border-color:rgba(255,255,255,.5);box-shadow:0 0 0 1px rgba(9,9,11,.22)}
.cursor.link .cursor-ring{border-color:rgba(255,255,255,.75)}
.cursor-dot{transition:width .3s var(--ease),height .3s var(--ease),margin .3s var(--ease),background .3s,box-shadow .3s,opacity .3s}
.cursor-ring{color:#615fff}
.cursor-ring::before,.cursor-ring::after{content:"";position:absolute;background:currentColor;opacity:0;transition:opacity .25s}
.cursor-lbl{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:0 8px;text-align:center;
 font:600 10px/1.15 Inter,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#fff;opacity:0;transition:opacity .2s}
.cursor.light .cursor-dot{width:8px;height:8px;margin:-4px 0 0 -4px;background:#615fff;box-shadow:0 0 0 2px #fff}
.cursor.light .cursor-ring{width:34px;height:34px;margin:-17px 0 0 -17px;border:2px solid #615fff;background:rgba(97,95,255,.06)}
.cursor.light .cursor-ring::before{opacity:1;left:50%;top:-8px;width:2px;height:calc(100% + 16px);margin-left:-1px;
 -webkit-mask:linear-gradient(#000 0 9px,transparent 9px calc(100% - 9px),#000 calc(100% - 9px));mask:linear-gradient(#000 0 9px,transparent 9px calc(100% - 9px),#000 calc(100% - 9px))}
.cursor.light .cursor-ring::after{opacity:1;top:50%;left:-8px;height:2px;width:calc(100% + 16px);margin-top:-1px;
 -webkit-mask:linear-gradient(90deg,#000 0 9px,transparent 9px calc(100% - 9px),#000 calc(100% - 9px));mask:linear-gradient(90deg,#000 0 9px,transparent 9px calc(100% - 9px),#000 calc(100% - 9px))}
.cursor.light.link .cursor-ring{width:44px;height:44px;margin:-22px 0 0 -22px;background:rgba(97,95,255,.16)}
.cursor.light.doc .cursor-ring{width:84px;height:84px;margin:-42px 0 0 -42px;background:#615fff;border-color:#615fff;box-shadow:0 10px 30px -8px rgba(97,95,255,.7)}
.cursor.light.doc .cursor-ring::before,.cursor.light.doc .cursor-ring::after{opacity:0}
.cursor.light.doc .cursor-dot{opacity:0}
.cursor.light.doc .cursor-lbl{opacity:1}
.cursor.light.down .cursor-ring{transform-origin:center}
}
@media (prefers-reduced-motion:reduce){.cursor-dot,.cursor-lbl,.cursor-ring::before,.cursor-ring::after{transition:none!important}}""",
}

# В: курсор сам определяет светлый объект под собой — фон элемента или яркость картинки (один раз на картинку)
JS_V = """(function(){var cur=document.querySelector('.cursor'),ring=document.querySelector('.cursor-ring');if(!cur||!ring)return;
var lbl=document.createElement('b');lbl.className='cursor-lbl';ring.appendChild(lbl);
var cache=new WeakMap(),imgs=new WeakMap(),last=null;
function lum(r,g,b){return (0.2126*r+0.7152*g+0.0722*b)/255;}
function imgLight(im){if(imgs.has(im))return imgs.get(im);var v=false;
 try{if(im.complete&&im.naturalWidth){var c=document.createElement('canvas');c.width=c.height=8;var x=c.getContext('2d');x.drawImage(im,0,0,8,8);
 var d=x.getImageData(0,0,8,8).data,s=0;for(var i=0;i<d.length;i+=4)s+=lum(d[i],d[i+1],d[i+2]);v=s/64>.62;imgs.set(im,v);}}catch(_){imgs.set(im,false);}
 return v;}
function light(el){for(var n=el,k=0;n&&n.nodeType===1&&k<14;n=n.parentElement,k++){
 var m=n.getAttribute('data-cursor');if(m==='light')return true;if(m==='dark')return false;
 if(n.classList&&n.classList.contains('btn'))return false;
 if(n.tagName==='IMG')return imgLight(n);
 var bg=getComputedStyle(n).backgroundColor,p=bg.match(/[\\d.]+/g);
 if(p&&(p.length<4||+p[3]>.5))return lum(+p[0],+p[1],+p[2])>.62;}
 return false;}
function doc(t){var a=t.closest&&t.closest('a[href]');if(!a||a.classList.contains('btn'))return '';
 var h=a.getAttribute('href')||'';if(a.hasAttribute('download')||/\\.pdf($|[?#])/i.test(h))return 'Скачать PDF';return a.querySelector('img')?'Открыть':'';}
addEventListener('pointermove',function(e){var t=e.target;if(t===last)return;last=t;
 var l=cache.has(t)?cache.get(t):light(t);cache.set(t,l);var d=l?doc(t):'';
 cur.classList.toggle('light',l);cur.classList.toggle('doc',!!d);if(d)lbl.textContent=d;},{passive:true});
addEventListener('scroll',function(){last=null;},{passive:true});
})();"""


def switcher(v):
    links = ''.join(
        f'<a href="../variant-{k}/#obrazets" style="padding:7px 12px;border-radius:999px;'
        + ('background:#fff;color:#09090b' if k == v else 'color:#fff;border:1px solid rgba(255,255,255,.25)')
        + f'"{" aria-current=page" if k == v else ""}>{n[0]} · {n[1]}</a>' for k, n in NAMES.items())
    return ('<div class="pv-sw" role="note" data-cursor="dark" style="position:fixed;left:16px;bottom:16px;z-index:150;display:flex;'
            'flex-wrap:wrap;gap:6px;align-items:center;padding:6px 6px 6px 14px;border-radius:999px;background:rgba(9,9,11,.94);'
            'border:1px solid rgba(124,134,255,.5);font:500 13px/1.2 Inter,system-ui,sans-serif;color:#fff;'
            f'box-shadow:0 10px 30px -10px rgba(0,0,0,.8)"><span>Тест курсора:</span>{links}</div>')


def main():
    s = PAGE.read_text(encoding='utf-8')
    assert 'noindex' in s and '<div class="cursor"' in s
    for v in NAMES:
        p = s.replace('</head>', f'<style id="kursor-test">{COMMON_CSS}\n{CSS[v]}</style>\n</head>', 1)
        js = COMMON_JS + (JS_V if v == 'v' else '')
        p = p.replace('</body>', f'<script>{js}</script>\n{switcher(v)}\n</body>', 1)
        out = ROOT / 'preview-kursor' / f'variant-{v}' / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(p, encoding='utf-8')
        print('  тест курсора', out.relative_to(ROOT))


if __name__ == '__main__':
    main()
