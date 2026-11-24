// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import Page from "@/app/page"

/**
 * The page's own failure modes: the two the cipher can hand it, and the one it
 * can cause itself.
 *
 * These run against a stubbed API rather than a live server so the suite stays
 * hermetic; the Python half is covered by test_app.py. jsdom is enough because
 * nothing here measures layout — the assertions are about what a user is told.
 */

// React 19 reads this flag to decide whether act() warnings apply to a render
// it did not start. The tests are the only driver here, so it is always true.
;(
  globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }
).IS_REACT_ACT_ENVIRONMENT = true

const NAMES = ["Zubat", "Weepinbell", "Ponyta"]

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response
}

/** A canned reply: the JSON envelope plus the status the server would send. */
interface Reply {
  body: unknown
  status?: number
}

interface ApiStub {
  names?: () => Promise<Response>
  encode?: (text: string) => Reply
  decode?: (text: string) => Reply
}

function stubApi({ names, encode, decode }: ApiStub): void {
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.endsWith("/api/names")) {
      return names ? names() : Promise.resolve(jsonResponse({ names: NAMES }))
    }
    const { text = "" } = JSON.parse(String(init?.body ?? "{}")) as {
      text?: string
    }
    const reply = url.endsWith("/api/encode")
      ? (encode?.(text) ?? { body: { result: "Zubat" } })
      : url.endsWith("/api/decode")
        ? (decode?.(text) ?? { body: { result: "H" } })
        : { body: { error: "no such route" }, status: 404 }
    return Promise.resolve(jsonResponse(reply.body, reply.status ?? 200))
  })
}

const resultCard = () => document.querySelector(".min-h-20") as HTMLElement
const statusLine = () =>
  document.querySelector('[aria-live="polite"]') as HTMLElement
const budgetWarning = () => screen.queryByText(/search budget/)

/** Type into the textarea and press a button by its accessible name. */
async function useTool(text: string, button: RegExp) {
  const user = userEvent.setup()
  render(<Page />)
  const box = screen.getByRole("textbox") as HTMLTextAreaElement
  await user.click(box)
  await user.paste(text)
  await waitFor(() => expect(box.value).toBe(text))
  await user.click(screen.getByRole("button", { name: button }))
  return { user, box }
}

beforeEach(() => stubApi({}))
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe("the tool's failure modes", () => {
  it("warns when the decode was only best-effort", async () => {
    stubApi({
      decode: () => ({ body: { result: "hello wnrld", truncated: true } }),
    })
    await useTool("Zubat", /^Decode$/)

    await waitFor(() =>
      expect(resultCard().textContent).toContain("hello wnrld")
    )
    expect(budgetWarning()).not.toBeNull()
    expect(budgetWarning()?.getAttribute("role")).toBe("status")
  })

  it("stays quiet when the decode was exact", async () => {
    stubApi({ decode: () => ({ body: { result: "Hello W[n,o]rld!" } }) })
    await useTool("Zubat", /^Decode$/)

    await waitFor(() =>
      expect(resultCard().textContent).toContain("Hello W[n,o]rld!")
    )
    expect(budgetWarning()).toBeNull()
  })

  it("blames the service, not the input, when the name list never loads", async () => {
    // The page logs the failure as well as showing it; silence the log here so a
    // failing fetch is visible in the output only when the assertion fails.
    const logged = vi.spyOn(console, "error").mockImplementation(() => {})
    stubApi({ names: () => Promise.reject(new Error("offline")) })

    await useTool("Zubat", /^Encode$/)

    await waitFor(() =>
      expect(statusLine().textContent).toContain(
        "Could not load the Pokémon list"
      )
    )
    expect(statusLine().textContent).not.toContain("Not Pokémon names")
    expect(logged).toHaveBeenCalled()
    logged.mockRestore()
  })

  it("surfaces a server error verbatim instead of a generic one", async () => {
    const message = "Field 'text' exceeds 4000 characters."
    stubApi({ encode: () => ({ body: { error: message }, status: 413 }) })

    await useTool("Zubat", /^Encode$/)

    await waitFor(() =>
      expect(screen.getByRole("alert").textContent).toContain(message)
    )
    // A rejected encode leaves the previous result alone rather than clearing it.
    expect(resultCard().textContent).toContain("will appear here")
  })
})
