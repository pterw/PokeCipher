import type { Metadata } from "next"
import { Press_Start_2P, VT323 } from "next/font/google"

import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

// Headings and the wordmark only: pixel type is unreadable in bulk.
const fontPixel = Press_Start_2P({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-pixel",
})

// The CLI terminal voice: a chunky monospace for the hero transcript.
const fontTerminal = VT323({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-terminal",
})

export const metadata: Metadata = {
  title: "PokeCipher",
  description:
    "Encrypt text into Pokemon names and decrypt them back again, using a stateful polyalphabetic cipher over three regional Pokedexes.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontPixel.variable} ${fontTerminal.variable} font-sans antialiased`}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
