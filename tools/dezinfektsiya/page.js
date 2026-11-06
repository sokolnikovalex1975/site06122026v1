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
        var parts=['Страница: дезинфекция для организаций (/dezinfektsiya/)'];
        if(tp&&tp.selectedIndex>0)parts.push('Объект: '+tp.options[tp.selectedIndex].text);
        if(tk&&tk.value)parts.push('Задача: '+tk.value);
        if(cm&&cm.value.trim())parts.push('Комментарий / адрес: '+cm.value.trim());
        ms.value=parts.join('\n');
      }
    },true);
  }
})();
