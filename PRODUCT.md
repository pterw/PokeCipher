# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: **portfolio visitors judging craft** — recruiters, engineers and
designers who land here to assess the author's work. The cipher is the demo;
the build quality and the design are themselves the deliverable.

Secondary, and explicitly required rather than incidental: the thing must
actually be **fun to use**, not a static case study. A visitor who only reads
and never plays with it has had a worse experience than the product intends.

## Product Purpose

PokéCipher turns plaintext into space-separated Pokémon names and turns those
names back into plaintext. It is a stateful polyalphabetic substitution cipher
built as a puzzle and a teaching artifact for substitution ciphers and state
tracking.

Success is a visitor who understands what the cipher is doing, tries it on
their own text, and comes away with a higher opinion of the author's
engineering and design judgment.

It is explicitly **not** a way to protect data and must never be presented as
one. The repository states this directly and future work must not soften it
into security-adjacent language.

### The product must explain itself

A dedicated **"What is a cipher?"** area is required, not optional. Being a toy
and teaching the principles it uses are the same goal here, not competing ones.

**The hero terminal is the surface for this.** Decided 2026-08-30 by the user:
"Terminal is plenty of hero space to explain in pseudo code on how to use the
app." The terminal carries the *abstraction* — pseudocode for what a cipher is
and how to drive the app — which suits the Field Terminal world, where the
machine explains itself in its own transcript rather than in marketing prose.

A **second, quieter surface** is still needed for this cipher's specific mapping
(the `ord(char) - 32` index, the `N % 3` region cycle, why ambiguity appears).
Pseudocode in the terminal and the concrete mapping are two different jobs.

The explainer must cover what the product currently assumes visitors already
know and they do not: that there are only **three** Pokédex regions in play, and
that this number is what governs how often ambiguity appears.

Explanatory copy uses **ASD-STE100 Simplified Technical English**, approximately
rather than to the letter: short sentences, one instruction per sentence,
controlled vocabulary, no idiom, consistent terms for the same thing every time.

## Positioning

The mechanism a neighboring toy could not truthfully copy is the **deliberate,
principled lossiness**:

- Each printable ASCII character (32–126) maps to index `ord(char) - 32`.
- Regions cycle per character occurrence: the Nth occurrence of a character
  uses region `N % 3` (Kanto → Johto → Hoenn), so repeated characters rarely
  produce the same Pokémon.
- Pokémon names legitimately repeat across regional dexes. That overlap makes
  decoding **genuinely ambiguous**, and that ambiguity is the interesting part
  of the cipher, not a defect.
- The decoder forks one branch per candidate character and merges branches that
  reconverge, so a later token often retroactively resolves an earlier
  ambiguity.

Design consequence: the ambiguity markers are the product's most distinctive
output. They are a feature to be surfaced and explained, never an error state
to be hidden, styled away, or silently resolved by guessing.

## Operating Context

Two workflows, both first-class:

1. **In-place round-trip.** Encode, then decode, to watch the mechanism work.
   The ambiguity markers are the payoff of this loop.
2. **Copy and hand off.** The user wants a copy affordance that yields the
   Pokémon names so they can run a reverse pass themselves or send the result
   to a friend. Shareability is a stated goal.

A copy control exists in the current implementation but gives no confirmation
feedback and does not handle a rejected clipboard permission.

## Capabilities and Constraints

- Printable ASCII 32–126 only. Non-printable characters are preserved as
  tokens: `[NEWLINE]`, `[RETURN]`, `[CHAR:N]`.
- Only the first 95 entries of each regional dex are used. Names containing
  spaces (Mr. Mime, Tapu Koko) cannot be added without changing the delimiter.
- **Three regions (Kanto, Johto, Hoenn) is a design parameter, not a fixed law
  of the cipher.** The count sets the cycle length, so it directly controls how
  often ambiguity occurs. Folding in a fourth generation would raise both the
  complexity and the frequency of ambiguity. No decision has been made to do
  so; the explainer should make the current number and its consequence legible.
- Input is capped at 4,000 characters. Decode time is near-linear for ordinary
  prose (~1.2 s for 10,000 characters on CPython 3.13) but degrades to
  quadratic when an ambiguity never collapses (~3.3 s at 4,100 characters). The
  cap keeps the worst case inside the serverless function timeout.
- Python is the single source of truth for the cipher. The frontend never
  re-implements it; it calls `POST /api/encode` and `POST /api/decode`, which
  take `{"text": "..."}` and return `{"result": "..."}`.
- `GET /api/names` serves the 210 indexed Pokémon names (~2 KB, cached an hour)
  so the frontend can tell ciphertext from plaintext without copying the dex
  into TypeScript. Adding a region reaches the UI with no frontend edit.
