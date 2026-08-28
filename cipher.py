# Pokémon cipher encoding/decoding functions

# Correctly ordered lists for the first 95 entries (index 0-94)
# Mapping ASCII 32 (space) to index 0, up to ASCII 126 (~) to index 94
# Pokedex #N is at List Index [N-1]
regions = {
    # Corrected Kanto Regional Dex
    "Kanto": [
        "Bulbasaur",
        "Ivysaur",
        "Venusaur",
        "Charmander",
        "Charmeleon",
        "Charizard",  # 1-6
        "Squirtle",
        "Wartortle",
        "Blastoise",
        "Caterpie",
        "Metapod",
        "Butterfree",  # 7-12
        "Weedle",
        "Kakuna",
        "Beedrill",
        "Pidgey",
        "Pidgeotto",
        "Pidgeot",  # 13-18
        "Rattata",
        "Raticate",
        "Spearow",
        "Fearow",
        "Ekans",
        "Arbok",  # 19-24
        "Pikachu",
        "Raichu",
        "Sandshrew",
        "Sandslash",
        "Nidoran-F",
        "Nidorina",  # 25-30
        "Nidoqueen",
        "Nidoran-M",
        "Nidorino",
        "Nidoking",
        "Clefairy",
        "Clefable",  # 31-36
        "Vulpix",
        "Ninetales",
        "Jigglypuff",
        "Wigglytuff",
        "Zubat",
        "Golbat",  # 37-42 (#40=Wigglytuff@39, #41=Zubat@40)
        "Oddish",
        "Gloom",
        "Vileplume",
        "Paras",
        "Parasect",
        "Venonat",  # 43-48
        "Venomoth",
        "Diglett",
        "Dugtrio",
        "Meowth",
        "Persian",
        "Psyduck",  # 49-54 (#54=Psyduck@53)
        "Golduck",
        "Mankey",
        "Primeape",
        "Growlithe",
        "Arcanine",
        "Poliwag",  # 55-60 (#55=Golduck@54, #56=Mankey@55, #57=Primeape@56)
        "Poliwhirl",
        "Poliwrath",
        "Abra",
        "Kadabra",
        "Alakazam",
        "Machop",  # 61-66
        "Machoke",
        "Machamp",
        "Bellsprout",
        "Weepinbell",
        "Victreebel",
        "Tentacool",  # 67-72 (#68=Machamp@67, #69=Bellsprout@68, #70=Weepinbell@69)
        "Tentacruel",
        "Geodude",
        "Graveler",
        "Golem",
        "Ponyta",
        "Rapidash",  # 73-78 (#76=Golem@75, #77=Ponyta@76)
        "Slowpoke",
        "Slowbro",
        "Magnemite",
        "Magneton",
        "Farfetch'd",
        "Doduo",  # 79-84 (#79=Slowpoke@78, #80=Slowbro@79, #81=Magnemite@80, #82=Magneton@81, #83=Farfetch'd@82)
        "Dodrio",
        "Seel",
        "Dewgong",
        "Grimer",
        "Muk",
        "Shellder",  # 85-90
        "Cloyster",
        "Gastly",
        "Haunter",
        "Gengar",
        "Onix",  # 91-95 (#95=Onix@94)
    ],
    # Corrected Johto Regional Dex
    "Johto": [
        "Chikorita",
        "Bayleef",
        "Meganium",
        "Cyndaquil",
        "Quilava",
        "Typhlosion",  # 1-6
        "Totodile",
        "Croconaw",
        "Feraligatr",
        "Pidgey",
        "Pidgeotto",
        "Pidgeot",  # 7-12   (#10=Pidgey@9)
        "Spearow",
        "Fearow",
        "Hoothoot",
        "Noctowl",
        "Rattata",
        "Raticate",  # 13-18
        "Sentret",
        "Furret",
        "Pichu",
        "Pikachu",
        "Raichu",
        "Caterpie",  # 19-24
        "Metapod",
        "Butterfree",
        "Weedle",
        "Kakuna",
        "Beedrill",
        "Ledyba",  # 25-30
        "Ledian",
        "Spinarak",
        "Ariados",
        "Geodude",
        "Graveler",
        "Golem",  # 31-36  (#34=Geodude@33, #36=Golem@35)
        "Zubat",
        "Golbat",
        "Crobat",
        "Cleffa",
        "Clefairy",
        "Clefable",  # 37-42  (#40=Cleffa@39)
        "Igglybuff",
        "Jigglypuff",
        "Wigglytuff",
        "Togepi",
        "Togetic",
        "Sandshrew",  # 43-48
        "Sandslash",
        "Ekans",
        "Arbok",
        "Dunsparce",
        "Mareep",
        "Flaaffy",  # 49-54
        "Ampharos",
        "Wooper",
        "Quagsire",
        "Gastly",
        "Haunter",
        "Gengar",  # 55-60
        "Unown",
        "Onix",
        "Steelix",
        "Bellsprout",
        "Weepinbell",
        "Victreebel",  # 61-66  (#64=Bellsprout@63, #65=Weepinbell@64)
        "Hoppip",
        "Skiploom",
        "Jumpluff",
        "Paras",
        "Parasect",
        "Poliwag",  # 67-72
        "Poliwhirl",
        "Poliwrath",
        "Politoed",
        "Magikarp",
        "Gyarados",
        "Goldeen",  # 73-78  (#76=Magikarp@75, #77=Gyarados@76)
        "Seaking",
        "Slowpoke",
        "Slowbro",
        "Slowking",
        "Oddish",
        "Gloom",  # 79-84  (#79=Seaking@78, #80=Slowpoke@79, #81=Slowbro@80)
        "Vileplume",
        "Bellossom",
        "Drowzee",
        "Hypno",
        "Abra",
        "Kadabra",  # 85-90
        "Alakazam",
        "Ditto",
        "Pineco",
        "Forretress",
        "Nidoran-F",  # 91-95 (#95=Nidoran-F@94)
    ],
    # Corrected Hoenn Regional Dex
    "Hoenn": [
        "Treecko",
        "Grovyle",
        "Sceptile",
        "Torchic",
        "Combusken",
        "Blaziken",  # 1-6
        "Mudkip",
        "Marshtomp",
        "Swampert",
        "Poochyena",
        "Mightyena",
        "Zigzagoon",  # 7-12
        "Linoone",
        "Wurmple",
        "Silcoon",
        "Beautifly",
        "Cascoon",
        "Dustox",  # 13-18
        "Lotad",
        "Lombre",
        "Ludicolo",
        "Seedot",
        "Nuzleaf",
        "Shiftry",  # 19-24
        "Taillow",
        "Swellow",
        "Wingull",
        "Pelipper",
        "Ralts",
        "Kirlia",  # 25-30
        "Gardevoir",
        "Surskit",
        "Masquerain",
        "Shroomish",
        "Breloom",
        "Slakoth",  # 31-36
        "Vigoroth",
        "Slaking",
        "Abra",
        "Kadabra",
        "Alakazam",
        "Nincada",  # 37-42 (#39=Abra@38)
        "Ninjask",
        "Shedinja",
        "Whismur",
        "Loudred",
        "Exploud",
        "Makuhita",  # 43-48
        "Hariyama",
        "Goldeen",
        "Seaking",
        "Magikarp",
        "Gyarados",
        "Azurill",  # 49-54 (#53=Gyarados@52)
        "Marill",
        "Azumarill",
        "Geodude",
        "Graveler",
        "Golem",
        "Nosepass",  # 55-60 (#57=Geodude@56, #59=Golem@58)
        "Skitty",
        "Delcatty",
        "Zubat",
        "Golbat",
        "Crobat",
        "Tentacool",  # 61-66 (#63=Zubat@62, #66=Tentacool@65)
        "Tentacruel",
        "Sableye",
        "Mawile",
        "Aron",
        "Lairon",
        "Aggron",  # 67-72 (#68=Sableye@67, #69=Mawile@68, #70=Aron@69)
        "Machop",
        "Machoke",
        "Machamp",
        "Meditite",
        "Medicham",
        "Electrike",  # 73-78 (#75=Machamp@74, #76=Meditite@75, #77=Medicham@76)
        "Manectric",
        "Plusle",
        "Minun",
        "Magnemite",
        "Magneton",
        "Voltorb",  # 79-84 (#82=Magnemite@81, #83=Magneton@82)
        "Electrode",
        "Volbeat",
        "Illumise",
        "Oddish",
        "Gloom",
        "Vileplume",  # 85-90 (#88=Oddish@87)
        "Bellossom",
        "Doduo",
        "Dodrio",
        "Roselia",
        "Gulpin",  # 91-95 (#95=Gulpin@94)
    ],
}

