#!/usr/bin/env python3
"""assets/header.svg + assets/div-*.svg: hero banner and section dividers.

Hero: a night sky with three parallax layers of drifting clouds, an aurora, a
live service-mesh cluster (packets travelling between nodes), a typed terminal
prompt, rotating role lines, live status chips, a glowing traffic wave built
from the last 52 weeks of contributions, and a row of server racks with
blinking LEDs along the bottom. Pure SMIL, so it animates inside <img>.

Dividers: one pipeline-stage line per README section; a packet runs the line
and lights each node as it passes.
"""
import os
import random
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
W, H = 830, 430
NAME = "Swastik"
ROLES = ["Building on the cloud.", "Containers, CI/CD & serverless.", "Full-stack, shipped to prod."]

DIVIDERS = [  # (file, number, label)
    ("div-arch", "01", "ARCHITECTURE"),
    ("div-cluster", "02", "CLUSTER STATUS"),
    ("div-observe", "03", "OBSERVABILITY"),
    ("div-dc", "04", "DATA CENTER"),
    ("div-mesh", "05", "SERVICE MESH"),
    ("div-deploy", "06", "DEPLOYMENTS"),
    ("div-edge", "07", "GLOBAL EDGE"),
    ("div-ctf", "08", "INTERCEPTED TRANSMISSION"),
    ("div-stack", "09", "TOOLCHAIN"),
]


def ago(delta):
    h = delta.total_seconds() / 3600
    if h < 1:
        return "just now"
    if h < 24:
        return f"{int(h)}h ago"
    d = int(h // 24)
    return "yesterday" if d == 1 else f"{d}d ago"


def cloud_layer(rnd, y, scale, opacity, dur, n, fill):
    """n clouds drifting left->right across the full width, endlessly."""
    out = []
    span = W + 260
    for k in range(n):
        cx = -130 + k * span / n
        cy = y + rnd.uniform(-16, 16)
        s = scale * rnd.uniform(.85, 1.2)
        d = dur * rnd.uniform(.9, 1.1)
        out.append(
            f'<g opacity="{opacity}"><animateTransform attributeName="transform" type="translate" values="0 0;{span} 0" dur="{d:.0f}s" '
            f'begin="-{rnd.uniform(0, d):.0f}s" repeatCount="indefinite"/>'
            f'<path d="{t.cloud_path(cx, cy, s)}" fill="{fill}"/></g>')
    return "".join(out)


def mesh_cluster(rnd):
    """Service-mesh cluster, right side: hex nodes, links, travelling packets."""
    cx, cy = 668, 146
    ring = [("API", -90), ("DB", -30), ("CDN", 30), ("CI", 90), ("AI", 150), ("S3", 210)]
    R = 112
    pos = {}
    for name, a in ring:
        import math
        pos[name] = (cx + R * math.cos(math.radians(a)), cy + R * .86 * math.sin(math.radians(a)))
    o = []
    o.append(f'<g transform="translate({cx} {cy})"><circle r="{R + 22}" fill="none" stroke="{t.SKY}" stroke-opacity=".16" stroke-dasharray="2 7">'
             f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="70s" repeatCount="indefinite"/></circle>'
             f'<circle r="{R - 46}" fill="none" stroke="{t.TEAL}" stroke-opacity=".14" stroke-dasharray="1 5">'
             f'<animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="46s" repeatCount="indefinite"/></circle></g>')
    # links
    names = [n for n, _ in ring]
    links = [(cx, cy, *pos[n]) for n in names] + [(*pos[names[i]], *pos[names[(i + 1) % 6]]) for i in range(6)]
    for (x1, y1, x2, y2) in links:
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t.SKY}" stroke-opacity=".28" stroke-width="1"/>')
    cols = [t.TEAL, t.SKY, t.VIOLET]
    for i, (x1, y1, x2, y2) in enumerate(links):
        for rep in range(2):
            dur = rnd.uniform(2.6, 5.2)
            a, b = ((x1, y1), (x2, y2)) if (i + rep) % 2 == 0 else ((x2, y2), (x1, y1))
            col = cols[(i + rep) % 3]
            o.append(f'<circle r="2.4" fill="{col}" filter="url(#glow)" opacity="0"><animateMotion path="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}" dur="{dur:.1f}s" begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="{dur:.1f}s" begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/></circle>')
    # satellite hexes
    for k, (name, _) in enumerate(ring):
        x, y = pos[name]
        o.append(f'<g><polygon points="{t.hexagon(x, y, 19)}" fill="{t.SURFACE}" stroke="{cols[k % 3]}" stroke-width="1.4"/>'
                 f'<polygon points="{t.hexagon(x, y, 19)}" fill="{cols[k % 3]}" fill-opacity=".12"><animate attributeName="fill-opacity" values=".06;.3;.06" dur="{2.4 + k * .35:.2f}s" begin="{k * .4:.1f}s" repeatCount="indefinite"/></polygon>'
                 f'<text x="{x:.1f}" y="{y + 3.5:.1f}" class="mono" font-size="9.5" font-weight="700" fill="{t.TEXT}" text-anchor="middle">{name}</text></g>')
    # core
    o.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="{t.SKY}" fill-opacity=".14" filter="url(#soft)"/>')
    for k in range(3):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="{t.SKY}" stroke-width="1.2" opacity="0"><animate attributeName="r" values="22;58" dur="3.6s" begin="{k * 1.2}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".6;0" dur="3.6s" begin="{k * 1.2}s" repeatCount="indefinite"/></circle>')
    o.append(f'<path d="{t.cloud_path(cx, cy + 4, .36)}" fill="url(#aurora)" filter="url(#glow)"/>')
    return "".join(o)


