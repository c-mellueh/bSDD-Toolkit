/** Purpose × milestone matrix with drag painting – used by the LOIN editor and the export dialogs. */
import { Group, Table, Text, Tooltip } from "@mantine/core";
import { IconCheck, IconMinus } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { LoinState } from "../types";

export const specKey = (p: string, m: string) => `${p}|${m}`;

export type Tri = "on" | "off" | "partial";
export const triOf = (n: number, total: number): Tri => (n === 0 ? "off" : n >= total ? "on" : "partial");

/** Square checkmark (instead of a toggle) – "partial" shows a dash. */
export function Check({ state, disabled, onClick, label, size = 22 }: { state: Tri; disabled?: boolean; onClick?: (e: React.MouseEvent) => void; label: string; size?: number }) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={state === "on" ? true : state === "partial" ? "mixed" : false}
      aria-label={label}
      disabled={disabled}
      className={`loin-check ${state}`}
      style={{ width: size, height: size }}
      onClick={onClick}
    >
      {state === "on" ? <IconCheck size={size - 6} stroke={3} /> : state === "partial" ? <IconMinus size={size - 6} stroke={3} /> : null}
    </button>
  );
}

/**
 * The matrix. ``isOn`` says which cells are ticked, ``onChange`` is called with the cells to change
 * (one call per click / drag). Cells for which ``unavailable`` returns a text cannot be ticked
 * (the text is shown as tooltip). ``extra`` renders additional content of a cell (e.g. a badge).
 */
