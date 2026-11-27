#!/usr/bin/env python3
"""assets/deploy.svg: a deployment log for my active repos.

One lane per repo (most recently pushed first). Each bubble is a 6-hour window
over the last two weeks; bigger bubble = more pushes (deploys). Bubbles pop in
as a scan beam passes, a rolling trace joins the active windows, and the newest
push in every lane sends out a ring. Built from the public events feed.
Pure SMIL.
"""
import math
import sys
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/deploy.svg"
DAYS, BIN_H, LANES = 30, 12, 8
W = 830
LX, RX = 226, 776
PITCH, TOPY = 46, 98
DUR = 14.0


def ago(td):
    h = td.total_seconds() / 3600
    if h < 1:
        return "just now"
    if h < 24:
        return f"{int(h)}h ago"
    return f"{int(h // 24)}d ago"


def main():
    now = datetime.now(timezone.utc)
    evs = common.push_events(USER)
    repos = {r["name"]: r for r in common.repos(USER)}
    start = now - timedelta(days=DAYS)
    evs = [(n, d) for n, d in evs if d >= start and n in repos and n.lower() != USER.lower()]
    nb = DAYS * 24 // BIN_H
    per, last = {}, {}
    for n, d in evs:
        b = min(nb - 1, int((d - start).total_seconds() / (BIN_H * 3600)))
        per.setdefault(n, [0] * nb)[b] += 1
        last[n] = max(last.get(n, d), d)
    names = sorted(per, key=lambda n: last[n], reverse=True)[:LANES]
    H = TOPY + max(1, len(names)) * PITCH + 58
    bw = (RX - LX) / nb
    mx = max((max(per[n]) for n in names), default=1)
    total = sum(sum(per[n]) for n in names)

    alt = (f"Deployment log: push activity for the {len(names)} most recently active repositories over the last {DAYS} days. "
           + "; ".join(f"{n}: {sum(per[n])} pushes, last {ago(now - last[n])}" for n in names) + ".")
    o = t.svg_open(W, H, escape(alt), "DEPLOYMENT LOG")
    o.append(t.card_open(W, H, "DEPLOYMENT LOG", f"last {DAYS} days &#183; {total} deploys &#183; 12h windows"))
    if not names:
        o.append(f'<text x="{W / 2}" y="{H / 2}" font-size="{t.T_HEAD}" fill="{t.TEXT2}" text-anchor="middle">No pushes in the last {DAYS} days. The log fills as soon as I ship.</text>')
        o += ["</g>", t.card_border(W, H), "</svg>"]
        t.write(OUT, o)
        print("wrote empty-state", OUT)
        return

    # day columns
    for d in range(DAYS + 1):
        x = LX + d * 24 / BIN_H * bw
        day = start + timedelta(days=d)
        if d < DAYS and day.weekday() >= 5:
            o.append(f'<rect x="{x:.1f}" y="{TOPY - 16}" width="{24 / BIN_H * bw:.1f}" height="{len(names) * PITCH + 4}" fill="{t.VIOLET}" fill-opacity=".05"/>')
        o.append(f'<line x1="{x:.1f}" y1="{TOPY - 16}" x2="{x:.1f}" y2="{TOPY + len(names) * PITCH - 12}" stroke="{t.HAIRLINE}" stroke-opacity=".7" stroke-dasharray="1 4"/>')
        if d < DAYS and d % 3 == 0:
            o.append(f'<text x="{x + 3:.1f}" y="{TOPY - 24}" class="mono" font-size="9" fill="{t.TEXT3}">{day:%d %b}</text>')

    for li, n in enumerate(names):
        y = TOPY + li * PITCH + 16
        rep = repos[n]
        col = t.lang_color(rep["language"] if rep["language"] in t.LANG else "Other")
        age = now - last[n]
        status = t.GREEN if age.days <= 3 else (t.AMBER if age.days <= 10 else t.TEXT3)
        o.append(f'<line x1="{LX}" y1="{y}" x2="{RX}" y2="{y}" stroke="{t.HAIRLINE}"/>')
        o.append(f'<circle cx="34" cy="{y - 4}" r="4" fill="{status}"><animate attributeName="opacity" values="1;.3;1" dur="{2 + li * .3:.1f}s" repeatCount="indefinite"/></circle>')
        o.append(f'<text x="46" y="{y - 1}" font-size="{t.T_HEAD}" font-weight="600" fill="{t.TEXT}">{escape(n[:22])}</text>')
        o.append(f'<text x="46" y="{y + 14}" font-size="{t.T_CAP}" fill="{t.TEXT3}">{escape(rep["language"] or "misc")} &#183; {ago(age)}</text>')
        o.append(f'<text x="{RX + 36}" y="{y + 4}" class="mono" font-size="13" font-weight="700" fill="{t.TEXT2}" text-anchor="end">{sum(per[n])}</text>')
        newest = max(i for i, c in enumerate(per[n]) if c)
        trace = []
        for b, c in enumerate(per[n]):
            x = LX + b * bw + bw / 2
            t0 = 0.6 + (b / nb) * 7.0
            if not c:
                o.append(f'<circle cx="{x:.1f}" cy="{y}" r="1.3" fill="{t.HAIRLINE}"/>')
                continue
            r = 2.4 + 5.2 * math.sqrt(c / mx)
            trace.append((x, y))
            kt = ";".join(f"{v:.4f}" for v in (0, t0 / DUR, (t0 + .5) / DUR, 1))
            o.append(f'<circle cx="{x:.1f}" cy="{y}" r="0" fill="{col}" fill-opacity="{.45 + .45 * c / mx:.2f}" stroke="{col}" stroke-width="1"{" filter=\"url(#glow)\"" if b == newest else ""}>'
                     f'<animate attributeName="r" values="0;0;{r:.1f};{r:.1f}" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.2 1.4 .4 1;0 0 1 1"/></circle>')
        if len(trace) > 1:
            d = "M" + " L".join(f"{px:.1f},{py}" for px, py in trace)
            o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-width="1.2"/>')
        nx = LX + newest * bw + bw / 2
        o.append(f'<circle cx="{nx:.1f}" cy="{y}" r="4" fill="none" stroke="{col}" stroke-width="1.3" opacity="0"><animate attributeName="r" values="4;18" dur="2.6s" begin="{8.4 + li * .18:.2f}s;{8.4 + li * .18 + DUR:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".9;0" dur="2.6s" begin="{8.4 + li * .18:.2f}s;{8.4 + li * .18 + DUR:.2f}s" repeatCount="indefinite"/></circle>')

    # scan beam + NOW marker
    y0, y1 = TOPY - 18, TOPY + len(names) * PITCH - 8
    k = ";".join(f"{v:.4f}" for v in (0, .6 / DUR, 7.6 / DUR, 1))
    o.append(f'<rect x="{LX}" y="{y0}" width="2" height="{y1 - y0}" fill="{t.TEAL}" filter="url(#glow)" opacity="0">'
             f'<animate attributeName="x" values="{LX};{LX};{RX};{RX}" keyTimes="{k}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="{k}" dur="{DUR}s" repeatCount="indefinite"/></rect>')
    o.append(f'<line x1="{RX}" y1="{y0}" x2="{RX}" y2="{y1}" stroke="{t.AMBER}" stroke-width="1.2" stroke-dasharray="3 3"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></line>')
    o.append(f'<text x="{RX}" y="{y1 + 14}" class="label" text-anchor="middle" style="fill:{t.AMBER}">NOW</text>')
    o.append(f'<text x="{RX + 36}" y="{TOPY - 24}" class="label" text-anchor="end">DEPLOYS</text>')
    o.append(f'<text x="28" y="{H - 16}" font-size="{t.T_CAP}" fill="{t.TEXT3}">each bubble = one 12-hour window &#183; bigger = more pushes &#183; glowing = latest deploy &#183; tinted columns = weekends</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: {len(names)} lanes, {total} pushes in {DAYS}d, lanes={names}")


if __name__ == "__main__":
    main()