NATIONAL_DEX = {
    "Bulbasaur": 1,
    "Ivysaur": 2,
    "Venusaur": 3,
    "Charmander": 4,
    "Charmeleon": 5,
    "Charizard": 6,
    "Squirtle": 7,
    "Wartortle": 8,
    "Blastoise": 9,
    "Caterpie": 10,
    "Metapod": 11,
    "Butterfree": 12,
    "Weedle": 13,
    "Kakuna": 14,
    "Beedrill": 15,
    "Pidgey": 16,
    "Pidgeotto": 17,
    "Pidgeot": 18,
    "Rattata": 19,
    "Raticate": 20,
    "Spearow": 21,
    "Fearow": 22,
    "Ekans": 23,
    "Arbok": 24,
    "Pikachu": 25,
    "Raichu": 26,
    "Sandshrew": 27,
    "Sandslash": 28,
    "Nidoran-F": 29,
    "Nidorina": 30,
    "Nidoqueen": 31,
    "Nidoran-M": 32,
    "Nidorino": 33,
    "Nidoking": 34,
    "Clefairy": 35,
    "Clefable": 36,
    "Vulpix": 37,
    "Ninetales": 38,
    "Jigglypuff": 39,
    "Wigglytuff": 40,
    "Zubat": 41,
    "Golbat": 42,
    "Oddish": 43,
    "Gloom": 44,
    "Vileplume": 45,
    "Paras": 46,
    "Parasect": 47,
    "Venonat": 48,
    "Venomoth": 49,
    "Diglett": 50,
    "Dugtrio": 51,
    "Meowth": 52,
    "Persian": 53,
    "Psyduck": 54,
    "Golduck": 55,
    "Mankey": 56,
    "Primeape": 57,
    "Growlithe": 58,
    "Arcanine": 59,
    "Poliwag": 60,
    "Poliwhirl": 61,
    "Poliwrath": 62,
    "Abra": 63,
    "Kadabra": 64,
    "Alakazam": 65,
    "Machop": 66,
    "Machoke": 67,
    "Machamp": 68,
    "Bellsprout": 69,
    "Weepinbell": 70,
    "Victreebel": 71,
    "Tentacool": 72,
    "Tentacruel": 73,
    "Geodude": 74,
    "Graveler": 75,
    "Golem": 76,
    "Ponyta": 77,
    "Rapidash": 78,
    "Slowpoke": 79,
    "Slowbro": 80,
    "Magnemite": 81,
    "Magneton": 82,
    "Farfetch'd": 83,
    "Doduo": 84,
    "Dodrio": 85,
    "Seel": 86,
    "Dewgong": 87,
    "Grimer": 88,
    "Muk": 89,
    "Shellder": 90,
    "Cloyster": 91,
    "Gastly": 92,
    "Haunter": 93,
    "Gengar": 94,
    "Onix": 95,
    "Drowzee": 96,
    "Hypno": 97,
    "Krabby": 98,
    "Kingler": 99,
    "Voltorb": 100,
    "Electrode": 101,
    "Exeggcute": 102,
    "Exeggutor": 103,
    "Cubone": 104,
    "Marowak": 105,
    "Hitmonlee": 106,
    "Hitmonchan": 107,
    "Lickitung": 108,
    "Koffing": 109,
    "Weezing": 110,
    "Rhyhorn": 111,
    "Rydon": 112,
    "Chansey": 113,
    "Tangela": 114,
    "Kangaskhan": 115,
    "Horsea": 116,
    "Seadra": 117,
    "Goldeen": 118,
    "Seaking": 119,
    "Staryu": 120,
    "Starmie": 121,
    "Mr. Mime": 122,
    "Scyther": 123,
    "Jynx": 124,
    "Electabuzz": 125,
    "Magmar": 126,
    "Pinsir": 127,
    "Tauros": 128,
    "Magikarp": 129,
    "Gyarados": 130,
    "Lapras": 131,
    "Ditto": 132,
    "Eevee": 133,
    "Vaporeon": 134,
    "Jolteon": 135,
    "Flareon": 136,
    "Porygon": 137,
    "Omanyte": 138,
    "Omastar": 139,
    "Kabuto": 140,
    "Kabutops": 141,
    "Aerodactyl": 142,
    "Snorlax": 143,
    "Articuno": 144,
    "Zapdos": 145,
    "Moltres": 146,
    "Dratini": 147,
    "Dragonair": 148,
    "Dragonite": 149,
    "Mewtwo": 150,
    "Mew": 151,
    "Chikorita": 152,
    "Bayleef": 153,
    "Meganium": 154,
    "Cyndaquil": 155,
    "Quilava": 156,
    "Typhlosion": 157,
    "Totodile": 158,
    "Croconaw": 159,
    "Feraligatr": 160,
    "Sentret": 161,
    "Furret": 162,
    "Hoothoot": 163,
    "Noctowl": 164,
    "Ledyba": 165,
    "Ledian": 166,
    "Spinarak": 167,
    "Ariados": 168,
    "Crobat": 169,
    "Chinchou": 170,
    "Lanturn": 171,
    "Pichu": 172,
    "Cleffa": 173,
    "Igglybuff": 174,
    "Togepi": 175,
    "Togetic": 176,
    "Natu": 177,
    "Xatu": 178,
    "Mareep": 179,
    "Flaaffy": 180,
    "Ampharos": 181,
    "Bellossom": 182,
    "Marill": 183,
    "Azumarill": 184,
    "Sudowoodo": 185,
    "Politoed": 186,
    "Hoppip": 187,
    "Skiploom": 188,
    "Jumpluff": 189,
    "Aipom": 190,
    "Sunkern": 191,
    "Sunflora": 192,
    "Yanma": 193,
    "Wooper": 194,
    "Quagsire": 195,
    "Espeon": 196,
    "Umbreon": 197,
    "Murkrow": 198,
    "Slowking": 199,
    "Misdreavus": 200,
    "Unown": 201,
    "Wobbuffet": 202,
    "Girafarig": 203,
    "Pineco": 204,
    "Forretress": 205,
    "Dunsparce": 206,
    "Gligar": 207,
    "Steelix": 208,
    "Snubbull": 209,
    "Granbull": 210,
    "Qwilfish": 211,
    "Scizor": 212,
    "Shuckle": 213,
    "Heracross": 214,
    "Sneasel": 215,
    "Teddiursa": 216,
    "Ursaring": 217,
    "Slugma": 218,
    "Magcargo": 219,
    "Swinub": 220,
    "Piloswine": 221,
    "Corsola": 222,
    "Remoraid": 223,
    "Octillery": 224,
    "Delibird": 225,
    "Mantine": 226,
    "Skarmory": 227,
    "Houndour": 228,
    "Houndoom": 229,
    "Kingdra": 230,
    "Phanpy": 231,
    "Donphan": 232,
    "Porygon2": 233,
    "Stantler": 234,
    "Smeargle": 235,
    "Tyrogue": 236,
    "Hitmontop": 237,
    "Smoochum": 238,
    "Elekid": 239,
    "Magby": 240,
    "Miltank": 241,
    "Blissey": 242,
    "Raikou": 243,
    "Entei": 244,
    "Suicune": 245,
    "Larvitar": 246,
    "Pupitar": 247,
    "Tyranitar": 248,
    "Lugia": 249,
    "Ho-Oh": 250,
    "Celebi": 251,
    "Treecko": 252,
    "Grovyle": 253,
    "Sceptile": 254,
    "Torchic": 255,
    "Combusken": 256,
    "Blaziken": 257,
    "Mudkip": 258,
    "Marshtomp": 259,
    "Swampert": 260,
    "Poochyena": 261,
    "Mightyena": 262,
    "Zigzagoon": 263,
    "Linoone": 264,
    "Wurmple": 265,
    "Silcoon": 266,
    "Beautifly": 267,
    "Cascoon": 268,
    "Dustox": 269,
    "Lotad": 270,
    "Lombre": 271,
    "Ludicolo": 272,
    "Seedot": 273,
    "Nuzleaf": 274,
    "Shiftry": 275,
    "Taillow": 276,
    "Swellow": 277,
    "Wingull": 278,
    "Pelipper": 279,
    "Ralts": 280,
    "Kirlia": 281,
    "Gardevoir": 282,
    "Surskit": 283,
    "Masquerain": 284,
    "Shroomish": 285,
    "Breloom": 286,
    "Slakoth": 287,
    "Vigoroth": 288,
    "Slaking": 289,
    "Nincada": 290,
    "Ninjask": 291,
    "Shedinja": 292,
    "Whismur": 293,
    "Loudred": 294,
    "Exploud": 295,
    "Makuhita": 296,
    "Hariyama": 297,
    "Azurill": 298,
    "Nosepass": 299,
    "Skitty": 300,
    "Delcatty": 301,
    "Sableye": 302,
    "Mawile": 303,
    "Aron": 304,
    "Lairon": 305,
    "Aggron": 306,
    "Meditite": 307,
    "Medicham": 308,
    "Electrike": 309,
    "Manectric": 310,
    "Plusle": 311,
    "Minun": 312,
    "Volbeat": 313,
    "Illumise": 314,
    "Roselia": 315,
    "Gulpin": 316,
}

