#!/usr/bin/env python3
"""assets/architecture.svg: a live reference architecture.

Clients -> edge/CDN -> load balancer -> an autoscaling container tier -> data
tier, inside a VPC boundary. The container "pods" are my most recently pushed
repos (green = pushed in the last 2 weeks, amber = within 2 months). Request
packets travel the full route, replicas scale out and back in, CPU bars breathe,
and a CI/CD strip cycles beneath. Pure SMIL.
"""
import math
import random
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/architecture.svg"
W, H = 830, 480
CYCLE = 16.0


def pod_status(days):
    if days <= 14:
        return t.GREEN, "RUNNING"
    if days <= 60:
        return t.AMBER, "IDLE"
    return t.TEXT3, "STOPPED"


def main():
    now = datetime.now(timezone.utc)
    rp = [r for r in common.repos(USER) if r["name"].lower() != USER.lower()]
    rp.sort(key=lambda r: r["pushed_at"], reverse=True)
    pods = []
    for r in rp[:4]:
        d = max(0, (now - datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))).days)
        pods.append(dict(name=r["name"], lang=r["language"] or "misc", days=d))
    while len(pods) < 4:
        pods.append(dict(name="service", lang="misc", days=999))
    rnd = random.Random(11)

    X_POD, W_POD, Y0, PITCH, H_POD = 392, 188, 92, 50, 40
    pod_cy = [Y0 + i * PITCH + H_POD / 2 for i in range(6)]
    CY = (pod_cy[0] + pod_cy[5]) / 2
    clients = [(60, CY - 74), (60, CY), (60, CY + 74)]
    EDGE = (184, CY)
    LB = (298, CY)
    BUS = 622
    DATA = [(724, CY - 94), (724, CY), (724, CY + 94)]

    alt = (f"Reference cloud architecture: clients, CDN edge, load balancer, an autoscaling container tier running "
           f"{', '.join(p['name'] for p in pods)}, and a data tier, with request packets flowing through.")
    o = t.svg_open(W, H, escape(alt), "REFERENCE ARCHITECTURE")
    o.append(t.card_open(W, H, "REFERENCE ARCHITECTURE", f"{sum(1 for p in pods if p['days'] <= 14)} of 4 services live &#183; autoscaling on"))
    # grid backdrop
    for gx in range(28, W - 20, 28):
        for gy in range(64, 400, 28):
            o.append(f'<circle cx="{gx}" cy="{gy}" r=".8" fill="#ffffff" fill-opacity=".055"/>')

    # tier captions
    caps = [(60, "CLIENTS", "web · mobile"), (184, "EDGE", "CDN · TLS"), (298, "LOAD BALANCER", "L7 · health checks"),
            (X_POD, "CONTAINERS", "autoscaling group"), (724, "DATA TIER", "SQL · NoSQL · cache")]
    for x, a, b in caps:
        anchor = "start" if x == X_POD else "middle"
        o.append(f'<text x="{x}" y="70" class="label" text-anchor="{anchor}" style="fill:{t.TEXT2}">{a}</text>'
                 f'<text x="{x}" y="82" class="mono" font-size="8.5" text-anchor="{anchor}" fill="{t.TEXT3}">{b}</text>')

    # VPC boundary
    o.append(f'<rect x="372" y="94" width="436" height="302" rx="14" fill="{t.SKY}" fill-opacity=".035" stroke="{t.SKY}" stroke-opacity=".45" stroke-dasharray="5 5">'
             f'<animate attributeName="stroke-dashoffset" values="0;-20" dur="2s" repeatCount="indefinite"/></rect>')
    o.append(f'<text x="384" y="388" class="label" style="fill:{t.SKY}">VPC &#183; private subnet</text>')

    # ---- static wiring ----
    def line(a, b, op=.35):
        return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t.SKY}" stroke-opacity="{op}" stroke-width="1.2"/>'

    for c in clients:
        o.append(line((c[0] + 24, c[1]), (EDGE[0] - 24, EDGE[1])))
    o.append(line((EDGE[0] + 24, EDGE[1]), (LB[0] - 24, LB[1])))
    for i in range(6):
        x2, y2 = X_POD, pod_cy[i]
        o.append(f'<path d="M{LB[0] + 24},{LB[1]} C{LB[0] + 70},{LB[1]} {x2 - 46},{y2} {x2},{y2}" fill="none" stroke="{t.SKY}" stroke-opacity="{.35 if i < 4 else .16}" stroke-width="1.2"' + (' stroke-dasharray="3 4"' if i >= 4 else "") + '/>')
        o.append(line((X_POD + W_POD, y2), (BUS, y2), .35 if i < 4 else .16))
    o.append(f'<line x1="{BUS}" y1="{pod_cy[0]}" x2="{BUS}" y2="{pod_cy[5]}" stroke="{t.SKY}" stroke-opacity=".4" stroke-width="1.6"/>')
    for d in DATA:
        o.append(f'<path d="M{BUS},{CY} C{BUS + 30},{CY} {d[0] - 62},{d[1]} {d[0] - 34},{d[1]}" fill="none" stroke="{t.SKY}" stroke-opacity=".4" stroke-width="1.2"/>')

    # ---- nodes ----
    # clients
    for k, (x, y) in enumerate(clients):
        if k == 0:  # browser
            o.append(f'<rect x="{x - 22}" y="{y - 15}" width="44" height="30" rx="5" fill="{t.RAISED}" stroke="{t.TEAL}" stroke-width="1.3"/>'
                     f'<line x1="{x - 22}" y1="{y - 7}" x2="{x + 22}" y2="{y - 7}" stroke="{t.TEAL}" stroke-width="1"/>'
                     f'<circle cx="{x - 16}" cy="{y - 11}" r="1.4" fill="{t.TEAL}"/><circle cx="{x - 11}" cy="{y - 11}" r="1.4" fill="{t.TEAL}"/>')
        elif k == 1:  # phone
            o.append(f'<rect x="{x - 12}" y="{y - 20}" width="24" height="40" rx="5" fill="{t.RAISED}" stroke="{t.TEAL}" stroke-width="1.3"/>'
                     f'<line x1="{x - 4}" y1="{y + 14}" x2="{x + 4}" y2="{y + 14}" stroke="{t.TEAL}" stroke-width="1.4" stroke-linecap="round"/>')
        else:  # laptop
            o.append(f'<rect x="{x - 19}" y="{y - 14}" width="38" height="24" rx="3" fill="{t.RAISED}" stroke="{t.TEAL}" stroke-width="1.3"/>'
                     f'<path d="M{x - 26},{y + 15} L{x + 26},{y + 15} L{x + 20},{y + 10} L{x - 20},{y + 10} Z" fill="{t.TEAL}" fill-opacity=".5"/>')
    # edge: globe
    ex, ey = EDGE
    o.append(f'<circle cx="{ex}" cy="{ey}" r="30" fill="{t.SKY}" fill-opacity=".12" filter="url(#soft)"/>'
             f'<circle cx="{ex}" cy="{ey}" r="24" fill="{t.RAISED}" stroke="{t.SKY}" stroke-width="1.5"/>'
             f'<ellipse cx="{ex}" cy="{ey}" rx="24" ry="9" fill="none" stroke="{t.SKY}" stroke-opacity=".55"/>')
    for ph in range(3):
        vals = ";".join(f"{24 * abs(math.sin(math.radians(a + ph * 60))):.1f}" for a in range(0, 181, 15))
        o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="12" ry="24" fill="none" stroke="{t.SKY}" stroke-opacity=".6"><animate attributeName="rx" values="{vals}" dur="9s" repeatCount="indefinite"/></ellipse>')
    # load balancer: hex with arrows
    lx, ly = LB
    o.append(f'<circle cx="{lx}" cy="{ly}" r="32" fill="{t.VIOLET}" fill-opacity=".14" filter="url(#soft)"/>'
             f'<polygon points="{t.hexagon(lx, ly, 25)}" fill="{t.RAISED}" stroke="{t.VIOLET}" stroke-width="1.6"/>'
             f'<path d="M{lx - 11},{ly} L{lx + 7},{ly} M{lx + 2},{ly - 5} L{lx + 8},{ly} L{lx + 2},{ly + 5} M{lx - 11},{ly} L{lx - 4},{ly - 11} L{lx + 6},{ly - 11} M{lx - 11},{ly} L{lx - 4},{ly + 11} L{lx + 6},{ly + 11}" fill="none" stroke="{t.VIOLET}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{lx}" cy="{ly}" r="25" fill="none" stroke="{t.VIOLET}" stroke-width="1.2" opacity="0"><animate attributeName="opacity" values=".8;0" dur="2.2s" repeatCount="indefinite"/>'
             f'<animate attributeName="r" values="25;46" dur="2.2s" repeatCount="indefinite"/></circle>')

    # pods
    ghost_kt = "0;.28;.38;.78;.88;1"
    for i in range(6):
        y = Y0 + i * PITCH
        live = i < 4
        grp_open = "<g>"
        if not live:
            grp_open = f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{ghost_kt}" dur="{CYCLE}s" repeatCount="indefinite"/>'
        o.append(grp_open)
        if live:
            p = pods[i]
            col, status = pod_status(p["days"])
            o.append(f'<rect x="{X_POD}" y="{y}" width="{W_POD}" height="{H_POD}" rx="9" fill="{t.RAISED}" stroke="{col}" stroke-opacity=".6"/>'
                     f'<circle cx="{X_POD + 14}" cy="{y + 14}" r="3.6" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="{1.8 + i * .3:.1f}s" repeatCount="indefinite"/></circle>'
                     f'<text x="{X_POD + 26}" y="{y + 18}" font-size="12.5" font-weight="600" fill="{t.TEXT}">{escape(p["name"][:17])}</text>'
                     f'<text x="{X_POD + W_POD - 10}" y="{y + 17}" class="mono" font-size="8.5" text-anchor="end" fill="{t.lang_color(p["lang"] if p["lang"] in t.LANG else "Other")}">{escape(p["lang"][:10])}</text>'
                     f'<rect x="{X_POD + 14}" y="{y + 28}" width="{W_POD - 28}" height="3" rx="1.5" fill="{t.HAIRLINE}"/>')
            lo, hi = rnd.uniform(.18, .4), rnd.uniform(.55, .95)
            wlo, whi = (W_POD - 28) * lo, (W_POD - 28) * hi
            o.append(f'<rect x="{X_POD + 14}" y="{y + 28}" width="{wlo:.0f}" height="3" rx="1.5" fill="{col}"><animate attributeName="width" values="{wlo:.0f};{whi:.0f};{wlo:.0f}" dur="{rnd.uniform(3, 6):.1f}s" repeatCount="indefinite"/></rect>')
            o.append(f'<text x="{X_POD + W_POD - 10}" y="{y + 36}" class="mono" font-size="7.5" text-anchor="end" fill="{t.TEXT3}">{status}</text>')
        else:
            o.append(f'<rect x="{X_POD}" y="{y}" width="{W_POD}" height="{H_POD}" rx="9" fill="{t.TEAL}" fill-opacity=".06" stroke="{t.TEAL}" stroke-opacity=".8" stroke-dasharray="4 3"/>'
                     f'<text x="{X_POD + 14}" y="{y + 24}" class="mono" font-size="10.5" fill="{t.TEAL}">+ replica {i - 3}</text>'
                     f'<text x="{X_POD + W_POD - 10}" y="{y + 24}" class="mono" font-size="8.5" text-anchor="end" fill="{t.TEXT3}">scaling out</text>')
        o.append("</g>")
    # autoscaler readout
    o.append(f'<g class="mono"><text x="{BUS + 22}" y="{Y0 - 6}" font-size="9.5" fill="{t.TEAL}" letter-spacing=".08em">REPLICAS</text>'
             f'<text x="{BUS + 88}" y="{Y0 - 6}" font-size="12" font-weight="700" fill="{t.TEXT}" opacity="1">4<animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="{ghost_kt}" dur="{CYCLE}s" repeatCount="indefinite"/></text>'
             f'<text x="{BUS + 88}" y="{Y0 - 6}" font-size="12" font-weight="700" fill="{t.TEAL}" opacity="0">6<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{ghost_kt}" dur="{CYCLE}s" repeatCount="indefinite"/></text></g>')

    # data tier
    dx, dy = DATA[0]  # database cylinder
    o.append(f'<ellipse cx="{dx}" cy="{dy}" rx="40" ry="38" fill="{t.AMBER}" fill-opacity=".08" filter="url(#soft)"/>'
             f'<path d="M{dx - 26},{dy - 18} L{dx - 26},{dy + 18} A26,9 0 0 0 {dx + 26},{dy + 18} L{dx + 26},{dy - 18}" fill="{t.RAISED}" stroke="{t.AMBER}" stroke-width="1.5"/>'
             f'<ellipse cx="{dx}" cy="{dy - 18}" rx="26" ry="9" fill="{t.RAISED}" stroke="{t.AMBER}" stroke-width="1.5"/>'
             f'<path d="M{dx - 26},{dy - 2} A26,9 0 0 0 {dx + 26},{dy - 2} M{dx - 26},{dy + 8} A26,9 0 0 0 {dx + 26},{dy + 8}" fill="none" stroke="{t.AMBER}" stroke-opacity=".6"/>')
    for k in range(3):
        o.append(f'<circle cx="{dx + 16}" cy="{dy - 8 + k * 10}" r="1.5" fill="{t.GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="{1.1 + k * .5:.1f}s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{dx}" y="{dy + 50}" class="label" text-anchor="middle" style="fill:{t.AMBER}">DATABASE</text>')
    cx_, cy_ = DATA[1]  # cache: hex w/ bolt
    o.append(f'<polygon points="{t.hexagon(cx_, cy_, 26)}" fill="{t.RAISED}" stroke="{t.ROSE}" stroke-width="1.5"/>'
             f'<path d="M{cx_ + 3},{cy_ - 13} L{cx_ - 8},{cy_ + 2} L{cx_ - 1},{cy_ + 2} L{cx_ - 4},{cy_ + 13} L{cx_ + 8},{cy_ - 3} L{cx_ + 1},{cy_ - 3} Z" fill="{t.ROSE}" fill-opacity=".9"><animate attributeName="fill-opacity" values=".4;1;.4" dur="1.4s" repeatCount="indefinite"/></path>'
             f'<text x="{cx_}" y="{cy_ + 46}" class="label" text-anchor="middle" style="fill:{t.ROSE}">CACHE</text>')
    sx, sy = DATA[2]  # object store: stacked layers
    for k in range(3):
        o.append(f'<path d="M{sx - 26},{sy - 8 + k * 9} L{sx},{sy - 18 + k * 9} L{sx + 26},{sy - 8 + k * 9} L{sx},{sy + 2 + k * 9} Z" fill="{t.RAISED}" stroke="{t.TEAL}" stroke-width="1.4" stroke-opacity="{1 - k * .22:.2f}"/>')
    o.append(f'<text x="{sx}" y="{sy + 46}" class="label" text-anchor="middle" style="fill:{t.TEAL}">OBJECT STORE</text>')

    # ---- request packets ----
    def route(ci, pi, di):
        c, p, d = clients[ci], pod_cy[pi], DATA[di]
        return (f"M{c[0] + 24},{c[1]} L{EDGE[0] - 24},{EDGE[1]} L{EDGE[0] + 24},{EDGE[1]} L{LB[0] - 24},{LB[1]} "
                f"L{LB[0] + 24},{LB[1]} C{LB[0] + 70},{LB[1]} {X_POD - 46},{p} {X_POD},{p} L{X_POD + W_POD},{p} L{BUS},{p} L{BUS},{CY} "
                f"C{BUS + 30},{CY} {d[0] - 62},{d[1]} {d[0] - 34},{d[1]}")

    combos = [(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 3, 1), (1, 2, 0), (2, 1, 1), (0, 1, 2), (1, 3, 0), (2, 0, 1), (1, 0, 2)]
    cols = [t.TEAL, t.SKY, t.VIOLET, t.TEXT]
    for n, (ci, pi, di) in enumerate(combos + [(0, 4, 0), (1, 5, 1), (2, 4, 2), (1, 5, 0)]):
        ghost = pi >= 4
        dur = 6.0 + rnd.uniform(-.8, 1.4)
        begin = -rnd.uniform(0, dur)
        pk = (f'<circle r="2.6" fill="{cols[n % 4]}" filter="url(#glow)" opacity="0"><animateMotion path="{route(ci, pi, di)}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.95;1" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>')
        if ghost:
            pk = f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{ghost_kt}" dur="{CYCLE}s" repeatCount="indefinite"/>{pk}</g>'
        o.append(pk)

    # ---- CI/CD strip ----
    stages = ["COMMIT", "BUILD", "TEST", "CONTAINER", "DEPLOY", "MONITOR"]
    y = 424
    sw = 112
    gap = (W - 56 - sw * len(stages)) / (len(stages) - 1)
    o.append(f'<text x="28" y="{y - 12}" class="label" style="fill:{t.TEXT2}">CI / CD PIPELINE</text>')
    ST = 12.0
    for k, s in enumerate(stages):
        x = 28 + k * (sw + gap)
        a = k / len(stages)
        keys = f"0;{a:.3f};{a + .02:.3f};{a + .14:.3f};{a + .16:.3f};1" if k < len(stages) - 1 else f"0;{a:.3f};{a + .02:.3f};.97;1;1"
        o.append(f'<rect x="{x:.0f}" y="{y}" width="{sw}" height="30" rx="15" fill="{t.RAISED}" stroke="{t.HAIRLINE}"/>'
                 f'<rect x="{x:.0f}" y="{y}" width="{sw}" height="30" rx="15" fill="{t.GREEN}" fill-opacity="0" stroke="{t.GREEN}"><animate attributeName="fill-opacity" values="0;0;.22;.22;0;0" keyTimes="{keys}" dur="{ST}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-opacity" values="0;0;1;1;0;0" keyTimes="{keys}" dur="{ST}s" repeatCount="indefinite"/></rect>'
                 f'<text x="{x + sw / 2:.0f}" y="{y + 19}" class="mono" font-size="10" letter-spacing=".12em" text-anchor="middle" fill="{t.TEXT}">{s}</text>')
        if k < len(stages) - 1:
            ax = x + sw + 3
            o.append(f'<path d="M{ax:.0f},{y + 15} L{ax + gap - 6:.0f},{y + 15} M{ax + gap - 11:.0f},{y + 10} L{ax + gap - 5:.0f},{y + 15} L{ax + gap - 11:.0f},{y + 20}" fill="none" stroke="{t.TEXT3}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: pods {[p['name'] for p in pods]}")


if __name__ == "__main__":
    main()
