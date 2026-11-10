/**
 * Registry of forms with unsaved changes. "page" forms (inline on a page) block navigation,
 * "popup" forms block closing their dialog; both warn before the browser tab is closed.
 */
import { useEffect, useId, useRef } from "react";

export type UnsavedScope = "page" | "popup";

const dirty = new Map<string, UnsavedScope>();

export const hasUnsaved = (scope?: UnsavedScope) => (scope ? [...dirty.values()].includes(scope) : dirty.size > 0);

/** Forget all registered changes of a scope (after the user chose to discard them). */
export function forgetUnsaved(scope: UnsavedScope) {
  for (const [k, v] of dirty) if (v === scope) dirty.delete(k);
}

/**
 * Register a form's dirty state. Returns ``release()``: call it right after a successful save,
 * before navigating or closing, so the just-saved form does not trigger a warning.
 */
export function useUnsaved(isDirty: boolean, scope: UnsavedScope): () => void {
  const id = useId();
  const released = useRef(false);
  useEffect(() => {
    if (isDirty && !released.current) dirty.set(id, scope);
    else dirty.delete(id);
    if (!isDirty) released.current = false;
    return () => {
      dirty.delete(id);
    };
  }, [id, isDirty, scope]);
  return () => {
    released.current = true;
    dirty.delete(id);
  };
}

if (typeof window !== "undefined") {
  window.addEventListener("beforeunload", (e) => {
    if (!hasUnsaved()) return;
    e.preventDefault();
    e.returnValue = ""; // browsers show their own "leave site?" text
  });
}
