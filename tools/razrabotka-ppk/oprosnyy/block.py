"""Блок «Опросный лист заказчика» на /razrabotka-ppk/ (#oprosnyy-list) и онлайн-форма к нему.

Содержание — content.py (тот же источник, что у PDF), сведения о PDF (листы, размер, превью) — pdf.json от build_pdf.py.
Вызывается из tools/razrabotka-ppk/build_page.py: section_html() встаёт на место метки <!--OPROSNYY--> в main.html,
FORM_JS — в конец страницы.

Онлайн-форма лежит в <template id="olTpl"> и попадает на страницу только по кнопке «Заполнить онлайн»
(ссылки с data-ol-open или адрес #oprosnyy-online), поэтому не влияет на первую отрисовку и скорость.
Отправка — тот же send.php, что у формы заявки: name, phone, email, company (ответ 1.1), type (вид объекта
из списка send.php), msg (ответы). В msg не больше 3000 знаков, поэтому длинный опросный лист уходит
несколькими письмами «часть 1 из N». Цели Метрики после ответа сервера: audit (как у всех заявок) и
ppk_oprosnyy_send; UIS — Comagic.addOfflineRequest, как в app.js. Клики по PDF — ppk_oprosnyy_ppk и
ppk_oprosnyy_haccp (общий обработчик data-dl страницы).
"""
import html
import json
import pathlib

from content import COMMENT, DOCS_ALL, DOCS_HACCP, OBJECT_TYPES, PROGRAMS, SECTIONS, count

HERE = pathlib.Path(__file__).resolve().parent
MAIL = 'b2b@pestcontrol-center.ru'


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s.replace('\u00a0', ' '), quote=True)


def kb(n):
    return f'{round(n / 1024)}\u00a0КБ'


def plural_list(n):
    return 'лист' if n % 10 == 1 and n % 100 != 11 else ('листа' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'листов')


# ---------------------------------------------------------------- блок на странице
def sections_table():
    rows = []
    for s in SECTIONS:
        tag = '<span class="rp-tag rp-tag-h">только ППК по ХАССП</span>' if s.get('haccp') else ''
        rows.append(f'        <tr><td data-l="Раздел"><span class="rp-ol-sn"><span class="rp-pt">{s["n"]}</span><b>{esc(s["title"])}</b></span>{tag}</td>'
                    f'<td data-l="Что спрашиваем">{esc(s["what"])}</td><td data-l="Для чего в программе">{esc(s["why"])}</td></tr>')
    return ('    <table class="d-table rp-ol-t">\n      <caption class="sr-only">Разделы опросного листа заказчика для разработки ППК и ППК по ХАССП</caption>\n'
            '      <thead><tr><th scope="col">Раздел</th><th scope="col">Что спрашиваем</th><th scope="col">Для чего в программе</th></tr></thead>\n'
            '      <tbody>\n' + '\n'.join(rows) + '\n      </tbody>\n    </table>\n')


def pdf_card(prog, info):
    P = PROGRAMS[prog]
    i = info[prog]
    th = {w: name for name, _, w, _ in i['thumbs']}
    alt = (f'Опросный лист для разработки {P["short"]}, лист 1: шапка ПЕСТКОНТРОЛЬ Центра, способы отправки, '
           'цена и срок, вопросы раздела «Организация и объект»')
    return (f'        <a class="rp-ol-pdf" href="{P["file"]}" target="_blank" rel="noopener" data-dl="oprosnyy_{prog}">'
            f'<span class="rp-ol-th"><img src="../img/{th[360]}" srcset="../img/{th[240]} 240w, ../img/{th[360]} 360w, ../img/{th[720]} 720w" '
            f'sizes="(max-width:600px) 30vw, 120px" width="360" height="509" loading="lazy" decoding="async" alt="{attr(alt)}"></span>'
            f'<span class="rp-ol-pt"><b>Опросный лист для {esc(P["short"])}</b><small>PDF · {i["pages"]} {plural_list(i["pages"])} · {kb(i["bytes"])}</small>'
            f'<em>Скачать PDF</em></span></a>')


