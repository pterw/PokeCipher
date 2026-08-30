"use client"

import { useEffect, useState } from "react"

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
/** Enough one-tile-tall strips to cover the hero at any viewport height. */
const BANDS = 9

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

function BufferCursor() {
  const [frameIndex, setFrameIndex] = useState(0)

  // Calmer cadence: solid beats, blank beats, with occasional buffer coherence glitch
  const FRAMES = ["█", "█", "█", "▓", "█", " ", " ", " ", "░", "█", " ", " "]

  useEffect(() => {
    const timer = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % FRAMES.length)
    }, 380)
    return () => clearInterval(timer)
  }, [FRAMES.length])

  return (
    <span className="inline-block font-terminal text-poke-yellow select-none" aria-hidden="true">
      {FRAMES[frameIndex]}
    </span>
  )
}

/** CLI-terminal hero that sits above the cipher tool. */
export function CliHero() {
  return (
    <section className="relative overflow-hidden">
      {/* Backdrop: the scene's own horizontal bands, alternating direction. Each
          strip is exactly one tile tall and repeats on X only, so neighbouring
          bands slide past each other rather than overlapping. */}
      <div aria-hidden className="absolute inset-0 overflow-hidden">
        {Array.from({ length: BANDS }, (_, band) => (
          <div
            key={band}
            className={`hero-band ${band % 2 === 0 ? "hero-band-l" : "hero-band-r"}`}
            style={{
              top: `${band * ROWS * CELL}px`,
              height: `${ROWS * CELL}px`,
              backgroundImage: TILE,
              backgroundSize: `${COLS * CELL}px ${ROWS * CELL}px`,
              animationDuration: `${70 + band * 14}s`,
              imageRendering: "pixelated",
            }}
          />
        ))}
      </div>
      {/* The veil stays clear and only gently grounds into solid background at the bottom */}
      <div
        aria-hidden
        className="absolute inset-0"
        style={{
            background:
              "linear-gradient(to bottom, "+
              "rgba(15,56,15,0) 0%, rgba(15,56,15,0) 50%, rgba(15,56,15,0.08) 70%, rgba(15,56,15,0.25) 85%, rgba(15,56,15,0.65) 95%, #0f380f 100%)",
          }}
      />

      <div className="relative z-10 mx-auto w-full max-w-4xl px-6 pt-3 pb-2 sm:pt-4 sm:pb-3">
        <div>
          <h1 className="wordmark font-pixel text-[clamp(1.6rem,8vw,4.5rem)] leading-none select-none">
            <span className="text-poke-yellow">Poké</span>
            <span className="text-white">Cipher</span>
          </h1>
          <p className="hero-legible font-terminal text-xl text-poke-yellow sm:text-2xl">
            $ encrypt.txt --help
          </p>
        </div>
        <p className="hero-legible mt-1 max-w-[80ch] font-terminal text-xl leading-snug text-white sm:text-2xl">
          Turn text into Pokemon names — and Pokemon names back into text.
        </p>

        <div className="mt-2.5 sm:mt-3 border border-border bg-terminal-void shadow-[8px_8px_0px_#000000]">
          {/* Chrome: cmd.exe style titlebar with stepped tab linked to the body */}
          <div className="relative flex items-end border-b border-border bg-secondary pt-1 font-terminal text-sm sm:text-base">
            <span className="tab-staircase relative z-10 -mb-[1px] ml-2 flex h-[calc(1.625rem+1px)] w-[9rem] items-center bg-terminal-void px-2.5 text-left text-foreground">
              <span className="text-poke-yellow">$&nbsp;</span>
              POKEDEX.EXE
            </span>
          </div>
          <div className="flex flex-col gap-1.5 p-3.5 font-terminal text-lg leading-normal text-foreground sm:p-4 sm:text-xl [scrollbar-width:none]">
            <p>
              <span className="text-poke-yellow">$ </span>
              <span className="text-foreground">help --cipher</span>
            </p>

            <p className="text-foreground">
              PokéCipher maps printable ASCII (32–126) to Pokémon
              <br />
              from the Kanto, Johto, and Hoenn regional Pokédexes.
            </p>

            <div className="my-1 flex flex-col font-mono text-base text-primary sm:text-lg">
              <p>index &nbsp;= ord(char) - 32</p>
              <p>
                region = occurrence % 3 &nbsp; &nbsp;[
                <span className="font-semibold text-destructive">Kanto → Johto → Hoenn</span>
                ]
              </p>
              <p>token &nbsp;= POKEDEX[region][index]</p>
            </div>

            <p className="text-foreground">
              Each repeated character advances to the next region.
            </p>

            <div className="font-terminal text-lg sm:text-xl">
              <div className="flex flex-wrap items-start gap-x-2">
                <span>&quot;Hello&quot;</span>
                <span className="font-bold text-destructive">→</span>
                <span className="text-primary">Zubat</span>
                <span className="text-primary">Weepinbell</span>
                <div className="inline-flex flex-col items-center">
                  <span className="text-primary">Ponyta</span>
                  <span className="font-bold text-destructive text-sm sm:text-base whitespace-nowrap">
                    ↑ Kanto &apos;l&apos;
                  </span>
                </div>
                <div className="inline-flex flex-col items-center">
                  <span className="text-primary">Gyarados</span>
                  <span className="font-bold text-destructive text-sm sm:text-base whitespace-nowrap">
                    ↑ Johto &apos;l&apos;
                  </span>
                </div>
                <span className="text-primary">Slowbro</span>
              </div>
            </div>

            <p className="text-foreground">
              Names can repeat across regional Pokédexes, so decoding
              <br />
              may produce <span className="font-semibold text-marker-ambiguous">[x,y]</span> - multiple characters remain valid.
            </p>

            <p className="flex items-center gap-1.5 pt-1 text-lg sm:text-xl">
              <span className="text-poke-yellow font-bold">$</span>
              <BufferCursor />
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
