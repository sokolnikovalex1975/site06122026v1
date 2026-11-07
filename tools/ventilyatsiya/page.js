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
/* Фонарь на фото первого экрана — как на главной: следует за мышью, без движения мыши плавно ходит сам,
   на сенсорных экранах ходит сам (30 кадров в секунду). Не считаем, пока первый экран не виден или вкладка скрыта.
   При «уменьшить движение» фонаря нет — фото остаётся как было */
(function(){
  var hero=document.getElementById('hero'),lit=document.getElementById('vLit'),mm=window.matchMedia;
  if(!hero||!lit||!mm||mm('(prefers-reduced-motion: reduce)').matches)return;
  var media=lit.parentNode,fine=mm('(hover: hover) and (pointer: fine)').matches,small=mm('(max-width:860px)').matches;
  lit.style.setProperty('--sr',small?'150px':'clamp(240px, 21vw, 400px)');
  var cx=small?.5:.74,ax=small?.24:.13,cy=small?.5:.47,ay=small?.2:.17;
  var sx=cx,sy=cy,tx=cx,ty=cy,last=-1e9,vis=true,on=false,raf=0,lt=0;
  var frame=function(now){
    raf=0;
    if(!on||!vis||document.hidden)return;
    var dt=now-lt;
    if(!fine&&dt<30){raf=requestAnimationFrame(frame);return;}
    lt=now;
    if(now-last>2600){var t=now/1000;tx=cx+ax*Math.sin(t*.33);ty=cy+ay*Math.sin(t*.47+1.3);}
    var k=1-Math.pow(.94,Math.min(dt,100)/16.67);
    sx+=(tx-sx)*k;sy+=(ty-sy)*k;
    lit.style.setProperty('--sx',(sx*100).toFixed(2)+'%');
    lit.style.setProperty('--sy',(sy*100).toFixed(2)+'%');
    raf=requestAnimationFrame(frame);
  };
  var kick=function(){if(!raf&&on&&vis&&!document.hidden){lt=performance.now();raf=requestAnimationFrame(frame);}};
  hero.addEventListener('pointermove',function(e){
    if(e.pointerType!=='mouse')return;
    var r=media.getBoundingClientRect();if(!r.width||!r.height)return;
    tx=(e.clientX-r.left)/r.width;ty=(e.clientY-r.top)/r.height;last=performance.now();kick();
  },{passive:true});
  if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;kick();}).observe(hero);
  document.addEventListener('visibilitychange',kick);
  var start=function(){if(on)return;on=true;hero.classList.add('v-lit-on');kick();};
  /* старт вместе со входом первого экрана (общий скрипт ставит класс in на надзаголовок); страховка — через 5 с */
  var eb=hero.querySelector('.eyebrow');
  if(eb&&'MutationObserver' in window){
    if(eb.classList.contains('in'))start();
    else{var mo=new MutationObserver(function(){if(eb.classList.contains('in')){mo.disconnect();start();}});mo.observe(eb,{attributes:true,attributeFilter:['class']});}
  }
  setTimeout(start,5000);
})();
/* подсветка рамки информационных карточек за курсором — как у карточек .card на главной */
(function(){
  if(!window.matchMedia||!matchMedia('(hover: hover) and (pointer: fine)').matches)return;
  document.addEventListener('pointermove',function(e){
    var c=e.target.closest&&e.target.closest('.d-card');if(!c)return;
    var r=c.getBoundingClientRect();
    c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px');
  },{passive:true});
})();
