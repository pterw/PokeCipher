import type { Metadata } from "next"
import { Press_Start_2P, VT323 } from "next/font/google"

import "./globals.css"

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
  // The product name carries the accent everywhere it is read: the tab, the
  // search result, the share card. The wordmark already does.
  title: "PokéCipher",
  applicationName: "PokéCipher",
  description:
    "Encode text into Pokémon names and decode it back again, using a stateful polyalphabetic cipher over three regional Pokédexes.",
  openGraph: {
    title: "PokéCipher",
    description:
      "A retro terminal that turns text into Pokémon names, and back again. Decoding is deliberately ambiguous, and says so.",
    siteName: "PokéCipher",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "PokéCipher",
    description:
      "A retro terminal that turns text into Pokémon names, and back again. Decoding is deliberately ambiguous, and says so.",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      className={`${fontPixel.variable} ${fontTerminal.variable} font-sans antialiased`}
    >
      <body>{children}</body>
    </html>
  )
}