def section_html():
    info = json.loads((HERE / 'pdf.json').read_text(encoding='utf-8'))
    n_ppk, n_h = count('ppk'), count('haccp')
    docs = ''.join(f'<li>{esc(d)}</li>' for d in DOCS_ALL)
    docs_h = ''.join(f'<li>{esc(d)}</li>' for d in DOCS_HACCP)
    return (
        '<section class="s" id="oprosnyy-list">\n  <div class="wrap">\n'
        '    <div class="head"><div class="eyebrow">Опросный лист</div><h2>Что нужно для разработки ППК: <em>опросный лист заказчика</em></h2>'
        '<p class="sub">Чтобы программа описывала ваш объект, нужны сведения о нём: организация, помещения, персонал, вода, вентиляция, '
        'оборудование, отходы и действующие договоры. Мы собираем их опросным листом заказчика: для ППК в нём '
        f'{n_ppk} вопросов, для ППК по ХАССП — ещё {n_h - n_ppk} о продукции и технологических процессах. '
        'Отвечайте на то, что знаете, остальное уточним по телефону. По заполненному листу называем точную цену и срок.</p></div>\n'
        + sections_table() +
        '    <div class="rp-ol">\n'
        '      <div class="card rp-ol-docs">\n'
        '        <h3>Документы, которые пригодятся</h3>\n'
        f'        <ul class="rp-ol-dl">{docs}</ul>\n'
        '        <p class="rp-ol-dh">Для ППК по ХАССП — ещё</p>\n'
        f'        <ul class="rp-ol-dl">{docs_h}</ul>\n'
        f'        <p class="rp-ol-dn">Без документов тоже можно начать — по ответам на вопросы. Документы присылайте на <a href="mailto:{MAIL}">{MAIL}</a>, в теме письма — название организации.</p>\n'
        '      </div>\n'
        '      <div class="rp-ol-get">\n'
        '        <div class="card rp-ol-how">\n'
        '          <h3>Как заполнить опросный лист</h3>\n'
        '          <ol class="rp-ol-ways">\n'
        '            <li><b>Онлайн на этой странице</b><span>ответы придут нам вместе с вашими контактами, незаконченный лист сохраняется в этом браузере</span></li>\n'
        f'            <li><b>В PDF</b><span>распечатайте, заполните и пришлите скан или фото на <a href="mailto:{MAIL}">{MAIL}</a></span></li>\n'
        '            <li><b>По телефону</b><span>специалист задаст вопросы сам: <a href="tel:+74951043570">+7 (495) 104-35-70</a></span></li>\n'
        '          </ol>\n'
        '          <a href="#oprosnyy-online" class="btn btn-w btn-lg" data-ol-open><span class="btn-t">Заполнить опросный лист онлайн</span></a>\n'
        '        </div>\n'
        '        <div class="rp-ol-pdfs">\n'
        + pdf_card('ppk', info) + '\n' + pdf_card('haccp', info) + '\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="rp-ol-box" id="oprosnyy-online" hidden></div>\n'
        f'    <template id="olTpl">{form_html()}</template>\n'
        '  </div>\n</section>\n')


# ---------------------------------------------------------------- онлайн-форма
def qid(no):
    return 'ol-' + no.replace('.', '-')


def chips(name, opts, kind, extra_attrs=None):
    t = 'radio' if kind in ('radio', 'type', 'prog') else 'checkbox'
    out = []
    for o in opts:
        label, value = (o if isinstance(o, tuple) else (o, o))
        ex = f' data-type="{attr(extra_attrs[label])}"' if extra_attrs else ''
        out.append(f'<label class="rp-chip"><input type="{t}" name="{name}" value="{attr(label)}"{ex}><span><span class="rp-ct">{esc(label)}</span></span></label>')
    return '<div class="rp-chips">' + ''.join(out) + '</div>'


