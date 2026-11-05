import { useProject } from "./project";

/** True when the dictionary was opened through a read-only link. */
export const useReadOnly = () => useProject((s) => s.role === "view");
