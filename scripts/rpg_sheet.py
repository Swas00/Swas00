#!/usr/bin/env python3
"""assets/rpg_sheet.svg: Retro 16-Bit RPG Character Sheet & Battle HUD.

Transforms real GitHub data (streaks, commits, repos, tech stack) into an
authentic retro JRPG character sheet (Final Fantasy / Chrono Trigger style):
  - Animated 16-bit pixel hero sprite with breathing idle & mana sparks
  - Dynamic HP (Streak Vitality), MP (Commit Mana), and EXP to next Level
  - D&D / JRPG Core Attributes: STR, INT, AGI, VIT, CHA, LUK
  - Equipped Gear & Artifacts mapped to developer stack
  - Active Questline fetched from most recently updated repository
"""
import collections
import math
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as th

USER = sys.argv[1] if len(sys.argv) > 1 else "Swas00"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "rpg_sheet.svg")

W, H = 830, 440

# --- Retro 16-Bit RPG Palette Tokens ---
BG_DARK = "#070a14"
FRAME_OUTER = "#283457"
FRAME_GOLD = "#f3be34"
FRAME_INNER = "#10162a"
FRAME_HI = "#fff0a3"
FRAME_SHADOW = "#05070f"

TEXT_WHITE = "#fbfdff"
TEXT_GOLD = "#ffd753"
TEXT_MUTED = "#8697bd"
TEXT_CYAN = "#45ddff"
TEXT_GREEN = "#37f394"
TEXT_RED = "#ff5468"

BAR_BG = "#161c30"
HP_BAR = "#34eb77"
MP_BAR = "#38bdf8"
EXP_BAR = "#ffc233"

PIXEL_FONT = "ui-monospace, 'Courier New', monospace, 'SF Mono', Menlo, Consolas"


def get_profile_data(login):
    """Fetch GitHub data with resilient offline / rate-limit fallback."""
    try:
        u = common.user_graph(login)
        ds = common.days(u)
        cur_streak, longest_streak = common.streaks(ds)
        repos_list = common.repos(login)
        recent_repos = sorted(repos_list, key=lambda r: r.get("pushed_at") or "", reverse=True)
        langs = collections.Counter(r["language"] for r in repos_list if r.get("language"))
        stars = sum(r.get("stargazers_count", 0) for r in repos_list)
        total_commits = u["contributionsCollection"].get("totalCommitContributions", 350)
        followers = u["followers"]["totalCount"]
        following = u["following"]["totalCount"]
        top_repo = recent_repos[0]["name"] if recent_repos else "sovereign-proof"
        desc = recent_repos[0].get("description") if recent_repos else "Active development"
    except Exception as e:
        # Fallback values tailored for @Swas00 if rate-limited or offline
        cur_streak, longest_streak = 4, 14
        stars = 18
        total_commits = 412
        followers = 12
        following = 15
        top_repo = "verity"
        desc = "AI truth verification engine"
        langs = collections.Counter({"TypeScript": 7, "JavaScript": 5, "Python": 4, "HTML": 2})

    return {
        "user": login,
        "cur_streak": cur_streak,
        "longest_streak": longest_streak,
        "stars": stars,
        "commits": total_commits,
        "followers": followers,
        "following": following,
        "top_repo": top_repo,
        "desc": desc or "Forging the future of software",
        "langs": langs,
    }


