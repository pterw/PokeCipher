import { fileURLToPath } from "node:url"

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
  // Pin the workspace root to this app. A stray package-lock.json in the user's
  // home directory otherwise makes Next infer C:\Users\<user> as the root, so
  // the dev file watcher walks the entire home folder and HMR turns slow and
  // unreliable.
  turbopack: {
    root: fileURLToPath(new URL(".", import.meta.url)),
  },

  // Next treats 127.0.0.1 and localhost as different origins and blocks the HMR
  // socket for the one it was not started on. Without this, browsing the app on
  // 127.0.0.1 leaves HMR dead and the dev client falls back to full reloads.
  allowedDevOrigins: ["127.0.0.1"],

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
