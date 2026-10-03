"""Generate the PokéCipher favicon from a first-generation Pikachu sprite.

The mark is a real Generation 1 sprite — the Pokémon Yellow artwork, the same era
the Game Boy palette in `DESIGN.md` comes from — downsized and knocked into a
circular cutout. It is built from the sprite's own pixels rather than traced by
hand, so the favicon is the character and not an impression of it.

Two files are written, because Next.js's App Router publishes every icon file it
finds in `app/` and browsers choose between them inconsistently:

    next-app/app/icon.svg    vector, theme-aware
    next-app/app/favicon.ico raster, one fixed scheme

Shipping only one leaves the other stale, and a stale `favicon.ico` still wins in
the browsers that prefer it. So both come from the same runs, the same placement
and the same ring geometry, and editing either by hand is how the two drift.

The ICO is rasterised from `icon.svg` rather than by re-rendering the sprite a
second time, so the two formats cannot disagree about the mark. That is also the
only route a fresh checkout has: the Generation 1 sprite is Nintendo's art and is
deliberately not committed, so `favicon.ico` is rebuilt from the SVG. A sprite
path is still accepted, for regenerating both files from a new download.

Why the SVG is rectangles rather than an embedded image: a favicon must be
self-contained, so referencing the PokémonDB CDN would make the tab icon depend
on a third party at the exact moment a user is looking at the tab. One <rect> per
horizontal run of same-coloured pixels needs no encoder, stays crisp at every
size because it is vector geometry, and collapses aggressively because the sprite
is tiny and mostly transparent.

Why the raster is not theme-aware: a favicon is drawn in the browser's own chrome,
outside the document, so it can see neither the app's `next-themes` toggle nor a
CSS cascade. The SVG at least gets `prefers-color-scheme`; an ICO gets nothing at
all and must therefore carry its own field, exactly as `make_wordmark.py` does.
Its disc is `--background`, its ring is `--foreground`, and the sprite's greys are
quantised onto the four-shade Game Boy ramp the rest of the UI already uses, so
the mark reads on a light toolbar and a dark one alike without needing to know
which it is on.

In neither format will changing the app's own theme recolour the tab. That is a
platform limitation, not something this file can work around.

Usage:
    python docs/make_favicon.py              # rebuild favicon.ico from icon.svg
    python docs/make_favicon.py sprite.png   # rebuild both, from a sprite
"""

from __future__ import annotations

import math
import re
import struct
import sys
import zlib
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import NamedTuple

OUT_PATH = Path(__file__).resolve().parent.parent / "next-app" / "app" / "icon.svg"

# The mark's geometry, in a 32x32 viewBox: the standard favicon grid, so one
# unit is one pixel at the smallest size a browser actually renders.
CANVAS = 32
CENTRE = CANVAS / 2
RING_RADIUS = 15.0
RING_WIDTH = 2.0
# Keep the sprite clear of the ring so the cutout reads as a window rather than
# as art colliding with a border. RING_RADIUS is the ring's *outer* edge, so the
# clear space begins a full stroke-width in, not half: the ring circle sits at
# RING_RADIUS - RING_WIDTH / 2 and its stroke straddles that, reaching inward to
# RING_RADIUS - RING_WIDTH.
INSET = RING_RADIUS - RING_WIDTH - 0.5

# `fit_scale` solves the farthest pixel corner to land exactly on the cutout
# circle, so the clipping test needs a tolerance: a point precisely on the
# boundary is inside the closed disc, and without this slack float rounding in
# the scale division reports that pixel as trimmed when it is not.
EPSILON = 1e-9

# The Generation 1 sprites are 56x56. Box-averaging each 2x2 block down to 28x28
# puts the art at favicon resolution before it is fitted, so the browser is not
# left to alias away half the pixels by itself.
DOWNSAMPLE = 2

# Ink for the ring. Black on a light browser toolbar, white on a dark one — the
# same inversion the wordmark uses for its stroke.
INK_LIGHT = "#000000"
INK_DARK = "#ffffff"

# The raster sibling of the SVG. Same mark, same geometry — but an ICO cannot
# carry a media query, so it is rendered once against a field of its own.
ICO_PATH = Path(__file__).resolve().parent.parent / "next-app" / "app" / "favicon.ico"

# 16 and 32 are what browser chrome actually draws, 48 is the Windows shortcut
# size, and 256 is the high-DPI entry modern browsers reach for first.
ICO_SIZES = (16, 32, 48, 256)

