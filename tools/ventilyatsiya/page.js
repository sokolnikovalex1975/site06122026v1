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
  /* кадры камеры в коробе: до работ → после очистки → после дезинфекции.
     Три фото одного участка. Смена — WebGL: щётка уходит вглубь короба и поднимает пыль, затем туман дезсредства
     накрывает участок и оседает. Без WebGL — плавная смена фото. Пока кадр на экране, состояния меняются сами по кругу;
     кнопка в углу кадра — пауза, щелчок по состоянию — остановка на нём. При «уменьшить движение» сами не меняются,
     переходы — без эффектов. Пока кадр не виден или вкладка скрыта, ничего не считается */
  var vd=document.getElementById('vduct');
  if(vd)(function(){
    var ST=['do','clean','dez'],HOLD=[2600,2400,3200],FX=[3400,3600,1100],
      art=vd.querySelector('.v-duct-art'),bs=vd.querySelectorAll('.v-seg button'),caps=vd.querySelectorAll('[data-cap]'),
      im=vd.querySelectorAll('.vk-f'),cv=vd.querySelector('.vk-gl'),pb=vd.querySelector('.vk-play'),mm=window.matchMedia,
      calm=!!(mm&&mm('(prefers-reduced-motion: reduce)').matches),
      cur=0,stopd=calm,vis=false,held=false,busy=false,R=null,tId=0,tFn=null,tLeft=0,tAt=0;
    if(!art||im.length<3||!pb)return;
    var ui=function(i){
      vd.setAttribute('data-state',ST[i]);
      for(var k=0;k<bs.length;k++)bs[k].setAttribute('aria-pressed',bs[k].getAttribute('data-s')===ST[i]?'true':'false');
      for(var j=0;j<caps.length;j++)caps[j].hidden=caps[j].getAttribute('data-cap')!==ST[i];
    };
    var pic=function(i){
      for(var k=0;k<im.length;k++){var on=k===i;im[k].classList.toggle('is-on',on);if(on)im[k].removeAttribute('aria-hidden');else im[k].setAttribute('aria-hidden','true')}
    };
    var bar=function(i,ms){ /* полоска на кнопке: сколько осталось до следующего кадра */
      for(var k=0;k<bs.length;k++)bs[k].classList.remove('vk-run');
      if(i<0)return;
      for(var n=0;n<bs.length;n++)if(bs[n].getAttribute('data-s')===ST[i]){bs[n].style.setProperty('--vk-d',ms+'ms');void bs[n].offsetWidth;bs[n].classList.add('vk-run')}
    };
    /* таймер с паузой: кадр ушёл с экрана — время стоит */
    var fire=function(){var f=tFn;tFn=null;if(f)f()};
    var later=function(ms,fn){clearTimeout(tId);tFn=fn;tLeft=ms;tAt=Date.now();if(!held)tId=setTimeout(fire,ms)};
    var drop=function(){clearTimeout(tId);tFn=null};
    var hold=function(){if(held)return;held=true;vd.classList.add('vk-hold');if(tFn){clearTimeout(tId);tLeft-=Date.now()-tAt}if(R)R.hold()};
    var thaw=function(){if(!held)return;held=false;vd.classList.remove('vk-hold');if(tFn){tAt=Date.now();tId=setTimeout(fire,Math.max(0,tLeft))}if(R)R.go()};
    var go=function(to,mode,ms,cb){
      var from=cur;cur=to;ui(to);
      if(R&&ms>0){if(busy)R.cancel();busy=true;R.run(from,to,mode,ms,function(){busy=false;pic(to);if(cb)cb()})}
      else{pic(to);if(cb)later(ms>0?900:0,cb)}
    };
    var auto=function(fresh){
      if(stopd)return;
      if(fresh)bar(cur,HOLD[cur]);
      later(HOLD[cur],function(){
        var nx=(cur+1)%3,mode=calm?2:(cur===2?3:cur),ms=R?(calm?600:FX[cur]):900;
        bar(nx,ms+HOLD[nx]);
        go(nx,mode,ms,function(){auto(false)});
      });
    };
    var setStop=function(v){
      stopd=v;vd.classList.toggle('vk-paused',v);
      pb.setAttribute('aria-label',v?'Запустить смену кадров':'Остановить смену кадров');
      if(v){drop();bar(-1)}
    };
    setStop(stopd);
    /* смена идёт только по загруженным кадрам: при быстром переходе к блоку (меню, якорь) фото ещё грузятся */
    var loaded=function(){for(var k=0;k<im.length;k++)if(!(im[k].complete&&im[k].naturalWidth))return false;return true},wl=false;
    var kick=function(){
      if(!vis||stopd||tFn||busy)return;
      if(loaded()){auto(true);return}
      if(wl)return;wl=true;
      for(var k=0;k<im.length;k++)im[k].addEventListener('load',function(){if(loaded()){wl=false;kick()}});
    };
    pb.addEventListener('click',function(){
      if(!stopd){setStop(true);return}
      setStop(false);kick();
    });
    for(var k=0;k<bs.length;k++)bs[k].addEventListener('click',function(){
      var to=ST.indexOf(this.getAttribute('data-s'));if(to<0)return;
      setStop(true);
      if(to===cur&&!busy)return;
      var fwd=to===cur+1&&!busy,mode=calm?2:(fwd?cur:3),ms=calm?400:(fwd?FX[cur]:900);
      go(to,mode,ms,null);
    });
    if('IntersectionObserver' in window){
      new IntersectionObserver(function(es){
        vis=es[es.length-1].isIntersecting;
        if(!vis){hold();return}
        if(!document.hidden)thaw();
        kick();
      },{threshold:.6}).observe(art);
      /* WebGL готовим заранее, когда кадр подходит к экрану */
      var near=new IntersectionObserver(function(es){if(es[es.length-1].isIntersecting){near.disconnect();gl()}},{rootMargin:'500px 0px'});
      near.observe(art);
    }
    document.addEventListener('visibilitychange',function(){if(document.hidden)hold();else if(vis)thaw()});

    function gl(){
      if(!cv||!window.WebGLRenderingContext)return;
      var g;try{g=cv.getContext('webgl',{alpha:false,antialias:false,depth:false,stencil:false,premultipliedAlpha:false,preserveDrawingBuffer:false,powerPreference:'low-power'})}catch(e){g=null}
      if(!g)return;
      var VS='attribute vec2 aP;varying vec2 vUv;void main(){vUv=aP*.5+.5;gl_Position=vec4(aP,0.,1.);}';
      var FS=[
        '#ifdef GL_FRAGMENT_PRECISION_HIGH','precision highp float;','#else','precision mediump float;','#endif',
        'varying vec2 vUv;uniform sampler2D uA,uB;uniform float uP,uT,uM,uAsp;uniform vec2 uRing,uVP;uniform vec4 uMark;',
        'float h3(vec3 p){p=fract(p*.1031);p+=dot(p,p.zyx+31.32);return fract((p.x+p.y)*p.z);}',
        'float h2(vec2 p){vec3 q=fract(vec3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return fract((q.x+q.y)*q.z);}',
        'float vn(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
        'return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),',
        'mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z);}',
        'float sq(float x){return x*x;}',
        'float fbm(vec3 p){float v=0.,a=.55;for(int i=0;i<4;i++){v+=a*vn(p);p=p*2.02+vec3(5.1,1.7,3.3);a*=.5;}return v;}',
        'void main(){',
        ' vec3 A=texture2D(uA,vUv).rgb,B=texture2D(uB,vUv).rgb;',
        /* q — точка в долях первого фланца; d растёт к камере (≈ 1/расстояние), r — точка на контуре сечения */
        ' vec2 q=(vUv-uVP)/uRing;float d=max(abs(q.x),abs(q.y))+1e-4;vec2 r=q/d;float lz=log(d);',
        ' vec2 c=(vUv-.5)*vec2(uAsp,1.);float fx=1.-smoothstep(.9,.975,length(c));',
        ' fx*=1.-step(uMark.x,vUv.x)*step(vUv.x,uMark.z)*step(uMark.y,vUv.y)*step(vUv.y,uMark.w);',
        ' float led=clamp(.25+.55*d,.25,1.25);vec3 col;',
        ' if(uM<.5){',
        /* щётка уходит вглубь: за ней чистый металл, у щётки — клубы пыли и пылинки, летящие к камере */
        '  float e=1.-pow(1.-uP,1.3);',
        '  float dF=3.7*pow(1.-e,1.6)+.04;',
        '  float n=fbm(vec3(r*2.6,uT*.35));',
        '  float m=smoothstep(dF*.92,dF*1.08,d*(1.+.18*(n-.5)));m=max(m,smoothstep(.9,1.,uP));',
        '  col=mix(A,B,m);',
        '  float env=smoothstep(0.,.06,uP)*(1.-smoothstep(.84,1.,uP));',
        '  float band=exp(-sq((d-dF*.9)/(.26*dF)));',
        '  float cl=smoothstep(.3,.8,fbm(vec3(r*3.2,lz*2.6-uT*1.3)));',
        '  col=mix(col,vec3(.66,.62,.56)*led,clamp(band*env*(.12+.88*cl)*.85,0.,.78)*fx);',
        '  float an=atan(q.y,q.x)+3.14159;vec2 gg=vec2((lz-uT*.9)*7.6,an*7.6);vec2 gi=floor(gg),gf=fract(gg)-.5;',
        '  vec2 of=vec2(h2(gi+7.3),h2(gi+3.1))-.5;float rd=.07+.09*h2(gi+5.1);',
        '  float sp=smoothstep(rd,0.,length((gf-of*.6)*vec2(.55,1.)))*step(.88,h2(gi))*(.35+.65*h2(gi+1.7));',
        '  col+=vec3(.92,.89,.82)*sp*exp(-sq((d-dF)/(.45*dF)))*env*.5*led*fx;',
        ' }else if(uM<1.5){',
        /* туман дезсредства: приходит из глубины, накрывает участок, под ним кадр меняется, потом туман оседает */
        '  float dM=exp(mix(log(.04),log(4.6),smoothstep(0.,.5,uP)));',
        '  float n=fbm(vec3(r*2.,lz*1.8-uT*.6));',
        '  float fr=smoothstep(dM*1.3,dM*.7,d*(1.+.5*(n-.5)));',
        '  float pk=exp(-sq((uP-.55)/.12));',
        '  float bl=fbm(vec3(r*2.8+3.,lz*2.4-uT*.8));',
        '  float dens=(fr*(.45+.55*smoothstep(.25,.85,bl))+.25*pk)*(1.-smoothstep(.62,1.,uP));',
        '  col=mix(A,B,smoothstep(.42,.68,uP));',
        '  vec3 fc=vec3(.84,.88,.92)*(.55+.45*clamp(d/2.4,0.,1.))*(.85+.3*bl);',
        '  col=mix(col,fc,clamp(dens*.85,0.,.86)*fx);',
        '  vec2 sg=floor(c*150.);col+=vec3(1.)*step(.9985,h2(sg+floor(uT*5.)))*clamp(dens,0.,1.)*.22*fx;',
        ' }else if(uM<2.5){',
        '  col=mix(A,B,smoothstep(0.,1.,uP));',
        ' }else{',
        /* к началу — через затемнение, как новый проход камеры */
        '  col=uP<.5?mix(A,vec3(.02),smoothstep(0.,.5,uP)):mix(vec3(.02),B,smoothstep(.5,1.,uP));',
        ' }',
        ' gl_FragColor=vec4(col,1.);',
        '}'].join('\n');
      var sh=function(t,src){var s=g.createShader(t);g.shaderSource(s,src);g.compileShader(s);return g.getShaderParameter(s,g.COMPILE_STATUS)?s:null};
      var vs=sh(g.VERTEX_SHADER,VS),fs=sh(g.FRAGMENT_SHADER,FS);if(!vs||!fs)return;
      var pr=g.createProgram();g.attachShader(pr,vs);g.attachShader(pr,fs);g.linkProgram(pr);
      if(!g.getProgramParameter(pr,g.LINK_STATUS))return;
      g.useProgram(pr);
      var bf=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,bf);g.bufferData(g.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),g.STATIC_DRAW);
      var loc=g.getAttribLocation(pr,'aP');g.enableVertexAttribArray(loc);g.vertexAttribPointer(loc,2,g.FLOAT,false,0,0);
      var U=function(n){return g.getUniformLocation(pr,n)},uP=U('uP'),uT=U('uT'),uM=U('uM'),uAsp=U('uAsp');
      g.uniform1i(U('uA'),0);g.uniform1i(U('uB'),1);
      g.uniform2f(U('uRing'),.155,.218);g.uniform2f(U('uVP'),.5,.512);
      g.uniform4f(U('uMark'),.8335,.9089,.9609,.9567); /* плашка «ИЛЛЮСТРАЦИЯ» на кадрах — пыль и туман её не закрывают */
      g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,true);
      var tex=[],ready=0,anim=null,raf=0,last=0,dirty=true;
      /* ширина выбранного файла из srcset (naturalWidth у srcset-картинок — в CSS-пикселях, не в пикселях файла) */
      var fileW=function(el){var s=el.currentSrc||el.src,ps=(el.getAttribute('srcset')||'').split(',');
        for(var i=0;i<ps.length;i++){var t=ps[i].trim().split(/\s+/);if(t[0]&&/w$/.test(t[1]||'')&&s.indexOf(t[0].replace(/^(\.\.\/)+/,''))>-1)return parseInt(t[1],10)}
        return 1440};
      var size=function(){
        var w=cv.clientWidth,h=cv.clientHeight;if(!w||!h)return;
        var k=Math.min(window.devicePixelRatio||1,2),W=Math.round(w*k),H=Math.round(h*k),mx=fileW(im[0]);
        if(W>mx){H=Math.round(H*mx/W);W=mx}
        if(W*H>1.6e6){var s=Math.sqrt(1.6e6/(W*H));W=Math.round(W*s);H=Math.round(H*s)}
        if(cv.width!==W||cv.height!==H){cv.width=W;cv.height=H}
        g.viewport(0,0,W,H);g.uniform1f(uAsp,W/H);dirty=false;
      };
      var draw=function(a,b,mode,p,t){
        if(dirty)size();
        g.activeTexture(g.TEXTURE0);g.bindTexture(g.TEXTURE_2D,tex[a]);
        g.activeTexture(g.TEXTURE1);g.bindTexture(g.TEXTURE_2D,tex[b]);
        g.uniform1f(uP,p);g.uniform1f(uT,t);g.uniform1f(uM,mode);
        g.drawArrays(g.TRIANGLES,0,3);
      };
      var tick=function(now){
        raf=0;if(!anim)return;
        anim.el+=Math.min(now-last,50);last=now;
        var p=Math.min(anim.el/anim.ms,1);
        draw(anim.a,anim.b,anim.mode,p,anim.el/1000);
        if(p>=1){var cb=anim.cb;anim=null;if(cb)cb();return}
        raf=requestAnimationFrame(tick);
      };
      var still=function(){if(!anim&&R)draw(cur,cur,2,1,0)};
      var up=function(i){
        var t=g.createTexture();g.bindTexture(g.TEXTURE_2D,t);
        g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.LINEAR);
        g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
        try{g.texImage2D(g.TEXTURE_2D,0,g.RGB,g.RGB,g.UNSIGNED_BYTE,im[i])}catch(e){return}
        tex[i]=t;
        if(++ready===3){
          R={
            run:function(a,b,mode,ms,cb){if(raf)cancelAnimationFrame(raf);raf=0;anim={a:a,b:b,mode:mode,ms:ms,el:0,cb:cb};if(!held){last=performance.now();raf=requestAnimationFrame(tick)}},
            cancel:function(){if(raf)cancelAnimationFrame(raf);raf=0;anim=null},
            hold:function(){if(raf)cancelAnimationFrame(raf);raf=0},
            go:function(){if(anim&&!raf){last=performance.now();raf=requestAnimationFrame(tick)}}
          };
          if(!busy)still();
          vd.classList.add('vk-gl-on');
        }
      };
      for(var i=0;i<3;i++)(function(i){
        var el=im[i];
        if(el.complete&&el.naturalWidth)up(i);
        else el.addEventListener('load',function(){up(i)},{once:true});
      })(i);
      var rs=function(){dirty=true;if(!anim)still()};
      if('ResizeObserver' in window)new ResizeObserver(rs).observe(cv);else window.addEventListener('resize',rs);
      cv.addEventListener('webglcontextlost',function(e){
        e.preventDefault();var cb=anim&&anim.cb;if(raf)cancelAnimationFrame(raf);raf=0;anim=null;R=null;
        vd.classList.remove('vk-gl-on');busy=false;pic(cur);if(cb)cb();
      });
    }
  })();
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
