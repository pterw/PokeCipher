import { fileURLToPath } from "node:url"

import { defineConfig } from "vitest/config"

/**
 * Unit tests for frontend logic.
 *
 * Runs in the `node` environment: the modules under test (marker parsing, the
 * API client) are pure and do not touch the DOM. Adding component tests later
 * means switching to `jsdom` and adding @testing-library/react.
 */
export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL(".", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    include: ["lib/**/*.test.ts", "components/**/*.test.tsx"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      reportsDirectory: "coverage",
      include: ["lib/**/*.ts", "components/**/*.tsx"],
      exclude: ["**/*.test.ts", "**/*.test.tsx"],
    },
  },
})
