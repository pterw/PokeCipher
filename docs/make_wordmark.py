#!/usr/bin/env python3
"""Render the PokéCipher wordmark to ``docs/wordmark.svg``.

Regenerate with ``python docs/make_wordmark.py`` from the repository root.

Why this is a bitmap and not a ``<text>`` element
------------------------------------------------
GitHub serves README images through an ``<img>`` element, which loads no
external resources. A ``<text>`` element asking for Press Start 2P would never
receive its webfont and would silently fall back to a generic monospace, losing
the pixel look the product is built on. Drawing the letterforms as rectangles
makes the mark render identically everywhere, forever, with no font dependency
and no font-licensing question.

Why the letterforms live here rather than in the SVG
----------------------------------------------------
The mark is roughly 150 rectangles. Hand-authored, that is unreviewable and
unmaintainable: nobody can see the letters in a wall of coordinates. Keeping the
glyphs as bitmaps means the alphabet is readable at a glance, and a palette or
scale change is a one-line edit plus a re-run. The generated SVG is still
committed, so GitHub never needs this script.

Colours are the product's own, taken from ``next-app/app/globals.css``. The
``wordmark`` utility paints a terminal-void stroke *behind* the fill
(``paint-order: stroke fill``) and a hard terminal-void offset shadow with no
blur; ``components/cli-hero.tsx`` splits the lockup into a cartridge-yellow
"Poké" and a white "Cipher".
"""

from __future__ import annotations

from pathlib import Path

# --- The lockup -------------------------------------------------------------
# Split exactly where cli-hero.tsx splits it: the first four glyphs are
# cartridge-yellow, the rest are white.
WORD = "PokéCipher"
YELLOW_RUN = len("Poké")

CARTRIDGE_YELLOW = "#ffd100"  # --poke-yellow
WHITE = "#ffffff"  # text-white
TERMINAL_VOID = "#071a07"  # --terminal-void: the stroke and the offset shadow
LCD_DEEP = "#0f380f"  # --background: the banner's own field

# --- Geometry ---------------------------------------------------------------
UNIT = 10  # SVG units per pixel; raise for a larger file, not a different look
GLYPH_W = 6  # pixel columns drawn per glyph
ADVANCE = 7  # GLYPH_W plus one pixel of sidebearing
ROWS = 9  # ascender (2) + x-height (5) + descender (2)
SHADOW = 2  # hard offset in pixels, standing in for text-shadow: 0.12em 0.12em
PAD = 3  # pixels of margin around the mark

# --- Glyphs -----------------------------------------------------------------
# Nine rows each so ascenders, x-height and descenders line up by inspection.
# Rows 0-1 are the ascender/accent zone, 2-6 the x-height, 7-8 the descender.
GLYPHS: dict[str, tuple[str, ...]] = {
    "P": (
        "######",
        "##..##",
        "##..##",
        "######",
        "##....",
        "##....",
        "##....",
        "......",
        "......",
    ),
    "o": (
        "......",
        "......",
        ".####.",
        "##..##",
        "##..##",
        "##..##",
        ".####.",
        "......",
        "......",
    ),
    "k": (
        "##....",
        "##....",
        "##..#.",
        "##.#..",
        "####..",
        "##.#..",
        "##..#.",
        "......",
        "......",
    ),
    # Acute accent over a lowercase e: the accent owns the ascender zone.
    "é": (
        "...##.",
        "..##..",
        ".####.",
        "##..##",
        "######",
        "##....",
        ".####.",
        "......",
        "......",
    ),
    "C": (
        ".####.",
        "##..##",
        "##....",
        "##....",
        "##....",
        "##..##",
        ".####.",
        "......",
        "......",
    ),
    "i": (
        "..##..",
        "..##..",
        "......",
        ".####.",
        "..##..",
        "..##..",
        ".####.",
        "......",
        "......",
    ),
    # Descender: the bowl sits in the x-height, the stem runs into rows 7-8.
    "p": (
        "......",
        "......",
        "######",
        "##..##",
        "##..##",
        "##..##",
        "######",
        "##....",
        "##....",
    ),
    "h": (
        "##....",
        "##....",
        "##.##.",
        "##..##",
        "##..##",
        "##..##",
        "##..##",
        "......",
        "......",
    ),
    "e": (
        "......",
        "......",
        ".####.",
        "##..##",
        "######",
        "##....",
        ".####.",
        "......",
        "......",
    ),
    "r": (
        "......",
        "......",
        "##.##.",
        "###...",
        "##....",
        "##....",
        "##....",
        "......",
        "......",
    ),
}


