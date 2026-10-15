import { test, expect } from "@playwright/test";
import { login, ask } from "./helpers";
test("unsupported question abstains and invalid code has an accessible error", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Demo access code").fill("deliberately-invalid");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("alert")).toBeFocused();
  await expect(page.getByLabel("Demo access code")).toHaveAttribute(
    "aria-invalid",
    "true",
  );
  await login(page, "reader");
  await ask(page, "Which lunar alloy is used?");
  await expect(
    page.getByRole("heading", { name: "Insufficient evidence", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("No supporting passages.", { exact: true }),
  ).toBeVisible();
});
