import * as React from "react"
import { cn } from "@/lib/utils"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/8bit/card"

import "@/components/ui/8bit/styles/retro.css"

export interface TerminalLine {
  color?: string
  text: string
  type: "input" | "output" | "comment"
}

export interface Advanced1Props {
  className?: string
  lines?: TerminalLine[]
  title?: string
  children?: React.ReactNode
}

export const defaultLines: TerminalLine[] = [
  { type: "comment", text: "# PokéCipher Terminal Session" },
  { type: "input", text: "pokecipher --help" },
  { type: "output", text: "Loading Kanto, Johto, Hoenn Pokédexes..." },
  { type: "output", text: "Cipher core initialized. Ready." },
]

function lineClass(type: TerminalLine["type"]): string {
  if (type === "input") {
    return "text-foreground"
  }
  if (type === "comment") {
    return "text-muted-foreground"
  }
  return "text-muted-foreground/80"
}

function linePrefix(type: TerminalLine["type"]): string {
  if (type === "input") {
    return "$ "
  }
  return ""
}

export default function Advanced1({
  title = "POKEDEX.EXE",
  lines = defaultLines,
  className,
  children,
}: Advanced1Props) {
  return (
    <div className={cn("w-full", className)}>
      <Card variant="void" className="shadow-[8px_8px_0px_#000000]">
        <CardHeader className="bg-secondary px-3 py-1.5 border-b-2 border-[#000000]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-terminal text-base text-poke-yellow select-none">$</span>
              <CardTitle className="font-pixel text-xs tracking-wider text-foreground select-none">
                {title}
              </CardTitle>
            </div>
            <span className="font-terminal text-xs text-foreground select-none tracking-wider">
              [TTY1 &bull; 8-BIT]
            </span>
          </div>
        </CardHeader>
        <CardContent className="p-3 sm:p-4 bg-terminal-void">
          {children ? (
            children
          ) : (
            <div className="space-y-0.5 font-terminal text-lg">
              {lines.map((line, idx) => (
                <p
                  className={cn("leading-tight", lineClass(line.type))}
                  key={`${line.text}-${idx}`}
                >
                  {linePrefix(line.type)}
                  {line.text}
                </p>
              ))}
              <p className="animate-pulse text-foreground font-terminal text-lg">
                {"$ "} _
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export { Advanced1 }
