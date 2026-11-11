import json, glob, os, sys
from PIL import Image
from ultralytics import YOLO
R = '/home/user/workspace/site06122026v1/img/'
G = '/home/user/workspace/qa/gen/'
m = YOLO('yolov8m-pose.pt')
MAP = {  # семейство: мастер
 'bctc-prohodka': 'h_bctc-prohodka.png', 'dez-format-ochag': 'dez-format-ochag.png', 'dez-ipm-kontrol': 'dez-ipm-kontrol.png',
 'farma-herbs': 'farma-herbs.png', 'step3': 'h_step3.png', 'step2': 'step2-fixed.png', 'lab-smyvy-hero': 'lab-smyvy-hero.png',
 'mat-smyvy-hero': 'mat-smyvy-hero.png', 'programma-hero': 'programma-hero.png', 'lab-vrz-hero': 'lab-vrz-hero.png',
 'programma-plan-skhema': 'z_programma-plan-skhema.png', 'seti-format-darkstor': 'seti-format-darkstor.png',
 'sklad-feromon': 'h_sklad-feromon.png', 'sklad-produkty': 'sklad-produkty.png', 'step1': 'h_step1.png', 'step4': 'h_step4.png',
 'vent-brush': 'vent-brush.png', 'vent-video': 'vent-video.png', 'ind-hotel-room': 'h_ind-hotel-room.png', 'seti-hero-mob': 'seti-hero-mob.png', 'sklad-vorota': 'h_sklad-vorota.png', 'bctc-bc': 'z_bctc-bc.png', 'sklad-pm': 'z_sklad-pm.png', 'vent-disinfection': 'z_vent-disinfection.png'}
only = sys.argv[1:] or list(MAP)
SUF = ['', '-480', '-720', '-760', '-1440', '-mob', '-mob-760', '-sq']
import sys as _s
def people(im):
    r = m(im, verbose=False, conf=0.4)[0]; W, H = im.size; out = []
    for i in range(len(r.boxes)):
        if float(r.boxes.conf[i]) < 0.5: continue
        x0, y0, x1, y1 = r.boxes.xyxy[i].tolist(); out.append((x0 / W, y0 / H, x1 / W, y1 / H))
    return out
def crop_for(im, ppl, ar):
    W, H = im.size
    if abs(W / H - ar) < 0.01: return im
    if W / H > ar:  # режем по ширине
        cw = H * ar
        if ppl:
            x0 = min(p[0] for p in ppl) * W; x1 = max(p[2] for p in ppl) * W; c = (x0 + x1) / 2
        else: c = W / 2
        L = min(max(0, c - cw / 2), W - cw); return im.crop((round(L), 0, round(L + cw), H))
    ch = W / ar
    if ppl:
        y0 = min(p[1] for p in ppl) * H; T = max(0, y0 - 0.2 * ch)  # голова с запасом сверху
        y1 = max(p[3] for p in ppl) * H
        if y1 - T < ch: T = max(0, min(T, (y0 + y1) / 2 - ch / 2))
    else: T = (H - ch) / 2
    T = min(T, H - ch); return im.crop((0, round(T), W, round(T + ch)))
for fam in only:
    src = Image.open(G + MAP[fam]).convert('RGB'); ppl = people(src)
    print(fam, 'master', src.size, 'people', [[round(v, 2) for v in p] for p in ppl])
    for suf in SUF:
        f = R + fam + suf + '.webp'
        if not os.path.exists(f): continue
        if fam == 'seti-hero-mob' and suf not in ('', '-760'): continue
        old = Image.open(f); w, h = old.size; ob = os.path.getsize(f)
        if suf in ('-mob', '-mob-760') and fam.endswith('-hero'):
            base = src
        else: base = src
        c = crop_for(base, ppl, w / h).resize((w, h), Image.LANCZOS)
        import io, subprocess
        ob = len(subprocess.run(['git','-C','/home/user/workspace/site06122026v1','show','HEAD:img/'+fam+suf+'.webp'],capture_output=True).stdout) or (70000 if w > 900 else 34000)
        best = None
        for q in range(84, 55, -3):
            b = io.BytesIO(); c.save(b, 'WEBP', quality=q, method=6)
            best = (q, b.getvalue())
            if len(best[1]) <= ob * 1.08: break
        open(f, 'wb').write(best[1]); print('     q', best[0])
        print('  ', os.path.basename(f), (w, h), ob, '->', os.path.getsize(f))
