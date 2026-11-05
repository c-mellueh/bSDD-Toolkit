import { Modal } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { PropertyForm } from "../forms/PropertyForm";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";

/** Modal for creating properties (and editing them from tables, the graph or context menus). */
export function PropertyEditor() {
  const { t } = useTranslation();
  const target = useUi((s) => s.propertyEditor);
  const idx = useProject((s) => s.idx);
  if (!target) return null;
  const close = () => useUi.getState().set({ propertyEditor: null });
  const existing = target.code ? idx.properties.get(target.code) : undefined;
  return (
    <Modal opened onClose={close} title={existing ? t("Edit property: {{name}}", { name: existing.Name }) : t("New property")} size="xl" zIndex={300}>
      <PropertyForm
        key={target.code ?? "new"}
        code={target.code}
        onCancel={close}
        onDone={(code, created) => {
          if (created) target.onCreated?.(code);
          close();
        }}
      />
    </Modal>
  );
}
