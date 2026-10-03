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

### F1 — fixed: the decode gate was advertised but not enforced

`next-app/app/page.tsx` rendered the Decode button with `aria-disabled={!canDecode}`
and `opacity-40`, and `PRODUCT.md` specifies the control is "gated rather than
error-handled". But `aria-disabled` does not suppress click events, and `run()`
guarded only `hasInput`, `tooLong` and `busy` — never `canDecode`.

**Observed consequence:** clicking the visibly-shaded Decode button while the
input was ordinary prose still issued `POST /api/decode`, and replaced the
result panel with a wall of `<?unknown: ...>` markers. The control looked off,
announced itself as off, and worked anyway — directly contradicting the status
line beside it ("Not Pokemon names, so decoding is off.").

**Fix:** extract the three input preconditions into one pure, testable function
`blockedReason(mode, text, known)` in `lib/pokecipher-api.ts`, and have `run()`
consult it. This keeps the gate in the module that already owns
`looksLikeCiphertext` and `isWithinLimit`, so the component cannot drift from
it, and it is unit-testable in the existing `node`-environment vitest setup —
`jsdom` and `@testing-library/react` are not installed, so a component test was
not available without adding dependencies.

**Behaviour preserved:** the empty-input and over-limit messages are unchanged
byte for byte. Only the previously-missing decode guard is new. Encoding is
never gated, per `PRODUCT.md`.

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

