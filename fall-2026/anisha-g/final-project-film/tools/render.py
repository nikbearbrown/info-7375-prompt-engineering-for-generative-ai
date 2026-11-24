"""Renders the show-tell style clips (silent) for the job-search agent film (four-part version).
Usage: python3 render.py <beat_sheet.json> <fonts_dir> <out_dir> [BID ...]
Each clip runs until its last animation lands (+0.6 s); make_film.sh holds the last
frame for the rest of the narration.
"""
import json, math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample
W, H = 1920, 1080
FPS = 24
WPM = 180                   # macOS `say -r 180`
# palette: teal / coral (own design)
BG    = (248, 249, 248)
INK   = (23, 51, 58)
ACC   = (226, 114, 91)
DIM   = (110, 128, 130)
GHOST = (150, 172, 168)
CARD  = (247, 250, 249)
LIGHT = [(170, 202, 193), (118, 162, 151), (88, 134, 123)]   # top, left, right
DARK  = [(44, 82, 90), (26, 56, 63), (17, 40, 46)]
PAGE  = [(255, 255, 255), (221, 229, 227), (205, 216, 213)]
CORAL = [(232, 124, 100), (203, 86, 64), (166, 66, 49)]
MUSTARD = [(238, 188, 82), (212, 148, 36), (176, 118, 26)]
SKY = [(104, 152, 196), (62, 110, 160), (42, 84, 130)]
SKYC, MUSC = (52, 98, 150), (200, 138, 30)

def _bg():
    from PIL import ImageFilter
    im = Image.new('RGB', (W, H))
    top, bot = (250, 251, 250), (245, 246, 243)
    for y in range(H):
        u = y / (H - 1)
        ImageDraw.Draw(im).line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3)))
    cl = im.copy(); d = ImageDraw.Draw(cl)
    for (x, y, r, col) in [(1920, 0, 340, (250, 236, 230)), (0, 1080, 360, (234, 241, 249)),
                           (0, 0, 240, (238, 246, 242)), (1920, 1080, 280, (250, 243, 228))]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im = cl.filter(ImageFilter.GaussianBlur(120))
    return im.resize((W * SS, H * SS), Image.BILINEAR)
BG_IM = None

sheet, FONTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = sys.argv[4:]
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size * SS)
F_LAB  = lambda: font('EBGaramond-Medium.ttf', 40)
F_SUB  = lambda: font('EBGaramond-Italic.ttf', 32)
F_BIG  = lambda: font('EBGaramond-Regular.ttf', 72)
F_HEAD = lambda: font('EBGaramond-Regular.ttf', 34)
F_TINY = lambda: font('Inter_28pt-Medium.ttf', 15)
F_MONO = lambda: font('PTMono-Regular.ttf', 26)

def lerp(c, a): return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3

class Ctx:
    def __init__(self):
        global BG_IM
        if BG_IM is None: BG_IM = _bg()
        self.im = BG_IM.copy()
        self.d = ImageDraw.Draw(self.im)
    def poly(self, pts, fill, a, outline=INK, width=3):
        P = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(P, fill=lerp(fill, a) if fill else None)
        if outline: self.d.line(P + [P[0]], fill=lerp(outline, a), width=width * SS, joint='curve')
    def line(self, pts, col, a, width=3):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=lerp(col, a), width=width * SS, joint='curve')
    def text(self, x, y, s, f, col, a, anchor='mm'):
        self.d.text((x * SS, y * SS), s, font=f, fill=lerp(col, a), anchor=anchor)
    def save(self): return self.im.resize((W, H), Image.BOX)

# ---------- isometric primitives (unit u px; object anchored at its ground centre) ----------
C30 = math.cos(math.radians(30))
def P(cx, cy, u, x, y, z): return (cx + (x - y) * u * C30, cy + (x + y) * u * 0.5 - z * u)

def box(c, cx, cy, u, w, d, h, faces, a, z=0, top_extra=None, outline=INK):
    x0, y0 = -w / 2, -d / 2; x1, y1 = x0 + w, y0 + d
    p = lambda x, y, zz: P(cx, cy, u, x, y, zz)
    c.poly([p(x0, y1, z), p(x1, y1, z), p(x1, y1, z + h), p(x0, y1, z + h)], faces[1], a, outline)
    c.poly([p(x1, y0, z), p(x1, y1, z), p(x1, y1, z + h), p(x1, y0, z + h)], faces[2], a, outline)
    c.poly([p(x0, y0, z + h), p(x1, y0, z + h), p(x1, y1, z + h), p(x0, y1, z + h)], faces[0], a, outline)
    if top_extra: top_extra(p, x0, y0, x1, y1, z + h)

def ghost_box(c, cx, cy, u, w, d, h, a):
    x0, y0 = -w / 2, -d / 2; x1, y1 = x0 + w, y0 + d
    p = lambda x, y, zz: P(cx, cy, u, x, y, zz)
    for seg in [[p(x0, y1, 0), p(x1, y1, 0), p(x1, y0, 0)], [p(x0, y1, h), p(x1, y1, h), p(x1, y0, h), p(x0, y0, h), p(x0, y1, h)],
                [p(x0, y1, 0), p(x0, y1, h)], [p(x1, y1, 0), p(x1, y1, h)], [p(x1, y0, 0), p(x1, y0, h)]]:
        dashed(c, seg, GHOST, a)

