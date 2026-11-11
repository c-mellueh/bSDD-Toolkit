import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, failOnPageErrors, openClass } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

const cpsOf = async (request: any, id: string, code: string) =>
  ((await dictionaryOf(request, id)).Classes.find((c: any) => c.Code === code).ClassProperties ?? []).map((cp: any) => `${cp.PropertySet}|${cp.PropertyCode}`).sort();

test("strict inheritance: children get and keep the parent's class properties", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "InnerWall");
  expect(await cpsOf(request, id, "InnerWall")).toEqual([]);

  // switch on in the project settings: asks, then fills Inner Wall from Wall
  await page.getByText("File", { exact: true }).first().click();
  await page.getByRole("menuitem", { name: "Project settings" }).click();
  const settings = page.getByRole("dialog").filter({ hasText: "These settings are saved with the dictionary" });
  await settings.getByRole("switch", { name: "Strict inheritance" }).evaluate((el: HTMLElement) => el.click());
  const ask = page.getByRole("dialog").filter({ hasText: "Switch on strict inheritance?" });
  await expect(ask.getByText("2 class properties are missing")).toBeVisible();
  await ask.getByRole("button", { name: "Switch on" }).click();
  await expect.poll(() => cpsOf(request, id, "InnerWall")).toEqual(["Common|Material", "Geometry|Height"]);
  await settings.getByRole("button", { name: "Close" }).click();

  // inherited rows are marked; deleting them is not possible
  const row = page.locator(".grid-table tr", { hasText: "height" }).first();
  await expect(row.getByLabel("Inherited from Wall (strict inheritance)")).toBeVisible();
  await row.click();
  await page.keyboard.press("Delete");
  await expect(page.getByText("remove it in the parent class")).toBeVisible();
  expect(await cpsOf(request, id, "InnerWall")).toContain("Geometry|Height");

  // the editor only allows values to change
  await row.dblclick();
  const editor = page.getByRole("dialog").filter({ hasText: "Property and property set can only be changed in the parent class" });
  await expect(editor).toBeVisible();
  await expect(editor.getByLabel("Property set")).toBeDisabled();
});
