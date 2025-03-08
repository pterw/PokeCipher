import tkinter as tk
from tkinter import scrolledtext

# Pokémon Cipher Encoding/Decoding Functions
import string

# Define the first 95 Pokémon from each regional dex (ASCII 32-126 normalized)
regions = {
    "Kanto":  ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
               "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
               "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot",
               "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok",
               "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran", "Nidorina",
               "Nidoqueen", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
               "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom",
               "Vileplume", "Paras", "Parasect", "Venonat", "Venomoth", "Diglett",
               "Dugtrio", "Meowth", "Persian", "Psyduck", "Golduck", "Mankey",
               "Primeape", "Growlithe", "Arcanine", "Poliwag", "Poliwhirl", "Poliwrath",
               "Abra", "Kadabra", "Alakazam", "Machop", "Machoke", "Machamp",
               "Bellsprout", "Weepinbell", "Victreebel", "Tentacool", "Tentacruel", "Geodude",
               "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke", "Slowbro",
               "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
               "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly",
               "Haunter", "Gengar", "Onix", "Drowzee", "Hypno", "Krabby"],

    "Johto":  ["Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion",
               "Totodile", "Croconaw", "Feraligatr", "Sentret", "Furret", "Hoothoot",
               "Noctowl", "Ledyba", "Ledian", "Spinarak", "Ariados", "Crobat",
               "Chinchou", "Lanturn", "Pichu", "Cleffa", "Igglybuff", "Togepi",
               "Togetic", "Natu", "Xatu", "Mareep", "Flaaffy", "Ampharos",
               "Bellossom", "Marill", "Azumarill", "Sudowoodo", "Politoed", "Hoppip",
               "Skiploom", "Jumpluff", "Aipom", "Sunkern", "Sunflora", "Yanma",
               "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow", "Slowking",
               "Misdreavous", "Unown", "Wobbuffet", "Girafarig", "Pineco", "Forretress",
               "Dunsparce", "Gligar", "Steelix", "Snubbull", "Granbull", "Qwilfish",
               "Scizor", "Shuckle", "Heracross", "Sneasel", "Teddiursa", "Ursaring",
               "Slugma", "Magcargo", "Swinub", "Piloswine", "Corsola", "Remoraid",
               "Octillery", "Delibird", "Mantine", "Skarmory", "Houndour", "Houndoom",
               "Kingdra", "Phanpy", "Donphan", "Porygon2", "Stantler", "Smeargle",
               "Tyrogue", "Hitmontop", "Smoochum", "Elekid", "Magby", "Miltank",
               "Blissey", "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar"]
}

region_list = list(regions.values())

# Encoding function
def encode_message(message):
    letter_counts = {}
    encoded_message = []

    for char in message:
        ascii_value = ord(char)
        if 32 <= ascii_value <= 126:  # Ensure it's a printable character
            normalized_index = ascii_value - 32  # Shift ASCII to fit Pokémon range
            region_index = letter_counts.get(char, 0) % len(region_list)
            encoded_message.append(region_list[region_index][normalized_index])
            letter_counts[char] = letter_counts.get(char, 0) + 1  # Cycle region on repeats
        else:
            encoded_message.append(char)  # Preserve unknown characters

    return " ".join(encoded_message)

# Decoding function
def decode_message(encoded_pokemon):
    decoded_message = []
    
    for name in encoded_pokemon.split():
        for ascii_offset in range(95):  # Covers all printable ASCII (32-126)
            for region in region_list:
                if name == region[ascii_offset]:  # Find Pokémon in any region
                    decoded_message.append(chr(ascii_offset + 32))  # Convert back to ASCII
                    break
    
    return "".join(decoded_message)

# GUI Setup
root = tk.Tk()
root.title("Pokémon Cipher")

# Input Box
tk.Label(root, text="Enter Text:").pack()
input_box = scrolledtext.ScrolledText(root, height=5, width=50)
input_box.pack()

# Encode Button
def handle_encode():
    user_input = input_box.get("1.0", tk.END).strip()
    if user_input:
        encoded_text = encode_message(user_input)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, encoded_text)

tk.Button(root, text="Encrypt", command=handle_encode).pack()

# Decode Button
def handle_decode():
    user_input = input_box.get("1.0", tk.END).strip()
    if user_input:
        decoded_text = decode_message(user_input)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, decoded_text)

tk.Button(root, text="Decrypt", command=handle_decode).pack()

# Output Box
tk.Label(root, text="Output:").pack()
output_box = scrolledtext.ScrolledText(root, height=5, width=50)
output_box.pack()

# Run GUI
root.mainloop()
