#!/usr/bin/env python3
"""preview.py [assets_dir] [out.html]: lay every SVG out in one page for a local look (no server needed)."""
import base64
import glob
import os
import sys


def uri(f):
    return "data:image/svg+xml;base64," + base64.b64encode(open(f, "rb").read()).decode()


d = sys.argv[1] if len(sys.argv) > 1 else "assets"
out = sys.argv[2] if len(sys.argv) > 2 else "preview.html"
only = sys.argv[3:] 
files = sorted(glob.glob(os.path.join(d, "*.svg")), key=lambda p: (not os.path.basename(p).startswith("header"), os.path.basename(p)))
if only:
    files = [f for f in files if os.path.basename(f) in only]
body = "".join(f'<p class="n">{os.path.basename(f)}</p><img src="{uri(f)}">' for f in files if not os.path.basename(f).startswith("div-")) 
divs = "".join(f'<img src="{uri(f)}">' for f in files if os.path.basename(f).startswith("div-"))
open(out, "w").write(f'<!doctype html><meta charset="utf-8"><body style="margin:0;padding:16px;background:#0d1117;font-family:ui-monospace,monospace;color:#8b949e"><style>img{{width:100%;display:block;max-width:830px;margin:0 auto 8px}}.n{{max-width:830px;margin:16px auto 4px;font-size:11px}}</style>{body}<p class="n">dividers</p>{divs}')
print("wrote", out)
