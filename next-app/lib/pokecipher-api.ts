/**
 * Client for the PokéCipher Python serverless functions.
 *
 * The cipher lives in Python only. This module is the single place the frontend
 * talks to it, so the algorithm and Pokédex data are never re-implemented here.
 */

const DEFAULT_MAX_CHARS = 4_000

/** Where the Python API is deployed. Same-origin by default in production. */
const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? ""

/** Mirrors api_support.MAX_TEXT_CHARS. */
export const MAX_TEXT_CHARS =
  Number(process.env.NEXT_PUBLIC_MAX_TEXT_CHARS) || DEFAULT_MAX_CHARS

export class PokeCipherError extends Error {}

async function call(endpoint: "encode" | "decode", text: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  })

  let payload: unknown = null
  try {
    payload = await response.json()
  } catch {
    throw new PokeCipherError("The server returned a malformed response.")
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
  return result
}

/** Encode plaintext into a space-separated sequence of Pokémon names. */
export function encodeText(text: string): Promise<string> {
  return call("encode", text)
}

/** Decode a Pokémon-name sequence back into plaintext. */
export function decodeText(text: string): Promise<string> {
  return call("decode", text)
}

/** True when the text is within the API's input limit. */
export function isWithinLimit(text: string): boolean {
  return text.length <= MAX_TEXT_CHARS
}
