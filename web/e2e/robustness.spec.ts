import { expect, test } from "@playwright/test";
import { createProject } from "./helpers";

test("a crashing page shows a message and the rest keeps working", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}`);
  await expect(page.getByText("Dictionary data")).toBeVisible();
  // make the lazily loaded graph page fail to load
  await page.route(/assets\/GraphRoute-.*\.js/, (route) => route.abort());
  await page.getByText("Graph viewer", { exact: true }).click();
  await expect(page.getByText("Something went wrong")).toBeVisible();
  // navigation still works and clears the error
  await page.getByText("Properties", { exact: true }).first().click();
  await expect(page).toHaveURL(/\/properties$/);
  await expect(page.getByText("Something went wrong")).toHaveCount(0);
});

test("graph viewer on a phone: the graph gets the full width, panels are overlays", async ({ browser, request }) => {
  const id = await createProject(request);
  const page = await (await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true })).newPage();
  await page.goto(`/p/${id}/graph`);
  const canvas = page.locator("canvas");
  await expect(canvas).toBeVisible();
  expect((await canvas.boundingBox())!.width).toBeGreaterThan(380);
  await page.getByRole("button", { name: "Dictionary panel" }).click();
  await expect(page.getByText("Drag items into the graph")).toBeVisible();
  expect((await canvas.boundingBox())!.width).toBeGreaterThan(380);
  await page.getByRole("button", { name: "Display settings" }).click();
  await expect(page.getByText("Drag items into the graph")).toHaveCount(0);
  await expect(page.getByText("Node types")).toBeVisible();
});
