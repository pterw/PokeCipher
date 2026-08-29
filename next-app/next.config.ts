import type { NextConfig } from "next"

// Where the Python cipher API lives. Local dev defaults to the stdlib server
// (`python api_server.py`, port 8000); production sets this to the deployed
// API project. The frontend always calls same-origin `/api/*`, which the
// rewrite below proxies to this origin.
const API_ORIGIN = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "")

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
    return [
      {
        source: "/api/:path*",
        destination: `${API_ORIGIN}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