def question(no, label, kind, p):
    i = qid(no)
    num = f'<i>{no}</i>'
    lab = attr(label)
    if kind in ('text', 'area'):
        ph = p.get('ph') or p.get('hint') or ''
        mx = p.get('max', 300)
        wide = ' rp-olf-w' if kind == 'area' or not p.get('short') and len(label) > 34 else ''
        if kind == 'text':
            extra = ' inputmode="numeric"' if no == '1.2' else (' autocomplete="organization"' if p.get('key') == 'company' else '')
            ctl = f'<input id="{i}" name="q{no}" maxlength="{mx}" placeholder="{attr(ph)}"{extra}>'
        else:
            ctl = f'<textarea id="{i}" name="q{no}" maxlength="{mx}" placeholder="{attr(ph)}"></textarea>'
        return f'<div class="field rp-olf-q{wide}" data-q="{no}" data-label="{lab}"><label for="{i}">{num}{esc(label)}</label>{ctl}</div>'
    if kind == 'type':
        types = dict(OBJECT_TYPES)
        ctl = chips('otype', [t for t, _ in OBJECT_TYPES], 'type', types)
        return (f'<div class="rp-olf-q rp-olf-w" data-q="{no}" data-label="{lab}" data-req="type" role="radiogroup" aria-required="true" '
                f'aria-labelledby="{i}-l"><p class="rp-olf-l" id="{i}-l">{num}{esc(label)}<b class="rp-olf-req" aria-hidden="true">*</b></p>{ctl}'
                '<small class="ferr">Выберите вид объекта</small></div>')
    role = 'radiogroup' if kind == 'radio' else 'group'
    ctl = chips(f'q{no}', p['opts'], kind)
    hint = f'<small class="rp-olf-h">{esc(p["hint"])}</small>' if p.get('hint') else ''
    x = ''
    if p.get('extra'):
        x = (f'<div class="field rp-olf-x"><label class="sr-only" for="{i}-x">{esc(label)}: {esc(p["extra"])}</label>'
             f'<input id="{i}-x" name="q{no}x" maxlength="200" placeholder="{attr(p["extra"])}" data-x="{attr(p["extra"])}"></div>')
    return (f'<div class="rp-olf-q rp-olf-w" data-q="{no}" data-label="{lab}" role="{role}" aria-labelledby="{i}-l">'
            f'<p class="rp-olf-l" id="{i}-l">{num}{esc(label)}</p>{hint}{ctl}{x}</div>')


