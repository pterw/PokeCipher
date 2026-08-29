"""Backwards-compatible entry point for the PokéCipher codec.

The implementation now lives in the :mod:`pokecipher` package, split into
focused modules. This module re-exports the historical names so that existing
imports and the existing test-suite keep working unchanged.

New code should import from ``pokecipher`` directly and let this shim fade out.
"""

from pokecipher import (
    ASCII_MAX,
    ASCII_MIN,
    MAX_DECODE_BRANCHES,
    NAME_INDEX,
    NUM_REGIONS,
    REGION_LISTS,
    REGION_NAMES,
    REGION_SIZE,
    REGIONS,
    decode_flexible_error_reporting,
    decode_message,
    encode_message,
)

# Names kept in their historical lower-case spelling for backwards compatibility.
regions = REGIONS
region_names = REGION_NAMES
num_regions = NUM_REGIONS
name_to_mappings = NAME_INDEX

__all__ = [
    "ASCII_MAX",
    "ASCII_MIN",
    "MAX_DECODE_BRANCHES",
    "NAME_INDEX",
    "NUM_REGIONS",
    "REGION_LISTS",
    "REGION_NAMES",
    "REGION_SIZE",
    "REGIONS",
    "decode_flexible_error_reporting",
    "decode_message",
    "encode_message",
    "name_to_mappings",
    "num_regions",
    "region_names",
    "regions",
]
