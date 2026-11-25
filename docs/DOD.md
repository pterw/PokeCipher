# Definition of Done — product-quality and correctness pass

> The contract for this pass. A task is done when every gate below is met and the
> evidence for it is recorded in `LEDGER.md`. `AGENTS.md` remains authoritative;
> where this file and `AGENTS.md` disagree, follow `AGENTS.md` and say so.

## Ground rules

- **Evidence, not memory.** A gate is met only when a command run *in this
  session* shows it. Notes from earlier sessions are hints to re-verify, never
  proof.
- **Preserve behaviour by default.** Ciphertext is a compatibility surface. A
  change to encode/decode output needs a proven defect and an explicit note in
  the ledger.
- **Atomic commits.** One concern per commit, message prefixed by type
  (`docs:`, `fix(web):`, `test:` …). No commit that mixes a doc change with a
  behaviour change.
- **No push without explicit approval.** Commit locally; pushing and re-aliasing
  the Vercel domains are separate, human-approved steps.
- **Report honestly.** A failing gate is reported as failing.

## Gates

### 1. Cipher correctness

- [ ] `encode_message` / `decode_message` behave as documented in `AGENTS.md`
      and `readme.md`, verified by running the code, not by reading it.
- [ ] Every factual claim the UI or README hardcodes about cipher output is
      checked against the real encoder (hero transcript, README examples,
      name counts, region sizes).
- [ ] Known limitations stay documented as limitations. The
      `MAX_DECODE_BRANCHES` truncation and the bracket-vs-marker collision are
      pinned by tests, not silently "fixed".

### 2. Real end-to-end validation

- [ ] The API contract is exercised through `TestClient`, not by inspection:
      `POST /api/encode`, `POST /api/decode`, `GET /api/names`, plus the 400 /
      413 rejection paths.
- [ ] A round trip is observed through the HTTP surface, not just the library.

### 3. Backend checks

- [ ] `python -m pytest` — full suite green.
- [ ] `python -m ruff check .` — clean.
- [ ] `python -m ruff format --check .` — clean.

### 4. Frontend checks (from `next-app/`)

- [ ] `npm run test` — vitest green.
- [ ] `npm run lint` — clean.
- [ ] `npm run typecheck` — clean.
- [ ] `npm run build` — succeeds.

### 5. Regression safety

- [ ] Every behaviour change ships with a failing-first regression test.
- [ ] `test_cipher.py` and `test_cipher_pyramidal.py` still pass untouched; a
      failure there is treated as a real regression.
- [ ] Historical shapes stay pinned: `region_names` is a `list`,
      `name_to_mappings[name]` is a `list[tuple[str, int]]`, and
      `decode_flexible_error_reporting` is the *same object* as
      `decode_message`.

### 6. Product quality

- [ ] A control that presents itself as unavailable does not perform its action.
- [ ] All errors are handled gracefully (firm `PRODUCT.md` requirement).
- [ ] Ambiguity markers are surfaced and explained, never styled as failures.
- [ ] Nothing implies security. No lock iconography, no "encrypt your secrets".
- [ ] The frontend never re-implements the cipher.

### 7. Hygiene

- [ ] No scratch or probe files committed; `coverage/`, `.next/`,
      `node_modules/`, `.vercel/` stay out.
- [ ] No secrets, `.env` files, or absolute local paths committed.
- [ ] Every fix and every deliberate non-fix is recorded in `LEDGER.md` with
      the reasoning and the evidence.
