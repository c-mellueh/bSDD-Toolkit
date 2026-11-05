import { Modal } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { GOP } from "../model";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";
import { ClassPropertyTable } from "./ClassPropertyTable";
import { ClassTree } from "./ClassTree";

/** Groups of properties (classes of type GroupOfProperties) and their properties. */
export function GopWindow() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.gopWindow);
  const activeClass = useProject((s) => s.activeClass);
  const idx = useProject((s) => s.idx);
  if (!opened) return null;
  const cls = activeClass ? idx.classes.get(activeClass) : undefined;
  const gop = cls?.ClassType === GOP ? cls.Code : null;
  return (
    <Modal opened onClose={() => useUi.getState().set({ gopWindow: false })} title={t("Groups of properties")} size="90%" styles={{ body: { height: "75vh" } }}>
      <div style={{ display: "flex", height: "100%", border: "1px solid var(--mantine-color-default-border)" }}>
        <div style={{ width: 360, flex: "none" }}><ClassTree mode="gop" /></div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <ClassPropertyTable classCode={gop} pset={null} title={t("Properties of the group")} />
        </div>
      </div>
    </Modal>
  );
}
