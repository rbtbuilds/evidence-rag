import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "../api";
import type { DocumentSummary, JobView } from "../contracts";
import { DocumentAdmin } from "./DocumentAdmin";

const doc: DocumentSummary = {
  id: "d",
  title: "Manual",
  revision: 2,
  version_id: "v2",
  version_label: "v2",
  effective_date: "2026-10-15",
};
const job = (status: JobView["status"]): JobView => ({
  id: "j",
  status,
  error_code: status === "failed" ? "model_busy" : null,
  created_at: "2026-10-15",
  updated_at: "2026-10-15",
});
afterEach(() => vi.restoreAllMocks());

it.each(["import", "replace"] as const)(
  "recovers a failed %s draft with its original target revision",
  async (kind) => {
    vi.spyOn(api, "import").mockResolvedValue({ job_id: "j" });
    vi.spyOn(api, "replace").mockResolvedValue({ job_id: "j" });
    vi.spyOn(api, "document").mockResolvedValue({
      ...doc,
      text: "# Old\nOriginal.",
    });
    vi.spyOn(api, "job").mockResolvedValue(job("failed"));
    render(<DocumentAdmin documents={[doc]} changed={() => {}} />);
    await userEvent.click(
      screen.getByRole("button", {
        name: kind === "import" ? "New document" : "Replace Manual",
      }),
    );
    await userEvent.clear(await screen.findByLabelText("Document title"));
    await userEvent.type(
      screen.getByLabelText("Document title"),
      "Retained title",
    );
    await userEvent.clear(screen.getByLabelText("New version label"));
    await userEvent.type(screen.getByLabelText("New version label"), "v3");
    await userEvent.selectOptions(
      screen.getByLabelText("Minimum access role"),
      "maintainer",
    );
    await userEvent.clear(screen.getByLabelText("Markdown source"));
    await userEvent.type(
      screen.getByLabelText("Markdown source"),
      "# Draft\nKeep these edits.",
    );
    await userEvent.click(
      screen.getByRole("button", {
        name: kind === "import" ? "Queue import" : "Queue replacement",
      }),
    );
    await screen.findByText("Job failed / model_busy");
    await userEvent.click(screen.getByRole("button", { name: "New document" }));
    await userEvent.click(
      screen.getByRole("button", { name: "Edit/retry draft" }),
    );
    expect(screen.getByLabelText("Document title")).toHaveValue(
      "Retained title",
    );
    expect(screen.getByLabelText("Markdown source")).toHaveValue(
      "# Draft\nKeep these edits.",
    );
    expect(screen.getByLabelText("Minimum access role")).toHaveValue(
      "maintainer",
    );
    await userEvent.click(
      screen.getByRole("button", {
        name: kind === "import" ? "Queue import" : "Queue replacement",
      }),
    );
    await waitFor(() =>
      expect(
        kind === "import" ? api.import : api.replace,
      ).toHaveBeenCalledTimes(2),
    );
    if (kind === "replace")
      expect(api.replace).toHaveBeenLastCalledWith(
        "d",
        expect.objectContaining({ expected_revision: 2 }),
      );
  },
);

it("keeps the pending job accessible and blocks another submission until cancellation", async () => {
  vi.spyOn(api, "rebuild").mockResolvedValue({ job_id: "j" });
  vi.spyOn(api, "job").mockResolvedValue(job("running"));
  vi.spyOn(api, "cancelJob").mockResolvedValue(job("cancelled"));
  render(<DocumentAdmin documents={[doc]} changed={() => {}} />);
  await userEvent.click(screen.getByRole("button", { name: "Rebuild index" }));
  await screen.findByText("Job running");
  expect(screen.getByRole("button", { name: "New document" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Replace Manual" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Rebuild index" })).toBeDisabled();
  await userEvent.click(screen.getByRole("button", { name: "Cancel job" }));
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "New document" })).toBeEnabled(),
  );
  expect(api.cancelJob).toHaveBeenCalledWith("j");
});