# The four-shade Game Boy DMG ramp, darkest first. `--background` and `--primary`
# in globals.css are the first and third of these, so quantising the sprite onto
# this ramp puts the favicon in the app's own palette instead of a greyscale of
# its own — the sprite is greyscale source art, and left alone it would be the
# only non-green thing in the UI.
DMG_RAMP = (
    (0x0F, 0x38, 0x0F),
    (0x30, 0x62, 0x30),
    (0x8B, 0xAC, 0x0F),
    (0x9B, 0xBC, 0x0F),
)

# The shades the sprite itself may paint with. `DMG_RAMP[0]` is excluded because
# it *is* `DISC`: the sprite sits on top of that field, so any ink snapped to the
# field's shade is invisible. Those are not stray pixels — Pikachu's outline, ear
# tips and eye pupils are the sprite's darkest ones. Quantising them onto the
# field painted the character's contour in the background colour, which is what
# left the ICO reading as a pale blob while the vector SVG read as Pikachu. The
# sprite therefore gets the three lighter shades and the field keeps the darkest.
SPRITE_RAMP = DMG_RAMP[1:]

# The raster mark's field and edge. Neither can invert, so together they bracket
# the toolbar: a dark disc reads on a light toolbar, a light ring on a dark one.
DISC = DMG_RAMP[0]  # --background
RING_INK = (0xD7, 0xF5, 0xC4)  # --foreground

# The sampling surface the raster is averaged off, in viewBox units per cell. At
# an eighth of a unit a cell is about a seventh of a sprite pixel, and a 16px
# favicon covers ~16 cells per output pixel per axis — fine enough that the
# averaging is the real thing rather than a slightly denser point sample.
CELL = 0.125
GRID = int(CANVAS / CELL)

# One generated <rect>, read back by `parse_rects`. Anchored to the exact
# attribute order and spacing `format_rects` emits, so the round trip is lossless
# — including fill-opacity, which survives the three decimals it is written with.
SVG_RECT = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"'
    r' fill="rgb\((\d+),(\d+),(\d+)\)"(?: fill-opacity="([\d.]+)")?/>'
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class Chunk(NamedTuple):
    """One PNG chunk: a four-byte type and its payload."""

    kind: bytes
    data: bytes


class Sprite(NamedTuple):
    """A decoded sprite: its size and its pixels, row-major, as RGBA tuples."""

    width: int
    height: int
    pixels: list[tuple[int, int, int, int]]


def paeth(a: int, b: int, c: int) -> int:
    """The PNG Paeth predictor: whichever neighbour is closest to a+b-c."""
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def unfilter(raw: bytes, stride: int, height: int, bpp: int) -> bytes:
    """Reverse PNG scanline filtering to recover the raw pixel bytes."""
    out = bytearray(height * stride)
    pos = 0
    for row in range(height):
        kind = raw[pos]
        pos += 1
        line = bytearray(raw[pos : pos + stride])
        pos += stride
        above = out[(row - 1) * stride : row * stride] if row else bytes(stride)
        if kind == 0:  # None
            pass
        elif kind == 1:  # Sub: add the byte bpp positions to the left.
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 0xFF
        elif kind == 2:  # Up: add the byte directly above.
            for x in range(stride):
                line[x] = (line[x] + above[x]) & 0xFF
        elif kind == 3:  # Average: floor of the left and above neighbours.
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + above[x]) >> 1)) & 0xFF
        elif kind == 4:  # Paeth
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                upleft = above[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + paeth(left, above[x], upleft)) & 0xFF
        else:
            raise ValueError(f"unknown PNG filter type {kind}")
        out[row * stride : (row + 1) * stride] = line
    return bytes(out)


