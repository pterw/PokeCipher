"use client"

import { useEffect, useState } from "react"
import { Advanced1 } from "@/components/ui/8bit/blocks/advanced1"

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
const BANDS = 7

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
  yellow: "#f6c72a",
  black: "#071a07",
} as const

/** A sprite is a list of [dx, dy, width, height, colour] rects. */
type Parts = readonly (readonly [dx: number, dy: number, w: number, h: number, color: string])[]

function buildTile(): string {
  const cells: string[] = new Array(COLS * ROWS).fill(C.sky)

  const set = (x: number, y: number, color: string): void => {
    if (x >= 0 && x < COLS && y >= 0 && y < ROWS) cells[y * COLS + x] = color
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

const CURSOR_FRAMES = ["█", "█", "█", "▓", "█", " ", " ", " ", "░", "█", " ", " "] as const

function BufferCursor() {
  const [frameIndex, setFrameIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % CURSOR_FRAMES.length)
    }, 380)
    return () => clearInterval(timer)
  }, [])

  return (
    <span className="inline-block font-terminal text-poke-yellow select-none" aria-hidden="true">
      {CURSOR_FRAMES[frameIndex]}
    </span>
  )
}

/** CLI-terminal hero that sits above the cipher tool. */
export function CliHero() {
  return (
    <section className="relative overflow-hidden">
      {/* Backdrop: horizontal bands sliding past each other.

          The tile is a ~60KB data URI. Held once here as a custom property and
          inherited by every band, it is serialised into the HTML a single time
          instead of once per band. */}
      <div
        aria-hidden
        className="absolute inset-0 overflow-hidden"
        style={{ "--hero-tile": TILE } as React.CSSProperties}
      >
        {Array.from({ length: BANDS }, (_, band) => (
          <div
            key={band}
            className={`hero-band ${band % 2 === 0 ? "hero-band-l" : "hero-band-r"}`}
            style={{
              top: `${band * ROWS * CELL}px`,
              height: `${ROWS * CELL}px`,
              backgroundImage: "var(--hero-tile)",
              backgroundSize: `${COLS * CELL}px ${ROWS * CELL}px`,
              animationDuration: `${160 + band * 30}s`,
              imageRendering: "pixelated",
            }}
          />
        ))}
      </div>
      {/* Smooth gradient overlay starting at 30% and grounding into solid background at the bottom */}
      <div
        aria-hidden
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(to bottom, " +
            "rgba(15,56,15,0) 0%, rgba(15,56,15,0) 30%, rgba(15,56,15,0.15) 50%, rgba(15,56,15,0.45) 73%, rgba(15,56,15,0.8) 91%, rgba(15,56,15,0.96) 98%, #0f380f 100%)",
        }}
      />

      {/* The bottom padding is smaller than the top on purpose. The band the eye
          reads below the terminal also carries the next section's heading slack,
          so equal padding renders as an unequal gap. These were solved by
          measuring both bands; 18 and 26 are off the 4px step because that is
          where the measured delta reaches zero, and the wordmark's size feeds
          into it, so re-measure if the mark changes. */}
      <div className="relative z-10 mx-auto w-full max-w-5xl px-4 sm:px-6 pt-8 pb-[18px] sm:pt-10 sm:pb-[26px]">
        <header className="overflow-visible">
          {/* The size lives in the clamp, not in a transform. A scale() would
              paint larger glyphs without growing the layout box, so the hero
              would under-report its own height and the mark could ride over
              the terminal below it. */}
          <h1 className="wordmark inline-block font-pixel text-[clamp(1.6rem,8vw,5.2rem)] leading-none select-none">
            <span className="text-poke-yellow">Poké</span>
            <span className="text-white">Cipher</span>
          </h1>
        </header>

        <Advanced1 title="POKEDEX.EXE" className="mt-6 sm:mt-8">
          <div className="flex flex-col gap-1.5 font-terminal text-[20px] leading-snug text-foreground sm:text-[22px] [scrollbar-width:none]">
            <p>
              <span className="text-poke-yellow font-normal">$ </span>
              <span className="text-foreground">help --cipher</span>
            </p>

            <p className="text-foreground">
              A cipher <span className="font-semibold text-destructive">transforms</span> text into secret code. PokéCipher encodes characters into Pokémon names drawn from three regional Pokédexes.
            </p>

            <div className="my-1 flex flex-col font-mono text-[14px] sm:text-[16px] text-primary">
              <p>index &nbsp;= ord(char) - 32</p>
              <p>
                region = occurrence % 3 &nbsp; &nbsp;[
                <span className="font-semibold text-foreground">Kanto → Johto → Hoenn</span>
                ]
              </p>
              <p>token &nbsp;= POKEDEX[region][index]</p>
            </div>

            <p className="text-foreground">
              Each repeated character advances to the next region:
            </p>

            <div className="font-terminal text-[20px] sm:text-[22px]">
              <div className="flex flex-wrap items-start gap-x-2.5">
                <span>&quot;Hello&quot;</span>
                <span className="font-bold text-poke-yellow">→</span>
                <span className="text-poke-yellow">Zubat</span>
                <div className="inline-flex flex-col items-center">
                  <span className="text-poke-yellow">Weepinbell</span>
                  <span className="font-bold text-destructive text-[13.5px] sm:text-[15.5px] whitespace-nowrap">
                    ↑ Kanto &apos;e&apos;
                  </span>
                </div>
                <div className="inline-flex flex-col items-center">
                  <span className="text-poke-yellow">Ponyta</span>
                  <span className="font-bold text-destructive text-[13.5px] sm:text-[15.5px] whitespace-nowrap">
                    ↑ Kanto &apos;l&apos;
                  </span>
                </div>
                <div className="inline-flex flex-col items-center">
                  <span className="text-poke-yellow">Gyarados</span>
                  <span className="font-bold text-destructive text-[13.5px] sm:text-[15.5px] whitespace-nowrap">
                    ↑ Johto &apos;l&apos;
                  </span>
                </div>
                <span className="text-poke-yellow">Slowbro</span>
              </div>
            </div>

            <p className="text-foreground">
              Because Pokémon names repeat across regions, decoding is intentionally ambiguous:
            </p>

            <div className="flex flex-wrap items-center gap-x-2.5 font-terminal text-[20px] sm:text-[22px]">
              <span>Round-trip &quot;Hello World!&quot;</span>
              <span className="font-bold text-poke-yellow">→</span>
              <span className="font-bold">
                Hello W<span className="text-marker-ambiguous">[n,o]</span>rld!
              </span>
              <span className="font-mono text-[14px] sm:text-[16px] text-primary">
                (Slowpoke: Kanto &apos;n&apos; vs Johto &apos;o&apos;)
              </span>
            </div>

            <p className="flex items-center gap-1.5 pt-0.5 text-[20px] sm:text-[22px]">
              <span className="text-poke-yellow font-normal">$</span>
              <BufferCursor />
            </p>
          </div>
        </Advanced1>
      </div>
    </section>
  )
}
