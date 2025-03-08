# Pokémon Cipher

A fun, creative, and solvable encryption tool/chalenge that converts text messages into sequences of Pokemon names using regional pokedex entries.

## Overview

Pokemon Cipher is a polyalphabetic substitution cipher that maps ASCII characters to Pokemon names from different regional pokedexes. When a character repeats in a message, the cipher cycles to the next region's Pokémon, making the encryption more complex, intersting, and fun to decrypt.

![Screenshot of the app](Screenshot.png)

## How It Works

### Encoding Process

1. Each printable ASCII character (32-126) maps to a Pokemon at the corresponding position in a regional Pokedex 
2. The first occurrence of a character uses the Kanto regional pokedex
3. When a character repeats, the cipher cycles to the next region (Johto)
4. When all available regions are used, it cycles back to the first region (which would be Kanto)

### Decoding Process

The decoder identifies which Pokemon name corresponds to which character and reconstructs the original message.

### Example

The message "hello" would be encoded as:
- 'h' → Kadabra (Kanto)
- 'e' → Paras (Kanto)
- 'l' → Diglett (Kanto)
- 'l' → Ledyba (Johto) - *notice the region change for the repeated 'l' which changes the pokemon - increasing complexity
- 'o' → Shellder (Kanto)

## Features

- Encrypt any text to a string of mutliple Pokemon names
- Decrypt Pokemon names back to original text
- Simple GUI interface 
- Preserves punctuation, and special characters
- Region cycling for repeated characters increases complexity.

## Requirements

- Python 3.x
- tkinter (usually included with Python)

## Usage

1. Run the script:
```
python cipher.py
```

2. Enter text in the top text box
3. Click "Encrypt" to convert to Pokémon names
4. Click "Decrypt" to convert Pokémon names back to text

## Technical Details

### ASCII Mapping

The cipher maps printable ASCII characters (32-126) to pokemon:
- ASCII 32 (space) → First pokemon in each region (Bulbasaur/Chikorita)
- ASCII 33 (!) → Second pokemon in each region (Ivysaur/Bayleef)
- And so on...

### Optimization

The repository contains an optimized implementation of the origianl.

The optimized version improves decoding performance from O(n × r × p) to O(n) by using precomputed lookup tables.

## Extending the Cipher

You can add more regions (Hoenn, Sinnoh, etc.) by updating the `regions` dictionary with additional Pokémon lists. Each region must have at least 95 pokemon to cover all printable ASCII characters.

## Use Cases

- Educational tool for teaching cryptography concepts
- Fun puzzles for cipher or pokemon enthusiasts
- Secret messages for fan communities
- Themed challenges for escape rooms or scavenger hunts
