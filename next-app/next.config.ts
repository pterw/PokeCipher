import type { NextConfig } from "next"

// Where the Python cipher API lives.
//
// Empty means "same origin": in production the Python functions are served
// from /api/* by the platform itself, so no rewrite is needed. Local dev has
// no same-origin backend — the API is a separate stdlib server on port 8000
// (`python api_server.py`) — so dev falls back to that.
//
// Note this must not use `??`: NEXT_PUBLIC_API_URL is set-but-empty in
// .env.local, and an empty string is not nullish. Reading it with `??` yields
// "" and the rewrite destination collapses to `/api/:path*`, which points at
// Next itself and 404s every request.
const API_ORIGIN = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "")
const DEV_API_ORIGIN = "http://localhost:8000"

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "img.pokemondb.net",
        pathname: "/sprites/**",
      },
    ],
  },
  async rewrites() {
    const origin = API_ORIGIN || (process.env.NODE_ENV === "development" ? DEV_API_ORIGIN : "")
    // Same-origin: let /api/* fall through to the platform's Python functions.
    if (!origin) return []
    return [
      {
        source: "/api/:path*",
        destination: `${origin}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
