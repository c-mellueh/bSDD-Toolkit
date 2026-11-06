/**
 * Double-click opens an item in its editor popup (like in the graph view) – used in lists that do
 * not already show the item's details. Single clicks keep their own action; where both exist, the
 * single click waits briefly so a double click does not trigger it.
 */
import type React from "react";
import { useEffect, useRef } from "react";
import { openUi, useUi } from "../state/ui";

/** An editor popup is open: don't replace it (that would drop unsaved changes). */
const editorOpen = () => {
  const s = useUi.getState();
  return !!(s.classEditor || s.propertyEditor || s.cpEditor);
};

export function editClassPopup(code: string) {
  if (!editorOpen()) openUi({ classEditor: { code } });
}

export function editPropertyPopup(code: string) {
  if (!editorOpen()) openUi({ propertyEditor: { code } });
}

export function editClassPropertyPopup(classCode: string, code: string) {
  if (!editorOpen()) openUi({ cpEditor: { classCode, code } });
}

const DOUBLE_CLICK_MS = 230;

/**
 * Handlers for an element with a single-click action and a double-click action:
 * ``<div {...clicks(() => navigate(), () => editClassPopup(code))} />``.
 */
export function useClicks() {
  const timer = useRef<number>();
  useEffect(() => () => window.clearTimeout(timer.current), []);
  return (single?: () => void, double?: () => void) => ({
    onClick: (e: React.MouseEvent) => {
      if (!double || editorOpen()) return single?.();
      if (e.detail > 1) return; // second click of a double click
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => single?.(), DOUBLE_CLICK_MS);
    },
    onDoubleClick: (e: React.MouseEvent) => {
      if (!double || editorOpen()) return;
      e.preventDefault();
      window.clearTimeout(timer.current);
      double();
    },
  });
}
