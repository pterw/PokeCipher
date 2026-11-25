import type { Metadata } from "next"
import localFont from "next/font/local"

import "./globals.css"

// Both faces are vendored in ./fonts under the SIL Open Font License (the
// licence files sit beside them) rather than loaded with next/font/google.
// Google's loader downloads the files during `next build`, so the build itself
// failed anywhere without egress to fonts.googleapis.com -- a hard error, not a
// warning, and one that no amount of retrying fixes. These are the same latin
// subsets that loader requested, so the rendered page is unchanged; the only
// difference is that the bytes now come from the repository.
//
// Headings and the wordmark only: pixel type is unreadable in bulk.
const fontPixel = localFont({
  src: "./fonts/press-start-2p-latin-400.woff2",
  weight: "400",
  variable: "--font-pixel",
  display: "swap",
})

// The CLI terminal voice: a chunky monospace for the hero transcript.
const fontTerminal = localFont({
  src: "./fonts/vt323-latin-400.woff2",
  weight: "400",
  variable: "--font-terminal",
  display: "swap",
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