export function LoinMatrix({
  loin,
  isOn,
  onChange,
  readOnly,
  unavailable,
  extra,
}: {
  loin: LoinState;
  isOn: (key: string) => boolean;
  onChange: (keys: string[], value: boolean) => void;
  readOnly?: boolean;
  unavailable?: (key: string) => string | undefined;
  extra?: (key: string) => React.ReactNode;
}) {
  const { t } = useTranslation();
  const purposes = loin.purposes ?? [];
  const milestones = loin.milestones ?? [];
  const usable = (k: string) => !unavailable?.(k);

  // drag painting: pressing on a cell flips it; every cell the pointer then passes over gets that
  // same value. Shown immediately, reported as one change when the button is released.
  const [paint, setPaint] = useState<{ value: boolean; keys: Set<string> } | null>(null);
  const paintRef = useRef(paint);
  paintRef.current = paint;
  const last = useRef<{ x: number; y: number } | null>(null);
  const shown = (k: string) => (paint?.keys.has(k) ? paint.value : isOn(k));
  const isOnRef = useRef(isOn);
  isOnRef.current = isOn;
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (!paint) return;
    const cellAt = (x: number, y: number) => (document.elementFromPoint(x, y) as HTMLElement | null)?.closest<HTMLElement>("[data-cell]")?.dataset.cell;
    const move = (e: PointerEvent) => {
      const cur = paintRef.current;
      if (!cur) return;
      // fast movements report only a few positions: also take every cell on the straight line
      // between the previous and this position (sampled every 6 px), plus coalesced events
      const points = (e.getCoalescedEvents?.() ?? []).map((c) => ({ x: c.clientX, y: c.clientY }));
      points.push({ x: e.clientX, y: e.clientY });
      const found = new Set<string>();
      for (const pt of points) {
        const from = last.current ?? pt;
        const steps = Math.max(1, Math.ceil(Math.hypot(pt.x - from.x, pt.y - from.y) / 6));
        for (let i = 1; i <= steps; i++) {
          const k = cellAt(from.x + ((pt.x - from.x) * i) / steps, from.y + ((pt.y - from.y) * i) / steps);
          if (k && !cur.keys.has(k)) found.add(k);
        }
        last.current = pt;
      }
      if (found.size) setPaint({ value: cur.value, keys: new Set([...cur.keys, ...found]) });
    };
    const up = () => {
      const cur = paintRef.current;
      setPaint(null);
      if (!cur) return;
      const changed = [...cur.keys].filter((k) => isOnRef.current(k) !== cur.value);
      if (changed.length) onChangeRef.current(changed, cur.value);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up, { once: true });
    window.addEventListener("pointercancel", up, { once: true });
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      window.removeEventListener("pointercancel", up);
    };
  }, [!!paint]);

  const start = (e: React.PointerEvent, k: string) => {
    if (readOnly || e.button !== 0 || !usable(k)) return;
    e.preventDefault(); // no text selection while dragging
    last.current = { x: e.clientX, y: e.clientY };
    setPaint({ value: !isOn(k), keys: new Set([k]) });
  };

  const state = (keys: string[]): Tri => {
    const list = keys.filter(usable);
    return triOf(list.filter(shown).length, list.length);
  };
  const flip = (keys: string[]) => {
    const list = keys.filter(usable);
    const value = state(list) !== "on";
    const changed = list.filter((k) => isOn(k) !== value);
    if (changed.length) onChange(changed, value);
  };
  const all = purposes.flatMap((p) => milestones.map((m) => specKey(p.guid, m.guid)));
  const none = (keys: string[]) => readOnly || !keys.some(usable);

  return (
    <div className="loin-matrix-wrap">
      <Table withTableBorder withColumnBorders className={`loin-matrix${paint ? " painting" : ""}`} verticalSpacing={6}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>
              <Group gap={8} wrap="nowrap" align="center">
                <Check state={state(all)} disabled={none(all)} onClick={() => flip(all)} label={t("All")} size={18} />
                <Text size="xs" c="dimmed" style={{ whiteSpace: "normal", lineHeight: 1.3 }}>{t("Purpose")} ↓<br />{t("Milestone")} →</Text>
              </Group>
            </Table.Th>
            {milestones.map((m) => {
              const col = purposes.map((p) => specKey(p.guid, m.guid));
              return (
                <Table.Th key={m.guid}>
                  <Group gap={8} wrap="nowrap">
                    <Check state={state(col)} disabled={none(col)} onClick={() => flip(col)} label={m.name} size={18} />
                    <div style={{ minWidth: 0 }}>
                      <Text size="sm" fw={600} truncate>{m.name}</Text>
                      {m.date && <Text size="xs" c="dimmed">{m.date.slice(0, 10)}</Text>}
                    </div>
                  </Group>
                </Table.Th>
              );
            })}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {purposes.map((p) => {
            const row = milestones.map((m) => specKey(p.guid, m.guid));
            return (
              <Table.Tr key={p.guid}>
                <Table.Th>
                  <Group gap={8} wrap="nowrap">
                    <Check state={state(row)} disabled={none(row)} onClick={() => flip(row)} label={p.name} size={18} />
                    <Text size="sm" fw={600} truncate>{p.name}</Text>
                  </Group>
                </Table.Th>
                {milestones.map((m) => {
                  const k = specKey(p.guid, m.guid);
                  const reason = unavailable?.(k);
                  const on = !reason && shown(k);
                  const editable = !readOnly && !reason;
                  return (
                    <Table.Td
                      key={m.guid}
                      data-cell={reason ? undefined : k}
                      className={`loin-cell${on ? " on" : ""}${editable ? " paintable" : ""}${reason ? " unavailable" : ""}`}
                      onPointerDown={(e) => {
                        if ((e.target as HTMLElement).closest(".loin-open")) return;
                        start(e, k);
                      }}
                    >
                      <Group gap={8} wrap="nowrap" justify="space-between">
                        {/* mouse/touch are handled by the cell (drag painting); keyboard (Space/Enter) toggles here */}
                        <Tooltip label={reason} disabled={!reason}>
                          <span style={{ display: "inline-flex" }}>
                            <Check state={on ? "on" : "off"} disabled={!editable} label={`${p.name} – ${m.name}`} onClick={(e) => { if (e.detail === 0) onChange([k], !isOn(k)); }} />
                          </span>
                        </Tooltip>
                        {extra?.(k)}
                      </Group>
                    </Table.Td>
                  );
                })}
              </Table.Tr>
            );
          })}
        </Table.Tbody>
      </Table>
    </div>
  );
}
