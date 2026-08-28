import tkinter as tk
from tkinter import scrolledtext
import string
import time
import os

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

# --- Build the lookup table ---
name_to_mappings = {}
region_names = list(regions.keys())
num_regions = len(region_names)

print("Building lookup table...")
for region_index, region_name in enumerate(region_names):
    pokemon_list = regions[region_name]
    for i in range(min(len(pokemon_list), 95)):
        char_code = i + 32
        char = chr(char_code)
        pokemon_name = pokemon_list[i]
        if pokemon_name not in name_to_mappings:
            name_to_mappings[pokemon_name] = []
        # Store tuple (character, region index)
        name_to_mappings[pokemon_name].append((char, region_index))
print(f"Precomputed detailed lookup table with {len(name_to_mappings)} unique Pokémon names.")
region_list_values = list(regions.values())
# --- End of precomputation ---

# Encoding function
def encode_message(message):
    letter_counts = {}
    encoded_message_parts = []
    for char in message:
        ascii_value = ord(char)
        if 32 <= ascii_value <= 126:
            normalized_index = ascii_value - 32
            char_count = letter_counts.get(char, 0)
            region_index = char_count % num_regions
            letter_counts[char] = char_count + 1
            current_region_list = region_list_values[region_index]
            index_to_lookup = normalized_index
            if index_to_lookup < len(current_region_list):
                pokemon_to_append = current_region_list[index_to_lookup]
                encoded_message_parts.append(pokemon_to_append)
            else:
                encoded_message_parts.append(f"[err:idx_{index_to_lookup}_region_{region_names[region_index]}]")
        elif char in ('\n', '\r'):
            encoded_message_parts.append("[NEWLINE]" if char == '\n' else "[RETURN]")
        else:
            encoded_message_parts.append(f"[CHAR:{ascii_value}]")
    return " ".join(encoded_message_parts)

# --- MODIFIED: Decoder flags ambiguity or shows all possibilities on error ---
def decode_flexible_error_reporting(encoded_pokemon_string):
    decoded_message_parts = []
    pokemon_names = encoded_pokemon_string.split()
    letter_counts = {} # STATE tracking

    for name in pokemon_names:
        # Handle special tags first
        if name == "[NEWLINE]": decoded_message_parts.append('\n'); continue
        elif name == "[RETURN]": decoded_message_parts.append('\r'); continue
        elif name.startswith("[CHAR:") :
            try: decoded_message_parts.append(chr(int(name[6:-1])));
            except: decoded_message_parts.append("<?>");
            continue
        elif name.startswith("[err:") :
            decoded_message_parts.append(f"<?error encoding: {name}>"); continue

        # Handle actual Pokémon names
        if name in name_to_mappings:
            possible_mappings = name_to_mappings[name]
            valid_matches = [] # Store valid potential characters found

            # Step 1: Find ALL valid possibilities based on current state
            for potential_char, mapped_region_idx in possible_mappings:
                current_count = letter_counts.get(potential_char, 0)
                expected_region_idx = current_count % num_regions
                if expected_region_idx == mapped_region_idx:
                    valid_matches.append(potential_char) # Store the valid character

            # Step 2: Decide output based on number of valid matches
            if len(valid_matches) == 1:
                # Case 1: Exactly one valid character found
                found_char = valid_matches[0]
                decoded_message_parts.append(found_char)
                # Update state only if unambiguous
                letter_counts[found_char] = letter_counts.get(found_char, 0) + 1

            elif len(valid_matches) > 1:
                # Case 2: AMBIGUITY - Multiple characters fit the current state
                # Output the simple list format marker
                ambiguous_chars_str = ",".join(sorted(list(set(valid_matches)))) # Use set for unique chars
                output_marker = f"[{ambiguous_chars_str}]"
                # print(f"[DECODE AMBIGUITY] Name: '{name}' -> Outputting: {output_marker}") # Optional log
                decoded_message_parts.append(output_marker)
                # DO NOT update letter_counts state here

            else: # len(valid_matches) == 0
                # Case 3: DECODING ERROR (State Mismatch)
                # Output all potential chars for this Pokemon, ignoring state
                all_possible_chars = sorted(list(set([mapping[0] for mapping in possible_mappings])))
                all_chars_str = ",".join(all_possible_chars)
                # Use the simple list format marker for errors too
                output_marker = f"[{all_chars_str}]"
                # print(f"[DECODE ERR] Name: '{name}' | State mismatch! Showing all possibilities: {output_marker}") # Optional log
                decoded_message_parts.append(output_marker)
                # DO NOT update letter_counts state here

        else:
             # Handle unknown Pokemon names
            # print(f"[DECODE UNKNOWN] Name: '{name}'") # Optional console log
            decoded_message_parts.append(f"<?unknown: {name}>")

    return "".join(decoded_message_parts)
