/* Предпросмотр: вне рабочего домена заявка не отправляется (на пестконтроль-центр.рф этот блок не срабатывает) */
(function(){
  if(!/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname)){
    var origFetch=window.fetch;
    window.fetch=function(u){
      if(typeof u==='string'&&u.indexOf('send.php')>-1){
        return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},400)});
      }
      return origFetch.apply(this,arguments);
    };
  }
  /* самопроверка: 5 пунктов */
  var box=document.getElementById('samoproverka');
  if(box){
    var cbs=box.querySelectorAll('input[type=checkbox]'),res=document.getElementById('chk-res'),note=document.getElementById('chk-note');
    var upd=function(){
      var n=0;for(var i=0;i<cbs.length;i++)if(cbs[i].checked)n++;
      res.innerHTML='<b>'+n+'</b> из '+cbs.length+' на месте';
      res.classList.toggle('warn',n<cbs.length);
      note.textContent=n===cbs.length
        ?'Все пять пунктов закрыты — продлите график, чтобы следующий акт и запись в журнале появились вовремя. Напомним о сроке и приедем в удобное окно.'
        :'Не хватает '+(cbs.length-n)+' из '+cbs.length+'. За один выезд очистим и продезинфицируем систему, оформим акт по п. 43 ППР и заведём журнал по МР 3.5.0396-25.';
    };
    for(var i=0;i<cbs.length;i++)cbs[i].addEventListener('change',upd);
  }
  /* схема воздуховода: до работ → после очистки → после дезинфекции */
  var vd=document.getElementById('vduct');
  if(vd){
    var bs=vd.querySelectorAll('.v-seg button'),caps=vd.querySelectorAll('[data-cap]'),touched=false,timers=[];
    var set=function(st){
      vd.setAttribute('data-state',st);
      for(var i=0;i<bs.length;i++)bs[i].setAttribute('aria-pressed',bs[i].getAttribute('data-s')===st?'true':'false');
      for(var j=0;j<caps.length;j++)caps[j].hidden=caps[j].getAttribute('data-cap')!==st;
    };
    for(var k=0;k<bs.length;k++)bs[k].addEventListener('click',function(){
      touched=true;timers.forEach(clearTimeout);set(this.getAttribute('data-s'));
    });
    /* один показ всех состояний, когда схема впервые видна (без автопоказа при «уменьшить движение») */
    var calm=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(!calm&&'IntersectionObserver' in window){
      var vo=new IntersectionObserver(function(es){
        if(!es[0].isIntersecting)return;vo.disconnect();
        timers.push(setTimeout(function(){if(!touched)set('clean')},1800));
        timers.push(setTimeout(function(){if(!touched)set('dez')},4000));
      },{threshold:.55});
      vo.observe(vd);
    }
  }
  var lz=document.querySelectorAll('.f-lazy');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('bg-in');io.unobserve(e.target)}})},{rootMargin:'300px'});
    lz.forEach(function(el){io.observe(el)});
  }else{lz.forEach(function(el){el.classList.add('bg-in')})}
  /* заявка: тип объекта, задача, комментарий и страница — в поле msg, которое читает send.php */
  var f=document.getElementById('form');
  if(f){
    f.addEventListener('submit',function(){
      var tp=document.getElementById('f-type'),tk=document.getElementById('fk'),cm=document.getElementById('fm'),ms=document.getElementById('fmsg');
      if(ms){
        var parts=['Страница: очистка и дезинфекция вентиляции (/ochistka-dezinfektsiya-ventilyatsii/)'];
        if(tp&&tp.selectedIndex>0)parts.push('Объект: '+tp.options[tp.selectedIndex].text);
        if(tk&&tk.value)parts.push('Задача: '+tk.value);
        if(cm&&cm.value.trim())parts.push('Комментарий / адрес: '+cm.value.trim());
        ms.value=parts.join('\n');
      }
    },true);
  }
})();
/* Лупа на фото первого экрана — как на главной (с 15.11.2026 «лёгкая»): светлая копия фото в круглой маске; сдвигаются
   только круг и фото внутри него (transform), фото и маска не перерисовываются. Кадры — только пока круг догоняет мышь;
   без мыши круг стоит на открытой части фото и сам не ходит, мышь ушла с первого экрана — плавно возвращается.
   Только компьютер с мышью шире 860 px; без лупы (и без приглушения фото) — на телефонах, планшетах, при «уменьшить
   движение» и в облегчённом режиме (window.pcFx, скрипт в <head>): если, пока круг догоняет мышь, кадров меньше 40
   в секунду, режим включается сам */