- Decoding is **case-insensitive**. Ciphertext routed through a URL, a chat
  client or a spreadsheet arrives lowercased, and the old failure was silent:
  every token became `<?unknown: ...>` with nothing indicating case was why.
  Folding is safe and asserted — no two of the 210 names collide when folded.
- Sprites come from the PokémonDB CDN keyed by name, falling back to the name
  when a slug is unknown. The set is `ruby-sapphire` — Generation 3, GBA, the
  same hardware whose palette the design system emulates, and whose roster is
  exactly Kanto + Johto + Hoenn. All 210 names resolve there, at ~626 bytes
  each. The sprites are 64×64, so a 32px cell is an exact 2:1 downscale, which
  is what makes `image-rendering: pixelated` faithful rather than destructive.
- Deployed on Vercel as two projects from one repository. A single project
  cannot serve both, because a detected framework preset takes over all routing
  — Vercel's [Services](https://vercel.com/docs/services) is the sanctioned way
  to combine them if that is ever revisited. The `/api/*.py` file-based Python
  path is **not** available: Vercel now grants it only to projects created
  before it was retired, so a new project fails in `vercel build` before
  dependencies install.

### Terminology (durable; do not rename)

| Notation | Meaning |
|---|---|
| `x` | Decoded unambiguously. |
| `[x,y]` | **Ambiguity** — the cipher is lossy here; several characters remain valid. |
| `{x,y}` | **State mismatch** — no valid interpretation; ciphertext likely corrupted. |
| `<?unknown: X>` | `X` is not a known Pokémon name. |

### Open decisions

- **Which surface is the canonical tool is undecided.** The page currently
  carries two complete, independently working encode/decode clients: the CLI
  terminal hero and the form beneath it. Whether the terminal is the product or
  a demo has not been settled, and most layout decisions follow from it.
  Related known defect: the terminal's opening line reads `encode "Try below"`,
  which points the visitor downward while the terminal itself accepts input.
  The affordance and the copy contradict each other.
