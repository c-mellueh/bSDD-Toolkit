/** Drag-resizable table columns; widths are remembered per table in this browser. */
import { useCallback, useState } from "react";
import { storageGet, storageSet } from "../state/settings";

export type Width = number | string | undefined;

export function useColumnWidths(table: string) {
  const key = `bsdd-cols-${table}`;
  const [widths, setWidths] = useState<Record<string, number>>(() => storageGet(key, {}));

  const update = useCallback(
    (next: Record<string, number>) => {
      setWidths(next);
      storageSet(key, next);
    },
    [key],
  );

  /** Width for a column: the user's width, or the default. */
  const width = (col: string, fallback: Width): Width => widths[col] ?? fallback;

  /** Handle placed inside a <th data-col=…>: drag to resize, double-click to reset all widths. */
  const handle = (col: string) => (
    <span
      className="col-resize"
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => {
        e.stopPropagation();
        update({}); // back to the default layout
      }}
      onPointerDown={(e) => {
        e.preventDefault();
        e.stopPropagation();
        const th = (e.currentTarget as HTMLElement).parentElement!;
        const start = e.clientX;
        const startWidth = th.getBoundingClientRect().width;
        let latest = startWidth;
        const move = (ev: PointerEvent) => {
          latest = Math.max(40, Math.round(startWidth + ev.clientX - start));
          th.style.width = `${latest}px`;
        };
        const up = () => {
          window.removeEventListener("pointermove", move);
          window.removeEventListener("pointerup", up);
          // freeze every resizable column at its current pixel width, so the sum is exact
          const all: Record<string, number> = {};
          th.parentElement?.querySelectorAll<HTMLElement>("th[data-col]").forEach((cell) => {
            all[cell.dataset.col!] = Math.round(cell.getBoundingClientRect().width);
          });
          update({ ...all, [col]: latest });
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", up);
      }}
    />
  );

  /** Sum of the user-set widths (use as the table's min-width so the flexible column keeps room). */
  const total = Object.values(widths).reduce((a, b) => a + b, 0);

  return { width, handle, total };
}
