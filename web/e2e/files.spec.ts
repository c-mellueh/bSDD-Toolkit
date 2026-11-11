import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, failOnPageErrors, sampleDictionary } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

test("upload of a bSDD website export ([null] lists, missing class property codes)", async ({ page }) => {
  const data: any = sampleDictionary();
  data.Classes[1].ClassProperties[0].Code = null;
  data.Classes[0].ReplacedObjectCodes = [null];
  data.Properties[0].Units = [null];
  await page.goto("/");
  await page.locator("input[type=file]").first().setInputFiles({ name: "export.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(data)) });
  await expect(page).toHaveURL(/\/p\/[\w-]+$/);
  await expect(page.getByRole("heading", { name: "E2E Sample" })).toBeVisible();
  const id = page.url().split("/p/")[1];
  const saved = await dictionaryOf(page.request, id);
  expect(saved.Classes[1].ClassProperties[0].Code).toBe("Height");
});

test("version history: save, restore, undo; delete dictionary", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/classes/Door`);
  await expect(page.locator(".detail-header")).toBeVisible();
  const openVersions = async () => {
    await page.getByText("File", { exact: true }).first().click();
    await page.getByRole("menuitem", { name: "Version history" }).click();
  };
  const codes = async () => (await dictionaryOf(request, id)).Classes.map((c: any) => c.Code);

  await openVersions();
  const versions = page.getByRole("dialog").filter({ hasText: "Version history" });
  await versions.getByRole("button", { name: "Save version now" }).click();
  await expect(versions.locator("tbody tr")).toHaveCount(1);
  await page.keyboard.press("Escape");

  await request.get(`/api/projects/${id}`); // keep-alive
  await page.locator(".detail-header").getByRole("button").last().click();
  await page.getByRole("menuitem", { name: /Delete/ }).click();
  await page.getByRole("dialog").getByRole("button", { name: /^Delete/ }).click();
  await expect.poll(codes).not.toContain("Door");

  await openVersions();
  await versions.getByRole("button", { name: "Restore", exact: true }).first().click();
  await page.getByRole("dialog").filter({ hasText: "Replace the current dictionary" }).getByRole("button", { name: "Restore", exact: true }).click();
  await expect.poll(codes).toContain("Door");

  await page.locator("header").first().click({ position: { x: 5, y: 5 } });
  await page.keyboard.press("Control+z");
  await expect.poll(codes).not.toContain("Door");

  // delete: wrong name does nothing, the right name deletes
  const del = async (name: string) => {
    await page.getByText("File", { exact: true }).first().click();
    await page.getByRole("menuitem", { name: /Delete dictionary/ }).click();
    const input = page.getByRole("dialog").getByRole("textbox");
    await input.fill(name);
    await input.press("Enter");
  };
  await del("something else");
  await expect(page.getByText("The name does not match")).toBeVisible();
  expect((await request.get(`/api/projects/${id}`)).status()).toBe(200);
  await del("E2E Sample");
  await expect(page).toHaveURL(/\/$/);
  expect((await request.get(`/api/projects/${id}`)).status()).toBe(404);
});
