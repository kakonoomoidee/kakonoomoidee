"""Build the profile README's SVGs (banner + CointMU map) in dark and light themes.

Fonts are Google Fonts subsets (printable ASCII) embedded as base64, because an SVG
shown through <img> cannot load external fonts. Run: python3 assets/src/build.py
"""

import base64
from pathlib import Path
from xml.sax.saxutils import escape

SRC = Path(__file__).parent
OUT = SRC.parent

THEMES = {
    "dark": {
        "ground": "#0B2340", "ground2": "#123A66", "ink": "#E6EFF6",
        "muted": "#93B3CF", "line": "#2F5A86", "amber": "#F2B441", "panel": "#0F2C4F",
    },
    "light": {
        "ground": "#EEF4F9", "ground2": "#D6E4F0", "ink": "#0B2340",
        "muted": "#46668A", "line": "#A7C0D8", "amber": "#B06A00", "panel": "#F8FBFD",
    },
}

# Public projects in creation order; the last block is the one still being mined.
TIMELINE = [
    ("2025.05", "ACTA"),
    ("2025.12", "Tekser labs"),
    ("2026.03", "KasihinAja"),
    ("2026.03", "StockSim"),
    ("2026.05", "CointMU"),
    ("now", "Muvo"),
]

HOLDERS = [
    ("Desktop client", "Electron + Geth node"),
    ("Browser extension", "wallet for dApps"),
    ("Muvo", "mobile wallet, Expo"),
]
BUILDERS = [
    ("cmu CLI", "scaffold, compile, deploy"),
    ("Node kit", "full node in one command"),
    ("Mining feed bot", "Telegram + Discord alerts"),
]


