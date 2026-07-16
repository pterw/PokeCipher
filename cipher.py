import string
import time
import re

# Pokémon cipher encoding/decoding functions

# Correctly ordered lists for the first 95 entries (index 0-94)
# Mapping ASCII 32 (space) to index 0, up to ASCII 126 (~) to index 94
# Pokedex #N is at List Index [N-1]
regions = {
    # Corrected Kanto Regional Dex
    "Kanto": [
        "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",  # 1-6
        "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree", # 7-12
        "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot",          # 13-18
        "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok",              # 19-24
        "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran-F", "Nidorina",   # 25-30
        "Nidoqueen", "Nidoran-M", "Nidorino", "Nidoking", "Clefairy", "Clefable",   # 31-36
        "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff", "Zubat", "Golbat",       # 37-42 (#40=Wigglytuff@39, #41=Zubat@40)
        "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat",            # 43-48
        "Venomoth", "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck",          # 49-54 (#54=Psyduck@53)
        "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine", "Poliwag",        # 55-60 (#55=Golduck@54, #56=Mankey@55, #57=Primeape@56)
        "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",         # 61-66
        "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",# 67-72 (#68=Machamp@67, #69=Bellsprout@68, #70=Weepinbell@69)
        "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash",         # 73-78 (#76=Golem@75, #77=Ponyta@76)
        "Slowpoke", "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo",      # 79-84 (#79=Slowpoke@78, #80=Slowbro@79, #81=Magnemite@80, #82=Magneton@81, #83=Farfetch'd@82)
        "Dodrio", "Seel", "Dewgong", "Grimer", "Muk", "Shellder",                 # 85-90
        "Cloyster", "Gastly", "Haunter", "Gengar", "Onix"                         # 91-95 (#95=Onix@94)
    ],
    # Corrected Johto Regional Dex
    "Johto": [
        "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", # 1-6
        "Totodile", "Croconaw", "Feraligatr", "Pidgey", "Pidgeotto", "Pidgeot",    # 7-12   (#10=Pidgey@9)
        "Spearow", "Fearow", "Hoothoot", "Noctowl", "Rattata", "Raticate",       # 13-18
        "Sentret", "Furret", "Pichu", "Pikachu", "Raichu", "Caterpie",           # 19-24
        "Metapod", "Butterfree", "Weedle", "Kakuna", "Beedrill", "Ledyba",        # 25-30
        "Ledian", "Spinarak", "Ariados", "Geodude", "Graveler", "Golem",          # 31-36  (#34=Geodude@33, #36=Golem@35)
        "Zubat", "Golbat", "Crobat", "Cleffa", "Clefairy", "Clefable",           # 37-42  (#40=Cleffa@39)
        "Igglybuff", "Jigglypuff", "Wigglytuff", "Togepi", "Togetic", "Sandshrew",  # 43-48
        "Sandslash", "Ekans", "Arbok", "Dunsparce", "Mareep", "Flaaffy",          # 49-54
        "Ampharos", "Wooper", "Quagsire", "Gastly", "Haunter", "Gengar",         # 55-60
        "Unown", "Onix", "Steelix", "Bellsprout", "Weepinbell", "Victreebel",     # 61-66  (#64=Bellsprout@63, #65=Weepinbell@64)
        "Hoppip", "Skiploom", "Jumpluff", "Paras", "Parasect", "Poliwag",        # 67-72
        "Poliwhirl", "Poliwrath", "Politoed", "Magikarp", "Gyarados", "Goldeen",    # 73-78  (#76=Magikarp@75, #77=Gyarados@76)
        "Seaking", "Slowpoke", "Slowbro", "Slowking", "Oddish", "Gloom",          # 79-84  (#79=Seaking@78, #80=Slowpoke@79, #81=Slowbro@80)
        "Vileplume", "Bellossom", "Drowzee", "Hypno", "Abra", "Kadabra",          # 85-90
        "Alakazam", "Ditto", "Pineco", "Forretress", "Nidoran-F"                 # 91-95 (#95=Nidoran-F@94)
    ],
     # Corrected Hoenn Regional Dex
     "Hoenn": [
        "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken",      # 1-6
        "Mudkip", "Marshtomp", "Swampert", "Poochyena", "Mightyena", "Zigzagoon", # 7-12
        "Linoone", "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox",      # 13-18
        "Lotad", "Lombre", "Ludicolo", "Seedot", "Nuzleaf", "Shiftry",         # 19-24
        "Taillow", "Swellow", "Wingull", "Pelipper", "Ralts", "Kirlia",          # 25-30
        "Gardevoir", "Surskit", "Masquerain", "Shroomish", "Breloom", "Slakoth",   # 31-36
        "Vigoroth", "Slaking", "Abra", "Kadabra", "Alakazam", "Nincada",         # 37-42 (#39=Abra@38)
        "Ninjask", "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita",      # 43-48
        "Hariyama", "Goldeen", "Seaking", "Magikarp", "Gyarados", "Azurill",     # 49-54 (#53=Gyarados@52)
        "Marill", "Azumarill", "Geodude", "Graveler", "Golem", "Nosepass",        # 55-60 (#57=Geodude@56, #59=Golem@58)
        "Skitty", "Delcatty", "Zubat", "Golbat", "Crobat", "Tentacool",         # 61-66 (#63=Zubat@62, #66=Tentacool@65)
        "Tentacruel", "Sableye", "Mawile", "Aron", "Lairon", "Aggron",          # 67-72 (#68=Sableye@67, #69=Mawile@68, #70=Aron@69)
        "Machop", "Machoke", "Machamp", "Meditite", "Medicham", "Electrike",     # 73-78 (#75=Machamp@74, #76=Meditite@75, #77=Medicham@76)
        "Manectric", "Plusle", "Minun", "Magnemite", "Magneton", "Voltorb",       # 79-84 (#82=Magnemite@81, #83=Magneton@82)
        "Electrode", "Volbeat", "Illumise", "Oddish", "Gloom", "Vileplume",       # 85-90 (#88=Oddish@87)
        "Bellossom", "Doduo", "Dodrio", "Roselia", "Gulpin"                      # 91-95 (#95=Gulpin@94)
    ]
}

