import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { MAX_TEXT_CHARS, PokeCipherError, decodeText, encodeText, isWithinLimit } from "./pokecipher-api"

/** Build a minimal Response whose body parses as JSON. */
function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response
}

/** Build a Response whose body is not parseable as JSON. */
function responseWithoutJson(status: number): Response {
  return {
    ok: false,
    status,
    json: async () => {
      throw new SyntaxError("not json")
    },
  } as unknown as Response
}

let fetchMock: ReturnType<typeof vi.fn>

beforeEach(() => {
  fetchMock = vi.fn()
  vi.stubGlobal("fetch", fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
})

describe("encodeText", () => {
  it("posts the text to /api/encode", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ result: "Zubat" }))
    await encodeText("H")
    expect(fetchMock).toHaveBeenCalledTimes(1)

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe("/api/encode")
    expect(init.method).toBe("POST")
    expect(init.headers).toEqual({ "Content-Type": "application/json" })
    expect(JSON.parse(init.body)).toEqual({ text: "H" })
  })

  it("returns the result field", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ result: "Zubat Weepinbell" }))
    await expect(encodeText("He")).resolves.toBe("Zubat Weepinbell")
  })
})

describe("decodeText", () => {
  it("posts the text to /api/decode", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ result: "He" }))
    await decodeText("Zubat Weepinbell")

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe("/api/decode")
    expect(JSON.parse(init.body)).toEqual({ text: "Zubat Weepinbell" })
  })
})

describe("error handling", () => {
  it("surfaces the server's error message", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ error: "Field 'text' must be a string." }, 400))
    await expect(encodeText("x")).rejects.toThrow(PokeCipherError)
    await expect(encodeText("x")).rejects.toThrow("Field 'text' must be a string.")
  })

  it("reports a status when the body has no error field", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}, 413))
    await expect(encodeText("x")).rejects.toThrow("Request failed with status 413.")
  })

  it("reports a malformed response body", async () => {
    fetchMock.mockResolvedValue(responseWithoutJson(500))
    await expect(encodeText("x")).rejects.toThrow("The server returned a malformed response.")
  })

  it("reports a response whose result is not a string", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ result: 42 }))
    await expect(encodeText("x")).rejects.toThrow("The server returned a malformed response.")
  })

  it("reports a response with no result field", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}))
    await expect(encodeText("x")).rejects.toThrow("The server returned a malformed response.")
  })
})

describe("configuration", () => {
  it("prefixes requests with NEXT_PUBLIC_API_URL and strips a trailing slash", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://cipher.example.com/")
    vi.resetModules()
    const configured = await import("./pokecipher-api")

    fetchMock.mockResolvedValue(jsonResponse({ result: "Zubat" }))
    await configured.encodeText("H")

    expect(fetchMock.mock.calls[0][0]).toBe("https://cipher.example.com/api/encode")
  })

  it("reads the input cap from NEXT_PUBLIC_MAX_TEXT_CHARS", async () => {
    vi.stubEnv("NEXT_PUBLIC_MAX_TEXT_CHARS", "1234")
    vi.resetModules()
    const configured = await import("./pokecipher-api")

    expect(configured.MAX_TEXT_CHARS).toBe(1234)
    expect(configured.isWithinLimit("x".repeat(1234))).toBe(true)
    expect(configured.isWithinLimit("x".repeat(1235))).toBe(false)
  })
})

describe("isWithinLimit", () => {
  it("accepts text at and below the default cap", () => {
    expect(isWithinLimit("x".repeat(MAX_TEXT_CHARS))).toBe(true)
    expect(isWithinLimit("x".repeat(MAX_TEXT_CHARS - 1))).toBe(true)
  })

  it("rejects text above the default cap", () => {
    expect(isWithinLimit("x".repeat(MAX_TEXT_CHARS + 1))).toBe(false)
  })

  it("accepts the empty string", () => {
    expect(isWithinLimit("")).toBe(true)
  })
})
