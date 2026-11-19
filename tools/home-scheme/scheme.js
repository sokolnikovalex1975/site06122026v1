/* Схема объекта на главной: вкладки и подсветка зон */
(function(){var r=document.getElementById('shema');if(!r)return;var tabs=r.querySelectorAll('.hz-tab');
function zone(p,z){p.querySelectorAll('.f-plan [data-z]').forEach(function(g){g.classList.toggle('on',g.getAttribute('data-z')===z)});p.querySelectorAll('.hz-zl li').forEach(function(l){l.classList.toggle('on',l.getAttribute('data-z')===z)})}
r.querySelectorAll('.hz-pan').forEach(function(p){zone(p,'1');p.addEventListener('mouseover',function(e){var t=e.target.closest('[data-z]');if(t&&p.contains(t))zone(p,t.getAttribute('data-z'))});p.addEventListener('click',function(e){var t=e.target.closest('[data-z]');if(t)zone(p,t.getAttribute('data-z'))});p.addEventListener('focusin',function(e){var t=e.target.closest('li[data-z]');if(t)zone(p,t.getAttribute('data-z'))})});
/* Телефон (до 760 px), вариант A (19.11.2026): после нажатия зоны её описание — на экране, сразу под «прилипшим» планом
   и над нижней панелью. Прокрутка вверх возвращает шапку (план опускается под неё), вниз — убирает. */
var mq=window.matchMedia&&matchMedia('(max-width:760px)');function hc(){return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--hdr-c'))||56}
function show(p,li,smooth){var f=p.querySelector('.f-plan'),h=document.getElementById('hdr'),vis=h&&!h.classList.contains('hide'),pr=f.getBoundingClientRect(),r=li.getBoundingClientRect(),lim=innerHeight-90,d=0;
if(r.top<pr.bottom+8){d=r.top-(hc()+8+pr.height)-12;if(!vis&&d>-24)d=r.top-(8+pr.height)-12}else if(r.bottom>lim)d=Math.min(r.bottom-lim+12,r.top-pr.height-20);
if(Math.abs(d)>2)window.scrollBy({top:d,behavior:smooth?'smooth':'auto'});return Math.abs(d)>2}
if(mq&&mq.matches)r.querySelectorAll('.hz-pan').forEach(function(p){p.addEventListener('click',function(e){var t=e.target.closest('[data-z]');if(!t)return;var li=p.querySelector('.hz-zl li[data-z="'+t.getAttribute('data-z')+'"]');if(!li)return;
setTimeout(function(){if(show(p,li,true))setTimeout(function(){show(p,li,false)},900)},40)})});
tabs.forEach(function(b){b.addEventListener('click',function(){tabs.forEach(function(x){var on=x===b;x.classList.toggle('is-on',on);x.setAttribute('aria-selected',on);document.getElementById('hz-p-'+x.dataset.o).hidden=!on})})})})();
