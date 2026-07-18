#!/usr/bin/env python3
"""
make_ascii_svg.py

Converts a photo into a monochrome ASCII-art portrait rendered as an SVG,
matching the "terminal portrait" style used in the reference README.

Usage:
    python scripts/make_ascii_svg.py path/to/photo.jpg -o avi-ascii.svg

Options:
    -o, --output      output SVG path (default: ascii-portrait.svg)
    -w, --width       number of ASCII columns (default: 90)
    --bg              background color (default: #0d1117, GitHub dark bg)
    --fg              foreground/text color (default: #58a6ff)
    --invert          invert brightness mapping (use for light photos on dark bg)
"""

import argparse
import sys

from PIL import Image

# Characters ordered from "dense/dark" to "sparse/light"
RAMP = "@%#*+=-:. "

# A monospace character is taller than it is wide; this factor corrects
# the aspect ratio so the ASCII portrait isn't squished vertically.
CHAR_ASPECT = 0.55


def image_to_ascii(img: Image.Image, width: int, invert: bool) -> list[str]:
    img = img.convert("L")  # grayscale
    orig_w, orig_h = img.size
    height = int(orig_h / orig_w * width * CHAR_ASPECT)
    img = img.resize((width, height))

    pixels = img.getdata()
    ramp = RAMP[::-1] if invert else RAMP
    chars = [ramp[pixel * (len(ramp) - 1) // 255] for pixel in pixels]

    lines = []
    for row in range(height):
        lines.append("".join(chars[row * width:(row + 1) * width]))
    return lines


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_svg(lines: list[str], bg: str, fg: str) -> str:
    char_w = 8.5
    char_h = char_w / CHAR_ASPECT * CHAR_ASPECT * 1.0  # visual line height
    line_h = 15
    font_size = 14
    pad = 20

    width = int(max(len(l) for l in lines) * char_w + pad * 2)
    height = int(len(lines) * line_h + pad * 2)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Consolas, Menlo, monospace">',
        f'<rect width="100%" height="100%" fill="{bg}" rx="12"/>',
        f'<style>.a{{fill:{fg};font-size:{font_size}px;white-space:pre;}}</style>',
    ]

    for i, line in enumerate(lines):
        y = pad + (i + 1) * line_h - 4
        svg_lines.append(
            f'<text x="{pad}" y="{y}" class="a" xml:space="preserve">{escape_xml(line)}</text>'
        )

    svg_lines.append("</svg>")
    return "\n".join(svg_lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("photo", help="Path to input photo")
    parser.add_argument("-o", "--output", default="ascii-portrait.svg")
    parser.add_argument("-w", "--width", type=int, default=90)
    parser.add_argument("--bg", default="#0d1117")
    parser.add_argument("--fg", default="#58a6ff")
    parser.add_argument("--invert", action="store_true")
    args = parser.parse_args()

    try:
        img = Image.open(args.photo)
    except FileNotFoundError:
        print(f"Photo not found: {args.photo}", file=sys.stderr)
        sys.exit(1)

    lines = image_to_ascii(img, args.width, args.invert)
    svg = render_svg(lines, args.bg, args.fg)

    with open(args.output, "w") as f:
        f.write(svg)

    print(f"Wrote {args.output} ({args.width} cols x {len(lines)} rows)")


if __name__ == "__main__":
    main()
