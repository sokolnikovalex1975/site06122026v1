import json
P = json.load(open('people.json'))
out, srccut = {}, []
for src, ppl in P.items():
    ppl = [p for p in ppl if p['conf'] >= 0.5]
    if not ppl: continue
    area = lambda p: (p['box'][2]-p['box'][0])*(p['box'][3]-p['box'][1])
    mx = max(area(p) for p in ppl)
    main = [p for p in ppl if area(p) >= 0.25*mx and area(p) >= 0.01]
    if not main: continue
    S = [min(p['box'][0] for p in main), min(p['box'][1] for p in main), max(p['box'][2] for p in main), max(p['box'][3] for p in main)]
    H = None
    for p in main:
        hk = [k for k in p['kp'][:5] if k[2] > 0.5]
        if not hk: continue
        xs = [k[0] for k in hk]; ys = [k[1] for k in hk]
        x0, y0, x1, y1 = p['box']
        hs = max(max(xs)-min(xs), (x1-x0)*0.22, (y1-y0)*0.07)
        hb = [min(xs)-hs*.45, min(y0, min(ys)-hs*1.0), max(xs)+hs*.45, max(ys)+hs*.7]
        H = hb if H is None else [min(H[0],hb[0]), min(H[1],hb[1]), max(H[2],hb[2]), max(H[3],hb[3])]
        if hb[1] <= 0.005: srccut.append(src)
    if H is None: H = [S[0], S[1], S[2], S[1] + (S[3]-S[1])*0.2]
    r = lambda v: round(min(1, max(0, v)), 3)
    out[src.split('/')[-1]] = {'s': [r(v) for v in S], 'h': [r(v) for v in H]}
json.dump(out, open('focal_points.json', 'w'), indent=0, sort_keys=True)
print(len(out), 'images; head at source top edge:', sorted(set(s.split('/')[-1] for s in srccut)))
