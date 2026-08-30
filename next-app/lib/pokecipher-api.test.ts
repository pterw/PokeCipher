import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  MAX_TEXT_CHARS,
  PokeCipherError,
  countKnownNames,
  decodeText,
  encodeText,
  fetchKnownNames,
  isWithinLimit,
  looksLikeCiphertext,
} from "./pokecipher-api"

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

  it("reports a non-JSON response as an unreachable service", async () => {
    fetchMock.mockResolvedValue(responseWithoutJson(500))
    await expect(encodeText("x")).rejects.toThrow(
      "Could not reach the cipher service (HTTP 500). Is the API running?",
    )
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


const KNOWN = new Set(["zubat", "weepinbell", "ponyta", "gyarados", "slowbro", "farfetch'd"])

describe("looksLikeCiphertext", () => {
  it("is false before the name list has loaded", () => {
    expect(looksLikeCiphertext("Zubat Weepinbell", new Set())).toBe(false)
  })

  it("accepts a single name, which is legitimate ciphertext", () => {
    expect(looksLikeCiphertext("Zubat", KNOWN)).toBe(true)
  })

  it("rejects plain prose", () => {
    expect(looksLikeCiphertext("The quick brown fox", KNOWN)).toBe(false)
  })

  it("opens and closes live as the first token is typed", () => {
    expect(looksLikeCiphertext("Zub", KNOWN)).toBe(false)
    expect(looksLikeCiphertext("Zubat", KNOWN)).toBe(true)
    expect(looksLikeCiphertext("Zubatx", KNOWN)).toBe(false)
  })

  it("ignores case", () => {
    expect(looksLikeCiphertext("zubat weepinbell", KNOWN)).toBe(true)
    expect(looksLikeCiphertext("ZUBAT", KNOWN)).toBe(true)
  })

  it("tolerates surrounding and repeated whitespace", () => {
    expect(looksLikeCiphertext("   Zubat   Weepinbell  ", KNOWN)).toBe(true)
    expect(looksLikeCiphertext(["", "Zubat"].join(String.fromCharCode(10)), KNOWN)).toBe(
      true
    )
  })

  it("is false for empty or whitespace-only input", () => {
    expect(looksLikeCiphertext("", KNOWN)).toBe(false)
    expect(looksLikeCiphertext("   ", KNOWN)).toBe(false)
  })

  it("judges only the first token, so leading prose closes the gate", () => {
    expect(looksLikeCiphertext("Hello Zubat", KNOWN)).toBe(false)
  })

  it("handles a name carrying an apostrophe", () => {
    expect(looksLikeCiphertext("Farfetch'd Zubat", KNOWN)).toBe(true)
  })
})

describe("countKnownNames", () => {
  it("counts only recognised tokens", () => {
    expect(countKnownNames("Zubat Weepinbell banana", KNOWN)).toBe(2)
  })

  it("is zero before the list loads", () => {
    expect(countKnownNames("Zubat", new Set())).toBe(0)
  })

  it("ignores case and extra whitespace", () => {
    expect(countKnownNames("  zubat   PONYTA  ", KNOWN)).toBe(2)
  })
})

describe("fetchKnownNames", () => {
  it("lowercases the served names into a set", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ names: ["Zubat", "Ponyta"] }))
    vi.stubGlobal("fetch", fetchMock)
    const names = await fetchKnownNames()
    expect(names.has("zubat")).toBe(true)
    expect(names.has("ponyta")).toBe(true)
    expect(names.size).toBe(2)
  })

  it("throws a PokeCipherError on a non-ok response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({}, 500)))
    await expect(fetchKnownNames()).rejects.toBeInstanceOf(PokeCipherError)
  })

  it("throws when the payload is malformed", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ names: "nope" })))
    await expect(fetchKnownNames()).rejects.toBeInstanceOf(PokeCipherError)
  })
})
