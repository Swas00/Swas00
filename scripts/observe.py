#!/usr/bin/env python3
"""assets/observe.svg: an observability dashboard built from my GitHub activity.

  * requests/day  : 365 days of contributions as a smoothed time series with an
                    average ("SLO") line, a live scan cursor and a peak marker
  * traffic/hour  : when in the day I push code (public events feed)
  * heatmap       : 52 weeks x 7 days, with a light wave sweeping through it
Pure SMIL.
"""
import sys
from datetime import date
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/observe.svg"
W, H = 830, 486
TZ = 330  # minutes east of UTC used for the hour histogram
PERIODS = [("NIGHT", range(0, 6), t.VIOLET), ("MORNING", range(6, 12), t.TEAL), ("DAY", range(12, 18), t.SKY), ("EVENING", range(18, 24), t.PINK)]


def hour_col(h):
    for _, rg, col in PERIODS:
        if h in rg:
            return col
    return t.SKY


def main():
    u = common.user_graph(USER)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"][-52:]
    grid = [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]
    dates = [[d["date"] for d in w["contributionDays"]] for w in weeks]
    flat = [(dt, c) for wd, wc in zip(dates, grid) for dt, c in zip(wd, wc)]
    counts = [c for _, c in flat]
    total = sum(counts)
    active = sum(1 for c in counts if c)
    peak_i = max(range(len(counts)), key=lambda i: counts[i])
    peak = counts[peak_i]
    avg_active = total / active if active else 0
    cur, longest = common.streaks(flat)
    hist, npush = common.push_hours(USER, tz_minutes=TZ)

    alt = (f"Observability dashboard: {total} contributions in the last year across {active} active days, "
           f"busiest day {peak}, current streak {cur} days; pushes by hour from {npush} recent events; and a 52 week heatmap.")
    o = t.svg_open(W, H, escape(alt), "OBSERVABILITY")
    o.append(t.card_open(W, H, "OBSERVABILITY", f"last 52 weeks &#183; {total:,} requests"))

    # ---- stat row ----
    stats = [("REQUESTS", f"{total:,}", t.SKY), ("PEAK / DAY", str(peak), t.AMBER), ("AVG / ACTIVE DAY", f"{avg_active:.1f}", t.TEAL),
             ("UPTIME", f"{round(100 * active / max(1, len(counts)))}%", t.GREEN), ("LONGEST RUN", f"{longest}d", t.VIOLET)]
    sw = (W - 56 - 4 * 10) / 5
    for i, (lab, val, col) in enumerate(stats):
        x = 28 + i * (sw + 10)
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="{.1 + i * .1:.1f}s" fill="freeze"/>'
                 f'<rect x="{x:.0f}" y="62" width="{sw:.0f}" height="54" rx="12" fill="{t.RAISED}"/>'
                 f'<rect x="{x:.0f}" y="62" width="3" height="54" rx="1.5" fill="{col}"/>'
                 f'<text x="{x + 16:.0f}" y="82" class="label">{lab}</text>'
                 f'<text x="{x + 16:.0f}" y="107" font-size="23" font-weight="800" fill="{t.TEXT}" letter-spacing="-.5">{val}</text></g>')

    # ---- time series panel ----
    PX0, PX1, PY0, PY1 = 28, 566, 150, 296
    o.append(f'<text x="{PX0}" y="138" class="label" style="fill:{t.TEXT2}">REQUESTS / DAY</text>'
             f'<text x="{PX1}" y="138" class="label" text-anchor="end">7-day avg</text>')
    n = len(counts)
    ma = []
    for i in range(n):
        lo, hi = max(0, i - 3), min(n, i + 4)
        ma.append(sum(counts[lo:hi]) / (hi - lo))
    ymax = max(max(ma), 1) * 1.15
    pw = PX1 - PX0
    X = lambda i: PX0 + pw * i / (n - 1)
    Y = lambda v: PY1 - (PY1 - PY0) * v / ymax
    for k in range(5):
        gy = PY0 + (PY1 - PY0) * k / 4
        o.append(f'<line x1="{PX0}" y1="{gy:.1f}" x2="{PX1}" y2="{gy:.1f}" stroke="{t.HAIRLINE}" stroke-opacity=".7" stroke-dasharray="2 4"/>')
    for k in range(0, 13):
        i = min(n - 1, int(k * (n - 1) / 12))
        o.append(f'<line x1="{X(i):.1f}" y1="{PY1}" x2="{X(i):.1f}" y2="{PY1 + 4}" stroke="{t.HAIRLINE}"/>')
        if k % 2 == 0:
            d = date.fromisoformat(flat[i][0])
            o.append(f'<text x="{X(i):.1f}" y="{PY1 + 16}" class="mono" font-size="8.5" fill="{t.TEXT3}" text-anchor="middle">{d:%b}</text>')
    # raw bars (faint)
    for i, c in enumerate(counts):
        if c:
            yy = Y(min(c, ymax * .98))
            o.append(f'<rect x="{X(i) - .5:.1f}" y="{yy:.1f}" width="1.1" height="{PY1 - yy:.1f}" fill="{t.SKY}" fill-opacity=".2"/>')
    pts = [(X(i), Y(ma[i])) for i in range(0, n, 3)] + [(X(n - 1), Y(ma[-1]))]
    line = t.smooth(pts)
    area = f"{line} L{PX1},{PY1} L{PX0},{PY1} Z"
    o.append(f'<clipPath id="reveal"><rect x="{PX0}" y="{PY0 - 10}" width="0" height="{PY1 - PY0 + 20}"><animate attributeName="width" values="0;{pw}" dur="2.2s" begin=".3s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".25 .7 .25 1"/></rect></clipPath>')
    o.append(f'<g clip-path="url(#reveal)"><path d="{area}" fill="url(#fadeV)"/><path d="{line}" fill="none" stroke="url(#aurora)" stroke-width="2.2" stroke-linejoin="round" filter="url(#glow)"/></g>')
    # SLO / average line
    mean = total / n
    o.append(f'<line x1="{PX0}" y1="{Y(mean):.1f}" x2="{PX1}" y2="{Y(mean):.1f}" stroke="{t.AMBER}" stroke-opacity=".8" stroke-dasharray="5 4"/>'
             f'<text x="{PX1 - 4}" y="{Y(mean) - 5:.1f}" class="mono" font-size="8.5" fill="{t.AMBER}" text-anchor="end">avg {mean:.1f}/day</text>')
    # peak marker
    px, py = X(peak_i), Y(ma[peak_i])
    o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{t.SURFACE}" stroke="{t.PINK}" stroke-width="2"/>'
             f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="none" stroke="{t.PINK}" opacity="0"><animate attributeName="r" values="4;16" dur="2.4s" begin="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="2.4s" begin="2.4s" repeatCount="indefinite"/></circle>'
             f'<text x="{min(max(px, PX0 + 40), PX1 - 40):.1f}" y="{max(py - 12, PY0 - 2):.1f}" class="mono" font-size="9" fill="{t.PINK}" text-anchor="middle">peak {peak}</text>')
    # scan cursor + dot riding the line
    DUR = 9
    o.append(f'<line x1="{PX0}" y1="{PY0 - 6}" x2="{PX0}" y2="{PY1}" stroke="{t.TEXT}" stroke-opacity=".5" stroke-width="1" stroke-dasharray="2 3" opacity="0">'
             f'<animate attributeName="x1" values="{PX0};{PX1}" dur="{DUR}s" begin="2.6s" repeatCount="indefinite"/><animate attributeName="x2" values="{PX0};{PX1}" dur="{DUR}s" begin="2.6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.96;1" dur="{DUR}s" begin="2.6s" repeatCount="indefinite"/></line>')
    o.append(f'<circle r="4.5" fill="#fff" filter="url(#glow)" opacity="0"><animateMotion path="{line}" dur="{DUR}s" begin="2.6s" repeatCount="indefinite" calcMode="linear"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.96;1" dur="{DUR}s" begin="2.6s" repeatCount="indefinite"/></circle>')

    # ---- hour histogram ----
    HX0, HX1 = 604, W - 28
    o.append(f'<text x="{HX0}" y="138" class="label" style="fill:{t.TEXT2}">TRAFFIC / HOUR</text>'
             f'<text x="{HX1}" y="138" class="label" text-anchor="end">UTC+5:30</text>')
    bw = (HX1 - HX0) / 24
    if npush:
        hm = max(hist)
        pk = hist.index(hm)
        for h in range(24):
            c = hist[h]
            hh = 4 + (PY1 - PY0 - 14) * (c / hm) ** .8 if c else 2
            x = HX0 + h * bw
            col = hour_col(h)
            o.append(f'<rect x="{x + 1:.1f}" y="{PY1:.1f}" width="{bw - 2:.1f}" height="0" rx="2" fill="{col}" fill-opacity="{.5 + .5 * c / hm:.2f}"{" filter=\"url(#glow)\"" if h == pk else ""}>'
                     f'<animate attributeName="height" from="0" to="{hh:.1f}" dur=".7s" begin="{.5 + h * .04:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'
                     f'<animate attributeName="y" from="{PY1}" to="{PY1 - hh:.1f}" dur=".7s" begin="{.5 + h * .04:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>')
            if h % 6 == 0:
                o.append(f'<text x="{x + bw / 2:.1f}" y="{PY1 + 16}" class="mono" font-size="8.5" fill="{t.TEXT3}" text-anchor="middle">{h:02d}h</text>')
        o.append(f'<text x="{HX0 + pk * bw + bw / 2:.1f}" y="{PY1 - (PY1 - PY0 - 14) - 12:.1f}" class="mono" font-size="9" fill="{hour_col(pk)}" text-anchor="middle">peak {pk:02d}:00</text>')
    else:
        o.append(f'<text x="{(HX0 + HX1) / 2}" y="{(PY0 + PY1) / 2}" font-size="12" fill="{t.TEXT3}" text-anchor="middle">no recent pushes in the public feed</text>')
    lx = HX0
    for name, _, col in PERIODS:
        o.append(f'<circle cx="{lx + 3}" cy="{PY1 + 33}" r="3" fill="{col}"/><text x="{lx + 10}" y="{PY1 + 36}" class="mono" font-size="8" fill="{t.TEXT3}">{name}</text>')
        lx += 10 + 6.2 * len(name) + 10

    # ---- heatmap ----
    GY0, GX0 = 352, 28
    cell = (W - 56) / 52
    o.append(f'<text x="{GX0}" y="{GY0 - 12}" class="label" style="fill:{t.TEXT2}">REQUEST HEATMAP</text>')
    mx = max(max(counts), 1)
    last_m, last_x = None, -99
    for wi, (wd, wc) in enumerate(zip(dates, grid)):
        m = date.fromisoformat(wd[0]).strftime("%b")
        if m != last_m:
            if GX0 + wi * cell - last_x >= 30:
                o.append(f'<text x="{GX0 + wi * cell:.1f}" y="{GY0 - 2}" class="mono" font-size="8" fill="{t.TEXT3}">{m}</text>')
                last_x = GX0 + wi * cell
            last_m = m
        for di, c in enumerate(wc):
            x, y = GX0 + wi * cell, GY0 + 6 + di * (cell * .72)
            col = t.ramp(.18 + .82 * (c / mx) ** .6) if c else "#0c1c30"
            o.append(f'<rect x="{x + 1:.1f}" y="{y:.1f}" width="{cell - 2:.1f}" height="{cell * .72 - 2:.1f}" rx="2.2" fill="{col}" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1" dur=".35s" begin="{.4 + wi * .03 + di * .02:.2f}s" fill="freeze"/></rect>')
    # sweeping wave
    gh = 7 * cell * .72
    o.append(f'<rect x="{GX0}" y="{GY0 + 4}" width="46" height="{gh:.0f}" fill="url(#sweep)" opacity=".0">'
             f'<animate attributeName="x" values="{GX0 - 46};{W - 28}" dur="6s" begin="3s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;.55;.55;0" keyTimes="0;.1;.9;1" dur="6s" begin="3s" repeatCount="indefinite"/></rect>')
    o.append(f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    # legend
    lgx = W - 28 - 5 * 14 - 62
    o.append(f'<text x="{lgx}" y="{H - 14}" class="mono" font-size="8.5" fill="{t.TEXT3}" text-anchor="end">less</text>')
    for k in range(5):
        o.append(f'<rect x="{lgx + 6 + k * 14}" y="{H - 23}" width="11" height="11" rx="2.5" fill="{t.ramp(k / 4) if k else "#0c1c30"}"/>')
    o.append(f'<text x="{lgx + 6 + 5 * 14 + 4}" y="{H - 14}" class="mono" font-size="8.5" fill="{t.TEXT3}">more</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: total {total}, active {active}, peak {peak}, pushes {npush}, streak {cur}/{longest}")


if __name__ == "__main__":
    main()
