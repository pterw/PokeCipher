---
name: PokéCipher
description: A Game Boy-green field terminal for a deliberately lossy Pokémon cipher.
colors:
  lcd-deep: "#0f380f"
  lcd-card: "#14421a"
  lcd-shade: "#1d4d24"
  lcd-moss: "#265626"
  lcd-border: "#2c5c2c"
  lcd-olive: "#8bac0f"
  lcd-sage: "#9bbc8a"
  lcd-wash: "#d7f5c4"
  terminal-void: "#071a07"
  cartridge-yellow: "#ffd100"
  signal-amber: "#e8b93b"
  signal-coral: "#e0674f"
  signal-ice: "#7fb3d5"
  alert-rust: "#b03a2e"
  alert-parchment: "#f5e6d7"
typography:
  display:
    fontFamily: "Press Start 2P, ui-monospace, monospace"
    fontSize: "clamp(1.875rem, 5vw, 2.25rem)"
    fontWeight: 400
    lineHeight: 1.25
  headline:
    fontFamily: "Press Start 2P, ui-monospace, monospace"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.25
  body:
    fontFamily: "VT323, ui-monospace, monospace"
    fontSize: "clamp(1.125rem, 2vw, 1.25rem)"
    fontWeight: 400
    lineHeight: 1.375
  label:
    fontFamily: "VT323, ui-monospace, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    letterSpacing: "0.05em"
rounded:
  none: "0px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  section: "40px"
components:
  button-primary:
    backgroundColor: "{colors.cartridge-yellow}"
    textColor: "{colors.lcd-deep}"
    rounded: "{rounded.none}"
    padding: "0 16px"
    height: "40px"
  button-secondary:
    backgroundColor: "{colors.lcd-moss}"
    textColor: "{colors.lcd-wash}"
    rounded: "{rounded.none}"
    padding: "0 16px"
    height: "40px"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.lcd-wash}"
    rounded: "{rounded.none}"
    padding: "0 16px"
    height: "40px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.lcd-wash}"
    rounded: "{rounded.none}"
    padding: "0 16px"
    height: "40px"
  terminal-panel:
    backgroundColor: "{colors.terminal-void}"
    textColor: "{colors.lcd-wash}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "16px"
  terminal-chrome:
    backgroundColor: "{colors.lcd-moss}"
    textColor: "{colors.lcd-sage}"
    rounded: "{rounded.none}"
    padding: "6px 12px"
  input-field:
    backgroundColor: "{colors.lcd-shade}"
    textColor: "{colors.lcd-wash}"
    rounded: "{rounded.none}"
    padding: "12px"
  token-chip:
    backgroundColor: "{colors.lcd-moss}"
    textColor: "{colors.lcd-wash}"
    rounded: "{rounded.none}"
    padding: "2px 6px"
---

# Design System: PokéCipher

## Overview

**Creative North Star: "The Field Terminal"**

A researcher's command line for reading Pokédex data. The cipher is not
presented as a toy trick but as instrument output: you type at a prompt, the
machine answers in a transcript, and when the machine is uncertain it says so in
its own notation rather than guessing. The `$` prompt, the monospace transcript
and the blinking block cursor are the spine of the identity.

The surface is a four-tone Game Boy LCD. Depth is carried entirely by stepped
greens — five of them, from near-black `#0f380f` up to `#2c5c2c` — with no
shadows and no rounded corners anywhere. One warm colour, cartridge yellow,
exists in an otherwise wholly green world, which is why it can mean something.

This world is **semi-settled and explicitly iterative**. The Game Boy greens are
good but not sacred: they hold until they fail the squint test or something
better earns the place. The type pairing was a ship-fast choice and self-hosted
retro faces have not been explored. Treatments here are meant to be tried,
looked at, and reversed without ceremony — a reversal is the process working.

**Key Characteristics:**

- Four-tone LCD green, tonal depth, zero shadow, zero radius
- One warm accent (`#ffd100`) in an otherwise green system
- Terminal transcript as the primary voice
- Uncertainty rendered as notation, never hidden
- Every surface bordered; nothing floats

## Colors

A near-monochrome green field with a single warm accent and a small set of
signal colours reserved for decoder semantics.

### Primary

- **Cartridge Yellow** (`#ffd100`): the only warm colour in the system. Carries
  the `$` prompt, the block cursor, and the primary button. It is also the
  requested border for the terminal panel. Its scarcity is the entire reason it
  reads as important.
- **LCD Olive** (`#8bac0f`): terminal output lines, the focus ring, and the
  grass in the pixel backdrop. The brightest structural green.

### Neutral

- **LCD Deep** (`#0f380f`): the page ground. The darkest green in the system.
- **Terminal Void** (`#071a07`): the terminal panel interior, deliberately
  darker than the page so the transcript reads as a recessed screen.
