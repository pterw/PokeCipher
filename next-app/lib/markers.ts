/**
 * Split decoded text into plain runs and the decoder's marker runs, so the UI
 * can colour-code them. Mirrors the notation emitted by pokecipher.markers.
 *
 * Marker shapes:
 *   [n,o]            ambiguity      — several characters remain valid
 *   {n,R}            mismatch       — no branch could consume the token
 *   <?unknown: X>    unknown token
 *   <?error encoding: X>  legacy [err:...] token
 *
 * Known limitation: a message that contains literal square or curly brackets
 * decodes to text that is indistinguishable from a marker, so such brackets are
 * highlighted as markers. Resolving that would require escaping the notation in
 * the decoder output, which would change the decode contract.
 */

export type MarkerKind = "ambiguous" | "mismatch" | "unknown"

export type Piece =
  | { kind: "text"; text: string }
  | { kind: MarkerKind; text: string }

const MARKER_PATTERN = /\[([^[\]\s]+)\]|\{([^{}\s]+)\}|<\?([^>]*)>/g

/** Split decoded text into plain and marker pieces, preserving order. */
export function splitMarkers(text: string): Piece[] {
  const pieces: Piece[] = []
  let cursor = 0

  for (const match of text.matchAll(MARKER_PATTERN)) {
    const start = match.index ?? 0
    if (start > cursor) {
      pieces.push({ kind: "text", text: text.slice(cursor, start) })
    }

    // The third capture group is the <?...> form; it is the fallback branch.
    const [whole, ambiguous, mismatch] = match
    if (ambiguous !== undefined) {
      pieces.push({ kind: "ambiguous", text: whole })
    } else if (mismatch !== undefined) {
      pieces.push({ kind: "mismatch", text: whole })
    } else {
      pieces.push({ kind: "unknown", text: whole })
    }
    cursor = start + whole.length
  }

  if (cursor < text.length) {
    pieces.push({ kind: "text", text: text.slice(cursor) })
  }
  return pieces
}

/** True when the decoded text still contains an unresolved ambiguity. */
export function hasAmbiguity(text: string): boolean {
  return splitMarkers(text).some((piece) => piece.kind !== "text")
}