def pixel_hero_sprite(px, py):
    """Procedural 16-bit Pixel Hero (Archmage / Coder) with idle animation."""
    # Palette map for sprite
    C_OUTLINE = "#070913"
    C_HAIR = "#202a44"
    C_SKIN = "#ffcfa3"
    C_SHADOW_SKIN = "#e0a579"
    C_ROBE = "#3b58c7"
    C_ROBE_HI = "#5d7eff"
    C_GOLD = "#ffd753"
    C_STAFF = "#8b5a2b"
    C_ORB = "#38e0ff"
    C_ORB_CORE = "#ffffff"
    C_BOOT = "#1a2136"

    # 18x18 pixel grid definition (scale = 5.2px per pixel)
    s = 5.2
    # Each row is an 18-char string
    grid = [
        "......HHHH......",
        ".....HHHHHH.....",
        "....HHFFFFHH....",
        "....HFFFSFFH....",
        "....FFFFFFSS....",
        "....FEFFEFSS....",
        "....FFFFFFSS....",
        "....SSFFSSSS....",
        "..O...RRRR...G..",
        ".OXO.RRGRRR..G..",
        "..O.RRRRRRRR.G..",
        "....RRGGRRRR.G..",
        "....RRRRRRRR.G..",
        "....RRRRRRRR.G..",
        "....RR....RR.G..",
        "....BB....BB.G..",
    ]

    colormap = {
        "H": C_HAIR,
        "F": C_SKIN,
        "S": C_SHADOW_SKIN,
        "E": "#1a1f33",
        "R": C_ROBE,
        "G": C_GOLD,
        "B": C_BOOT,
        "O": C_ORB,
        "X": C_ORB_CORE,
    }

    rects = []
    for r_idx, row in enumerate(grid):
        for c_idx, ch in enumerate(row):
            if ch in colormap:
                color = colormap[ch]
                rects.append(f'<rect x="{px + c_idx * s:.1f}" y="{py + r_idx * s:.1f}" width="{s + 0.1:.1f}" height="{s + 0.1:.1f}" fill="{color}"/>')

    # Add staff
    staff_x = px + 14 * s
    staff_y = py + 6 * s
    rects.append(f'<rect x="{staff_x:.1f}" y="{staff_y:.1f}" width="{s:.1f}" height="{10 * s:.1f}" fill="{C_STAFF}"/>')
    # Glowing orb on staff top
    rects.append(f'<circle cx="{staff_x + s/2:.1f}" cy="{staff_y - s:.1f}" r="{s * 1.4:.1f}" fill="{C_ORB}" filter="url(#manaGlow)"/>')
    rects.append(f'<circle cx="{staff_x + s/2:.1f}" cy="{staff_y - s:.1f}" r="{s * 0.7:.1f}" fill="{C_ORB_CORE}"/>')

    return "".join(rects)