- **LCD Card** (`#14421a`): result panels and raised containers.
- **LCD Shade** (`#1d4d24`): input interiors.
- **LCD Moss** (`#265626`): terminal chrome bar, secondary buttons, token chips.
- **LCD Border** (`#2c5c2c`): the universal border colour, applied globally.
- **LCD Sage** (`#9bbc8a`): muted and secondary text.
- **LCD Wash** (`#d7f5c4`): primary body and heading text. **Currently rejected
  in the hero** — this is the pistachio the user has called out on the wordmark
  and hero copy. It is documented because it is the incumbent value, not because
  it is endorsed.

### Tertiary — decoder signals

These three are semantic, not decorative. They encode what the decoder knows.

- **Signal Amber** (`#e8b93b`): genuine ambiguity, the `[x,y]` marker.
- **Signal Coral** (`#e0674f`): state mismatch, the `{x,y}` marker. **Fails
  contrast at 3.41:1 on card and 3.91:1 on ground; needs raising.**
- **Signal Ice** (`#7fb3d5`): unknown token. The only cool colour in the system,
  which is appropriate — an unrecognised name is outside the cipher entirely.

### Named Rules

**The One Warm Thing Rule.** Yellow is the only warm colour permitted in the
chrome. If a second warm accent appears, one of them is wrong.

**The Signal Reservation Rule.** Amber, coral and ice mean decoder states and
nothing else. Never reuse a signal colour for form validation, hover, or
emphasis — an empty-input error must not borrow coral from corrupted ciphertext.

## Typography

**Display Font:** Press Start 2P (fallback `ui-monospace, monospace`)
**Body Font:** VT323 (fallback `ui-monospace, monospace`)

Both are loaded through `next/font/google`. Notably `--font-sans` and
`--font-mono` both resolve to VT323: there is no proportional face anywhere in
the system, by intent. Geist, Inter, Instrument Serif and JetBrains Mono are
absent and must stay absent.

**Character:** Press Start 2P is a hard pixel face, unreadable in bulk and used
only for the wordmark and section headings. VT323 carries everything else with a
tall, narrow, cathode-tube feel that suits a transcript.

### Hierarchy

- **Display** (Press Start 2P, `clamp(1.875rem, 5vw, 2.25rem)`, 1.25): the
  wordmark only.
- **Headline** (Press Start 2P, 1.125rem, 1.25): section headings.
- **Body** (VT323, `clamp(1.125rem, 2vw, 1.25rem)`, 1.375): hero copy, terminal
  transcript, results.
- **Label** (VT323, 0.875rem, uppercase, 0.05em tracking): field labels, counters,
  helper text. Raised from 0.75rem: VT323's x-height is near half its em, so 12px
  rendered like ~9px of a normal face and "Show sprites" was barely legible.

### Named Rules

**The Pixel Sparingly Rule.** Press Start 2P appears at the wordmark and section
headings only. It has no lowercase rhythm and no comfortable reading size; using
it for more than a few words is a legibility failure, not a stylistic one.

**The Open Pairing Rule.** This pairing is provisional. Self-hosted retro faces
have not been evaluated, and the pairing may be replaced — but only by another
retro/pixel pairing, never by a neutral grotesque.

## Layout

A single centred column, `max-width: 56rem` (`max-w-4xl`), with `24px` horizontal
padding. The page is one continuous scroll: hero terminal, then the encode/decode
tool. Vertical rhythm runs on a `4 / 8 / 12 / 16 / 24 / 40px` scale.

**Whitespace is the system's weakest area and its main open work.** Positive and
negative space here must do grouping and association — binding a label to its
field, separating the hero's wordmark from its kicker without stranding them,
and guiding the eye down to the tool. At present the hero's text elements are
spaced too loosely, so the wordmark and the `$ encrypt.txt --help` line read as
unrelated rather than as a unit. The terminal panel is also undersized for its
role as the primary interactive surface.

Mobile requires a considered layout, not a reflow of the desktop column.

### Named Rules

**The Grouping Rule.** Space communicates relationship. Elements that belong
together are closer to each other than to anything else, and no gap inside a
group may exceed the gap around it.

## Elevation & Depth

**There are no shadows in this system.** Depth is entirely tonal: five stepped
greens stack surfaces against one another, and every surface additionally
carries a `1px` border in LCD Border (`#2c5c2c`), applied globally via
`* { border-color: var(--border) }`. The terminal interior goes *darker* than the
page rather than lighter, reading as a recessed screen rather than a raised card.

Soft, blurred, ambient "lifted card" shadows are banned outright and are
incompatible with the world.

