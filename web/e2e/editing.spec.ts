import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, failOnPageErrors, openClass, treeRow } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

test("edit a class, save, undo", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "Wall");
  await page.getByRole("tab", { name: /^General/ }).click();
  const definition = page.getByLabel("Definition");
  await definition.fill("A changed definition.");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect.poll(async () => (await dictionaryOf(request, id)).Classes.find((c: any) => c.Code === "Wall").Definition).toBe("A changed definition.");

  await page.locator(".detail-header").click();
  await page.keyboard.press("Control+z");
  await expect.poll(async () => (await dictionaryOf(request, id)).Classes.find((c: any) => c.Code === "Wall").Definition).toBe("A vertical element.");
  await expect(definition).toHaveValue("A vertical element.");
});

test("new class dialog shows no errors before typing and creates the class", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/classes`);
  await page.getByRole("button", { name: /New class/ }).first().click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("must not be empty")).toHaveCount(0);
  await dialog.getByLabel(/^Name/).fill("Roof Tile");
  await expect(dialog.getByLabel(/^Code/)).toHaveValue("Roof-Tile");
  await dialog.getByRole("button", { name: "Create" }).click();
  await expect(page).toHaveURL(/classes\/Roof-Tile$/);
  expect((await dictionaryOf(request, id)).Classes.map((c: any) => c.Code)).toContain("Roof-Tile");
});

test("class tree: filter and arrow keys", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/classes`);
  await page.getByPlaceholder(/Filter/).first().fill("inner");
  await expect(treeRow(page, "Inner Wall")).toBeVisible();
  await expect(treeRow(page, "Door")).toHaveCount(0);
  await page.keyboard.press("Escape");
  await expect(treeRow(page, "Inner Wall")).toHaveCount(0); // collapsed again

  await treeRow(page, "Building").click();
  await expect(page).toHaveURL(/classes\/Building$/);
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowDown");
  await expect(page).toHaveURL(/classes\/Wall$/);
});

test("double-click opens the editor popup in lists but not in the main tree", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "Building");
  await treeRow(page, "Building").dblclick();
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await page.getByRole("tab", { name: /^Subclasses/ }).click();
  await page.locator(".list-card", { hasText: "Door" }).dblclick();
  await expect(page.getByRole("dialog").getByText("Edit class: Door")).toBeVisible();
  await expect(page).toHaveURL(/classes\/Building$/);
});

test("property details: range preview is saved", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/properties/Height`);
  await page.getByRole("tab", { name: /^Details/ }).click();
  await page.getByLabel("inclusive (≥)").fill("0");
  await page.getByLabel("exclusive (<)").fill("100");
  await expect(page.getByText("0 ≤ x < 100")).toBeVisible();
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect.poll(async () => (await dictionaryOf(request, id)).Properties.find((p: any) => p.Code === "Height").MaxExclusive).toBe(100);
});
