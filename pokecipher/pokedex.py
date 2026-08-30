"""Regional Pokédex data and the derived name → (character, region) lookup index.

The Pokédex lists are the single source of truth for the whole cipher. They are
validated at import time: a malformed list raises :class:`PokedexError`
immediately instead of surfacing later as an ``IndexError`` during encoding or
as silently wrong ciphertext.

Invariants enforced here (and relied upon by the encoder):

* at least one region is defined;
* every region supplies at least ``REGION_SIZE`` (95) names;
* names are non-empty and stripped;
* names are unique *within* a region.

Names may repeat *across* regions — that overlap is deliberate and is exactly
what produces the cipher's ambiguities.
"""

from __future__ import annotations

from .constants import ASCII_MIN, REGION_SIZE
from .errors import PokedexError

RegionName = str
PokemonName = str

#: Mapping of region name → regional Pokédex, in Pokédex order.
#: Pokémon #N sits at list index N-1; index 0 encodes ASCII 32 (space).
# fmt: off
REGIONS: dict[RegionName, tuple[PokemonName, ...]] = {
    "Kanto": (
        "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",    # 1-6
        "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",      # 7-12
        "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot",               # 13-18
        "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok",                   # 19-24
        "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran-F", "Nidorina",         # 25-30
        "Nidoqueen", "Nidoran-M", "Nidorino", "Nidoking", "Clefairy", "Clefable",       # 31-36
        "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff", "Zubat", "Golbat",           # 37-42
        "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat",                 # 43-48
        "Venomoth", "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck",               # 49-54
        "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine", "Poliwag",            # 55-60
        "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",              # 61-66
        "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",    # 67-72
        "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash",             # 73-78
        "Slowpoke", "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo",          # 79-84
        "Dodrio", "Seel", "Dewgong", "Grimer", "Muk", "Shellder",                       # 85-90
        "Cloyster", "Gastly", "Haunter", "Gengar", "Onix",                              # 91-95
    ),
    "Johto": (
        "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion",       # 1-6
        "Totodile", "Croconaw", "Feraligatr", "Pidgey", "Pidgeotto", "Pidgeot",         # 7-12
        "Spearow", "Fearow", "Hoothoot", "Noctowl", "Rattata", "Raticate",              # 13-18
        "Sentret", "Furret", "Pichu", "Pikachu", "Raichu", "Caterpie",                  # 19-24
        "Metapod", "Butterfree", "Weedle", "Kakuna", "Beedrill", "Ledyba",              # 25-30
        "Ledian", "Spinarak", "Ariados", "Geodude", "Graveler", "Golem",                # 31-36
        "Zubat", "Golbat", "Crobat", "Cleffa", "Clefairy", "Clefable",                  # 37-42
        "Igglybuff", "Jigglypuff", "Wigglytuff", "Togepi", "Togetic", "Sandshrew",      # 43-48
        "Sandslash", "Ekans", "Arbok", "Dunsparce", "Mareep", "Flaaffy",                # 49-54
        "Ampharos", "Wooper", "Quagsire", "Gastly", "Haunter", "Gengar",                # 55-60
        "Unown", "Onix", "Steelix", "Bellsprout", "Weepinbell", "Victreebel",           # 61-66
        "Hoppip", "Skiploom", "Jumpluff", "Paras", "Parasect", "Poliwag",               # 67-72
        "Poliwhirl", "Poliwrath", "Politoed", "Magikarp", "Gyarados", "Goldeen",        # 73-78
        "Seaking", "Slowpoke", "Slowbro", "Slowking", "Oddish", "Gloom",                # 79-84
        "Vileplume", "Bellossom", "Drowzee", "Hypno", "Abra", "Kadabra",                # 85-90
        "Alakazam", "Ditto", "Pineco", "Forretress", "Nidoran-F",                       # 91-95
    ),
    "Hoenn": (
        "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken",           # 1-6
        "Mudkip", "Marshtomp", "Swampert", "Poochyena", "Mightyena", "Zigzagoon",       # 7-12
        "Linoone", "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox",              # 13-18
        "Lotad", "Lombre", "Ludicolo", "Seedot", "Nuzleaf", "Shiftry",                  # 19-24
        "Taillow", "Swellow", "Wingull", "Pelipper", "Ralts", "Kirlia",                 # 25-30
        "Gardevoir", "Surskit", "Masquerain", "Shroomish", "Breloom", "Slakoth",        # 31-36
        "Vigoroth", "Slaking", "Abra", "Kadabra", "Alakazam", "Nincada",                # 37-42
        "Ninjask", "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita",             # 43-48
        "Hariyama", "Goldeen", "Seaking", "Magikarp", "Gyarados", "Azurill",            # 49-54
        "Marill", "Azumarill", "Geodude", "Graveler", "Golem", "Nosepass",              # 55-60
        "Skitty", "Delcatty", "Zubat", "Golbat", "Crobat", "Tentacool",                 # 61-66
        "Tentacruel", "Sableye", "Mawile", "Aron", "Lairon", "Aggron",                  # 67-72
        "Machop", "Machoke", "Machamp", "Meditite", "Medicham", "Electrike",            # 73-78
        "Manectric", "Plusle", "Minun", "Magnemite", "Magneton", "Voltorb",             # 79-84
        "Electrode", "Volbeat", "Illumise", "Oddish", "Gloom", "Vileplume",             # 85-90
        "Bellossom", "Doduo", "Dodrio", "Roselia", "Gulpin",                            # 91-95
    ),
}
# fmt: on

