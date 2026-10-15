import { defineConfig } from "@playwright/test";
for (const name of [
  "EVIDENCE_TEST_READER_CODE",
  "EVIDENCE_TEST_MAINTAINER_CODE",
]) {
  if (!process.env[name])
    throw new Error(
      `Missing ${name}: run npm run test:e2e through the owned API launcher.`,
    );
}
export default defineConfig({
  testDir: "./e2e",
  timeout: 45000,
  workers: 1,
  fullyParallel: false,
  use: {
    baseURL: "http://127.0.0.1:5115",
    trace: "off",
    video: "off",
    screenshot: "off",
  },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5115",
    reuseExistingServer: false,
    timeout: 30000,
  },
  reporter: "list",
});
