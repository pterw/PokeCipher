# AGENTS.md

> Operational contract for coding agents in this repository.
> Read it fully before editing anything.

## Rules for Gemini

- Treat this file as authoritative; when a prompt conflicts with it, follow it and say so.
- Plan before writing. State the files you will touch and why.
- Change behaviour only when asked. Refactors must preserve existing output byte for byte.
- Never reformat files you did not otherwise need to change; keep diffs reviewable.
- Run the full verification sequence before declaring any task done (see Commands).
- Report honestly: if a test fails, a check fails, or you are unsure, say so instead of guessing.
- Have suggestions when it comes to installing or initializing any skills for front-end polish or design.

## Project

PokéCipher is a stateful polyalphabetic substitution cipher. It turns plaintext
into space-separated Pokémon names drawn from three regional Pokédexes (Kanto,
Johto, Hoenn), and turns those names back into plaintext.

- Each printable ASCII character (32-126) maps to index `ord(char) - 32`.
- The Pokémon at that index in the current region becomes the ciphertext unit.
- Regions cycle per character: the Nth occurrence of a character uses region
  `N % 3`, so repeated characters rarely produce the same Pokémon.
- Names repeat across regions by design. That overlap makes decoding ambiguous,
  which is the point of the cipher.
- Non-printable characters are preserved as tokens: `[NEWLINE]`, `[RETURN]`,
  `[CHAR:N]`.

Decoding forks one branch per candidate character and merges branches that
reconverge, so a later token often retroactively resolves an earlier ambiguity.

### Decoder output notation

| Notation | Meaning |
|---|---|
| `x` | Unambiguous across all surviving branches. |
| `[x,y]` | Genuine ambiguity: several characters remain valid. |
| `{x,y}` | State mismatch: no branch could consume the token; likely corruption. |
| `<?unknown: X>` | `X` is not a known Pokémon name. |
| `<?error encoding: X>` | Legacy `[err:...]` token; the encoder no longer emits these. |

## Repository layout

```
pokecipher/      Cipher core. One concern per module.
  constants.py   Invariant numbers. Imports nothing else in the package.
  errors.py      Exception types.
  pokedex.py     Pokédex data, import-time validation, name→(char, region) index.
  tokens.py      Spelling and parsing of [NEWLINE]/[RETURN]/[CHAR:N]/[err:...].
  markers.py     Formatting of the [x,y] and {x,y} markers.
  state.py       Immutable per-character occurrence counts.
  encoder.py     Plaintext → Pokémon names.
  decoder.py     Pokémon names → plaintext (fork/merge branch engine).
cipher.py        Backwards-compatible re-export shim. Do not add logic here.
app.py           FastAPI app: POST /api/encode, POST /api/decode, and
                 GET /api/names (the decoder's vocabulary, for the frontend's
                 decode gate). The only HTTP surface; Vercel finds it by
                 filename.
next-app/        Next.js 16 + React 19 + Tailwind v4 + shadcn/ui frontend.
  lib/pokecipher-api.ts  The only place the frontend talks to Python.
  lib/markers.ts         Parses [x,y] / {x,y} / <?...> for colour-coding.
  lib/utils.ts           cn() class-name helper (shadcn convention).
  components/ui/         shadcn primitives.
  components.json        shadcn config; `npx shadcn add <name>` adds primitives.
tests            Live at the repository root as test_*.py files.
```

## Branch and workflow

- Default and protected branch: `main`.
- Branch from `main` using `<type>/<short-slug>` (for example `fix/decoder-merge`).
- Open a pull request into `main`; CI must be green before merge.
- Fill in the pull request template, including the cipher-behaviour checklist.

## Deployment

Deployed on Vercel as **two projects from this one repository**. A single project
cannot host both a Next.js app and a Python backend, so do not try to merge them.
(Vercel's [Services](https://vercel.com/docs/services) feature is the sanctioned
way to combine them if that is ever worth revisiting.)

1. **API** — root directory `.` (the repository root). `vercel.json` sets
   `framework: "fastapi"`, and Vercel deploys `app.py` as a single Function.
2. **Web** — root directory `next-app`. `next-app/vercel.json` pins
   `framework: "nextjs"`. That file is not optional: the repository-root
   `vercel.json` reaches this project too, so without it the web build inherits
   `framework: "fastapi"` and fails with `FASTAPI_ENTRYPOINT_NOT_FOUND`.