#: Region names in cycling order. Kept as a list: it is part of the package's
#: public, historically-consumed API surface.
REGION_NAMES: list[RegionName] = list(REGIONS)

#: Number of regions the cipher cycles through.
NUM_REGIONS: int = len(REGION_NAMES)

#: The Pokédex lists, in cycling order, as the encoder consumes them.
REGION_LISTS: tuple[tuple[PokemonName, ...], ...] = tuple(REGIONS[name] for name in REGION_NAMES)


def validate_regions(
    regions: dict[RegionName, tuple[PokemonName, ...]],
    region_names: list[RegionName],
) -> None:
    """Validate Pokédex data, raising :class:`PokedexError` on the first problem found.

    Failing fast here is what lets the encoder index the regional lists directly
    without bounds checks, and what makes a "character outside the Pokédex"
    error path unreachable rather than merely untested.
    """
    if not region_names:
        raise PokedexError("At least one region must be defined.")

    for name in region_names:
        if not name or name.strip() != name:
            raise PokedexError(f"Region name {name!r} must be a non-empty, stripped string.")
        if name not in regions:
            raise PokedexError(f"Region {name!r} is listed in REGION_NAMES but has no data.")

    for name in region_names:
        pokemon = regions[name]
        if len(pokemon) < REGION_SIZE:
            raise PokedexError(
                f"Region {name!r} has {len(pokemon)} entries but needs at least {REGION_SIZE}."
            )
        seen: set[PokemonName] = set()
        for entry in pokemon:
            if not entry or entry.strip() != entry:
                raise PokedexError(
                    f"Region {name!r} contains a blank or untrimmed name: {entry!r}."
                )
            if entry in seen:
                raise PokedexError(f"Region {name!r} contains a duplicate name: {entry!r}.")
            seen.add(entry)


def build_name_index(
    regions: dict[RegionName, tuple[PokemonName, ...]],
    region_names: list[RegionName],
) -> dict[PokemonName, list[tuple[str, int]]]:
    """Build the decoder's lookup table: Pokémon name → candidate (character, region) pairs.

    Only the first ``REGION_SIZE`` entries of each region are indexed, which is
    exactly the range the encoder can address.
    """
    index: dict[PokemonName, list[tuple[str, int]]] = {}
    for region_index, region_name in enumerate(region_names):
        pokemon = regions[region_name]
        for offset in range(REGION_SIZE):
            index.setdefault(pokemon[offset], []).append((chr(offset + ASCII_MIN), region_index))
    return index


validate_regions(REGIONS, REGION_NAMES)

#: Pokémon name → every (character, region index) pair it can represent.
NAME_INDEX: dict[PokemonName, list[tuple[str, int]]] = build_name_index(REGIONS, REGION_NAMES)


def build_folded_index(
    index: dict[PokemonName, list[tuple[str, int]]],
) -> dict[str, list[tuple[str, int]]]:
    """Build a case-folded view of ``index`` for tolerant decoding.

    Raises :class:`PokedexError` if two distinct names fold together with
    different mappings, which would make case-insensitive lookup ambiguous in a
    way the cased index is not. Checked here rather than assumed, in keeping with
    the module's fail-at-import contract.
    """
    folded: dict[str, list[tuple[str, int]]] = {}
    for name, mappings in index.items():
        key = name.casefold()
        existing = folded.get(key)
        if existing is not None and existing != mappings:
            raise PokedexError(f"Case-folded name collision on {key!r}.")
        folded[key] = mappings
    return folded


#: Case-folded view of :data:`NAME_INDEX`, for :func:`lookup_name`.
FOLDED_NAME_INDEX: dict[str, list[tuple[str, int]]] = build_folded_index(NAME_INDEX)


def lookup_name(token: PokemonName) -> list[tuple[str, int]] | None:
    """Return the candidate (character, region) pairs for ``token``, ignoring case.

    Produce strictly, consume tolerantly. The encoder only ever emits canonical
    capitalisation, but ciphertext routed through a URL, a chat client or a
    spreadsheet often arrives lowercased, and the failure is silent: every token
    becomes ``<?unknown: ...>`` with nothing to indicate that case was the cause.
    """
    mappings = NAME_INDEX.get(token)
    if mappings is not None:
        return mappings
    return FOLDED_NAME_INDEX.get(token.casefold())
