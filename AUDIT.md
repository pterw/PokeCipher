# PokéCipher Audit — Findings, Improvements & Roadmap

*A structured analysis of the current implementation, covering correctness issues, decoder
limitations, GUI shortcomings, and opportunities to elevate the cipher's complexity and
usability.*

---

## Table of Contents

1. [Overview](#1-overview)
2. [Decoder Correctness Issues](#2-decoder-correctness-issues)
3. [Encoder Observations](#3-encoder-observations)
4. [GUI Shortcomings](#4-gui-shortcomings)
5. [Code Quality & Maintainability](#5-code-quality--maintainability)
6. [Test Coverage Gaps](#6-test-coverage-gaps)
7. [Proposed Feature: Key System](#7-proposed-feature-key-system)
8. [Other Complexity Elevations](#8-other-complexity-elevations)
9. [Priority Summary](#9-priority-summary)

---

## 1. Overview

PokéCipher is a stateful polyalphabetic substitution cipher that maps printable ASCII
characters (codes 32–126) to Pokémon names drawn from three regional Pokédex lists (Kanto,
Johto, Hoenn). The cipher is inherently interesting: repeated characters cycle through
regions, and the intentional overlap of Pokémon names across lists creates real ambiguity
during decoding.

The implementation is functional, creative, and well-documented, but several technical
deficiencies limit its correctness, extensibility, and appeal. This audit documents those
deficiencies and proposes concrete improvements.

---

## 2. Decoder Correctness Issues

### 2.1 State Is Abandoned After Ambiguity (Critical)

**What happens today:**  
When the decoder encounters a Pokémon whose identity is ambiguous (multiple valid
characters fit the current state), it outputs a marker such as `[n,o]` and **does not
update `letter_counts`**. Every subsequent occurrence of any candidate character is then
decoded against a stale state, causing a cascading chain of false errors for the remainder
of the message.

**Concrete evidence:**  
Decoding `"AAAA"` (encoded as `"Nidoking Geodude Shroomish Nidoking"`) yields
`"A[A,i][A][A]"`. The second Pokémon, Geodude, is genuinely ambiguous between 'A' and 'i',
but the third and fourth Pokémon — which are unambiguous in the original encoding — are
reported as errors solely because the state was not advanced.

**Why it matters:**  
A cipher's decoder should be as correct as possible. Abandoning state at the first
ambiguity is an over-conservative policy that renders most real-world ciphertext
unreadable past the first ambiguity.

**Proposed fix:**  
Implement **fork-based (multi-state) decoding**: when ambiguity is detected, the decoder
spawns one branch of the decoding state per candidate character, advances each branch
independently, and merges branches when they reconverge. At each position the decoder
reports the character only if all live branches agree; otherwise, it marks the specific
differing characters. This is analogous to the Viterbi algorithm applied to an HMM and
would dramatically reduce spurious errors in subsequent tokens.

### 2.2 Ambiguity vs. State-Mismatch Markers Are Indistinguishable to Users

**What happens today:**  
Both an ambiguity (`len(valid_matches) > 1`) and a state-mismatch error
(`len(valid_matches) == 0`) produce the same bracket notation, e.g. `[n,o]`. The user
cannot tell whether the decoder is saying "I found two valid interpretations" or "I found
no valid interpretation and am listing raw possibilities."

**Why it matters:**  
These are semantically different situations. An ambiguity means the decoder tracked state
correctly but the cipher itself is lossy at this position. A state mismatch means the
state diverged (most likely due to a prior unresolved ambiguity) and the current token
should be treated with even less confidence.

**Proposed fix:**  
Use distinct notation — for example `[n|o]` (pipe-separated) for a state ambiguity and
`[!n,o]` or `{n,o}` for a state-mismatch error — so users and downstream tools can
distinguish the two cases.

### 2.3 No Look-Ahead for Single-Step Ambiguity Resolution

**What happens today:**  
The decoder makes a greedy left-to-right decision at every token. A one-token look-ahead
would resolve the majority of the cipher's two-candidate ambiguities: if only one of the
candidate characters leads to a valid decoding of the next token, the ambiguity is
automatically resolved.

**Why it matters:**  
The most famous ambiguity in the current lists — Slowpoke decoding as either 'n' (Kanto
index 78) or 'o' (Johto index 79) — can often be resolved by inspecting the following
Pokémon, because only one branch of the state will match.

**Proposed fix:**  
Add an optional look-ahead pass: after the primary decode, re-evaluate any position marked
`[x,y]` by trying both `x` and `y` as resolved characters and checking whether the
*next* decoded position becomes unambiguous. Where only one candidate survives the check,
replace the marker with that character.

### 2.4 Trailing Newline from the tkinter Text Widget Is Always Encoded

**What happens today:**  
`input_box.get("1.0", tk.END)` in tkinter always appends a trailing `\n`. The encoder
receives it and emits a `[NEWLINE]` token at the end of every encrypted message.

**Why it matters:**  
Round-trip decoding adds an invisible newline to every message, silently corrupting the
output compared to the user's original input.

**Proposed fix:**  
Strip the trailing newline in the GUI handler before passing the string to `encode_message`,
i.e. `user_input.rstrip('\n')`.

---

## 3. Encoder Observations

### 3.1 Error Token Format Is Not Round-Trip Safe

**What happens today:**  
The encoder emits `[err:idx_N_region_R]` for characters whose normalized index exceeds the
regional list length. The decoder handles `[err:…]` tokens but re-wraps them in its own
`<?error encoding: …>` notation, producing a double-nested error that cannot be
re-encoded.

**Why it matters:**  
Even error paths should be consistently round-trippable so that encoded ciphertext can be
passed back through the pipeline without surprising transformations.

**Proposed fix:**  
Standardise on a single error token format used by both encoder and decoder, or simply
document that encoding errors are terminal and the ciphertext is invalid.

### 3.2 Module-Level `print` Statements Pollute Import Namespace

**What happens today:**  
Two `print` calls execute at module import time: `"Building lookup table..."` and the
summary line. Any module that imports from `cipher.py` (including `test_cipher.py`) will
emit these lines to stdout unconditionally.

**Why it matters:**  
In test environments or when `cipher.py` is used as a library, noisy stdout output is
unexpected and breaks clean test runner output. It also violates the principle of
least surprise for library consumers.

**Proposed fix:**  
Wrap the precomputation print statements with `if __name__ == "__main__":` or replace them
with Python `logging` calls at `DEBUG` level, which are silent by default.

---

## 4. GUI Shortcomings

### 4.1 No Colour Differentiation in Output

**What happens today:**  
All output — clean characters, ambiguity markers, and error markers — appears in the same
default font and colour.

**Why it matters:**  
Users cannot quickly identify which portions of the decoded text are reliable and which
require manual disambiguation. Visual feedback is essential for a tool whose primary value
is cryptographic puzzle-solving.

**Proposed fix:**  
Use tkinter's `Text` tag system to colour-code output:
- Normal decoded characters: default foreground.
- Ambiguous markers `[x,y]`: orange / amber.
- State-mismatch markers: red.
- Successfully verified round-trip characters: green (if a verify mode is added).

### 4.2 No Swap (↕) Button

**What happens today:**  
To chain operations — e.g., encrypt, inspect the result, then decrypt — users must
manually select all output text, copy it, clear the input, and paste.

**Why it matters:**  
This is a common workflow and the friction of four manual steps is unnecessarily high for a
tool whose core loop is encode→inspect→decode.

**Proposed fix:**  
Add a "Swap ↕" button that moves the output box content into the input box in one click.

### 4.3 Fixed Window Size / No Resizability Hint

**What happens today:**  
The window does not set a minimum size or remember its last dimensions. On high-resolution
displays the default `60×6` character text areas are quite small.

**Proposed fix:**  
Set a sensible `minsize` and allow the window to resize freely (which it already does
via `expand=True`), but also persist window geometry in a lightweight preferences file
using Python's `json` module so the last window position is restored on relaunch.

### 4.4 No Region/State Visualiser

**What happens today:**  
The cipher's most interesting property — stateful region cycling — is completely hidden
from the user.

**Why it matters:**  
For an educational tool this is a missed opportunity. Showing which region each character
mapped to, or a live count of how many times each character has been seen, would make the
cipher's mechanics tangible and engaging.

**Proposed fix:**  
Add a collapsible "State Panel" below the output box that displays the current
`letter_counts` dictionary and highlights which region each decoded Pokémon came from.

### 4.5 No Input/Output Pair History

**What happens today:**  
Each operation overwrites the previous output. There is no way to compare results or
revisit a prior encoding without re-typing.

**Proposed fix:**  
Add a small scrollable history pane or a tab-based interface that keeps the last N
operations visible.

---

## 5. Code Quality & Maintainability

### 5.1 Lack of Docstrings and Type Hints

Neither `encode_message` nor `decode_flexible_error_reporting` has a docstring or type
annotations. Adding these (e.g., `def encode_message(message: str) -> str:`) would make
the public API immediately self-documenting and compatible with static analysis tools like
`mypy`.

### 5.2 Magic Numbers in Encoding Logic

`32`, `126`, and `95` appear as bare literals throughout the code. Centralising them as
named constants (`ASCII_MIN = 32`, `ASCII_MAX = 126`, `REGION_SIZE = 95`) would make
intent explicit and prevent subtle bugs if the bounds are ever adjusted.

### 5.3 `encode_message` Calls `list(regions.values())` on Every Invocation

A new list is built on every call. Since `regions` is a module-level constant, the ordered
list of region value lists should also be precomputed once at module load time alongside
`name_to_mappings`.

### 5.4 Inconsistent Comment Style in `test_cipher.py`

Every test docstring begins with `"for testing…"` (lowercase, gerund phrase) rather than
the standard `unittest` convention of a declarative sentence describing the expected
behaviour (e.g., `"Encoding an empty string returns an empty string."`). This is minor
but affects readability of test output.

---

## 6. Test Coverage Gaps

### 6.1 No Tests for the Look-Up Table Precomputation

The correctness of `name_to_mappings` is never directly tested. A test that verifies a
sample of expected `(name → [(char, region_index)])` entries would catch Pokédex ordering
regressions immediately.

### 6.2 No Tests for Non-Printable / Out-of-Range Characters

`encode_message` handles `\n`, `\r`, and `[CHAR:N]` tokens, but none of these code paths
are tested. Encoding `"\t"` (ASCII 9) should produce `[CHAR:9]`, and decoding that token
should return `"\t"`.

### 6.3 No Tests for Very Long / High-Repeat Inputs

The cipher's region cycling wraps every three occurrences, but no test exercises characters
that cycle back to region 0 after visiting all three regions (i.e., four or more
repetitions). This gap means the modulo-wrapping logic is never covered.

### 6.4 No Performance / Smoke Tests

For messages of, say, 10,000 characters, the quadratic behaviour of string concatenation
(via list append + `"".join`) should remain acceptable, but no test verifies this.

---

## 7. Proposed Feature: Key System

### Motivation

Currently anyone who knows the cipher algorithm (which is publicly described) can decode
any message. Adding a **key** transforms PokéCipher from a simple substitution scheme into
a personalised cipher whose outputs are opaque to observers without the key — closer to a
proper cryptographic primitive (though still not cryptographically secure in the modern
sense).

### 7.1 Numeric Shift Key

A single integer `k ∈ [0, 94]` shifts all character-to-index mappings modulo 95:

```
shifted_index = (normalized_index + k) % 95
```

- **Encoding:** before looking up the Pokémon, add `k` to the normalised index.
- **Decoding:** after retrieving the normalised index from the lookup, subtract `k`
  modulo 95 to recover the original character.
- **Effect:** every character now maps to a completely different Pokémon than it would
  without the key. Without knowing `k`, an attacker cannot even start building the
  look-up table for decoding.
- **Key space:** 95 possible values — trivially small for cryptographic purposes, but more
  than enough for casual puzzles.

### 7.2 Region Permutation Key

A string key (e.g., `"pikachu"`) selects a permutation of the three regions:

```
perm_index = hash(key) % 6   # 3! = 6 possible permutations
region_order = PERMUTATIONS[perm_index]   # e.g., [Johto, Hoenn, Kanto]
```

- **Effect:** instead of always cycling Kanto → Johto → Hoenn, the key determines a
  different cyclic order. The decoder uses the same key to reconstruct the same
  permutation.
- **Combined with the numeric key**, this gives 95 × 6 = 570 total key combinations for
  the two-parameter version.

### 7.3 Character-Count Seed Key

The key is used to initialise all character counts to a non-zero offset:

```
seed_offset = sum(ord(c) for c in key) % 3
letter_counts = {c: seed_offset for c in PRINTABLE_ASCII}
```

- **Effect:** the first occurrence of every character is treated as if it had already
  appeared `seed_offset` times, so the starting region shifts by a constant derived from
  the key.
- **Interesting property:** this changes which region is selected for the first occurrence
  of every character without changing the region-cycling period.

### 7.4 Vigenère-Style Positional Key

A text passphrase is applied cyclically. At position `i` in the message, the normalised
index is additionally shifted by `ord(key[i % len(key)]) % 95`:

```
shift = ord(key_char) % 95
shifted_index = (normalized_index + shift) % 95
```

- **Effect:** the mapping is different at each position in the message, making frequency
  analysis significantly harder.
- **This is the most powerful key scheme of the four** and is compatible with multi-region
  state tracking.
- **Implementation note:** the key character is consumed at each *plaintext character*
  position, not per unique character occurrence, so state tracking and key cycling are
  independent.

### 7.5 Key UI Integration

In the GUI, add a "Key (optional)" text field between the input and button frames. When
non-empty, the key is passed to `encode_message` / `decode_flexible_error_reporting`. A
small lock icon adjacent to the field could indicate whether a key is active. Encoded
messages produced with a key should not be decodable through the GUI without entering the
same key, giving the tool tangible puzzle value.

---

## 8. Other Complexity Elevations

### 8.1 Additional Regions (Sinnoh, Unova, Kalos, …)

The `regions` dictionary can be extended with further Pokédex lists. Each new region
increases the cycling period, reduces the frequency with which the same Pokémon appears
for the same character, and — paradoxically — can *reduce* ambiguity by giving previously
colliding Pokémon distinct meanings at higher occurrence counts.

### 8.2 Multi-Character Pokémon Tokens (Compound Names)

Currently the encoder joins Pokémon names with spaces and the decoder splits on spaces.
Pokémon names that contain spaces (e.g., Mr. Mime, Tapu Koko) cannot be included without
breaking the tokenisation. Switching to a delimiter that never appears in a Pokémon name
(e.g., ` / ` or comma-separation) would unlock Gen IV+ Pokémon names.

### 8.3 Bidirectional Scramble via a Secondary Alphabet

Rather than always mapping index → Pokémon in Pokédex number order, a key could specify a
custom ordering within each region (a bijective shuffle). This is equivalent to a keyed
S-box and dramatically increases the difficulty of a known-plaintext attack.

### 8.4 Fused Cipher Mode (Stacked Encoding)

Apply the cipher twice with different keys: the outer encoding conceals the inner
Pokémon-name ciphertext by treating each output Pokémon's name as an input string and
encoding it again. This nesting is unusual, doubles ciphertext length, but is a visually
striking demonstration of cipher composition.

### 8.5 Exportable Ciphertext Format

Rather than a bare space-separated string, introduce a lightweight JSON envelope:

```json
{
  "v": 1,
  "regions": ["Kanto", "Johto", "Hoenn"],
  "key_hint": "numeric-shift",
  "tokens": ["Zubat", "Weepinbell", ...]
}
```

This makes the format self-describing and forward-compatible with new features such as
additional regions or key schemes.

---

## 9. Priority Summary

| # | Finding | Impact | Effort |
|---|---------|--------|--------|
| 2.1 | State abandoned after ambiguity | High | Medium |
| 2.4 | Trailing newline from tkinter | Medium | Low |
| 2.2 | Indistinguishable error markers | Medium | Low |
| 3.2 | Module-level `print` at import | Low | Low |
| 4.1 | No colour in output | Medium | Low |
| 4.2 | No Swap button | Low | Low |
| 7.x | Key system | High (feature) | Medium |
| 6.x | Test coverage gaps | Medium | Low |
| 2.3 | Look-ahead ambiguity resolution | High | High |
| 8.x | Additional regions / formats | Low (feature) | High |

Items marked **High impact / Low effort** (2.4, 2.2, 3.2) should be addressed
immediately. Items **2.1** and the **key system** represent the most significant
improvement to the cipher's correctness and depth, respectively, and should follow.

---

*Audit compiled against commit `223339e` on the `main` branch.*
