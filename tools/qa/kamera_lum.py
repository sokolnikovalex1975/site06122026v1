#!/usr/bin/env python3
"""Яркость центра кадра при возврате «После дезинфекции» → «До работ» по снимкам tools/qa/kamera_test.mjs (OUT).

    python3 tools/qa/kamera_lum.py /tmp/kamera-shots

На телефоне (до 760 px) провала быть не должно — закон владельца «на телефоне ничего не затемнять» (README.md).
"""
import sys,glob,os
from PIL import Image, ImageStat
d=sys.argv[1]
for w in ['1440','1180','768','390','360','320']:
    def L(n):
        f=os.path.join(d,f'{w}-art-{n}.png')
        if not os.path.exists(f): return None
        im=Image.open(f).convert('L'); W,H=im.size
        im=im.crop((int(W*.2),int(H*.2),int(W*.8),int(H*.8)))  # центр кадра, без углов и кнопки
        return round(ImageStat.Stat(im).mean[0],1)
    vals={n:L(n) for n in ['dez','back-1','back-2','back-3','do']}
    lo=min(v for v in [vals['dez'],vals['do']] if v is not None) if vals['dez'] and vals['do'] else None
    mn=min(v for k,v in vals.items() if k.startswith('back') and v is not None) if any(vals[k] for k in vals if k.startswith('back')) else None
    print(w, vals, 'провал' if (lo and mn is not None and mn < 0.6*lo) else 'без провала')
