/* Расчёт «Лабораторные исследования»: позиции из прайса (+, количество), наборы по видам объектов,
   панель внизу экрана, список в заявке и в поле msg для send.php. window.LB = {код: [название, единица, цена, «от»]} */
(function(){
var L=window.LB||{},S={},K='lb-calc',sent={};
try{S=JSON.parse(sessionStorage.getItem(K))||{};}catch(_){S={};}
for(var k in S){if(!L[k]||!(S[k]>0))delete S[k];}
function goal(g){if(sent[g])return;sent[g]=1;try{if(window.ym)ym(113675622,'reachGoal',g)}catch(_){}}
function rub(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,'\u00a0')+'\u00a0₽';}
function plural(n,a,b,c){var m=n%10,h=n%100;return n+' '+(m==1&&h!=11?a:m>=2&&m<=4&&(h<12||h>14)?b:c);}
function total(){var s=0,n=0;for(var k in S){s+=L[k][2]*S[k];n++;}return {s:s,n:n};}
function save(){try{sessionStorage.setItem(K,JSON.stringify(S));}catch(_){}}
function cell(id){
  var q=S[id],nm=L[id][0];
  if(!q)return '<button type="button" class="lb-add" data-add="'+id+'" aria-label="Добавить в расчёт: '+nm+'"><span aria-hidden="true">+</span></button>';
  return '<span class="lb-qty"><button type="button" data-dec="'+id+'" aria-label="Меньше: '+nm+'">−</button>'+
    '<input type="number" inputmode="numeric" min="0" max="999" value="'+q+'" data-q="'+id+'" aria-label="Количество, '+L[id][1]+': '+nm+'">'+
    '<button type="button" data-inc="'+id+'" aria-label="Больше: '+nm+'">+</button></span>';
}
function render(focus){
  var rows=document.querySelectorAll('.lb-tbl tr[data-id]');
  for(var i=0;i<rows.length;i++){
    var r=rows[i],id=r.getAttribute('data-id'),td=r.querySelector('.lb-tc'),want=S[id]?'q':'a';
    r.classList.toggle('lb-on',!!S[id]);
    if(td.getAttribute('data-st')!==want){td.innerHTML=cell(id);td.setAttribute('data-st',want);}
    else if(S[id]){var inp=td.querySelector('input');if(inp&&document.activeElement!==inp)inp.value=S[id];}
  }
  var t=total(),bar=document.getElementById('lb-bar');
  if(bar){bar.hidden=!t.n;document.body.classList.toggle('lb-has-bar',!!t.n);
    document.getElementById('lb-bar-n').textContent=plural(t.n,'позиция','позиции','позиций');
    document.getElementById('lb-bar-s').textContent='от '+rub(t.s);}
  var fc=document.getElementById('lb-fcalc');
  if(fc){fc.hidden=!t.n;var ul=document.getElementById('lb-fcalc-list'),h='';
    for(var k in S){h+='<li><span>'+L[k][0]+'</span><span>'+S[k]+' × '+rub(L[k][2])+'</span></li>';}
    ul.innerHTML=h;document.getElementById('lb-fcalc-t').textContent='Итого: от '+rub(t.s);}
  if(focus){var el=document.querySelector(focus);if(el)el.focus();}
  save();
}
function set(id,q,focus){q=Math.max(0,Math.min(999,parseInt(q,10)||0));if(q)S[id]=q;else delete S[id];if(q)goal('lab_pozitsiya');render(focus);}
document.addEventListener('click',function(e){
  var t=e.target.closest&&e.target.closest('[data-add],[data-inc],[data-dec],[data-set],[data-open],#lb-bar-clear,#lb-bar-go');
  if(!t)return;var id;
  if((id=t.getAttribute('data-add'))){set(id,1,'input[data-q="'+id+'"]');}
  else if((id=t.getAttribute('data-inc'))){set(id,(S[id]||0)+1,'[data-inc="'+id+'"]');}
  else if((id=t.getAttribute('data-dec'))){var q=(S[id]||0)-1;set(id,q,q>0?'[data-dec="'+id+'"]':'[data-add="'+id+'"]');}
  else if(t.hasAttribute('data-set')){
    try{JSON.parse(t.getAttribute('data-set')).forEach(function(p){if(L[p[0]])S[p[0]]=(S[p[0]]||0)+p[1];});}catch(_){}
    goal('lab_nabor');render();
    var ok=t.parentNode.querySelector('.lb-set-ok');if(ok){ok.textContent='Добавлено ✓';clearTimeout(ok._t);ok._t=setTimeout(function(){ok.textContent='';},2500);}
  }
  else if((id=t.getAttribute('data-open'))){var d=document.getElementById('g-'+id);if(d)d.open=true;}
  else if(t.id==='lb-bar-clear'){S={};render();}
  else if(t.id==='lb-bar-go'){goal('lab_raschet');}
});
document.addEventListener('change',function(e){var id=e.target.getAttribute&&e.target.getAttribute('data-q');if(id)set(id,e.target.value);});
document.addEventListener('keydown',function(e){var id=e.target.getAttribute&&e.target.getAttribute('data-q');if(id&&e.key==='Enter'){e.preventDefault();set(id,e.target.value);}});
function openHash(){var h=location.hash;if(h&&h.indexOf('#g-')===0){var d=document.getElementById(h.slice(1));if(d)d.open=true;}}
window.addEventListener('hashchange',openHash);openHash();
/* Заявка: вид объекта, что нужно, адрес, комментарий, расчёт и страница — в поле msg (send.php, до 3000 знаков) */
document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,
  g=e.goal.value||'не выбрано',a=e.address.value.trim()||'не указан',c=e.comment.value.trim(),
  o=e.type.options[e.type.selectedIndex],k=o&&o.value&&o.text!==o.value?'Вид объекта: '+o.text+'\n':'',r='',t=total();
  if(t.n){r='\nРасчёт:';for(var id in S){r+='\n— '+L[id][0]+': '+S[id]+' ('+L[id][1]+') × '+(L[id][3]?'от ':'')+L[id][2]+' ₽';}r+='\nИтого: от '+t.s+' ₽';}
  var m=k+'Что нужно: '+g+'\nАдрес: '+a+(c?'\nКомментарий: '+c:'')+r+'\nСтраница: Лабораторные исследования (/laboratornye-issledovaniya/)';
  e.msg.value=m.length>3000?m.slice(0,2990)+'…':m;},true);
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-goal]');if(!b)return;
  var g=document.getElementById('f-goal');if(g)g.value=b.getAttribute('data-goal');});
render();
})();
