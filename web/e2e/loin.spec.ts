import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createProject, failOnPageErrors } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

test("purpose × milestone matrix: click, drag, export of empty combinations", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/loin`);
  await page.getByRole("tab", { name: /Purposes, milestones/ }).click();
  const add = async (title: string, name: string) => {
    await page.getByText(title, { exact: true }).locator("xpath=ancestor::div[1]").getByRole("button", { name: "Add" }).click();
    const input = page.getByRole("dialog").getByRole("textbox");
    await input.fill(name);
    await input.press("Enter");
    await expect(page.getByText(name, { exact: true }).filter({ visible: true }).first()).toBeVisible();
  };
  await add("Milestones", "MS 2");
  await add("Milestones", "MS 3");
  await add("Purposes", "PP 2");

  await page.getByRole("tab", { name: /matrix/ }).click();
  const cells = page.locator("td[data-cell]");
  await expect(cells).toHaveCount(6);
  await expect(page.getByText("0 of 6 combinations ticked")).toBeVisible();

  // one fast drag across the first row ticks all three cells
  const first = (await cells.nth(0).boundingBox())!;
  const last = (await cells.nth(2).boundingBox())!;
  await page.mouse.move(first.x + 20, first.y + first.height / 2);
  await page.mouse.down();
  await page.mouse.move(last.x + 20, last.y + last.height / 2, { steps: 1 });
  await page.mouse.up();
  await expect(page.getByText("3 of 6 combinations ticked")).toBeVisible();

  // a single click toggles one cell off again
  await page.mouse.click(first.x + 20, first.y + first.height / 2);
  await expect(page.getByText("2 of 6 combinations ticked")).toBeVisible();

  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export XML" }).click();
  const xml = readFileSync((await (await download).path())!, "utf8");
  const names = [...xml.matchAll(/Specification name="([^"]+)"/g)].map((m) => m[1]);
  expect(names).toEqual(["PP 1 – MS 2", "PP 1 – MS 3"]);
  expect(xml).not.toContain("SpecificationPerObjectType"); // empty combinations
});

test("property set tree lists all property sets and includes their classes", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/loin`);
  const psets = page.locator(".loin-panel").nth(2);
  await expect(psets.getByText("Geometry")).toBeVisible();
  await expect(psets.getByText("Common")).toBeVisible();
  await psets.locator(".loin-group-row", { hasText: "Geometry" }).getByRole("switch").evaluate((el: HTMLElement) => el.click());
  // both classes that have the "Geometry" set are now included
  await expect(page.locator(".loin-panel").first().getByText("2 included", { exact: false })).toBeVisible();
});