def dashed(c, pts, col, a, dash=14, gap=10):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = int(L // (dash + gap)) + 1
        for i in range(n):
            s = i * (dash + gap) / L; e = min(1, (i * (dash + gap) + dash) / L)
            if s >= 1: break
            c.line([(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s), (x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)], col, a, 3)

def page_lines(n, col=(170, 186, 184)):
    def f(p, x0, y0, x1, y1, z):
        pass
    return f

def page(c, cx, cy, u, a, z=0, n=5, w=1.6, d=2.0, lines_col=(165, 182, 180), mark=None):
    def lines(p, x0, y0, x1, y1, zz):
        for i in range(n):
            yy = y0 + (i + 1) * (y1 - y0) / (n + 1)
            ln = 0.55 + 0.35 * ((i * 37) % 10) / 10
            c.line([p(x0 + 0.2, yy, zz), p(x0 + 0.2 + (w - 0.4) * ln, yy, zz)], lines_col, a, 3)
        if mark:
            mx, my = p(x0 + w * 0.8, y0 + d * 0.15, zz)
            c.d.ellipse([(mx - 7) * SS, (my - 7) * SS, (mx + 7) * SS, (my + 7) * SS], fill=lerp(mark, a))
    box(c, cx, cy, u, w, d, 0.12, PAGE, a, z, lines)

def stack(c, cx, cy, u, a, n=3, z=0):
    for i in range(n): page(c, cx, cy, u, a, z + i * 0.2, n=4 if i == n - 1 else 0)

def tray(c, cx, cy, u, w, d, a, z=0, faces=LIGHT):
    box(c, cx, cy, u, w, d, 0.35, faces, a, z)
    x0, y0 = -w / 2 + 0.18, -d / 2 + 0.18; x1, y1 = w / 2 - 0.18, d / 2 - 0.18
    p = lambda x, y: P(cx, cy, u, x, y, z + 0.35)
    c.poly([p(x0, y0), p(x1, y0), p(x1, y1), p(x0, y1)], (236, 243, 241), a, INK, 2)

def monitor(c, cx, cy, u, a, z=0, screen=None):
    box(c, cx, cy, u, 1.0, 0.7, 0.12, DARK, a, z)
    box(c, cx, cy, u, 0.18, 0.18, 0.7, DARK, a, z + 0.12)
    def scr(p, x0, y0, x1, y1, zz): pass
    # panel thin in y; its +y face is the screen
    w, d, h, zz = 2.2, 0.16, 1.5, z + 0.75
    x0, y0 = -w / 2, -d / 2; x1, y1 = w / 2, d / 2
    p = lambda x, y, q: P(cx, cy, u, x, y, q)
    c.poly([p(x0, y1, zz), p(x1, y1, zz), p(x1, y1, zz + h), p(x0, y1, zz + h)], DARK[2], a)
    c.poly([p(x1, y0, zz), p(x1, y1, zz), p(x1, y1, zz + h), p(x1, y0, zz + h)], DARK[1], a)
    c.poly([p(x0, y0, zz + h), p(x1, y0, zz + h), p(x1, y1, zz + h), p(x0, y1, zz + h)], DARK[0], a)
    m = 0.14
    c.poly([p(x0 + m, y1, zz + m), p(x1 - m, y1, zz + m), p(x1 - m, y1, zz + h - m), p(x0 + m, y1, zz + h - m)], CARD, a, None)
    for i in range(4):
        q = zz + h - 0.35 - i * 0.28; ln = [0.8, 0.6, 0.75, 0.5][i]
        c.line([p(x0 + 0.3, y1, q), p(x0 + 0.3 + (w - 0.6) * ln, y1, q)], (160, 178, 176), a, 3)

def desk(c, cx, cy, u, a):
    for lx, ly in [(-1.3, -0.7), (1.3, -0.7), (-1.3, 0.7), (1.3, 0.7)]:
        x, y = P(cx, cy, u, lx, ly, 0); x2, y2 = P(cx, cy, u, lx, ly, 1.1)
        c.line([(x, y), (x2, y2)], INK, a, 6)
    box(c, cx, cy, u, 3.0, 1.8, 0.15, MUSTARD, a, 1.1)
    # laptop
    box(c, cx, cy, u, 1.3, 0.9, 0.06, DARK, a, 1.25)
    p = lambda x, y, q: P(cx, cy, u, x, y, q)
    c.poly([p(-0.65, -0.45, 1.31), p(0.65, -0.45, 1.31), p(0.65, -0.55, 2.1), p(-0.65, -0.55, 2.1)], DARK[1], a)

def check(c, x, y, s, a, col=ACC, width=6):
    c.line([(x - s, y), (x - s * 0.35, y + s * 0.6), (x + s, y - s * 0.8)], col, a, width)

def cross(c, x, y, s, a, col=INK, width=5):
    c.line([(x - s, y - s), (x + s, y + s)], col, a, width); c.line([(x - s, y + s), (x + s, y - s)], col, a, width)

def arrow(c, x0, y0, x1, y1, a, k=1.0):
    x1 = x0 + (x1 - x0) * k; y1 = y0 + (y1 - y0) * k
    c.line([(x0, y0), (x1, y1)], INK, a, 3)
    if k > 0.95:
        ang = math.atan2(y1 - y0, x1 - x0)
        for s in (0.5, -0.5):
            c.line([(x1, y1), (x1 - 18 * math.cos(ang + s), y1 - 18 * math.sin(ang + s))], INK, a, 3)

def label(c, x, y, s, a, sub=None, col=INK):
    c.text(x, y, s, F_LAB(), col, a)
    if sub: c.text(x, y + 38, sub, F_SUB(), DIM, a)

def header(c, s, a): c.text(W / 2, 92, s, F_HEAD(), INK, a)

# ---------- scene machinery ----------
class Scene:
    def __init__(self, text):
        self.text = text; self.words = len(text.split())
        self.est = self.words / WPM * 60
        self.items = []; self.loops = []
    def at(self, phrase, off=0.0):
        i = self.text.find(phrase)
        assert i >= 0, phrase
        return self.est * i / len(self.text) + off
    def add(self, t, dur, fn, until=1e9): self.items.append((t, dur, fn, until))
    def loop(self, t, fn): self.loops.append((t, fn))
    def end(self): return max(t + d for t, d, _f, _u in self.items) + 0.6
    def frame(self, t):
        c = Ctx()
        for t0, dur, fn, until in self.items:
            if t0 <= t < until: fn(c, ease((t - t0) / dur) if dur > 0 else 1.0)
        return c.save()

def drop(fn, h=60):
    """object falls into place while fading in"""
    def g(c, k): fn(c, k, (1 - k) * -h)
    return g

U = 46  # default iso unit

def pill(c, cx, y, txt, k, fill=None, fg=(255, 255, 255)):
    fill = fill or INK
    f = font('Inter_28pt-Medium.ttf', 20); w = c.d.textlength(txt, font=f) / SS
    c.d.rounded_rectangle([(cx - w / 2 - 18) * SS, (y - 20) * SS, (cx + w / 2 + 18) * SS, (y + 20) * SS], radius=20 * SS, fill=lerp(fill, k))
    c.text(cx, y, txt, f, fg if k > 0.5 else lerp(fill, k), 1)

EVID = os.path.join(os.path.dirname(os.path.abspath(sheet)), 'evidence')
_SHOTS = {}
def shot(c, name, crop, x, y, w, k):
    key = (name, crop, w)
    if key not in _SHOTS:
        im = Image.open(os.path.join(EVID, name)).convert('RGB').crop(crop)
        h = round(w * im.height / im.width)
        _SHOTS[key] = im.resize((int(w * SS), int(h * SS)), Image.LANCZOS)
    im = _SHOTS[key]; h = im.height / SS
    c.d.rectangle([(x + 8) * SS, (y + 8) * SS, (x + w + 8) * SS, (y + h + 8) * SS], fill=lerp((214, 222, 220), k))
    c.im.paste(im, (int(x * SS), int(y * SS)), Image.new('L', im.size, int(255 * clamp(k))))
    c.d.rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], outline=lerp(INK, k), width=3 * SS)
    return h



GREEN = (46, 140, 98); PURPLE = (124, 92, 196); PINK = (226, 92, 140)
GRN3 = [(120, 204, 160), (64, 156, 112), (40, 120, 84)]
PUR3 = [(176, 152, 232), (124, 92, 196), (92, 64, 160)]
PNK3 = [(244, 156, 186), (226, 92, 140), (182, 60, 104)]

