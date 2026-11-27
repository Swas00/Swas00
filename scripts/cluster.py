#!/usr/bin/env python3
"""assets/cluster.svg: live account stats as a cluster status board.

Identity node (my avatar, embedded so it works inside <img>) with a rotating
ring and a consistency arc, four stat tiles with live equalisers, a stacked
resource-allocation bar of my language mix, and a 30-day pulse strip.
Numbers come from the GitHub API on every run.
"""
import base64
import io
import json
import os
import sys
from collections import Counter
from datetime import datetime
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/cluster.svg"
AVATAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "avatar.png")
W, H = 830, 372


def avatar_uri():
    try:
        from PIL import Image
        im = Image.open(AVATAR).convert("RGB")
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((132, 132), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=84, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def main():
    prof = json.loads(common._req(f"https://api.github.com/users/{USER}"))
    rp = [r for r in common.repos(USER) if r["name"].lower() != USER.lower()]
    u = common.user_graph(USER)
    ds = common.days(u)
    cur, longest = common.streaks(ds)
    last364 = [c for _, c in ds][-364:]
    active = sum(1 for c in last364 if c)
    consistency = active / max(1, len(last364))
    stars = sum(r["stargazers_count"] for r in rp)
    followers = prof.get("followers", 0)
    joined = (prof.get("created_at") or "")[:4]
    mix = Counter(r["language"] or "Other" for r in rp)
    top = mix.most_common(6)
    total = sum(mix.values()) or 1

    uri = avatar_uri()
    alt = (f"Cluster status for {USER}: {len(rp)} repositories, {stars} stars, {followers} followers, "
           f"{cur} day streak, top languages {', '.join(l for l, _ in top[:3])}.")
    o = t.svg_open(W, H, escape(alt), "CLUSTER STATUS",
                   f'<clipPath id="av"><circle cx="139" cy="124" r="46"/></clipPath>')
    o.append(t.card_open(W, H, "CLUSTER STATUS", f"@{escape(USER)} &#183; refreshed every 6h"))

    # ---- identity node ----
    cx, cy = 139, 124
    o.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="{t.SKY}" fill-opacity=".10" filter="url(#soft)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="64" fill="none" stroke="{t.SKY}" stroke-opacity=".35" stroke-dasharray="2 6"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></circle>')
    circ = 2 * 3.14159 * 56
    o.append(f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="{t.HAIRLINE}" stroke-width="4"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="url(#aurora)" stroke-width="4" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cx} {cy})">'
             f'<animate attributeName="stroke-dashoffset" values="{circ:.1f};{circ * (1 - consistency):.1f}" dur="2s" begin=".3s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1"/></circle>')
    if uri:
        o.append(f'<image href="{uri}" x="{cx - 46}" y="{cy - 46}" width="92" height="92" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="{t.RAISED}"/><text x="{cx}" y="{cy + 12}" font-size="34" font-weight="800" fill="{t.SKY}" text-anchor="middle">{escape(USER[:2].upper())}</text>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{t.SKY}" stroke-opacity=".6" stroke-width="1.4"/>')
    o.append(f'<circle cx="{cx + 36}" cy="{cy + 36}" r="7.5" fill="{t.SURFACE}"/><circle cx="{cx + 36}" cy="{cy + 36}" r="5" fill="{t.GREEN}"><animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{cx}" y="212" font-size="19" font-weight="800" fill="{t.TEXT}" text-anchor="middle">@{escape(USER)}</text>')
    o.append(f'<text x="{cx}" y="230" class="mono" font-size="10" letter-spacing=".14em" fill="{t.GREEN}" text-anchor="middle">NODE RUNNING</text>')
    rows = [("member since", joined or "n/a"), ("uptime", f"{cur}d streak"), ("longest run", f"{longest}d"), ("active days", f"{active}/{len(last364)}")]
    for i, (a, b) in enumerate(rows):
        y = 256 + i * 20
        o.append(f'<text x="44" y="{y}" class="mono" font-size="10.5" fill="{t.TEXT3}">{a}</text>'
                 f'<text x="234" y="{y}" class="mono" font-size="11.5" font-weight="700" fill="{t.TEXT}" text-anchor="end">{escape(str(b))}</text>'
                 f'<line x1="44" y1="{y + 7}" x2="234" y2="{y + 7}" stroke="{t.HAIRLINE}" stroke-dasharray="1 3"/>')
    o.append(f'<line x1="262" y1="64" x2="262" y2="{H - 24}" stroke="{t.HAIRLINE}"/>')

    # ---- stat tiles ----
    tiles = [("REPOSITORIES", len(rp), t.SKY), ("STARS EARNED", stars, t.AMBER), ("FOLLOWERS", followers, t.VIOLET), ("DAY STREAK", cur, t.GREEN)]
    tw, gap, x0 = 122, 10, 280
    for i, (lab, val, col) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" begin="{.2 + i * .15:.2f}s" fill="freeze"/>'
                 f'<rect x="{x}" y="66" width="{tw}" height="112" rx="14" fill="{t.RAISED}" stroke="{col}" stroke-opacity=".35"/>'
                 f'<rect x="{x}" y="66" width="{tw}" height="3" rx="1.5" fill="{col}" fill-opacity=".9"/>'
                 f'<text x="{x + 14}" y="90" class="label" style="fill:{t.TEXT3}">{lab}</text>'
                 f'<text x="{x + 14}" y="136" font-size="44" font-weight="800" fill="{t.TEXT}" letter-spacing="-1.5">{val}</text>')
        for b in range(10):
            bx = x + 14 + b * 10.4
            hh = 4 + (b * 7 + i * 5) % 14
            o.append(f'<rect x="{bx:.1f}" y="{168 - hh}" width="6" height="{hh}" rx="2" fill="{col}" fill-opacity=".8"><animate attributeName="height" values="{hh};{4 + (hh * 2 + b) % 16};{hh}" dur="{1.4 + (b % 5) * .3:.1f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y" values="{168 - hh};{168 - (4 + (hh * 2 + b) % 16)};{168 - hh}" dur="{1.4 + (b % 5) * .3:.1f}s" repeatCount="indefinite"/></rect>')
        o.append("</g>")

    # ---- resource allocation: language mix ----
    o.append(f'<text x="{x0}" y="204" class="label" style="fill:{t.TEXT2}">RESOURCE ALLOCATION</text>'
             f'<text x="{W - 28}" y="204" class="label" text-anchor="end">primary language per repo</text>')
    bx, bw = x0, W - 28 - x0
    o.append(f'<clipPath id="bar"><rect x="{bx}" y="212" width="0" height="20" rx="10"><animate attributeName="width" values="0;{bw}" dur="1.6s" begin=".6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1"/></rect></clipPath>')
    o.append(f'<rect x="{bx}" y="212" width="{bw}" height="20" rx="10" fill="{t.HAIRLINE}"/><g clip-path="url(#bar)">')
    cur_x = bx
    for lang, n in top:
        w = bw * n / total
        col = t.lang_color(lang if lang in t.LANG else "Other")
        o.append(f'<rect x="{cur_x:.1f}" y="212" width="{max(1, w - 2):.1f}" height="20" fill="{col}"/>')
        cur_x += w
    o.append("</g>")
    lx, ly = bx, 252
    for lang, n in top:
        col = t.lang_color(lang if lang in t.LANG else "Other")
        label = f"{lang} {round(100 * n / total)}%"
        o.append(f'<circle cx="{lx + 5}" cy="{ly}" r="4" fill="{col}"/><text x="{lx + 15}" y="{ly + 4}" font-size="11" fill="{t.TEXT2}">{escape(label)}</text>')
        lx += 15 + 6.4 * len(label) + 14
        if lx > W - 120:
            break

    # ---- 30-day pulse ----
    o.append(f'<text x="{x0}" y="290" class="label" style="fill:{t.TEXT2}">PULSE &#183; LAST 30 DAYS</text>')
    last30 = [c for _, c in ds][-30:]
    mx = max(max(last30), 1)
    pw = (W - 28 - x0) / 30
    for i, c in enumerate(last30):
        hh = 3 + 34 * (c / mx) ** .7 if c else 3
        col = t.ramp(.25 + .75 * c / mx) if c else t.HAIRLINE
        o.append(f'<rect x="{x0 + i * pw + 1.5:.1f}" y="{H - 26 - hh:.1f}" width="{pw - 3:.1f}" height="{hh:.1f}" rx="2" fill="{col}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{1.0 + i * .03:.2f}s" fill="freeze"/></rect>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: repos {len(rp)} stars {stars} followers {followers} streak {cur} mix {top}")


if __name__ == "__main__":
    main()
