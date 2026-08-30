"use client"

import { useEffect, useState } from "react"

import { CliHero } from "@/components/cli-hero"
import { PokemonToken } from "@/components/pokemon-token"
import { Button } from "@/components/ui/button"
import { splitMarkers } from "@/lib/markers"
import {
  MAX_TEXT_CHARS,
  PokeCipherError,
  countKnownNames,
  decodeText,
  encodeText,
  fetchKnownNames,
  isWithinLimit,
  looksLikeCiphertext,
} from "@/lib/pokecipher-api"
import { cn } from "@/lib/utils"

type Mode = "encode" | "decode"

const MARKER_CLASS: Record<string, string> = {
  ambiguous: "text-marker-ambiguous",
  mismatch: "text-marker-mismatch",
  unknown: "text-marker-unknown",
}

const MARKER_LEGEND: Record<string, string> = {
  ambiguous: "Amber marks genuine ambiguity: several characters are valid there.",
  mismatch: "Red marks a state mismatch: that token may not belong to this message.",
  unknown: "Blue marks a name the Pokedex does not contain.",
}

export default function Page() {
  const [input, setInput] = useState("")
  const [result, setResult] = useState("")
  const [mode, setMode] = useState<Mode>("encode")
  const [showSprites, setShowSprites] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [knownNames, setKnownNames] = useState<Set<string>>(new Set())

  // The decode gate needs the Pokedex vocabulary, which lives in Python. Fetched
  // once per mount rather than hardcoded, so the dex stays the single source of
  // truth. A failure here only leaves decoding shut; encoding is unaffected.
  useEffect(() => {
    let cancelled = false
    fetchKnownNames()
      .then((names) => {
        if (!cancelled) setKnownNames(names)
      })
      .catch(() => {
        /* Decoding stays gated shut; encode still works. */
      })
    return () => {
      cancelled = true
    }
  }, [])

  const tooLong = !isWithinLimit(input)
  const hasInput = input.trim().length > 0
  // Gate decode, never encode: any text is encodable, but decoding plaintext
  // produces a wall of <?unknown: ...> tokens presented as though it were output.
  // If the control cannot be pressed, that state cannot be reached.
  const canDecode = looksLikeCiphertext(input, knownNames)
  const recognised = canDecode ? countKnownNames(input, knownNames) : 0

  async function run(nextMode: Mode) {
    if (!hasInput) {
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

  // Swapping moves the result into the input, so the gate has to be re-evaluated
  // from the new text. It is derived from `input` on every render, so this needs
  // no explicit recomputation — only the state change below.
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

  const markerKinds = new Set(
    mode === "decode" ? splitMarkers(result).map((piece) => piece.kind) : []
  )

  return (
    <>
      <CliHero />
      <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 pb-16 pt-6">
        <header>
          <h2 className="font-pixel text-lg leading-tight text-foreground">Encode &amp; Decode</h2>
          <p className="mt-2 text-lg text-foreground">
            Each repeated character cycles through the Kanto, Johto and Hoenn dexes.
          </p>
        </header>

        <section className="flex flex-col gap-2">
          <label htmlFor="input" className="text-sm uppercase tracking-wide text-foreground">
            Input
          </label>
          <textarea
            id="input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            rows={6}
            spellCheck={false}
            placeholder="Type a message, or paste Pokemon names to decode."
            className="w-full resize-y border border-border bg-input p-3 font-mono text-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <div className="flex items-center justify-between text-sm">
            <span className={tooLong ? "text-marker-mismatch" : "text-foreground"}>
              {input.length} / {MAX_TEXT_CHARS}
            </span>
            <label className="flex items-center gap-2 text-foreground">
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
          {/*
            aria-disabled rather than disabled: the control keeps its place in the
            tab order and stays announced, so a keyboard or screen-reader user can
            find it and read why it is unavailable, instead of it silently
            vanishing from the page.
          */}
          <Button
            variant="secondary"
            onClick={() => canDecode && run("decode")}
            aria-disabled={!canDecode || busy}
            className={cn(!canDecode && "cursor-not-allowed opacity-40")}
          >
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

        {/*
          Persistent status, not a hover tooltip: it explains why decoding is shut
          without waiting for the user to go looking for an explanation.
        */}
        <p className="text-sm text-foreground" aria-live="polite">
          {!hasInput
            ? "Type text to encode, or paste Pokemon names to decode."
            : canDecode
              ? `${recognised} Pokemon ${recognised === 1 ? "name" : "names"} recognised.`
              : "Not Pokemon names, so decoding is off. Encode instead."}
        </p>

        {error ? (
          <p
            role="alert"
            className="border border-marker-mismatch p-3 text-lg text-marker-mismatch"
          >
            {error}
          </p>
        ) : null}

        {result ? (
          <section className="flex flex-col gap-2" aria-live="polite">
            <h2 className="text-sm uppercase tracking-wide text-foreground">
              {mode === "encode" ? "Pokemon" : "Decoded text"}
            </h2>
            <div className="min-h-24 border border-border bg-card p-3 font-mono text-lg leading-8 text-card-foreground">
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
                      className={cn(
                        piece.kind !== "text" && "font-semibold",
                        MARKER_CLASS[piece.kind]
                      )}
                    >
                      {piece.text}
                    </span>
                  ))}
            </div>
            {/*
              Only describe markers actually on screen. The old fixed legend named
              amber and red even when every marker was blue, so the one piece of
              guidance shown could contradict the output it was explaining.
            */}
            {mode === "decode" &&
              [...markerKinds]
                .filter((kind) => kind in MARKER_LEGEND)
                .map((kind) => (
                  <p key={kind} className="text-sm text-foreground">
                    {MARKER_LEGEND[kind]}
                  </p>
                ))}
          </section>
        ) : null}
      </main>
    </>
  )
}
