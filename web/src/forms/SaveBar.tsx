import { Button, Group, Paper, Text } from "@mantine/core";
import { useTranslation } from "react-i18next";

/** Sticky bar shown below inline forms while they have unsaved changes. */
export function SaveBar({ dirty, busy, invalid, onSave, onDiscard }: { dirty: boolean; busy?: boolean; invalid?: boolean; onSave: () => void; onDiscard: () => void }) {
  const { t } = useTranslation();
  if (!dirty) return null;
  return (
    <Paper className="save-bar" shadow="md" withBorder p="xs" radius="md">
      <Group justify="space-between" wrap="nowrap">
        <Text size="sm" c="dimmed">{t("Unsaved changes")}</Text>
        <Group gap="xs" wrap="nowrap">
          <Button variant="default" onClick={onDiscard} disabled={busy}>{t("Discard")}</Button>
          <Button onClick={onSave} loading={busy} disabled={invalid}>{t("Save")}</Button>
        </Group>
      </Group>
    </Paper>
  );
}

/** Snapshot helper for dirty tracking. */
export const snap = (...v: unknown[]) => JSON.stringify(v);

/* eslint-disable @typescript-eslint/no-explicit-any */
const same = (a: unknown, b: unknown) => JSON.stringify(a ?? null) === JSON.stringify(b ?? null);

/** 3-way merge for collaborative forms: fields the user did not touch take the remote value. */
export function mergeRemote(form: Record<string, any>, base: Record<string, any>, next: Record<string, any>) {
  const out: Record<string, any> = { ...form };
  for (const k of new Set([...Object.keys(base), ...Object.keys(next)])) if (same(form[k], base[k])) out[k] = next[k];
  return out;
}

/** Keys whose (cleaned) value differs from the baseline the user started editing from. */
export function changedKeys(keys: string[], data: Record<string, any>, base: Record<string, any>) {
  return keys.filter((k) => !same(data[k], base[k]));
}
export { same };