def TAG(txt, col=None):
    col = col or INK
    def f(c, k):
        fnt = font('Inter_28pt-Medium.ttf', 20); w = c.d.textlength(txt, font=fnt) / SS
        c.d.rounded_rectangle([(1800 - w - 36) * SS, 72 * SS, 1800 * SS, 112 * SS], radius=20 * SS, fill=lerp(col, k))
        c.text(1800 - w / 2 - 18, 92, txt, fnt, (255, 255, 255) if k > 0.5 else lerp(col, k), 1)
    return f
REAL = TAG('REAL · IN MY GITHUB FOLDER', GREEN)
PLAN = TAG('PLANNED · NOT BUILT YET', ACC)

def card(c, x, y, w, h, k, fill=(255, 255, 255), edge=INK, r=18):
    c.d.rounded_rectangle([(x + 8) * SS, (y + 10) * SS, (x + w + 8) * SS, (y + h + 10) * SS], radius=r * SS, fill=lerp((222, 228, 226), k))
    c.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=r * SS, fill=lerp(fill, k), outline=lerp(edge, k), width=3 * SS)

def txt(c, x, y, s_, k, size=36, col=INK, anchor='lm', face='EBGaramond-Regular.ttf'):
    c.text(x, y, s_, font(face, size), col, k, anchor)

def circ(c, x, y, r, col, k, edge=INK, w=3):
    c.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=lerp(col, k) if col else None, outline=lerp(edge, k) if edge else None, width=w * SS)

def pop(fn):
    """grow-in with a small overshoot"""
    def g(c, k):
        sc = 1 + 0.15 * math.sin(math.pi * clamp(k)) if k < 1 else 1
        fn(c, k, sc)
    return g

def flow(s, t0, pts, col=ACC, period=2.2, n=3, r=9):
    L = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]; T = sum(L)
    def f(c, dt):
        for j in range(n):
            u = ((dt / period) + j / n) % 1 * T
            for i, l in enumerate(L):
                if u <= l:
                    x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u / l; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u / l; break
                u -= l
            circ(c, x, y, r, col, 1, None)
    s.loop(t0, f)

def pulse(s, t0, x, y, col=ACC, period=1.6, rmax=70):
    def f(c, dt):
        u = (dt % period) / period
        c.d.ellipse([(x - rmax * u) * SS, (y - rmax * u) * SS, (x + rmax * u) * SS, (y + rmax * u) * SS], outline=lerp(col, 1 - u), width=4 * SS)
    s.loop(t0, f)

def robot(c, x, y, k, sc=1.0, col=None):
    col = col or DARK
    u = 60 * sc
    box(c, x, y, u, 1.8, 1.8, 1.5, col, k)
    hx, hy = P(x, y, u, 0, 0.9, 0.75)
    for dx in (-0.45, 0.45):
        ex, ey = P(x, y, u, dx, 0.9, 0.95)
        circ(c, ex, ey, 11 * sc, (255, 255, 255), k, None); circ(c, ex + 2, ey, 5 * sc, ACC, k, None)
    ax, ay = P(x, y, u, 0, 0, 1.5)
    c.line([(ax, ay), (ax, ay - 40 * sc)], INK, k, 4); circ(c, ax, ay - 46 * sc, 9 * sc, MUSTARD[0], k)

def magnifier(c, x, y, k, r=46, col=SKY[0]):
    c.line([(x + r * 0.7, y + r * 0.7), (x + r * 1.6, y + r * 1.6)], INK, k, 12)
    circ(c, x, y, r, (232, 244, 252), k, INK, 6)

def doc(c, x, y, w, h, k, lines=5, hl=None, col=(255, 255, 255)):
    card(c, x, y, w, h, k, col, INK, 10)
    for i in range(lines):
        yy = y + 30 + i * (h - 50) / max(1, lines - 1); ln = 0.55 + 0.35 * ((i * 37) % 10) / 10
        cc = hl[1] if hl and i == hl[0] else (190, 204, 202)
        c.line([(x + 20, yy), (x + 20 + (w - 40) * ln, yy)], cc, k, 6 if hl and i == hl[0] else 4)

def envelope(c, x, y, k, col=MUSTARD[0]):
    c.d.rectangle([(x - 60) * SS, (y - 40) * SS, (x + 60) * SS, (y + 40) * SS], fill=lerp(col, k), outline=lerp(INK, k), width=3 * SS)
    c.line([(x - 60, y - 40), (x, y + 5), (x + 60, y - 40)], INK, k, 3)

def shield(c, x, y, k, col=GREEN, sc=1.0):
    pts = [(x - 60 * sc, y - 70 * sc), (x + 60 * sc, y - 70 * sc), (x + 60 * sc, y + 5 * sc), (x, y + 75 * sc), (x - 60 * sc, y + 5 * sc)]
    c.poly(pts, col, k)
    check(c, x, y, 28 * sc, k, (255, 255, 255), max(3, int(8 * sc)))

def person(c, x, y, k, col=PINK, sc=1.0):
    circ(c, x, y - 70 * sc, 30 * sc, (246, 214, 190), k)
    c.d.pieslice([(x - 60 * sc) * SS, (y - 30 * sc) * SS, (x + 60 * sc) * SS, (y + 90 * sc) * SS], 180, 360, fill=lerp(col, k), outline=lerp(INK, k), width=3 * SS)

def board(c, cx, cy, k, nm, faces, o=0):
    box(c, cx, cy + o, 34, 2.4, 1.8, 1.2, faces, k)
    for i in range(3):
        x0, y0 = P(cx, cy + o, 34, -0.8, -0.5 + i * 0.4, 1.21); x1, y1 = P(cx, cy + o, 34, 0.7, -0.5 + i * 0.4, 1.21)
        c.line([(x0, y0), (x1, y1)], (255, 255, 255), k, 4)
    label(c, cx, cy + 80, nm, k)

def bars(c, k, x, y, label_, num, den, col):
    txt(c, x, y, label_, k, 34)
    c.d.rounded_rectangle([(x + 330) * SS, (y - 22) * SS, (x + 930) * SS, (y + 22) * SS], radius=22 * SS, outline=lerp(INK, k), width=2 * SS, fill=lerp((255, 255, 255), k))
    if k > 0.05: c.d.rounded_rectangle([(x + 334) * SS, (y - 18) * SS, (x + 334 + 592 * num / den * k) * SS, (y + 18) * SS], radius=18 * SS, fill=lerp(col, 1))
    txt(c, x + 960, y, f'{num}/{den}', k, 38, INK, face='EBGaramond-Medium.ttf')

