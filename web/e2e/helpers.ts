import { expect, type Page } from "@playwright/test";
export function code(role: "reader" | "maintainer"): string {
  const value =
    process.env[
      role === "reader"
        ? "EVIDENCE_TEST_READER_CODE"
        : "EVIDENCE_TEST_MAINTAINER_CODE"
    ];
  if (!value) throw new Error("Missing test launch code");
  return value;
}
export async function login(page: Page, role: "reader" | "maintainer") {
  await page.goto("/");
  await page.getByLabel("Demo access code").fill(code(role));
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByTestId("identity")).toContainText(role);
}
export async function ask(page: Page, question: string) {
  await page.getByLabel("Question", { exact: true }).fill(question);
  await page.getByRole("button", { name: "Ask question", exact: true }).click();
  await expect(page.getByTestId("answer")).toBeVisible();
}
