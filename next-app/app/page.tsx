"use client"

import { useState } from "react"

import { PokemonToken } from "@/components/pokemon-token"
import { Button } from "@/components/ui/button"
import { splitMarkers } from "@/lib/markers"
import {
  MAX_TEXT_CHARS,
  PokeCipherError,
  decodeText,
  encodeText,
  isWithinLimit,
} from "@/lib/pokecipher-api"
import { cn } from "@/lib/utils"

type Mode = "encode" | "decode"

const MARKER_CLASS: Record<string, string> = {
  ambiguous: "text-marker-ambiguous",
  mismatch: "text-marker-mismatch",
  unknown: "text-marker-unknown",
}

export default function Page() {
  const [input, setInput] = useState("")
  const [result, setResult] = useState("")
  const [mode, setMode] = useState<Mode>("encode")
  const [showSprites, setShowSprites] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const tooLong = !isWithinLimit(input)

  async function run(nextMode: Mode) {
    if (!input.trim()) {
      setError("Type something first.")
      return
    }
    if (tooLong) {
      setError(`Text is limited to ${MAX_TEXT_CHARS} characters.`)
      return
    }

    setBusy(true)
    setError(null)
    try {
      const output = nextMode === "encode" ? await encodeText(input) : await decodeText(input)
      setMode(nextMode)
      setResult(output)
    } catch (caught) {
      setError(
        caught instanceof PokeCipherError
          ? caught.message
          : "Could not reach the cipher service."
      )
    } finally {
      setBusy(false)
    }
  }

  function swap() {
    if (!result) return
    setInput(result)
    setResult("")
    setMode(mode === "encode" ? "decode" : "encode")
    setError(null)
  }

  function clearAll() {
    setInput("")
    setResult("")
    setError(null)
  }

  async function copy() {
    if (!result) return
    await navigator.clipboard.writeText(result)
  }

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-3xl flex-col gap-6 p-6">
      <header>
        <h1 className="font-pixel text-2xl leading-tight text-primary">PokeCipher</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Turn text into Pokemon names, and Pokemon names back into text. Each repeated
          character cycles through the Kanto, Johto and Hoenn dexes.
        </p>
      </header>

      <section className="flex flex-col gap-2">
        <label htmlFor="input" className="text-xs uppercase tracking-wide text-muted-foreground">
          Input
        </label>
        <textarea
          id="input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={6}
          spellCheck={false}
          placeholder="Type a message, or paste Pokemon names to decode."
          className="w-full resize-y border border-border bg-input p-3 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <div className="flex items-center justify-between text-xs">
          <span className={tooLong ? "text-marker-mismatch" : "text-muted-foreground"}>
            {input.length} / {MAX_TEXT_CHARS}
          </span>
          <label className="flex items-center gap-2 text-muted-foreground">
            <input
              type="checkbox"
              checked={showSprites}
              onChange={(event) => setShowSprites(event.target.checked)}
              className="accent-primary"
            />
            Show sprites
          </label>
        </div>
      </section>

      <section className="flex flex-wrap gap-2">
        <Button onClick={() => run("encode")} disabled={busy}>
          {busy ? "Working..." : "Encode to Pokemon"}
        </Button>
        <Button variant="secondary" onClick={() => run("decode")} disabled={busy}>
          Decode to text
        </Button>
        <Button variant="outline" onClick={swap} disabled={!result}>
          Swap
        </Button>
        <Button variant="outline" onClick={copy} disabled={!result}>
          Copy
        </Button>
        <Button variant="ghost" onClick={clearAll}>
          Clear
        </Button>
      </section>

      {error ? (
        <p className="border border-marker-mismatch p-3 text-sm text-marker-mismatch">{error}</p>
      ) : null}

      {result ? (
        <section className="flex flex-col gap-2">
          <h2 className="text-xs uppercase tracking-wide text-muted-foreground">
            {mode === "encode" ? "Pokemon" : "Decoded text"}
          </h2>
          <div className="min-h-24 border border-border bg-card p-3 font-mono text-sm leading-8 text-card-foreground">
            {mode === "encode"
              ? result.split(" ").map((name, index) => (
                  <span key={index}>
                    {index > 0 ? " " : null}
                    <PokemonToken name={name} showSprites={showSprites} />
                  </span>
                ))
              : splitMarkers(result).map((piece, index) => (
                  <span
                    key={index}
                    className={cn(piece.kind !== "text" && "font-semibold", MARKER_CLASS[piece.kind])}
                    title={
                      piece.kind === "ambiguous"
                        ? "Ambiguous: several characters are valid here"
                        : piece.kind === "mismatch"
                          ? "State mismatch: this token may not belong to this message"
                          : undefined
                    }
                  >
                    {piece.text}
                  </span>
                ))}
          </div>
          {mode === "decode" ? (
            <p className="text-xs text-muted-foreground">
              Amber marks genuine ambiguity, red marks a state mismatch.
            </p>
          ) : null}
        </section>
      ) : null}
    </main>
  )
}