# ================= scenes =================
def S_B00(s):
    s.add(0, 0.5, lambda c, k: c.text(W / 2, 60, 'FINAL PROJECT FILM  ·  ANISHA GAIKAR  ·  INFO 7375', F_TINY(), DIM, k))
    s.add(0.1, 0.8, pop(lambda c, k, sc: robot(c, 300, 330, k, 0.9 * sc, PUR3)))
    s.add(0.3, 0.8, pop(lambda c, k, sc: (doc(c, 1540, 200, 150, 190, k, 5, (2, ACC)), magnifier(c, 1640, 330, k, 40))))
    s.add(s.at('a job-search agent'), 0.8, lambda c, k: c.text(W / 2, 250, 'A job-search agent', font('EBGaramond-Medium.ttf', 96), INK, k))
    s.add(s.at('a job-search agent') + 0.6, 0.8, lambda c, k: (c.text(W / 2, 340, 'that shows its reasons, and says "I cannot tell" instead of guessing', F_SUB(), DIM, k), c.line([(700, 395), (1220, 395)], ACC, k, 3)))
    t1 = s.at('The question I started'); t2 = s.at('The better question')
    s.typing = ('Can AI', 'find me jobs?', 'tell me which new postings are worth my time?', t1, max(1.0, t2 - t1 - 1.0), t2)
    s.add(t2 + 3.4, 0.01, lambda c, k: None)

def S_B01(s):
    cols = [GRN3, SKY, PUR3]
    for i, nm in enumerate(['Greenhouse', 'Greenhouse', 'Lever']):
        y = 300 + i * 190
        s.add(s.at('watches public job boards') + i * 0.3, 0.7, drop(lambda c, k, o, y=y, nm=nm, i=i: board(c, 250, y, k, nm + ' board', cols[i], o)))
    t = s.at('only the postings that are new')
    s.add(t, 0.6, lambda c, k: [arrow(c, 370, 300 + i * 190, 780, 500, 1, k) for i in range(3)])
    for i in range(3): flow(s, t + 0.6, [(370, 300 + i * 190), (780, 500)], [GREEN, SKYC, PURPLE][i], 1.8, 2, 8)
    s.add(t, 0.9, pop(lambda c, k, sc: (robot(c, 900, 560, k, sc), label(c, 900, 700, 'my agent', k, 'only what is new'))))
    s.add(t + 0.8, 0.01, lambda c, k: None); pulse(s, t + 0.9, 900, 470, PURPLE)
    tf = s.at('whether each one fits me')
    s.add(tf, 0.6, lambda c, k: arrow(c, 1030, 500, 1220, 500, 1, k)); flow(s, tf + 0.6, [(1030, 500), (1220, 500)], ACC, 1.4, 2, 8)
    def short(c, k):
        card(c, 1240, 330, 560, 330, k)
        for i, (v, col) in enumerate([('fits', GREEN), ('not for me', DIM), ('I cannot tell', MUSC)]):
            circ(c, 1280, 385 + i * 100, 12, col, k, None)
            txt(c, 1305, 385 + i * 100, f'new posting {i + 1}', k, 32); txt(c, 1560, 385 + i * 100, v, k, 32, col, face='EBGaramond-Medium.ttf')
            txt(c, 1305, 420 + i * 100, '"…the posting’s own words…"', k, 24, DIM, face='EBGaramond-Italic.ttf')
    s.add(tf, 0.8, short)
    t = s.at('It never applies')
    for i, w in enumerate(['applies', 'emails', 'messages', 'logs in']):
        x = 480 + i * 320
        s.add(t + i * 0.45, 0.5, pop(lambda c, k, sc, x=x, w=w: (pill(c, x, 880, 'never ' + w, k, (110, 128, 130)), cross(c, x + 100, 880, 14 * sc, k, ACC, 5))))

def S_B02(s):
    s.add(0, 0.5, REAL)
    hit = {7, 23, 61, 88, 104, 140}
    def grid(c, k):
        n = int(156 * k)
        for i in range(n):
            r, q = divmod(i, 26); x = 330 + q * 48; y = 270 + r * 58
            if i in hit and k >= 1: box(c, x, y, 15, 1.4, 1.8, 0.5, CORAL, 1)
            else: box(c, x, y, 14, 1.4, 1.8, 0.15, PAGE, 1, outline=GHOST)
    s.add(s.at('Most of a job board'), 2.2, grid)
    for j, i in enumerate(sorted(hit)):
        r, q = divmod(i, 26); pulse(s, s.at('only 6 of 156') + j * 0.15, 330 + q * 48, 262 + r * 58, ACC, 1.8, 34)
    s.add(s.at('only 6 of 156'), 0.6, pop(lambda c, k, sc: (txt(c, W / 2, 700, '6 of 156', k, int(86 * sc), ACC, 'mm', 'EBGaramond-Medium.ttf'),
                                                           txt(c, W / 2, 770, 'postings had an analyst title · Klaviyo board, my JS1 run, 2026-10-31', k, 30, DIM, 'mm', 'EBGaramond-Italic.ttf'))))
    s.add(s.at('a summary that invents'), 0.6, lambda c, k: (doc(c, 300, 600, 130, 160, k, 4, (2, ACC)), cross(c, 470, 660, 22, k, ACC, 6),
                                                              txt(c, 520, 660, 'invented detail', k, 34, ACC, face='EBGaramond-Italic.ttf')))

def S_B03(s):
    s.add(0, 0.5, TAG('ILLUSTRATION · EXAMPLE ROWS', PURPLE))
    s.add(0.1, 0.7, lambda c, k: card(c, 300, 230, 1320, 520, k))
    rows = [('Data Analyst, Payments', 'fits', '"2+ years of SQL and Tableau"', GREEN),
            ('Senior Compensation Analyst', 'not for me', '"3-5 years of experience in compensation"', DIM),
            ('Analytics Associate', 'I cannot tell', 'the posting does not say how many years', MUSC)]
    t = s.at('a short list')
    for i, (t_, v, q, col) in enumerate(rows):
        y = 300 + i * 150
        def row(c, k, y=y, t_=t_, v=v, q=q, col=col, i=i):
            c.d.rounded_rectangle([320 * SS, (y - 40) * SS, 334 * SS, (y + 70) * SS], radius=6 * SS, fill=lerp(col, k))
            txt(c, 360, y, t_, k, 38, INK, face='EBGaramond-Medium.ttf'); pill(c, 1400, y, v, k, col)
            txt(c, 390, y + 50, q, k, 30, DIM, face='EBGaramond-Italic.ttf')
        s.add(t + i * 0.6, 0.6, row)
    s.add(s.at('the exact lines'), 0.6, lambda c, k: magnifier(c, 1250, 360, k, 40))
    s.add(s.at('check every reason'), 0.6, pop(lambda c, k, sc: (check(c, 800, 860, 26 * sc, k, GREEN, 7), txt(c, 850, 860, 'every reason checkable in seconds', k, 38))))