Both deploy on push to `main`. Every pull request gets a preview URL.

### Domains, and a live trap

| Domain | Serves | Vercel project |
|---|---|---|
| `poke-cipher.vercel.app` | the Next.js app | `poke-cipher` (root dir `next-app`) |
| `poke-cipher-api.vercel.app` | the FastAPI backend | `poke-cipher-api` (root dir `.`) |

The names were swapped on 2026-08-30: the good name had been on the API, and the
app was on `next-app-blue-nine.vercel.app`. Note `next-app.vercel.app` belongs to
**someone else** — it resolves, it is not ours, and it must never be used.

**Both `.vercel.app` names are pinned deployment aliases, not project domains.**
They do **not** follow production deploys. After every merge to `main` the alias
must be re-pointed by hand or the domain silently serves the previous build:

```bash
npx vercel alias set <new-production-deployment-url> poke-cipher.vercel.app
npx vercel alias set <new-production-deployment-url> poke-cipher-api.vercel.app
```

This has already caused a false "the fix didn't deploy" report. The real fix is
in the dashboard — Settings → Domains, release the name from the project that
still owns it and add it to the right one — because the CLI cannot: `vercel
domains rm` answers `Domain not found`, and `vercel domains add` answers
`alias_conflict`. Until that is done, treat re-aliasing as part of deploying.

Two further facts worth not rediscovering: `vercel project resume` refuses to run
non-interactively and must be typed by a human; and both projects report
`live: false` yet serve production normally, so that flag is not the thing to
chase when a domain 404s — a missing production deployment is.

**Do not reintroduce an `api/` directory of `.py` files.** Vercel's file-based
Python functions are now limited to projects created before that path was
retired — the docs say so in as many words: "Vercel supports *existing* projects
that define file-based Python functions in an `/api` directory." A project
created today fails in `vercel build`, seconds after clone and before
dependencies install, with `The pattern "api/**/*.py" ... doesn't match any
Serverless Functions`. That is not a configuration problem and no `vercel.json`
key fixes it. FastAPI at a supported entrypoint is the replacement.

## Commands

Run from the repository root unless noted.

```bash
python -m pytest                      # full suite
python -m pytest -q path/to/test.py   # a single test file
python -m ruff check .                # lint
python -m ruff format .               # format
python -m ruff format --check .       # format check only
python -m pytest --cov --cov-report=html:coverage/   # coverage into coverage/
```

Frontend, from `next-app/`:

```bash
npm ci
npm run dev
npm run test            # vitest unit tests
npm run test:coverage   # with coverage into next-app/coverage/
npm run lint
npm run typecheck
npm run build
```

Coverage output goes to `coverage/`, which is gitignored. Never commit it.

Invoke tools as `python -m ruff` and `python -m pytest`; the bare executables are
not on PATH in this environment.

## Architecture rules

- **No godfiles.** Each module owns one concern. If a file needs a second banner
  comment to describe another responsibility, split it.
- **Single source of truth.** Token spellings live only in `tokens.py`; marker
  formatting only in `markers.py`; Pokédex data only in `pokedex.py`. Never
  spell a token or marker literally anywhere else.
- **Fail fast.** Validate data and inputs at the boundary. `pokedex.py`
  validates the Pokédex at import time and raises `PokedexError` on bad data,
  which is why the encoder can index regional lists without bounds checks. Do
  not add defensive branches for states that cannot occur.
- **Law of Demeter.** Ask objects questions; do not reach through them. Use
  `state.count_of(c)` and `state.region_index(c, n)`, never `state._counts`.
- **Immutability for state.** `CharCounts` and `Branch` are immutable;
  `advanced()` returns new objects. Never mutate shared cipher state.
- **Keep the shim thin.** `cipher.py` re-exports and nothing more.
- Prefer standard library only. Justify any new runtime dependency.

## Patterns and invariants

- **Produce strictly, consume tolerantly.** The encoder cannot emit `[err:...]`
  tokens — every index it can produce lies inside the validated Pokédex — yet the
  decoder still recognises them, so legacy ciphertext is reported clearly instead
  of being mistaken for an unknown Pokémon. That asymmetry is deliberate; do not
  "clean it up" by deleting either half.
