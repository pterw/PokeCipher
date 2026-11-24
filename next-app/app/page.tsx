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
  EMPTY_VOCABULARY,
  MAX_TEXT_CHARS,
  PokeCipherError,
  countKnownNames,
  decodeText,
  encodeText,
  fetchKnownNames,
  isWithinLimit,
  looksLikeCiphertext,
  type Vocabulary,
} from "@/lib/pokecipher-api"
import { cn } from "@/lib/utils"

type Mode = "encode" | "decode"

const MARKER_CLASS: Record<string, string> = {
  ambiguous: "text-marker-ambiguous",
  mismatch: "text-marker-mismatch",
  unknown: "text-marker-unknown",
}

const MARKER_LEGEND: Record<string, string> = {
  ambiguous:
    "Amber marks genuine ambiguity: several characters are valid there.",
  mismatch:
    "Red marks a state mismatch: that token may not belong to this message.",
  unknown: "Blue marks a name the Pokédex does not contain.",
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
  // Set when the decoder exceeded its search budget. The decoded text looks
  // exactly like an exact decode, so without this line a visitor is shown
  // confident nonsense: see lib/pokecipher-api.ts.
  const [truncated, setTruncated] = useState(false)
  const [copied, setCopied] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [vocabulary, setVocabulary] = useState<Vocabulary>(EMPTY_VOCABULARY)

  // Why the vocabulary is missing, when it is. Without this the status line
  // reports a failed fetch as "Not Pokémon names", which blames the text the
  // user pasted for a service that never answered.
  const [gateError, setGateError] = useState(false)

  // The decode gate needs the Pokedex vocabulary, which lives in Python. Fetched
  // once per mount rather than hardcoded, so the dex stays the single source of
  // truth. A failure here only leaves decoding shut; encoding is unaffected.
  useEffect(() => {
    let cancelled = false
    fetchKnownNames()
      .then((loaded) => {
        if (cancelled) return
        setVocabulary(loaded)
      })
      .catch((err) => {
        console.error("Failed to fetch Pokédex names for decode gate:", err)
        if (!cancelled) setGateError(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Wait for the vocabulary before the shortcut guesses a mode: only a loaded dex
  // can tell ciphertext from plain text, and guessing wrong encodes the ciphertext
  // the user meant to decode, which is the one mistake they cannot see in the
  // output. Absent names mean the fetch failed, which counts as not ready.
  const gateReady = vocabulary.names.size > 0
  const canDecode = looksLikeCiphertext(input, vocabulary)
  const hasInput = input.trim().length > 0
  const tooLong = !isWithinLimit(input)
  const busy = pending !== null
  const recognised = countKnownNames(input, vocabulary)

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
        setTruncated(false)
        setMode("encode")
      } else {
        const decoded = await decodeText(input)
        setResult(decoded.text)
        setTruncated(decoded.truncated)
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
    setTruncated(false)
    setClearing(true)
    setTimeout(() => setClearing(false), 200)
  }

  function swap() {
    if (!result) return
    setInput(result)
    setResult("")
    setMode(mode === "encode" ? "decode" : "encode")
    setError(null)
    setTruncated(false)
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
    // A retry that works clears the earlier complaint, so the page cannot show
    // "Copied!" above an alert still saying the clipboard was blocked.
    setError(null)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const markerKinds = new Set(
    mode === "decode" ? splitMarkers(result).map((piece) => piece.kind) : []
  )

  return (
    /* min-h-dvh, not vh: on mobile browsers `vh` is the tallest possible
       viewport (address bar retracted), so a vh-based shell is always taller
       than what the user can actually see and the last control sits under the
       chrome. dvh tracks the real, current viewport. */
    <div className="flex min-h-dvh flex-col">
      <CliHero />
      <main className="relative z-10 mx-auto flex w-full max-w-4xl flex-1 flex-col gap-2 px-4 pt-0 pb-[clamp(1rem,3vh,2rem)] sm:px-6">
        <header className="mt-2 mb-1 flex flex-col justify-between gap-1 sm:flex-row sm:items-end">
          <div>
            <h2 className="font-pixel text-xl tracking-[0.02em] text-foreground [text-shadow:3px_3px_0_#000000]">
              Encode &amp; Decode
            </h2>
            <p className="mt-1 font-terminal text-lg leading-[1.35] text-muted-foreground short:text-base">
              Each repeated character cycles through the Kanto, Johto and Hoenn
              dexes.
            </p>
          </div>
          <span
            className={cn(
              "shrink-0 font-terminal text-base select-none",
              tooLong ? "text-marker-mismatch" : "text-muted-foreground"
            )}
          >
            {input.length} / {MAX_TEXT_CHARS}
          </span>
        </header>

        <section className="flex flex-col gap-1.5">
          <BitTextarea
            id="input"
            aria-label="Message to encode or Pokémon names to decode"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.preventDefault()
                if (canDecode) {
                  run("decode")
                } else if (hasInput && gateReady) {
                  // Only guess the mode once the dex is loaded. Without it,
                  // pasted ciphertext reads as plain text and encoding it is
                  // the one wrong answer the user cannot spot in the output.
                  // If the dex never loads the shortcut stays quiet; the
                  // buttons still work and say why.
                  run("encode")
                }
              }
            }}
            spellCheck={false}
            placeholder="Type a message to encode, or paste Pokémon names to decode."
          />
        </section>

        <section className="flex flex-col justify-between gap-2.5 pt-0.5 sm:flex-row sm:items-center">
          {/* Action buttons (Encode, Decode, Swap, Copy, Clear) */}
          <div className="flex flex-wrap items-center gap-1 sm:gap-2">
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
              className={cn(
                (!canDecode || busy) && "cursor-not-allowed opacity-40"
              )}
            >
              {pending === "decode" ? "Decoding..." : "Decode"}
            </BitButton>
            <BitButton variant="outline" onClick={swap} disabled={!result}>
              Swap
            </BitButton>
            <BitButton variant="outline" onClick={copy} disabled={!result}>
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
          <div className="flex shrink-0 items-center justify-end gap-2 self-end py-0.5 font-pixel text-xs select-none sm:justify-start sm:self-center">
            <span
              className={cn(
                "transition-colors",
                !showSprites ? "text-poke-yellow" : "text-muted-foreground"
              )}
            >
              Names
            </span>
            <BitSwitch
              id="view-toggle"
              checked={showSprites}
              onCheckedChange={setShowSprites}
              aria-label="Toggle sprites view"
            />
            <span
              className={cn(
                "transition-colors",
                showSprites ? "text-poke-yellow" : "text-muted-foreground"
              )}
            >
              Sprites
            </span>
          </div>
        </section>

        {/*
          The status line and the error line share one reserved slot. The error
          is conditional, so without the reservation a validation failure would
          push the result card — and everything after it — down by a line the
          moment it appears, and back up when it clears. Two lines of slack
          (status + error) keep the geometry stable; the tool no longer jumps
          when a message arrives.
        */}
        <div className="flex min-h-[3.25rem] flex-col justify-start gap-0.5 short:min-h-[3rem]">
          <p
            className="font-terminal text-lg text-foreground"
            aria-live="polite"
          >
            {!hasInput
              ? "Type text to encode, or paste Pokémon names to decode."
              : canDecode
                ? `${recognised} Pokémon ${recognised === 1 ? "name" : "names"} recognised.`
                : gateError
                  ? "Could not load the Pokémon list, so decoding is off. Encoding still works."
                  : "Not Pokémon names, so decoding is off. Encode instead."}
          </p>

          {error ? (
            <p
              className="font-terminal text-lg text-marker-mismatch"
              role="alert"
            >
              {error}
            </p>
          ) : null}
        </div>

        <section className="mt-1 flex flex-col gap-1" aria-live="polite">
          <BitCard
            variant="void"
            className={cn(
              "min-h-20 p-4 font-terminal text-xl text-foreground",
              clearing && "animate-crt-clear"
            )}
          >
            {result ? (
              mode === "encode" ? (
                showSprites ? (
                  <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
                    {result.split(" ").map((name, index) => (
                      <PokemonToken
                        key={index}
                        name={name}
                        showSprites={true}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="font-terminal text-xl leading-relaxed break-words text-foreground select-all">
                    {result}
                  </p>
                )
              ) : (
                <div className="font-terminal text-xl leading-relaxed break-words select-all">
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
          {result && mode === "decode" && truncated ? (
            <p
              className="font-terminal text-base text-marker-ambiguous"
              role="status"
            >
              This message exceeded the decoder&apos;s search budget, so some
              characters may be wrong. Decode a shorter message for an exact
              answer.
            </p>
          ) : null}
          {result &&
            mode === "decode" &&
            [...markerKinds]
              .filter((kind) => kind in MARKER_LEGEND)
              .map((kind) => (
                <p
                  key={kind}
                  className="font-terminal text-base text-muted-foreground"
                >
                  {MARKER_LEGEND[kind]}
                </p>
              ))}
        </section>
      </main>
    </div>
  )
}
