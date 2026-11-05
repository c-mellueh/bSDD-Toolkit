import { Center, Loader } from "@mantine/core";
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { ClassEditor } from "../components/ClassEditor";
import { ClassPropertyEditor } from "../components/ClassPropertyEditor";
import { ContextMenuHost } from "../components/ContextMenu";
import { PropertyEditor } from "../components/PropertyEditor";
import { SearchDialog } from "../components/SearchDialog";
import { GraphViewer } from "../graph/GraphViewer";
import { connect, disconnect, useProject } from "../state/project";

/** The graph viewer in its own browser window (e.g. on a second screen). */
export function GraphPage() {
  const { projectId } = useParams();
  const doc = useProject((s) => s.doc);
  useEffect(() => {
    if (!projectId) return;
    connect(projectId);
    return () => disconnect();
  }, [projectId]);
  useEffect(() => {
    if (doc) document.title = `${doc.dictionary.DictionaryName ?? doc.dictionary.DictionaryCode} – Graph`;
  }, [doc]);
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
