import { expect, test } from "@playwright/test";
import { createProject, failOnPageErrors, openClass, treeRow } from "./helpers";

test.beforeEach(({ page }) => failOnPageErrors(page));

async function makeDirty(page: import("@playwright/test").Page) {
  await page.getByRole("tab", { name: /^General/ }).click();
  await page.getByLabel("Definition").fill("UNSAVED");
}

test("leaving a page with unsaved edits asks first", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/classes`);
  await treeRow(page, "Building").click();
  await page.keyboard.press("ArrowRight");
  await treeRow(page, "Wall").click();
  await expect(page).toHaveURL(/classes\/Wall$/);
  await makeDirty(page);

  const prompt = page.getByRole("dialog").filter({ hasText: "This page has unsaved changes" });
  await treeRow(page, "Door").click();
  await expect(prompt).toBeVisible();
  await prompt.getByRole("button", { name: "Stay" }).click();
  await expect(page).toHaveURL(/classes\/Wall$/);
  await expect(page.getByLabel("Definition")).toHaveValue("UNSAVED");

  await page.getByRole("tab", { name: /^Details/ }).click(); // tabs of the same class: no prompt
  await expect(prompt).toHaveCount(0);

  await page.goBack();
  await expect(prompt).toBeVisible();
  await prompt.getByRole("button", { name: "Discard" }).click();
  await expect(page).toHaveURL(/\/classes$/); // tree clicks replace the history entry
});

test("saving clears the warning", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "Building");
  await makeDirty(page);
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Unsaved changes")).toHaveCount(0);
  await page.getByText("Properties", { exact: true }).first().click();
  await expect(page).toHaveURL(/\/properties$/);
});

test("editor popup asks before closing with unsaved edits", async ({ page, request }) => {
  const id = await createProject(request);
  await openClass(page, id, "Building");
  await page.getByRole("tab", { name: /^Subclasses/ }).click();
  await page.locator(".list-card", { hasText: "Door" }).dblclick();
  const editor = page.getByRole("dialog").filter({ hasText: "Edit class: Door" });
  await editor.getByLabel("Definition").fill("popup UNSAVED");
  await page.keyboard.press("Escape");
  const confirm = page.getByRole("dialog").filter({ hasText: "Your changes have not been saved yet" });
  await confirm.getByRole("button", { name: "Cancel" }).click();
  await expect(editor.getByLabel("Definition")).toHaveValue("popup UNSAVED");
  await page.keyboard.press("Escape");
  await confirm.getByRole("button", { name: "Discard" }).click();
  await expect(editor).toHaveCount(0);
});

test("unknown addresses show a not-found page", async ({ page }) => {
  await page.goto("/some/nonsense");
  await expect(page.getByRole("heading", { name: "Page not found" })).toBeVisible();
});