- **The two legacy test files pin exact shapes, not just behaviour.**
  `region_names` is a `list` (not a tuple), `name_to_mappings[name]` is a
  `list[tuple[str, int]]`, and `decode_flexible_error_reporting` is compared with
  `assertIs`, so re-exporting it is not enough — it must alias the same object.
  Check these before changing any public name, type, or constant.
- **Cross-region duplicate names are the feature.** A name may repeat across
  regions — that overlap is what makes decoding ambiguous — but must be unique
  within a single region.
- **Immutability, not defensive copying.** `CharCounts.advanced()` and
  `Branch.advanced()` / `skipped()` return new objects rather than mutating, so
  forked hypotheses can never alias each other's state.
- **Assert invariants where the language allows it.** `zip(..., strict=True)`
  encodes "these sequences always align" instead of silently truncating.
- **Emit as soon as it is final.** The decoder flushes pending positions the
  moment a single branch survives, because a lone branch's history is the common
  prefix of every possible future. Dropping that history is what keeps decoding
  near-linear; removing the collapse step silently restores quadratic cost.
- **Cap limits at the transport, not in the core.** Decode cost rises when an
  ambiguity survives an entire message, so `app.MAX_TEXT_CHARS` bounds input.
  Keep the cipher functions total and unbounded; enforce policy at the boundary.
- **Ciphertext is a compatibility surface.** Changing the Pokédex lists or the
  algorithm invalidates every message ever encoded.

### Gotchas

- `# fmt: off` / `# fmt: on` in `pokedex.py` must sit at column 0, outside the
  dict literal. Ruff ignores them when nested inside the braces and will explode
  the 285-entry tables to one item per line.
- Long-running commands make PowerShell output capture unreliable. Redirect to a
  file and read that instead; run `Stop-Process -Name python` if orphaned runs
  leave the shell unresponsive.

## Testing rules

- Tests are `unittest`-style classes at the repository root, named `test_*.py`,
  and are collected by pytest.
- Write docstrings as declarative sentences: "Encoding an empty string returns an
  empty string." — not "for testing…".
- Every new cipher behaviour needs a test. Every bug fix needs a regression test.
- `test_cipher.py` and `test_cipher_pyramidal.py` encode the historical public
  contract. Treat a failure in them as a real regression unless you can prove
  the change is intentional and agreed.
- Changing the Pokédex lists or the algorithm invalidates all previously
  generated ciphertext. Call that out explicitly in the pull request.
- Frontend unit tests are Vitest files co-located with the code they cover
  (`lib/markers.test.ts`). They run in the `node` environment because the code
  under test is pure; component tests need `jsdom` and `@testing-library/react`
  added first. CI runs `npm run test` before lint, typecheck and build.

## Style rules

- Python 3.10+ syntax, fully type-annotated, docstrings on public functions.
- Line length 100; `ruff format` is the formatter of record.
- Keep the Pokédex tables between the `# fmt: off` / `# fmt: on` markers so the
  compact six-per-row layout survives formatting.
- TypeScript: strict mode, functional components, `camelCase` variables,
  `PascalCase` components. `npm run lint` and `npm run typecheck` must pass.
- **The frontend never re-implements the cipher.** All encode/decode goes through
  `lib/pokecipher-api.ts`. Adding cipher logic to TypeScript duplicates the
  single source of truth and will drift.
- Sprites come from the PokémonDB CDN keyed by name (see `components/pokemon-token.tsx`),
  and fall back to the name when a slug is unknown. Do not hardcode national dex
  numbers: the cipher works in *regional* dex names, where one name can mean
  different characters in different regions.
- Retro Game Boy palette for the UI: dark greens, off-white, hard edges, pixel
  type. No rounded corners, no soft gradients.
- Pokémon output toggles between sprites and names; both views must stay in sync.

## Do not

- Do not commit secrets, keys, `.env` files, or absolute local paths.
- Do not commit `coverage/`, `.next/`, `node_modules/`, or `.vercel/`.
- Do not add `print` calls at import time; use `logging` if a library must emit.
- Do not silently swallow exceptions in the cipher core.
- Do not change encode/decode output as a side effect of a refactor.
