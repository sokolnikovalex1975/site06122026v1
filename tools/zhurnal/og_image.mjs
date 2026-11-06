import fs0 from 'fs';
import { chromium } from 'playwright';
// node og_image.mjs <dir с превью zhurnal-*-720.webp>  ->  <dir>/zhurnal-og.jpg (1200×630)
const out=process.argv[2]; const FONT=new URL('../../fonts/inter-ru-wght-normal.woff2', import.meta.url).href;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1200,height:630} });
const html=(`<html><head><style>
@font-face{font-family:Inter;font-weight:100 900;src:url(${FONT})}
body{margin:0;width:1200px;height:630px;overflow:hidden;background:radial-gradient(700px 420px at 80% 30%,rgba(124,134,255,.28),rgba(0,0,0,0) 70%),#000;font-family:Inter;color:#fff;position:relative}
.l{position:absolute;left:72px;top:70px;width:600px}
.brand{display:flex;align-items:center;gap:14px;font-weight:600;font-size:26px;letter-spacing:-.02em}
.brand small{font-size:14px;color:#7c86ff;letter-spacing:.12em;font-weight:500;margin-left:6px}
h1{font-weight:300;font-size:68px;line-height:1.02;letter-spacing:-.05em;margin:70px 0 0}
h1 em{font-style:normal;color:#7c86ff}
p{font-size:22px;color:#9f9fa9;margin:26px 0 0;line-height:1.4}
.tags{display:flex;gap:10px;margin-top:34px}.tags span{border:1px solid rgba(255,255,255,.18);border-radius:99px;padding:9px 16px;font-size:17px;color:#e4e4e7}
.tags span.y{background:#fdc700;color:#09090b;border-color:#fdc700;font-weight:600}
.d1,.d2{position:absolute;width:330px;border-radius:8px;box-shadow:0 30px 70px rgba(0,0,0,.6)}
.d2{right:70px;top:120px;transform:rotate(6deg);opacity:.9}
.d1{right:190px;top:70px;transform:rotate(-4deg)}
</style></head><body>
<div class="l"><div class="brand"><svg width="52" height="52" viewBox="0 0 48 48"><circle cx="24" cy="24" r="23" fill="#09090b" stroke="rgba(255,255,255,.25)"/><g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round"><path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/><circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/><path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>
<h1>Журнал<br>пест-контроля: <em>образец и шаблон</em></h1>
<p>Образец и шаблон совпадают лист в лист · СанПиН 3.3686-21 и ХАССП</p>
<div class="tags"><span class="y">Образец PDF</span><span>Шаблон PDF</span><span>10 листов</span></div></div>
<img class="d2" src="file://${out}/zhurnal-shablon-p1-720.webp"><img class="d1" src="file://${out}/zhurnal-obrazets-p1-720.webp">
</body></html>`);
fs0.writeFileSync(out+'/og.html', html); await p.goto('file://'+out+'/og.html');
await p.waitForTimeout(400);
await p.screenshot({ path: out + '/zhurnal-og.jpg', type: 'jpeg', quality: 84 });
await b.close();