# --- Named constants ---
ASCII_MIN = 32  # first printable ASCII (space)
ASCII_MAX = 126  # last printable ASCII (~)
REGION_SIZE = (
    95  # number of characters / Pokémon per region list (ASCII 32-126 inclusive)
)
MAX_DECODE_BRANCHES = 32  # cap on live states during multi-state decoding

# --- Precomputed module-level data ---
name_to_mappings: dict[str, list[tuple[str, int]]] = {}
region_names = list(regions.keys())
num_regions = len(region_names)
# Ordered list of region Pokémon lists, used directly by the encoder.
_region_list_values = list(regions.values())

for _region_index, _region_name in enumerate(region_names):
    _pokemon_list = regions[_region_name]
    for _i in range(min(len(_pokemon_list), REGION_SIZE)):
        _char = chr(_i + ASCII_MIN)
        _pokemon_name = _pokemon_list[_i]
        if _pokemon_name not in name_to_mappings:
            name_to_mappings[_pokemon_name] = []
        name_to_mappings[_pokemon_name].append((_char, _region_index))
# --- End of precomputation ---


def get_pokemon_tokens_info(encoded_pokemon_string: str) -> list[dict]:
    """Parse space-separated encoded string into structured token objects with sprite IDs."""
    tokens = encoded_pokemon_string.split()
    results = []
    for token in tokens:
        if token in NATIONAL_DEX:
            dex_id = NATIONAL_DEX[token]
            results.append({"type": "pokemon", "name": token, "dex_id": dex_id})
        else:
            results.append({"type": "special", "name": token, "dex_id": None})
    return results


