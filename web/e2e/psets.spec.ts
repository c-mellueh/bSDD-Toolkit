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

  // switch it on with a custom prefix
  await page.getByRole("button", { name: "Settings" }).click();
  const settings = page.getByRole("dialog");
  await settings.getByLabel("Code prefix for predefined property sets").fill("EPset_");
  await settings.getByRole("switch", { name: "Create a predefined property set automatically" }).evaluate((el: HTMLElement) => el.click());
  await settings.getByRole("button", { name: "Close" }).click();

  await newPset.fill("Fire Safety");
  await newPset.press("Enter");
  await expect.poll(() => gops(request, id)).toContain("EPset_Fire-Safety|Fire Safety");

  // the prefix is also used for the code of a new Group of Properties
  await page.goto(`/p/${id}/groups`);
  await page.getByRole("button", { name: /New group of properties/ }).first().click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel(/^Name/).fill("Thermal");
  await expect(dialog.getByLabel(/^Code/)).toHaveValue("EPset_Thermal");
});
