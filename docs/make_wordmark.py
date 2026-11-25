#!/usr/bin/env python3
"""Render the README wordmark from the frontend's vendored font."""

from __future__ import annotations

from math import ceil, floor
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

DOCS = Path(__file__).resolve().parent
FONT = DOCS.parent / "next-app" / "app" / "fonts" / "press-start-2p-latin-400.woff2"
OUTPUT = DOCS / "assets" / "wordmark.svg"

# Match the two spans in cli-hero.tsx and the wordmark utility in globals.css.
RUNS = (("poke", "Poké", "#ffd100"), ("cipher", "Cipher", "#ffffff"))
FIELD = "#0f380f"
INK = "#071a07"
TRACKING_EM = -0.03
STROKE_EM = 0.055
SHADOW_EM = 0.12
PADDING_EM = 0.26


def build_svg() -> str:
    """Convert the two colour runs into paths and fit the canvas around the ink."""
    with TTFont(FONT) as font:
        em = font["head"].unitsPerEm
        codepoints = font.getBestCmap()
        glyphs = font.getGlyphSet()
        bounds = BoundsPen(glyphs)
        origin = 0.0
        paths: list[str] = []
        for name, text, _colour in RUNS:
            outline = SVGPathPen(glyphs)
            for character in text:
                glyph = glyphs[codepoints[ord(character)]]
                # Fonts count up from the baseline. SVG coordinates count down.
                transform = (1, 0, 0, -1, origin, 0)
                glyph.draw(TransformPen(outline, transform))
                glyph.draw(TransformPen(bounds, transform))
                origin += glyph.width + em * TRACKING_EM
            paths.append(f'    <path id="{name}" d="{outline.getCommands()}"/>')

    left, top, right, bottom = bounds.bounds
    stroke = em * STROKE_EM
    shadow = em * SHADOW_EM
    margin = em * PADDING_EM + stroke / 2
    x = floor(left - margin)
    y = floor(top - margin)
    width = ceil(right + shadow + margin) - x
    height = ceil(bottom + shadow + margin) - y

    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg"',
            f'     width="{width}" height="{height}" viewBox="{x} {y} {width} {height}"',
            '     role="img" aria-labelledby="wordmark-title">',
            '  <title id="wordmark-title">PokéCipher</title>',
            "  <defs>",
            *paths,
            "  </defs>",
            f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{FIELD}"/>',
            f'  <g fill="{INK}" transform="translate({shadow:g} {shadow:g})">',
            *(f'    <use href="#{name}"/>' for name, _text, _colour in RUNS),
            "  </g>",
            f'  <g stroke="{INK}" stroke-width="{stroke:g}" paint-order="stroke fill">',
            *(f'    <use href="#{name}" fill="{colour}"/>' for name, _text, colour in RUNS),
            "  </g>",
            "</svg>",
            "",
        ]
    )


def main() -> None:
    """Write a stable SVG file for the README to embed."""
    OUTPUT.write_text(build_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