def _validate() -> None:
    """Fail fast on a malformed glyph table, before it can emit a broken mark."""
    for name, rows in GLYPHS.items():
        if len(rows) != ROWS:
            raise ValueError(f"glyph {name!r} has {len(rows)} rows, expected {ROWS}")
        for row in rows:
            if len(row) != GLYPH_W:
                raise ValueError(f"glyph {name!r} row {row!r} is not {GLYPH_W} wide")
            if set(row) - {".", "#"}:
                raise ValueError(f"glyph {name!r} row {row!r} has non-bitmap characters")
    for char in WORD:
        if char not in GLYPHS:
            raise ValueError(f"WORD {WORD!r} needs glyph {char!r}, which is not defined")


def lit_pixels() -> dict[str, set[tuple[int, int]]]:
    """Return the mark's lit pixels, keyed by fill colour.

    Glyph *i* of the word starts at column ``i * ADVANCE``, so the sidebearing
    between letters is a property of the layout, not of the glyph bitmaps.
    """
    by_colour: dict[str, set[tuple[int, int]]] = {}
    for index, char in enumerate(WORD):
        colour = CARTRIDGE_YELLOW if index < YELLOW_RUN else WHITE
        bucket = by_colour.setdefault(colour, set())
        origin_x = index * ADVANCE
        for y, row in enumerate(GLYPHS[char]):
            for x, cell in enumerate(row):
                if cell == "#":
                    bucket.add((origin_x + x, y))
    return by_colour


def dilate(pixels: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Grow a pixel set by one pixel in all eight directions.

    Drawn in the void colour and then overpainted with the fill, this is the
    stroke: what remains visible is exactly a one-pixel outline hugging each
    letterform. Eight neighbours rather than four, so the outline stays solid
    across diagonals instead of letting the banner field show through.
    """
    grown = set(pixels)
    for x, y in pixels:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                grown.add((x + dx, y + dy))
    return grown


def runs(pixels: set[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Merge horizontally adjacent pixels into ``(x, y, width)`` runs.

    One rect per run instead of one per pixel: the same mark, roughly a third of
    the elements, and the file stays small enough to diff.
    """
    merged: list[tuple[int, int, int]] = []
    by_row: dict[int, list[int]] = {}
    for x, y in pixels:
        by_row.setdefault(y, []).append(x)
    for y in sorted(by_row):
        xs = sorted(by_row[y])
        start = previous = xs[0]
        for x in xs[1:]:
            if x == previous + 1:
                previous = x
                continue
            merged.append((start, y, previous - start + 1))
            start = previous = x
        merged.append((start, y, previous - start + 1))
    return merged


def _layer(pixels: set[tuple[int, int]], colour: str) -> str:
    """Render one pixel set as a group of rects."""
    parts = [
        f'<rect x="{x * UNIT}" y="{y * UNIT}" width="{w * UNIT}" height="{UNIT}"/>'
        for x, y, w in runs(pixels)
    ]
    return f'<g fill="{colour}">\n' + "\n".join(parts) + "\n</g>"


def build_svg() -> str:
    """Assemble the wordmark: field, void outline and shadow, then the fills."""
    _validate()
    fills = lit_pixels()

    # The outline and the offset shadow are the same colour in the product, so
    # they are the same layer here. Dilating the offset copy too keeps the
    # shadow's own edge as solid as the outline it merges into.
    ink: set[tuple[int, int]] = set()
    for pixels in fills.values():
        ink |= dilate(pixels)
        ink |= dilate({(x + SHADOW, y + SHADOW) for x, y in pixels})

    # Size the canvas from what was actually drawn, so a wider word, a heavier
    # outline or a longer shadow all re-fit themselves instead of clipping.
    every = ink | {pixel for pixels in fills.values() for pixel in pixels}
    max_x = max(x for x, _ in every)
    max_y = max(y for _, y in every)
    width = (max_x + 1 + PAD * 2) * UNIT
    height = (max_y + 1 + PAD * 2) * UNIT

    # crispEdges stops the renderer anti-aliasing the seams between adjacent
    # rects, which is what would otherwise turn a pixel grid into a blur.
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"',
            f'     viewBox="0 0 {width} {height}" shape-rendering="crispEdges"',
            '     role="img" aria-labelledby="wordmark-title">',
            '  <title id="wordmark-title">PokéCipher</title>',
            f'  <rect width="{width}" height="{height}" fill="{LCD_DEEP}"/>',
            f'  <g transform="translate({PAD * UNIT},{PAD * UNIT})">',
            _layer(ink, TERMINAL_VOID),
            *[
                _layer(pixels, colour)
                for colour, pixels in sorted(fills.items(), key=lambda item: item[0])
            ],
            "  </g>",
            "</svg>",
            "",
        ]
    )


def main() -> None:
    """Write the wordmark next to this script."""
    target = Path(__file__).with_name("wordmark.svg")
    # newline="\n" keeps the generated bytes platform-independent: without it
    # write_text translates to CRLF on Windows, so the committed asset would
    # depend on which machine last re-ran this script.
    target.write_text(build_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
