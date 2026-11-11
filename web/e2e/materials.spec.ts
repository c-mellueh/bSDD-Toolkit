import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, failOnPageErrors, sampleDictionary, treeRow } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

function withMaterials() {
  const d = sampleDictionary();
  d.Classes.push(
    { Code: "Materials", Name: "Materials", ClassType: "Material" } as never,
    { Code: "Metal", Name: "Metal", ClassType: "Material", ParentClassCode: "Materials" } as never,
    { Code: "Steel", Name: "Steel", ClassType: "Material", ParentClassCode: "Metal", ClassProperties: [{ Code: "height", PropertyCode: "Height", PropertySet: "Geometry" }] } as never,
  );
  return d;
}

test("materials have their own page like classes and are not in the class tree", async ({ page, request }) => {
  const id = await createProject(request, withMaterials());
  await page.goto(`/p/${id}/classes`);
  await expect(treeRow(page, "Building")).toBeVisible();
  await expect(page.locator("[role=treeitem]", { hasText: "Steel" })).toHaveCount(0);

  await expect(page.getByRole("button", { name: "New class (Ctrl+N)" })).toBeVisible();
  // navigation entry with its count
  const nav = page.getByText("Materials", { exact: true }).first();
  await nav.click();
  await expect(page).toHaveURL(/\/materials$/);
  await expect(page.getByText("Select a material on the left")).toBeVisible();
  await expect(page.getByRole("button", { name: "New material (Ctrl+N)" })).toBeVisible();
  await expect(page.locator("[role=treeitem]", { hasText: "Building" })).toHaveCount(0);

  // hierarchy: Materials > Metal > Steel
  await treeRow(page, "Materials").click();
  await page.keyboard.press("ArrowRight");
  await treeRow(page, "Metal").click();
  await page.keyboard.press("ArrowRight");
  await treeRow(page, "Steel").click();
  await expect(page).toHaveURL(/\/materials\/Steel$/);
  await expect(page.locator(".detail-header")).toContainText("Steel");
  await expect(page.getByRole("tab", { name: /Subclasses/ })).toBeVisible();
  // class properties with property sets like a class
  await expect(page.getByText("Geometry").first()).toBeVisible();

  // a new subclass of a material is a material
  await page.goto(`/p/${id}/materials/Metal`);
  await page.getByRole("tab", { name: /Subclasses/ }).click();
  await page.getByRole("button", { name: "New subclass" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel(/^Name/).fill("Copper");
  await dialog.getByRole("button", { name: "Create" }).click();
  await expect(page).toHaveURL(/\/materials\/Copper$/);
  const d = await dictionaryOf(request, id);
  expect(d.Classes.find((c: { Code: string }) => c.Code === "Copper")).toMatchObject({ ClassType: "Material", ParentClassCode: "Metal" });
});

test("graph viewer: materials tab in the dictionary panel", async ({ page, request }) => {
  const id = await createProject(request, withMaterials());
  await page.goto(`/p/${id}/graph`);
  await page.locator(".mantine-SegmentedControl-root").getByText("Materials", { exact: true }).click();
  const panel = page.locator(".row", { hasText: "Materials" });
  await expect(panel).toBeVisible();
  await expect(page.locator(".row", { hasText: "Wall" })).toHaveCount(0);
  await panel.locator("span").first().click(); // expand
  await expect(page.locator(".row", { hasText: "Metal" })).toBeVisible();
  // own node type in the display settings
  await expect(page.locator("label").filter({ hasText: /^Material\s*\d+$/ })).toBeVisible();
});
