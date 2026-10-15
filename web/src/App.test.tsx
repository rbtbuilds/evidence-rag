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
