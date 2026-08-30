"use client"

import { useEffect, useState } from "react"

import { CliHero } from "@/components/cli-hero"
import { PokemonToken } from "@/components/pokemon-token"
import { BitButton } from "@/components/ui/8bit/button"
import { BitCard } from "@/components/ui/8bit/card"
import { BitCheckbox } from "@/components/ui/8bit/checkbox"
import { BitTextarea } from "@/components/ui/8bit/textarea"
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
      .catch((err) => {
        console.error("Failed to fetch Pokedex names for decode gate:", err)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const canDecode = looksLikeCiphertext(input, knownNames)
  const recognised = canDecode ? countKnownNames(input, knownNames) : 0
  const hasInput = input.trim().length > 0
  const tooLong = !isWithinLimit(input)

  async function run(targetMode: Mode) {
    if (!hasInput) {
      setError("Type something first.")
      return
    }
    if (tooLong) {
      setError(`Text is limited to ${MAX_TEXT_CHARS} characters.`)
      return
    }
    if (busy) return
    setError(null)
    setBusy(true)
    try {
      if (targetMode === "encode") {
        const text = await encodeText(input)
        setResult(text)
        setMode("encode")
      } else {
        const text = await decodeText(input)
        setResult(text)
        setMode("decode")
      }
    } catch (err) {
      if (err instanceof PokeCipherError) {
        setError(err.message)
      } else {
        setError("Could not reach the cipher service.")
      }
    } finally {
      setBusy(false)
    }
  }

  function clearAll() {
    setInput("")
    setResult("")
    setError(null)
  }

  function swap() {
    if (!result) return
    setInput(result)
    setResult("")
    setMode(mode === "encode" ? "decode" : "encode")
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
      <main className="mx-auto flex w-full max-w-4xl flex-col gap-3 px-6 pt-0 pb-10">
        <header>
          <h2 className="font-pixel text-lg text-foreground sm:text-xl">Encode &amp; Decode</h2>
          <p className="mt-0.5 text-base text-foreground sm:text-lg">
            Each repeated character cycles through the Kanto, Johto and Hoenn dexes.
          </p>
        </header>

        <section className="flex flex-col gap-1.5">
          <label htmlFor="input" className="text-sm uppercase tracking-wide text-foreground">
            Input
          </label>
          <BitTextarea
            id="input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            spellCheck={false}
            placeholder="Type a message, or paste Pokemon names to decode."
          />
          <div className="flex items-center justify-between text-sm">
            <span className={tooLong ? "text-marker-mismatch" : "text-foreground"}>
              {input.length} / {MAX_TEXT_CHARS}
            </span>
            <label
              htmlFor="show-sprites"
              className="flex cursor-pointer items-center gap-2 text-foreground select-none font-terminal text-lg"
            >
              <BitCheckbox
                id="show-sprites"
                checked={showSprites}
                onChange={(event) => setShowSprites(event.target.checked)}
              />
              <span>Show sprites</span>
            </label>
          </div>
        </section>

        <section className="flex flex-wrap items-center gap-3">
          <BitButton
            variant="yellow"
            onClick={() => run("encode")}
            disabled={busy}
          >
            {busy ? "Working..." : "Encode to Pokemon"}
          </BitButton>
          {/*
            aria-disabled rather than disabled: the control keeps its place in the
            tab order and stays announced, so a keyboard or screen-reader user can
            find it and read why it is unavailable, instead of it silently
            vanishing from the page.
          */}
          <BitButton
            variant="secondary"
            onClick={() => canDecode && run("decode")}
            aria-disabled={!canDecode || busy}
            className={cn(!canDecode && "cursor-not-allowed opacity-40")}
          >
            Decode to text
          </BitButton>
          <BitButton variant="outline" onClick={swap} disabled={!result}>
            Swap
          </BitButton>
          <BitButton variant="outline" onClick={copy} disabled={!result}>
            Copy
          </BitButton>
          <BitButton variant="ghost" onClick={clearAll}>
            Clear
          </BitButton>
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
            <BitCard className="min-h-24 p-4 font-mono text-lg text-card-foreground">
              {mode === "encode" ? (
                showSprites ? (
                  <div className="flex flex-wrap items-center gap-2">
                    {result.split(" ").map((name, index) => (
                      <PokemonToken key={index} name={name} showSprites={true} />
                    ))}
                  </div>
                ) : (
                  <p className="leading-relaxed text-foreground select-all break-words">
                    {result}
                  </p>
                )
              ) : (
                <div className="leading-relaxed select-all break-words">
                  {splitMarkers(result).map((piece, index) => (
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
              )}
            </BitCard>
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
