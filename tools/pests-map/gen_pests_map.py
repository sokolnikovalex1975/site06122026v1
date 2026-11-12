"""Фон блока «Вредители» — бесшовная плитка изолиний «Карта очагов» (img/pests-map.svg), 12.11.2026.

    python3 tools/pests-map/gen_pests_map.py            # пишет img/pests-map.svg (1200×1200, ~62 КБ)

Поле — периодический шум (белый шум с фильтром в частотной области, спектральная интерполяция до шага 2 px)
и два гауссовых «очага». Поле на торе, поэтому плитка стыкуется без шва при background-repeat. Изолинии —
contourpy (matplotlib), упрощение Рамера — Дугласа — Пекера, сглаживание Катмулла — Рома в кубические кривые,
относительные координаты с точностью 0,1 px. Каждая пятая линия ярче (как горизонтали на карте).
Собрано: numpy 2.5.4, contourpy 1.4.0; seed 7, плитка 1200, 22 уровня, допуск 0,5 px.
"""
import pathlib

import numpy as np
import contourpy
import sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
out = sys.argv[2] if len(sys.argv) > 2 else str(pathlib.Path(__file__).resolve().parents[2] / "img" / "pests-map.svg")
L = int(sys.argv[3]) if len(sys.argv) > 3 else 1200   # размер плитки, CSS px
NLEV = int(sys.argv[4]) if len(sys.argv) > 4 else 22
d = 5                                                 # шаг сетки, px
N = L // d
M = 10                                                # запас за краем плитки, ячеек
rng = np.random.default_rng(seed)

# периодический шум: белый шум -> фильтр в частотной области
k = np.fft.fftfreq(N) * N            # циклов на плитку
KX, KY = np.meshgrid(k, k)
K = np.hypot(KX, KY)
filt = np.exp(-(K / 3.2) ** 2) / (1 + (K / 1.5) ** 2) ** 0.6
filt[0, 0] = 0
spec = np.fft.fft2(rng.normal(size=(N, N))) * filt
dh = 2
NH = L // dh
spec_h = np.zeros((NH, NH), dtype=complex)
h = N // 2
spec_h[:h, :h] = spec[:h, :h]; spec_h[:h, -h:] = spec[:h, -h:]
spec_h[-h:, :h] = spec[-h:, :h]; spec_h[-h:, -h:] = spec[-h:, -h:]
noise = np.real(np.fft.ifft2(spec_h))
noise /= np.abs(noise).max()
N = NH
d = dh
M = 12

u = (np.arange(N) / N)[None, :].repeat(N, 0)
v = (np.arange(N) / N)[:, None].repeat(N, 1)
F = 0.9 * noise
# «очаги» — гауссовы пики с периодическим переносом
for (px, py, s, amp) in [(0.74, 0.27, 0.085, 1.1), (0.24, 0.73, 0.07, 0.9)]:
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            F += amp * np.exp(-(((u - px - ox) ** 2 + (v - py - oy) ** 2) / (2 * s * s)))
F = (F - F.min()) / (F.max() - F.min())

# расширенная сетка с периодическим переносом
idx = np.arange(-M, N + M + 1)
FE = F.take(idx, axis=0, mode="wrap").take(idx, axis=1, mode="wrap")
x = (idx * d).astype(float)
X, Y = np.meshgrid(x, x)

levels = np.linspace(0.04, 0.98, NLEV)
gen = contourpy.contour_generator(X, Y, FE, line_type="Separate")


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    ab = b - a
    n = np.hypot(*ab)
    w = pts - a
    dists = np.hypot(w[:, 0], w[:, 1]) if n == 0 else np.abs(ab[0] * w[:, 1] - ab[1] * w[:, 0]) / n
    i = int(np.argmax(dists))
    if dists[i] > eps:
        left = rdp(pts[: i + 1], eps)
        right = rdp(pts[i:], eps)
        return np.vstack([left[:-1], right])
    return np.vstack([a, b])


EPS = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
def fmt(v):
    t = f"{v:.1f}"
    if t.endswith(".0"):
        t = t[:-2]
    if t.startswith("0."):
        t = t[1:]
    elif t.startswith("-0."):
        t = "-" + t[2:]
    if t == "-0":
        t = "0"
    return t


def join_nums(nums):
    out = ""
    prev = None
    for t in nums:
        if prev is not None:
            need = True
            if t.startswith("-"):
                need = False
            elif t.startswith(".") and "." in prev:
                need = False
            if need:
                out += " "
        out += t
        prev = t
    return out


def path_d(pts):
    pts = rdp(pts, EPS)
    if len(pts) < 2:
        return ""
    closed = np.allclose(pts[0], pts[-1])
    n = len(pts)
    # абсолютные координаты кривых, затем перевод в относительные с округлением накоплением
    segs = []
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else (pts[-2] if closed else pts[i])
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else (pts[1] if closed else pts[i + 1])
        segs.append((p1 + (p2 - p0) / 6, p2 - (p3 - p1) / 6, p2))
    cur = np.round(pts[0], 1)
    s = "M" + join_nums([fmt(cur[0]), fmt(cur[1])]) + "c"
    nums = []
    for c1, c2, p2 in segs:
        a = np.round(c1 - cur, 1); b = np.round(c2 - cur, 1); e = np.round(p2 - cur, 1)
        nums += [fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]), fmt(e[0]), fmt(e[1])]
        cur = cur + e
    return s + join_nums(nums)


minor, major = [], []
for li, lv in enumerate(levels):
    for ln in gen.lines(lv):
        if len(ln) < 4:
            continue
        if ln[:, 0].max() < -20 or ln[:, 0].min() > L + 20 or ln[:, 1].max() < -20 or ln[:, 1].min() > L + 20:
            continue
        (major if li % 5 == 2 else minor).append(path_d(ln))

svg = (
    f"<svg xmlns='http://www.w3.org/2000/svg' width='{L}' height='{L}' viewBox='0 0 {L} {L}'>"
    f"<g fill='none' stroke='#a5acff' stroke-linecap='round' stroke-linejoin='round'>"
    f"<path stroke-opacity='.13' stroke-width='1' d='{''.join(minor)}'/>"
    f"<path stroke-opacity='.24' stroke-width='1.2' d='{''.join(major)}'/>"
    f"</g></svg>"
)
open(out, "w").write(svg)
print(out, len(svg), "bytes", len(minor), "minor", len(major), "major")
