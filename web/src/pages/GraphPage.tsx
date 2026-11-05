import { Center, Loader } from "@mantine/core";
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { ClassEditor } from "../components/ClassEditor";
import { ClassPropertyEditor } from "../components/ClassPropertyEditor";
import { ContextMenuHost } from "../components/ContextMenu";
import { PropertyEditor } from "../components/PropertyEditor";
import { SearchDialog } from "../components/SearchDialog";
import { GraphViewer } from "../graph/GraphViewer";
import { PasswordScreen } from "../components/PasswordScreen";
import { connect, disconnect, useProject } from "../state/project";

/** The graph viewer in its own browser window (e.g. on a second screen). */
export function GraphPage({ base = "/p" }: { base?: "/p" | "/v" } = {}) {
  const { projectId } = useParams();
  const doc = useProject((s) => s.doc);
  const status = useProject((s) => s.status);
  useEffect(() => {
    if (!projectId) return;
    connect(projectId, base);
    return () => disconnect();
  }, [projectId, base]);
  useEffect(() => {
    if (doc) document.title = `${doc.dictionary.DictionaryName ?? doc.dictionary.DictionaryCode} – Graph`;
  }, [doc]);
  if (status === "locked") return <PasswordScreen />;
  if (!doc || !projectId) return <Center h="100%"><Loader /></Center>;
  return (
    <div style={{ height: "100%" }}>
      <GraphViewer projectId={projectId} standalone />
      <ContextMenuHost />
      <ClassEditor />
      <ClassPropertyEditor />
      <PropertyEditor />
      <SearchDialog />
    </div>
  );
}