A **hard black pixel-offset shadow** — zero blur, a solid offset block, the 8-bit
convention — is a different thing and is an open, sanctioned experiment for
buttons. If tried and disliked, reverse it; that is the intended working method.

### Named Rules

**The Flat Field Rule.** Nothing floats. Separation comes from tone and border,
never from blur.

## Shapes

Hard edges without exception: `--radius: 0px`, and the token exists mainly to
make the zero explicit to anything that looks for it. Every panel, button, input
and chip is a plain rectangle with a `1px` border. Sprites render with
`image-rendering: pixelated` and the backdrop tile uses `shape-rendering:
crispEdges`, so no anti-aliasing softens the pixel grid.

### Named Rules

**The No-Curve Rule.** A radius above `0px` anywhere is a defect. The Game Boy
could not draw one.

## Components

shadcn is the chosen base specifically because the components are owned outright
and compatible designs from elsewhere can be imported and tweaked rather than
fought. Preserve that ownership: prefer adapting a primitive in-repo over adding
a dependency that hides it.

### Buttons

- **Shape:** square (`0px` radius), `1px` border, `40px` tall at default size.
- **Primary:** cartridge yellow fill (`#ffd100`) with LCD Deep text (`#0f380f`),
  border matching the fill. The only yellow-filled element on the page.
- **Secondary:** LCD Moss fill (`#265626`), LCD Wash text, LCD Border stroke.
- **Outline / Ghost:** transparent, LCD Wash text; ghost drops the border.
- **Hover:** colour shift only (`transition-colors`); no lift, no scale.
- **Focus:** `2px` ring in LCD Olive (`#8bac0f`).
- **Known gap:** these are still generic shadcn shapes. A pixel-art treatment is
  wanted, with pixelact-ui, 8bitcn and glitchcn-ui as unevaluated candidates.

### Terminal Panel (signature component)

The defining component. A bordered rectangle with a chrome bar above a
transcript body.

- **Chrome bar:** LCD Moss (`#265626`) ground, LCD Sage (`#9bbc8a`) label text,
  bottom border. Carries the literal word `bash`. **Currently fails contrast at
  4.08:1.**
- **Body:** Terminal Void (`#071a07`), VT323, line-per-entry transcript.
- **Line kinds:** command (LCD Wash, prefixed with a yellow `$`), output (LCD
  Olive), error (Alert Rust — **fails at 3.01:1**), info (LCD Sage).
- **Cursor:** a solid `12 × 20px` cartridge-yellow block, blinking on a `1.1s`
  hard-step cycle with no fade.
- **Required:** the panel must carry a thin cartridge-yellow border so it stands
  off the ground. Not yet implemented.
- **Absolutely not:** three red/amber/green dots in the chrome bar. They tell the
  user nothing, clash with the palette, and fill space for its own sake.

### Inputs / Fields

- **Style:** LCD Shade (`#1d4d24`) interior, `1px` LCD Border stroke, square,
  `12px` padding, VT323.
- **Focus:** `2px` LCD Olive ring, no border colour change.
- **Over-limit:** the character counter switches to Signal Coral past 4,000.

### Token Chip (signature component)

One unit of ciphertext. Either a `32 × 32px` bordered cell holding a pixelated
sprite, or — when sprites are off or the sprite fails — the Pokémon name in a
bordered LCD Moss chip. The fallback is a first-class state, not an error.

## Do's and Don'ts

### Do

- **Do** keep yellow scarce. It marks the prompt, the cursor, the primary
  action, and the terminal's border. Nothing else.
- **Do** render decoder uncertainty as visible notation. `[x,y]` and `{x,y}` are
  the product's most distinctive output.
- **Do** let colour carry meaning on its own where that is the stronger design.
  No blanket rule applies in either direction here; decide case by case. A
  control that needs a tooltip to explain itself has failed visually.
- **Do** use space to group. Related elements sit closer together than
  unrelated ones.
- **Do** keep every surface bordered and flat.
- **Do** treat treatments as reversible experiments.

### Don't

- **Don't** add soft, blurred or ambient shadows. (A hard pixel-offset block is
  a separate, permitted experiment.)
- **Don't** introduce any corner radius above `0px`.
- **Don't** add Geist, Inter, Instrument Serif, JetBrains Mono, or any neutral
  grotesque. Retro faces only.
- **Don't** put the three macOS traffic-light dots on the terminal chrome.
- **Don't** place the kicker above the wordmark; it sits below.
- **Don't** reuse a decoder signal colour for anything that is not a decoder
  state.
- **Don't** set body copy in Press Start 2P.
- **Don't** ship `#e0674f`, `#b03a2e`, or `#9bbc8a`-on-`#265626` at their current
  contrast; all three fail AA where they are used.
