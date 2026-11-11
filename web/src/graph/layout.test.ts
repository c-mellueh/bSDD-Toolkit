import { describe, expect, it } from "vitest";
import { buildIndexes } from "../model";
import type { Doc } from "../types";
import { normalizeTreeOrder, TREE_EDGE_KINDS, treeLayout } from "./layout";
import { edgesBetween, type EdgeKind } from "./model";

const uri = (code: string) => `https://identifier.buildingsmart.org/uri/t/d/1.0/class/${code}`;

const doc = {
  extras: {},
  dictionary: {
    OrganizationCode: "t",
    DictionaryCode: "d",
    DictionaryVersion: "1.0",
    LanguageIsoCode: "en-GB",
    LanguageOnly: false,
    UseOwnUri: false,
    DictionaryName: "d",
    Classes: [
      { Code: "Building", Name: "Building" },
      {
        Code: "Wall",
        Name: "Wall",
        ParentClassCode: "Building",
        ClassRelations: [{ RelationType: "HasReference", RelatedClassUri: uri("EPset_Fire") }],
        ClassProperties: [{ Code: "rating", PropertyCode: "FireRating", PropertySet: "EPset_Fire" }],
      },
      { Code: "EPset_Fire", Name: "EPset_Fire", ClassType: "GroupOfProperties", ClassProperties: [{ Code: "rating", PropertyCode: "FireRating", PropertySet: "EPset_Fire" }] },
    ],
    Properties: [{ Code: "FireRating", Name: "Fire rating", DataType: "String" }],
  },
} as unknown as Doc;

const idx = buildIndexes(doc);
const ids = ["c:Building", "c:Wall", "c:EPset_Fire", "p:FireRating"];
const nodes = ids.map((id) => ({ id, w: 40, h: 20 }));
const edges = edgesBetween(doc, idx, new Set(ids));

/** depth (level) of every node in a top-down tree */
function levels(order: EdgeKind[], hidden: EdgeKind[] = []) {
  const pos = treeLayout(nodes, edges.filter((e) => !hidden.includes(e.kind)), "TB", order);
  const ys = [...new Set(ids.map((id) => pos.get(id)!.y))].sort((a, b) => a - b);
  return Object.fromEntries(ids.map((id) => [id, ys.indexOf(pos.get(id)!.y)]));
}

describe("class property edges", () => {
  it("are told apart for classes and groups of properties", () => {
    const kinds = edges.filter((e) => e.target === "p:FireRating").map((e) => [e.source, e.kind]);
    expect(kinds).toEqual(
      expect.arrayContaining([
        ["c:Wall", "ClassProperty"],
        ["c:EPset_Fire", "GopProperty"],
      ]),
    );
  });
});

describe("tree layout order", () => {
  it("builds Class > Group of Properties > Property", () => {
    const order = normalizeTreeOrder(["ParentClassCode", "HasReference", "GopProperty"]);
    expect(levels(order, ["ClassProperty"])).toEqual({ "c:Building": 0, "c:Wall": 1, "c:EPset_Fire": 2, "p:FireRating": 3 });
  });

  it("the earlier edge type wins", () => {
    // the class property of Wall places the property directly under Wall
    const order = normalizeTreeOrder(["ParentClassCode", "ClassProperty", "HasReference", "GopProperty"]);
    expect(levels(order)["p:FireRating"]).toBe(2);
  });

  it("a node that is already in the tree of an earlier edge type is not moved", () => {
    // the group of properties heads its own tree (with its property) and is not moved under Wall
    const order = normalizeTreeOrder(["GopProperty", "ParentClassCode", "HasReference"]);
    const l = levels(order, ["ClassProperty"]);
    expect(l["c:EPset_Fire"]).toBe(0);
    expect(l["p:FireRating"]).toBe(1);
    expect(l["c:Wall"]).toBe(1);
  });

  it("completes saved orders with unknown and new kinds", () => {
    const order = normalizeTreeOrder(["HasReference", "Bogus", "HasReference"]);
    expect(order[0]).toBe("HasReference");
    expect([...order].sort()).toEqual([...TREE_EDGE_KINDS].sort());
  });
});
