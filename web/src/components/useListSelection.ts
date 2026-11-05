import { useCallback, useRef, useState } from "react";

/** Multi selection with ctrl/shift click semantics for simple lists/tables. */
export function useListSelection(keys: string[]) {
  const [selected, setSelected] = useState<string[]>([]);
  const anchor = useRef<string | null>(null);
  const click = useCallback(
    (key: string, e: { ctrlKey: boolean; metaKey: boolean; shiftKey: boolean }) => {
      if (e.shiftKey && anchor.current && keys.includes(anchor.current)) {
        const a = keys.indexOf(anchor.current);
        const b = keys.indexOf(key);
        const [lo, hi] = a < b ? [a, b] : [b, a];
        setSelected(keys.slice(lo, hi + 1));
        return;
      }
      if (e.ctrlKey || e.metaKey) {
        setSelected((s) => (s.includes(key) ? s.filter((x) => x !== key) : [...s, key]));
      } else {
        setSelected([key]);
      }
      anchor.current = key;
    },
    [keys],
  );
  const ensure = useCallback((key: string) => setSelected((s) => (s.includes(key) ? s : [key])), []);
  const valid = selected.filter((k) => keys.includes(k));
  return { selected: valid, setSelected, click, ensure };
}
