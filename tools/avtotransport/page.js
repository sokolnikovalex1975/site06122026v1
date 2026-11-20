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
  /* самопроверка: счёт отмеченных пунктов (полоску и форму добавляют tools/site/samoproverka*.py) */
  var box=document.getElementById('samoproverka');
  if(box){
    var cbs=box.querySelectorAll('input[type=checkbox]'),res=document.getElementById('chk-res'),note=document.getElementById('chk-note');
    var upd=function(){
      var n=0;for(var i=0;i<cbs.length;i++)if(cbs[i].checked)n++;
      res.innerHTML='<b>'+n+'</b> из '+cbs.length+' на месте';
      res.classList.toggle('warn',n<cbs.length);
      res.classList.toggle('full',n===cbs.length);
      note.textContent=n===cbs.length
        ?'Все '+cbs.length+' пунктов на месте. Пришлите список машин — составим график и посчитаем обработку.'
        :'Не хватает '+(cbs.length-n)+' из '+cbs.length+'. Отправьте отметки — подскажем, что поправить, и посчитаем дезинфекцию для ваших машин.';
    };
    for(var i=0;i<cbs.length;i++)cbs[i].addEventListener('change',upd);
  }
  /* схема кузова: подсветка зоны по пункту списка и наоборот */
  var map=document.querySelector('.avt-zmap');
  if(map){
    var plan=map.querySelector('.avt-plan'),items=map.querySelectorAll('.avt-zlist li');
    var set=function(z){
      plan.querySelectorAll('[data-z]').forEach(function(g){g.classList.toggle('on',g.getAttribute('data-z')===z)});
      items.forEach(function(li){li.classList.toggle('on',li.getAttribute('data-z')===z)});
    };
    items.forEach(function(li){
      var z=li.getAttribute('data-z');
      li.addEventListener('mouseenter',function(){set(z)});
      li.addEventListener('focus',function(){set(z)});
      li.addEventListener('click',function(){set(z)});
    });
    plan.querySelectorAll('[data-z]').forEach(function(g){
      var z=g.getAttribute('data-z');
      g.addEventListener('mouseenter',function(){set(z)});
      g.addEventListener('click',function(){set(z)});
    });
    map.addEventListener('mouseleave',function(){set(null)});
  }
  /* скачивание образца и бланка акта — цели Метрики */
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('[data-dl]');if(!a)return;
    var g={'avto-akt':'avto_akt_obrazets','avto-blank':'avto_akt_blank'}[a.getAttribute('data-dl')];
    try{if(g&&typeof ym==='function')ym(113675622,'reachGoal',g)}catch(_){}
  });
  var lz=document.querySelectorAll('.f-lazy');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('bg-in');io.unobserve(e.target)}})},{rootMargin:'300px'});
    lz.forEach(function(el){io.observe(el)});
  }else{lz.forEach(function(el){el.classList.add('bg-in')})}
  /* заявка: тип транспорта, число машин, задача, адрес и страница — в поле msg, которое читает send.php
     (у всех пунктов «Тип транспорта» значение «Другое» — оно есть в списке send.php) */
  var f=document.getElementById('form');
  if(f){
    f.addEventListener('submit',function(){
      var tp=document.getElementById('f-type'),nc=document.getElementById('f-cars'),tk=document.getElementById('fk'),cm=document.getElementById('fm'),ms=document.getElementById('fmsg');
      if(ms){
        var parts=['Страница: дезинфекция автотранспорта (/dezinfektsiya/avtotransport/)'];
        if(tp&&tp.selectedIndex>0)parts.push('Вид объекта: транспорт — '+tp.options[tp.selectedIndex].text);
        if(nc&&nc.value.trim())parts.push('Машин: '+nc.value.trim());
        if(tk&&tk.value)parts.push('Задача: '+tk.value);
        if(cm&&cm.value.trim())parts.push('Адрес и время: '+cm.value.trim());
        ms.value=parts.join('\n');
      }
    },true);
  }
})();
