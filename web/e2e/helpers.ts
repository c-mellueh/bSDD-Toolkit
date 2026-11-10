import { expect, type APIRequestContext, type Page } from "@playwright/test";

/** Small made-up dictionary: Building > Wall > Inner Wall, Door; one Group of Properties. */
export function sampleDictionary() {
  return {
    OrganizationCode: "e2e",
    DictionaryCode: "sample",
    DictionaryVersion: "1.0",
    LanguageIsoCode: "en-GB",
    LanguageOnly: false,
    UseOwnUri: false,
    DictionaryName: "E2E Sample",
    Classes: [
      { Code: "Building", Name: "Building", Definition: "A building." },
      {
        Code: "Wall",
        Name: "Wall",
        ParentClassCode: "Building",
        Definition: "A vertical element.",
        ClassProperties: [
          { Code: "height", PropertyCode: "Height", PropertySet: "Geometry", IsRequired: true },
          { Code: "material", PropertyCode: "Material", PropertySet: "Common" },
        ],
      },
      { Code: "Door", Name: "Door", ParentClassCode: "Building", ClassProperties: [{ Code: "height", PropertyCode: "Height", PropertySet: "Geometry" }] },
      { Code: "InnerWall", Name: "Inner Wall", ParentClassCode: "Wall" },
      { Code: "Pset_Fire", Name: "Pset_Fire", ClassType: "GroupOfProperties", ClassProperties: [{ Code: "rating", PropertyCode: "FireRating", PropertySet: "Pset_Fire" }] },
    ],
    Properties: [
      { Code: "Height", Name: "Height", DataType: "Real", Units: ["m"] },
      { Code: "Material", Name: "Material", DataType: "String" },
      { Code: "FireRating", Name: "Fire rating", DataType: "String" },
    ],
  };
}

export async function createProject(request: APIRequestContext, dictionary: unknown = sampleDictionary()): Promise<string> {
  const res = await request.post("/api/projects", { data: { dictionary } });
  expect(res.status(), await res.text()).toBe(201);
  return (await res.json()).id;
}

export async function dictionaryOf(request: APIRequestContext, id: string) {
  return (await request.get(`/api/projects/${id}/dictionary.json`)).json();
}

/** Open a class page and wait until the project is loaded. */
export async function openClass(page: Page, id: string, code: string) {
  await page.goto(`/p/${id}/classes/${code}`);
  await expect(page.locator(".detail-header")).toBeVisible();
}

export const treeRow = (page: Page, name: string) => page.locator("[role=treeitem]", { hasText: name }).first();

/** Fail the test on uncaught page errors. */
export function failOnPageErrors(page: Page) {
  page.on("pageerror", (e) => {
    throw e;
  });
}
