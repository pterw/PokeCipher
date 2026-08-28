import { describe, expect, it } from "vitest"

import { hasAmbiguity, splitMarkers, type Piece } from "./markers"

/** Convenience: collect only the non-text pieces. */
function markersOf(text: string): Piece[] {
  return splitMarkers(text).filter((piece) => piece.kind !== "text")
}

describe("splitMarkers", () => {
  it("returns a single plain-text run when there are no markers", () => {
    expect(splitMarkers("Hello")).toEqual([{ kind: "text", text: "Hello" }])
  })

  it("returns no pieces for the empty string", () => {
    expect(splitMarkers("")).toEqual([])
  })

  it("classifies a bracketed ambiguity marker", () => {
    expect(splitMarkers("W[n,o]rld!")).toEqual([
      { kind: "text", text: "W" },
      { kind: "ambiguous", text: "[n,o]" },
      { kind: "text", text: "rld!" },
    ])
  })

  it("classifies a braced state-mismatch marker", () => {
    expect(splitMarkers("a{n,R}b")).toEqual([
      { kind: "text", text: "a" },
      { kind: "mismatch", text: "{n,R}" },
      { kind: "text", text: "b" },
    ])
  })

  it("keeps ambiguity and mismatch distinct", () => {
    const ambiguous = markersOf("[n,o]")[0]
    const mismatch = markersOf("{n,o}")[0]
    expect(ambiguous.kind).toBe("ambiguous")
    expect(mismatch.kind).toBe("mismatch")
  })

  it("classifies an unknown-Pokemon marker", () => {
    expect(splitMarkers("H<?unknown: FakeMon>l")).toEqual([
      { kind: "text", text: "H" },
      { kind: "unknown", text: "<?unknown: FakeMon>" },
      { kind: "text", text: "l" },
    ])
  })

  it("classifies a legacy error-encoding marker", () => {
    const pieces = markersOf("<?error encoding: [err:idx_99_region_Kanto]>")
    expect(pieces).toEqual([
      { kind: "unknown", text: "<?error encoding: [err:idx_99_region_Kanto]>" },
    ])
  })

  it("handles a three-way ambiguity", () => {
    expect(markersOf("[A,i,X]")).toEqual([{ kind: "ambiguous", text: "[A,i,X]" }])
  })

  it("parses several markers in one string", () => {
    const pieces = splitMarkers("a[n,o]b{x,y}c<?unknown: Z>d")
    expect(pieces.map((piece) => piece.kind)).toEqual([
      "text",
      "ambiguous",
      "text",
      "mismatch",
      "text",
      "unknown",
      "text",
    ])
  })

  it("handles a marker at the very start and very end", () => {
    expect(splitMarkers("[n,o]")).toEqual([{ kind: "ambiguous", text: "[n,o]" }])
    expect(splitMarkers("hi[n,o]")).toEqual([
      { kind: "text", text: "hi" },
      { kind: "ambiguous", text: "[n,o]" },
    ])
    expect(splitMarkers("[n,o]hi")).toEqual([
      { kind: "ambiguous", text: "[n,o]" },
      { kind: "text", text: "hi" },
    ])
  })

  it("handles adjacent markers with no text between them", () => {
    expect(markersOf("[n,o]{x,y}")).toEqual([
      { kind: "ambiguous", text: "[n,o]" },
      { kind: "mismatch", text: "{x,y}" },
    ])
  })

  it("never loses characters: pieces rejoin to the original text", () => {
    for (const text of [
      "Hello W[n,o]rld!",
      "a{n,R}b",
      "H<?unknown: FakeMon>l",
      "[n,o]{x,y}<?unknown: Z>",
      "plain text with no markers at all",
      "",
    ]) {
      expect(splitMarkers(text).map((piece) => piece.text).join("")).toBe(text)
    }
  })

  it("preserves text containing newlines and tabs", () => {
    const text = "line1\nline2\tend"
    expect(splitMarkers(text)).toEqual([{ kind: "text", text }])
  })

  it("treats brackets containing whitespace as plain text", () => {
    // Guards against highlighting prose like "see [note to self]".
    expect(markersOf("see [note to self]")).toEqual([])
  })

  it("documents the known limitation: literal brackets are read as markers", () => {
    // This is the documented trade-off, asserted so a fix changes it deliberately.
    expect(markersOf("array[0]")).toEqual([{ kind: "ambiguous", text: "[0]" }])
  })
})

describe("hasAmbiguity", () => {
  it("is false for clean text", () => {
    expect(hasAmbiguity("Hello")).toBe(false)
  })

  it("is true when an ambiguity marker is present", () => {
    expect(hasAmbiguity("Hello W[n,o]rld!")).toBe(true)
  })

  it("is true for a mismatch or unknown marker", () => {
    expect(hasAmbiguity("a{n,R}b")).toBe(true)
    expect(hasAmbiguity("<?unknown: FakeMon>")).toBe(true)
  })
})
