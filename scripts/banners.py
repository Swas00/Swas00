#!/usr/bin/env python3
"""assets/header.svg + assets/div-*.svg: 16-Bit Retro RPG Title Screen Header & Section Dividers.

Hero: Retro 16-Bit JRPG Title Screen (Final Fantasy / Chrono Trigger style):
  - 16-bit gold-studded dialog window bezel with CRT scanlines
  - Twinkling pixel starfield & distant parallax pixel mountain ridge
  - Layered 3D retro arcade title typography with cyan-to-gold gradient
  - Rotating animated quest prompts with retro cursor
  - JRPG Party status HUD (Player 1 Online, Active Quest, Combo Streak)
  - Contribution wave rendered as a glowing neon phosphor ridge along the base
"""
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
W = 830
NAME = "Swastik"
ROLES = [
    "Full-stack software developer.",
    "Exploring GenAI, LLMs & LangChain.",
    "MCA student & passionate builder.",
]

DIVIDERS = [  # (file, number, label)
    ("div-rpg", "01", "Character status"),
    ("div-dossier", "02", "Operator dossier"),
    ("div-vitals", "03", "Vitals"),
    ("div-skyline", "04", "Contribution skyline"),
    ("div-neural", "05", "Repo neural map"),
    ("div-galaxy", "06", "Contribution galaxy"),
    ("div-ops", "07", "Active ops: flight recorder"),
    ("div-ctf", "08", "Intercepted transmission"),
    ("div-arsenal", "09", "Arsenal"),
]

# Retro Palette Constants
BG_DARK = "#070a16"
FRAME_OUTER = "#283457"
FRAME_GOLD = "#f3be34"
FRAME_INNER = "#0c1224"
FRAME_HI = "#fff0a3"
FRAME_SHADOW = "#04060d"

TEXT_WHITE = "#fbfdff"
TEXT_GOLD = "#ffd753"
TEXT_CYAN = "#45ddff"
TEXT_GREEN = "#37f394"
TEXT_MUTED = "#8697bd"

PIXEL_FONT = "ui-monospace, 'Courier New', monospace, 'SF Mono', Menlo, Consolas"


def smooth(pts):
    """Catmull-Rom spline through pts as cubic bezier path data."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def header(last, streak, weekly):
    H = 340
    mx = max(weekly) or 1
    base, amp = H - 18, 68
    pts = [(i * (W - 32) / (len(weekly) - 1) + 16, base - amp * (v / mx) ** 0.7) for i, v in enumerate(weekly)]
    line = smooth(pts)
    area = f"{line} L{W - 16},{H - 16} L16,{H - 16} Z"

    # Twinkling pixel stars (x, y, size, dur, delay)
    stars_data = [
        (45, 42, 2, "1.8s", "0.2s"), (120, 75, 2.5, "2.4s", "0.7s"), (210, 35, 1.8, "3.1s", "1.2s"),
        (280, 80, 2, "2.0s", "0.4s"), (360, 48, 2.2, "2.7s", "0.9s"), (440, 70, 1.5, "1.9s", "1.5s"),
        (510, 38, 2.5, "3.3s", "0.1s"), (580, 92, 1.8, "2.2s", "1.1s"), (720, 45, 2.2, "2.5s", "0.6s"),
        (90, 120, 1.5, "2.8s", "1.3s"), (160, 155, 2, "2.1s", "0.5s"), (490, 130, 2, "3.0s", "1.7s"),
        (330, 140, 1.6, "2.3s", "0.8s"), (760, 110, 2.4, "2.6s", "0.3s"), (680, 150, 1.8, "3.2s", "1.4s"),
        (75, 240, 2, "2.2s", "0.9s"), (230, 260, 2.5, "2.9s", "0.2s"), (420, 270, 1.8, "2.4s", "1.6s")
    ]

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="{escape(USER)}: 16-Bit Retro RPG Profile Title Screen">',
        f"<title>{escape(USER)} // 16-BIT RETRO RPG TITLE SCREEN</title>",
        f"""<defs>
