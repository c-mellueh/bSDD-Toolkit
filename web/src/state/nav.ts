/** Navigation helpers usable outside React components (menus, graph, search callbacks). */
import type { NavigateFunction } from "react-router-dom";
import { classMode, type ClassMode } from "../model";
import { useProject } from "./project";

let navigate: NavigateFunction | null = null;
export const setNavigator = (fn: NavigateFunction | null) => {
  navigate = fn;
};

export type Section = "" | "classes" | "groups" | "materials" | "properties" | "loin" | "graph" | "export";

/** Page of each class tree. */
export const MODE_SECTION: Record<ClassMode, Section> = { main: "classes", gop: "groups", material: "materials" };

export function projectPath(section: Section, code?: string | null) {
  const { projectId: id, base: prefix } = useProject.getState();
  const base = `${prefix}/${id}${section ? `/${section}` : ""}`;
  return code ? `${base}/${encodeURIComponent(code)}` : base;
}

export function go(section: Section, code?: string | null, replace = false) {
  navigate?.(projectPath(section, code), { replace });
}

/** Section (classes / groups / materials) a class belongs to. */
export function classSection(code: string): Section {
  return MODE_SECTION[classMode(useProject.getState().idx.classes.get(code))];
}

export function openClass(code: string) {
  useProject.getState().setActiveClass(code);
  go(classSection(code), code);
}

export function openProperty(code: string) {
  go("properties", code);
}
