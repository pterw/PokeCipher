# Pokémon Cipher: A Stateful Polyalphabetic Substitution Cipher

A fun, creative, and surprisingly complex substitution cipher that converts text messages into sequences of Pokemon names using regional Pokedex entries and character-based state tracking.

## Overview

Pokemon Cipher implements a stateful polyalphabetic substitution cipher. It maps printable ASCII characters (codes 32-126) to Pokemon names based on their position (Index = Pokedex # - 1) in different regional Pokedex lists (Kanto, Johto, Hoenn). The core feature is its stateful nature: when a character repeats, the cipher cycles to the next region's list for subsequent occurrences based on the character's appearance count.

This design, utilizing real-world overlapping Pokedex data, intentionally creates ambiguities where the same Pokémon can represent different characters. The decoder attempts to resolve this using state but explicitly flags cases where the original character is uncertain or where the encoded sequence leads to a state mismatch error. This makes it a challenging cipher to decode perfectly without context.

![Screenshot of the app](Screenshot.png)

## How It Works

### Encoding (`encode_message`)

1.  Each printable ASCII character (code 32-126) is mapped to a 0-based index (`normalized_index = ascii_value - 32`).
2.  The cipher tracks the number of times each character has appeared (`letter_counts`).
3.  The region (Kanto, Johto, Hoenn) is determined by the character's current count modulo the number of regions (`region_index = char_count % num_regions`).
4.  The Pokémon at the `normalized_index` within the selected region's list (`regions[region_name][normalized_index]`) is chosen as the ciphertext unit.
5.  The character's count is incremented *after* determining the region and Pokémon.

### Decoding (`decode_flexible_error_reporting`)

The decoder reverses the process using state tracking:

1.  It reads the input sequence of Pokémon names.
2.  For each name, it consults a precomputed lookup table (`name_to_mappings`) to find all possible `(original_character, region_index)` pairs it could represent.
3.  It tracks the count of previously decoded characters (`letter_counts`).
4.  For each possibility, it checks if the Pokémon's `mapped_region_idx` matches the `expected_region_idx` (calculated from the `potential_char`'s `current_count % num_regions`).
5.  **Handling Results:**
    * **One Match:** If exactly one character fits the current state, that character is outputted, and its count in `letter_counts` is incremented.
    * **Multiple Matches (Ambiguity):** If multiple characters fit the current state (e.g., Slowpoke could be 'n' or 'o'), the decoder outputs a marker listing all valid possibilities (e.g., `[n,o]`). The `letter_counts` state is **not** updated in this case.
    * **Zero Matches (State Mismatch Error):** If no possible character fits the current state (e.g., decoding Seaking in the sequence for "I don't know"), the decoder outputs a marker listing *all* characters that Pokémon *could ever* map to, ignoring state (e.g., `[n,R]` for Seaking). The `letter_counts` state is **not** updated in this case.

This decoding approach accurately reflects the cipher's behavior, including its inherent limitations.

### Example

Encoding `"Hello"`:
* 'H' (Idx 40, Kanto) → `Zubat`
* 'e' (Idx 69, Kanto) → `Weepinbell`
* 'l' (Idx 76, Kanto) → `Ponyta`
* 'l' (Idx 76, Johto) → `Gyarados`
* 'o' (Idx 79, Kanto) → `Slowbro`
Result: `Zubat Weepinbell Ponyta Gyarados Slowbro`

Decoding `"Zubat Weepinbell Ponyta Gyarados Slowbro"` results in `"Hello"`.

Encoding `"Hello World!"` results in `Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur`.
Decoding that sequence results in `Hello W[n,o]rld!` because the state for decoding `Slowpoke` makes both 'n' and 'o' valid possibilities.

## Features

* Encrypts text messages into sequences of Pokémon names using ASCII mapping and stateful region cycling.
* Attempts stateful decryption back to text.
* Uses corrected Kanto, Johto, and Hoenn Pokedex lists (first 95 entries).
* Explicitly flags points of ambiguity (e.g., `[n,o]`) and state mismatch errors (e.g., `[n,R]`) during decoding rather than guessing incorrectly.
* Simple GUI interface using `tkinter`.
* Handles printable ASCII characters (32-126); preserves newlines and indicates other characters.

## Requirements

* Python 3.x
* tkinter (usually included with Python)

## Usage

1.  Save the code as `cipher.py`.
2.  Run the script from your terminal:
    ```bash
    python cipher.py
    ```
3.  Use the GUI to enter text/Pokémon names and click Encrypt/Decrypt.
4.  **(Optional) Run Unit Tests:** Verify functionality using:
    ```bash
    python -m unittest test_cipher.py
    ```
    *(Requires `test_cipher.py` with appropriate test cases)*

## Technical Details

* **Cipher Type:** Stateful Polyalphabetic Substitution Cipher.
* **Mapping:** ASCII 32-126 map to List Index 0-94 (`Index = ASCII - 32`). Pokémon #N is at Index N-1 in the lists.
* **State:** Character counts (`letter_counts`) determine region cycling (encoding) and state validation (decoding).
* **Precomputation:** A `name_to_mappings` dictionary is built on startup for efficient decoder lookup.
* **Security:** This is a classical cipher concept, **not cryptographically secure** against modern analysis. It's intended as a fun puzzle or themed cipher.

## Development Notes & Challenges

* Ensuring accurate Pokedex list ordering (Index = Pokedex # - 1) across all regions was critical and required careful verification.
* The stateful decoding logic needed refinement to handle inherent ambiguities caused by Pokémon appearing in multiple lists (e.g., Slowpoke mapping to both 'n' and 'o'). The final decoder explicitly reports these ambiguities (`[n,o]`) or state mismatch errors (`[n,R]`) rather than guessing, providing accurate feedback on the reversibility limitations for certain sequences.
* Thorough testing, including cross-platform checks and the provided unit tests (`test_cipher.py`), was essential to confirm the final implementation correctly follows the defined cipher rules.

## Extending the Cipher

You can add more regions (Sinnoh, Unova, etc.) by updating the `regions` dictionary with additional, correctly ordered Pokémon lists (minimum 95 per list). Note that this will increase the complexity and potentially the frequency of ambiguous decodings.

## Use Cases

* Educational tool for exploring substitution ciphers, state tracking, and ambiguity.
* Fun puzzles for cipher or Pokémon enthusiasts.
* Themed messages for fan communities (understanding the decoding limitations).