"""FastAPI entrypoint for the PokéCipher HTTP API.

Vercel resolves this module by filename: a ``FastAPI`` instance named ``app`` in
``app.py`` at the repository root is a supported zero-config entrypoint, and the
whole application ships as a single Vercel Function.

This replaces the previous file-based ``api/encode.py`` and ``api/decode.py``
handlers. Vercel now grants that path only to projects created before it was
retired ("Vercel supports existing projects that define file-based Python
functions in an ``/api`` directory"), so a project created today can never build
against it: the deployment fails during ``vercel build``, one second after clone
and before dependencies are installed, with

    The pattern "api/**/*.py" defined in `functions` doesn't match any
    Serverless Functions inside the `api` directory.

See https://vercel.com/docs/functions/runtimes/python/api-directory.

The wire contract is deliberately unchanged, because next-app/lib/pokecipher-api.ts
and its vitest suite depend on it exactly:

    POST /api/encode  {"text": "..."}  -> 200 {"result": "..."}
    POST /api/decode  {"text": "..."}  -> 200 {"result": "..."}
    any failure                        -> {"error": "..."} with 400 or 413

That last line is why the body is parsed by hand rather than through a Pydantic
model: FastAPI's own validation failures are 422 with a ``detail`` array, and the
frontend reads ``error``.

Run it locally on the port next.config.ts proxies to::

    uvicorn app:app --port 8000
"""

from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from pokecipher import NAME_INDEX, decode_report, encode_message

MAX_BODY_BYTES = 32 * 1024

# Two costs matter. Decoding keeps every live hypothesis, which reaches ~5,200
# for 500 chars of prose, so MAX_DECODE_BRANCHES bounds a step - that bound is
# what makes the timing below linear, and it is also why a long decode can be
# wrong (see decode_report). With the budget applied, ~1.2 s for 10,000 chars of
# prose on CPython 3.13. Text that sustains an unresolved ambiguity throughout
# cannot collapse and stays quadratic (~3.3 s at 4,100 chars, ~13 s at 8,000).
# Capping here keeps the pathological case inside the function's maxDuration
# instead of turning a huge paste into a timeout.
MAX_TEXT_CHARS = 4_000

# docs_url/redoc_url/openapi_url are off so the deployed surface stays exactly the
# two POST routes the previous handlers exposed. Enabling them is a one-line
# change if the interactive docs are ever wanted as a portfolio artefact.
app = FastAPI(
    title="PokéCipher API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# The browser calls this API directly whenever NEXT_PUBLIC_API_URL is set, because
# lib/pokecipher-api.ts builds an absolute URL from it and so bypasses the Next
# rewrite. In that split deployment the request is genuinely cross-origin, so the
# headers are load-bearing. This mirrors the "*" allow-origin that the old
# api_support.send_json put on every response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Render every HTTP error as ``{"error": ...}``, the shape the frontend reads.

    Registered against Starlette's exception rather than FastAPI's subclass so it
    also covers the framework's own 404 and 405 responses, which would otherwise
    come back as ``{"detail": ...}`` and read as a malformed response client-side.
    """
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


def decode_surrogate_pairs(text: str) -> str:
    """Join UTF-16 surrogate pairs and reject the unpaired ones.

    JSON permits astral characters to be written as two escapes
    (``"\\ud83d\\ude00"``), and ``json.loads`` keeps them as two lone surrogates
    rather than one character. Re-encoding through UTF-16 puts the pair back
    together, so a client that escapes properly is served correctly.

    A genuinely unpaired surrogate cannot be encoded as UTF-8, so no response
    could ever carry it back: the round trip through UTF-16 fails and the caller
    sees a 400 instead of a 500 raised while serialising the reply.
    """
    try:
        return text.encode("utf-16", "surrogatepass").decode("utf-16")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Field 'text' contains an unpaired surrogate and is not valid Unicode text.",
        ) from exc


async def read_text(request: Request) -> str:
    """Return the validated ``text`` field, or raise the matching HTTP error."""
    raw = await request.body()
    if not 0 < len(raw) <= MAX_BODY_BYTES:
        raise HTTPException(status_code=400, detail="Expected a JSON object body under 32 KiB.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=400, detail="Expected a JSON object body under 32 KiB."
        ) from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Expected a JSON object body under 32 KiB.")

    text = payload.get("text")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Field 'text' must be a string.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=413, detail=f"Field 'text' exceeds {MAX_TEXT_CHARS} characters."
        )
    return decode_surrogate_pairs(text)


@app.get("/api/names")
async def names() -> JSONResponse:
    """Every Pokémon name the decoder accepts, for client-side input validation.

    The frontend gates its decode control on whether the input actually looks like
    ciphertext, which it cannot judge without the name set. Serving that set from
    the live Pokédex keeps Python the single source of truth: the list is derived
    here, never copied into TypeScript, so changing the dex reaches the UI without
    a second edit.

    Cached for an hour. The payload is ~1.8 KB and only changes when the Pokédex
    does, which is a deploy.
    """
    return JSONResponse(
        {"names": sorted(NAME_INDEX)},
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.post("/api/encode")
async def encode(request: Request) -> dict[str, str]:
    """Encode plaintext into a space-separated sequence of Pokémon names."""
    text = await read_text(request)
    # The cipher is synchronous and CPU-bound, and a worst-case decode runs for
    # seconds. Fluid compute multiplexes concurrent requests onto one instance, so
    # running it inline would block the event loop for every other caller.
    return {"result": await run_in_threadpool(encode_message, text)}


@app.post("/api/decode")
async def decode(request: Request) -> JSONResponse:
    """Decode a sequence of Pokémon names back into plaintext.

    ``truncated`` is added only when the decoder exceeded its branch budget, so
    the response for every message that fits stays byte-identical to the
    documented contract. When it is present, the text is best-effort: the
    decoder dropped hypotheses, and a plain character may be wrong even though
    nothing in the text says so. The frontend surfaces it as a warning.
    """
    text = await read_text(request)
    report = await run_in_threadpool(decode_report, text)
    payload: dict[str, object] = {"result": report.text}
    if report.truncated:
        payload["truncated"] = True
    return JSONResponse(payload)
