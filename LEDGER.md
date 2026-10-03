# Ledger — product-quality and correctness pass

> Chronological record of this pass: what was measured, what was changed, and
> what was deliberately left alone. Governed by `DOD.md`. Every number here came
> from a command run in this session, on branch `chore/single-viewport-quality`
> at `de79dea`.

## Environment

| Fact | Value |
|---|---|
| Python | 3.13.3 (venv); `.python-version` pins 3.12 for deploy |
| Node / npm | v24.16.0 / 10.8.2 |
| `next-app/node_modules`, `next-app/.next` | present |
| Working tree at start | clean apart from untracked scratch files |

## Baseline (measured before any edit)

| Gate | Command | Result |
|---|---|---|
| Backend tests | `python -m pytest -q` | **206 passed**, 7208 subtests, 13.91 s |
| Backend lint | `python -m ruff check .` | clean |
| Backend format | `python -m ruff format --check .` | 26 files already formatted |
| Frontend tests | `npm run test` | **46 passed** (2 files) |
| Frontend lint | `npm run lint` | clean |
| Frontend typecheck | `npm run typecheck` | clean |
| Frontend build | `npm run build` | compiled in 5.2 s, 4 static pages |

## Claims checked against the running cipher

The UI and README hardcode cipher output. Each was re-derived from the real
encoder rather than trusted.

| Claim | Where | Verdict |
|---|---|---|
| `Hello` → `Zubat Weepinbell Ponyta Gyarados Slowbro` | `cli-hero.tsx`, `readme.md`, `test_app.py` | **correct** |
| `Hello World!` round-trips to `Hello W[n,o]rld!` | `cli-hero.tsx`, `readme.md` | **correct** |
| `Slowpoke` is Kanto `n` vs Johto `o` | `cli-hero.tsx`, `readme.md` | **correct** — `lookup_name("Slowpoke") == [('n', 0), ('o', 1)]` |
| `GET /api/names` returns 210 names | `readme.md` | **correct** — `len(NAME_INDEX) == 210` |
| Each region supplies 95 entries | `readme.md`, `pokedex.py` | **correct** — Kanto/Johto/Hoenn all 95 |
| No indexed name contains a space | `readme.md` (delimiter limitation) | **correct** — none; only `Farfetch'd` carries punctuation |

No documentation drift found in the cipher claims. Nothing changed here.

## Findings

### F1 — investigated and DISPROVEN: the decode gate is enforced

**Suspected:** `next-app/app/page.tsx` renders Decode with `aria-disabled={!canDecode}`
and `opacity-40`, and `aria-disabled` does not suppress click events. `run()`
guards `hasInput`, `tooLong` and `busy` but never `canDecode`. Read in isolation
that looks like a control that announces itself as off and works anyway.

**Disproof — the exact call site, `page.tsx:218`:**

```tsx
onClick={() => canDecode && run("decode")}
```

The handler short-circuits on `canDecode`, so the button cannot fire while the
gate is shut. `aria-disabled` and the shading *announce* the condition; the `&&`
in `onClick` *enforces* it. Both are present and consistent, and the keyboard
shortcut at `page.tsx:183` routes through the same `canDecode` test. This matches
`PRODUCT.md`: gated, with `aria-disabled` chosen over `disabled` deliberately so
the control keeps its place in the tab order.

**No defect. No change made.**

The suspicion was acted on before it was proven: a prototype fix (a pure
`blockedReason(mode, text, known)` extracted into `lib/pokecipher-api.ts`, with
nine regression tests written failing-first — confirmed red, `9 failed | 46
passed`) was built on the unverified premise. Reading the call site disproved it,
and both files were restored with
`git checkout -- next-app/lib/pokecipher-api.ts next-app/lib/pokecipher-api.test.ts`.
The suite is back to **46 passed**, and `git status` shows no modification to
either file.

Recorded in full because the near-miss is the useful part. `run()` genuinely
reads as though the gate is missing, and the next reader will suspect the same
thing. Moving the guard into `run()` would be a readability improvement, but
`AGENTS.md` forbids defensive branches for states that cannot occur, and this one
cannot — so it stays as it is. **This is exactly the failure `DOD.md`'s
"evidence, not memory" rule exists to catch.**

## Outcome

**No product code changed in this pass.** Every claim the product makes about the
cipher was re-derived from the running encoder and held. The one suspected defect
was disproven at its call site and reverted. The two real observations (F2, F3)
are contract decisions that belong to the user, not bug fixes to make
unilaterally.

### Verification after the revert

| Gate | Result |
|---|---|
| `npm run test` | **46 passed** (2 files) — back to baseline |
| `git status` for `next-app/` | clean; neither reverted file is modified |

Because the revert restored both files byte for byte, the tracked tree differs
from `de79dea` only by the two documentation files, so the backend baseline
(206 passed, ruff clean, format clean) still holds unchanged.

### Commits

| SHA | Message |
|---|---|
| `e14cbf7` | docs: add the definition of done and the work ledger |
| _(this commit)_ | docs: correct the ledger — the decode gate was never broken |

