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
 * `black-white` is Generation 5, not greyscale: 96x96 indexed-colour pixel art
 * at roughly 540 bytes. The `home` set this used to load is 22 KB per sprite —
 * 41x larger for something drawn at 32px, so a 100-character message pulled
 * about 2.2 MB — and those are smooth 3D renders that fight the pixel design
 * system. The set spans Gens 1-5, so Kanto/Johto/Hoenn is covered with room for
 * the Gen 4 expansion.
 */
export function spriteUrl(name: string): string {
  const slug = name
    .toLowerCase()
    .replace(/['’.]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return `https://img.pokemondb.net/sprites/black-white/normal/${slug}.png`
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
          "inline-block border border-border bg-secondary/60 px-1.5 py-0.5 font-mono text-xs leading-relaxed"
        )}
      >
        {name}
      </span>
    )
  }

  return (
    <span
      className="inline-flex h-8 w-8 items-center justify-center border border-border bg-secondary/60 align-middle"
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
      />
    </span>
  )
}
