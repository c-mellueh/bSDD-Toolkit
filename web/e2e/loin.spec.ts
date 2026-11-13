import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createProject, failOnPageErrors, sampleDictionary } from "./helpers";

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

test("export dialog: the purpose × milestone matrix selects what is exported; the dialog fits the matrix", async ({ page, request }) => {
  const purposes = ["P1", "P2", "P3"].map((name, i) => ({ guid: `p${i}`, name }));
  const milestones = ["Design", "Tender", "Construction", "Handover", "Operation"].map((name, i) => ({ guid: `m${i}`, name, date: null }));
  const k = (p: number, m: number) => `p${p}|m${m}`;
  const loin = {
    purposes,
    milestones,
    specs: { [k(0, 0)]: { guid: "s1", classes: ["Wall"], properties: {} }, [k(1, 2)]: { guid: "s2", classes: ["Wall", "Door"], properties: {} } },
    matrix: [k(0, 0), k(0, 1), k(1, 2), k(2, 4)],
  };
  const res = await request.post("/api/projects", { data: { dictionary: sampleDictionary(), extras: { loin } } });
  const id = (await res.json()).id;
  await page.setViewportSize({ width: 1600, height: 900 });
  await page.goto(`/p/${id}/export`);
  await page.getByRole("button", { name: "Configure & export" }).first().click(); // Excel
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Level of Information Need selection").check();

  // same matrix as in the LOIN editor; combinations not ticked there cannot be chosen
  await expect(dialog.locator("td[data-cell]")).toHaveCount(4);
  await expect(dialog.locator("td.unavailable")).toHaveCount(11);
  await expect(dialog.getByText("4 of 4 combinations selected")).toBeVisible();
  await dialog.getByRole("checkbox", { name: "P1 – Design" }).press("Space");
  await expect(dialog.getByText("3 of 4 combinations selected")).toBeVisible();
  // row checkbox: all usable cells of P1
  await dialog.getByRole("checkbox", { name: "P1", exact: true }).click();
  await expect(dialog.getByText("4 of 4 combinations selected")).toBeVisible();

  // the dialog is as wide as the matrix needs (wider than the old fixed size, less than the window)
  const dialogBox = (await dialog.boundingBox())!;
  const tableBox = (await dialog.locator("table.loin-matrix").boundingBox())!;
  expect(dialogBox.width).toBeGreaterThan(tableBox.width);
  expect(dialogBox.width).toBeLessThan(tableBox.width + 120);
  expect(dialogBox.width).toBeLessThan(1600);
});
