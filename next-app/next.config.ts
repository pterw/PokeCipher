import type { NextConfig } from "next"

// Where the Python cipher API lives.
//
// Three cases, in priority order:
//
//  1. NEXT_PUBLIC_API_URL set    -> proxy /api/* there (split deployment).
//  2. Unset, running on Vercel   -> no rewrite. The platform serves the
//                                   Python functions from /api/* same-origin,
//                                   so rewriting would point them at us.
//  3. Unset, running locally     -> proxy to the stdlib server on port 8000
//                                   (`python api_server.py`). This covers both
//                                   `next dev` and `next start`, which
//                                   api_server.py documents as supported.
//
// Read the variable with `||`, not `??`: .env.local ships it set-but-empty,
// and an empty string is not nullish, so `??` yields "" and the destination
// collapses to `/api/:path*` — pointing Next at itself and 404ing every call.
const API_ORIGIN = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "")
const LOCAL_API_ORIGIN = "http://localhost:8000"

// Vercel sets VERCEL=1 in both build and runtime environments. NODE_ENV cannot
// stand in for it: `next start` is production but still wants the local proxy.
const ON_VERCEL = Boolean(process.env.VERCEL)

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
    const origin = API_ORIGIN || (ON_VERCEL ? "" : LOCAL_API_ORIGIN)
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
