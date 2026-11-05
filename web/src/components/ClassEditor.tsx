import { Modal } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { ClassForm } from "../forms/ClassForm";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";
import type { BsddClass } from "../types";

/** Modal for creating classes (and editing them from the graph / context menus). */
export function ClassEditor() {
  const { t } = useTranslation();
  const target = useUi((s) => s.classEditor);
  const idx = useProject((s) => s.idx);
  const setActiveClass = useProject((s) => s.setActiveClass);
  if (!target) return null;
  const close = () => useUi.getState().set({ classEditor: null });
  const existing = target.code ? idx.classes.get(target.code) : undefined;
  return (
    <Modal opened onClose={close} title={existing ? t("Edit class: {{name}}", { name: existing.Name }) : t("New class")} size="xl">
      <ClassForm
        key={target.code ?? `new-${target.parentCode ?? ""}`}
        code={target.code}
        parentCode={target.parentCode}
        classType={target.classType}
        onCancel={close}
        onDone={(code) => {
          setActiveClass(code);
          close();
        }}
      />
    </Modal>
  );
}

export type { BsddClass };
