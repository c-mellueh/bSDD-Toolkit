import { Alert, Button, Group, Modal, Stack, Text } from "@mantine/core";
import { IconHierarchy2 } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { missingInherited } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { useReadOnly } from "../state/readonly";
import { useUi } from "../state/ui";
import { askConfirm } from "./dialogs";
import { Toggle } from "./Toggle";

/** Settings stored with the dictionary (apply to everyone working on it). */
export function ProjectSettingsDialog() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.projectSettings);
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const readOnly = useReadOnly();
  const close = () => useUi.getState().set({ projectSettings: false });
  const strict = !!doc?.extras?.strict_inheritance;

  const toggleStrict = async (enabled: boolean) => {
    if (!doc) return;
    if (enabled) {
      const n = missingInherited(idx, doc);
      if (n > 0) {
        const ok = await askConfirm(
          t("Switch on strict inheritance?"),
          t("{{n}} class properties are missing in child classes and will be added from their parent classes.", { n }),
          t("Switch on"),
        );
        if (!ok) return;
      }
    }
    const added = await attempt(() => op<number>("inheritance.set_strict", { enabled }));
    if (added) notifyOk(t("{{n}} inherited class properties added", { n: added }));
  };

  return (
    <Modal opened={opened} onClose={close} title={t("Project settings")} size="lg">
      <Stack>
        <Text size="sm" c="dimmed">{t("These settings are saved with the dictionary and apply to everyone working on it.")}</Text>
        <Toggle
          label={t("Strict inheritance")}
          description={t("Every child class has all class properties of its parent class. In child classes only the values of inherited class properties can be changed (allowed values, unit, required …); they cannot be removed or moved to another property set.")}
          checked={strict}
          disabled={readOnly}
          onChange={(e) => void toggleStrict(e.currentTarget.checked)}
        />
        {strict && (
          <Alert variant="light" icon={<IconHierarchy2 size={16} />}>
            {t("Class properties added to, changed in or removed from a parent class are passed on to all its child classes. Values a child class changed itself are kept.")}
          </Alert>
        )}
        <Group justify="flex-end">
          <Button variant="default" onClick={close}>{t("Close")}</Button>
        </Group>
      </Stack>
    </Modal>
  );
}
