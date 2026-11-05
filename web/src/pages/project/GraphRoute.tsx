import { GraphViewer } from "../../graph/GraphViewer";
import { useProject } from "../../state/project";

export function GraphRoute() {
  const projectId = useProject((s) => s.projectId);
  if (!projectId) return null;
  return <div style={{ height: "100%" }}><GraphViewer projectId={projectId} /></div>;
}