def S_B04(s):
    def bell(c, k, sc):
        x, y = 470, 430; r = 120 * sc
        c.d.pieslice([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], 180, 360, fill=lerp(MUSTARD[0], k), outline=lerp(INK, k), width=3 * SS)
        c.d.rectangle([(x - r) * SS, y * SS, (x + r) * SS, (y + 45 * sc) * SS], fill=lerp(MUSTARD[0], k), outline=lerp(INK, k), width=3 * SS)
        circ(c, x, y + 70 * sc, 20 * sc, INK, k, None)
        label(c, x, 600, 'job alert', k, 'e.g. LinkedIn job alerts')
    s.add(s.at('Job sites send alerts'), 0.8, pop(bell)); pulse(s, s.at('Job sites send alerts') + 0.8, 470, 400, MUSC, 1.3, 160)
    s.add(s.at('matched your keywords'), 0.6, lambda c, k: (envelope(c, 820, 330, k), check(c, 960, 330, 22, k, GREEN), txt(c, 1000, 330, 'something new matched my keywords', k, 40)))
    s.add(s.at('not whether it fits you'), 0.6, pop(lambda c, k, sc: (person(c, 830, 540, k, PINK, 0.7), cross(c, 960, 500, 18 * sc, k, ACC, 6), txt(c, 1000, 500, 'does it fit me?', k, 40, ACC))))
    s.add(s.at('or why'), 0.6, pop(lambda c, k, sc: (txt(c, 830, 680, '?', k, int(90 * sc), PURPLE, 'mm', 'EBGaramond-Medium.ttf'), cross(c, 960, 680, 18 * sc, k, ACC, 6), txt(c, 1000, 680, 'why?', k, 40, ACC))))

def S_B05(s):
    s.add(0, 0.5, REAL)
    t1 = s.at('On October 13th'); t2 = s.at('On October 31st')
    s.add(t1, 0.6, lambda c, k: (shot(c, 'chatgpt-pasted-2026-10-13.png', (200, 30, 1830, 850), 120, 170, 780, k),
                                 pill(c, 330, 600, 'ChatGPT · my test · 2026-10-13', k, SKYC)))
    s.add(s.at('no source for each fact'), 0.5, pop(lambda c, k, sc: (cross(c, 140, 680, 14 * sc, k, ACC, 5), txt(c, 175, 680, 'no source line for each fact', k, 34))))
    s.add(s.at('added a location detail'), 0.5, pop(lambda c, k, sc: (cross(c, 140, 740, 14 * sc, k, ACC, 5), txt(c, 175, 740, 'added a location detail not in the posting', k, 34))))
    s.add(t2, 0.6, lambda c, k: (shot(c, 'claude-way1-2026-10-31.png', (160, 320, 1560, 940), 1000, 170, 800, k),
                                 pill(c, 1200, 600, 'Claude · my test · 2026-10-31', k, PURPLE)))
    s.add(s.at('hedged prose'), 0.5, pop(lambda c, k, sc: (cross(c, 1020, 680, 14 * sc, k, ACC, 5), txt(c, 1055, 680, '"mostly not relevant": hedged prose', k, 34))))
    s.add(s.at('nothing I could check'), 0.5, pop(lambda c, k, sc: (cross(c, 1020, 740, 14 * sc, k, ACC, 5), txt(c, 1055, 740, 'nothing to check automatically', k, 34))))
    s.add(s.at('no memory'), 0.5, pop(lambda c, k, sc: (cross(c, 1020, 800, 14 * sc, k, ACC, 5), txt(c, 1055, 800, 'no memory of what I had seen', k, 34))))

