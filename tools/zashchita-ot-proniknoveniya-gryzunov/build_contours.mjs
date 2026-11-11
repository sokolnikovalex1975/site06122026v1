import {mkdirSync,writeFileSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as k from './vendor/iso-kit.mjs';
import * as A from './vendor/audit.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const W = 760, H = 470;
const site = {x:-146,y:-108,w:292,d:216,r:5};
const P = k.fitProjection(
  [...k.boxCorners(site,-12,-8),...k.boxCorners({x:-95,y:-58,w:190,d:116,r:0},-8,78)],
  W,H,{pad:28,azimuth:49,elevation:32}
);
const R = A.recorder(P);
let count = 0;

function slab(name,x,y,w,d,z,h,{tone='mid',level=0,r=0,inner='',ground=false}={}) {
  const plan = {x,y,w,d,r};
  const paths = k.slabOf(plan,z,h,P,4,0);
  const svg = k.solidSvg(paths,{tone,crease:'faint',inner});
  const painted = `<g data-part="${name}"${level?` class="proof-node proof-node-${level}"`:''}>${svg}</g>`;
  R.put({name,piece:'building',at:[x+w/2,y+d/2,z+h/2],svg:painted,
    shapes:[R.solid(A.slab(plan,z,h,{name,ground},4))]});
  count++;
}
const contour = (level,plan,z,dashed=false) =>
  `<g class="proof-level proof-level-${level}">${k.lineSvg(k.planOutline(plan,z,P,6),
    {tone:'hi',dashed,className:`proof-outline proof-outline-${level}`})}</g>`;

// Ground and foundation. All three outlines sit on real horizontal faces.
slab('stand.site',site.x,site.y,site.w,site.d,-12,4,{tone:'lo',r:5,ground:true,
  inner:contour(1,{x:-135,y:-97,w:270,d:194,r:12},-8)});
slab('foundation',-100,-63,200,126,-8,7,{tone:'lo'});
slab('floor',-95,-58,190,116,-1,1,{tone:'mid',
  inner:contour(2,{x:-94,y:-57,w:188,d:114,r:2},0)+
    contour(3,{x:-83,y:-46,w:164,d:90,r:3},0,true)});
slab('approach.left',-127,-78,18,156,-8,1.2,{tone:'lo'});
slab('approach.back',-109,-86,228,18,-8,1.2,{tone:'lo'});
slab('approach.front',-109,69,228,18,-8,1.2,{tone:'lo'});
slab('approach.right',109,-68,18,136,-8,1.2,{tone:'lo'});

// Rear and left walls.
slab('wall.back',-95,-58,190,4,0,72);
slab('wall.left',-95,-54,4,108,0,72);
// Front wall is cut away in the centre. Door and service inlet are real openings.
slab('wall.front.left-jamb',-95,54,6,4,0,72);
slab('wall.front.door-right',-69,54,9,4,0,72);
slab('wall.front.door-lintel',-89,54,20,4,48,24);
slab('wall.front.right-a',50,54,10,4,0,72);
slab('wall.front.right-b',82,54,13,4,0,72);
slab('wall.front.inlet-bottom',60,54,22,4,0,8);
slab('wall.front.inlet-top',60,54,22,4,19,53);
// Right facade with loading gate.
slab('wall.right.back',91,-54,4,12,0,72);
slab('wall.right.vent-bottom',91,-42,4,24,0,39);
slab('wall.right.vent-top',91,-42,4,24,59,13);
slab('wall.right.middle',91,-18,4,11,0,72);
slab('wall.right.front',91,43,4,11,0,72);
slab('wall.right.lintel',91,-7,4,50,60,12);

// Roof strip and cap: the rest is intentionally removed to show the inside.
slab('roof',-95,-58,190,24,72,3,{tone:'hi'});
slab('roof.parapet',-95,-58,190,3,75,3,{tone:'mid'});
for (let x=-65;x<=65;x+=26)
  slab(`roof.seam.${x}`,x,-55,.6,21,75,.3,{tone:'lo'});

// Personnel door and its metal threshold.
slab('door.leaf',-88.5,54.4,19,3.2,1,46,{tone:'hi'});
slab('door.frame.left',-89.5,58,1.6,1.1,1,48,{tone:'hi',level:2});
slab('door.frame.right',-70,58,1.6,1.1,1,48,{tone:'hi',level:2});
slab('door.frame.top',-87.9,58,17.9,1.1,47.4,1.6,{tone:'hi',level:2});
slab('door.threshold',-89,54,20,6,0,1,{tone:'hi',level:2});
slab('door.plate',-88.5,57.6,19,.4,1,7,{tone:'hi',level:2});
slab('door.handle',-74,57.6,3,1.4,26,1.2,{tone:'hi'});

// Gate guides and ten actual shutter sections.
slab('gate.rail.back',95,-7,1.3,2,0,60,{tone:'hi',level:2});
slab('gate.rail.front',95,41,1.3,2,0,60,{tone:'hi',level:2});
slab('gate.top',95,-5,1.3,46,58,2,{tone:'hi',level:2});
for(let i=0;i<10;i++)
  slab(`gate.slat.${i}`,93.4,-5,1.6,46,2+i*5.6,5.4,{tone:'hi'});
slab('gate.seal',95,-5,1.3,46,0,2,{tone:'hi',level:2});
slab('gate.apron',100,-7,9,50,-8,8,{tone:'lo'});

// Vent grille: louvers sit between the frame, not on top of a blank wall.
slab('vent.frame.back',95,-42,1.2,1.4,39,20,{tone:'hi',level:2});
slab('vent.frame.front',95,-19.4,1.2,1.4,39,20,{tone:'hi',level:2});
slab('vent.frame.bottom',95,-40.6,1.2,21.2,39,1.2,{tone:'hi',level:2});
slab('vent.frame.top',95,-40.6,1.2,21.2,57.8,1.2,{tone:'hi',level:2});
for(let i=0;i<6;i++)
  slab(`vent.louver.${i}`,95,-40.6,1.2,21.2,41+i*2.7,1.1,{tone:'mid'});

// Cable/utility inlet, with a protective surround and a closed service channel.
slab('inlet.collar.left',60,58,5,1.2,8,11,{tone:'hi',level:2});
slab('inlet.collar.right',77,58,5,1.2,8,11,{tone:'hi',level:2});
slab('inlet.collar.bottom',65,58,12,1.2,8,2,{tone:'hi',level:2});
slab('inlet.collar.top',65,58,12,1.2,16,3,{tone:'hi',level:2});
slab('inlet.channel',65,47,12,28,10,6,{tone:'mid'});
slab('inlet.cap',64,75,14,2,9,8,{tone:'hi'});
slab('inlet.support',65,72,12,3,-6.8,16.8,{tone:'lo'});

// Interior partitions, a closed service cabinet and a protected inter-room door.
slab('inside.partition.long',-20,-54,3,75,0,40,{tone:'mid'});
slab('inside.partition.left',-17,18,25,3,0,40,{tone:'mid'});
slab('inside.partition.right',27,18,29,3,0,40,{tone:'mid'});
slab('inside.partition.lintel',8,18,19,3,30,10,{tone:'mid'});
slab('inside.door.left',8,21,1,1,0,30,{tone:'hi',level:3});
slab('inside.door.right',26,21,1,1,0,30,{tone:'hi',level:3});
slab('inside.door.threshold',8,18,19,4,0,.7,{tone:'hi',level:3});
slab('cabinet.plinth',-77,-47,27,14,0,2,{tone:'lo'});
slab('cabinet.body',-76,-46,25,12,2,29,{tone:'mid'});
slab('cabinet.door.left',-76,-34,12.2,.7,3,27,{tone:'hi'});
slab('cabinet.door.right',-63.3,-34,12.3,.7,3,27,{tone:'hi'});
slab('cabinet.cap',-76,-46,25,12,31,1,{tone:'hi'});

A.settle(R,P);
R.items.sort((a,b)=>a.key-b.key);
A.auditOrExit(R,P);
if(process.exitCode) process.exit(process.exitCode);

const localCSS = `
.proof-drawing{--anatomy-paper:#151518;--anatomy-face:#222227;--anatomy-top:#29292f;--anatomy-shade-0:#111114;--anatomy-shade-1:#19191e;--anatomy-shade-2:#202026;--anatomy-shade-3:#25252c;--anatomy-hi:#a8a8b5;--anatomy-mid:#656572;--anatomy-lo:#454550;--anatomy-faint:#373741;--anatomy-weight:.75px}
.proof-outline{stroke-width:2.2!important}
.proof-level-1 .proof-outline{stroke:#7cbdb7;stroke-dasharray:5 4}
.proof-level-2 .proof-outline{stroke:#8f9bff}
.proof-level-3 .proof-outline{stroke:#dabd89;stroke-dasharray:2 3}
.proof-node-2 .iso-edge{stroke:#8f9bff;stroke-width:1.1}
.proof-node-3 .iso-edge{stroke:#dabd89;stroke-width:1.1}
.proof-level,.proof-node .iso-edge{transition:opacity .25s ease,filter .25s ease,stroke-width .25s ease}
.proof-outline{transition:stroke-width .25s ease}
.proof-drawing[data-contour="1"] .proof-level-1 .proof-outline,.proof-drawing[data-contour="2"] .proof-level-2 .proof-outline,.proof-drawing[data-contour="3"] .proof-level-3 .proof-outline{stroke-width:3.4!important}
.proof-drawing[data-contour="1"] .proof-level-1{filter:drop-shadow(0 0 3px rgba(124,189,183,.75))}
.proof-drawing[data-contour="2"] .proof-level-2,.proof-drawing[data-contour="2"] .proof-node-2{filter:drop-shadow(0 0 3px rgba(143,155,255,.8))}
.proof-drawing[data-contour="3"] .proof-level-3,.proof-drawing[data-contour="3"] .proof-node-3{filter:drop-shadow(0 0 3px rgba(218,189,137,.75))}
.proof-drawing[data-contour="2"] .proof-node-2 .iso-edge,.proof-drawing[data-contour="3"] .proof-node-3 .iso-edge{stroke-width:1.7}
.proof-drawing[data-contour="1"] .proof-level-1 .proof-outline{animation:proof-march-1 1.1s linear infinite}
.proof-drawing[data-contour="3"] .proof-level-3 .proof-outline{animation:proof-march-3 .9s linear infinite}
.proof-drawing[data-contour="2"] .proof-level-2,.proof-drawing[data-contour="2"] .proof-node-2{animation:proof-pulse .7s ease-in-out 2 alternate}
@keyframes proof-march-1{to{stroke-dashoffset:-18}}
@keyframes proof-march-3{to{stroke-dashoffset:-10}}
@keyframes proof-pulse{to{filter:drop-shadow(0 0 7px rgba(143,155,255,.95))}}
.proof-drawing[data-contour="1"] .proof-level:not(.proof-level-1),.proof-drawing[data-contour="1"] .proof-node .iso-edge,.proof-drawing[data-contour="2"] .proof-level:not(.proof-level-2),.proof-drawing[data-contour="2"] .proof-node-3 .iso-edge,.proof-drawing[data-contour="3"] .proof-level:not(.proof-level-3),.proof-drawing[data-contour="3"] .proof-node-2 .iso-edge{opacity:.18}
@media(prefers-reduced-motion:reduce){.proof-level,.proof-node,.proof-node .iso-edge,.proof-outline{transition:none!important;animation:none!important}}
`;
const body = R.items.map(i=>i.svg).join('');
for(const theme of ['dark','light']) {
  let svg = k.figureSvg({width:W,height:H,standalone:theme,
    className:'proof-drawing',label:'Условный разрез здания: территория, оболочка здания и внутренние помещения',body});
  svg = svg.replace('</style>',`</style><style>${localCSS}</style>`);
  // The existing site is dark; the light build is retained only for geometry/line inspection.
  if(theme==='light') svg=svg.replace('.proof-drawing{--anatomy-paper:', '.proof-drawing[data-theme="dark"]{--anatomy-paper:');
  writeFileSync(join(HERE,`contours${theme==='light'?'-light':''}.svg`),svg);
  const inspectionAt = process.argv.indexOf('--inspection-dir');
  if(inspectionAt>=0 && process.argv[inspectionAt+1]) {
    const dir=process.argv[inspectionAt+1];
    mkdirSync(dir,{recursive:true});
    writeFileSync(join(dir,`contours-${theme}.html`),k.pageHtml({
      title:'Проверка геометрии схемы контуров',theme,body:k.plateHtml({
        fig:'Схема 01',title:'Три контура защиты',hint:'Условный разрез',body:svg
      })
    }));
  }
}
writeFileSync(join(HERE,'contours-parts.json'),JSON.stringify({solids:count,projection:P,
  parts:R.items.map(({name,key})=>({name,key}))},null,2));
console.log(`contours: ${count} solids; ${W}×${H}; ready SVG, no browser geometry runtime`);
