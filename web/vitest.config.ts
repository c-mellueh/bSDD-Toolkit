import { defineConfig } from "vitest/config";

// unit tests only; the Playwright browser tests in e2e/ run with `npm run e2e`
export default defineConfig({
  test: { include: ["src/**/*.test.ts"] },
});
