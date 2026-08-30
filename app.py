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

from pokecipher import decode_message, encode_message

MAX_BODY_BYTES = 32 * 1024

# The decoder emits positions as soon as they are final, so cost is close to
# linear: ~1.2 s for 10,000 chars of prose on CPython 3.13. Text that sustains an
# unresolved ambiguity throughout cannot collapse and stays quadratic (~3.3 s at
# 4,100 chars, and ~13 s at 8,000). Capping here keeps the pathological case
# inside the function's maxDuration instead of turning a huge paste into a
# timeout.
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
    allow_methods=["POST", "OPTIONS"],
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
    return text


@app.post("/api/encode")
async def encode(request: Request) -> dict[str, str]:
    """Encode plaintext into a space-separated sequence of Pokémon names."""
    text = await read_text(request)
    # The cipher is synchronous and CPU-bound, and a worst-case decode runs for
    # seconds. Fluid compute multiplexes concurrent requests onto one instance, so
    # running it inline would block the event loop for every other caller.
    return {"result": await run_in_threadpool(encode_message, text)}


@app.post("/api/decode")
async def decode(request: Request) -> dict[str, str]:
    """Decode a sequence of Pokémon names back into plaintext."""
    text = await read_text(request)
    return {"result": await run_in_threadpool(decode_message, text)}