<linearGradient id="titleSweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="45%" stop-color="#ffffff"/>
    <stop offset="100%" stop-color="#f59e0b"/>
</linearGradient>
<linearGradient id="waveFillGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.32"/>
    <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
</linearGradient>
<linearGradient id="ridgeGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="50%" stop-color="#67e8f9"/>
    <stop offset="100%" stop-color="#fbbf24"/>
</linearGradient>
<filter id="neonPulse" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<pattern id="crtScan" width="100" height="4" patternUnits="userSpaceOnUse">
    <line x1="0" y1="0" x2="100" y2="0" stroke="#000000" stroke-width="1.2" opacity="0.22"/>
</pattern>
<style>
.rpg-mono {{ font-family: {PIXEL_FONT}; }}
.rpg-tag {{ font-family: {PIXEL_FONT}; font-size: 11px; font-weight: bold; fill: {TEXT_GOLD}; letter-spacing: 0.16em; }}
.rpg-title {{ font-family: {PIXEL_FONT}; font-weight: 900; letter-spacing: -2px; }}
.rpg-sub {{ font-family: {PIXEL_FONT}; font-size: 14px; fill: {TEXT_WHITE}; }}
.rpg-badge-lbl {{ font-family: {PIXEL_FONT}; font-size: 9px; font-weight: bold; fill: {TEXT_MUTED}; letter-spacing: 0.12em; text-transform: uppercase; }}
.rpg-badge-val {{ font-family: {PIXEL_FONT}; font-size: 13px; font-weight: bold; fill: {TEXT_WHITE}; }}
</style>
</defs>""",
        # Background base
        f'<rect width="{W}" height="{H}" fill="{BG_DARK}"/>',

        # 16-Bit JRPG Double Beveled Outer Window Frame
        f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="6" fill="{FRAME_INNER}" stroke="{FRAME_OUTER}" stroke-width="4"/>',
        f'<rect x="12" y="12" width="{W - 24}" height="{H - 24}" rx="4" fill="none" stroke="{FRAME_GOLD}" stroke-width="2.5"/>',
        f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="3" fill="none" stroke="{FRAME_SHADOW}" stroke-width="1.5"/>',

        # 4 Corner decorative studs (Classic RPG gold rivets)
        f'<rect x="11" y="11" width="6" height="6" fill="{FRAME_HI}"/>',
        f'<rect x="13" y="13" width="2" height="2" fill="{FRAME_SHADOW}"/>',
        f'<rect x="{W - 17}" y="11" width="6" height="6" fill="{FRAME_HI}"/>',
        f'<rect x="{W - 15}" y="13" width="2" height="2" fill="{FRAME_SHADOW}"/>',
        f'<rect x="11" y="{H - 17}" width="6" height="6" fill="{FRAME_HI}"/>',
        f'<rect x="13" y="{H - 15}" width="2" height="2" fill="{FRAME_SHADOW}"/>',
        f'<rect x="{W - 17}" y="{H - 17}" width="6" height="6" fill="{FRAME_HI}"/>',
        f'<rect x="{W - 15}" y="{H - 15}" width="2" height="2" fill="{FRAME_SHADOW}"/>',

        # Top Game Cartridge / Level Header Plate
        f'<rect x="26" y="5" width="260" height="22" fill="{FRAME_INNER}" stroke="{FRAME_GOLD}" stroke-width="1.8"/>',
        f'<text x="36" y="20" class="rpg-tag" fill="{TEXT_GOLD}">★ RETRO RPG EDITION v2.6 ★</text>',
        f'<text x="{W - 26}" y="22" class="rpg-mono" font-size="10" fill="{TEXT_MUTED}" text-anchor="end">PRESS [START] TO INITIALIZE</text>',
    ]

    # Twinkling Pixel Stars
    for sx, sy, s_size, dur, del_t in stars_data:
        o.append(f'<rect x="{sx}" y="{sy}" width="{s_size}" height="{s_size}" fill="{TEXT_WHITE}">'
                 f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}" begin="{del_t}" repeatCount="indefinite"/>'
                 f'</rect>')

    # Distant 16-bit Pixel Mountain Ridge (Silhouette)
    mountain_pts = [
        (16, 280), (70, 245), (130, 275), (190, 230), (250, 265), (320, 220), (390, 260),
        (460, 235), (540, 270), (620, 225), (700, 255), (770, 215), (W - 16, 250),
        (W - 16, H - 16), (16, H - 16)
    ]
    poly_d = " ".join(f"{x},{y}" for x, y in mountain_pts)
    o.append(f'<polygon points="{poly_d}" fill="#0b1329" opacity="0.75"/>')

    # Weekly Contribution Phosphor Terrain Ridge
    o.append(f'<path d="{area}" fill="url(#waveFillGrad)"/>')
    o.append(f'<path d="{line}" fill="none" stroke="url(#ridgeGrad)" stroke-width="2.6" stroke-linecap="round" filter="url(#neonPulse)"/>')

    # Main Left Branding Section
    o.append(f'<text x="44" y="82" class="rpg-tag">⚔ FULL-STACK · AI &amp; GENAI ARCHMAGE · INDIA ⚔</text>')

    # 3D Layered Pixel Arcade Title: SWASTIK
    # Drop shadow layer
    o.append(f'<text x="44" y="174" class="rpg-title" font-size="94" fill="#060914">{NAME}</text>')
    # Mid-layer bevel
    o.append(f'<text x="42" y="172" class="rpg-title" font-size="94" fill="#1e3a8a">{NAME}</text>')
    # Front Gradient layer
    o.append(f'<text x="40" y="170" class="rpg-title" font-size="94" fill="url(#titleSweep)">{NAME}</text>')

    # Rotating RPG Quest Roles with animated typewriter prompt
    cyc = 4.2 * len(ROLES)
    for i, r in enumerate(ROLES):
        a, b = i / len(ROLES), (i + 1) / len(ROLES)
        kt = f"0;{a:.3f};{a + .03:.3f};{b - .04:.3f};{b - .01:.3f};1" if i else f"0;0;.03;{b - .04:.3f};{b - .01:.3f};1"
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/>'
                 f'<text x="44" y="214" class="rpg-sub" font-size="15" fill="{TEXT_GOLD}">► </text>'
                 f'<text x="64" y="214" class="rpg-sub" font-size="15">{escape(r)}</text>'
                 f'<text x="{68 + len(r) * 9}" y="214" class="rpg-mono" font-size="15" fill="{TEXT_CYAN}">_'
                 f'<animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>'
                 f'</text></g>')

    # Sub-badge below roles
    o.append(f'<rect x="44" y="238" width="145" height="24" fill="#0d1630" stroke="#25355c" stroke-width="1.2"/>')
    o.append(f'<text x="54" y="254" class="rpg-mono" font-size="10" fill="{TEXT_CYAN}">EXP MULTIPLIER: 2.5X</text>')

    o.append(f'<rect x="198" y="238" width="135" height="24" fill="#0d1630" stroke="#25355c" stroke-width="1.2"/>')
    o.append(f'<text x="208" y="254" class="rpg-mono" font-size="10" fill="{TEXT_GREEN}">ALIGNMENT: PROD</text>')

    # Right JRPG Party Status HUD Cards
    hud_chips = [
        ("PARTY MEMBER", "PLAYER 1: ONLINE", TEXT_GREEN, "💚"),
        ("ACTIVE QUEST", last, TEXT_CYAN, "💠"),
        ("STREAK COMBO", f"{streak} DAYS (BUFFED)", TEXT_GOLD, "🔥"),
    ]

    for i, (k, v, col, icon) in enumerate(hud_chips):
        cy = 50 + i * 58
        cx = 535
        cw = 255
        ch = 48
        # Card chassis
        o.append(f'<g transform="translate({cx}, {cy})">')
        o.append(f'<rect width="{cw}" height="{ch}" fill="#0b1226" stroke="{FRAME_OUTER}" stroke-width="1.5"/>')
        o.append(f'<rect x="2" y="2" width="{cw - 4}" height="{ch - 4}" fill="none" stroke="#182342" stroke-width="1"/>')
        # Left status badge icon box
        o.append(f'<rect x="8" y="8" width="32" height="32" fill="#070c1a" stroke="{col}" stroke-width="1.2"/>')
        o.append(f'<text x="24" y="28" class="rpg-mono" font-size="14" text-anchor="middle">{icon}</text>')
        # Labels
        o.append(f'<text x="48" y="20" class="rpg-badge-lbl">{k}</text>')
        o.append(f'<text x="48" y="36" class="rpg-badge-val" fill="{col}">{escape(v)}</text>')
        o.append('</g>')

    # CRT Scanline Overlay
    o.append(f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" fill="url(#crtScan)" pointer-events="none"/>')

    o.append("</svg>")
    return "\n".join(o)


def divider(num, label):
    H = 44
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">',
        f"<title>{escape(label)}</title>",
        f"""<defs>
<linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#38bdf8"/><stop offset="50%" stop-color="#ffffff"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient>
<linearGradient id="auroraV" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#38bdf8"/><stop offset="50%" stop-color="#ffffff"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient>
<linearGradient id="bdr" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#38bdf8" stop-opacity=".7"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".4"/><stop offset="1" stop-color="#f59e0b" stop-opacity=".7"/></linearGradient>
<style>
.mono{{font-family:{PIXEL_FONT};}}
</style>
<clipPath id="bar"><rect width="{W}" height="{H}" rx="6"/></clipPath>
</defs>""",
        f'<g clip-path="url(#bar)"><rect width="{W}" height="{H}" fill="{FRAME_INNER}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#aurora)" opacity=".08"/>',
        f'<rect width="5" height="{H}" fill="url(#auroraV)"/>',
        f'<rect x="-120" width="120" height="{H}" fill="url(#aurora)" opacity=".18"><animate attributeName="x" values="-120;{W};{W}" keyTimes="0;.55;1" dur="9s" repeatCount="indefinite"/></rect></g>',
        f'<text x="24" y="27" class="mono" font-size="12" font-weight="bold" fill="{TEXT_CYAN}">[{num}]</text>',
        f'<text x="64" y="28" class="mono" font-size="14" font-weight="bold" fill="{TEXT_WHITE}">▶ {escape(label).upper()}</text>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="5" fill="none" stroke="{FRAME_GOLD}" stroke-width="1.2"/>',
        "</svg>"
    ])


def main():
    try:
        u = common.user_graph(USER)
        weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
        weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
        cur, _ = common.streaks(common.days(u))
        rp = sorted(common.repos(USER), key=lambda r: r.get("pushed_at") or "", reverse=True)
        now = datetime.now(timezone.utc)
        d = (now - datetime.fromisoformat(rp[0]["pushed_at"].replace("Z", "+00:00"))).days if rp else 0
        last = f'{rp[0]["name"][:16]} ({"today" if d == 0 else f"{d}d ago"})' if rp else "Swas00 (today)"
    except Exception:
        weekly = [3, 6, 8, 4, 12, 16, 9, 14, 22, 18, 12, 8, 15, 24, 19, 14, 22, 18, 26, 15]
        cur = 15
        last = "Swas00 (today)"

    with open(f"{OUTDIR}/header.svg", "w", encoding="utf-8") as f:
        f.write(header(last, cur, weekly))
    for fn, num, label in DIVIDERS:
        with open(f"{OUTDIR}/{fn}.svg", "w", encoding="utf-8") as f:
            f.write(divider(num, label))
    print("banners: wrote redesigned 16-bit RPG header + dividers; last:", last, "| streak:", cur)


if __name__ == "__main__":
    main()
