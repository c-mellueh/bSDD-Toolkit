import { Modal } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { GraphViewer } from "../graph/GraphViewer";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";

export function GraphView() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.graph);
  const projectId = useProject((s) => s.projectId);
  if (!opened || !projectId) return null;
  return (
    <Modal
      opened
      onClose={() => useUi.getState().set({ graph: false })}
      title={t("Graph viewer")}
      fullScreen
      styles={{ body: { height: "calc(100vh - 60px)", padding: 0 }, content: { display: "flex", flexDirection: "column" } }}
    >
      <GraphViewer projectId={projectId} />
    </Modal>
  );
}
