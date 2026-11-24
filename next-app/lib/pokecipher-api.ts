/**
 * Client for the PokéCipher Python serverless functions.
 *
 * The cipher lives in Python only. This module is the single place the frontend
 * talks to it, so the algorithm and Pokédex data are never re-implemented here.
 */

const DEFAULT_MAX_CHARS = 4_000

/** Where the Python API is deployed. Same-origin by default in production. */
const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? ""

/** Mirrors app.MAX_TEXT_CHARS. */
export const MAX_TEXT_CHARS =
  Number(process.env.NEXT_PUBLIC_MAX_TEXT_CHARS) || DEFAULT_MAX_CHARS

export class PokeCipherError extends Error {}

/** A decode, plus the one thing the decoded string cannot say for itself. */
export interface DecodeResult {
  text: string
  /**
   * True when the decoder exceeded its branch budget and dropped hypotheses, so
   * `text` is best-effort: a plain character in it may be wrong. Only ever set
   * by the server; absent means the decode was exact (modulo `[x,y]` markers,
   * which are the cipher working as designed).
   */
  truncated: boolean
}

interface Payload {
  result: string
  truncated: boolean
}

async function call(endpoint: "encode" | "decode", text: string): Promise<Payload> {
  const response = await fetch(`${API_BASE}/api/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  })

  let payload: unknown = null
  try {
    payload = await response.json()
  } catch {
    throw new PokeCipherError(
      `Could not reach the cipher service (HTTP ${response.status}). Is the API running?`,
    )
  }

  if (!response.ok) {
    const message =
      payload && typeof payload === "object" && "error" in payload
        ? String((payload as { error: unknown }).error)
        : `Request failed with status ${response.status}.`
    throw new PokeCipherError(message)
  }

  const result = (payload as { result?: unknown })?.result
  if (typeof result !== "string") {
    throw new PokeCipherError("The server returned a malformed response.")
  }
  // Absent is the normal case: the API only sends the flag when the budget was
  // exceeded, which keeps every in-budget response byte-identical.
  const truncated = (payload as { truncated?: unknown }).truncated === true
  return { result, truncated }
}

/**
 * Fetch every Pokémon name the decoder accepts, case-folded for lookup.
 *
 * The decode control is gated on whether the input actually looks like
 * ciphertext, which cannot be judged without this set. It is fetched rather than
 * hardcoded so Python stays the single source of truth: the list is derived from
 * the live Pokédex, so adding a region reaches the UI with no TypeScript edit.
 *
 * Roughly 2 KB, served with a one-hour Cache-Control, fetched once per mount.
 */
export async function fetchKnownNames(): Promise<Set<string>> {
  const response = await fetch(`${API_BASE}/api/names`)
  if (!response.ok) {
    throw new PokeCipherError(`Could not load the Pokemon list (HTTP ${response.status}).`)
  }
  const payload = (await response.json()) as { names?: unknown }
  if (!Array.isArray(payload.names)) {
    throw new PokeCipherError("The server returned a malformed name list.")
  }
  return new Set(payload.names.map((name) => String(name).toLowerCase()))
}

/**
 * True when the input reads as ciphertext rather than plaintext.
 *
 * The test is simply whether the first whitespace-delimited token is a known
 * name. That is live rather than staged: `Zub` is not a name so decoding stays
 * shut, `Zubat` opens it, and `Zubatx` closes it again. No token count is
 * required, because a lone name is legitimate ciphertext — `Zubat` decodes to
 * `H` — and demanding two or three would lock out every short message.
 *
 * Returns false while `known` is empty, i.e. before the list has loaded, so the
 * control stays shut rather than briefly permitting a call that would fail.
 */
export function looksLikeCiphertext(text: string, known: Set<string>): boolean {
  if (known.size === 0) return false
  const [first] = text.trim().split(/\s+/, 1)
  return Boolean(first) && known.has(first.toLowerCase())
}

/** How many whitespace-separated tokens in `text` are known Pokémon names. */
export function countKnownNames(text: string, known: Set<string>): number {
  if (known.size === 0) return 0
  return text.split(/\s+/).filter((token) => token && known.has(token.toLowerCase())).length
}

/** Encode plaintext into a space-separated sequence of Pokémon names. */
export async function encodeText(text: string): Promise<string> {
  const { result } = await call("encode", text)
  return result
}

/** Decode a Pokémon-name sequence back to plaintext, and say if it was best-effort. */
export async function decodeText(text: string): Promise<DecodeResult> {
  const { result, truncated } = await call("decode", text)
  return { text: result, truncated }
}

/** True when the text is within the API's input limit. */
export function isWithinLimit(text: string): boolean {
  return text.length <= MAX_TEXT_CHARS
}
