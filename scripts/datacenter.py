#!/usr/bin/env python3
"""assets/datacenter.svg: one year of contributions as an isometric data center.

One server rack per week (52 racks, three rows), seven LED slots per rack, one
slot per weekday. A slot's colour is that day's contribution count, so a hot
week is a rack lit up like a busy node. Coolant lines run through the aisles, a
light wave sweeps down every row, status LEDs blink, and the busiest week gets
a beacon. Pure SMIL.
"""
import random
import sys
from datetime import date
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/datacenter.svg"
W = 830
ROWS = [18, 17, 17]            # weeks per row, oldest first
RW, RD, RH = 24, 22, 50       # rack footprint (iso half-diagonals) and height
SA, SB = 28, 112              # pitch along a row / between rows
DUR = 10.0


def main():
    u = common.user_graph(USER)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"][-52:]
    grid = [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]
    starts = [w["contributionDays"][0]["date"] for w in weeks]
    mx = max((c for w in grid for c in w), default=1) or 1
    totals = [sum(w) for w in grid]
    total = sum(totals)
    best = max(range(len(totals)), key=lambda i: totals[i])
    active = sum(1 for w in grid for c in w if c)
    rnd = random.Random(52)

    # geometry: ground back-vertex of rack (i, j) = O + i*A + j*B
    Ax, Ay = SA, SA / 2
    Bx, By = -SB, SB / 2
    ox, oy = 28 + 2 * SB + RD + 6, 150

    def G(i, j):
        return ox + i * Ax + j * Bx, oy + i * Ay + j * By

    maxi = max(ROWS) - 1
    bottom = G(maxi, len(ROWS) - 1)[1] + RW / 2 + RD / 2 + 26
    H = int(bottom + 52)

    alt = (f"Isometric data center: one server rack per week for the last year, seven LEDs per rack for the days of the week; "
           f"{total} contributions across {active} active days, busiest week {totals[best]} contributions.")
    o = t.svg_open(W, H, escape(alt), "CONTRIBUTION DATA CENTER",
                   f'<linearGradient id="floor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b2540"/><stop offset="1" stop-color="#06162a"/></linearGradient>'
                   f'<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t.PINK}" stop-opacity=".85"/><stop offset="1" stop-color="{t.PINK}" stop-opacity="0"/></linearGradient>')
    o.append(t.card_open(W, H, "DATA CENTER", f"{len(grid)} racks &#183; {len(grid) * 7} slots &#183; {total:,} requests"))

    # ---- floor ----
    ex = 26
    c0 = G(-.8, -.4)
    c1 = G(maxi + 1.6, -.4)
    c2 = G(maxi + 1.6, len(ROWS) - .1)
    c3 = G(-.8, len(ROWS) - .1)
    o.append(f'<polygon points="{c0[0]:.0f},{c0[1]:.0f} {c1[0]:.0f},{c1[1]:.0f} {c2[0]:.0f},{c2[1]:.0f} {c3[0]:.0f},{c3[1]:.0f}" fill="url(#floor)" stroke="{t.HAIRLINE}" stroke-width="1.2"/>')
    for k in range(-1, maxi + 3):
        a, b = G(k - .3, -.4), G(k - .3, len(ROWS) - .1)
        o.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{t.SKY}" stroke-opacity=".07"/>')
    for k in range(0, len(ROWS) * 4 + 1):
        j = -.4 + k * (len(ROWS) + .3) / (len(ROWS) * 4)
        a, b = G(-.8, j), G(maxi + 1.6, j)
        o.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{t.SKY}" stroke-opacity=".07"/>')
    # coolant lines in the aisles (animated)
    for j in range(len(ROWS)):
        jj = j + .78
        a, b = G(-.5, jj), G(maxi + 1.3, jj)
        o.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{t.TEAL}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="3 11">'
                 f'<animate attributeName="stroke-dashoffset" values="0;-28" dur="1.6s" repeatCount="indefinite"/></line>')

    # ---- racks, painter's order (far -> near) ----
    cells = []
    wk = 0
    for j, n in enumerate(ROWS):
        for i in range(n):
            if wk < len(grid):
                cells.append((i + j, j, i, wk))
            wk += 1
    cells.sort()
    for _, j, i, wk in cells:
        gx, gy = G(i, j)
        x, y = gx, gy - RH
        tot = totals[wk]
        heat = tot / (max(totals) or 1)
        # ground glow for hot racks
        if heat > .45:
            o.append(f'<ellipse cx="{gx - RD / 2 + RW / 2:.1f}" cy="{gy + RW / 4 + RD / 4 + 2:.1f}" rx="{RW + 10}" ry="{(RW + 10) / 2}" fill="{t.ramp(.55 + .4 * heat)}" fill-opacity="{.12 + .18 * heat:.2f}" filter="url(#soft)"/>')
        o.append(t.iso_box(x, y, RW, RD, RH, "#173556", "#0c1f38", "#081528"))
        o.append(f'<polygon points="{x:.1f},{y:.1f} {x + RW:.1f},{y + RW / 2:.1f} {x + RW - RD:.1f},{y + RW / 2 + RD / 2:.1f} {x - RD:.1f},{y + RD / 2:.1f}" fill="none" stroke="{t.SKY}" stroke-opacity=".28" stroke-width=".7"/>')
        # left face slots: one per weekday
        tlx, tly = x - RD, y + RD / 2
        trx, try_ = x + RW - RD, y + RW / 2 + RD / 2
        sh, gap, pad = 4.6, 1.8, 5
        for d, c in enumerate(grid[wk]):
            off = pad + d * (sh + gap)
            u0, u1 = .12, .88
            ax_, ay_ = tlx + (trx - tlx) * u0, tly + (try_ - tly) * u0 + off
            bx_, by_ = tlx + (trx - tlx) * u1, tly + (try_ - tly) * u1 + off
            col = t.ramp(.22 + .78 * (c / mx) ** .6) if c else "#10243d"
            pts = f"{ax_:.1f},{ay_:.1f} {bx_:.1f},{by_:.1f} {bx_:.1f},{by_ + sh:.1f} {ax_:.1f},{ay_ + sh:.1f}"
            if c and rnd.random() < .18:
                lo = .55
                o.append(f'<polygon points="{pts}" fill="{col}"><animate attributeName="fill-opacity" values="1;{lo};1" dur="{rnd.uniform(1.2, 3.4):.1f}s" begin="-{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></polygon>')
            else:
                o.append(f'<polygon points="{pts}" fill="{col}"/>')
        # right face: vent lines
        for k in range(3):
            yy = RH * (.3 + k * .22)
            o.append(f'<line x1="{x + RW - RD * .78:.1f}" y1="{y + RW / 2 + RD * .5 * .78 + yy:.1f}" x2="{x + RW - RD * .22:.1f}" y2="{y + RW / 2 + RD * .5 * .22 + yy:.1f}" stroke="#16365a" stroke-width=".9"/>')
        # status LED on top
        sx_, sy_ = x - RD / 2 + RW / 2, y + RW / 4 + RD / 4
        scol = t.GREEN if tot else t.TEXT3
        o.append(f'<circle cx="{sx_:.1f}" cy="{sy_:.1f}" r="1.7" fill="{scol}"><animate attributeName="opacity" values="1;.2;1" dur="{rnd.uniform(.8, 2.8):.1f}s" begin="-{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
        # sweep wave overlay on the left face
        pos = (i * SA + (j * SB * .35)) / (maxi * SA + 2 * SB * .35)
        a = .06 + .78 * pos
        kt = f"0;{a:.3f};{a + .035:.3f};{a + .09:.3f};1"
        o.append(f'<polygon points="{tlx:.1f},{tly:.1f} {trx:.1f},{try_:.1f} {trx:.1f},{try_ + RH:.1f} {tlx:.1f},{tly + RH:.1f}" fill="#bfe9ff" opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;.38;0;0" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite"/></polygon>')
        if wk == best:
            o.append(f'<rect x="{sx_ - 1:.1f}" y="{sy_ - 46:.1f}" width="2" height="46" fill="url(#beam)"/>'
                     f'<circle cx="{sx_:.1f}" cy="{sy_ - 46:.1f}" r="3.2" fill="{t.PINK}" filter="url(#glow)"/>'
                     f'<ellipse cx="{sx_:.1f}" cy="{sy_:.1f}" rx="6" ry="3" fill="none" stroke="{t.PINK}" stroke-width="1.2" opacity="0"><animate attributeName="rx" values="6;34" dur="2.4s" repeatCount="indefinite"/><animate attributeName="ry" values="3;17" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="2.4s" repeatCount="indefinite"/></ellipse>')

    # ---- row labels at the right end of each row ----
    wk = 0
    for j, n in enumerate(ROWS):
        i1 = min(n, len(grid) - wk) - 1
        if i1 < 0:
            break
        d0 = date.fromisoformat(starts[wk])
        d1 = date.fromisoformat(starts[wk + i1])
        gx, gy = G(i1, j)
        o.append(f'<text x="{gx + RW:.0f}" y="{gy + RW / 2 + RD / 2 + 16:.0f}" class="mono" font-size="9" fill="{t.TEXT3}" text-anchor="end">ROW {chr(65 + j)} &#183; {d0:%b %y}&#8211;{d1:%b %y}</text>')
        wk += n

    # ---- stats panel (top-right corner) ----
    px, py = W - 28 - 230, 66
    o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".8s" begin=".6s" fill="freeze"/>'
             f'<rect x="{px}" y="{py}" width="230" height="92" rx="12" fill="{t.RAISED}" fill-opacity=".85" stroke="{t.SKY}" stroke-opacity=".3"/>'
             f'<text x="{px + 16}" y="{py + 24}" class="label">YEAR LOAD</text>'
             f'<text x="{px + 16}" y="{py + 56}" font-size="32" font-weight="800" fill="{t.TEXT}" letter-spacing="-1">{total:,}</text>'
             f'<text x="{px + 16}" y="{py + 76}" class="mono" font-size="9.5" fill="{t.TEXT3}">{active} active days &#183; peak week {totals[best]}</text>'
             f'<circle cx="{px + 208}" cy="{py + 22}" r="3.4" fill="{t.PINK}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle></g>')
    # ---- legend (bottom-left) ----
    lx, ly = 28, H - 84
    o.append(f'<text x="{lx}" y="{ly}" class="label" style="fill:{t.TEXT2}">HOW TO READ</text>'
             f'<text x="{lx}" y="{ly + 17}" class="mono" font-size="9.5" fill="{t.TEXT3}">1 rack = 1 week &#183; 7 slots = Sun&#8211;Sat</text>'
             f'<text x="{lx}" y="{ly + 31}" class="mono" font-size="9.5" fill="{t.TEXT3}">brighter slot = more commits that day</text>')
    for k in range(5):
        o.append(f'<rect x="{lx + k * 22}" y="{ly + 40}" width="18" height="7" rx="2" fill="{t.ramp(k / 4) if k else "#10243d"}"/>')
    o.append(f'<text x="{lx + 5 * 22 + 6}" y="{ly + 47}" class="mono" font-size="8.5" fill="{t.TEXT3}">idle &#8594; hot</text>')
    o.append(f'<circle cx="{lx + 4}" cy="{ly + 61}" r="3" fill="{t.PINK}"/><text x="{lx + 14}" y="{ly + 64}" class="mono" font-size="8.5" fill="{t.PINK}">busiest week</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: {len(grid)} racks, H={H}, total {total}, best week {starts[best]} ({totals[best]})")


if __name__ == "__main__":
    main()
