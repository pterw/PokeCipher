"""Regression tests for the generated favicon and app icon.

`favicon.ico` is a build artefact, so these tests pin the two properties that
broke it rather than merely re-running the generator:

1. it is a rasterisation of the committed `icon.svg`, so the two cannot disagree;
2. no sprite ink is ever painted in the disc's own field colour.

They read the committed files, because the committed files are what ships. The
generator is imported by path: `docs` is deliberately not a package.
"""

from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATOR = ROOT / "docs" / "make_favicon.py"
ICON = ROOT / "next-app" / "app" / "icon.svg"
ICO = ROOT / "next-app" / "app" / "favicon.ico"


def load_generator():
    """Import docs/make_favicon.py by path, registering it under a module name."""
    spec = importlib.util.spec_from_file_location("make_favicon", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


favicon = load_generator()


def ico_entries(path: Path) -> dict[int, bytes]:
    """Read an ICO directory: entry size -> its PNG payload."""
    raw = path.read_bytes()
    reserved, kind, count = struct.unpack_from("<HHH", raw, 0)
    if (reserved, kind) != (0, 1):
        raise ValueError(f"{path} is not an ICO")
    entries: dict[int, bytes] = {}
    for index in range(count):
        width, _height, _colours, _pad, _planes, _bits, length, start = struct.unpack_from(
            "<BBBBHHII", raw, 6 + 16 * index
        )
        # The size field is one byte wide, so 256 is stored as the documented 0.
        entries[width or 256] = raw[start : start + length]
    return entries


def ico_pixels(path: Path, size: int) -> list[tuple[int, int, int, int]]:
    """Decode one ICO entry with the generator's own PNG reader."""
    payload = ico_entries(path)[size]
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder) / f"{size}.png"
        temp.write_bytes(payload)
        sprite = favicon.decode_png(temp)
    if (sprite.width, sprite.height) != (size, size):
        raise AssertionError(f"entry {size} decoded as {sprite.width}x{sprite.height}")
    return sprite.pixels


def committed_rects() -> list:
    """The runs the committed SVG describes."""
    return favicon.parse_rects(ICON.read_text(encoding="utf-8"))


class TestTheIcoRasterisesTheCommittedSvg(unittest.TestCase):
    """favicon.ico is a rasterisation of the committed icon.svg."""

    def test_the_ico_carries_one_entry_per_documented_size(self):
        """The ICO holds exactly the sizes the generator documents."""
        self.assertEqual(sorted(ico_entries(ICO)), sorted(favicon.ICO_SIZES))

    def test_every_entry_matches_a_fresh_rasterisation_of_the_svg(self):
        """Each entry equals the rasteriser run over the committed SVG's runs."""
        surface = favicon.paint(committed_rects())
        for size in favicon.ICO_SIZES:
            with self.subTest(size=size):
                self.assertEqual(ico_pixels(ICO, size), favicon.rasterise(surface, size))

    def test_regenerating_the_ico_is_deterministic(self):
        """Building the ICO twice from the same runs produces identical bytes."""
        rects = committed_rects()
        self.assertEqual(favicon.build_ico(rects), favicon.build_ico(rects))

    def test_the_smallest_entry_is_mostly_sprite(self):
        """The 16px entry the browser draws holds sprite ink, not bare field."""
        pixels = ico_pixels(ICO, 16)
        inside = [
            pixel
            for pixel in pixels
            if pixel[3] and pixel[:3] not in (favicon.DISC, favicon.RING_INK)
        ]
        self.assertGreater(len(inside), 20)


class TestTheCommittedSvgRoundTrips(unittest.TestCase):
    """The generator can read back the SVG it wrote."""

    def test_every_rect_in_the_svg_is_parsed(self):
        """The parser finds every <rect> the file contains."""
        svg = ICON.read_text(encoding="utf-8")
        self.assertEqual(len(favicon.parse_rects(svg)), svg.count("<rect"))

    def test_reformatting_the_parsed_runs_reproduces_the_svg_lines(self):
        """Serialising the parsed runs reproduces the committed <rect> lines."""
        svg = ICON.read_text(encoding="utf-8")
        lines = favicon.format_rects(favicon.parse_rects(svg))
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(line, svg)

    def test_fill_opacity_survives_the_round_trip(self):
        """A partly transparent run keeps its alpha exactly."""
        rects = favicon.parse_rects(ICON.read_text(encoding="utf-8"))
        partial = [rect for rect in rects if rect.rgba[3] not in (0, 255)]
        self.assertTrue(partial, "the committed SVG carries no translucent runs")
        for rect in partial:
            with self.subTest(rect=rect):
                self.assertEqual(favicon.parse_rects(favicon.format_rects([rect])[0])[0], rect)