def racks(rnd):
    out = []
    x, i = 6, 0
    while x < W - 10:
        w = rnd.choice([26, 30, 34])
        h = rnd.choice([20, 26, 32, 38])
        y = H - h
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h + 2}" rx="2" fill="#081a2e" stroke="{t.HAIRLINE}" stroke-opacity=".7"/>')
        for ry in range(y + 5, H - 2, 6):
            col = rnd.choice([t.GREEN, t.SKY, t.GREEN, t.AMBER, t.TEAL])
            out.append(f'<rect x="{x + 4}" y="{ry}" width="{w - 14}" height="2" rx="1" fill="{t.HAIRLINE}"/>'
                       f'<circle cx="{x + w - 7}" cy="{ry + 1}" r="1.3" fill="{col}"><animate attributeName="opacity" values="1;.15;1" dur="{rnd.uniform(.9, 3.2):.1f}s" begin="-{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
        x += w + 4
        i += 1
    return "".join(out)


def header(last, streak, weekly, total):
    rnd = random.Random(7)
    mx = max(weekly) or 1
    base, amp = H - 44, 58
    pts = [(i * (W + 8) / (len(weekly) - 1) - 4, base - amp * (v / mx) ** .7) for i, v in enumerate(weekly)]
    line = t.smooth(pts)
    area = f"{line} L{W + 4},{H} L-4,{H} Z"

    o = t.svg_open(W, H, f"{escape(USER)}: cloud computing engineer. {streak} day streak.", f"{escape(NAME)} // cloud profile",
                   f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#020611"/><stop offset=".55" stop-color="#081d38"/><stop offset="1" stop-color="#0f4468"/></linearGradient>'
                   f'<linearGradient id="nameg" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{t.TEAL}"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="{t.VIOLET}"/>'
                   f'<animate attributeName="x1" values="-300;340" dur="7s" repeatCount="indefinite"/><animate attributeName="x2" values="0;640" dur="7s" repeatCount="indefinite"/></linearGradient>'
                   f'<linearGradient id="cl1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe6ff"/><stop offset="1" stop-color="#6fa3d6"/></linearGradient>'
                   f'<linearGradient id="wave" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.TEAL}" stop-opacity="0"/><stop offset=".25" stop-color="{t.TEAL}"/><stop offset=".6" stop-color="{t.SKY}"/><stop offset=".9" stop-color="{t.VIOLET}"/><stop offset="1" stop-color="{t.VIOLET}" stop-opacity="0"/></linearGradient>'
                   f'<linearGradient id="waveFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.SKY}" stop-opacity=".30"/><stop offset="1" stop-color="{t.SKY}" stop-opacity="0"/></linearGradient>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # aurora blobs
    for (cx, cy, rx, ry, col, dur) in [(180, 90, 230, 70, t.TEAL, 17), (520, 60, 260, 60, t.VIOLET, 23), (700, 150, 200, 80, t.SKY, 19)]:
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity=".16" filter="url(#soft)"><animate attributeName="cx" values="{cx};{cx + 60};{cx - 40};{cx}" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".10;.22;.10" dur="{dur * .6:.0f}s" repeatCount="indefinite"/></ellipse>')
    # stars
    for _ in range(46):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 210), rnd.choice([.7, .9, 1.2, 1.5])
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#dff1ff"><animate attributeName="opacity" values=".15;.9;.15" dur="{rnd.uniform(1.6, 4.2):.1f}s" begin="-{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>')
    # shooting star
    o.append(f'<g opacity="0"><line x1="0" y1="0" x2="-46" y2="-18" stroke="url(#aurora)" stroke-width="1.6" stroke-linecap="round"/>'
             f'<animateTransform attributeName="transform" type="translate" values="300 40;520 128" dur="1.1s" begin="3s;11s;19s;27s" repeatCount="1" additive="replace"/>'
             f'<animate attributeName="opacity" values="0;1;0" dur="1.1s" begin="3s;11s;19s;27s"/></g>')
    # cloud layers (back -> front)
    o.append(cloud_layer(rnd, 128, 1.9, .10, 150, 3, "url(#cl1)"))
    o.append(cloud_layer(rnd, 222, 1.35, .16, 100, 4, "url(#cl1)"))
    o.append(mesh_cluster(rnd))
    o.append(cloud_layer(rnd, 318, 1.1, .20, 70, 5, "url(#cl1)"))

    # wave
    o.append(f'<path d="{area}" fill="url(#waveFill)" opacity=".9"/>')
    o.append(f'<path d="{line}" fill="none" stroke="url(#wave)" stroke-width="2.4" stroke-linecap="round" filter="url(#glow)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
             f'<animate attributeName="stroke-dashoffset" values="1;0" dur="2.6s" begin=".4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1"/></path>')
    o.append(f'<circle r="4" fill="#fff" filter="url(#glow)"><animateMotion path="{line}" dur="9s" begin="3s" repeatCount="indefinite"/></circle>')
    # racks
    o.append(racks(rnd))

    # --- text block ---
    o.append(f'<clipPath id="tp"><rect x="44" y="66" width="0" height="26"><animate attributeName="width" values="0;12;24;36;52;70;88;104;124;140;160;180;200;220;250;280;310;330" dur="2.4s" begin=".3s" fill="freeze"/></rect></clipPath>')
    o.append(f'<g clip-path="url(#tp)"><text x="44" y="84" class="mono" font-size="13"><tspan fill="{t.TEAL}">swastik</tspan><tspan fill="{t.TEXT3}">@</tspan><tspan fill="{t.SKY}">cloud</tspan><tspan fill="{t.TEXT3}">:~$ </tspan><tspan fill="{t.TEXT2}">./deploy --profile</tspan></text></g>')
    o.append(f'<rect x="323" y="73" width="8" height="15" fill="{t.SKY}" opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.5;.51;1" dur="1.1s" begin="2.7s" repeatCount="indefinite"/></rect>')
    o.append(f'<text x="40" y="166" font-size="72" font-weight="800" letter-spacing="-3" fill="url(#nameg)" opacity="0">{escape(NAME)}'
             f'<animate attributeName="opacity" values="0;1" dur=".9s" begin=".9s" fill="freeze"/></text>')
    o.append(f'<text x="44" y="200" font-size="12" class="mono" fill="{t.TEXT3}" letter-spacing=".22em" opacity="0">CLOUD COMPUTING  /  DEVOPS  /  DISTRIBUTED SYSTEMS<animate attributeName="opacity" values="0;1" dur=".8s" begin="1.5s" fill="freeze"/></text>')
    n = len(ROLES)
    s = 1.0 / n
    for i, role in enumerate(ROLES):
        a = i * s
        wmax = 420
        keys = [0, a, a + .30 * s, a + .88 * s, a + s, 1.0]
        keys = [min(1.0, k) for k in keys]
        vals = [0, 0, wmax, wmax, 0, 0]
        kt = ";".join(f"{k:.4f}" for k in keys)
        o.append(f'<clipPath id="r{i}"><rect x="44" y="214" width="0" height="30"><animate attributeName="width" values="{";".join(map(str, vals))}" keyTimes="{kt}" dur="{n * 4.4}s" begin="1.8s" repeatCount="indefinite"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#r{i})"><text x="44" y="238" font-size="23" font-weight="600" fill="{t.TEXT}">{escape(role)}</text></g>')

    # chips
    chips = [(t.GREEN, "STATUS", "ONLINE"), (t.SKY, "LAST DEPLOY", escape(last)), (t.AMBER, "UPTIME", f"{streak}d streak"), (t.VIOLET, "TRAFFIC 52W", f"{total:,}")]
    x = 44
    for k, (col, k1, v1) in enumerate(chips):
        w = 26 + 7.1 * len(k1) + 7.6 * len(v1) + 10
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" begin="{2.0 + k * .18:.2f}s" fill="freeze"/>'
                 f'<rect x="{x}" y="266" width="{w:.0f}" height="30" rx="15" fill="#06182b" fill-opacity=".82" stroke="{col}" stroke-opacity=".55"/>'
                 f'<circle cx="{x + 15}" cy="281" r="3.4" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="{2 + k * .4:.1f}s" repeatCount="indefinite"/></circle>'
                 f'<text x="{x + 26}" y="285" class="mono" font-size="10" letter-spacing=".1em" fill="{t.TEXT3}">{k1}</text>'
                 f'<text x="{x + 26 + 7.1 * len(k1) + 8:.0f}" y="285" class="mono" font-size="11.5" font-weight="700" fill="{t.TEXT}">{v1}</text></g>')
        x += w + 10
        if x > W - 110:
            break
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    return o