# --- Named constants ---
ASCII_MIN = 32      # first printable ASCII (space)
ASCII_MAX = 126     # last printable ASCII (~)
REGION_SIZE = 95    # number of characters / Pokémon per region list (ASCII 32-126 inclusive)
MAX_DECODE_BRANCHES = 32   # cap on live states during multi-state decoding

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
        elif char in ('\n', '\r'):
            encoded_message_parts.append("[NEWLINE]" if char == '\n' else "[RETURN]")
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
    branches: list[dict] = [{'lc': {}, 'choices': []}]

    # output_plan: ordered list of (kind, value) items, built as we process tokens.
    #   ('char',    str)       — literal string, emitted verbatim
    #   ('pokemon', int)       — look up surviving branches' choices at index int
    #   ('error',   list[str]) — state-mismatch; value = sorted list of all possible chars
    output_plan: list[tuple] = []
    pokemon_count = 0

    for name in tokens:
        # --- Special tokens ---
        if name == '[NEWLINE]':
            output_plan.append(('char', '\n'))
            continue
        if name == '[RETURN]':
            output_plan.append(('char', '\r'))
            continue
        if name.startswith('[CHAR:'):
            try:
                output_plan.append(('char', chr(int(name[6:-1]))))
            except ValueError:
                output_plan.append(('char', '<?>'))
            continue
        if name.startswith('[err:'):
            output_plan.append(('char', f'<?error encoding: {name}>'))
            continue
        if name not in name_to_mappings:
            output_plan.append(('char', f'<?unknown: {name}>'))
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
                c for c, r in possible_mappings
                if b['lc'].get(c, 0) % num_regions == r
            ]
            for char in valid_chars:
                new_lc = dict(b['lc'])
                new_lc[char] = new_lc.get(char, 0) + 1
                key = frozenset(new_lc.items())
                if key in next_by_lc:
                    # Merge: union prior choice-sets, add current char
                    existing = next_by_lc[key]
                    for p2 in range(len(b['choices'])):
                        existing['choices'][p2] |= b['choices'][p2]
                    existing['choices'][pos] |= {char}
                else:
                    new_choices = [set(s) for s in b['choices']]  # deep copy
                    new_choices.append({char})
                    next_by_lc[key] = {'lc': new_lc, 'choices': new_choices}

        new_branches = list(next_by_lc.values())

        if new_branches:
            # Trim to cap to prevent pathological blowup
            branches = new_branches[:MAX_DECODE_BRANCHES]
            output_plan.append(('pokemon', pos))
        else:
            # All branches dead — genuine state-mismatch error
            all_possible = sorted({c for c, _r in possible_mappings})
            output_plan.append(('error', all_possible))
            # Keep branches unchanged and add a placeholder so choice indices stay aligned
            for b in branches:
                b['choices'].append(set())

    # --- Build the final output string ---
    result: list[str] = []
    for kind, value in output_plan:
        if kind == 'char':
            result.append(value)
        elif kind == 'error':
            result.append('{' + ','.join(value) + '}')
        else:  # 'pokemon'
            p: int = value
            chars_at_p: set[str] = set()
            for b in branches:
                if p < len(b['choices']):
                    chars_at_p |= b['choices'][p]
            chars_sorted = sorted(chars_at_p)
            if len(chars_sorted) == 1:
                result.append(chars_sorted[0])
            elif len(chars_sorted) > 1:
                result.append('[' + ','.join(chars_sorted) + ']')
            else:
                result.append('<???>')  # should not occur in practice

    return ''.join(result)


