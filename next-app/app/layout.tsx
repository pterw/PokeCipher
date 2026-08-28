import type { Metadata } from "next"
import { Geist, Geist_Mono, Press_Start_2P } from "next/font/google"

import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

const fontSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
})

// Headings and the wordmark only: pixel type is unreadable in bulk.
const fontPixel = Press_Start_2P({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-pixel",
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
      className={`${fontSans.variable} ${fontMono.variable} ${fontPixel.variable} font-sans antialiased`}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
