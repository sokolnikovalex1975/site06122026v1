import json, urllib.parse, pathlib
from ultralytics import YOLO
R = pathlib.Path('/home/user/workspace/site06122026v1')
d = json.load(open('collect.json'))
srcs = sorted({urllib.parse.unquote(x['src'].split('?')[0]) for x in d['imgs']})
m = YOLO('yolov8m-pose.pt')
res = {}
for s in srcs:
    f = R / s.lstrip('/')
    if not f.exists(): print('missing', s); continue
    r = m(str(f), verbose=False, conf=0.35)[0]
    W, H = r.orig_shape[1], r.orig_shape[0]
    people = []
    for i in range(len(r.boxes)):
        x0, y0, x1, y1 = r.boxes.xyxy[i].tolist(); kp = r.keypoints.data[i].tolist()
        people.append({'conf': round(float(r.boxes.conf[i]), 2), 'box': [x0 / W, y0 / H, x1 / W, y1 / H], 'kp': [[k[0] / W, k[1] / H, k[2]] for k in kp]})
    res[s] = people
json.dump(res, open('people.json', 'w'))
print(len(srcs), 'images,', sum(1 for v in res.values() if v), 'with people')
