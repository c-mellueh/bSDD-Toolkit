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

type Pt = { id: string; x: number; y: number };
const positions = (page: import("@playwright/test").Page) =>
  page.evaluate(() => (window as unknown as { __bsddGraph: { nodes: () => Pt[] } }).__bsddGraph.nodes().map((n) => ({ id: n.id, x: n.x, y: n.y })));

test("graph: with physics paused, adding or dropping nodes does not move the other nodes", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/graph`);
  await expect(page.getByRole("button", { name: "Run physics (Space)" })).toBeVisible(); // paused
  // wait until the first layout has come to rest
  let before: Pt[] = [];
  await expect(async () => {
    const a = await positions(page);
    await page.waitForTimeout(400);
    before = await positions(page);
    expect(a.length).toBeGreaterThan(0);
    expect(before).toEqual(a);
  }).toPass();

  // drop a property from the dictionary panel onto the graph
  const box = (await page.locator("canvas").boundingBox())!;
  await page.evaluate(({ x, y }) => {
    const dt = new DataTransfer();
    dt.setData("application/x-bsdd-graph-nodes", JSON.stringify(["p:FireRating"]));
    const target = document.elementFromPoint(x, y)!;
    for (const type of ["dragenter", "dragover", "drop"]) target.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt, clientX: x, clientY: y }));
  }, { x: box.x + box.width - 60, y: box.y + 60 });
  // and add more nodes through the menu
  await page.getByRole("button", { name: "Add…" }).click();
  await page.getByRole("menuitem", { name: "All groups of properties" }).click();
  await page.waitForTimeout(1500);

  const after = await positions(page);
  expect(after.map((n) => n.id)).toEqual(expect.arrayContaining(["p:FireRating", "c:Pset_Fire"]));
  for (const p of before) {
    const q = after.find((n) => n.id === p.id)!;
    expect([q.x, q.y], p.id).toEqual([p.x, p.y]);
  }
});

test("graph: the dictionary panel can be resized and keeps its width", async ({ page, request }) => {
  const id = await createProject(request);
  await page.goto(`/p/${id}/graph`);
  const handle = page.getByRole("separator", { name: "Resize dictionary panel" });
  const panelWidth = () => handle.evaluate((el) => el.previousElementSibling!.getBoundingClientRect().width);
  const canvasWidth = async () => (await page.locator("canvas").boundingBox())!.width;
  await expect.poll(panelWidth).toBe(260);
  const before = await canvasWidth();
  const box = (await handle.boundingBox())!;
  await page.mouse.move(box.x + 2, box.y + 100);
  await page.mouse.down();
  await page.mouse.move(box.x + 152, box.y + 100, { steps: 5 });
  await page.mouse.up();
  await expect.poll(panelWidth).toBe(410);
  await expect.poll(canvasWidth).toBeLessThan(before - 100); // the graph gets narrower

  await page.reload();
  await expect.poll(panelWidth).toBe(410);
  await handle.focus();
  await page.keyboard.press("ArrowLeft");
  await expect.poll(panelWidth).toBe(390);
  await handle.dblclick();
  await expect.poll(panelWidth).toBe(260);
});