def main():
    d = get_profile_data(USER)

    # --- RPG Calculations ---
    level = max(1, int(math.sqrt(d["commits"] * 1.8) + len(d["langs"]) * 1.5))
    xp_curr = (d["commits"] * 17 + d["stars"] * 45) % 1000
    xp_max = 1000

    # HP: Health scaled from current streak (max 100)
    hp_curr = min(100, max(25, d["cur_streak"] * 12 + 20))
    hp_max = 100

    # MP: Mana scaled from commit velocity
    mp_curr = min(200, max(60, int(d["commits"] * 0.6)))
    mp_max = 200

    # RPG Attributes (Scale 1-99)
    str_stat = min(99, max(45, int(math.log(max(2, d["commits"]), 1.12))))
    int_stat = min(99, 78 + len(d["langs"]) * 4)
    agi_stat = min(99, 65 + (d["cur_streak"] * 3))
    vit_stat = min(99, 50 + (d["longest_streak"] * 3))
    cha_stat = min(99, 55 + (d["stars"] * 2 + d["followers"]))
    luk_stat = 88

    # Top equipment from langs
    top_lang = d["langs"].most_common(1)[0][0] if d["langs"] else "TypeScript"
    weapon = f"{top_lang} Soul-Blade +{min(9, level // 4)}"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
               f'aria-label="Retro 16-Bit RPG Character Sheet for {escape(d["user"])}">')
    svg.append(f"<title>CHARACTER STATUS // {escape(d['user'])}</title>")

    # Definitions: Pixel borders, filters, and animations
    svg.append(f"""<defs>
<filter id="manaGlow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="retroScan">
    <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.95 0"/>
</filter>
<linearGradient id="expGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#f59e0b"/>
    <stop offset="100%" stop-color="#fbbf24"/>
</linearGradient>
<linearGradient id="hpGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#10b981"/>
    <stop offset="100%" stop-color="#34d399"/>
</linearGradient>
<linearGradient id="mpGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#0284c7"/>
    <stop offset="100%" stop-color="#38bdf8"/>
</linearGradient>
<pattern id="scanlines" width="100" height="4" patternUnits="userSpaceOnUse">
    <line x1="0" y1="0" x2="100" y2="0" stroke="#000000" stroke-width="1.2" opacity="0.25"/>
</pattern>
<style>
.pix {{ font-family: {PIXEL_FONT}; font-size: 12px; fill: {TEXT_WHITE}; }}
.pix-title {{ font-family: {PIXEL_FONT}; font-size: 15px; font-weight: bold; fill: {TEXT_GOLD}; letter-spacing: 0.1em; }}
.pix-sub {{ font-family: {PIXEL_FONT}; font-size: 11px; fill: {TEXT_MUTED}; }}
.pix-stat {{ font-family: {PIXEL_FONT}; font-size: 12px; font-weight: bold; fill: {TEXT_CYAN}; }}
.pix-val {{ font-family: {PIXEL_FONT}; font-size: 12px; font-weight: bold; fill: {TEXT_WHITE}; }}
.gold-bracket {{ fill: {FRAME_GOLD}; }}
</style>
</defs>""")

    # Background canvas
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG_DARK}"/>')

    # Main 16-bit JRPG Dialog Window Box
    # Outer bezel (3D pixel frame)
    svg.append(f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="6" fill="{FRAME_INNER}" stroke="{FRAME_OUTER}" stroke-width="4"/>')
    svg.append(f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="4" fill="none" stroke="{FRAME_GOLD}" stroke-width="2.5"/>')
    svg.append(f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" rx="3" fill="none" stroke="{FRAME_SHADOW}" stroke-width="1.5"/>')

    # 4 Corner decorative studs (Classic RPG window corner rivets)
    for cx, cy in [(14, 14), (W - 14, 14), (14, H - 14), (W - 14, H - 14)]:
        svg.append(f'<rect x="{cx - 3}" y="{cy - 3}" width="6" height="6" fill="{FRAME_HI}"/>')
        svg.append(f'<rect x="{cx - 1}" y="{cy - 1}" width="2" height="2" fill="{FRAME_SHADOW}"/>')

    # Title Banner Plate at Top
    svg.append(f'<rect x="28" y="6" width="310" height="24" fill="{FRAME_INNER}" stroke="{FRAME_GOLD}" stroke-width="2"/>')
    svg.append(f'<text x="40" y="22" class="pix-title">⚔ CHARACTER STATUS ⚔</text>')

    # Realm & Time stamp
    utc_str = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    svg.append(f'<text x="{W - 36}" y="24" class="pix-sub" text-anchor="end">REALM: GITHUB // TIME: {utc_str}</text>')

    # ==============================================================
    # PANEL 1 (LEFT): Hero Sprite, Vocation & Character Info
    # ==============================================================
    # Avatar Box with pixel boundary
    av_x, av_y, av_w, av_h = 32, 42, 210, 368
    svg.append(f'<rect x="{av_x}" y="{av_y}" width="{av_w}" height="{av_h}" fill="#0b101f" stroke="{FRAME_OUTER}" stroke-width="2"/>')
    svg.append(f'<rect x="{av_x + 4}" y="{av_y + 4}" width="{av_w - 8}" height="{av_h - 8}" fill="none" stroke="#1d2847" stroke-width="1"/>')

    # Inner Sprite Stage
    stage_x, stage_y, stage_w, stage_h = av_x + 12, av_y + 12, av_w - 24, 150
    svg.append(f'<rect x="{stage_x}" y="{stage_y}" width="{stage_w}" height="{stage_h}" fill="#080c18" stroke="#1a2540" stroke-width="1.5"/>')

    # Magical summoning circle on stage floor
    circ_cx, circ_cy = stage_x + stage_w // 2, stage_y + stage_h - 18
    svg.append(f'<ellipse cx="{circ_cx}" cy="{circ_cy}" rx="64" ry="12" fill="none" stroke="{TEXT_CYAN}" stroke-width="1.2" opacity="0.4"/>')
    svg.append(f'<ellipse cx="{circ_cx}" cy="{circ_cy}" rx="42" ry="7" fill="none" stroke="{FRAME_GOLD}" stroke-width="1" opacity="0.6"/>')

    # Floating mana motes (animated)
    for idx, (mx, my, dur, del_t) in enumerate([(stage_x + 25, stage_y + 110, "3.2s", "0s"),
                                               (stage_x + 150, stage_y + 90, "2.7s", "0.8s"),
                                               (stage_x + 140, stage_y + 45, "3.8s", "1.4s")]):
        svg.append(f'<circle cx="{mx}" cy="{my}" r="1.8" fill="{TEXT_CYAN}" filter="url(#manaGlow)">'
                   f'<animate attributeName="cy" values="{my};{my - 40};{my}" dur="{dur}" begin="{del_t}" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{dur}" begin="{del_t}" repeatCount="indefinite"/>'
                   f'</circle>')

    # Render Animated 16-bit Pixel Hero with breathing idle
    hero_px = stage_x + (stage_w - (18 * 5.2)) // 2 + 8
    hero_py = stage_y + 26
    svg.append(f'<g transform="translate(0, 0)">')
    svg.append(f'<animateTransform attributeName="transform" type="translate" values="0,0; 0,-3.5; 0,0" dur="2.1s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1; 0.4 0 0.6 1"/>')
    svg.append(pixel_hero_sprite(hero_px, hero_py))
    svg.append('</g>')

    # Hero Label & Class
    info_y = stage_y + stage_h + 24
    svg.append(f'<text x="{av_x + av_w // 2}" y="{info_y}" class="pix-title" text-anchor="middle" font-size="16">{escape(d["user"].upper())}</text>')
    svg.append(f'<text x="{av_x + av_w // 2}" y="{info_y + 18}" class="pix" text-anchor="middle" fill="{TEXT_GOLD}">LV.{level} ARCHMAGE</text>')
    svg.append(f'<text x="{av_x + av_w // 2}" y="{info_y + 35}" class="pix-sub" text-anchor="middle">TITLE: FULL-STACK SORCERER</text>')

    svg.append(f'<line x1="{av_x + 16}" y1="{info_y + 48}" x2="{av_x + av_w - 16}" y2="{info_y + 48}" stroke="#212d4d" stroke-dasharray="3,3"/>')

    # Alignment & Guild Info
    svg.append(f'<text x="{av_x + 18}" y="{info_y + 68}" class="pix-sub">ALIGNMENT:</text>')
    svg.append(f'<text x="{av_x + av_w - 18}" y="{info_y + 68}" class="pix-val" text-anchor="end" fill="{TEXT_GREEN}">CHAOTIC PRODUCTIVE</text>')

    svg.append(f'<text x="{av_x + 18}" y="{info_y + 88}" class="pix-sub">GUILD:</text>')
    svg.append(f'<text x="{av_x + av_w - 18}" y="{info_y + 88}" class="pix-val" text-anchor="end">MCA ADVENTURERS</text>')

    svg.append(f'<text x="{av_x + 18}" y="{info_y + 108}" class="pix-sub">STATUS:</text>')
    svg.append(f'<text x="{av_x + av_w - 18}" y="{info_y + 108}" class="pix-val" text-anchor="end" fill="{TEXT_GREEN}">● BUFFED (ONLINE)</text>')

    # ==============================================================
    # PANEL 2 (CENTER): Vitals (HP/MP/EXP) & Attributes (STR/INT...)
    # ==============================================================
    mid_x, mid_y, mid_w, mid_h = 254, 42, 280, 368
    svg.append(f'<rect x="{mid_x}" y="{mid_y}" width="{mid_w}" height="{mid_h}" fill="#0b101f" stroke="{FRAME_OUTER}" stroke-width="2"/>')
    svg.append(f'<rect x="{mid_x + 4}" y="{mid_y + 4}" width="{mid_w - 8}" height="{mid_h - 8}" fill="none" stroke="#1d2847" stroke-width="1"/>')

    # Header
    svg.append(f'<text x="{mid_x + 16}" y="{mid_y + 26}" class="pix-title" font-size="13">▶ ATTRIBUTES &amp; VITALS</text>')
    svg.append(f'<line x1="{mid_x + 12}" y1="{mid_y + 36}" x2="{mid_x + mid_w - 12}" y2="{mid_y + 36}" stroke="{FRAME_OUTER}"/>')

    # --- Animated Resource Bars (HP, MP, EXP) ---
    bar_x, bar_w = mid_x + 54, 185
    gauges = [
        ("HP", f"{hp_curr}/{hp_max}", hp_curr / hp_max, "url(#hpGrad)", f"{d['cur_streak']}d Streak", mid_y + 60),
        ("MP", f"{mp_curr}/{mp_max}", mp_curr / mp_max, "url(#mpGrad)", "Code Velocity", mid_y + 90),
        ("EXP", f"{xp_curr}/{xp_max}", xp_curr / xp_max, "url(#expGrad)", f"+{xp_max - xp_curr} to Lv.{level+1}", mid_y + 120),
    ]

    for label, val_text, frac, grad_url, sub, gy in gauges:
        svg.append(f'<text x="{mid_x + 16}" y="{gy + 10}" class="pix" font-weight="bold" fill="{TEXT_GOLD}">{label}</text>')
        # Bar track (segmented look)
        svg.append(f'<rect x="{bar_x}" y="{gy}" width="{bar_w}" height="12" fill="{BAR_BG}" stroke="#263559" stroke-width="1"/>')
        fill_w = max(4.0, bar_w * frac)
        # Bar fill with animation
        svg.append(f'<rect x="{bar_x + 1}" y="{gy + 1}" width="{fill_w - 2}" height="10" fill="{grad_url}">'
                   f'<animate attributeName="width" values="0;{fill_w - 2}" dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                   f'</rect>')
        # Segment lines overlay for authentic retro 8-bit segmented gauge
        for sx in range(1, 10):
            svg.append(f'<line x1="{bar_x + sx * (bar_w / 10):.1f}" y1="{gy}" x2="{bar_x + sx * (bar_w / 10):.1f}" y2="{gy + 12}" stroke="{BG_DARK}" stroke-width="1"/>')
        # Numbers & helper text
        svg.append(f'<text x="{bar_x + bar_w}" y="{gy + 24}" class="pix-sub" text-anchor="end">{escape(sub)} &#183; <tspan fill="{TEXT_WHITE}">{escape(val_text)}</tspan></text>')

    svg.append(f'<line x1="{mid_x + 12}" y1="{mid_y + 160}" x2="{mid_x + mid_w - 12}" y2="{mid_y + 160}" stroke="{FRAME_OUTER}"/>')

    # --- Core Attributes Grid (STR, INT, AGI, VIT, CHA, LUK) ---
    svg.append(f'<text x="{mid_x + 16}" y="{mid_y + 180}" class="pix-title" font-size="12">CORE PARAMETERS</text>')

    attributes = [
        ("STR", str_stat, "Commit Power", TEXT_RED),
        ("INT", int_stat, "Tech Stacks & AI", TEXT_CYAN),
        ("AGI", agi_stat, "Shipping Velocity", TEXT_GOLD),
        ("VIT", vit_stat, "Consistency/Streak", TEXT_GREEN),
        ("CHA", cha_stat, "Rep / Stargazers", "#c084fc"),
        ("LUK", luk_stat, "Zero-Bug Builds", "#f472b6"),
    ]

    for i, (name, val, trait, col) in enumerate(attributes):
        row_y = mid_y + 208 + (i * 25)
        # Stat abbreviation
        svg.append(f'<text x="{mid_x + 20}" y="{row_y}" class="pix-stat" fill="{col}">{name}</text>')
        # Value
        svg.append(f'<text x="{mid_x + 64}" y="{row_y}" class="pix-val">{val}</text>')
        # Trait description
        svg.append(f'<text x="{mid_x + 104}" y="{row_y}" class="pix-sub">{escape(trait)}</text>')
        # Mini stat pip bar
        pip_x = mid_x + mid_w - 56
        pips = min(8, int((val / 100) * 8))
        pip_str = "■" * pips + "□" * (8 - pips)
        svg.append(f'<text x="{pip_x}" y="{row_y}" class="pix" font-size="10" fill="{col}">{pip_str}</text>')

    # ==============================================================
    # PANEL 3 (RIGHT): Equipment Inventory & Active Quest Log
    # ==============================================================
    r_x, r_y, r_w, r_h = 546, 42, 252, 368
    svg.append(f'<rect x="{r_x}" y="{r_y}" width="{r_w}" height="{r_h}" fill="#0b101f" stroke="{FRAME_OUTER}" stroke-width="2"/>')
    svg.append(f'<rect x="{r_x + 4}" y="{r_y + 4}" width="{r_w - 8}" height="{r_h - 8}" fill="none" stroke="#1d2847" stroke-width="1"/>')

    # Equipment Header
    svg.append(f'<text x="{r_x + 16}" y="{r_y + 26}" class="pix-title" font-size="13">▶ EQUIPPED GEAR</text>')
    svg.append(f'<line x1="{r_x + 12}" y1="{r_y + 36}" x2="{r_x + r_w - 12}" y2="{r_y + 36}" stroke="{FRAME_OUTER}"/>')

    gear = [
        ("WEAPON", "⚔", weapon, TEXT_WHITE),
        ("SHIELD", "🛡", "Docker Bastion Aegis", TEXT_CYAN),
        ("ARMOR", "🥋", "Next.js Robes of Speed", "#a78bfa"),
        ("RELIC", "💍", "LangChain Ring of Thought", TEXT_GOLD),
        ("POTION", "☕", "Elixir of Espresso (x99)", TEXT_GREEN),
    ]

    for idx, (slot, icon, item, text_col) in enumerate(gear):
        gy = r_y + 58 + idx * 32
        # Slot icon & badge
        svg.append(f'<rect x="{r_x + 14}" y="{gy - 13}" width="22" height="22" fill="#141c33" stroke="#25355c" stroke-width="1"/>')
        svg.append(f'<text x="{r_x + 25}" y="{gy + 2}" class="pix" font-size="12" text-anchor="middle">{icon}</text>')
        # Slot name & item name
        svg.append(f'<text x="{r_x + 44}" y="{gy - 2}" class="pix-sub" font-size="9">{slot}</text>')
        svg.append(f'<text x="{r_x + 44}" y="{gy + 10}" class="pix" font-size="11" font-weight="600" fill="{text_col}">{escape(item[:24])}</text>')

    # Quest Log Header
    svg.append(f'<line x1="{r_x + 12}" y1="{r_y + 224}" x2="{r_x + r_w - 12}" y2="{r_y + 224}" stroke="{FRAME_OUTER}"/>')
    svg.append(f'<text x="{r_x + 16}" y="{r_y + 244}" class="pix-title" font-size="13">📜 ACTIVE QUEST</text>')

    # Quest Box
    q_box_y = r_y + 254
    svg.append(f'<rect x="{r_x + 12}" y="{q_box_y}" width="{r_w - 24}" height="76" fill="#080c16" stroke="#253354" stroke-width="1.2"/>')
    svg.append(f'<text x="{r_x + 22}" y="{q_box_y + 20}" class="pix" font-size="11" fill="{TEXT_GOLD}">MAIN: "{escape(d["top_repo"].upper())}"</text>')
    brief_desc = d["desc"][:42] + ("…" if len(d["desc"]) > 42 else "")
    svg.append(f'<text x="{r_x + 22}" y="{q_box_y + 36}" class="pix-sub" font-size="10">OBJECTIVE: {escape(brief_desc)}</text>')
    svg.append(f'<text x="{r_x + 22}" y="{q_box_y + 54}" class="pix" font-size="10" fill="{TEXT_CYAN}">STATUS: In Battle · BOUNTY: +750 XP</text>')

    # Bottom JRPG Action Buttons
    btn_y = r_y + 338
    svg.append(f'<g transform="translate({r_x + 12}, {btn_y})">')
    buttons = [("PUSH", TEXT_RED), ("AI/MAGIC", TEXT_CYAN), ("REPOS", TEXT_GOLD), ("FLEE", TEXT_MUTED)]
    for bi, (btn_name, b_col) in enumerate(buttons):
        bx = bi * 57
        svg.append(f'<rect x="{bx}" y="0" width="54" height="20" fill="#131b30" stroke="{b_col}" stroke-width="1"/>')
        svg.append(f'<text x="{bx + 27}" y="14" class="pix" font-size="9" font-weight="bold" fill="{b_col}" text-anchor="middle">{btn_name}</text>')
    svg.append('</g>')

    # Scanline Overlay over entire card for CRT retro aesthetic
    svg.append(f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="url(#scanlines)" pointer-events="none"/>')

    svg.append("</svg>")

    content = "\n".join(svg)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"rpg_sheet: rendered {OUT} for {USER} (Level {level})")


if __name__ == "__main__":
    main()
