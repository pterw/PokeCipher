"use client"

import { useState } from "react"

import { PokeCipherError, decodeText, encodeText } from "@/lib/pokecipher-api"

/**
 * CLI-terminal hero with an 8-bit Pokémon overworld backdrop.
 *
 * The backdrop is a tileable SVG pixel scene generated from a tiny grid at
 * module scope, inlined as a data URI, and repeated with `background-repeat`.
 * No external assets. The terminal is a working CLI demo that talks to the
 * Python cipher through lib/pokecipher-api and never re-implements it.
 */

const COLS = 48
const ROWS = 12
const CELL = 10

/** Retro 8-bit palette: sky, clouds, grass, and the two scene sprites. */
const C = {
  sky: "#7dc4cf",
  cloud: "#e9f4f0",
  grassTop: "#8bac0f",
  grassEdge: "#0f380f",
  grassA: "#6da60f",
  grassB: "#4a8507",
  red: "#e0473a",
  white: "#f2efe6",
  black: "#20302a",
  yellow: "#f6c72a",
  brown: "#8a5a2b",
} as const

/** A sprite is a list of [dx, dy, width, height, colour] rects. */
type Parts = ReadonlyArray<readonly [number, number, number, number, string]>

function buildTile(): string {
  const cells = new Array<string>(COLS * ROWS).fill(C.sky)
  const set = (x: number, y: number, color: string): void => {
    if (x < 0 || x >= COLS || y < 0 || y >= ROWS) return
    cells[y * COLS + x] = color
  }
  const fill = (x: number, y: number, w: number, h: number, color: string): void => {
    for (let dy = 0; dy < h; dy += 1) {
      for (let dx = 0; dx < w; dx += 1) set(x + dx, y + dy, color)
    }
  }
  const sprite = (ox: number, oy: number, parts: Parts): void => {
    for (const [dx, dy, w, h, color] of parts) fill(ox + dx, oy + dy, w, h, color)
  }

  // Ground: horizon strip, dark edge, then a checker of two greens.
  fill(0, 6, COLS, 1, C.grassTop)
  fill(0, 7, COLS, 1, C.grassEdge)
  for (let y = 8; y < ROWS; y += 1) {
    for (let x = 0; x < COLS; x += 1) {
      set(x, y, (x + y) % 2 === 0 ? C.grassA : C.grassB)
    }
  }

  const cloud: Parts = [
    [1, 0, 4, 1, C.cloud],
    [0, 1, 7, 1, C.cloud],
    [1, 2, 5, 1, C.cloud],
  ]
  sprite(2, 0, cloud)
  sprite(18, 1, cloud)
  sprite(35, 0, cloud)

  const pokeball: Parts = [
    [1, 0, 4, 1, C.red],
    [0, 1, 6, 1, C.red],
    [0, 2, 2, 1, C.black],
    [4, 2, 2, 1, C.black],
    [2, 2, 2, 1, C.white],
    [0, 3, 6, 1, C.white],
    [1, 4, 4, 1, C.white],
    [2, 5, 2, 1, C.black],
  ]
  sprite(21, 6, pokeball)

  const pikachu: Parts = [
    [2, 0, 1, 1, C.yellow],
    [5, 0, 1, 1, C.yellow],
    [2, 1, 1, 1, C.yellow],
    [5, 1, 1, 1, C.yellow],
    [0, 2, 1, 1, C.yellow],
    [1, 2, 1, 1, C.black],
    [2, 2, 4, 1, C.yellow],
    [6, 2, 1, 1, C.black],
    [7, 2, 1, 1, C.yellow],
    [0, 3, 1, 1, C.red],
    [1, 3, 6, 1, C.yellow],
    [7, 3, 1, 1, C.red],
    [1, 4, 6, 1, C.yellow],
    [0, 5, 1, 1, C.yellow],
    [3, 5, 1, 1, C.yellow],
    [5, 5, 1, 1, C.yellow],
    [7, 5, 1, 1, C.yellow],
  ]
  sprite(8, 6, pikachu)

  const bush: Parts = [
    [0, 2, 4, 1, C.grassEdge],
    [1, 3, 3, 1, C.grassA],
    [1, 1, 1, 1, C.grassEdge],
    [2, 1, 1, 1, C.grassEdge],
  ]
  sprite(0, 8, bush)
  sprite(44, 8, bush)

  const rects: string[] = []
  for (let y = 0; y < ROWS; y += 1) {
    for (let x = 0; x < COLS; x += 1) {
      rects.push(`<rect x="${x}" y="${y}" width="1" height="1" fill="${cells[y * COLS + x]}"/>`)
    }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${COLS}" height="${ROWS}" shape-rendering="crispEdges">${rects.join("")}</svg>`
}

const TILE = `url("data:image/svg+xml,${encodeURIComponent(buildTile())}")`

type Line = { kind: "cmd" | "out" | "err" | "info"; text: string }

const INITIAL_LINES: Line[] = [
  { kind: "cmd", text: 'encode "Try below"' },
  {
    kind: "out",
    text: "Persian Farfetch'd Shellder Bulbasaur Machoke Weepinbell Ponyta Slowbro Grimer",
  },
  { kind: "info", text: 'type a message below, or "help"' },
]

const HELP_LINES: Line[] = [
  { kind: "info", text: "encode <text>  — turn text into Pokemon names" },
  { kind: "info", text: "decode <names> — turn Pokemon names back into text" },
  { kind: "info", text: "help           — show this" },
  { kind: "info", text: "clear          — reset the terminal" },
]

/** CLI-terminal hero that sits above the cipher tool. */
export function CliHero() {
  const [lines, setLines] = useState<Line[]>(INITIAL_LINES)
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const [focused, setFocused] = useState(false)

  function append(next: Line[]) {
    setLines((prev) => [...prev, ...next].slice(-12))
  }

  async function submit() {
    const raw = input.trim()
    if (!raw || busy) return
    setInput("")

    if (raw === "clear") {
      setLines(INITIAL_LINES)
      return
    }
    if (raw === "help") {
      append([{ kind: "cmd", text: raw }, ...HELP_LINES])
      return
    }

    const isDecode = raw.startsWith("decode ")
    const rest =
      raw.startsWith("encode ") || isDecode ? raw.slice(raw.indexOf(" ") + 1).trim() : raw
    if (!rest) {
      append([
        { kind: "cmd", text: raw },
        { kind: "err", text: "usage: encode <text> | decode <names>" },
      ])
      return
    }

    setBusy(true)
    append([{ kind: "cmd", text: raw }])
    try {
      const output = isDecode ? await decodeText(rest) : await encodeText(rest)
      append([{ kind: "out", text: output }])
    } catch (caught) {
      append([
        {
          kind: "err",
          text:
            caught instanceof PokeCipherError
              ? caught.message
              : "Could not reach the cipher service.",
        },
      ])
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0"
        style={{
          backgroundImage: TILE,
          backgroundSize: `${COLS * CELL}px ${ROWS * CELL}px`,
          imageRendering: "pixelated",
        }}
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-linear-to-b from-background/10 via-background/35 to-background"
      />

      <div className="relative z-10 mx-auto w-full max-w-4xl px-6 pt-10 pb-10 sm:pt-12 sm:pb-12">
        <h1 className="font-pixel text-3xl leading-tight text-foreground sm:text-4xl">
          PokeCipher
        </h1>
        <p className="mt-2 font-terminal text-xl text-foreground sm:text-2xl">
          $ encrypt.txt --help
        </p>
        <p className="mt-3 max-w-[80ch] font-terminal text-lg leading-snug text-foreground sm:text-xl">
          Turn text into Pokemon names — and Pokemon names back into text.
        </p>

        <div className="mt-6 border border-border bg-[#071a07]">
          <div className="border-b border-border bg-secondary px-3 py-1.5 font-terminal text-sm text-muted-foreground">
            bash
          </div>
          <div className="space-y-0.5 p-4 font-terminal text-lg text-foreground sm:text-xl">
            {lines.map((line, index) => (
              <p
                key={index}
                className={
                  line.kind === "out"
                    ? "text-primary"
                    : line.kind === "err"
                      ? "text-destructive"
                      : line.kind === "info"
                        ? "text-muted-foreground"
                        : "text-foreground"
                }
              >
                {line.kind === "cmd" ? <span className="text-poke-yellow">$ </span> : null}
                {line.text}
              </p>
            ))}
            <form
              className="flex items-center gap-2"
              onSubmit={(event) => {
                event.preventDefault()
                void submit()
              }}
            >
              <span className="text-poke-yellow">$</span>
              {input === "" && !busy && !focused ? (
                <span className="h-5 w-3 shrink-0 animate-blink bg-poke-yellow" aria-hidden />
              ) : null}
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                disabled={busy}
                spellCheck={false}
                autoComplete="off"
                aria-label="Terminal input"
                className="min-w-0 flex-1 bg-transparent font-terminal text-lg text-foreground focus:outline-none sm:text-xl"
              />
            </form>
          </div>
        </div>
      </div>
    </section>
  )
}