# Encoding function
def encode_message(message: str) -> str:
    """Encode a plaintext string into a space-separated sequence of Pokémon names.

    Each printable ASCII character (codes 32-126) is mapped to the Pokémon at the
    corresponding index in a regional Pokédex.  Repeated characters cycle through
    regions (Kanto → Johto → Hoenn → Kanto …) based on how many times that character
    has already appeared.  Non-printable characters other than ``\\n``/``\\r`` are
    preserved as ``[CHAR:N]`` tokens.
    """
    letter_counts: dict[str, int] = {}
    encoded_message_parts: list[str] = []
    for char in message:
        ascii_value = ord(char)
        if ASCII_MIN <= ascii_value <= ASCII_MAX:
            normalized_index = ascii_value - ASCII_MIN
            char_count = letter_counts.get(char, 0)
            region_index = char_count % num_regions
            letter_counts[char] = char_count + 1
            current_region_list = _region_list_values[region_index]
            if normalized_index < len(current_region_list):
                encoded_message_parts.append(current_region_list[normalized_index])
            else:
                encoded_message_parts.append(
                    f"[err:idx_{normalized_index}_region_{region_names[region_index]}]"
                )
        elif char in ("\n", "\r"):
            encoded_message_parts.append("[NEWLINE]" if char == "\n" else "[RETURN]")
        else:
            encoded_message_parts.append(f"[CHAR:{ord(char)}]")
    return " ".join(encoded_message_parts)


