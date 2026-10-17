import { test, expect } from "@playwright/test";
import { isAbsolute, join, relative, resolve } from "node:path";
import type { Answer } from "../src/contracts";
import { login } from "./helpers";

test("actual local Qwen answers supported facts and refuses unsupported questions", async ({
  page: loginPage,
  browser,
}) => {
  test.skip(
    process.env.EVIDENCE_TEST_ACTUAL_GENERATION !== "1",
    "Run through the explicit leased actual-generation browser launcher.",
  );
  test.setTimeout(120000);
  await login(loginPage, "reader");
  const capture = process.env.EVIDENCE_DEMO_CAPTURE_DIR;
  if (capture) {
    const localPath = relative(resolve("../.runtime"), resolve(capture));
    if (localPath.startsWith("..") || isAbsolute(localPath) || !localPath)
      throw new Error("Demo capture must use a project runtime subdirectory.");
  }
  // Authentication happens outside the recorded context; state stays in memory.
  const context = await browser.newContext({
    storageState: await loginPage.context().storageState(),
    viewport: { width: 1280, height: 900 },
    ...(capture ? { recordVideo: { dir: capture, size: { width: 1280, height: 900 } } } : {}),
  });
  const page = await context.newPage();
  try {
    await page.goto("/");
    await expect(page.getByLabel("Execution profile")).toContainText(
      "Local models",
    );
    await page.getByLabel("Retrieval method").selectOption("bm25");
    await page.getByLabel("Answer mode").selectOption("local");
    await page
      .getByLabel("Question", { exact: true })
      .fill("What is the circulation display limit?");
    const response = page.waitForResponse(
      (value) =>
        value.url().endsWith("/api/questions") &&
        value.request().method() === "POST",
    );
    await page.getByRole("button", { name: "Ask question", exact: true }).click();
    await expect(page.getByTestId("answer")).toBeVisible({ timeout: 95000 });
    const body = (await (await response).json()) as Answer;
    expect(body.execution_profile).toBe("local");
    expect(body.generation_mode).toBe("local");
    expect(body.abstained).toBe(false);
    expect(body.answer).toContain("35");
    expect(body.citations.length).toBeGreaterThan(0);
    expect(
      body.citations.some((citation) => citation.quote.includes("35 units")),
    ).toBe(true);
    if (capture) await page.screenshot({ path: join(capture, "supported.png") });
    await page
      .getByRole("link", { name: /Circulation manual - v2/ })
      .first()
      .click();
    await expect(page.getByLabel("Cited quotation")).toContainText("35 units");
    if (capture) await page.screenshot({ path: join(capture, "citation.png") });
    await page.getByRole("button", { name: "Back to answer" }).click();
    for (const question of [
      "Which lunar alloy is used?",
      "What is the calibration marker?",
      "Identify the restricted calibration review marker.",
    ]) {
      await page.getByLabel("Question", { exact: true }).fill(question);
      const refusedResponse = page.waitForResponse(
        (value) =>
          value.url().endsWith("/api/questions") &&
          value.request().method() === "POST",
      );
      await page.getByRole("button", { name: "Ask question", exact: true }).click();
      const refused = (await (await refusedResponse).json()) as Answer;
      expect(refused.execution_profile).toBe("local");
      expect(refused.abstained).toBe(true);
      expect(refused.reason).toBe("insufficient_evidence");
      expect(refused.answer).toBe("");
      expect(refused.citations).toEqual([]);
      await expect(page.getByTestId("answer")).toContainText("Insufficient evidence");
      await expect(page.getByTestId("answer").getByRole("link")).toHaveCount(0);
      if (capture) await page.screenshot({ path: join(capture, "refusal.png") });
    }
    await page
      .getByLabel("Question", { exact: true })
      .fill("What is the circulation display limit?");
    await page.getByRole("button", { name: "Ask question", exact: true }).click();
    await expect(page.getByTestId("answer")).toContainText("35");
  } finally {
    await context.close();
  }
});