# Backward-compatibility alias — existing code and tests that call the old name still work.
decode_flexible_error_reporting = decode_message

# --- GUI setup ---
def create_gui():
    import tkinter as tk
    from tkinter import scrolledtext

    root = tk.Tk()
    root.title(f"Pokémon Cipher  [{num_regions} regions · multi-state decoder]")
    root.minsize(520, 420)

    status_var = tk.StringVar(value="Ready")
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    input_frame = tk.Frame(root)
    input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    tk.Label(input_frame, text="Input:").pack(anchor=tk.W)
    input_box = scrolledtext.ScrolledText(input_frame, height=7, width=65, wrap=tk.WORD)
    input_box.pack(fill=tk.BOTH, expand=True)

    def update_status(message: str, duration: int = 3000) -> None:
        status_var.set(message)
        root.after(duration, lambda: status_var.set("Ready"))

    # --- Button row ---
    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    def handle_encode() -> None:
        # Strip the trailing newline that tkinter always appends to Text widget content.
        user_input = input_box.get("1.0", tk.END).rstrip('\n')
        output_box.delete("1.0", tk.END)
        _clear_output_tags(output_box)
        if not user_input.strip():
            update_status("Please enter text to encrypt")
            output_box.insert(tk.END, "Please enter text to encrypt.")
            return
        start_time = time.time()
        encoded_text = encode_message(user_input)
        elapsed_time = time.time() - start_time
        output_box.insert(tk.END, encoded_text)
        update_status(f"Encrypted in {elapsed_time:.3f}s")

    def handle_decode() -> None:
        user_input = input_box.get("1.0", tk.END).strip()
        output_box.delete("1.0", tk.END)
        _clear_output_tags(output_box)
        if not user_input:
            update_status("Please enter Pokémon names to decrypt")
            output_box.insert(tk.END, "Please enter Pokémon names to decrypt.")
            return
        start_time = time.time()
        decoded_text = decode_message(user_input)
        elapsed_time = time.time() - start_time
        output_box.insert(tk.END, decoded_text)
        _highlight_markers(output_box)
        update_status(f"Decrypted in {elapsed_time:.3f}s")

    def handle_clear() -> None:
        input_box.delete("1.0", tk.END)
        output_box.delete("1.0", tk.END)
        _clear_output_tags(output_box)
        update_status("Cleared")

    def handle_swap() -> None:
        """Move the output box content into the input box for chained operations."""
        out_text = output_box.get("1.0", tk.END).strip()
        if not out_text:
            update_status("Nothing to swap")
            return
        input_box.delete("1.0", tk.END)
        input_box.insert(tk.END, out_text)
        output_box.delete("1.0", tk.END)
        _clear_output_tags(output_box)
        update_status("Output swapped to input")

    def handle_copy() -> None:
        output_text = output_box.get("1.0", tk.END).strip()
        if output_text:
            root.clipboard_clear()
            root.clipboard_append(output_text)
            update_status("Output copied to clipboard")
        else:
            update_status("No output to copy")

    tk.Button(button_frame, text="Encrypt → Pokémon", command=handle_encode, width=18).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="Decrypt → Text",    command=handle_decode, width=16).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="Swap ↕",            command=handle_swap,   width=8 ).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="Copy Output",       command=handle_copy,   width=12).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="Clear",             command=handle_clear,  width=8 ).pack(side=tk.LEFT, padx=4)

    # --- Output box ---
    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    tk.Label(output_frame, text="Output:").pack(anchor=tk.W)
    output_box = scrolledtext.ScrolledText(output_frame, height=7, width=65, wrap=tk.WORD)
    output_box.pack(fill=tk.BOTH, expand=True)

    # Configure colour tags for decoded output highlighting
    output_box.tag_configure("ambiguous", foreground="#E07800")   # amber — [x,y] markers
    output_box.tag_configure("error",     foreground="#CC0000")   # red   — {x,y} markers

    def _clear_output_tags(widget: scrolledtext.ScrolledText) -> None:
        widget.tag_remove("ambiguous", "1.0", tk.END)
        widget.tag_remove("error",     "1.0", tk.END)

    def _highlight_markers(widget: scrolledtext.ScrolledText) -> None:
        """Apply colour tags to ambiguity and error markers in the output widget."""
        full_text = widget.get("1.0", tk.END)
        for match in re.finditer(r'\[[^\]]+\]', full_text):
            start = f"1.0 + {match.start()} chars"
            end   = f"1.0 + {match.end()} chars"
            widget.tag_add("ambiguous", start, end)
        for match in re.finditer(r'\{[^}]+\}', full_text):
            start = f"1.0 + {match.start()} chars"
            end   = f"1.0 + {match.end()} chars"
            widget.tag_add("error", start, end)

    return root


# Run the application
if __name__ == "__main__":
    print(f"Loaded {len(name_to_mappings)} unique Pokémon names across {num_regions} regions.")
    root = create_gui()
    root.mainloop()