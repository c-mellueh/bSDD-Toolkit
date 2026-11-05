import { Button, Group, List, ScrollArea, Stack, Text, TextInput } from "@mantine/core";
import { Toggle } from "./Toggle";
import { modals } from "@mantine/modals";
import { useState } from "react";
import i18n from "../i18n";

const t = (s: string, o?: Record<string, unknown>) => i18n.t(s, o);

export function askConfirm(title: string, message: string, confirmLabel = t("OK"), danger = false): Promise<boolean> {
  return new Promise((resolve) => {
    modals.openConfirmModal({
      title,
      children: <Text size="sm">{message}</Text>,
      labels: { confirm: confirmLabel, cancel: t("Cancel") },
      confirmProps: danger ? { color: "red" } : undefined,
      onConfirm: () => resolve(true),
      onCancel: () => resolve(false),
      onClose: () => resolve(false),
    });
  });
}

export function askText(title: string, label: string, initial = ""): Promise<string | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (v: string | null) => {
      if (done) return;
      done = true;
      resolve(v);
      modals.closeAll();
    };
    modals.open({
      title,
      onClose: () => finish(null),
      children: <TextPrompt label={label} initial={initial} onDone={finish} />,
    });
  });
}

function TextPrompt({ label, initial, onDone }: { label: string; initial: string; onDone: (v: string | null) => void }) {
  const [value, setValue] = useState(initial);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (value.trim()) onDone(value.trim());
      }}
    >
      <TextInput label={label} value={value} onChange={(e) => setValue(e.currentTarget.value)} data-autofocus />
      <Group justify="flex-end" mt="md">
        <Button variant="default" onClick={() => onDone(null)}>{t("Cancel")}</Button>
        <Button type="submit" disabled={!value.trim()}>{t("OK")}</Button>
      </Group>
    </form>
  );
}

export function askDeleteClasses(names: string[]): Promise<{ recursive: boolean } | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (v: { recursive: boolean } | null) => {
      if (done) return;
      done = true;
      resolve(v);
      modals.closeAll();
    };
    modals.open({ title: t("Delete classes"), onClose: () => finish(null), children: <DeletePrompt names={names} onDone={finish} /> });
  });
}

function DeletePrompt({ names, onDone }: { names: string[]; onDone: (v: { recursive: boolean } | null) => void }) {
  const [recursive, setRecursive] = useState(false);
  return (
    <Stack>
      <Text size="sm">{t("The following items will be deleted:")}</Text>
      <ScrollArea.Autosize mah={240}>
        <List size="sm">{names.map((n, i) => <List.Item key={i}>{n}</List.Item>)}</List>
      </ScrollArea.Autosize>
      <Toggle label={t("Also delete all child classes")} checked={recursive} onChange={(e) => setRecursive(e.currentTarget.checked)} />
      <Text size="xs" c="dimmed">{t("Otherwise child classes are moved to the parent of the deleted class.")}</Text>
      <Group justify="flex-end">
        <Button variant="default" onClick={() => onDone(null)}>{t("Cancel")}</Button>
        <Button color="red" onClick={() => onDone({ recursive })} data-autofocus>{t("Delete")}</Button>
      </Group>
    </Stack>
  );
}
