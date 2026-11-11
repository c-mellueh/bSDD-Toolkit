import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, failOnPageErrors, openClass } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

const gops = async (request: any, id: string) =>
  (await dictionaryOf(request, id)).Classes.filter((c: any) => c.ClassType === "GroupOfProperties").map((c: any) => `${c.Code}|${c.Name}`);

test("settings: prefix and automatic creation of predefined property sets", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "Wall");

  // default: a new property set does not create a Group of Properties
  const newPset = page.getByPlaceholder("New PropertySet");
  await newPset.fill("Acoustics");
  await newPset.press("Enter");
  await expect(page.getByText("Acoustics", { exact: true }).first()).toBeVisible();
  expect(await gops(request, id)).toEqual(["Pset_Fire|Pset_Fire"]);

  // switch it on: the default prefix is EPset_
  const settings = page.getByRole("dialog").filter({ hasText: "Settings are stored in this browser only" });
  await page.getByRole("button", { name: "Settings" }).click();
  await expect(settings.getByLabel("Code prefix for predefined property sets")).toHaveValue("EPset_");
  await settings.getByRole("switch", { name: "Create a predefined property set automatically" }).evaluate((el: HTMLElement) => el.click());
  await settings.getByRole("button", { name: "Close" }).click();
  await newPset.fill("Fire Safety");
  await newPset.press("Enter");
  await expect.poll(() => gops(request, id)).toContain("EPset_Fire-Safety|Fire Safety");

  // changing the prefix offers to rename the existing groups that use the old one
  await page.getByRole("button", { name: "Settings" }).click();
  await settings.getByLabel("Code prefix for predefined property sets").fill("X_");
  await settings.getByRole("button", { name: "Close" }).click();
  const ask = page.getByRole("dialog").filter({ hasText: "Rename existing predefined property sets?" });
  await expect(ask.getByText("EPset_Fire-Safety → X_Fire-Safety")).toBeVisible();
  await ask.getByRole("button", { name: "Rename 1" }).click();
  await expect.poll(() => gops(request, id)).toEqual(["Pset_Fire|Pset_Fire", "X_Fire-Safety|Fire Safety"]);

  // declining keeps the codes
  await page.getByRole("button", { name: "Settings" }).click();
  await settings.getByLabel("Code prefix for predefined property sets").fill("Y_");
  await settings.getByRole("button", { name: "Close" }).click();
  await ask.getByRole("button", { name: "Cancel" }).click();
  expect(await gops(request, id)).toContain("X_Fire-Safety|Fire Safety");

  // the prefix is also used for the code of a new Group of Properties
  await page.goto(`/p/${id}/groups`);
  await page.getByRole("button", { name: /New group of properties/ }).first().click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel(/^Name/).fill("Thermal");
  await expect(dialog.getByLabel(/^Code/)).toHaveValue("Y_Thermal");
});
