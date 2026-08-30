"use client"

import { useState } from "react"

import { cn } from "@/lib/utils"

/**
 * Build a sprite URL from a Pokémon name.
 *
 * The PokémonDB sprite CDN is keyed by name rather than national dex number,
 * which suits this app: the cipher works in regional dex names, where the same
 * name can mean different characters in different regions. Slugs drop
 * apostrophes and punctuation (`Farfetch'd` -> `farfetchd`, `Nidoran-F` ->
 * `nidoran-f`). Any slug the CDN does not know falls back to the name.
 *
 * The `ruby-sapphire` set is Generation 3 — GBA hardware, the same machine whose
 * palette the design system emulates, and whose roster is exactly this cipher's
 * Kanto + Johto + Hoenn. All 210 names in use resolve there, at ~626 bytes each.
 *
 * Two earlier choices were wrong. `home` renders are 22 KB smooth 3D models, so
 * a 100-character message pulled ~2.2 MB and fought the pixel world. `black-white`
 * fixed the weight but is Generation 5 art on Nintendo DS, an era the Game Boy
 * north star does not include.
 *
 * The dimensions matter as much as the era: these are 64x64, so drawing them in a
 * 32px cell is an exact 2:1 downscale where every output pixel is one 2x2 source
 * block. That is what makes `image-rendering: pixelated` faithful here — at the
 * 96x96 set's 3:1 it discarded two of every three pixels and read as mush.
 */
export function spriteUrl(name: string): string {
  const slug = name
    .toLowerCase()
    .replace(/['’.]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return `https://img.pokemondb.net/sprites/ruby-sapphire/normal/${slug}.png`
}

interface PokemonTokenProps {
  name: string
  showSprites: boolean
}

/** Render one ciphertext unit as a sprite, or as its name. */
export function PokemonToken({ name, showSprites }: PokemonTokenProps) {
  const [spriteFailed, setSpriteFailed] = useState(false)
  const useSprite = showSprites && !spriteFailed

  if (!useSprite) {
    return (
      <span
        className={cn(
          "inline-block border border-border bg-card px-2 py-0.5 font-mono text-sm leading-relaxed text-foreground transition-colors hover:border-poke-yellow"
        )}
        title={name}
      >
        {name}
      </span>
    )
  }

  return (
    <span
      className="inline-flex h-8 w-8 items-center justify-center align-middle"
      title={name}
    >
      {/* A plain <img>, not next/image. The Image here always carried
          `unoptimized`, which makes next/image return the raw src and skip
          /_next/image entirely — so the optimizer, and the `remotePatterns`
          allow-list that gates it, were never in play. What remained was a
          wrapper whose every remaining feature is one attribute below. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={spriteUrl(name)}
        alt={name}
        width={32}
        height={32}
        loading="lazy"
        decoding="async"
        onError={() => setSpriteFailed(true)}
        className="h-8 w-8 [image-rendering:pixelated]"
      />
    </span>
  )
}
