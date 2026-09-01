"use client"

import { useEffect, useState } from "react"

import { CliHero } from "@/components/cli-hero"
import { PokemonToken } from "@/components/pokemon-token"
import { BitButton } from "@/components/ui/8bit/button"
import { BitCard } from "@/components/ui/8bit/card"
import { Switch as BitSwitch } from "@/components/ui/8bit/switch"
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
  // Which operation is in flight, not merely that one is: the progress label
  // has to name the button the user actually pressed, and `mode` cannot do that
  // job because it only records the last operation that finished.
  const [pending, setPending] = useState<Mode | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [clearing, setClearing] = useState(false)
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
  const hasInput = input.trim().length > 0
  const tooLong = !isWithinLimit(input)
  const busy = pending !== null
  const recognised = countKnownNames(input, knownNames)

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
    setPending(targetMode)
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
      setPending(null)
    }
  }

  function clearAll() {
    setInput("")
    setResult("")
    setError(null)
    setClearing(true)
    setTimeout(() => setClearing(false), 200)
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
    try {
      await navigator.clipboard.writeText(result)
    } catch {
      // Say so rather than confirming a copy that did not happen: the API is
      // unavailable over plain HTTP and in some embedded browsers.
      setError("Could not copy: this browser blocked clipboard access.")
      return
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const markerKinds = new Set(
    mode === "decode" ? splitMarkers(result).map((piece) => piece.kind) : []
  )

  return (
    <>
      <CliHero />
      <main className="relative z-10 mx-auto flex w-full max-w-4xl flex-col gap-2.5 px-4 sm:px-6 pt-0 pb-8">
        <header className="mt-2 mb-1 flex flex-col sm:flex-row sm:items-end justify-between gap-1">
          <div>
            <h2 className="font-pixel text-xl tracking-[0.02em] text-foreground [text-shadow:3px_3px_0_#000000]">
              Encode &amp; Decode
            </h2>
            <p className="mt-1 font-terminal text-lg leading-[1.35] text-muted-foreground">
              Each repeated character cycles through the Kanto, Johto and Hoenn dexes.
            </p>
          </div>
          <span className={cn("font-terminal text-base select-none shrink-0", tooLong ? "text-marker-mismatch" : "text-muted-foreground")}>
            {input.length} / {MAX_TEXT_CHARS}
          </span>
        </header>

        <section className="flex flex-col gap-1.5">
          <BitTextarea
            id="input"
            aria-label="Message to encode or Pokemon names to decode"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.preventDefault()
                if (canDecode) {
                  run("decode")
                } else if (hasInput) {
                  run("encode")
                }
              }
            }}
            spellCheck={false}
            placeholder="Type a message to encode, or paste Pokemon names to decode."
          />
        </section>

        <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pt-0.5">
          {/* Action buttons (Encode, Decode, Swap, Copy, Clear) */}
          <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
            <BitButton
              variant="yellow"
              onClick={() => run("encode")}
              disabled={busy || !hasInput}
            >
              {pending === "encode" ? "Encoding..." : "Encode"}
            </BitButton>
            {/*
              aria-disabled rather than disabled: the control keeps its place in
              the tab order and stays announced, so a keyboard or screen-reader
              user can find it and read why it is unavailable, instead of it
              silently vanishing from the page.
            */}
            <BitButton
              variant="secondary"
              onClick={() => canDecode && run("decode")}
              aria-disabled={!canDecode || busy}
              className={cn((!canDecode || busy) && "cursor-not-allowed opacity-40")}
            >
              {pending === "decode" ? "Decoding..." : "Decode"}
            </BitButton>
            <BitButton
              variant="outline"
              onClick={swap}
              disabled={!result}
            >
              Swap
            </BitButton>
            <BitButton
              variant="outline"
              onClick={copy}
              disabled={!result}
            >
              {copied ? "Copied!" : "Copy"}
            </BitButton>
            <BitButton
              variant="ghost"
              onClick={clearAll}
              disabled={!input && !result && !error}
            >
              Clear
            </BitButton>
          </div>

          {/* View toggle (Names <-> Sprites) */}
          <div className="flex items-center justify-end sm:justify-start gap-2 self-end sm:self-center select-none font-pixel text-xs shrink-0 py-0.5">
            <span className={cn("transition-colors", !showSprites ? "text-poke-yellow" : "text-muted-foreground")}>
              Names
            </span>
            <BitSwitch
              id="view-toggle"
              checked={showSprites}
              onCheckedChange={setShowSprites}
              aria-label="Toggle sprites view"
            />
            <span className={cn("transition-colors", showSprites ? "text-poke-yellow" : "text-muted-foreground")}>
              Sprites
            </span>
          </div>
        </section>

        {/*
          Persistent status, not a hover tooltip: it explains why decoding is
          shut without waiting for the user to go looking for an explanation.
        */}
        <p className="font-terminal text-lg text-foreground" aria-live="polite">
          {!hasInput
            ? "Type text to encode, or paste Pokemon names to decode."
            : canDecode
              ? `${recognised} Pokemon ${recognised === 1 ? "name" : "names"} recognised.`
              : "Not Pokemon names, so decoding is off. Encode instead."}
        </p>

        {error ? (
          <p className="font-terminal text-lg text-marker-mismatch" role="alert">
            {error}
          </p>
        ) : null}

        <section className="mt-1 flex flex-col gap-1" aria-live="polite">
          <BitCard
            variant="void"
            className={cn(
              "min-h-24 p-4 font-terminal text-xl text-foreground",
              clearing && "animate-crt-clear"
            )}
          >
            {result ? (
              mode === "encode" ? (
                showSprites ? (
                  <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
                    {result.split(" ").map((name, index) => (
                      <PokemonToken key={index} name={name} showSprites={true} />
                    ))}
                  </div>
                ) : (
                  <p className="leading-relaxed text-foreground select-all break-words font-terminal text-xl">
                    {result}
                  </p>
                )
              ) : (
                <div className="leading-relaxed select-all break-words font-terminal text-xl">
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
              )
            ) : (
              <p className="font-terminal text-xl text-muted-foreground select-none">
                {"Encoded Pokémon or decoded plaintext will appear here..."}
              </p>
            )}
          </BitCard>
          {result &&
            mode === "decode" &&
            [...markerKinds]
              .filter((kind) => kind in MARKER_LEGEND)
              .map((kind) => (
                <p key={kind} className="font-terminal text-base text-muted-foreground">
                  {MARKER_LEGEND[kind]}
                </p>
              ))}
        </section>
      </main>
    </>
  )
}
