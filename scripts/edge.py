#!/usr/bin/env python3
"""assets/edge.svg: a global edge network, with visitors as edge nodes.

A rotating wireframe globe with network arcs and packets. Around it, a radial
ring of 365 bars (one per day of the last year, bar length = contributions)
slowly turns under a radar sweep. Visitors who open the "add your node" issue
join as satellites orbiting the planet and are listed in the node registry.
Pure SMIL.
"""
import json
import math
import os
import random
import sys
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/edge.svg"
STARS_DB = os.environ.get("STARS_DB") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stars", "visitors.json")
W, H = 830, 520
CX, CY, R = 250, 282, 112
MAX_LIST = 8


def load_visitors():
    try:
        with open(STARS_DB, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def main():
    u = common.user_graph(USER)
    ds = common.days(u)[-365:]
    mx = max((c for _, c in ds), default=1) or 1
    total = sum(c for _, c in ds)
    visitors = load_visitors()
    rnd = random.Random(99)

    alt = (f"Global edge network: a rotating globe ringed by 365 bars for the last year of contributions ({total} total), "
           f"with {len(visitors)} visitor nodes orbiting it.")
    o = t.svg_open(W, H, escape(alt), "GLOBAL EDGE NETWORK",
                   f'<radialGradient id="sph" cx=".38" cy=".32" r=".85"><stop offset="0" stop-color="#1b5a8a"/><stop offset=".55" stop-color="#0b2a4a"/><stop offset="1" stop-color="#04101f"/></radialGradient>'
                   f'<radialGradient id="atm" cx=".5" cy=".5" r=".5"><stop offset=".82" stop-color="{t.SKY}" stop-opacity=".0"/><stop offset=".93" stop-color="{t.SKY}" stop-opacity=".30"/><stop offset="1" stop-color="{t.SKY}" stop-opacity="0"/></radialGradient>'
                   f'<linearGradient id="radar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.TEAL}" stop-opacity="0"/><stop offset="1" stop-color="{t.TEAL}" stop-opacity=".42"/></linearGradient>'
                   f'<clipPath id="globe"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>')
    o.append(t.card_open(W, H, "GLOBAL EDGE", f"{len(visitors)} visitor nodes online"))
    for gx in range(28, 500, 28):
        for gy in range(64, H - 20, 28):
            o.append(f'<circle cx="{gx}" cy="{gy}" r=".8" fill="#ffffff" fill-opacity=".05"/>')

    # ---- ring of 365 days (rotating) ----
    r0 = R + 26
    o.append(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="120s" repeatCount="indefinite"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{r0 - 4}" fill="none" stroke="{t.HAIRLINE}" stroke-width="1"/>')
    n = len(ds)
    for i, (_, c) in enumerate(ds):
        ang = math.radians(-90 + 360 * i / n)
        ln = 2 + 34 * (c / mx) ** .7 if c else 2
        col = t.ramp(.2 + .8 * (c / mx) ** .6) if c else "#12304f"
        x1, y1 = CX + r0 * math.cos(ang), CY + r0 * math.sin(ang)
        x2, y2 = CX + (r0 + ln) * math.cos(ang), CY + (r0 + ln) * math.sin(ang)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>')
    o.append("</g>")
    # radar sweep wedge
    wr = r0 + 40
    a1 = math.radians(-34)
    o.append(f'<g opacity=".9"><path d="M{CX},{CY} L{CX + wr},{CY} A{wr},{wr} 0 0 0 {CX + wr * math.cos(a1):.1f},{CY + wr * math.sin(a1):.1f} Z" fill="url(#radar)" clip-path="none"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="9s" repeatCount="indefinite"/></g>')

    # ---- globe ----
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R + 24}" fill="url(#atm)"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#sph)"/>')
    o.append('<g clip-path="url(#globe)">')
    for lat in (-60, -30, 0, 30, 60):
        ry = R * math.cos(math.radians(lat))
        y = CY - R * math.sin(math.radians(lat))
        o.append(f'<ellipse cx="{CX}" cy="{y:.1f}" rx="{ry:.1f}" ry="{ry * .16:.1f}" fill="none" stroke="{t.SKY}" stroke-opacity=".3" stroke-width=".9"/>')
    for k in range(6):
        vals = ";".join(f"{R * abs(math.sin(math.radians(a + k * 30))):.1f}" for a in range(0, 181, 10))
        o.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{R * abs(math.sin(math.radians(k * 30))):.1f}" ry="{R}" fill="none" stroke="{t.SKY}" stroke-opacity=".34" stroke-width=".9">'
                 f'<animate attributeName="rx" values="{vals}" dur="30s" repeatCount="indefinite"/></ellipse>')
    o.append("</g>")
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{t.SKY}" stroke-opacity=".6" stroke-width="1.2"/>')
    # edge PoPs + arcs
    pops = [(-.52, -.30), (-.18, -.62), (.34, -.50), (.60, -.08), (.28, .38), (-.30, .46), (-.64, .12), (.06, .08)]
    pts = [(CX + R * px, CY + R * py) for px, py in pops]
    home = pts[-1]
    for i, p in enumerate(pts[:-1]):
        mxp, myp = (p[0] + home[0]) / 2, (p[1] + home[1]) / 2
        dx, dy = mxp - CX, myp - CY
        d = math.hypot(dx, dy) or 1
        cxp, cyp = mxp + dx / d * 30, myp + dy / d * 30 - 14
        path = f"M{p[0]:.1f},{p[1]:.1f} Q{cxp:.1f},{cyp:.1f} {home[0]:.1f},{home[1]:.1f}"
        o.append(f'<path d="{path}" fill="none" stroke="{t.TEAL}" stroke-opacity=".5" stroke-width="1" stroke-dasharray="3 4"><animate attributeName="stroke-dashoffset" values="0;-28" dur="2.2s" repeatCount="indefinite"/></path>')
        dur = 2.6 + i * .4
        o.append(f'<circle r="2.4" fill="#fff" filter="url(#glow)" opacity="0"><animateMotion path="{path}" dur="{dur:.1f}s" begin="-{i * .7:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="{dur:.1f}s" begin="-{i * .7:.1f}s" repeatCount="indefinite"/></circle>')
        o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.8" fill="{t.SKY}"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3" fill="none" stroke="{t.SKY}" opacity="0"><animate attributeName="r" values="3;12" dur="2.8s" begin="{i * .35:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.8s" begin="{i * .35:.2f}s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="{home[0]:.1f}" cy="{home[1]:.1f}" r="5" fill="{t.AMBER}" filter="url(#glow)"/>')
    for k in range(2):
        o.append(f'<circle cx="{home[0]:.1f}" cy="{home[1]:.1f}" r="5" fill="none" stroke="{t.AMBER}" stroke-width="1.3" opacity="0"><animate attributeName="r" values="5;26" dur="2.8s" begin="{k * 1.4}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="2.8s" begin="{k * 1.4}s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{home[0] + 9:.0f}" y="{home[1] - 8:.0f}" class="mono" font-size="8.5" fill="{t.AMBER}" stroke="#04101f" stroke-width="2.5" paint-order="stroke">ORIGIN</text>')

    # ---- orbiting visitor satellites ----
    rx, ry, tilt = 214, 62, -22
    orbit = f"M{CX - rx},{CY} A{rx},{ry} 0 1 0 {CX + rx},{CY} A{rx},{ry} 0 1 0 {CX - rx},{CY}"
    o.append(f'<g transform="rotate({tilt} {CX} {CY})"><path d="{orbit}" fill="none" stroke="{t.VIOLET}" stroke-opacity=".35" stroke-dasharray="2 6"/>')
    shown = visitors[::-1][:12]
    for k, v in enumerate(shown):
        col = t.VISITOR.get(v.get("color"), t.SKY)
        dur = 34 + (k % 4) * 7
        o.append(f'<g><circle r="9" fill="{col}" fill-opacity=".18" filter="url(#soft)"/><circle r="3.6" fill="{col}" filter="url(#glow)"/>'
                 f'<animateMotion path="{orbit}" dur="{dur}s" begin="-{k * dur / max(1, len(shown)):.1f}s" repeatCount="indefinite"/></g>')
    o.append("</g>")

    # ---- registry panel ----
    PX, PW = 520, W - 28 - 520
    o.append(f'<rect x="{PX}" y="66" width="{PW}" height="{H - 66 - 24}" rx="14" fill="{t.RAISED}" fill-opacity=".7" stroke="{t.HAIRLINE}"/>')
    o.append(f'<text x="{PX + 18}" y="92" class="label" style="fill:{t.TEXT2}">EDGE NODE REGISTRY</text>'
             f'<text x="{PX + PW - 18}" y="92" class="mono" font-size="10" fill="{t.GREEN}" text-anchor="end">{len(visitors)} online</text>'
             f'<line x1="{PX + 18}" y1="102" x2="{PX + PW - 18}" y2="102" stroke="{t.HAIRLINE}"/>')
    row = 31
    if not shown:
        o.append(f'<text x="{PX + PW / 2}" y="190" font-size="13" fill="{t.TEXT2}" text-anchor="middle">No visitor nodes yet.</text>'
                 f'<text x="{PX + PW / 2}" y="210" font-size="11" fill="{t.TEXT3}" text-anchor="middle">Be the first to join the network.</text>')
    for i, v in enumerate(shown[:MAX_LIST]):
        y = 112 + i * row
        col = t.VISITOR.get(v.get("color"), t.SKY)
        login = escape(str(v.get("login", ""))[:20])
        msg = escape(str(v.get("msg", ""))[:30])
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="{.3 + i * .12:.2f}s" fill="freeze"/>'
                 f'<rect x="{PX + 10}" y="{y}" width="{PW - 20}" height="{row - 5}" rx="8" fill="{col}" fill-opacity="0"><animate attributeName="fill-opacity" values="0;0;.10;0;0" keyTimes="0;{i / (MAX_LIST + 1):.3f};{(i + .5) / (MAX_LIST + 1):.3f};{(i + 1) / (MAX_LIST + 1):.3f};1" dur="9s" begin="1s" repeatCount="indefinite"/></rect>'
                 f'<circle cx="{PX + 26}" cy="{y + 12}" r="4" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="{1.6 + i * .2:.1f}s" repeatCount="indefinite"/></circle>'
                 f'<text x="{PX + 38}" y="{y + 11}" font-size="11.5" font-weight="700" fill="{t.TEXT}">@{login}</text>'
                 f'<text x="{PX + 38}" y="{y + 22}" class="mono" font-size="8.5" fill="{t.TEXT3}">{msg}</text>'
                 f'<text x="{PX + PW - 18}" y="{y + 12}" class="mono" font-size="8.5" fill="{t.TEXT3}" text-anchor="end">{escape(str(v.get("date", "")))}</text></g>')
    more = len(visitors) - MAX_LIST
    if more > 0:
        o.append(f'<text x="{PX + PW / 2}" y="{112 + MAX_LIST * row + 8}" class="mono" font-size="9" fill="{t.TEXT3}" text-anchor="middle">+ {more} more orbiting</text>')
    # CTA
    cy_ = H - 24 - 52
    o.append(f'<rect x="{PX + 18}" y="{cy_}" width="{PW - 36}" height="34" rx="17" fill="none" stroke="url(#aurora)" stroke-width="1.5"/>'
             f'<rect x="{PX + 18}" y="{cy_}" width="{PW - 36}" height="34" rx="17" fill="{t.SKY}" fill-opacity="0"><animate attributeName="fill-opacity" values="0;.14;0" dur="3s" repeatCount="indefinite"/></rect>'
             f'<text x="{PX + PW / 2}" y="{cy_ + 21}" class="mono" font-size="11" letter-spacing=".1em" fill="{t.TEXT}" text-anchor="middle">+ ADD YOUR NODE</text>')
    # legend bottom-left
    o.append(f'<text x="28" y="{H - 14}" class="mono" font-size="9" fill="{t.TEXT3}">outer ring: last 365 days of commits &#183; longer bar = busier day &#183; {total:,} total</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: {len(visitors)} visitors, 365-day ring total {total}")


if __name__ == "__main__":
    main()