**Nothing pushed.** `DOD.md` requires explicit approval before a push, and both
`.vercel.app` names are pinned deployment aliases that must be re-pointed by hand
after any merge to `main`.

## Open items handed back

1. **F2 — decide the byte cap.** Whether `MAX_BODY_BYTES` should rise so a
   4,000-character non-ASCII message cannot be rejected by the byte cap. Not
   reachable from the browser; changing it requires updating
   `test_body_exactly_at_the_size_limit_is_accepted`, which pins 32 KiB exactly.
2. **Scratch files that predate this pass are not gitignored.** `.gitignore`
   covers `_*.txt`, but not the `._`-prefixed or `out_`-prefixed forms, so these
   still show as untracked: `._probe_*.txt`, `._tmp_*.txt`, `_issues.json`,
   `out_*.txt`. Deleting them or extending the ignore rule is a small hygiene win.
   The `_verify*.py` probes written during this pass were deleted.
3. **Optional readability, deliberately not done.** `run()` in `page.tsx` reads as
   though the decode gate is missing because the guard lives in the `onClick`
   prop. Consolidating it would read better but adds a branch for a state that
   cannot occur, which `AGENTS.md` forbids.


### F2 — recorded, not changed: the 32 KiB body cap can reject legal input

`app.MAX_TEXT_CHARS` is 4,000 characters and `app.MAX_BODY_BYTES` is 32 KiB.
Those two caps are independent, and JSON escaping means the byte cap can bind
first. Measured through `TestClient`:

| Input | Chars | Body bytes | Status |
|---|---|---|---|
| `"a" * 4000` | 4,000 | 4,012 | 200 |
| `"日" * 4000` | 4,000 | 24,012 | 200 |
| `"😀" * 4000` | 4,000 | 48,012 | **400** |

A 4,000-character emoji string is legal under the documented character cap but
is rejected by the byte cap, with the message "Expected a JSON object body under
32 KiB." — which does not tell the caller that their *character* count was fine.

**Why this was left alone:** the browser path is unaffected. `JSON.stringify`
emits non-ASCII literally, so 4,000 emoji reach the wire as ~16 KB UTF-8, well
inside the cap; the 48 KB figure is an artefact of Python's `json.dumps`
defaulting to `ensure_ascii=True`, which escapes each surrogate pair to 12
bytes. So this is not reachable from the product's only client.

Raising `MAX_BODY_BYTES` would also break `test_body_exactly_at_the_size_limit_is_accepted`,
which pins 32 KiB exactly and asserts one byte more is a 400 — a deliberate
transport guard, consistent with the `AGENTS.md` rule "cap limits at the
transport, not in the core". Changing it is a contract decision for the user,
not a bug fix. **Recorded for a decision, not silently altered.**

### F3 — recorded, not changed: pre-existing decoder limitations stay pinned

Two known limitations were confirmed to be documented *and* test-pinned, so they
are not defects to fix:

- `MAX_DECODE_BRANCHES` (32) truncation can drop the true reading; pinned in
  `test_cipher_invariants.py`.
- Literal `[` / `{` in plaintext decodes to text indistinguishable from a
  marker; documented in `lib/markers.ts`.

Both would require changing the decode contract, which `DOD.md` forbids without
explicit approval.


---

# Ledger — favicon correctness pass

> A second, later pass, on top of the one above and under the same rules. Every
> number here came from a command run in this session, on branch
> `feat/branding-assets` at `1cd2b73`.

## Environment

| Fact | Value |
|---|---|
| Python | 3.13.3 (venv) |
| Node / npm | v24.16.0 / 10.8.2 |
| Working tree at start | clean apart from untracked scratch probes |

## The report

The deployed tab icon was reported wrong: `icon.svg` was correct, `favicon.ico`
was not the character. Both files are written by `docs/make_favicon.py` from the
same source, so the divergence had to be in the raster path specifically. It was
not a deployment fault — the committed ICO really was wrong.

## Findings

### F4 — the ICO point-sampled the art and discarded most of it

`disc_pixel` read exactly one art pixel per output pixel:

```python
u = int(math.floor((cx - placement.origin[0]) / placement.scale))
```

At 16x16 an output pixel spans `CANVAS / size = 2` viewBox units, while the art
grid is `scale ~= 0.884` units per pixel, so consecutive samples sat ~2.26 art
pixels apart. **Roughly 56% of the art in each axis — about 80% by area — was
never read**, and the eyes and the nose are what go first. This is precisely the
loss `downsample` box-averages 56->28 to avoid, reintroduced one level further
down.

### F5 — the sprite's ink could equal the disc's own field

`DISC = DMG_RAMP[0]` and `quantise` chose from the **whole** ramp, field included.
`sprite_ink` composited onto `DISC` and then quantised, so any colour below the
39.0/77.4 luminance midpoint landed on the field colour and vanished. Measured on
the old code:

| Sprite grey | Old ink | Visible? |
|---|---|---|
| 0 (`rgb(0,0,0)`) | `(15,56,15)` | **no — identical to the field** |
| 21 | `(15,56,15)` | **no** |
| 42 | `(15,56,15)` | **no** |
| 56 | `(15,56,15)` | **no** |
| 63 | `(48,98,48)` | yes |

