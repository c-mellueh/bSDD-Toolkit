import { useMediaQuery } from "@mantine/hooks";
import { useEffect, useRef, useState } from "react";
import { storageGet, storageSet } from "../state/settings";

/**
 * Master/detail layout: resizable side panel + main area. On narrow screens only one of the two is shown
 * (`showDetail` decides which).
 */
export function Split({ storeKey, initial = 340, side, children, showDetail }: { storeKey: string; initial?: number; side: React.ReactNode; children: React.ReactNode; showDetail: boolean }) {
  const narrow = useMediaQuery("(max-width: 48em)");
  const [width, setWidth] = useState<number>(() => storageGet(storeKey, initial));
  const drag = useRef<{ start: number; initial: number } | null>(null);
  const widthRef = useRef(width);
  widthRef.current = width;

  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!drag.current) return;
      setWidth(Math.max(220, Math.min(window.innerWidth * 0.6, drag.current.initial + e.clientX - drag.current.start)));
    };
    const up = () => {
      if (!drag.current) return;
      drag.current = null;
      document.body.classList.remove("resizing");
      storageSet(storeKey, widthRef.current);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [storeKey]);

  if (narrow) return <div className="split-single">{showDetail ? children : side}</div>;
  return (
    <div className="split">
      <aside className="split-side" style={{ width }}>{side}</aside>
      <div
        className="split-handle"
        onPointerDown={(e) => {
          drag.current = { start: e.clientX, initial: width };
          document.body.classList.add("resizing");
          e.preventDefault();
        }}
      />
      <section className="split-main">{children}</section>
    </div>
  );
}