def unpack_sub_byte(raw: bytes, width: int, height: int, depth: int) -> bytes:
    """Expand a bit-packed buffer to one byte per sample, most-significant first.

    Generation 1 sprites are 2-bit indexed — four colours, the Game Boy's own
    limit — so a byte holds four palette indices. PNG packs those from the top
    of the byte downward, and pads the tail of each scanline, so both the bit
    offset and the stride have to be derived rather than assumed.
    """
    mask = (1 << depth) - 1
    stride = (width * depth + 7) // 8
    out = bytearray(width * height)
    for row in range(height):
        line = raw[row * stride : (row + 1) * stride]
        for col in range(width):
            bit = col * depth
            out[row * width + col] = (line[bit // 8] >> (8 - depth - bit % 8)) & mask
    return bytes(out)


def decode_png(path: Path) -> Sprite:
    """Decode an 8-bit PNG to RGBA pixels, supporting indexed and truecolour."""
    chunks = list(iter_chunks(path.read_bytes()))
    by_kind: dict[bytes, bytes] = {}
    idat = bytearray()
    for chunk in chunks:
        if chunk.kind == b"IDAT":
            idat += chunk.data
        elif chunk.kind not in by_kind:
            by_kind[chunk.kind] = chunk.data

    ihdr = by_kind[b"IHDR"]
    width = int.from_bytes(ihdr[0:4], "big")
    height = int.from_bytes(ihdr[4:8], "big")
    depth, colour = ihdr[8], ihdr[9]
    if depth not in (1, 2, 4, 8):
        raise ValueError(f"unsupported PNG bit depth {depth}")
    if ihdr[12]:
        raise ValueError("interlaced PNGs are not supported")

    # Sub-byte images pack several samples into one byte, so the filtered stride
    # is a bit count rounded up, and the filter's bytes-per-pixel never drops
    # below one: PNG filters whole bytes, not individual samples.
    bits = depth * channels(colour)
    stride = (width * bits + 7) // 8
    raw = unfilter(zlib.decompress(bytes(idat)), stride, height, max(1, bits // 8))
    if depth < 8:
        raw = unpack_sub_byte(raw, width, height, depth)
        if colour != 3:
            # A sub-byte greyscale or truecolour sample only occupies the low
            # end of its range — a 2-bit shade maxes out at 3, not 255 — and the
            # PNG spec requires it be scaled up to fill the full depth. Indexed
            # samples are palette positions, not intensities, so they stay put.
            top = (1 << depth) - 1
            raw = bytes(sample * 255 // top for sample in raw)
    return Sprite(width=width, height=height, pixels=to_rgba(raw, width, height, colour, by_kind))


def channels(colour_type: int) -> int:
    """Bytes per pixel for a PNG colour type, at the 8-bit depth we require."""
    return {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]


def to_rgba(
    raw: bytes, width: int, height: int, colour_type: int, by_kind: dict[bytes, bytes]
) -> list[tuple[int, int, int, int]]:
    """Expand decoded bytes to RGBA tuples, applying PLTE and tRNS."""
    palette = by_kind.get(b"PLTE", b"")
    trns = by_kind.get(b"tRNS", b"")
    pixels: list[tuple[int, int, int, int]] = []
    for index in range(width * height):
        if colour_type == 3:  # Indexed: PLTE supplies colour, tRNS alpha.
            entry = raw[index]
            alpha = trns[entry] if entry < len(trns) else 255
            pixels.append((*palette[entry * 3 : entry * 3 + 3], alpha))
        elif colour_type == 0:  # Greyscale
            g = raw[index]
            pixels.append((g, g, g, 255))
        elif colour_type == 2:  # Truecolour
            base = index * 3
            pixels.append((*raw[base : base + 3], 255))
        elif colour_type == 4:  # Greyscale + alpha
            base = index * 2
            pixels.append((raw[base], raw[base], raw[base], raw[base + 1]))
        else:  # Truecolour + alpha
            base = index * 4
            pixels.append(tuple(raw[base : base + 4]))  # type: ignore[arg-type]
    return pixels


def iter_chunks(raw: bytes) -> Iterator[Chunk]:
    """Yield each PNG chunk, verifying the signature and every CRC."""
    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    pos = len(PNG_SIGNATURE)
    while pos < len(raw):
        length = int.from_bytes(raw[pos : pos + 4], "big")
        kind = raw[pos + 4 : pos + 8]
        data = raw[pos + 8 : pos + 8 + length]
        crc = int.from_bytes(raw[pos + 8 + length : pos + 12 + length], "big")
        # Fail fast on a truncated or corrupt download rather than emitting a
        # silently half-drawn icon.
        if zlib.crc32(kind + data) != crc:
            raise ValueError(f"bad CRC in {kind!r} chunk")
        yield Chunk(kind=kind, data=data)
        pos += 12 + length
        if kind == b"IEND":
            return


class Bounds(NamedTuple):
    """The tight bounding box of a sprite's opaque pixels, inclusive."""

    left: int
    top: int
    right: int
    bottom: int


def opaque_bounds(sprite: Sprite) -> Bounds:
    """Find the tight box around visible pixels, so padding does not shrink art."""
    cols = [i % sprite.width for i, p in enumerate(sprite.pixels) if p[3]]
    rows = [i // sprite.width for i, p in enumerate(sprite.pixels) if p[3]]
    if not cols:
        raise ValueError("sprite is fully transparent")
    return Bounds(left=min(cols), top=min(rows), right=max(cols), bottom=max(rows))


def origin_for(bounds: Bounds, scale: float) -> tuple[float, float]:
    """Top-left draw offset that centres the sprite's opaque box in the canvas."""
    width = (bounds.right - bounds.left + 1) * scale
    height = (bounds.bottom - bounds.top + 1) * scale
    return (
        CENTRE - width / 2 - bounds.left * scale,
        CENTRE - height / 2 - bounds.top * scale,
    )


def background_colour(sprite: Sprite) -> tuple[int, int, int, int]:
    """The colour that dominates the sprite's border, which is its background."""
    width, height = sprite.width, sprite.height
    border = [
        sprite.pixels[row * width + col]
        for row in range(height)
        for col in range(width)
        if row in (0, height - 1) or col in (0, width - 1)
    ]
    colour, _ = Counter(border).most_common(1)[0]
    return colour


def knock_out(sprite: Sprite) -> Sprite:
    """Make the background transparent by flooding inward from the border.

    Generation 1 sprites carry no `tRNS` chunk, so the paper behind Pikachu is a
    real colour rather than transparency. A flood fill rather than a global
    colour match is required: his eye highlights are the same white as that
    paper, so knocking out every matching pixel would punch holes in his face.
    Only the region connected to the edge is background.
    """
    width, height = sprite.width, sprite.height
    target = background_colour(sprite)
    filled = [False] * len(sprite.pixels)
    stack = [
        row * width + col
        for row in range(height)
        for col in range(width)
        if (row in (0, height - 1) or col in (0, width - 1))
        and sprite.pixels[row * width + col] == target
    ]
    for index in stack:
        filled[index] = True
    while stack:
        row, col = divmod(stack.pop(), width)
        for nrow, ncol in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            if not (0 <= nrow < height and 0 <= ncol < width):
                continue
            index = nrow * width + ncol
            if not filled[index] and sprite.pixels[index] == target:
                filled[index] = True
                stack.append(index)
    return Sprite(
        width=width,
        height=height,
        pixels=[
            (r, g, b, 0) if filled[i] else (r, g, b, a)
            for i, (r, g, b, a) in enumerate(sprite.pixels)
        ],
    )


def downsample(sprite: Sprite, factor: int) -> Sprite:
    """Average each factor x factor block of source pixels into one.

    Averaging rather than dropping. A 56px sprite has to shed roughly half its
    pixels to reach favicon size, and discarding them aliases away the eyes and
    the nose. Box averaging keeps the silhouette and blends the shading instead.

    Alpha weights the colour average, so a block that is only partly covered does
    not pull in the colour of pixels that are not actually there.
    """
    width = -(-sprite.width // factor)
    height = -(-sprite.height // factor)
    pixels: list[tuple[int, int, int, int]] = []
    for row in range(height):
        for col in range(width):
            red = green = blue = weight = alpha = covered = 0
            for dy in range(factor):
                for dx in range(factor):
                    sy, sx = row * factor + dy, col * factor + dx
                    if sy >= sprite.height or sx >= sprite.width:
                        continue
                    r, g, b, a = sprite.pixels[sy * sprite.width + sx]
                    covered += 1
                    alpha += a
                    red += r * a
                    green += g * a
                    blue += b * a
                    weight += a
            pixels.append(
                (0, 0, 0, 0)
                if not weight
                else (red // weight, green // weight, blue // weight, alpha // covered)
            )
    return Sprite(width=width, height=height, pixels=pixels)


def pixel_is_clipped(col: int, row: int, scale: float, origin: tuple[float, float]) -> bool:
    """True if any corner of this drawn pixel falls outside the cutout circle."""
    x, y = origin
    xs = (x + col * scale, x + (col + 1) * scale)
    ys = (y + row * scale, y + (row + 1) * scale)
    return any(math.hypot(px - CENTRE, py - CENTRE) > INSET + EPSILON for px in xs for py in ys)


def clipped_count(sprite: Sprite, bounds: Bounds, scale: float, origin: tuple[float, float]) -> int:
    """Count opaque pixels the cutout circle would trim at this scale."""
    total = 0
    for row in range(bounds.top, bounds.bottom + 1):
        for col in range(bounds.left, bounds.right + 1):
            if sprite.pixels[row * sprite.width + col][3] and pixel_is_clipped(
                col, row, scale, origin
            ):
                total += 1
    return total


def fit_scale(sprite: Sprite, bounds: Bounds) -> float:
    """Uniform scale that brings every opaque pixel inside the cutout circle.

    Uniform matters more than integer here. Scaling every source pixel to the
    same fractional square keeps the grid regular, which is what pixel art needs;
    a non-uniform scale would stretch some pixels wider than their neighbours and
    read as a printing error.

    The scale is solved from the farthest opaque corner rather than from the
    bounding box, because a circle inscribed in a square always clips that
    square's corners — and Pikachu's black ear tips sit in exactly those corners.
    Fitting the box would shave off his signature.
    """
    x0, y0 = origin_for(bounds, 1.0)
    farthest = 0.0
    for row in range(bounds.top, bounds.bottom + 1):
        for col in range(bounds.left, bounds.right + 1):
            if not sprite.pixels[row * sprite.width + col][3]:
                continue
            for px in (x0 + col, x0 + col + 1):
                for py in (y0 + row, y0 + row + 1):
                    farthest = max(farthest, math.hypot(px - CENTRE, py - CENTRE))
    return INSET / farthest if farthest else 1.0


def fmt(value: float) -> str:
    """Format a coordinate without a trailing '.0', to keep the SVG compact."""
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"


class Rect(NamedTuple):
    """One horizontal run of same-coloured sprite pixels, in viewBox units.

    The single geometry representation both routes share: the sprite pipeline
    emits runs from pixels, `parse_rects` reads the generated SVG's own <rect>
    elements back into runs, and `paint` rasterises either into one surface. One
    representation and one rasteriser is what stops the vector and the raster
    disagreeing about the mark.
    """

    x: float
    y: float
    width: float
    height: float
    rgba: tuple[int, int, int, int]


def rects_from_sprite(sprite: Sprite, scale: float, origin: tuple[float, float]) -> list[Rect]:
    """Emit one Rect per horizontal run of identical pixels.

    Merging runs is what keeps a bitmap-derived icon small: the sprite is mostly
    flat colour and mostly transparent, so consecutive pixels collapse into far
    fewer elements than one rect each would need.
    """
    x0, y0 = origin
    rects: list[Rect] = []
    for row in range(sprite.height):
        col = 0
        while col < sprite.width:
            pixel = sprite.pixels[row * sprite.width + col]
            if not pixel[3]:
                col += 1
                continue
            end = col + 1
            while end < sprite.width and sprite.pixels[row * sprite.width + end] == pixel:
                end += 1
            rects.append(
                Rect(
                    x=x0 + col * scale,
                    y=y0 + row * scale,
                    width=(end - col) * scale,
                    height=scale,
                    rgba=pixel,
                )
            )
            col = end
    return rects


def format_rects(rects: Sequence[Rect]) -> list[str]:
    """Serialise runs as SVG <rect> elements, one per run.

    `parse_rects` reverses this, so the attribute order and spacing here are a
    contract between the two halves and its regex is pinned to them.
    """
    lines: list[str] = []
    for rect in rects:
        red, green, blue, alpha = rect.rgba
        opacity = "" if alpha == 255 else f' fill-opacity="{alpha / 255:.3f}"'
        lines.append(
            f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" '
            f'width="{fmt(rect.width)}" height="{fmt(rect.height)}" '
            f'fill="rgb({red},{green},{blue})"{opacity}/>'
        )
    return lines


def parse_rects(svg: str) -> list[Rect]:
    """Recover the mark's geometry from a generated icon.svg.

    Rasterising the committed SVG, rather than re-rendering the sprite a second
    time, is what makes `favicon.ico` regenerable at all: the sprite is Nintendo's
    art and deliberately absent from the repository, so a fresh checkout has no
    other way to rebuild the raster. Reading the file this script itself wrote
    also means the two formats cannot disagree about the mark.

    The round trip is lossless. `fill-opacity` is written with three decimals and
    read back by scaling by 255, so the worst representation error is 0.1275 of a
    shade — well inside the half-shade that rounding needs to be exact.
    """
    rects: list[Rect] = []
    for match in SVG_RECT.finditer(svg):
        x, y, width, height, red, green, blue, opacity = match.groups()
        alpha = 255 if opacity is None else round(float(opacity) * 255)
        rects.append(
            Rect(
                x=float(x),
                y=float(y),
                width=float(width),
                height=float(height),
                rgba=(int(red), int(green), int(blue), alpha),
            )
        )
    return rects


class Placement(NamedTuple):
    """Where and how large the sprite draws inside the cutout circle."""

    bounds: Bounds
    scale: float
    origin: tuple[float, float]


def prepare(sprite: Sprite) -> Sprite:
    """Turn a raw sprite download into favicon art: transparent, then downsized."""
    return downsample(knock_out(sprite), DOWNSAMPLE)


def place(sprite: Sprite) -> Placement:
    """Solve the sprite's position and scale inside the circular cutout."""
    bounds = opaque_bounds(sprite)
    scale = fit_scale(sprite, bounds)
    return Placement(bounds=bounds, scale=scale, origin=origin_for(bounds, scale))


def luminance(rgb: tuple[int, int, int]) -> float:
    """Perceived brightness, weighted for the eye's bias towards green."""
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def quantise(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Snap a sprite colour to the nearest shade it is allowed to paint with.

    Matching on luminance rather than on RGB distance is what keeps the ramp in
    its own order: the shades differ far more in brightness than in hue, so a
    nearest-RGB pick would trade one shade for another of the same brightness and
    flatten the sprite's shading.

    The candidate set is `SPRITE_RAMP` and not the whole ramp, because the disc's
    own field is not a shade the sprite can paint: ink the colour of the field is
    ink nobody can see.
    """
    target = luminance(rgb)
    return min(SPRITE_RAMP, key=lambda shade: abs(luminance(shade) - target))


def blend_ink(colour: tuple[float, float, float], coverage: float) -> tuple[int, int, int]:
    """Composite a sprite sample onto the disc and snap it to a sprite shade.

    Box-averaging leaves the sprite's edges partly covered, so a sample is
    composited onto the disc's own darkness before it is quantised: a
    half-covered edge pixel is a dimmer shade, not a hole. Quantising first would
    snap every such edge to a full shade and throw away the anti-aliasing the
    averaging was there to produce.
    """
    red, green, blue = colour
    field = 1 - coverage
    return quantise(
        (
            round(red * coverage + DISC[0] * field),
            round(green * coverage + DISC[1] * field),
            round(blue * coverage + DISC[2] * field),
        )
    )


def sprite_ink(pixel: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """The shade one whole sprite pixel paints onto the disc."""
    red, green, blue, alpha = pixel
    return blend_ink((red, green, blue), alpha / 255)


def write_chunk(kind: bytes, data: bytes) -> bytes:
    """Serialise one PNG chunk: length, type, payload, then a CRC over type+payload.

    The writing half of `Chunk`, and the reason `encode_png` and `decode_png` can
    be trusted against each other: the CRC the reader refuses to skip is exactly
    the one this computes.
    """
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def encode_png(pixels: Sequence[tuple[int, int, int, int]], width: int, height: int) -> bytes:
    """Encode an RGBA buffer as a PNG — the mirror of `decode_png`.

    Scanlines carry a leading filter byte, set to 0 so each row is stored raw.
    Choosing a filter per row would shrink the file, but the mark is a handful of
    flat colour runs that zlib already collapses, and the encoder stays readable.
    """
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(pixels[y * width + x])
    return b"".join(
        (
            PNG_SIGNATURE,
            # 8 bits per channel, colour type 6: truecolour with alpha.
            write_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            write_chunk(b"IDAT", zlib.compress(bytes(rows), 9)),
            write_chunk(b"IEND", b""),
        )
    )


def paint(rects: Sequence[Rect]) -> list[tuple[int, int, int, int]]:
    """Rasterise runs onto the GRID x GRID sampling surface, in document order.

    Later rects overwrite earlier ones, which is SVG's own paint order, so the
    surface reproduces what the browser draws. A cell belongs to a run when its
    centre falls inside it, so membership is exact to half a cell — a sixteenth of
    a viewBox unit, far below one output pixel at any icon size.
    """
    surface: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (GRID * GRID)
    for rect in rects:
        col0 = max(0, math.ceil(rect.x / CELL - 0.5))
        col1 = min(GRID, math.ceil((rect.x + rect.width) / CELL - 0.5))
        row0 = max(0, math.ceil(rect.y / CELL - 0.5))
        row1 = min(GRID, math.ceil((rect.y + rect.height) / CELL - 0.5))
        for row in range(row0, row1):
            start = row * GRID
            for col in range(col0, col1):
                surface[start + col] = rect.rgba
    return surface


def disc_sample(
    surface: Sequence[tuple[int, int, int, int]], x0: float, y0: float, x1: float, y1: float
) -> tuple[tuple[float, float, float], float]:
    """Mean sprite colour and coverage over one output pixel's footprint.

    Colour and coverage come back separately on purpose. The colour is weighted by
    each cell's own alpha, so a partly transparent edge does not drag it towards
    whatever happens to sit behind the sprite, while coverage reports how much of
    the footprint the sprite actually filled. `blend_ink` then composites that one
    average onto the field — the same alpha-weighted arithmetic `downsample` uses
    a level up.
    """
    col0 = max(0, math.floor(x0 / CELL))
    col1 = min(GRID, math.ceil(x1 / CELL))
    row0 = max(0, math.floor(y0 / CELL))
    row1 = min(GRID, math.ceil(y1 / CELL))
    red = green = blue = weight = 0.0
    cells = 0
    for row in range(row0, row1):
        start = row * GRID
        for col in range(col0, col1):
            r, g, b, alpha = surface[start + col]
            cells += 1
            if not alpha:
                continue
            share = alpha / 255
            red += r * share
            green += g * share
            blue += b * share
            weight += share
    if not cells or not weight:
        return (0.0, 0.0, 0.0), 0.0
    return (red / weight, green / weight, blue / weight), weight / cells


def disc_pixel(
    surface: Sequence[tuple[int, int, int, int]],
    x0: float,
    y0: float,
    step: float,
    distance: float,
) -> tuple[int, int, int, int]:
    """The colour inside the ring: the disc's own field, with the sprite over it.

    The SVG clips the sprite to `INSET` and leaves the rest of the cutout empty;
    here that gap is filled with the field, because a raster has no toolbar to
    show through and a transparent hole would read as damage.
    """
    if distance > INSET:
        return (*DISC, 255)
    colour, coverage = disc_sample(surface, x0, y0, x0 + step, y0 + step)
    if not coverage:
        return (*DISC, 255)
    return (*blend_ink(colour, coverage), 255)


def rasterise(
    surface: Sequence[tuple[int, int, int, int]], size: int
) -> list[tuple[int, int, int, int]]:
    """Draw the mark into a size x size RGBA buffer, row-major.

    This is the SVG's geometry evaluated per pixel instead of described as shapes:
    the same ring radius, stroke width, clip circle and placement, so the raster
    cannot drift from the vector. The ring and the outer edge are decided by where
    the pixel's centre falls, which keeps the ring an even band at every size
    instead of one that thickens where the circle cuts diagonally.

    Inside the disc the art is *averaged* over the whole footprint rather than
    point-sampled from whichever cell the centre happens to land in. At 16px an
    output pixel spans about 2.3 sprite pixels, so a point sample reads less than
    half the art in each axis — and it is the eyes and the nose that go, exactly
    the loss `downsample` box-averages a level up to avoid.
    """
    factor = size / CANVAS
    step = CANVAS / size
    ring_inner = RING_RADIUS - RING_WIDTH
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(size):
        for x in range(size):
            # The pixel's centre, back in the 32x32 viewBox the geometry lives in.
            cx = (x + 0.5) / factor
            cy = (y + 0.5) / factor
            distance = math.hypot(cx - CENTRE, cy - CENTRE)
            if distance > RING_RADIUS:
                pixels.append((0, 0, 0, 0))  # outside the mark entirely
            elif distance >= ring_inner:
                pixels.append((*RING_INK, 255))  # the ring's stroke
            else:
                pixels.append(disc_pixel(surface, x * step, y * step, step, distance))
    return pixels


def encode_ico(images: Sequence[tuple[int, bytes]]) -> bytes:
    """Wrap PNG payloads in an ICO container.

    An ICO is a directory of sizes and offsets followed by the images themselves.
    PNG payloads are legal in it and are what every browser since Vista reads, so
    the older BMP-in-ICO form would mean a second encoder for no gain. The size
    field is one byte wide, so 256 is written as 0 — the documented escape for
    "the largest size this field can name".
    """
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = bytearray()
    payloads = bytearray()
    offset = len(header) + 16 * len(images)
    for size, payload in images:
        byte = 0 if size >= 256 else size
        entries.extend(struct.pack("<BBBBHHII", byte, byte, 0, 0, 1, 32, len(payload), offset))
        payloads.extend(payload)
        offset += len(payload)
    return bytes(header) + bytes(entries) + bytes(payloads)


def build_ico(rects: Sequence[Rect]) -> bytes:
    """Rasterise the mark at every documented size and wrap the PNGs in an ICO."""
    surface = paint(rects)
    images = [(size, encode_png(rasterise(surface, size), size, size)) for size in ICO_SIZES]
    return encode_ico(images)


def rebuild_ico() -> int:
    """Rebuild favicon.ico from the committed icon.svg.

    This is the mode a fresh checkout uses, and the one that keeps the raster
    honest: the art comes from the file the vector half of this script wrote, so
    there is no second rendering of the sprite that could disagree with it.
    """
    if not OUT_PATH.is_file():
        print(f"no committed icon to read: {OUT_PATH}")
        return 1
    rects = parse_rects(OUT_PATH.read_text(encoding="utf-8"))
    if not rects:
        print(f"no sprite runs found in {OUT_PATH}")
        return 1
    ico = build_ico(rects)
    ICO_PATH.write_bytes(ico)
    sizes = " + ".join(str(size) for size in ICO_SIZES)
    print(f"source     : {OUT_PATH}")
    print(f"runs       : {len(rects)} rects")
    print(f"surface    : {GRID}x{GRID} sampling cells")
    print(f"wrote      : {ICO_PATH} ({len(ico)} bytes, {sizes}, {len(SPRITE_RAMP)} sprite shades)")
    return 0


def render_svg(rects: Sequence[Rect]) -> str:
    """Compose the favicon: the sprite knocked into a circular cutout, plus a ring."""
    ring_radius = RING_RADIUS - RING_WIDTH / 2
    body = "\n    ".join(format_rects(rects))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  PokéCipher favicon. Generated by docs/make_favicon.py — do not edit by hand.

  The art is the Generation 1 Pikachu sprite from Pokémon Yellow, the era the
  Game Boy palette in DESIGN.md comes from. Its white paper background is flood
  filled away, the result is box-averaged down to favicon resolution, and what
  survives is scaled uniformly to fit inside a circular cutout. Each rect is one
  horizontal run of same-coloured pixels; transparent pixels are simply not
  emitted, so the mark has no background of its own.

  The ring is the only theme-aware part. It is black on a light browser toolbar
  and white on a dark one, because a favicon is drawn in the browser's own
  chrome rather than in the page, so it cannot see the app's next-themes toggle
  — prefers-color-scheme is the only signal available to it. Switching the
  app's theme therefore will not recolour the tab icon.

  Sprite art is the property of Nintendo / Game Freak / Creatures Inc.
-->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}"
     width="{CANVAS}" height="{CANVAS}" role="img" aria-labelledby="pokecipher-icon-title">
  <title id="pokecipher-icon-title">PokéCipher</title>

  <style>
    svg {{ --ink: {INK_LIGHT}; }}
    @media (prefers-color-scheme: dark) {{ svg {{ --ink: {INK_DARK}; }} }}
    .ring {{ fill: none; stroke: var(--ink); stroke-width: {fmt(RING_WIDTH)}; }}
  </style>

  <defs>
    <clipPath id="cutout">
      <circle cx="{fmt(CENTRE)}" cy="{fmt(CENTRE)}" r="{fmt(INSET)}"/>
    </clipPath>
  </defs>

  <!-- crispEdges keeps the sprite's pixel boundaries hard; without it the
       browser anti-aliases every rect edge and the pixel art turns to mush. -->
  <g clip-path="url(#cutout)" shape-rendering="crispEdges">
    {body}
  </g>

  <circle class="ring" cx="{fmt(CENTRE)}" cy="{fmt(CENTRE)}" r="{fmt(ring_radius)}"/>
</svg>
"""


def main(argv: Sequence[str]) -> int:
    """Write next-app/app/icon.svg and favicon.ico.

    With no argument only the ICO is rebuilt, from the committed SVG — the route a
    fresh checkout has. With a sprite path both files are rebuilt from that
    sprite, which is how a new download is adopted.
    """
    if len(argv) > 2:
        print("usage: python docs/make_favicon.py [sprite.png]")
        return 2
    if len(argv) == 1:
        return rebuild_ico()

    source = Path(argv[1])
    if not source.is_file():
        print(f"no such sprite: {source}")
        return 1

    raw = decode_png(source)
    art = prepare(raw)
    placement = place(art)
    rects = rects_from_sprite(art, placement.scale, placement.origin)
    svg = render_svg(rects)
    # newline="\n" keeps the generated bytes platform-independent: without it
    # write_text translates to CRLF on Windows, so the committed asset would
    # depend on which machine last re-ran this script.
    OUT_PATH.write_text(svg, encoding="utf-8", newline="\n")

    ico = build_ico(rects)
    ICO_PATH.write_bytes(ico)

    bounds = placement.bounds
    opaque = sum(1 for pixel in art.pixels if pixel[3])
    shades = len({sprite_ink(pixel) for pixel in art.pixels if pixel[3]})
    sizes = " + ".join(str(size) for size in ICO_SIZES)
    print(f"source     : {source}")
    print(f"sprite     : {raw.width}x{raw.height} -> {art.width}x{art.height} after knock-out")
    print(f"opaque     : {opaque} pixels")
    print(f"opaque box : {bounds.right - bounds.left + 1}x{bounds.bottom - bounds.top + 1}")
    print(f"pixel scale: {placement.scale:.4f} (uniform, so pixels stay square)")
    print(f"clipped    : {clipped_count(art, bounds, placement.scale, placement.origin)} trimmed")
    print(f"runs       : {len(rects)} rects")
    print(f"wrote      : {OUT_PATH} ({len(svg.encode('utf-8'))} bytes)")
    print(f"wrote      : {ICO_PATH} ({len(ico)} bytes, {sizes}, {shades} sprite shades)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
