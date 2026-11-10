import { defineConfig } from "@playwright/test";

// End-to-end tests against the real server (FastAPI + the built frontend in ./dist).
//   npm run build && npm run e2e
// E2E_PYTHON selects the Python that has bsdd_web's dependencies (default: "python").
const PORT = Number(process.env.E2E_PORT ?? 8797);

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 8_000 },
  fullyParallel: true, // every test creates its own dictionary
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    viewport: { width: 1440, height: 900 },
    locale: "en-US",
    trace: "retain-on-failure",
  },
  webServer: {
    command: `${process.env.E2E_PYTHON ?? "python"} -m bsdd_web --host 127.0.0.1 --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/api/health`,
    reuseExistingServer: false,
    timeout: 60_000,
    env: {
      PYTHONPATH: "../src",
      STATIC_DIR: "dist",
      DATA_DIR: ".e2e-data",
      OFFLINE: "1",
      SAVE_DELAY: "0.2",
    },
  },
});
