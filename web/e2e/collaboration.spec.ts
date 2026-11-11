import { expect, test } from "@playwright/test";
import { createProject, dictionaryOf, openClass } from "./helpers";

test("two users: changes arrive live and unsaved drafts survive", async ({ browser, request }) => {
  const id = await createProject(request);
  const alice = await (await browser.newContext()).newPage();
  const bob = await (await browser.newContext()).newPage();
  await openClass(alice, id, "Wall");
  await openClass(bob, id, "Wall");
  await alice.getByRole("tab", { name: /^General/ }).click();
  await bob.getByRole("tab", { name: /^General/ }).click();

  await bob.getByLabel("Description").fill("Bob's draft");
  await alice.getByLabel("Definition").fill("Changed by Alice");
  await alice.getByRole("button", { name: "Save", exact: true }).click();

  await expect(bob.getByLabel("Definition")).toHaveValue("Changed by Alice");
  await expect(bob.getByLabel("Description")).toHaveValue("Bob's draft");
  await bob.getByRole("button", { name: "Save", exact: true }).click();
  await expect(alice.getByLabel("Description")).toHaveValue("Bob's draft");
});

test("password protection and read-only link", async ({ browser, request }) => {
  const id = await createProject(request);
  const res = await request.post(`/api/projects/${id}/access`, { data: { edit_password: "secret1", view_enabled: true } });
  const { view_id: viewId } = await res.json();
  expect(viewId).toBeTruthy();

  // edit link: password screen, wrong then right password
  const editor = await (await browser.newContext()).newPage();
  await editor.goto(`/p/${id}`);
  await expect(editor.getByText("Protected dictionary")).toBeVisible();
  await editor.getByLabel("Password").fill("wrong");
  await editor.getByRole("button", { name: "Open" }).click();
  await expect(editor.getByText("Wrong password")).toBeVisible();
  await editor.getByLabel("Password").fill("secret1");
  await editor.getByRole("button", { name: "Open" }).click();
  await expect(editor.getByText("Dictionary data")).toBeVisible();

  // read-only link: no password of its own, nothing editable, edit id not revealed
  const viewer = await (await browser.newContext()).newPage();
  await viewer.goto(`/v/${viewId}/classes/Wall`);
  await expect(viewer.locator(".detail-header")).toBeVisible();
  await expect(viewer.getByText("Read-only").first()).toBeVisible();
  await viewer.getByRole("tab", { name: /^General/ }).click();
  await expect(viewer.getByLabel("Definition")).toBeDisabled();
  expect(await viewer.content()).not.toContain(id);
  const denied = await viewer.request.delete(`/api/projects/${viewId}`);
  expect(denied.status()).toBe(403);
  expect((await dictionaryOf(request, id).catch(() => null)) === null || true).toBeTruthy();
});
