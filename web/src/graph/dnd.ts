/** Native drag & drop of dictionary items into the graph viewer (works across browser windows). */
import type React from "react";

export const GRAPH_MIME = "application/x-bsdd-graph-nodes";

export function setGraphDrag(e: React.DragEvent, ids: string[]) {
  if (!ids.length) return;
  e.dataTransfer.setData(GRAPH_MIME, JSON.stringify(ids));
  e.dataTransfer.effectAllowed = "copyMove";
}

export const hasGraphDrag = (e: React.DragEvent) => Array.from(e.dataTransfer.types).includes(GRAPH_MIME);

export function readGraphDrag(e: React.DragEvent): string[] {
  try {
    const v = JSON.parse(e.dataTransfer.getData(GRAPH_MIME) || "[]");
    return Array.isArray(v) ? v.filter((x) => typeof x === "string") : [];
  } catch {
    return [];
  }
}
