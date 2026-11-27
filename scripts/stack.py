#!/usr/bin/env python3
"""assets/stack.svg: my toolchain as a layered cloud stack.

Six service layers from experience down to cloud delivery. A column of isometric
slabs on the left breathes in sequence while a data packet travels through every
layer; each layer lists the tools I use (solid) and a roadmap row of cloud
platforms I'm exploring (dashed). Static content, edit LAYERS below. Pure SMIL.
"""
import sys
from xml.sax.saxutils import escape

import theme as t

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/stack.svg"
W = 830
LAYERS = [  # (name, subtitle, colour, [tools], exploring?)
    ("EXPERIENCE", "frontend", t.SKY, ["React", "Next.js", "TypeScript", "Tailwind CSS"], False),
    ("SERVICES", "backend", t.TEAL, ["Node.js", "Express", "Python", "Java"], False),
    ("INTELLIGENCE", "genai", t.VIOLET, ["LangChain", "Generative AI", "LLM apps"], False),
    ("DATA", "storage", t.AMBER, ["PostgreSQL", "MongoDB", "Cassandra", "Oracle"], False),
    ("DELIVERY", "containers & ci/cd", t.GREEN, ["Docker", "Git", "GitHub Actions", "Vercel"], False),
    ("ROADMAP", "exploring next", t.PINK, ["AWS", "Kubernetes", "Terraform", "Azure"], True),
]
PITCH, TOP = 58, 76


def main():
    n = len(LAYERS)
    H = TOP + n * PITCH + 28
    o = t.svg_open(W, H, "Toolchain as a layered cloud stack: " + "; ".join(f"{a}: {', '.join(c)}" for a, _, _, c, _ in LAYERS), "TOOLCHAIN")
    o.append(t.card_open(W, H, "TOOLCHAIN", "layers &#183; solid = shipping with &#183; dashed = exploring"))
    cx = 96
    # data flow spine
    o.append(f'<line x1="{cx}" y1="{TOP - 6}" x2="{cx}" y2="{TOP + n * PITCH - 20}" stroke="{t.SKY}" stroke-opacity=".3" stroke-dasharray="2 4"/>')
    # slabs (back to front so lower layers overlap the upper ones correctly)
    for i, (name, sub, col, tools, explore) in enumerate(LAYERS):
        cy = TOP + i * PITCH + 16
        bob = 3 + (i % 3)
        o.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -{bob};0 0" dur="{3.2 + i * .25:.2f}s" begin="-{i * .5:.1f}s" repeatCount="indefinite"/>'
                 f'<polygon points="{cx},{cy - 22} {cx + 54},{cy} {cx},{cy + 22} {cx - 54},{cy}" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-width="1.4"{" stroke-dasharray=\"4 3\"" if explore else ""}/>'
                 f'<polygon points="{cx - 54},{cy} {cx},{cy + 22} {cx},{cy + 30} {cx - 54},{cy + 8}" fill="{col}" fill-opacity=".30"/>'
                 f'<polygon points="{cx + 54},{cy} {cx},{cy + 22} {cx},{cy + 30} {cx + 54},{cy + 8}" fill="{col}" fill-opacity=".18"/>'
                 f'<polygon points="{cx},{cy - 22} {cx + 54},{cy} {cx},{cy + 22} {cx - 54},{cy}" fill="#fff" fill-opacity="0"><animate attributeName="fill-opacity" values="0;0;.25;0;0" keyTimes="0;{i / (n + 1):.3f};{(i + .6) / (n + 1):.3f};{(i + 1.2) / (n + 1):.3f};1" dur="6s" repeatCount="indefinite"/></polygon></g>')
        # layer row
        x0 = 190
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" begin="{.2 + i * .12:.2f}s" fill="freeze"/>'
                 f'<text x="{x0}" y="{cy - 3}" font-size="13" font-weight="800" letter-spacing=".08em" fill="{col}">{name}</text>'
                 f'<text x="{x0}" y="{cy + 12}" class="mono" font-size="9" fill="{t.TEXT3}">{escape(sub)}</text>')
        x = x0 + 150
        for tool in tools:
            w = 34 + 7.7 * len(tool)
            o.append(f'<rect x="{x:.0f}" y="{cy - 14}" width="{w:.0f}" height="28" rx="14" fill="{col}" fill-opacity="{.05 if explore else .10}" stroke="{col}" stroke-opacity="{.8 if explore else .55}"' + (' stroke-dasharray="4 3"' if explore else "") + '/>'
                     f'<circle cx="{x + 12:.0f}" cy="{cy}" r="3" fill="{col}"' + (f'><animate attributeName="opacity" values="1;.2;1" dur="1.8s" repeatCount="indefinite"/></circle>' if explore else '/>') +
                     f'<text x="{x + 22:.0f}" y="{cy + 4}" font-size="12" font-weight="600" fill="{t.TEXT}">{escape(tool)}</text>')
            x += w + 10
        o.append("</g>")
    # packet travelling through the layers
    o.append(f'<circle r="3.6" fill="#fff" filter="url(#glow)"><animateMotion path="M{cx},{TOP - 6} L{cx},{TOP + n * PITCH - 20} L{cx},{TOP - 6}" dur="7s" repeatCount="indefinite"/></circle>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    t.write(OUT, o)
    print(f"wrote {OUT}: {n} layers")


if __name__ == "__main__":
    main()
