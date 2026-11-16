import { expect, test } from "@playwright/test";

// without the acknowledged notice of the default config
test.use({ storageState: { cookies: [], origins: [] } });

test("cookie notice is shown until it is acknowledged", async ({ page }) => {
  await page.goto("/");
  const notice = page.getByRole("region", { name: "Cookie notice" });
  await expect(notice).toContainText("no cookies");
  await notice.getByRole("button", { name: "Details" }).click();
  await expect(notice).toContainText("Session storage");
  await notice.getByRole("button", { name: "OK" }).click();
  await expect(notice).toBeHidden();
  await page.reload();
  await expect(page.getByRole("heading").first()).toBeVisible();
  await expect(notice).toBeHidden();
});