- **Pixel-art component library is unchosen.** Candidates the user raised, to be
  evaluated for compatibility (Tailwind v4 + React 19 + shadcn) and for the
  elements each actually provides: **pixelact-ui**
  (<https://www.pixelactui.com/>, <https://github.com/pixelact-ui/pixelact-ui>),
  **8bitcn**, and **glitchcn-ui** (as a restyle layer). The goal is to stop
  using generic shadcn buttons. Three need comparing before one is picked.
- **Whether a fourth generation gets folded in** — see Capabilities.
- **Self-hosted retro/8-bit fonts are unexplored.** The current pairing
  (Press Start 2P + VT323, via `next/font/google`) was a ship-fast choice, not a
  considered one. The user has not ruled out self-hosting a better retro face.
- **The Game Boy green palette is good but not married to.** It stays unless it
  fails the squint test or a better direction earns its place.

### Working method

Design here is **iterative and reversible**. The user expects to try a treatment,
look at it, and back it out if it does not hold up — a reversal is the process
working, not a mistake to avoid. Do not treat a recorded preference as permanent
when the user asks to try its opposite.

shadcn was chosen deliberately for this: you own the components outright, and
compatible designs from elsewhere can be imported and tweaked rather than
fought. Component choices should preserve that ownership and importability.

### Decided, pending implementation

- **404 page uses `@23rd/dithered-404`**, if and when a route can 404.

## Brand Commitments

Volunteered by the user as binding; recorded as stated, not expanded:

- **No soft or decorative drop shadows.** This ban is about blurred, ambient,
  "lifted card" shadows, which do not belong in this world. It is *not* a ban on
  a **hard black pixel-offset shadow** — a zero-blur offset block, the 8-bit
  convention — which the user has named as something they may want on buttons.
  Treat that as an open, reversible experiment rather than a violation.
- **Yellow as the accent** to contrast the heavy green palette.
- **No fake macOS traffic lights** — the three red/amber/green dots on mock
  terminal chrome tell users nothing, clash with the design system, and fill
  space for its own sake. Already removed; must not return.
- **The kicker/eyebrow sits below the wordmark**, not above it.
- **Retro fonts only.** Press Start 2P (pixel) and VT323 (terminal). The user
  objects specifically to Geist, Inter, Instrument Serif and JetBrains Mono
  appearing by default where they do not fit the design.
- **No rounded corners** (`--radius: 0px` in the incumbent tokens).
- The product name carries the accent: **PokéCipher**. The UI currently renders
  it as "PokeCipher".
- **Explanatory copy follows ASD-STE100** (approximate Simplified Technical
  English), per Product Purpose.
- **The terminal is wrapped in a thin yellow border** so it stands out against
  the background. This was asked for previously and has not been done.
- **The terminal is currently too small.**
- **The hero has too much vertical space between its text elements** — between
  the "PokéCipher" wordmark and the `$ encrypt.txt --help` line in particular.
- **The pistachio green in the hero is rejected.** Identified as `#d7f5c4`
  (`--foreground`), the colour of the wordmark and the hero text.
- **The Pokémon theming is too weak.** It needs to read as genuinely Pokémon,
  not as a generic retro terminal that mentions Pokémon.
- **An 8-bit Pokéball replaces the "o" in PokéCipher** in the wordmark. The user
  will supply this as an SVG from Illustrator.

## Evidence on Hand

Real, verified, and safe to use:

- Worked example: `Hello` becomes `Zubat Weepinbell Ponyta Gyarados Slowbro`.
  The two `l`s become `Ponyta` then `Gyarados` because the second has cycled to
  Johto.
- Ambiguity example: `Hello World!` round-trips to `Hello W[n,o]rld!` —
  `Slowpoke` maps to both `n` (Kanto) and `o` (Johto) and nothing later
  disambiguates it.
- Retroactive-resolution example: `Nidoking Geodude Shroomish Nidoking` decodes
  cleanly to `AAAA`, though `Geodude` alone is ambiguous.
- `Screenshot.png` at the repository root.
- Test suite: 178 Python tests (250 subtests), 97% statement coverage; 46
  frontend tests. Measured 2026-08-30; these counts drift silently, since
  nothing verifies them against the suite.

No testimonials, users, customers, benchmarks, press, pricing or adoption
figures exist. Future work must not fabricate any.

### Assets the user will supply

The user is a designer and will produce these rather than have them generated.
Do not substitute approximations without asking.

- An **8-bit Pokéball SVG** for the "o" in the PokéCipher wordmark, from
  Illustrator.
- Optionally a **mark** — either standalone or designed as one cohesive lockup
  with Press Start 2P.
- Optionally a **favicon set** for fallback: SVG plus 32×32 and 16×16.

## Product Principles

1. **Ambiguity is the feature.** Surface and explain `[x,y]` and `{x,y}`. Never
   hide them, never guess past them, never style them as failures.
2. **Never imply security.** This is a puzzle and a teaching artifact. No lock
   iconography, no "encrypt your secrets" framing.
3. **Craft is the argument.** The primary user is judging the author's work, so
   the interface itself carries the case. Unpolished detail is a product defect
   here, not a cosmetic one.
4. **Playable, not just legible.** A visitor who reads without trying it has
   been failed. Lower the cost of a first attempt.
5. **One source of truth.** The cipher lives in Python. Any frontend that
   reimplements or approximates it is wrong regardless of how well it reads.

## Accessibility & Inclusion

Target **WCAG 2.2 AA**, applied with judgment rather than as a checklist.
Pragmatic deviations are acceptable — a 44px minimum touch target, for example,
is not treated as mandatory. Two requirements are firm:

- A **clearly thought-out mobile layout**, not a desktop layout that merely
  reflows.
- **All errors handled gracefully.**

Confirmed contrast defects, measured against the incumbent tokens:

| Usage | Colors | Ratio | Status |
|---|---|---|---|
| `bash` chrome label on hero | `#d7f5c4` on `#265626` | **7.27:1** | fixed 2026-08-29, was 4.08:1 |
| Terminal `err` lines | `#b03a2e` on `#071a07` | **3.01:1** | fails |
| Error panel text | `#e0674f` on `#0f380f` | **3.91:1** | fails |
| `marker-mismatch` on card | `#e0674f` on `#14421a` | **3.41:1** | fails |

The rest of the palette passes, several comfortably: body text 11.14:1, the
yellow accent on terminal 12.39:1, `marker-ambiguous` on card 6.27:1,
`marker-unknown` on card 5.11:1.

The `marker-mismatch` contrast failure is a real defect and should be fixed.

**Colour carrying meaning is not itself a defect here.** Per the user, this is a
design judgment and no hard rule applies in either direction. Colour that
carries semantics on its own is often exactly the goal: if a green button with
an arrow needs a tooltip to explain itself, that is a failure of the visual
design, not a success of the annotation. The inverse is equally true in other
places. Decide it case by case on the merits; do not apply
"never convey meaning by colour alone" as a blanket rule, and do not add
explanatory tooltips to compensate for a mark that should have been legible.

Live regions: the tool below the hero now announces its dynamic output — the
result panel and the decode-gate status are `aria-live="polite"`, and the error
panel is `role="alert"`. **The hero terminal is still silent**: its transcript
appends command, output and error lines with nothing announced, which is the
larger of the two surfaces for a screen-reader user.

The decode control is gated rather than error-handled. It is shaded and
`aria-disabled` until the first whitespace-delimited token of the input is a
known Pokémon name, with a persistent status line saying why. `aria-disabled`
rather than `disabled` deliberately, so the control keeps its place in the tab
order and stays announced instead of vanishing. Encoding is never gated: any
text is encodable, and the asymmetry is the point.