def font_face(family: str, file: str) -> str:
    data = base64.b64encode((SRC / "fonts" / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


FONTS = (
    font_face("Display", "display.woff2")
    + font_face("Body", "body.woff2")
    + font_face("Mono", "mono.woff2")
)


def style(t: dict, extra: str) -> str:
    return f"""<style>{FONTS}
.d{{font-family:Display,sans-serif;font-weight:700;fill:{t['ink']}}}
.b{{font-family:Body,sans-serif;font-weight:500;fill:{t['ink']}}}
.m{{font-family:Mono,monospace;font-weight:500;fill:{t['muted']}}}
.mu{{fill:{t['muted']}}}
{extra}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def text(x, y, size, cls, s, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>'


def banner(t: dict) -> str:
    w, h = 1200, 420
    bw, bh, gap, x0, y0 = 160, 88, 28, 50, 296
    blocks, links = [], []
    for i, (date, name) in enumerate(TIMELINE):
        x = x0 + i * (bw + gap)
        is_pending = i == len(TIMELINE) - 1
        stroke = t["amber"] if is_pending else t["line"]
        cls = ' class="mine"' if is_pending else f' style="animation-delay:{i * 0.55:.2f}s" class="hit"'
        dash = ' stroke-dasharray="6 6"' if is_pending else ""
        blocks.append(
            f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="10" fill="{t["panel"]}" '
            f'stroke="{stroke}" stroke-width="1.5"{dash}{cls}/>'
            + text(x + 16, y0 + 28, 14, "m", date)
            + text(x + bw - 16, y0 + 28, 14, "m", f"#{i + 1}", "end")
            + text(x + 16, y0 + 66, 24, "d", name)
        )
        if i:
            lx = x - gap
            links.append(f'<line x1="{lx}" y1="{y0 + bh / 2}" x2="{x}" y2="{y0 + bh / 2}" stroke="{t["line"]}" stroke-width="2"/>')
    path = f"M{x0 + bw / 2} {y0 + bh / 2} H{x0 + 5 * (bw + gap) + bw / 2}"
    extra = f"""
.hit{{animation:hit 3.3s ease-out infinite}}
@keyframes hit{{0%,8%{{stroke:{t['amber']}}}30%,100%{{stroke:{t['line']}}}}}
.mine{{animation:march 1s linear infinite}}
@keyframes march{{to{{stroke-dashoffset:-12}}}}
.glow{{animation:glow 3.3s ease-in-out infinite}}
@keyframes glow{{0%,70%{{opacity:.15}}85%{{opacity:.6}}100%{{opacity:.15}}}}"""
    last_x = x0 + 5 * (bw + gap)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="kakonoomoide: building CointMU, a proof-of-work chain">
{style(t, extra)}
<defs><radialGradient id="sun" cx="0.92" cy="0" r="0.9"><stop offset="0" stop-color="{t['ground2']}"/><stop offset="1" stop-color="{t['ground']}"/></radialGradient>
<filter id="blur" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="14"/></filter></defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#sun)"/>
{text(50, 140, 104, "d", "kakonoomoide")}
{text(54, 196, 26, "b", "I build CointMU, a proof-of-work chain, and everything that runs on it.")}
{text(54, 232, 21, "b mu", "The node, the wallets, the CLI, and the bots that keep watch.")}
<rect x="{last_x - 6}" y="{y0 - 6}" width="{bw + 12}" height="{bh + 12}" rx="14" fill="{t['amber']}" filter="url(#blur)" class="glow"/>
{''.join(links)}
{''.join(blocks)}
<circle r="5" fill="{t['amber']}"><animateMotion dur="3.3s" repeatCount="indefinite" path="{path}" keyPoints="0;1;1" keyTimes="0;0.85;1" calcMode="linear"/></circle>
</svg>"""


def node(x, y, title, sub, anchor):
    return text(x, y, 24, "d", title, anchor) + text(x, y + 28, 17, "b mu", sub, anchor)


def ecosystem(t: dict) -> str:
    w, h = 1200, 460
    cx, cy = w / 2, 250
    rows = [140, 250, 360]
    parts, paths = [], []
    for side, items, x_text, x_end, anchor in (
        ("l", HOLDERS, 56, 330, "start"),
        ("r", BUILDERS, w - 56, w - 330, "end"),
    ):
        for i, (title, sub) in enumerate(items):
            y = rows[i]
            hub_x = cx - 120 if side == "l" else cx + 120
            mid = (x_end + hub_x) / 2
            d = f"M{hub_x} {cy} C{mid} {cy} {mid} {y} {x_end} {y}"
            pid = f"p{side}{i}"
            paths.append(f'<path id="{pid}" d="{d}" fill="none" stroke="{t["line"]}" stroke-width="2"/>')
            parts.append(f'<circle cx="{x_end}" cy="{y}" r="5" fill="{t["line"]}"/>')
            parts.append(
                f'<circle r="4.5" fill="{t["amber"]}"><animateMotion dur="2.8s" begin="{i * 0.9 + (0.45 if side == "r" else 0):.2f}s" '
                f'repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion></circle>'
            )
            parts.append(node(x_text, y - 2, title, sub, anchor))
    hub = (
        f'<rect x="{cx - 120}" y="{cy - 58}" width="240" height="116" rx="16" fill="{t["panel"]}" stroke="{t["amber"]}" stroke-width="2"/>'
        + text(cx, cy - 8, 30, "d", "CointMU", "middle")
        + text(cx, cy + 26, 16, "m", "PoW chain 1912", "middle")
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="CointMU ecosystem: desktop client, browser extension and Muvo wallet for holders; cmu CLI, node kit and mining feed bot for builders">
{style(t, "")}
<rect width="{w}" height="{h}" rx="18" fill="{t['ground']}"/>
{text(56, 62, 17, "m", "for holders")}
{text(w - 56, 62, 17, "m", "for builders and miners", "end")}
{''.join(paths)}
{''.join(parts)}
{hub}
</svg>"""


def main() -> None:
    for name, t in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(t))
        (OUT / f"cointmu-{name}.svg").write_text(ecosystem(t))


if __name__ == "__main__":
    main()
