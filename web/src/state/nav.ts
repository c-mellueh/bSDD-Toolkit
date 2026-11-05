/** Navigation helpers usable outside React components (menus, graph, search callbacks). */
import type { NavigateFunction } from "react-router-dom";
import { GOP } from "../model";
import { useProject } from "./project";

let navigate: NavigateFunction | null = null;
export const setNavigator = (fn: NavigateFunction | null) => {
  navigate = fn;
};

export type Section = "" | "classes" | "groups" | "properties" | "loin" | "graph" | "export";

export function projectPath(section: Section, code?: string | null) {
  const id = useProject.getState().projectId;
  const base = `/p/${id}${section ? `/${section}` : ""}`;
  return code ? `${base}/${encodeURIComponent(code)}` : base;
}

export function go(section: Section, code?: string | null, replace = false) {
  navigate?.(projectPath(section, code), { replace });
}

/** Section (classes / groups) a class belongs to. */
export function classSection(code: string): Section {
  return useProject.getState().idx.classes.get(code)?.ClassType === GOP ? "groups" : "classes";
}

export function openClass(code: string) {
  useProject.getState().setActiveClass(code);
  go(classSection(code), code);
}

export function openProperty(code: string) {
  go("properties", code);
}
