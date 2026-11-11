/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";

export type ExportKind = "excel" | "ids" | "iso23386" | "iso7817" | "revit-psets" | "revit-shared";

export interface ClassEditorTarget {
  code?: string; // edit an existing class
  parentCode?: string | null; // create a new class below this parent
  classType?: string;
}

export interface CpEditorTarget {
  classCode: string;
  code?: string; // edit existing
  pset?: string; // new class property in this pset
}

export interface PropertyEditorTarget {
  code?: string;
  onCreated?: (code: string) => void;
}

interface UiState {
  classEditor: ClassEditorTarget | null;
  cpEditor: CpEditorTarget | null;
  propertyEditor: PropertyEditorTarget | null;
  dictionaryEditor: boolean;
  propertiesWindow: boolean;
  gopWindow: boolean;
  loin: boolean;
  exportKind: ExportKind | null;
  search: { kind: "class" | "property"; onPick: (code: string) => void } | null;
  graph: boolean;
  shell: boolean;
  settings: boolean;
  share: boolean;
  versions: boolean;
  projectSettings: boolean;
  palette: boolean;
  revealClass: { code: string; at: number } | null;
  set: (patch: Partial<UiState>) => void;
}

export const useUi = create<UiState>((set) => ({
  classEditor: null,
  cpEditor: null,
  propertyEditor: null,
  dictionaryEditor: false,
  propertiesWindow: false,
  gopWindow: false,
  loin: false,
  exportKind: null,
  search: null,
  graph: false,
  shell: false,
  settings: false,
  share: false,
  versions: false,
  projectSettings: false,
  palette: false,
  revealClass: null,
  set: (patch) => set(patch),
}));

export const openUi = (patch: Partial<UiState>) => useUi.getState().set(patch);