def S_B06(s):
    t = s.at('Lectern')
    for i in range(6):
        x = 260 + (i % 3) * 120; y = 300 + (i // 3) * 110
        s.add(t + i * 0.12, 0.5, drop(lambda c, k, o, x=x, y=y, i=i: box(c, x, y + o, 22, 2.2, 1.6, 1.0, [GRN3, SKY, PUR3][i % 3], k)))
        flow(s, t + 1.2, [(x, y), (640, 560)], [GREEN, SKYC, PURPLE][i % 3], 1.6 + i * 0.1, 1, 7)
    s.add(t + 0.4, 0.8, drop(lambda c, k, o: (box(c, 640, 600 + o, 42, 3.6, 2.4, 1.5, SKY, k), label(c, 640, 730, 'Lectern', k, '18 boards collected'))))
    s.add(s.at('Reallocation Engine'), 0.8, drop(lambda c, k, o: (box(c, 1320, 600 + o, 42, 3.0, 2.4, 1.5, GRN3, k), label(c, 1320, 730, 'Reallocation Engine', k, 'role scorer'))))
    s.add(s.at('Collecting is solved'), 0.6, pop(lambda c, k, sc: (check(c, 1060, 300, 24 * sc, k, GREEN, 7), txt(c, 1110, 300, 'collecting: solved', k, 44))))
    s.add(s.at('Deciding, with evidence'), 0.6, pop(lambda c, k, sc: (txt(c, 1060, 390, '?', k, int(70 * sc), ACC, 'mm', 'EBGaramond-Medium.ttf'), txt(c, 1110, 390, 'deciding, with evidence: not yet', k, 44, ACC))))

def S_B07(s):
    items = [('new postings only', 'new postings only', GRN3), ('a verdict you can check', 'a verdict you can check', SKY),
             ("an honest 'I cannot tell'", '"I cannot tell"', MUSTARD), ('hard limits', 'hard limits', CORAL)]
    for i, (ph, lab, f) in enumerate(items):
        def blk(c, k, o, i=i, lab=lab, f=f):
            box(c, 760, 800 - i * 115 + o, 62, 4.2, 2.6, 1.4, f, k)
            c.line([(1010, 775 - i * 115), (1150, 775 - i * 115)], INK, k, 2)
            txt(c, 1170, 775 - i * 115, lab, k, 42, INK, face='EBGaramond-Medium.ttf')
        s.add(s.at(ph), 0.7, drop(blk, 120))
    s.add(s.at("That's the gap"), 0.6, lambda c, k: txt(c, 1170, 260, 'the gap my project fills', k, 48, ACC, face='EBGaramond-Italic.ttf'))
    s.add(s.at('why mine is worth building'), 0.6, lambda c, k: pill(c, 1400, 320, 'WHY MINE IS WORTH BUILDING', k, ACC))
    s.add(s.at('hard limits') + 0.6, 0.8, pop(lambda c, k, sc: (person(c, 360, 760, k, PINK, sc), label(c, 360, 860, 'you', k))))

def S_B08(s):
    s.add(0, 0.5, REAL)
    t = s.at('Greenhouse and Lever')
    s.add(t, 0.7, drop(lambda c, k, o: board(c, 300, 340, k, 'Greenhouse API', GRN3, o)))
    s.add(t + 0.4, 0.7, drop(lambda c, k, o: board(c, 300, 600, k, 'Lever API', PUR3, o)))
    s.add(s.at('No account'), 0.8, pop(lambda c, k, sc: (shield(c, 720, 460, k), label(c, 720, 590, 'allow-list', k, 'only these two hosts'))))
    flow(s, t + 1.2, [(410, 340), (650, 450)], GREEN, 1.6, 2, 8); flow(s, t + 1.2, [(410, 600), (650, 480)], PURPLE, 1.6, 2, 8)
    s.add(s.at('only those two hosts'), 0.6, lambda c, k: (pill(c, 720, 720, 'any other host', k, (150, 160, 160)), cross(c, 840, 720, 16, k, ACC, 5)))
    def persona(c, k):
        card(c, 1080, 280, 660, 420, k, (255, 250, 244))
        person(c, 1200, 430, k, PINK, 0.9)
        txt(c, 1290, 360, 'Nadia Okafor', k, 46, INK, face='EBGaramond-Medium.ttf')
        pill(c, 1400, 420, 'FICTIONAL PERSONA', k, ACC)
        txt(c, 1130, 540, 'entry-level data analyst', k, 32); txt(c, 1130, 590, 'SQL · Python · Tableau · Excel', k, 32)
        txt(c, 1130, 645, 'nadia.okafor@example.com', k, 26, DIM, face='PTMono-Regular.ttf')
    s.add(s.at('fictional persona'), 0.7, persona)

def S_B09(s):
    s.add(0, 0.5, REAL)
    s.add(s.at('already ran'), 0.5, lambda c, k: txt(c, W / 2, 200, 'both ran · tests, logs and live runs in my GitHub folder', k, 32, DIM, 'mm', 'EBGaramond-Italic.ttf'))
    t = s.at('Layer one')
    s.add(t, 0.8, drop(lambda c, k, o: (box(c, 520, 730 + o, 50, 4.4, 3.0, 1.0, GRN3, k), txt(c, 330, 870, 'Step 1 · Layer 1 (JS1)', k, 42, INK, face='EBGaramond-Medium.ttf'))))
    s.add(s.at('by a written rule'), 0.5, pop(lambda c, k, sc: (doc(c, 220, 280, 120, 150, k, 4), label(c, 280, 470, 'written rule', k))))
    s.add(s.at('by Claude'), 0.5, pop(lambda c, k, sc: (robot(c, 520, 420, k, 0.55 * sc, PUR3), label(c, 520, 470, 'Claude', k))))
    s.add(s.at('a validator'), 0.6, pop(lambda c, k, sc: (shield(c, 760, 380, k, ACC), label(c, 760, 490, 'validator', k, 'quotes must be in the posting'))))
    t2 = s.at('Layer two')
    s.add(t2, 0.8, drop(lambda c, k, o: (box(c, 1380, 730 + o, 50, 4.4, 3.0, 1.0, SKY, k), txt(c, 1190, 870, 'Step 2 · Layer 2 (JS2)', k, 42, INK, face='EBGaramond-Medium.ttf'))))
    ts = s.at('three boards on two systems')
    for i, f in enumerate([GRN3, GRN3, PUR3]):
        s.add(ts + i * 0.2, 0.5, drop(lambda c, k, o, i=i, f=f: box(c, 1150 + i * 150, 330 + o, 22, 2.4, 1.8, 1.2, f, k)))
    def loop_(c, dt):
        a0 = dt * 2.4
        cx, cy, r = 1380, 470, 70
        c.d.arc([(cx - r) * SS, (cy - r * 0.5) * SS, (cx + r) * SS, (cy + r * 0.5) * SS], 0, 360, fill=SKYC, width=4 * SS)
        circ(c, cx + r * math.cos(a0), cy + r * 0.5 * math.sin(a0), 10, ACC, 1, None)
    s.loop(ts + 0.6, loop_)
    s.add(s.at('budgets'), 0.5, lambda c, k: pill(c, 1240, 560, '5 boards · 15 requests · 60 s', k, MUSC))
    s.add(s.at('permission policy'), 0.6, pop(lambda c, k, sc: (shield(c, 1640, 470, k), label(c, 1640, 580, 'policy in code', k))))

def S_B10(s):
    s.add(0, 0.5, PLAN)
    s.add(0.2, 0.6, lambda c, k: (box(c, 360, 800, 34, 4.2, 3.0, 1.0, GRN3, k), box(c, 360, 800, 34, 4.2, 3.0, 1.0, SKY, k, z=1.0), txt(c, 260, 900, 'layers 1–2 (done)', k, 32, DIM)))
    s.add(s.at('layer three'), 0.6, lambda c, k: (ghost_box(c, 360, 800, 34, 4.2, 3.0, 1.0, k) if False else None, txt(c, 760, 230, 'Step 3 · Layer 3 (JS3, due this week)', k, 44, ACC, face='EBGaramond-Medium.ttf')))
    parts = [('a readable filter', 'readable filter', lambda c, k, x, y: doc(c, x - 50, y - 60, 100, 120, k, 4, (1, MUSC))),
             ("the 'I cannot tell' rule", '"I cannot tell"', lambda c, k, x, y: txt(c, x, y, '?', k, 80, MUSC, 'mm', 'EBGaramond-Medium.ttf')),
             ('the agent as a tool', 'tool for Claude', lambda c, k, x, y: robot(c, x, y + 40, k, 0.45, PUR3)),
             ('a score', 'explained score', lambda c, k, x, y: txt(c, x, y, '%', k, 70, SKYC, 'mm', 'EBGaramond-Medium.ttf'))]
    for i, (ph, lab, ic) in enumerate(parts):
        x = 820 + i * 250; y = 420
        def it(c, k, sc, x=x, y=y, lab=lab, ic=ic):
            circ(c, x, y, 95 * sc, (255, 255, 255), k, GHOST, 3); ic(c, k, x, y); txt(c, x, y + 140, lab, k, 28, INK, 'mm')
        s.add(s.at(ph), 0.6, pop(it))
    s.add(s.at('my appendix'), 0.5, lambda c, k: (doc(c, 300, 300, 120, 150, k, 4, (0, SKYC)), txt(c, 360, 490, 'APPENDIX.md', k, 28, DIM, 'mm', 'PTMono-Regular.ttf')))
    s.add(s.at('one daily shortlist'), 0.7, pop(lambda c, k, sc: (card(c, 820, 700, 920, 120, k, (255, 247, 230), MUSC), txt(c, 860, 760, 'Step 4 · final project: one daily shortlist', k, int(42 * sc), INK, face='EBGaramond-Medium.ttf'))))

def S_B11(s):
    s.add(s.at('Do I have what I need'), 0.6, lambda c, k: txt(c, 300, 230, 'Do I have what I need?', k, 52, INK, face='EBGaramond-Medium.ttf'))
    rows = [('Accounts', 'none needed: public job boards', lambda c, k, x, y: person(c, x, y + 30, k, PINK, 0.5)),
            ('Access', 'only two public APIs (allow-list)', lambda c, k, x, y: shield(c, x, y + 10, k, GREEN, 0.5)),
            ('Compute', 'my own laptop + Python', lambda c, k, x, y: box(c, x, y + 30, 26, 2.4, 1.6, 0.4, DARK, k)),
            ('Token credits', 'my own Claude account, small batches', lambda c, k, x, y: [circ(c, x - 18 + i * 18, y + 10 - i * 8, 24, MUSTARD[0], k) for i in range(3)])]
    for i, (ph, sub, ic) in enumerate(rows):
        y = 360 + i * 140
        def row(c, k, sc, y=y, ph=ph, sub=sub, ic=ic):
            card(c, 300, y - 55, 1320, 110, k)
            ic(c, k, 400, y - 10)
            txt(c, 520, y, ph, k, 44, INK, face='EBGaramond-Medium.ttf'); txt(c, 860, y, sub, k, 36)
            check(c, 1560, y, 22 * sc, k, GREEN, 7)
        s.add(s.at(ph + ':'), 0.6, pop(row))
    s.add(s.at('Yes.'), 0.5, lambda c, k: pill(c, 820, 230, 'YES', k, GREEN))

def S_B12(s):
    s.add(0, 0.5, REAL)
    s.add(s.at('my own hand labels'), 0.6, pop(lambda c, k, sc: (person(c, 200, 330, k, PINK, 0.7), txt(c, 280, 300, 'my own hand labels', k, 42, INK, face='EBGaramond-Medium.ttf'))))
    s.add(s.at('never with its own report'), 0.5, lambda c, k: (robot(c, 1550, 330, k, 0.5, PUR3), cross(c, 1650, 280, 20, k, ACC, 6), txt(c, 1460, 430, 'not its own report', k, 30, ACC, face='EBGaramond-Italic.ttf')))
    s.add(s.at('10 of 10'), 1.0, lambda c, k: bars(c, k, 300, 520, 'development', 10, 10, GREEN))
    s.add(s.at('9 of 10'), 1.0, lambda c, k: bars(c, k, 300, 610, 'held back', 9, 10, GREEN))
    s.add(s.at('19 of my 20'), 1.0, lambda c, k: bars(c, k, 300, 740, '"not relevant" labels', 19, 20, ACC))
    s.add(s.at('so that test was weak'), 0.5, lambda c, k: txt(c, 300, 820, 'an "always no" judge would also score 19/20', k, 34, ACC, face='EBGaramond-Italic.ttf'))

def S_B13(s):
    s.add(0, 0.5, REAL)
    t = s.at('All 18')
    for i in range(18):
        r, q = divmod(i, 6)
        s.add(t + i * 0.08, 0.35, pop(lambda c, k, sc, r=r, q=q: (circ(c, 260 + q * 75, 330 + r * 85, 28 * sc, (226, 244, 234), k, GREEN, 3), check(c, 260 + q * 75, 332 + r * 85, 13 * sc, k, GREEN, 5))))
    s.add(t + 1.5, 0.5, lambda c, k: txt(c, 220, 610, '18 of 18 boundary predictions matched', k, 36))
    s.add(s.at('two deliberately wrong versions'), 0.6, lambda c, k: (card(c, 900, 290, 860, 130, k), txt(c, 930, 335, 'wrong version A:  exit=finished', k, 30, INK, face='PTMono-Regular.ttf'),
                                                                     txt(c, 930, 385, 'wrong version B:  exit=finished', k, 30, INK, face='PTMono-Regular.ttf')))
    s.add(s.at('independent recount'), 0.6, lambda c, k: (magnifier(c, 1000, 560, k, 50, (255, 236, 230)), card(c, 1100, 480, 660, 160, k, (253, 240, 236), ACC),
                                                         txt(c, 1130, 525, 'INDEPENDENT CHECK: FAIL', k, 30, ACC, face='PTMono-Regular.ttf'),
                                                         txt(c, 1130, 580, 'reported 0 jobs, but the raw', k, 22, INK, face='PTMono-Regular.ttf'),
                                                         txt(c, 1130, 610, 'response contains 304', k, 22, INK, face='PTMono-Regular.ttf')))
    s.add(s.at('caught both'), 0.6, pop(lambda c, k, sc: (check(c, 940, 740, 26 * sc, k, GREEN, 7), txt(c, 990, 740, 'caught both', k, 46, INK, face='EBGaramond-Medium.ttf'))))

def S_B14(s):
    s.add(0, 0.5, PLAN)
    def target(c, k):
        for r, col in [(190, (252, 232, 226)), (135, (244, 190, 176)), (80, ACC)]:
            circ(c, 420, 520, r * k, col, 1, INK, 2)
        txt(c, 420, 520, '≥80%', k, 50, (255, 255, 255), 'mm', 'EBGaramond-Medium.ttf')
    s.add(s.at('My pass mark'), 0.9, target)
    def dart(c, k):
        x = 420 + 360 * (1 - k); y = 520 - 260 * (1 - k)
        c.line([(x, y), (x + 120, y - 90)], INK, 1, 6); c.poly([(x, y), (x + 22, y - 4), (x + 6, y - 20)], ACC, 1)
    s.add(s.at('80 percent'), 0.5, dart)
    lines = [('at least 30', '30+ new postings I label and hold back'), ('at least 10 relevant', 'at least 10 of them relevant'), ('80 percent', 'agrees with me ≥ 80%')]
    for i, (ph, t_) in enumerate(lines):
        s.add(s.at(ph), 0.5, pop(lambda c, k, sc, i=i, t_=t_: (check(c, 760, 330 + i * 75, 16 * sc, k, GREEN, 5), txt(c, 800, 330 + i * 75, t_, k, 36))))
    s.add(s.at('It fails'), 0.5, lambda c, k: txt(c, 760, 600, 'fails, however good the number looks, if:', k, 36, ACC, face='EBGaramond-Italic.ttf'))
    s.add(s.at('one quote'), 0.5, pop(lambda c, k, sc: (cross(c, 780, 680, 14 * sc, k, ACC, 6), txt(c, 810, 680, 'one quote is not in the posting', k, 36))))
    s.add(s.at('a failed board'), 0.5, pop(lambda c, k, sc: (cross(c, 780, 755, 14 * sc, k, ACC, 6), txt(c, 810, 755, 'a failed board shows as "no new jobs"', k, 36))))

def S_B15(s):
    s.add(s.at('layers one and two exist'), 0.8, drop(lambda c, k, o: (box(c, 560, 740 + o, 50, 3.6, 2.6, 1.0, GRN3, k), box(c, 560, 740 + o, 50, 3.6, 2.6, 1.0, SKY, k, z=1.0),
                                                                       label(c, 560, 850, 'exists today', k, 'layers 1–2 · tests · logs · live runs'))))
    s.add(s.at('The rest will exist'), 0.8, lambda c, k: (ghost_box(c, 1360, 740, 50, 3.6, 2.6, 1.0, k), ghost_box(c, 1360, 690, 50, 3.6, 2.6, 1.0, k),
                                                         label(c, 1360, 850, 'will exist', k, 'filter · tool · score · daily shortlist')))
    s.add(s.at('computer reading my script'), 0.5, lambda c, k: txt(c, W / 2, 330, 'narration: macOS voice reading my script', k, 32, DIM, 'mm', 'EBGaramond-Italic.ttf'))
    s.add(s.at('Thanks for watching'), 0.6, pop(lambda c, k, sc: (txt(c, W / 2, 230, 'Thanks for watching · Anisha Gaikar', k, int(56 * sc), INK, 'mm', 'EBGaramond-Medium.ttf'), robot(c, 960, 560, k, 0.5, PUR3))))

TITLES = {'B01': '1 · Executive summary: what it is', 'B02': '1 · Executive summary: why care', 'B03': '1 · Executive summary: what you get',
          'B04': '2 · Introduction: job alerts', 'B05': '2 · Introduction: chatbots (my tests)', 'B06': '2 · Introduction: collectors',
          'B07': '2 · Introduction: the gap', 'B08': '3 · Methods: the data', 'B09': '3 · Methods: my plan, step by step',
          'B10': '3 · Methods: steps 3 and 4', 'B11': '3 · Methods: do I have what I need?', 'B12': '4 · Evaluation: my own labels',
          'B13': '4 · Evaluation: checks that don’t trust it', 'B14': '4 · Evaluation: my pass mark', 'B15': 'Exists today vs. will exist'}

F_TITLE = lambda: font('EBGaramond-Medium.ttf', 46)
F_CAP = lambda: font('EBGaramond-Italic.ttf', 36)

def sentences(text, T):
    import re as _re
    parts = [p for p in _re.split(r'(?<=[.?!])\s+', text) if p]
    out, pos = [], 0
    for p in parts:
        i = text.find(p, pos); out.append((T * i / len(text), p)); pos = i + len(p)
    return [(t, (out[k + 1][0] if k + 1 < len(out) else T), p) for k, (t, p) in enumerate(out)]

def wrap(c, s_, f, maxw):
    words, lines, cur = s_.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if c.d.textlength(trial, font=f) / SS > maxw and cur: lines.append(cur); cur = w
        else: cur = trial
    lines.append(cur); return lines

def draw(s, bid, t):
    c = Ctx()
    for t0, dur, fn, until in s.items:
        if t0 <= t < until: fn(c, ease((t - t0) / dur) if dur > 0 else 1)
    for t0, fn in s.loops:
        if t >= t0: fn(c, t - t0)
    if hasattr(s, 'typing'): render_typing(s, t, c.im)
    if bid in TITLES:
        tt = TITLES[bid]
        if ' · ' in tt:
            num, tt = tt.split(' · ', 1)
            col = [ACC, MUSC, SKYC, (52, 120, 92)][(int(num) - 1) % 4]
            r = 30 * clamp(t / 0.4)
            c.d.ellipse([(140 - r) * SS, (92 - r) * SS, (140 + r) * SS, (92 + r) * SS], fill=col)
            if r > 20: c.text(140, 94, num, font('Inter_28pt-Medium.ttf', 30), (255, 255, 255), 1)
        n = int(clamp(t / 1.0) * len(tt))
        c.text(190, 92, tt[:n], F_TITLE(), INK, 1, 'lm')
    if bid != 'B00':
        f = F_CAP()
        for t0, t1, sen in s.caps:
            if t0 <= t < t1:
                shown = sen[:int(clamp((t - t0) / min(1.2, 0.4 * (t1 - t0))) * len(sen))]
                lines = wrap(c, sen, f, 1560)
                # reveal by character count across the wrapped lines
                left = len(shown); ys = [992] if len(lines) == 1 else [952, 992]
                wmax = max(c.d.textlength(l, font=f) for l in lines[:2]) / SS
                c.d.rounded_rectangle([(W / 2 - wmax / 2 - 40) * SS, (ys[0] - 30) * SS, (W / 2 + wmax / 2 + 40) * SS, (ys[-1] + 26) * SS],
                                      radius=28 * SS, fill=(255, 255, 255), outline=INK, width=2 * SS)
                for y, ln in zip(ys, lines[:2]):
                    part = ln[:max(0, left)]; left -= len(ln) + 1
                    c.text(W / 2, y, part, f, INK, 1)
                break
    # slow camera drift
    z = 1 + 0.010 * clamp(t / s.T)
    w2, h2 = W * SS / z, H * SS / z
    l, tp = (W * SS - w2) / 2, (H * SS - h2) / 2
    return c.im.resize((W, H), Image.BOX, box=(l, tp, l + w2, tp + h2))

SCENES = {k[2:]: v for k, v in globals().items() if k.startswith('S_B')}

def render_typing(s, t, img):
    l1, naive, fixed, t1, span, t2 = s.typing
    c = Ctx(); c.im = img; c.d = ImageDraw.Draw(img)
    f = F_BIG()
    n1 = len(l1) + len(naive)
    if t < t1: return
    typed = int(clamp((t - t1) / span) * n1)
    line1 = l1[:typed]
    line2, col2 = '', ACC
    if typed > len(l1): line2 = naive[:typed - len(l1)]
    if t >= t2:
        dt = t - t2
        back = int(dt / 0.06)
        if back < len(naive): line2 = naive[:len(naive) - back]
        else:
            n = int((dt - len(naive) * 0.06) / 0.05); line2 = fixed[:n]; col2 = INK
    blink = int(t * 2) % 2 == 0
    c.text(W / 2, 590, line1, f, INK, 1)
    c.text(W / 2, 690, line2, f, col2, 1)
    if blink:
        bb = c.d.textbbox((W / 2 * SS, 690 * SS), line2 or ' ', font=f, anchor='mm')
        x = bb[2] / SS + 6 if line2 else W / 2
        c.line([(x, 655), (x, 725)], INK, 1, 3)

def render(bid, text):
    s = Scene(text)
    SCENES[bid](s)
    s.T = max(s.est, s.end())
    s.caps = sentences(text, s.T)
    if os.environ.get('PREVIEW'):
        for frac in os.environ['PREVIEW'].split(','):
            draw(s, bid, s.T * float(frac)).save(os.path.join(OUT, f'{bid}_{frac}.png'))
        print(bid, f'{s.T:.1f}s'); return
    n = int(s.T * FPS) + 1
    path = os.path.join(OUT, bid + '.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'fast', path], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(draw(s, bid, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(bid, f'{s.T:.1f}s', flush=True)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    beats = json.load(open(sheet))['beats']
    for b in beats:
        if ONLY and b['beat_id'] not in ONLY: continue
        render(b['beat_id'], b['narration_text'])
