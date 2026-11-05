/* eslint-disable @typescript-eslint/no-explicit-any */
import { tokenHeaders } from "./state/access";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body: any,
  ) {
    super(message);
  }
}

export async function api<T = any>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const { json, ...rest } = init;
  const res = await fetch(path, {
    ...rest,
    headers: { ...(json !== undefined ? { "Content-Type": "application/json" } : {}), ...tokenHeaders(path), ...(rest.headers || {}) },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  const text = await res.text();
  let body: any = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  if (!res.ok) {
    const detail = typeof body === "object" && body ? body.detail : body;
    throw new ApiError(typeof detail === "string" ? detail : `Request failed (${res.status})`, res.status, body);
  }
  return body as T;
}

/** POST json, receive a file and trigger a browser download. Returns the export count header. */
export async function downloadFile(path: string, json?: unknown, method = "POST"): Promise<number | null> {
  const res = await fetch(path, {
    method,
    headers: { ...(json !== undefined ? { "Content-Type": "application/json" } : {}), ...tokenHeaders(path) },
    body: json !== undefined ? JSON.stringify(json) : undefined,
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) msg = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") || "";
  const match = /filename\*=UTF-8''([^;]+)/.exec(disposition) || /filename="?([^";]+)"?/.exec(disposition);
  const name = match ? decodeURIComponent(match[1]) : "download";
  saveBlob(blob, name);
  const count = res.headers.get("x-export-count");
  return count ? Number(count) : null;
}

export function saveBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

export function readFileText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file, "utf-8");
  });
}

const cache = new Map<string, Promise<any>>();
export function cached<T = any>(path: string): Promise<T> {
  if (!cache.has(path)) {
    const p = api<T>(path).catch((e) => {
      cache.delete(path);
      throw e;
    });
    cache.set(path, p);
  }
  return cache.get(path)!;
}
