import { test, expect } from "@playwright/test";
import { login, ask } from "./helpers";
test("import replacement deletion and stale links use the real API", async ({
  page,
}) => {
  await login(page, "maintainer");
  await page.getByRole("button", { name: "New document", exact: true }).click();
  await page
    .getByLabel("Document title", { exact: true })
    .fill("Browser specimen manual");
  await page
    .getByLabel("Minimum access role", { exact: true })
    .selectOption("reader");
  await page
    .getByLabel("Markdown source", { exact: true })
    .fill(
      '# Browser specimen overview\nThe browser specimen display limit is 35 units.\n<img src="https://example.invalid/remote.png" alt="Untrusted image">',
    );
  await page.getByRole("button", { name: "Queue import", exact: true }).click();
  await expect(
    page.getByLabel("Indexing job").getByRole("status"),
  ).toContainText("Job succeeded");
  await ask(page, "What limit does the browser specimen allow?");
  await expect(page.getByTestId("answer")).toContainText("35 units");
  const link = page
    .getByRole("link", { name: /Browser specimen manual - v1/ })
    .first();
  const oldPath = await link.getAttribute("href");
  expect(oldPath).toBeTruthy();
  await link.click();
  await expect(page.getByLabel("Cited quotation")).toContainText("<img src=");
  await expect(page.locator("img")).toHaveCount(0);
  await page.getByRole("button", { name: "Back to answer" }).click();
  await expect(
    page.getByLabel("Indexing job").getByRole("status"),
  ).toContainText("Job succeeded");
  await page
    .getByRole("button", {
      name: "Replace Browser specimen manual",
      exact: true,
    })
    .click();
  await page.getByLabel("New version label", { exact: true }).fill("v2");
  await page
    .getByLabel("Minimum access role", { exact: true })
    .selectOption("reader");
  await page
    .getByLabel("Markdown source", { exact: true })
    .fill(
      "# Browser specimen overview\nThe browser specimen display limit is 40 units.",
    );
  await page
    .getByRole("button", { name: "Queue replacement", exact: true })
    .click();
  await expect(
    page.getByLabel("Indexing job").getByRole("status"),
  ).toContainText("Job succeeded");
  await ask(page, "What limit does the browser specimen allow?");
  await expect(page.getByTestId("answer")).toContainText("40 units");
  await expect(page.getByTestId("answer")).not.toContainText("35 units");
  expect((await page.request.get("/api" + oldPath)).status()).toBe(404);
  await page
    .getByRole("button", {
      name: "Delete Browser specimen manual",
      exact: true,
    })
    .click();
  await expect(page.getByRole("dialog")).toContainText(
    "Browser specimen manual",
  );
  await page
    .getByRole("button", { name: "Confirm delete", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Replace Browser specimen manual",
      exact: true,
    }),
  ).not.toBeVisible();
  await ask(page, "What limit does the browser specimen allow?");
  await expect(
    page.getByRole("heading", { name: "Insufficient evidence", exact: true }),
  ).toBeVisible();
  await page.goto(oldPath ?? "/");
  await expect(page.getByRole("alert")).toContainText("unavailable");
});
