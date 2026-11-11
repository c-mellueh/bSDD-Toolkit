import { expect, test } from "@playwright/test";
import { createProject, failOnPageErrors } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

test("graph: class properties of classes and of groups of properties are separate edge types; the tree order can be changed", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/graph`);
  await page.getByRole("button", { name: "Add…" }).click();
  await page.getByRole("menuitem", { name: "All groups of properties" }).click();
  await page.getByRole("button", { name: "Add…" }).click();
  await page.getByRole("menuitem", { name: "All properties" }).click();

  // two toggles, the group of properties edge is counted separately
  const gopToggle = page.locator("label", { hasText: "ClassProperty (group of properties)" });
  // Wall (2) and Door (1) have class properties of their own
  await expect(page.locator("label", { hasText: "ClassProperty (class)" })).toHaveText(/ClassProperty \(class\)\s*3/);
  await expect(gopToggle).toHaveText(/\(group of properties\)\s*1/);

  // order: move HasReference to the top
  const rows = page.locator("[data-tree-kind]");
  await expect(rows.first()).toHaveAttribute("data-tree-kind", "ParentClassCode");
  for (let i = 0; i < 9; i++) await page.getByRole("button", { name: "Move HasReference up" }).click();
  await expect(rows.first()).toHaveAttribute("data-tree-kind", "HasReference");
  await expect(page.getByRole("button", { name: "Move HasReference up" })).toBeDisabled();

  // hiding an edge type marks it in the order list
  await gopToggle.click();
  await expect(page.locator('[data-tree-kind="GopProperty"]')).toContainText("(hidden)");

  // kept after a reload
  await page.waitForTimeout(3200);
  await page.reload();
  await expect(page.locator("[data-tree-kind]").first()).toHaveAttribute("data-tree-kind", "HasReference");

  await page.getByRole("button", { name: "Default order" }).click();
  await expect(page.locator("[data-tree-kind]").first()).toHaveAttribute("data-tree-kind", "ParentClassCode");
  await page.getByRole("button", { name: "Tree (top → bottom)" }).click();
});
