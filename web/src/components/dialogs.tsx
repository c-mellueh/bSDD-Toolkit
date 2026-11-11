import { Button, Group, List, ScrollArea, Stack, Text, TextInput } from "@mantine/core";
import { Toggle } from "./Toggle";
import { modals } from "@mantine/modals";
import { useState } from "react";
import i18n from "../i18n";

const t = (s: string, o?: Record<string, unknown>) => i18n.t(s, o);

export function askConfirm(title: string, message: string, confirmLabel = t("OK"), danger = false): Promise<boolean> {
  return new Promise((resolve) => {
    modals.openConfirmModal({
      zIndex: 1000, // above editor popups
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
      zIndex: 1000,
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

export interface DeleteClassesResult {
  recursive: boolean;
  /** also delete the properties used by deleted groups of properties */
  deleteProperties: boolean;
}

/** ``propertyUsage(recursive)``: properties used by the groups of properties that would be deleted. */
export type PropertyUsage = (recursive: boolean) => { names: string[]; otherClasses: number };

export function askDeleteClasses(names: string[], propertyUsage?: PropertyUsage): Promise<DeleteClassesResult | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (v: DeleteClassesResult | null) => {
      if (done) return;
      done = true;
      resolve(v);
      modals.closeAll();
    };
    modals.open({
      zIndex: 1000, title: t("Delete classes"), onClose: () => finish(null), children: <DeletePrompt names={names} propertyUsage={propertyUsage} onDone={finish} /> });
  });
}

function DeletePrompt({ names, propertyUsage, onDone }: { names: string[]; propertyUsage?: PropertyUsage; onDone: (v: DeleteClassesResult | null) => void }) {
  const [recursive, setRecursive] = useState(false);
  const [deleteProperties, setDeleteProperties] = useState(false);
  const usage = propertyUsage?.(recursive);
  const nProps = usage?.names.length ?? 0;
  const shown = usage?.names.slice(0, 8).join(", ") ?? "";
  return (
    <Stack>
      <Text size="sm">{t("The following items will be deleted:")}</Text>
      <ScrollArea.Autosize mah={240}>
        <List size="sm">{names.map((n, i) => <List.Item key={i}>{n}</List.Item>)}</List>
      </ScrollArea.Autosize>
      <Toggle label={t("Also delete all child classes")} checked={recursive} onChange={(e) => setRecursive(e.currentTarget.checked)} />
      <Text size="xs" c="dimmed">{t("Otherwise child classes are moved to the parent of the deleted class.")}</Text>
      {nProps > 0 && (
        <>
          <Toggle
            label={t("Also delete the {{n}} properties of the predefined property set", { n: nProps })}
            checked={deleteProperties}
            onChange={(e) => setDeleteProperties(e.currentTarget.checked)}
          />
          <Text size="xs" c="dimmed">
            {shown}
            {nProps > 8 ? ` ${t("and {{n}} more", { n: nProps - 8 })}` : ""}
          </Text>
          {deleteProperties && usage!.otherClasses > 0 && (
            <Text size="xs" c="red">{t("They are also used in {{n}} other classes and will be removed there too.", { n: usage!.otherClasses })}</Text>
          )}
        </>
      )}
      <Group justify="flex-end">
        <Button variant="default" onClick={() => onDone(null)}>{t("Cancel")}</Button>
        <Button color="red" onClick={() => onDone({ recursive, deleteProperties: nProps > 0 && deleteProperties })} data-autofocus>{t("Delete")}</Button>
      </Group>
    </Stack>
  );
}
