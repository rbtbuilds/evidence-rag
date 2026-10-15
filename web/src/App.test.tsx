import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { StatusNotice, ErrorNotice } from "./components/StatusNotice";
import { SessionForm } from "./components/SessionForm";
import { AnswerPanel } from "./components/AnswerPanel";

describe("evidence workbench", () => {
  it("labels fixture doubles visibly", () => {
    render(<StatusNotice profile="fixture" />);
    expect(screen.getByText(/dense.*test doubles/i)).toBeVisible();
  });
  it("focuses announced errors", () => {
    render(<ErrorNotice message="Corpus changed. Ask again." />);
    expect(screen.getByRole("alert")).toHaveFocus();
  });
  it("submits a launch code through an accessible form", async () => {
    const login = vi.fn();
    render(<SessionForm login={login} busy={false} />);
    await userEvent.type(
      screen.getByLabelText("Demo access code"),
      "example-code",
    );
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(login).toHaveBeenCalledWith("example-code");
  });
  it("activates a citation by identifier", async () => {
    const open = vi.fn();
    render(
      <AnswerPanel
        answer={{
          request_id: "q",
          execution_profile: "fixture",
          retrieval_mode: "bm25",
          generation_mode: "extractive",
          answer: "35 units [1]",
          abstained: false,
          reason: null,
          timings_ms: {},
          citations: [
            {
              chunk_id: "c",
              document_id: "d",
              version_id: "v",
              title: "Circulation",
              version_label: "v2",
              effective_date: "2026-10-15",
              section_id: "flow",
              start_char: 0,
              end_char: 2,
              quote: "35",
            },
          ],
        }}
        open={open}
      />,
    );
    await userEvent.click(
      screen.getByRole("link", { name: /Circulation.*v2/ }),
    );
    expect(open).toHaveBeenCalledWith("c");
  });
});

import { CitationViewer } from "./components/CitationViewer";
import { api } from "./api";
it("highlights Python Unicode code point offsets after an emoji", async () => {
  const quote = "café 35 units.";
  const mock = vi.spyOn(api, "citation").mockResolvedValue({
    chunk_id: "c",
    document_id: "d",
    version_id: "v",
    title: "Flow",
    version_label: "v2",
    effective_date: "2026-10-15",
    section_id: "flow",
    start_char: 9,
    end_char: 23,
    quote,
    section_text: "# Flow\n🟣 café 35 units.",
    section_start_char: 0,
    highlight_start: 9,
    highlight_end: 23,
  });
  try {
    render(<CitationViewer id="c" back={() => {}} />);
    expect((await screen.findByLabelText("Cited quotation")).textContent).toBe(
      quote,
    );
  } finally {
    mock.mockRestore();
  }
});

import App from "./App";
import { waitFor } from "@testing-library/react";
it("does not allow another sign in until sign out finishes", async () => {
  vi.spyOn(api, "health").mockResolvedValue({
    status: "ok",
    execution_profile: "fixture",
  });
  vi.spyOn(api, "session").mockResolvedValue({
    user_id: "maintainer",
    role: "maintainer",
    csrf_token: "token",
  });
  vi.spyOn(api, "documents").mockResolvedValue([]);
  let finish: () => void = () => {
    throw new Error("Sign out was not started");
  };
  vi.spyOn(api, "logout").mockImplementation(
    () =>
      new Promise<void>((resolve) => {
        finish = resolve;
      }),
  );
  try {
    render(<App />);
    await userEvent.click(
      await screen.findByRole("button", { name: "Sign out" }),
    );
    expect(screen.getByRole("button", { name: "Sign in" })).toBeDisabled();
    finish();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Sign in" })).toBeEnabled(),
    );
  } finally {
    finish();
    vi.restoreAllMocks();
  }
});