def form_html():
    secs = []
    for s in SECTIONS:
        h = ' data-haccp hidden' if s.get('haccp') else ''
        note = ('<p class="rp-olf-sn">Раздел для ППК по ХАССП: заполните, если на объекте изготавливают пищевую продукцию.</p>'
                if s.get('haccp') else '')
        qs = ''.join(question(no, label, kind, p) for no, label, kind, p in s['q'])
        secs.append(f'<fieldset class="rp-olf-sec" data-sec="{s["n"]}" data-title="{attr(s["title"])}"{h}>'
                    f'<legend><span class="rp-pt">{s["n"]}</span><span>{esc(s["title"])}</span></legend>{note}<div class="rp-olf-g">{qs}</div></fieldset>')
    _, label, kind, p = COMMENT
    secs.append('<fieldset class="rp-olf-sec" data-sec="+" data-title="Дополнительно"><legend><span class="rp-pt">+</span><span>Дополнительно</span></legend>'
                '<div class="rp-olf-g"><div class="field rp-olf-q rp-olf-w" data-q="+" data-label="' + attr(label) + '">'
                f'<label for="ol-extra">{esc(label)}</label><textarea id="ol-extra" name="qextra" maxlength="{p["max"]}" '
                'placeholder="особенности объекта, сроки, вопросы к нам"></textarea></div></div></fieldset>')
    prog = ('<fieldset class="rp-olf-sec rp-olf-prog"><legend><span>Какая программа нужна<b class="rp-olf-req" aria-hidden="true">*</b></span></legend>'
            '<div class="rp-olf-q" data-req="prog" role="radiogroup" aria-required="true" aria-label="Какая программа нужна">'
            + chips('prog', ['ППК', 'ППК по ХАССП', 'Не знаю, какая нужна'], 'prog') +
            '<small class="ferr">Выберите программу</small></div>'
            '<p class="rp-olf-sn">Для ППК по ХАССП добавятся разделы 5 и 6 — о продукции и технологических процессах.</p></fieldset>')
    contacts = ('<fieldset class="rp-olf-sec rp-olf-c"><legend><span>Контакты для связи</span></legend><div class="fg">'
                '<div class="field"><label for="ol-name">Ваше имя<b class="rp-olf-req" aria-hidden="true">*</b></label>'
                '<input id="ol-name" name="ol_c_name" maxlength="150" autocomplete="name" required aria-describedby="ol-name-e"><small class="ferr" id="ol-name-e">Укажите имя</small></div>'
                '<div class="field"><label for="ol-phone">Телефон<b class="rp-olf-req" aria-hidden="true">*</b></label>'
                '<input id="ol-phone" name="ol_c_phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" autocomplete="tel" required aria-describedby="ol-phone-e">'
                '<small class="ferr" id="ol-phone-e">Укажите телефон полностью</small></div>'
                '<div class="field full"><label for="ol-email">Электронная почта — пришлём расчёт</label>'
                '<input id="ol-email" name="ol_c_email" type="email" inputmode="email" maxlength="254" autocomplete="email" aria-describedby="ol-email-e">'
                '<small class="ferr" id="ol-email-e">Проверьте адрес почты</small></div>'
                '</div></fieldset>')
    return (
        '<form class="form rp-olf" id="olForm" novalidate aria-labelledby="olTitle"><div class="fbody">'
        '<div class="rp-olf-top"><h3 id="olTitle">Опросный лист заказчика для разработки ППК</h3>'
        '<p class="rp-olf-fs">Обязательны только программа, вид объекта, имя и телефон. Ответы сохраняются в этом браузере, пока вы не отправите лист.</p></div>'
        + prog + ''.join(secs) + contacts +
        '<div class="rp-olf-send"><button type="submit" class="btn btn-w btn-lg" id="olSubmit"><span class="btn-t">Отправить опросный лист</span>'
        '<svg class="btn-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
        '<i class="spin" aria-hidden="true"></i></button>'
        '<button type="button" class="rp-olf-reset" id="olReset">Очистить ответы</button></div>'
        '<p class="legal">Нажимая кнопку, вы даёте <a href="../soglasie/" target="_blank" rel="noopener">согласие на обработку персональных данных</a> '
        'и подтверждаете, что ознакомились с <a href="../privacy/" target="_blank" rel="noopener">политикой конфиденциальности</a>.</p>'
        f'<p class="rp-olf-mail">Документы из списка выше можно прислать на <a href="mailto:{MAIL}">{MAIL}</a>.</p>'
        '</div><div class="ok" role="status" aria-live="polite">'
        '<svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>'
        '<h3>Опросный лист отправлен</h3><p>Перезвоним в ближайшее рабочее время, назовём стоимость и срок. '
        f'Документы можно прислать на <a href="mailto:{MAIL}">{MAIL}</a>.</p></div></form>')