(function(){
  var hero=document.getElementById('hero'),lit=document.getElementById('vLit'),mm=window.matchMedia;
  var F=window.pcFx||{mode:'',lite:false,hooks:[],set:function(){}};
  if(!hero||!lit||!lit.firstElementChild||!mm||F.lite||mm('(prefers-reduced-motion: reduce)').matches||
     !mm('(hover: hover) and (pointer: fine)').matches||mm('(max-width:860px)').matches)return;
  var media=lit.parentNode,box=lit.firstElementChild;
  var W=0,H=0,r=0,x=0,y=0,tx=0,ty=0,hx=0,hy=0,raf=0,last=0,vis=true,on=false,follow=false,off=false,dts=[];
  var place=function(){ /* круг и копия фото — ровно навстречу: копия стоит на месте фото до долей пикселя */
    var X=Math.round((x-r)*10)/10,Y=Math.round((y-r)*10)/10;
    lit.style.transform='translate3d('+X+'px,'+Y+'px,0)';
    box.style.transform='translate3d('+(-X)+'px,'+(-Y)+'px,0)';
  };
  var size=function(){
    if(off)return;
    var cs=getComputedStyle(media); /* точный размер: копия совпадает с фото (offsetWidth/offsetHeight округляют до целых) */
    W=parseFloat(cs.width)||media.offsetWidth;H=parseFloat(cs.height)||media.offsetHeight;
    r=Math.round(Math.max(240,Math.min(400,innerWidth*.21))*.72);
    lit.style.width=lit.style.height=2*r+'px';box.style.width=W+'px';box.style.height=H+'px';
    hx=W*.74;hy=H*.47;if(!follow){tx=hx;ty=hy;if(!raf){x=hx;y=hy;}}
    place();
  };
  var frame=function(now){
    raf=0;
    if(off||!vis||document.hidden)return;
    var dt=last?Math.min(Math.max(now-last,0),100):16.67;
    if(last&&F.mode!=='full'){
      dts.push(now-last);
      if(dts.length>=40){
        dts.sort(function(a,b){return a-b;});
        var med=dts[20];dts=[];
        if(med>25){document.documentElement.setAttribute('data-fps',Math.round(1000/med));F.set(true);return;}
      }
    }
    last=now;
    var k=1-Math.pow(.94,dt/16.67);
    x+=(tx-x)*k;y+=(ty-y)*k;
    if(Math.abs(tx-x)<.3&&Math.abs(ty-y)<.3){x=tx;y=ty;place();return;}
    place();
    raf=requestAnimationFrame(frame);
  };
  var kick=function(){if(!raf&&!off&&vis&&!document.hidden){last=0;raf=requestAnimationFrame(frame);}};
  hero.addEventListener('pointermove',function(e){
    if(e.pointerType!=='mouse'||off)return;
    var b=media.getBoundingClientRect();if(!b.width||!b.height)return;
    tx=(e.clientX-b.left)/b.width*W;ty=(e.clientY-b.top)/b.height*H;follow=true;kick();
  },{passive:true});
  hero.addEventListener('pointerleave',function(){if(off)return;follow=false;tx=hx;ty=hy;kick();});
  if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;kick();}).observe(hero);
  document.addEventListener('visibilitychange',kick);
  if(window.ResizeObserver)new ResizeObserver(function(){size();}).observe(media);
  addEventListener('resize',size);
  size();
  var start=function(){if(on||off)return;on=true;hero.classList.add('v-lit-on');};
  F.hooks.push(function(){off=true;if(raf)cancelAnimationFrame(raf);raf=0;hero.classList.remove('v-lit-on');});
  /* старт вместе со входом первого экрана (общий скрипт ставит класс in на надзаголовок); страховка — через 5 с */
  var eb=hero.querySelector('.eyebrow');
  if(eb&&'MutationObserver' in window){
    if(eb.classList.contains('in'))start();
    else{var mo=new MutationObserver(function(){if(eb.classList.contains('in')){mo.disconnect();start();}});mo.observe(eb,{attributes:true,attributeFilter:['class']});}
  }
  setTimeout(start,5000);
})();
/* подсветка рамки информационных карточек за курсором — как у карточек .card на главной; в облегчённом режиме — нет */
(function(){
  if(!window.matchMedia||!matchMedia('(hover: hover) and (pointer: fine)').matches)return;
  document.addEventListener('pointermove',function(e){
    if(window.pcFx&&pcFx.lite)return;
    var c=e.target.closest&&e.target.closest('.d-card');if(!c)return;
    var r=c.getBoundingClientRect();
    c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px');
  },{passive:true});
})();
