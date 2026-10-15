import { afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiFailure } from "./api";
afterEach(() => {
  vi.unstubAllGlobals();
  api.clearSession();
});
describe("API boundary", () => {
  it("rejects malformed answers", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(JSON.stringify({ answer: "uncited" }), { status: 200 }),
        ),
    );
    await expect(
      api.ask({
        question: "flow",
        retrieval_mode: "bm25",
        generation_mode: "extractive",
      }),
    ).rejects.toBeInstanceOf(ApiFailure);
  });
  it("uses opaque cookies and the server CSRF token for mutations", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            user_id: "reader",
            role: "reader",
            csrf_token: "csrf",
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetch);
    await api.login("code");
    await api.logout();
    expect(fetch.mock.calls[1]?.[1]).toMatchObject({
      credentials: "include",
      headers: { "X-CSRF-Token": "csrf" },
    });
  });
});
