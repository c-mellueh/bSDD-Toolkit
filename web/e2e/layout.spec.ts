import { expect, test } from "@playwright/test";
import { createProject } from "./helpers";

test("collapsed sidebar: icons are centred", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}`);
  await page.getByText("Collapse sidebar").click();
  const rows = page.locator(".nav-collapsed");
  await expect(rows.first()).toBeVisible();
  const offsets = await rows.evaluateAll((els) =>
    els.map((el) => {
      const r = el.getBoundingClientRect();
      const i = el.querySelector("svg")!.getBoundingClientRect();
      return Math.abs(r.left + r.width / 2 - (i.left + i.width / 2));
    }),
  );
  expect(offsets.length).toBeGreaterThan(5);
  for (const d of offsets) expect(d).toBeLessThan(1.5);
});
