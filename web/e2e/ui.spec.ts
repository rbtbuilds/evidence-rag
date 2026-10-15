import { test, expect } from "@playwright/test";
import { login, ask } from "./helpers";
test("reader inspects a current passage across both themes and viewport sizes", async ({
  page,
}) => {
  await login(page, "reader");
  await ask(page, "What is the circulation display limit?");
  await expect(page.getByTestId("answer")).toContainText("35 units");
  for (const theme of ["light", "dark"]) {
    await page.getByLabel("Theme", { exact: true }).selectOption(theme);
    const contrast = await page.evaluate(() => {
      const luminance = (rgb: string) => {
        const channels = (rgb.match(/[\d.]+/g) ?? [])
          .slice(0, 3)
          .map(Number)
          .map((v) => v / 255)
          .map((v) =>
            v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4,
          );
        return channels.reduce(
          (sum, v, i) => sum + v * ([0.2126, 0.7152, 0.0722][i] ?? 0),
          0,
        );
      };
      return Math.min(
        ...Array.from(document.querySelectorAll<HTMLButtonElement>("button"))
          .filter((button) => !button.disabled && button.checkVisibility())
          .map((button) => {
            const style = getComputedStyle(button);
            const a = luminance(style.color),
              b = luminance(style.backgroundColor);
            return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
          }),
      );
    });
    expect(contrast).toBeGreaterThanOrEqual(4.5);
    for (const width of [360, 900, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
      await page.screenshot({
        path: `../.runtime/ui-${theme}-${width}.png`,
        fullPage: true,
      });
    }
  }
  await page
    .getByRole("link", { name: /Circulation manual - v2/ })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Circulation manual", exact: true }),
  ).toBeFocused();
  await expect(page.getByLabel("Cited quotation")).toContainText("35 units");
  await page.getByRole("button", { name: "Back to answer" }).click();
  await expect(
    page.getByRole("link", { name: /Circulation manual - v2/ }).first(),
  ).toBeFocused();
});
test("delete confirmation supports Escape and restores keyboard focus", async ({
  page,
}) => {
  await login(page, "maintainer");
  const opener = page.getByRole("button", {
    name: "Delete Circulation manual",
    exact: true,
  });
  await opener.click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(opener).toBeFocused();
});
