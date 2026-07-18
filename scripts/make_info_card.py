#!/usr/bin/env python3
"""
make_info_card.py

Generates a neofetch-style "whoami" info card as an SVG: a left-hand column
of field labels (like `neofetch` output) plus a small color-swatch strip,
matching the reference README's info-card.svg.

Edit the CONFIG dict below with your own details, then run:
    python scripts/make_info_card.py -o info-card.svg
"""

import argparse

CONFIG = {
    "user": "nishchal",
    "host": "github",
    "fields": [
        ("Role", "Software Engineer"),
        ("Focus", "Backend & AI Systems"),
        ("Stack", "React / Next.js / Node.js"),
        ("Backend", "Python, Java, Django, Flask"),
        ("DB", "MySQL, MongoDB, PostgreSQL"),
        ("Cloud", "AWS, Docker, Linux"),
        ("AI/LLM", "LangChain, LlamaIndex, FAISS, Bedrock"),
        ("Learning", "System Design, CI/CD, AI Agents"),
    ],
    "swatches": [
        "#e06c75", "#98c379", "#e5c07b", "#61afef",
        "#c678dd", "#56b6c2", "#abb2bf", "#ffffff",
    ],
}

BG = "#0d1117"
FG = "#c9d1d9"
ACCENT = "#58a6ff"
DIM = "#8b949e"


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(cfg: dict, width: int = 520) -> str:
    pad = 24
    line_h = 26
    header_h = 60
    swatch_h = 26
    fields = cfg["fields"]

    height = header_h + len(fields) * line_h + swatch_h + pad * 2

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Consolas, Menlo, monospace">',
        f'<rect width="100%" height="100%" fill="{BG}" rx="12"/>',
        f'<style>'
        f'.hdr{{fill:{ACCENT};font-size:16px;font-weight:bold;}}'
        f'.lbl{{fill:{ACCENT};font-size:14px;}}'
        f'.val{{fill:{FG};font-size:14px;}}'
        f'.dim{{fill:{DIM};font-size:13px;}}'
        f'</style>',
    ]

    # header: user@host
    y = pad + 18
    svg.append(
        f'<text x="{pad}" y="{y}" class="hdr">{escape_xml(cfg["user"])}@{escape_xml(cfg["host"])}</text>'
    )
    y += 8
    svg.append(f'<line x1="{pad}" y1="{y}" x2="{width - pad}" y2="{y}" stroke="{DIM}" stroke-width="1" opacity="0.4"/>')
    y += 26

    label_w = 100
    for label, value in fields:
        svg.append(f'<text x="{pad}" y="{y}" class="lbl">{escape_xml(label)}:</text>')
        svg.append(f'<text x="{pad + label_w}" y="{y}" class="val">{escape_xml(value)}</text>')
        y += line_h

    # swatch strip
    y += 10
    x = pad
    sw = (width - pad * 2) / len(cfg["swatches"])
    for color in cfg["swatches"]:
        svg.append(f'<rect x="{x:.1f}" y="{y}" width="{sw - 4:.1f}" height="18" rx="3" fill="{color}"/>')
        x += sw

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", default="info-card.svg")
    args = parser.parse_args()

    svg = render_svg(CONFIG)
    with open(args.output, "w") as f:
        f.write(svg)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