def decode_message(encoded_pokemon_string: str) -> str:
    """Decode a Pokémon-name sequence back to the original plaintext.

    Uses fork-based multi-state tracking so that an ambiguity at one position does
    **not** prevent correct decoding of later positions.  All plausible letter-count
    states are maintained in parallel; when a later token narrows the live states to
    one, prior ambiguous positions are retroactively resolved.

    Output notation
    ---------------
    * Normal character — decoded unambiguously across all surviving states.
    * ``[x,y]``        — genuine ambiguity: two or more characters remain valid in the
                         surviving states after processing the full sequence.
    * ``{x,y}``        — state-mismatch error: every live state had no valid
                         interpretation for this token (likely corrupted ciphertext).
    """
    tokens = encoded_pokemon_string.split()

    # Each branch is a dict with:
    #   'lc'      : letter_counts dict  (determines future decoding behaviour)
    #   'choices' : list[set[str]]      (one set per Pokémon token position; a set
    #                                    holds all chars any merged sub-branch chose)
    branches: list[dict] = [{"lc": {}, "choices": []}]

    # output_plan: ordered list of (kind, value) items, built as we process tokens.
    #   ('char',    str)       — literal string, emitted verbatim
    #   ('pokemon', int)       — look up surviving branches' choices at index int
    #   ('error',   list[str]) — state-mismatch; value = sorted list of all possible chars
    output_plan: list[tuple] = []
    pokemon_count = 0

    for name in tokens:
        # --- Special tokens ---
        if name == "[NEWLINE]":
            output_plan.append(("char", "\n"))
            continue
        if name == "[RETURN]":
            output_plan.append(("char", "\r"))
            continue
        if name.startswith("[CHAR:"):
            try:
                output_plan.append(("char", chr(int(name[6:-1]))))
            except ValueError:
                output_plan.append(("char", "<?>"))
            continue
        if name.startswith("[err:"):
            output_plan.append(("char", f"<?error encoding: {name}>"))
            continue
        if name not in name_to_mappings:
            output_plan.append(("char", f"<?unknown: {name}>"))
            continue

        # --- Pokémon token ---
        pos = pokemon_count
        pokemon_count += 1
        possible_mappings = name_to_mappings[name]

        # For each live branch, find valid characters and create forked next-branches.
        # Two branches that arrive at the same letter_counts state are merged: their
        # choice-sets at every past position are unioned so all candidate paths are
        # preserved for retroactive resolution.
        next_by_lc: dict[frozenset, dict] = {}

        for b in branches:
            valid_chars = [
                c for c, r in possible_mappings if b["lc"].get(c, 0) % num_regions == r
            ]
            for char in valid_chars:
                new_lc = dict(b["lc"])
                new_lc[char] = new_lc.get(char, 0) + 1
                key = frozenset(new_lc.items())
                if key in next_by_lc:
                    # Merge: union prior choice-sets, add current char
                    existing = next_by_lc[key]
                    for p2 in range(len(b["choices"])):
                        existing["choices"][p2] |= b["choices"][p2]
                    existing["choices"][pos] |= {char}
                else:
                    new_choices = [set(s) for s in b["choices"]]  # deep copy
                    new_choices.append({char})
                    next_by_lc[key] = {"lc": new_lc, "choices": new_choices}

        new_branches = list(next_by_lc.values())

        if new_branches:
            # Trim to cap to prevent pathological blowup
            branches = new_branches[:MAX_DECODE_BRANCHES]
            output_plan.append(("pokemon", pos))
        else:
            # All branches dead — genuine state-mismatch error
            all_possible = sorted({c for c, _r in possible_mappings})
            output_plan.append(("error", all_possible))
            # Keep branches unchanged and add a placeholder so choice indices stay aligned
            for b in branches:
                b["choices"].append(set())

    # --- Build the final output string ---
    result: list[str] = []
    for kind, value in output_plan:
        if kind == "char":
            result.append(value)
        elif kind == "error":
            result.append("{" + ",".join(value) + "}")
        else:  # 'pokemon'
            p: int = value
            chars_at_p: set[str] = set()
            for b in branches:
                if p < len(b["choices"]):
                    chars_at_p |= b["choices"][p]
            chars_sorted = sorted(chars_at_p)
            if len(chars_sorted) == 1:
                result.append(chars_sorted[0])
            elif len(chars_sorted) > 1:
                result.append("[" + ",".join(chars_sorted) + "]")
            else:
                result.append("<???>")  # should not occur in practice

    return "".join(result)


# Backward-compatibility alias — existing code and tests that call the old name still work.
decode_flexible_error_reporting = decode_message

# Run the application (CLI / GUI)
if __name__ == "__main__":
    print(
        f"Loaded {len(name_to_mappings)} unique Pokémon names across {num_regions} regions."
    )