# --- End of MODIFIED decoding function ---

# --- GUI setup ---
def create_gui():
    root = tk.Tk()
    # Update title to reflect decoder type
    root.title(f"Pokémon Cipher ({num_regions}-region | Flexible Error Decoder)")

    status_var = tk.StringVar()
    status_var.set("Ready")
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    input_frame = tk.Frame(root)
    input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,5))

    tk.Label(input_frame, text="Enter text:").pack(anchor=tk.W)
    input_box = scrolledtext.ScrolledText(input_frame, height=6, width=60, wrap=tk.WORD)
    input_box.pack(fill=tk.BOTH, expand=True)

    def update_status(message, duration=3000):
        status_var.set(message)
        root.after(duration, lambda: status_var.set("Ready"))

    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    def handle_encode():
        user_input = input_box.get("1.0", tk.END)
        output_box.delete("1.0", tk.END)
        if not user_input.strip():
            update_status("Please enter text to encrypt")
            output_box.insert(tk.END, "Please enter text to encrypt.")
            return
        start_time = time.time()
        encoded_text = encode_message(user_input)
        elapsed_time = time.time() - start_time
        output_box.insert(tk.END, encoded_text)
        update_status(f"Encrypted in {elapsed_time:.3f} seconds")

    encode_button = tk.Button(button_frame, text="Encrypt -> Pokémon", command=handle_encode, width=20)
    encode_button.pack(side=tk.LEFT, padx=5)

    def handle_decode():
        user_input = input_box.get("1.0", tk.END)
        output_box.delete("1.0", tk.END)
        if not user_input.strip():
            update_status("Please enter Pokémon names to decrypt")
            output_box.insert(tk.END, "Please enter Pokémon names to decrypt.")
            return
        start_time = time.time()
        # *** Calls the NEW flexible error decoder function ***
        decoded_text = decode_flexible_error_reporting(user_input.strip())
        elapsed_time = time.time() - start_time
        output_box.insert(tk.END, decoded_text)
        update_status(f"Decrypted in {elapsed_time:.3f} seconds")

    # Make sure the button calls the new decoder function name
    decode_button = tk.Button(button_frame, text="Decrypt -> Text", command=handle_decode, width=20)
    decode_button.pack(side=tk.LEFT, padx=5)

    def handle_clear():
        input_box.delete("1.0", tk.END)
        output_box.delete("1.0", tk.END)
        update_status("Cleared all text")

    clear_button = tk.Button(button_frame, text="Clear All", command=handle_clear, width=15)
    clear_button.pack(side=tk.LEFT, padx=5)

    def handle_copy():
        output_text = output_box.get("1.0", tk.END).strip()
        if output_text:
            root.clipboard_clear()
            root.clipboard_append(output_text)
            update_status("Copied output to clipboard")
        else:
            update_status("No output to copy")

    copy_button = tk.Button(button_frame, text="Copy Output", command=handle_copy, width=15)
    copy_button.pack(side=tk.LEFT, padx=5)

    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5,10))

    tk.Label(output_frame, text="Output:").pack(anchor=tk.W)
    output_box = scrolledtext.ScrolledText(output_frame, height=6, width=60, wrap=tk.WORD)
    output_box.pack(fill=tk.BOTH, expand=True)

    return root

# Run the application
if __name__ == "__main__":
    root = create_gui()
    root.mainloop()