/* eslint-disable @typescript-eslint/no-explicit-any */
export interface AllowedValue {
  Code: string;
  Value: string;
  Description?: string;
  Uri?: string;
  SortNumber?: number;
  OwnedUri?: string;
}

export interface ClassRelation {
  RelationType: string;
  RelatedClassUri: string;
  RelatedClassName?: string;
  Fraction?: number;
  OwnedUri?: string;
}

export interface PropertyRelation {
  RelationType: string;
  RelatedPropertyUri: string;
  RelatedPropertyName?: string;
  OwnedUri?: string;
}

export interface ClassProperty {
  Code: string;
  PropertyCode?: string;
  PropertyUri?: string;
  Description?: string;
  PropertySet?: string;
  Unit?: string;
  PredefinedValue?: string;
  IsRequired?: boolean;
  IsWritable?: boolean;
  MaxExclusive?: number;
  MaxInclusive?: number;
  MinExclusive?: number;
  MinInclusive?: number;
  Pattern?: string;
  OwnedUri?: string;
  PropertyType?: "Property" | "Dependency";
  SortNumber?: number;
  Symbol?: string;
  AllowedValues?: AllowedValue[];
}

export interface BsddClass {
  Code: string;
  Name: string;
  ClassType?: string;
  Definition?: string;
  Description?: string;
  ParentClassCode?: string;
  RelatedIfcEntityNamesList?: string[];
  Synonyms?: string[];
  Status?: string;
  OwnedUri?: string;
  ClassProperties?: ClassProperty[];
  ClassRelations?: ClassRelation[];
  [key: string]: any;
}

export interface BsddProperty {
  Code: string;
  Name: string;
  Definition?: string;
  Description?: string;
  DataType?: string;
  Units?: string[];
  OwnedUri?: string;
  AllowedValues?: AllowedValue[];
  PropertyRelations?: PropertyRelation[];
  [key: string]: any;
}

export interface Dictionary {
  OrganizationCode: string;
  DictionaryCode: string;
  DictionaryVersion: string;
  LanguageIsoCode: string;
  LanguageOnly: boolean;
  UseOwnUri: boolean;
  DictionaryName?: string;
  DictionaryUri?: string;
  Status?: string;
  Classes?: BsddClass[];
  Properties?: BsddProperty[];
  [key: string]: any;
}

export interface LoinEntry {
  guid: string;
  name: string;
  date?: string | null;
}

export interface LoinActor {
  guid?: string;
  role?: string | null;
  first_name?: string | null;
  middle_name?: string | null;
  last_name?: string | null;
  affiliation?: string | null;
  email_address?: string | null;
}

export interface LoinSpec {
  guid: string;
  classes: string[];
  properties: Record<string, [string, string][]>;
}

export interface LoinState {
  purposes?: LoinEntry[];
  milestones?: LoinEntry[];
  providing_actor?: LoinActor | null;
  receiving_actor?: LoinActor | null;
  added_classes?: string[];
  specs?: Record<string, LoinSpec>;
  /** ticked purpose × milestone combinations; null/undefined = not set (combinations with classes count) */
  matrix?: string[] | null;
}

export interface Extras {
  temporary_psets: Record<string, string[]>;
  loin: LoinState;
  export_settings: Record<string, any>;
  /** every child class has all class properties of its parent */
  strict_inheritance?: boolean;
}

export interface Doc {
  dictionary: Dictionary;
  extras: Extras;
}

export interface User {
  role?: "edit" | "view";
  id: string;
  name: string;
  color: string;
  selection: { class?: string; pset?: string; [k: string]: any };
}

export interface ProjectMeta {
  id?: string;
  protected?: boolean;
  name?: string;
  created?: number;
  updated?: number;
  source?: string;
}

export type PatchOp =
  | { op: "add"; path: string; value: any }
  | { op: "replace"; path: string; value: any }
  | { op: "remove"; path: string };
