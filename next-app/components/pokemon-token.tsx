"use client"

import Image from "next/image"
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
 */
export function spriteUrl(name: string): string {
  const slug = name
    .toLowerCase()
    .replace(/['’.]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return `https://img.pokemondb.net/sprites/home/normal/${slug}.png`
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
      <Image
        src={spriteUrl(name)}
        alt={name}
        width={32}
        height={32}
        unoptimized
        onError={() => setSpriteFailed(true)}
      />
    </span>
  )
}