The committed SVG carries 13 runs of `rgb(0,0,0)`, 8 of `rgb(42,42,42)`, and one
each of `rgb(21,21,21)` and `rgb(56,56,56)`: Pikachu's outline, ear tips and eye
pupils. Every one of them was being painted in the background colour. The vector
SVG was unaffected because it is geometry, which is exactly the reported
asymmetry.

### F6 — the ICO could not be regenerated at all

`main` required a sprite path. That sprite is Nintendo's art and is deliberately
not committed, and no copy existed on disk, so `favicon.ico` was **stuck**: any
edit would have had to be made by hand, which is how a generated asset and its
generator drift.


## Changes

| File | Change |
|---|---|
| `docs/make_favicon.py` | One geometry representation (`Rect`) that both routes share: `rects_from_sprite` / `format_rects` / `parse_rects`, with a single `paint` and a single `rasterise`. |
| `docs/make_favicon.py` | `disc_pixel` averages over the output pixel's whole footprint instead of point-sampling it (F4). |
| `docs/make_favicon.py` | `SPRITE_RAMP = DMG_RAMP[1:]`, so sprite ink can never be the field colour (F5). |
| `docs/make_favicon.py` | `python docs/make_favicon.py` with no argument rebuilds `favicon.ico` from the committed `icon.svg` (F6). |
| `next-app/app/favicon.ico` | Regenerated from the committed `icon.svg`. |
| `test_favicon.py` | 16 regression tests, 306 subtests (new file). |
| `readme.md` | Branding section: the new command, the field/ink rule, the averaging rule, and the ICO's fixed theming. |
| `LEDGER.md` | This record. |

`icon.svg` is deliberately **unchanged**. The vector was already correct, and
regenerating it would have risked the one artefact that was confirmed to look
right.

## Verification

The ICO was regenerated from the committed SVG, then decoded back and compared
against a fresh rasterisation of that same SVG:

| Check | Result |
|---|---|
| `python docs/make_favicon.py` | 193 rects, 256x256 surface, **2848 bytes**, sizes 16+32+48+256, 3 sprite shades |
| Each ICO entry vs. a fresh `rasterise` | all four sizes **identical** |
| `sprite_ink` for every grey 0..255 | **none** equal `DISC`; four of the sampled levels did before |
| Outline ink present at 16x16 | 33 pixels of `(48,98,48)` — it was 0 before |
| `favicon.ico` size | 2781 -> 2848 bytes |

| Gate | Command | Result |
|---|---|---|
| Backend tests | `python -m pytest -q` | **222 passed**, 7514 subtests, 7.83 s |
| Backend lint | `python -m ruff check .` | clean |
| Backend format | `python -m ruff format --check .` | 31 files already formatted |
| Frontend tests | `npm run test` | **46 passed** (2 files) |
| Frontend lint | `npm run lint` | clean |
| Frontend typecheck | `npm run typecheck` | clean |
| Frontend build | `npm run build` | compiled in 2.4 s, 5 static pages |

The backend totals rose from the 206 / 7208 recorded above by exactly the 16 tests
and 306 subtests added here. No existing test was edited.

## No core-cipher change

`pokecipher/`, `app.py` and `cipher.py` were not touched by this pass, nor by any
of the four branding commits beneath it; they name only `docs/`,
`next-app/app/`, `readme.md`, `.gitattributes` and the added `test_favicon.py`.
**No decoder branching, ambiguity resolution or `MAX_DECODE_BRANCHES` behaviour
was introduced or altered**, so the limitations recorded as F3 above stand
unchanged and remain pinned by `test_cipher_invariants.py`.


## Commits

| SHA | Message |
|---|---|
| `fedaeec` | `fix(docs): rasterise the favicon from the SVG and keep sprite ink off the field` |
| `5af00f4` | `test: pin the favicon to the SVG and the sprite ink to the ramp` |
| _(this commit)_ | `docs: record the favicon correctness pass` |

An earlier attempt landed `test_favicon.py` under the `fix(docs)` message: two
`git` invocations were issued as parallel commands and collided on
`.git/index.lock`, so one `git add` never ran. Nothing was pushed, the commit was
reverted with `git reset --soft HEAD~1`, and both commits were re-made in a single
sequential command. The SHAs above are the re-made ones.

## Open items handed back

1. **The ICO cannot follow the theme.** A raster favicon is drawn in browser
   chrome, outside the document, so it sees neither the app toggle nor a media
   query. It carries a fixed dark field and a light ring instead, which is now
   stated in `readme.md`. That is a platform limitation, not something the
   generator can work around.
2. **`icon.svg` is now the source of truth for the mark.** To change the art, the
   vector must be regenerated from a fresh sprite first and the ICO rebuilt from
   it afterwards. The sprite is still deliberately not committed, so changing the
   *art* needs Nintendo's PNG from outside the repository — but rebuilding only
   the raster does not.
3. **The tab icon keeps a fixed palette by design.** The sprite is greyscale
   source art, so the ICO quantises it onto the Game Boy ramp. That is what puts
   it in the app's palette, and it is also why it will never follow the page's
   theme toggle.