def divider(num, label):
    rnd = random.Random(num)
    H2 = 56
    lw = 40 + 8.9 * len(label) + 34
    x0, x1 = 44 + lw, W - 44
    y = 30
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H2}" width="{W}" height="{H2}" role="presentation" aria-hidden="true">',
         f'<defs><linearGradient id="dl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.TEAL}"/><stop offset=".5" stop-color="{t.SKY}"/><stop offset="1" stop-color="{t.VIOLET}"/></linearGradient>'
         f'<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
         f'<rect x="44" y="12" width="{lw - 14:.0f}" height="36" rx="18" fill="{t.SURFACE}" stroke="url(#dl)" stroke-opacity=".6"/>',
         f'<text x="64" y="35" font-family="{t.MONO}" font-size="12" font-weight="700" fill="{t.SKY}">{num}</text>',
         f'<text x="90" y="35" font-family="{t.MONO}" font-size="11" letter-spacing=".18em" fill="{t.TEXT2}">{label}</text>',
         f'<line x1="{x0:.0f}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t.HAIRLINE}" stroke-width="1.4"/>',
         f'<line x1="{x0:.0f}" y1="{y}" x2="{x1}" y2="{y}" stroke="url(#dl)" stroke-width="1.4" stroke-opacity=".55" stroke-dasharray="2 6"/>']
    nodes = 5
    DUR = 6.0
    for k in range(nodes):
        nx = x0 + (x1 - x0) * k / (nodes - 1)
        tt = k / (nodes - 1) * 0.84 + 0.02
        o.append(f'<circle cx="{nx:.0f}" cy="{y}" r="4" fill="{t.SURFACE}" stroke="{t.HAIRLINE}" stroke-width="1.4"/>'
                 f'<circle cx="{nx:.0f}" cy="{y}" r="4" fill="{t.GREEN}" opacity="0"><animate attributeName="opacity" values="0;0;1;.25;0;0" keyTimes="0;{max(0, tt - .01):.3f};{tt:.3f};{min(.97, tt + .12):.3f};{min(.98, tt + .2):.3f};1" dur="{DUR}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="r" values="4;4;7;4;4" keyTimes="0;{max(0, tt - .01):.3f};{tt:.3f};{min(.97, tt + .12):.3f};1" dur="{DUR}s" repeatCount="indefinite"/></circle>')
    for p in range(2):
        d = DUR
        o.append(f'<g filter="url(#gl)" opacity="0"><rect x="-9" y="-1.8" width="18" height="3.6" rx="1.8" fill="url(#dl)"/>'
                 f'<animateMotion path="M{x0:.0f},{y} L{x1},{y}" dur="{d}s" begin="{p * d / 2 + rnd.random() * 0:.1f}s" keyPoints="0;1" keyTimes="0;1" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.94;1" dur="{d}s" begin="{p * d / 2:.1f}s" repeatCount="indefinite"/></g>')
    o.append("</svg>")
    return o


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    u = common.user_graph(USER)
    ds = common.days(u)
    cur, _ = common.streaks(ds)
    rp = [r for r in common.repos(USER) if r["name"].lower() != USER.lower()]
    rp.sort(key=lambda r: r["pushed_at"], reverse=True)
    last = "n/a"
    if rp:
        pushed = datetime.fromisoformat(rp[0]["pushed_at"].replace("Z", "+00:00"))
        last = f"{rp[0]['name'][:18]} · {ago(now - pushed)}"
    counts = [c for _, c in ds][-364:]
    weekly = [sum(counts[i:i + 7]) for i in range(0, len(counts), 7)]
    total = sum(counts)
    t.write(os.path.join(OUTDIR, "header.svg"), header(last, cur, weekly, total))
    for fn, num, label in DIVIDERS:
        t.write(os.path.join(OUTDIR, f"{fn}.svg"), divider(num, label))
    print(f"banners: header + {len(DIVIDERS)} dividers; streak {cur}, last {last}, 52w {total}")


if __name__ == "__main__":
    main()
