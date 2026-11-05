/* eslint-disable @typescript-eslint/no-explicit-any */
import type { PatchOp } from "./types";

/** Apply an RFC-6902 subset immutably (structural sharing) so React can detect changes. */
export function applyPatch<T>(doc: T, patch: PatchOp[]): T {
  let result: any = doc;
  for (const op of patch) result = applyOne(result, op);
  return result as T;
}

function unescape(token: string) {
  return token.replace(/~1/g, "/").replace(/~0/g, "~");
}

function applyOne(doc: any, op: PatchOp): any {
  const tokens = op.path === "" ? [] : op.path.slice(1).split("/").map(unescape);
  if (tokens.length === 0) return op.op === "remove" ? undefined : clone((op as any).value);
  return update(doc, tokens, 0, op);
}

function update(node: any, tokens: string[], i: number, op: PatchOp): any {
  const key = tokens[i];
  const last = i === tokens.length - 1;
  if (Array.isArray(node)) {
    const copy = node.slice();
    const index = key === "-" ? copy.length : Number(key);
    if (last) {
      if (op.op === "add") copy.splice(index, 0, clone(op.value));
      else if (op.op === "remove") copy.splice(index, 1);
      else copy[index] = clone(op.value);
    } else {
      copy[index] = update(copy[index], tokens, i + 1, op);
    }
    return copy;
  }
  if (node && typeof node === "object") {
    const copy = { ...node };
    if (last) {
      if (op.op === "remove") delete copy[key];
      else copy[key] = clone((op as any).value);
    } else {
      copy[key] = update(copy[key], tokens, i + 1, op);
    }
    return copy;
  }
  throw new Error(`Cannot apply patch at ${tokens.slice(0, i + 1).join("/")}`);
}

function clone<V>(value: V): V {
  return value === undefined ? value : (JSON.parse(JSON.stringify(value)) as V);
}
