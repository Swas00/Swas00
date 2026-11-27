"""STRATOSPHERE: one design system for every generated asset.

Cloud-computing identity: a deep-ocean night sky, cloud-white text, and an
aurora accent (teal -> sky -> violet). Every generator reads named colour ROLES
from here, never hex literals.

Colour rules: one colour, one meaning. Green = live / healthy only. Amber =
warm / stale. Language colours are reserved for languages. Text roles are all
>= 4.5:1 on SURFACE. Cards are self-contained dark surfaces so they read the
same on GitHub's light and dark page themes. Everything animates with SMIL or
CSS only, so it runs inside <img> on github.com.
"""
import math

CANVAS = "#040b16"
SURFACE = "#071425"
RAISED = "#0d2038"
HAIRLINE = "#1c3556"
TEXT = "#eaf4ff"
TEXT2 = "#aac3e2"
TEXT3 = "#7f9bbf"

TEAL = "#2dd4bf"
SKY = "#4cc2ff"
BLUE = "#4f8dff"
VIOLET = "#a78bfa"
PINK = "#f472b6"
AMBER = "#fbbf24"
GREEN = "#34d399"   # live / healthy only
ROSE = "#fb7185"

A1, A2, A3 = TEAL, SKY, VIOLET
GRAD = (TEAL, SKY, VIOLET)
RAMP = ["#0e2238", "#0f5c73", "#14b8a6", "#7dd3fc", "#f0f9ff"]   # quiet -> busy (heat)

LANG = dict(Python="#34d399", TypeScript="#4cc2ff", JavaScript="#fbbf24", Java="#fb7185",
            HTML="#fb923c", C="#a78bfa", Other="#7f9bbf")
VISITOR = {"cyan": "#4cc2ff", "pink": "#f472b6", "gold": "#fbbf24", "green": "#34d399", "violet": "#a78bfa"}

SANS = "system-ui,-apple-system,'SF Pro Text','Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
T_TITLE, T_HEAD, T_BODY, T_CAP, T_LABEL = 22, 14, 13, 11, 10


def lang_color(name):
    return LANG.get(name, LANG["Other"])


def ramp(t):
    """Heat colour for 0..1 (piecewise-linear over RAMP)."""
    t = max(0.0, min(1.0, t))
    k = t * (len(RAMP) - 1)
    i = min(int(k), len(RAMP) - 2)
    a, b = RAMP[i], RAMP[i + 1]
    f = k - i
    ca = [int(a[j:j + 2], 16) for j in (1, 3, 5)]
    cb = [int(b[j:j + 2], 16) for j in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(ca[n] + (cb[n] - ca[n]) * f) for n in range(3))


def shade(hexc, f):
    """Scale a hex colour's brightness by f (0..1.5)."""
    c = [int(hexc[j:j + 2], 16) for j in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * f))) for v in c)


def defs(extra=""):
    """Shared <defs>. Include once per SVG."""
    return f"""<defs>
<linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{SKY}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="auroraV" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{SKY}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="bdr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity=".55"/><stop offset=".5" stop-color="{SKY}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".55"/></linearGradient>
<linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY}" stop-opacity=".38"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<style>
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.label{{font-family:{MONO};font-size:{T_LABEL}px;letter-spacing:.14em;text-transform:uppercase;fill:{TEXT3}}}
</style>{extra}</defs>"""


def card_open(w, h, title, meta="", r=18):
    """Standard card chrome: surface, a live (green) dot, title, meta."""
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{SURFACE}"/>'
            f'<circle cx="28" cy="30" r="3.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>'
            f'<text x="40" y="34" class="label" style="fill:{TEXT2}">{title}</text>'
            + (f'<text x="{w - 28}" y="34" class="label" text-anchor="end">{meta}</text>' if meta else "")
            + f'<line x1="28" y1="48" x2="{w - 28}" y2="48" stroke="{HAIRLINE}"/>')


def card_border(w, h, r=18):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="url(#bdr)" stroke-width="1.2"/>'


def svg_open(w, h, label, title, extra_defs="", desc=""):
    d = f"<desc>{desc}</desc>" if desc else ""
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">',
            f"<title>{title}</title>{d}", defs(extra_defs + f'<clipPath id="card"><rect width="{w}" height="{h}" rx="18"/></clipPath>'),
            '<g clip-path="url(#card)">']


def cloud_path(cx, cy, s=1.0):
    """A flat-bottomed puffy cloud silhouette centred at (cx, cy); s scales (base width ~120*s)."""
    def P(x, y):
        return f"{cx + x * s:.1f},{cy + y * s:.1f}"
    return (f"M{P(-60, 14)} "
            f"C{P(-82, 14)} {P(-84, -16)} {P(-54, -16)} "
            f"C{P(-52, -40)} {P(-14, -46)} {P(-4, -26)} "
            f"C{P(8, -50)} {P(52, -44)} {P(50, -14)} "
            f"C{P(78, -16)} {P(84, 14)} {P(58, 14)} Z")


def hexagon(cx, cy, r, rot=-90):
    pts = []
    for k in range(6):
        a = math.radians(rot + 60 * k)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def iso_box(x, y, w, d, h, top, left, right):
    """Isometric box whose back-top vertex sits at (x, y). w,d are iso half-diagonals; h is height.
    Returns SVG for top, left and right faces."""
    # 2:1 isometric: x-axis goes down-right, y-axis goes down-left
    p_top = [(x, y), (x + w, y + w / 2), (x + w - d, y + w / 2 + d / 2), (x - d, y + d / 2)]
    def pts(a):
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in a)
    lf = [(x - d, y + d / 2), (x + w - d, y + w / 2 + d / 2), (x + w - d, y + w / 2 + d / 2 + h), (x - d, y + d / 2 + h)]
    rt = [(x + w - d, y + w / 2 + d / 2), (x + w, y + w / 2), (x + w, y + w / 2 + h), (x + w - d, y + w / 2 + d / 2 + h)]
    return (f'<polygon points="{pts(lf)}" fill="{left}"/><polygon points="{pts(rt)}" fill="{right}"/>'
            f'<polygon points="{pts(p_top)}" fill="{top}"/>')


def smooth(pts):
    """Catmull-Rom spline through pts as cubic bezier path data."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def write(path, parts):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
