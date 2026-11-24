"""Renders the show-tell style clips (silent) for the JobPost Contracts pitch.
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

# ---------- scenes ----------
def S_B00(s):
    s.add(0, 0.5, lambda c, k: c.text(W / 2, 60, 'JOBPOST CONTRACTS  ·  FINAL PROJECT PITCH  ·  ANISHA GAIKAR  ·  INFO 7375', F_TINY(), DIM, k))
    s.add(0, 0.5, lambda c, k: c.text(W / 2, 990, 'Anisha Gaikar', F_SUB(), DIM, k))
    s.add(s.at('JobPost Contracts'), 0.8, lambda c, k: c.text(W / 2, 250, 'JobPost Contracts', font('EBGaramond-Medium.ttf', 96), INK, k))
    s.add(s.at('a Python tool'), 0.8, lambda c, k: (c.text(W / 2, 340, 'summarizes job postings, catches when the AI makes things up', F_SUB(), DIM, k), c.line([(760, 395), (1160, 395)], ACC, k, 3)))
    l1 = 'Can AI summarize a job posting'
    naive, fixed = 'for me?', 'without inventing anything?'
    t1 = s.at('My first question'); t2 = s.at('The better question')
    span1 = max(1.0, t2 - t1 - 1.0)
    def typing(c, _):
        pass
    s.typing = (l1, naive, fixed, t1, span1, t2)
    s.add(t2 + 2.6, 0.01, lambda c, k: None)

def S_B01(s):
    def card(c, k):
        c.text(240, 230, 'Terms In This Film', font('EBGaramond-Regular.ttf', 46), DIM, k, 'lm')
        c.line([(240, 280), (1680, 280)], GHOST, k, 2)
        c.text(1680, 950, 'ANISHA GAIKAR', F_TINY(), DIM, k, 'rm')
    s.add(0, 0.6, card)
    rows = [('prompt contract', 'rules the AI must follow', 'A prompt contract'),
            ('synthetic posting', 'a fake job ad I write myself', 'A synthetic posting'),
            ('grounded field', 'an answer with a quote from the posting', 'a grounded field')]
    for i, (term, mean, ph) in enumerate(rows):
        y = 380 + i * 170
        def row(c, k, y=y, term=term, mean=mean, i=i):
            c.text(260, y, term, font('EBGaramond-Medium.ttf', 44), INK, k, 'lm')
            c.text(820, y, mean, font('EBGaramond-Regular.ttf', 40), INK, k, 'lm')
            c.line([(240, y + 80), (1680, y + 80)], GHOST, k, 2)
            col = [ACC, MUSC, SKYC][i]
            c.d.ellipse([(222) * SS, (y - 9) * SS, (240) * SS, (y + 9) * SS], fill=lerp(col, k))
        s.add(s.at(ph), 0.6, row)

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

def CONS(c, k):
    f = font('Inter_28pt-Medium.ttf', 20); txt = 'CONSTRUCTED · NOT BUILT YET'
    w = c.d.textlength(txt, font=f) / SS
    c.d.rounded_rectangle([(1800 - w - 36) * SS, 72 * SS, 1800 * SS, 112 * SS], radius=20 * SS, fill=lerp(INK, k))
    c.text(1800 - w / 2 - 18, 92, txt, f, (255, 255, 255) if k > 0.5 else lerp(INK, k), 1)

def S_B02(s):
    s.add(0, 0.5, CONS)
    s.add(0.2, 0.8, drop(lambda c, k, o: (page(c, 470, 470 + o, 60, k, mark=ACC), label(c, 470, 640, 'job posting', k))))
    s.add(s.at('prompt contracts'), 0.5, lambda c, k: arrow(c, 620, 470, 820, 470, 1, k))
    s.add(s.at('prompt contracts'), 0.8, drop(lambda c, k, o: (box(c, 960, 500 + o, 60, 1.5, 1.5, 1.5, DARK, k), label(c, 960, 640, 'contract', k))))
    s.add(s.at('structured summary'), 0.5, lambda c, k: arrow(c, 1100, 470, 1300, 470, 1, k))
    def summ(c, k, o):
        tray(c, 1470, 480 + o, 60, 2.2, 2.2, k)
        for i in range(5):
            x0, y0 = P(1470, 480 + o, 60, -0.75, -0.8 + i * 0.4, 0.36); x1, y1 = P(1470, 480 + o, 60, 0.75, -0.8 + i * 0.4, 0.36)
            c.line([(x0, y0), (x1, y1)], ACC if i % 2 == 0 else DIM, k, 4)
        label(c, 1470, 640, 'summary', k)
    s.add(s.at('structured summary'), 0.8, drop(summ))
    ti = s.at('catches Claude inventing')
    def inv(c, k):
        c.text(1470, 290, 'salary: $90k?', F_LAB(), INK, k)
    s.add(ti, 0.5, inv)
    def strike(c, k):
        bb = c.d.textbbox((1470 * SS, 290 * SS), 'salary: $90k?', font=F_LAB(), anchor='mm')
        x0, x1 = bb[0] / SS, bb[2] / SS
        c.line([(x0, 292), (x0 + (x1 - x0) * k, 292)], ACC, 1, 4)
    s.add(ti + 1.0, 0.6, strike)
    s.add(ti + 1.8, 0.5, lambda c, k: c.text(1470, 238, 'not stated', F_LAB(), ACC, k))
    parts = [('contracts', DARK), ('20 postings', PAGE), ('tests', MUSTARD), ('eval log', SKY)]
    t0 = s.at("When it's done")
    _travel(s, s.at('structured summary') + 1.0, [((630, 470), (810, 470)), ((1110, 470), (1290, 470))])
    for i, (nm, f) in enumerate(parts):
        x = 560 + i * 270
        def part(c, k, o, x=x, nm=nm, f=f):
            if f is PAGE: stack(c, x, 790 + o, 34, k)
            else: box(c, x, 800 + o, 34, 1.4, 1.4, 1.0 if nm != 'eval log' else 0.4, f, k)
            label(c, x, 860, nm, k)
        s.add(t0 + 1.2 + i * 0.9, 0.7, drop(part))

def _travel(s, t0, segs, period=2.4):
    def f(c, dt):
        ph = (dt % period) / period * len(segs)
        i = int(ph); u = ph - i
        (x0, y0), (x1, y1) = segs[i]
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        c.d.ellipse([(x - 9) * SS, (y - 9) * SS, (x + 9) * SS, (y + 9) * SS], fill=ACC)
    s.loop(t0, f)

LINK_CROP = (90, 30, 1700, 380)
PASTE_CROP = (200, 30, 1830, 850)
GREEN = (33, 110, 92)
def S_B03(s):
    tp = s.at('Pasting'); tlink = s.at('I tried a real'); tpaste = s.at('with the text pasted')
    tsrc = s.at("didn't show which line"); tloc = s.at('under location it added'); ts = s.at('Copying'); tm = s.at('In my tool')
    # A: who it is for (until the alternatives start)
    for i in range(6):
        s.add(0.3 + i * 0.25, 0.5, drop(lambda c, k, o, i=i: page(c, 760 + i * 70, 440 + o - i * 6, 34, k, n=3), 40), tp)
    s.add(1.6, 0.5, lambda c, k: c.text(1270, 430, 'lots of postings', F_SUB(), DIM, k, 'lm'), tp)
    s.add(2.4, 0.5, lambda c, k: label(c, 960, 620, 'job seekers comparing roles', k), tp)
    # B: the REAL ChatGPT test, shown with my own screenshots
    s.add(tp, 0.5, lambda c, k: pill(c, 1580, 92, 'REAL · MY CHATGPT TEST · 2026-10-13', k, GREEN), ts)
    s.add(tlink, 0.6, lambda c, k: (shot(c, 'chatgpt-link-2026-10-13.png', LINK_CROP, 1230, 190, 560, k),
                                   c.text(1510, 352, "couldn't open the LinkedIn link", F_SUB(), INK, k)), ts)
    s.add(tpaste, 0.6, lambda c, k: shot(c, 'chatgpt-pasted-2026-10-13.png', PASTE_CROP, 130, 180, 1000, k), ts)
    s.add(tsrc, 0.5, lambda c, k: (c.text(1240, 470, 'no source for any field', F_LAB(), ACC, k, 'lm')), ts)
    def hl(c, k):
        # Location row of the pasted screenshot (crop coords -> screen)
        sc = 1000 / (PASTE_CROP[2] - PASTE_CROP[0])
        y0 = 180 + (690 - PASTE_CROP[1]) * sc; y1 = 180 + (768 - PASTE_CROP[1]) * sc
        c.d.rounded_rectangle([140 * SS, (y0 - 4) * SS, 1120 * SS, (y1 + 4) * SS], radius=8 * SS, outline=lerp(ACC, k), width=5 * SS)
        arrow(c, 1125, (y0 + y1) / 2, 1228, 600, k)
        c.text(1240, 590, 'added a fact not in the posting', F_LAB(), ACC, k, 'lm')
        c.text(1240, 632, '"headquartered near Boston"', F_SUB(), INK, k, 'lm')
    s.add(tloc, 0.6, hl, ts)
    # C: compare the three, side by side
    s.add(ts, 0.6, lambda c, k: (shot(c, 'chatgpt-pasted-2026-10-13.png', PASTE_CROP, 150, 400, 400, k),
                                 pill(c, 350, 360, 'REAL · 2026-10-13', k, GREEN),
                                 label(c, 350, 720, 'chatbot', k, 'no source shown')))
    def sheet(c, k, o):
        box(c, 960, 560 + o, 60, 2.6, 2.0, 0.12, PAGE, k)
        for i in range(1, 5):
            x0, y0 = P(960, 560 + o, 60, -1.3, -1 + i * 0.4, 0.12); x1, y1 = P(960, 560 + o, 60, 1.3, -1 + i * 0.4, 0.12)
            c.line([(x0, y0), (x1, y1)], (165, 182, 180), k, 2)
        for i in range(1, 3):
            x0, y0 = P(960, 560 + o, 60, -1.3 + i * 0.87, -1, 0.12); x1, y1 = P(960, 560 + o, 60, -1.3 + i * 0.87, 1, 0.12)
            c.line([(x0, y0), (x1, y1)], (165, 182, 180), k, 2)
        label(c, 960, 720, 'spreadsheet', k, 'slow, by hand')
    s.add(ts + 0.3, 0.8, drop(sheet))
    def clock(c, k):
        c.d.ellipse([(960 - 40) * SS, (380 - 40) * SS, (960 + 40) * SS, (380 + 40) * SS], outline=lerp(INK, k), width=4 * SS, fill=lerp(CARD, k))
        c.line([(960, 380), (960, 352)], INK, k, 4); c.line([(960, 380), (982, 392)], INK, k, 4)
    s.add(ts + 1.5, 0.5, clock)
    s.add(tm, 0.5, lambda c, k: pill(c, 1520, 380, 'CONSTRUCTED · NOT BUILT YET', k))
    s.add(tm, 0.8, drop(lambda c, k, o: (page(c, 1400, 590 + o, 50, k, n=5), tray(c, 1640, 560 + o, 46, 2.0, 2.0, k, faces=SKY))))
    def links(c, k):
        for i in range(3):
            a0 = P(1400, 590, 50, 0.2, -0.65 + i * 0.66, 0.12); a1 = P(1640, 560, 46, -0.6, -0.5 + i * 0.5, 0.36)
            dashed(c, [a0, (a0[0] + (a1[0] - a0[0]) * k, a0[1] + (a1[1] - a0[1]) * k)], ACC, 1)
        label(c, 1520, 720, 'my tool', 1, 'a quote for every field')
    s.add(tm + 1.4, 1.2, links)
    segs = []
    for i in range(3):
        a0 = P(1400, 590, 50, 0.2, -0.65 + i * 0.66, 0.12); a1 = P(1640, 560, 46, -0.6, -0.5 + i * 0.5, 0.36)
        segs.append((a0, a1))
    _travel(s, tm + 2.8, segs, 3.0)

def S_B04(s):
    s.add(0, 0.5, CONS)
    s.add(0.3, 0.8, drop(lambda c, k, o: (desk(c, 330, 640 + o, 52, k), label(c, 330, 760, 'hiring manager', k))))
    tr = s.at('open the README'); tc = s.at('run one command'); tp = s.at('see a pass')
    s.add(tr - 0.4, 0.4, lambda c, k: arrow(c, 520, 560, 640, 560, 1, k))
    s.add(tr, 0.8, drop(lambda c, k, o: (page(c, 790, 600 + o, 55, k), label(c, 790, 760, 'README', k))))
    s.add(tc - 0.4, 0.4, lambda c, k: arrow(c, 940, 560, 1060, 560, 1, k))
    def term(c, k, o):
        box(c, 1220, 620 + o, 55, 2.4, 1.4, 1.0, DARK, k)
        label(c, 1220, 760, 'one command', k)
        c.text(1220, 420, '$ python run_tests.py', F_MONO(), INK, k)
    s.add(tc, 0.8, drop(term))
    s.add(tp - 0.4, 0.4, lambda c, k: arrow(c, 1380, 560, 1480, 560, 1, k))
    s.add(tp, 0.8, drop(lambda c, k, o: (page(c, 1620, 600 + o, 55, k, n=5), label(c, 1620, 760, 'pass / fail', k))))
    for i, ok in enumerate([1, 1, 0, 1, 0]):
        def mk(c, k, i=i, ok=ok):
            x, y = 1760, 470 + i * 42
            (check(c, x, y, 13, k, ACC, 5) if ok else cross(c, x, y, 11, k, INK, 4))
        s.add(tp + 0.9 + i * 0.25, 0.3, mk)
    s.add(tp + 2.4, 0.6, lambda c, k: c.text(W / 2, 860, 'first 60 seconds', font('EBGaramond-Italic.ttf', 46), ACC, k))
    def cur(c, dt):
        if int(dt * 2) % 2 == 0:
            bb = c.d.textbbox((1220 * SS, 420 * SS), '$ python run_tests.py', font=F_MONO(), anchor='mm')
            x = bb[2] / SS + 8; c.d.rectangle([x * SS, 405 * SS, (x + 14) * SS, 436 * SS], fill=INK)
    s.loop(tc + 0.9, cur)
    _travel(s, tp + 1.0, [((530, 560), (630, 560)), ((950, 560), (1050, 560)), ((1390, 560), (1470, 560))], 2.4)

def S_B05(s):
    s.add(0, 0.5, CONS)
    s.add(0.3, 0.6, lambda c, k: ghost_box(c, 760, 840, 66, 2.6, 2.6, 3.6, k))
    s.add(0.8, 0.5, lambda c, k: c.text(760, 330, 'four course skills', F_SUB(), DIM, k))
    names = [('writing prompt contracts', 'contracts'), ('grounding every answer', 'grounding'), ('verifying that each quote', 'verify'), ('evaluating with a fixed', 'evaluate')]
    for i, (ph, nm) in enumerate(names):
        z = i * 0.9
        faces = [DARK, MUSTARD, SKY, CORAL][i]
        def blk(c, k, o, z=z, nm=nm, faces=faces, i=i):
            box(c, 760, 840 + o, 66, 2.6, 2.6, 0.9, faces, k, z)
            x, y = P(760, 840, 66, 1.3, 0, z + 0.45)
            c.line([(x + 30, y), (x + 120, y)], DIM, k, 2)
            c.text(x + 135, y, nm, F_LAB(), INK, k, 'lm')
        s.add(s.at(ph), 0.7, drop(blk, 120))
    tn = s.at('It will not prove')
    def gh(c, k):
        ghost_box(c, 1450, 760, 60, 2.4, 2.4, 1.2, k)
        cross(c, 1450, 700, 70, k, ACC, 5)
        label(c, 1450, 850, 'real data at scale', k, 'not proven')
    s.add(tn, 0.8, gh)
    def scan(c, dt):
        u = (dt % 3.0) / 3.0; y = 860 - u * 420
        c.line([(560, y), (960, y)], ACC, 1, 3)
    s.loop(s.at('evaluating with a fixed') + 1.0, scan)

def S_B06(s):
    s.add(0, 0.5, CONS)
    ti = s.at('In scope'); to = s.at('Out of scope'); tf = s.at('The first piece'); tk = s.at('test prints PASS')
    s.add(ti, 0.8, drop(lambda c, k, o: (tray(c, 400, 560 + o, 64, 3.0, 3.0, k), label(c, 400, 790, 'in', k, 'five fields'))))
    for i in range(5):
        def tile(c, k, o, i=i):
            gx, gy = [(-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7), (0, 0)][i]
            box(c, *P(400, 560 + o, 64, gx, gy, 0.35), 64, 0.8, 0.8, 0.3, [SKY, MUSTARD, LIGHT, SKY, CORAL][i], k)
        s.add(ti + 0.9 + i * 0.6, 0.5, drop(tile, 40))
    outs = ['scraping', 'real postings', 'career advice']
    for i, nm in enumerate(outs):
        def o_(c, k, o, i=i, nm=nm):
            x = 860 + i * 0  # stacked vertically
            y = 420 + i * 150
            box(c, 960, y + o, 34, 1.4, 1.4, 0.6, LIGHT, k)
            c.text(1040, y - 10, nm, F_LAB(), INK, k, 'lm')
        s.add(to + 0.5 + i * 0.7, 0.5, drop(o_, 40))
    for i in range(3):
        s.add(to + 2.8 + i * 0.3, 0.3, lambda c, k, i=i: cross(c, 960, 410 + i * 150, 24, k, ACC, 5))
    s.add(to, 0.5, lambda c, k: label(c, 960, 820, 'out', k))
    s.add(tf, 0.8, drop(lambda c, k, o: (page(c, 1580, 560 + o, 58, k), label(c, 1580, 820, 'first', k, 'one contract, one posting'))))
    s.add(tk, 0.5, lambda c, k: (check(c, 1580, 380, 34, k, ACC, 8), c.text(1580, 440, 'PASS', F_LAB(), INK, k)))

def S_B07(s):
    s.add(0, 0.5, CONS)
    for i in range(5):
        s.add(0.3 + i * 0.3, 0.6, drop(lambda c, k, o, i=i: page(c, 330 + i * 150, 560 + o, 44, k, n=4)))
        s.add(s.at('every test passes') + i * 0.25, 0.3, lambda c, k, i=i: check(c, 340 + i * 150, 430, 18, k, ACC, 5))
    s.add(s.at('proves nothing'), 0.5, lambda c, k: label(c, 630, 700, 'too clean', k, 'proves nothing'))
    tt = s.at('deliberately tricky')
    for i in range(5):
        tricky = i in (1, 3)
        def pg(c, k, o, i=i, tricky=tricky):
            page(c, 1150 + i * 150, 560 + o, 44, k, n=4, lines_col=ACC if tricky else (165, 182, 180))
        s.add(tt + i * 0.3, 0.6, drop(pg))
        s.add(tt + 2.2 + i * 0.25, 0.3, (lambda c, k, i=i: cross(c, 1160 + i * 150, 430, 15, k, INK, 5)) if tricky else (lambda c, k, i=i: check(c, 1160 + i * 150, 430, 18, k, ACC, 5)))
    s.add(tt + 3.6, 0.5, lambda c, k: label(c, 1450, 700, 'tricky cases', k, 'failures show up'))
    def sweep(c, dt):
        u = (dt % 2.8) / 2.8; x = 1080 + u * 760
        c.line([(x, 490), (x, 620)], ACC, 1, 4)
    s.loop(tt + 4.2, sweep)
    tw = s.at('A second limit')
    s.add(tw + 1.0, 0.6, lambda c, k: c.text(W / 2, 800, 'wrong field  →  hand-checked and logged', font('EBGaramond-Italic.ttf', 38), DIM, k))

def S_B08(s):
    s.add(0, 0.5, CONS)
    tn = s.at('Prompt contracts, building'); ta = s.at('The skill I already have')
    reasons = [('small enough to finish alone', 'small enough'), ('uses what this course teaches', 'uses exactly'), ('a mix: new and existing skills', 'a mix of new learning')]
    for i, (txt, ph) in enumerate(reasons):
        y = 250 + i * 62
        def r(c, k, y=y, txt=txt):
            n = int(k * len(txt)); c.text(780, y, txt[:n], font('EBGaramond-Italic.ttf', 40), INK, 1, 'lm')
            if k >= 1: check(c, 740, y, 14, 1, ACC, 5)
        s.add(s.at(ph), 1.2, r)
    s.add(tn, 0.5, lambda c, k: label(c, 600, 860, 'new to me', k))
    for i, nm in enumerate(['contracts', 'test sets', 'eval logs']):
        def b(c, k, o, i=i, nm=nm):
            box(c, 600, 760 + o, 66, 2.6, 2.6, 0.8, [SKY, DARK, MUSTARD][i], k, i * 0.8)
            x, y = P(600, 760, 66, 1.3, 0, i * 0.8 + 0.4)
            c.line([(x + 30, y), (x + 120, y)], DIM, k, 2)
            c.text(x + 135, y, nm, F_LAB(), INK, k, 'lm')
        s.add(tn + i * 0.9, 0.7, drop(b, 120))
    s.add(ta, 0.7, drop(lambda c, k, o: (box(c, 1400, 760 + o, 66, 2.6, 2.6, 0.8, CORAL, k), label(c, 1400, 860, 'already have', k))))
    s.add(ta + 0.6, 0.5, lambda c, k: (c.text(1400, 540, 'Python', F_LAB(), INK, k), c.text(1400, 580, 'MBTA pipeline on GitHub', F_SUB(), DIM, k)))

def S_B09(s):
    s.add(0, 0.5, CONS)
    te = s.at('today, what exists'); tw = s.at('Everything else')
    for i, nm in enumerate(['brief', 'beat sheet', 'film']):
        def b(c, k, o, i=i, nm=nm):
            page(c, 560, 700 + o, 60, k, z=i * 0.5, n=3)
            x, y = P(560, 700, 60, 0.8, 0, i * 0.5)
            c.line([(x + 40, y - 6 - i * 20), (x + 120, y - 6 - i * 30)], DIM, k, 2)
            c.text(x + 135, y - 6 - i * 30, nm, F_LAB(), INK, k, 'lm')
        s.add(te + 0.6 + i * 0.6, 0.6, drop(b, 80))
    s.add(te, 0.5, lambda c, k: label(c, 560, 840, 'exists today', k))
    for i, nm in enumerate(['contracts', 'postings', 'tests', 'eval log']):
        x = 1180 + (i % 2) * 330; y = 470 + (i // 2) * 240
        s.add(tw + i * 0.5, 0.6, lambda c, k, x=x, y=y, nm=nm: (ghost_box(c, x, y, 40, 1.8, 1.8, 1.0, k), c.text(x, y + 90, nm, F_SUB(), DIM, k)))
    s.add(tw, 0.5, lambda c, k: label(c, 1345, 840, 'will exist', k))
    _travel(s, tw + 2.5, [((720, 640), (1080, 520)), ((720, 640), (1080, 760))], 3.2)

TITLES = {'B02': '1 · What is it?', 'B03': '2 · Why would anyone care?', 'B04': '3 · Who opens it?',
          'B05': '4 · What does it prove?', 'B06': '5 · In, out, first', 'B07': '6 · What could sink it?',
          'B08': '7 · Why this project?', 'B09': 'Exists today vs. will exist'}
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
            col = [ACC, MUSC, SKYC][(int(num) - 1) % 3]
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
