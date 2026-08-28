## Summary

<!-- What does this PR change, and why? One or two sentences. -->

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor (no behaviour change)
- [ ] Documentation
- [ ] Build / CI / tooling

## How was this tested?

<!-- Commands run, cases covered. Delete what does not apply. -->

- [ ] `python -m pytest`
- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `cd next-app && npm run lint && npm run typecheck && npm run build`
- [ ] Verified in a Vercel preview deployment

## Cipher behaviour

<!-- Only if encode/decode behaviour or the Pokédex data changed. -->

- [ ] No change to encode/decode output for existing inputs
- [ ] Output changed deliberately; all affected tests updated, and the reason is below

<!-- Explain any intentional output change, before → after. -->

## Checklist

- [ ] Each module has a single responsibility; no new godfiles
- [ ] New logic is covered by tests
- [ ] Public functions have docstrings and type hints
- [ ] No secrets, keys, or local paths committed
- [ ] `AGENTS.md` was read and followed