# ---------------------------------------------------------------- скрипт формы
FORM_JS = r"""<script>/* Опросный лист заказчика (tools/razrabotka-ppk/oprosnyy/block.py): форма из <template id="olTpl"> по кнопке
   «Заполнить онлайн» или по адресу #oprosnyy-online; черновик — localStorage (без имени, телефона и почты);
   отправка — send.php частями до 3000 знаков в msg; цели Метрики audit и ppk_oprosnyy_send, UIS — как в app.js */
(function(){
var box=document.getElementById('oprosnyy-online'),tpl=document.getElementById('olTpl');if(!box||!tpl)return;
var KEY='rppk-ol-v1',LIM=2800,f=null,saveT=0,sending=false,done={key:'',next:0};
var PROD=/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname);
var FAIL='Не удалось отправить опросный лист. Попробуйте ещё раз или позвоните нам: +7 (495) 104-35-70.';
function q(s,c){return (c||f).querySelector(s)}function qa(s,c){return Array.prototype.slice.call((c||f).querySelectorAll(s))}
function txt(s){return String(s||'').replace(/\s+/g,' ').trim()}
function refresh(ms){setTimeout(function(){try{if(window.ScrollTrigger)ScrollTrigger.refresh()}catch(_){}},ms||120)}
function prog(){var r=q('input[name=prog]:checked');return r?r.value:''}
function sync(){var p=prog(),show=p&&p!=='ППК';qa('[data-haccp]').forEach(function(s){s.hidden=!show});}
function save(){clearTimeout(saveT);saveT=setTimeout(function(){var d={};qa('input,textarea').forEach(function(el){
  if(!el.name||el.name.indexOf('ol_c_')===0)return;
  if(el.type==='radio'||el.type==='checkbox'){if(el.checked)(d[el.name]=d[el.name]||[]).push(el.value)}else if(el.value)d[el.name]=el.value;});
  try{localStorage.setItem(KEY,JSON.stringify(d))}catch(_){}},300)}
function restore(){var d=null;try{d=JSON.parse(localStorage.getItem(KEY)||'null')}catch(_){}if(!d)return;
  qa('input,textarea').forEach(function(el){var v=d[el.name];if(v==null)return;
    if(el.type==='radio'||el.type==='checkbox')el.checked=v.indexOf(el.value)>-1;else el.value=v;});}
function mask(ph){var d=ph.value.replace(/\D/g,'');if(d[0]==='8')d='7'+d.slice(1);if(d[0]!=='7')d='7'+d;d=d.slice(0,11);
  var p=d.slice(1),s='+7';if(p.length)s+=' ('+p.slice(0,3);if(p.length>=3)s+=')';if(p.length>3)s+=' '+p.slice(3,6);
  if(p.length>6)s+='-'+p.slice(6,8);if(p.length>8)s+='-'+p.slice(8,10);ph.value=s;}
function init(){
  if(!PROD){var fs=q('.rp-olf-fs');if(fs)fs.textContent='Предпросмотр: опросный лист никуда не отправляется';}
  restore();sync();
  f.addEventListener('change',function(e){if(e.target.name==='prog'){sync();refresh();}var g=e.target.closest('.err');if(g)g.classList.remove('err');save();});
  f.addEventListener('input',function(e){var g=e.target.closest('.err');if(g){g.classList.remove('err');e.target.removeAttribute('aria-invalid');}save();});
  var ph=q('#ol-phone');ph.addEventListener('focus',function(){if(!ph.value)ph.value='+7 ('});
  ph.addEventListener('blur',function(){if(ph.value.replace(/\D/g,'').length<=1)ph.value=''});ph.addEventListener('input',function(){mask(ph)});
  q('#olReset').addEventListener('click',function(){if(!confirm('Очистить все ответы опросного листа?'))return;
    qa('input,textarea').forEach(function(el){if(el.type==='radio'||el.type==='checkbox')el.checked=false;else el.value=''});
    try{localStorage.removeItem(KEY)}catch(_){}sync();refresh();});
  f.addEventListener('submit',submit);
}
function open(p,ms){
  if(!f){box.appendChild(tpl.content.cloneNode(true));f=box.querySelector('form');init();}
  if(p){var r=q('input[name=prog][value="'+p+'"]');if(r){r.checked=true;sync();save();}}
  box.hidden=false;refresh(ms);
}
/* открываем раньше, чем app.js плавно прокрутит к #oprosnyy-online (обработчик на этапе перехвата);
   пересчёт ScrollTrigger — после прокрутки, чтобы не прервать её */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-ol-open]');if(a)open(a.getAttribute('data-ol-open'),1700);},true);
if(location.hash==='#oprosnyy-online'){open();setTimeout(function(){box.scrollIntoView()},60);}
function answer(b){
  var vals=qa('input:checked',b).map(function(el){return el.value});
  if(vals.length){var x=q('[data-x]',b),xv=x?txt(x.value):'';return vals.join(', ')+(xv?'; '+x.getAttribute('data-x')+': '+xv:'');}
  var t=q('input:not([type=radio]):not([type=checkbox]),textarea',b);
  if(t&&!t.hasAttribute('data-x'))return txt(t.value);
  var x2=q('[data-x]',b);return x2&&txt(x2.value)?x2.getAttribute('data-x')+': '+txt(x2.value):'';}
function compose(){
  var units=[],empty=[];
  qa('.rp-olf-sec[data-sec]').forEach(function(s){if(s.hidden||s.classList.contains('rp-olf-prog')||s.classList.contains('rp-olf-c'))return;
    var head=(s.getAttribute('data-sec')==='+'?'':s.getAttribute('data-sec')+'. ')+s.getAttribute('data-title'),first=true;
    qa('.rp-olf-q[data-q]',s).forEach(function(b){var n=b.getAttribute('data-q'),v=answer(b);
      if(!v){if(n!=='+')empty.push(n);return;}
      var line=(n==='+'?'':n+' ')+b.getAttribute('data-label')+': '+v;
      units.push(first?'— '+head+'\n'+line:line);first=false;});});
  if(empty.length)units.push('Без ответа: '+empty.join(', '));
  var top='Опросный лист заказчика: '+prog(),foot='Страница: Разработка ППК (/razrabotka-ppk/), опросный лист',parts=[],cur='';
  units.forEach(function(u){if(cur&&(cur.length+u.length+1)>LIM-top.length-foot.length-40){parts.push(cur);cur='';}cur+=(cur?'\n':'')+u;});
  if(cur||!parts.length)parts.push(cur);
  return parts.map(function(b,i){return top+(parts.length>1?' (часть '+(i+1)+' из '+parts.length+')':'')+'\n'+b+'\n'+foot;});}
function bad(el,box2){var g=box2||el.closest('.field');g.classList.remove('err');void g.offsetWidth;g.classList.add('err');if(el)el.setAttribute('aria-invalid','true');return g;}
function submit(e){
  e.preventDefault();if(sending)return;
  var first=null,nm=q('#ol-name'),ph=q('#ol-phone'),em=q('#ol-email'),pg=q('[data-req=prog]'),tp=q('[data-req=type]'),ot=q('input[name=otype]:checked');
  function chk(cond,el,g){if(cond){var b=bad(el,g);first=first||b;}}
  chk(!prog(),null,pg);chk(!ot,null,tp);chk(txt(nm.value).length<2,nm);chk(ph.value.replace(/\D/g,'').length!==11,ph);
  chk(txt(em.value)&&!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(txt(em.value)),em);
  if(first){var fi=q('input',first);first.scrollIntoView({block:'center'});if(fi)fi.focus({preventScroll:true});return;}
  var parts=compose(),key=parts.join('\u0001');if(key!==done.key)done={key:key,next:0};
  var co=q('#ol-1-1'),btn=q('#olSubmit');sending=true;btn.disabled=true;btn.classList.add('is-loading');
  function fd(m){var d=new FormData();d.append('name',txt(nm.value));d.append('phone',txt(ph.value));d.append('email',txt(em.value));
    d.append('company',txt(co?co.value:'').slice(0,250));d.append('type',ot.getAttribute('data-type'));d.append('msg',m);
    d.append('page','Разработка ППК — опросный лист');return d;}
  function step(){
    if(done.next>=parts.length)return ok();
    window.fetch('/send.php',{method:'POST',body:fd(parts[done.next]),headers:{'Accept':'application/json'},credentials:'same-origin'})
      .then(function(res){return res.text().then(function(t){var j=null;try{j=JSON.parse(t)}catch(_){}
        if(!res.ok||!j||!j.success){var er=new Error('send failed: '+res.status);er.userMessage=j&&j.message?j.message:'';throw er;}})})
      .then(function(){done.next++;step();})
      .catch(function(err){console.error('Опросный лист:',err);sending=false;btn.disabled=false;btn.classList.remove('is-loading');
        var m=err&&err.userMessage?err.userMessage:FAIL;if(done.next>0)m+=' Часть ответов уже у нас — при повторной отправке уйдут остальные.';alert(m);});}
  function ok(){
    try{if(typeof ym==='function'){ym(113675622,'reachGoal','audit');ym(113675622,'reachGoal','ppk_oprosnyy_send');}}catch(err){console.error('Яндекс Метрика:',err)}
    try{if(typeof Comagic!=='undefined'&&typeof Comagic.addOfflineRequest==='function')Comagic.addOfflineRequest({name:txt(nm.value),phone:txt(ph.value)});}catch(err){console.error('UIS:',err)}
    try{localStorage.removeItem(KEY)}catch(_){}
    f.classList.add('sent');window.scrollTo(0,box.getBoundingClientRect().top+window.pageYOffset-90);refresh();}
  step();
}
})();</script>
"""
