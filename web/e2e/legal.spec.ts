import { expect, test } from "@playwright/test";

test("imprint and privacy policy are linked from the start page", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Imprint" }).click();
  await expect(page).toHaveURL(/\/imprint$/);
  await expect(page.getByRole("heading", { name: "Imprint", level: 2 })).toBeVisible();
  // the test server has no operator details
  await expect(page.getByText("has not entered their details yet")).toBeVisible();
  await page.getByRole("link", { name: "Privacy policy" }).click();
  await expect(page.getByRole("heading", { name: "Privacy policy", level: 2 })).toBeVisible();
  await expect(page.getByText("sets no cookies")).toBeVisible();
  await page.getByRole("button", { name: "Back" }).click();
  await expect(page).toHaveURL(/\/imprint$/);
});

test("German addresses and texts", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("bsdd-settings", JSON.stringify({ language: "de" })));
  await page.goto("/datenschutz");
  await expect(page.getByRole("heading", { name: "Datenschutzerklärung", level: 2 })).toBeVisible();
  await expect(page.getByText("setzt keine Cookies")).toBeVisible();
});
