import { test, expect } from "@playwright/test";
import { login, ask } from "./helpers";
test("privileged cache and source cannot cross an identity change", async ({
  page,
}) => {
  await login(page, "maintainer");
  await ask(page, "What is the calibration marker?");
  await expect(page.getByTestId("answer")).toContainText("MAINTAINER-CAL-7391");
  const path = await page
    .getByRole("link", { name: /Calibration manual - v2/ })
    .first()
    .getAttribute("href");
  expect(path).toBeTruthy();
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page.getByLabel("Demo access code")).toBeVisible();
  await login(page, "reader");
  await expect(page.getByTestId("answer")).not.toBeVisible();
  await ask(page, "What is the calibration marker?");
  await expect(page.locator("body")).not.toContainText("MAINTAINER-CAL-7391");
  expect(
    (
      await page.request.get(
        "/api/admin/jobs/00000000-0000-4000-8000-000000000001",
      )
    ).status(),
  ).toBe(403);
  const identity = await page.request.get("/api/session", {
    headers: { "X-User": "maintainer" },
  });
  expect(((await identity.json()) as { role: string }).role).toBe("reader");
  await page.goto(path ?? "/");
  await expect(page.getByRole("alert")).toContainText("unavailable");
  await expect(page.locator("body")).not.toContainText("MAINTAINER-CAL-7391");
});