class TestSpriteInkStaysOffTheField(unittest.TestCase):
    """The sprite must stay visible against the disc's own field."""

    def test_the_field_is_not_a_shade_the_sprite_draws_with(self):
        """The disc's field colour is excluded from the sprite's ramp."""
        self.assertNotIn(favicon.DISC, favicon.SPRITE_RAMP)

    def test_black_ink_does_not_quantise_onto_the_field(self):
        """Pikachu's blackest pixels are not painted in the background colour."""
        self.assertNotEqual(favicon.sprite_ink((0, 0, 0, 255)), favicon.DISC)

    def test_no_opaque_grey_collapses_into_the_field(self):
        """Every opaque grey the sprite can hold stays clear of the field."""
        for level in range(256):
            with self.subTest(level=level):
                self.assertNotEqual(favicon.sprite_ink((level, level, level, 255)), favicon.DISC)

    def test_the_sprite_ramp_reads_against_the_field(self):
        """The sprite's darkest shade is measurably lighter than the field."""
        field = favicon.luminance(favicon.DISC)
        darkest = min(favicon.luminance(shade) for shade in favicon.SPRITE_RAMP)
        self.assertGreater(darkest - field, 20.0)

    def test_the_smallest_entry_still_carries_the_outline(self):
        """The 16px entry contains the sprite's darkest shade, not just field."""
        inks = {pixel[:3] for pixel in ico_pixels(ICO, 16) if pixel[3]}
        self.assertIn(favicon.DISC, inks)
        self.assertIn(favicon.SPRITE_RAMP[0], inks)


class TestTheRasterAveragesItsFootprint(unittest.TestCase):
    """Downsizing averages the art instead of point-sampling it."""

    @staticmethod
    def striped_surface(column: int) -> list[tuple[int, int, int, int]]:
        """A GRID x GRID surface holding one opaque white column."""
        surface = [(0, 0, 0, 0)] * (favicon.GRID * favicon.GRID)
        for row in range(favicon.GRID):
            surface[row * favicon.GRID + column] = (255, 255, 255, 255)
        return surface

    def test_a_narrow_feature_still_reports_coverage(self):
        """A one-cell stripe keeps a proportionate share of a whole-canvas footprint."""
        colour, coverage = favicon.disc_sample(
            self.striped_surface(favicon.GRID // 3), 0.0, 0.0, favicon.CANVAS, favicon.CANVAS
        )
        self.assertAlmostEqual(coverage, 1 / favicon.GRID, places=6)
        self.assertAlmostEqual(colour[0], 255.0, places=6)

    def test_a_narrow_feature_reaches_the_rasterised_pixel(self):
        """A stripe a point sample would step over still tints its output pixel."""
        pixel = favicon.disc_pixel(
            self.striped_surface(favicon.GRID // 3), 0.0, 0.0, favicon.CANVAS, 0.0
        )
        self.assertNotEqual(pixel[:3], favicon.DISC)

    def test_an_untouched_footprint_returns_the_field(self):
        """A footprint the sprite misses is the field, not an unquantised black."""
        empty = [(0, 0, 0, 0)] * (favicon.GRID * favicon.GRID)
        self.assertEqual(
            favicon.disc_pixel(empty, 0.0, 0.0, favicon.CANVAS, 0.0), (*favicon.DISC, 255)
        )

    def test_outside_the_ring_stays_transparent(self):
        """A pixel beyond the ring radius is left fully transparent."""
        empty = [(0, 0, 0, 0)] * (favicon.GRID * favicon.GRID)
        pixels = favicon.rasterise(empty, favicon.CANVAS)
        corners = (pixels[0], pixels[favicon.CANVAS - 1], pixels[-favicon.CANVAS])
        self.assertEqual(corners, ((0, 0, 0, 0),) * 3)
