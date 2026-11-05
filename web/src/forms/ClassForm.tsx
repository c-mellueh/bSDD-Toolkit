/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Grid, Group, MultiSelect, Select, Tabs, TagsInput, TextInput, Textarea } from "@mantine/core";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { AiTextarea, DateField, OptionalNumber, RelationsEditor, useResources } from "../components/fields";
import { CLASS_STATUSES, CLASS_TYPES, clean, slugify } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { useReadOnly } from "../state/readonly";
import type { BsddClass, ClassRelation } from "../types";
import { SaveBar, changedKeys, mergeRemote, same, snap } from "./SaveBar";

const EDITABLE = [
  "Code", "Name", "ClassType", "Definition", "Description", "ParentClassCode", "RelatedIfcEntityNamesList", "Synonyms", "Status",
  "ReferenceCode", "CountriesOfUse", "CountryOfOrigin", "CreatorLanguageIsoCode", "DocumentReference", "OwnedUri",
  "ReplacedObjectCodes", "ReplacingObjectCodes", "SubdivisionsOfUse", "Uid", "RevisionNumber", "VersionNumber",
  "RevisionDateUtc", "VersionDateUtc", "ActivationDateUtc", "DeActivationDateUtc", "DeprecationExplanation", "VisualRepresentationUri",
];

export type ClassSection = "general" | "details" | "relations";

export interface ClassFormProps {
  code?: string; // edit an existing class
  parentCode?: string | null; // new class below this parent
  classType?: string;
  /** Render only one section (inline on the class page); otherwise all sections in tabs. */
  section?: ClassSection;
  /** Inline: no Cancel button, sticky save bar while dirty, follows remote changes while clean. */
  inline?: boolean;
  onDone?: (code: string) => void;
  onCancel?: () => void;
}

function initial(c: BsddClass | undefined, props: ClassFormProps) {
  if (c) {
    const f: Record<string, any> = {};
    for (const k of EDITABLE) f[k] = c[k] ?? null;
    return { form: f, relations: c.ClassRelations ?? [] };
  }
  return { form: { Code: "", Name: "", ClassType: props.classType ?? "Class", ParentClassCode: props.parentCode ?? null, Status: "Preview" } as Record<string, any>, relations: [] as ClassRelation[] };
}

export function ClassForm(props: ClassFormProps) {
  const { code, section, inline, onDone, onCancel } = props;
  const { t } = useTranslation();
  const readOnly = useReadOnly();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const res = useResources();
  const existing = code ? idx.classes.get(code) : undefined;
  const [form, setForm] = useState<Record<string, any>>(() => initial(existing, props).form);
  const [relations, setRelations] = useState<ClassRelation[]>(() => initial(existing, props).relations);
  const [base, setBase] = useState(() => initial(existing, props));
  const [busy, setBusy] = useState(false);
  const dirty = snap(form, relations) !== snap(base.form, base.relations);
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;

  const reset = () => {
    const i = initial(existing, props);
    setForm(i.form);
    setRelations(i.relations);
    setBase(i);
  };
  // another class selected → reset; same class changed remotely → follow while clean
  const lastCode = useRef(code);
  useEffect(() => {
    if (lastCode.current !== code || !dirtyRef.current) reset();
    else if (existing) {
      // someone else changed this class while we edit: keep our edits, take theirs for untouched fields
      const next = initial(existing, props);
      setForm((f) => mergeRemote(f, base.form, next.form));
      setRelations((r) => (same(r, base.relations) ? next.relations : r));
      setBase(next);
    }
    lastCode.current = code;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, existing]);

  const ifcOptions = useMemo(() => res.ifcClasses.map((c) => c.code), [res.ifcClasses]);
  const parentOptions = useMemo(
    () => (doc?.dictionary.Classes ?? []).filter((c) => c.Code !== code).map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` })),
    [doc, code],
  );
  if (!doc) return null;

  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));
  const setName = (name: string) =>
    setForm((f) => {
      const next: Record<string, any> = { ...f, Name: name };
      if (!existing && (!f.Code || f.Code === slugify(f.Name ?? ""))) next.Code = slugify(name);
      return next;
    });

  const codeTaken = form.Code && form.Code !== code && idx.classes.has(form.Code);
  const codeError = !form.Code?.trim() ? t("Code must not be empty") : codeTaken ? t("Code exists already") : false;
  const nameError = !form.Name?.trim() ? t("Name must not be empty") : false;

  const save = async () => {
    if (codeError || nameError) return;
    setBusy(true);
    const data: Record<string, any> = clean({ ...form });
    let ok: string | undefined;
    if (existing) {
      // only send what this user changed (relative to the state the edit started from)
      const baseData: Record<string, any> = clean({ ...base.form });
      const changed: Record<string, any> = {};
      for (const k of changedKeys(EDITABLE, data, baseData)) changed[k] = data[k];
      if (!same(relations, base.relations)) changed.ClassRelations = relations;
      ok = Object.keys(changed).length ? await attempt(() => op<string>("class.update", { code: existing.Code, data: changed })) : existing.Code;
    } else {
      ok = await attempt(() => op<string>("class.create", { data: { ...data, ClassRelations: relations }, parent_code: data.ParentClassCode ?? null }));
    }
    setBusy(false);
    if (ok) {
      // the store update arrives with the server patch; treat the saved state as clean
      setBase({ form, relations });
      onDone?.(ok);
    }
  };

  const countryData = res.countries.map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` }));
  const languageData = [...new Set(res.languages.map((l) => l.IsoCode))].map((c) => ({ value: c, label: `${res.languages.find((l) => l.IsoCode === c)?.Name} (${c})` }));

  const general = (
    <Grid>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Name")} value={form.Name ?? ""} onChange={(e) => setName(e.currentTarget.value)} error={nameError} data-autofocus={!inline || undefined} required /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => set("Code", e.currentTarget.value)} error={codeError} required /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Class type")} data={CLASS_TYPES} value={form.ClassType ?? "Class"} onChange={(v) => set("ClassType", v)} allowDeselect={false} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Status")} data={CLASS_STATUSES} value={form.Status ?? null} onChange={(v) => set("Status", v)} clearable /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Parent class")} data={parentOptions} value={form.ParentClassCode ?? null} onChange={(v) => set("ParentClassCode", v)} searchable clearable limit={100} /></Grid.Col>
      <Grid.Col span={12}>
        <AiTextarea
          label={t("Definition")}
          kind="class"
          value={form.Definition ?? ""}
          onChange={(v) => set("Definition", v)}
          context={() => ({ Name: form.Name, ParentClassCode: form.ParentClassCode, RelatedIfcEntityNamesList: form.RelatedIfcEntityNamesList ?? [] })}
        />
      </Grid.Col>
      <Grid.Col span={12}><Textarea label={t("Description")} value={form.Description ?? ""} onChange={(e) => set("Description", e.currentTarget.value)} autosize minRows={2} maxRows={6} /></Grid.Col>
      <Grid.Col span={12}>
        <TagsInput label={t("Related IFC entities")} data={ifcOptions} value={form.RelatedIfcEntityNamesList ?? []} onChange={(v) => set("RelatedIfcEntityNamesList", v)} limit={30} clearable placeholder="IfcWall, IfcWallSTANDARD…" />
      </Grid.Col>
      <Grid.Col span={12}><TagsInput label={t("Synonyms")} value={form.Synonyms ?? []} onChange={(v) => set("Synonyms", v)} clearable /></Grid.Col>
    </Grid>
  );
  const details = (
    <Grid>
      <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Reference code")} value={form.ReferenceCode ?? ""} onChange={(e) => set("ReferenceCode", e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label="UID" value={form.Uid ?? ""} onChange={(e) => set("Uid", e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Document reference")} value={form.DocumentReference ?? ""} onChange={(e) => set("DocumentReference", e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><MultiSelect label={t("Countries of use")} data={countryData} value={form.CountriesOfUse ?? []} onChange={(v) => set("CountriesOfUse", v)} searchable clearable /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><Select label={t("Country of origin")} data={countryData} value={form.CountryOfOrigin ?? null} onChange={(v) => set("CountryOfOrigin", v)} searchable clearable /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><Select label={t("Creator language")} data={languageData} value={form.CreatorLanguageIsoCode ?? null} onChange={(v) => set("CreatorLanguageIsoCode", v)} searchable clearable /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TagsInput label={t("Subdivisions of use")} value={form.SubdivisionsOfUse ?? []} onChange={(v) => set("SubdivisionsOfUse", v)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Owned URI")} value={form.OwnedUri ?? ""} onChange={(e) => set("OwnedUri", e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Visual representation URI")} value={form.VisualRepresentationUri ?? ""} onChange={(e) => set("VisualRepresentationUri", e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TagsInput label={t("Replaced object codes")} value={form.ReplacedObjectCodes ?? []} onChange={(v) => set("ReplacedObjectCodes", v)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TagsInput label={t("Replacing object codes")} value={form.ReplacingObjectCodes ?? []} onChange={(v) => set("ReplacingObjectCodes", v)} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Version number")} value={form.VersionNumber} onChange={(v) => set("VersionNumber", v)} integer /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><DateField label={t("Version date")} value={form.VersionDateUtc} onChange={(v) => set("VersionDateUtc", v)} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Revision number")} value={form.RevisionNumber} onChange={(v) => set("RevisionNumber", v)} integer /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><DateField label={t("Revision date")} value={form.RevisionDateUtc} onChange={(v) => set("RevisionDateUtc", v)} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><DateField label={t("Activation date")} value={form.ActivationDateUtc} onChange={(v) => set("ActivationDateUtc", v)} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3 }}><DateField label={t("Deactivation date")} value={form.DeActivationDateUtc} onChange={(v) => set("DeActivationDateUtc", v)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Deprecation explanation")} value={form.DeprecationExplanation ?? ""} onChange={(e) => set("DeprecationExplanation", e.currentTarget.value)} /></Grid.Col>
    </Grid>
  );
  const rel = <RelationsEditor kind="class" relations={relations} onChange={(r) => setRelations(r as ClassRelation[])} selfCode={code} />;

  return (
    <form onSubmit={(e) => { e.preventDefault(); if (!readOnly) void save(); }}>
      {section ? (
        <fieldset disabled={readOnly} className="ro-fieldset">{{ general, details, relations: rel }[section]}</fieldset>
      ) : (
        <Tabs defaultValue="general" keepMounted={false}>
          <Tabs.List mb="sm">
            <Tabs.Tab value="general">{t("General")}</Tabs.Tab>
            <Tabs.Tab value="details">{t("Details")}</Tabs.Tab>
            <Tabs.Tab value="relations">{t("Relations")} ({relations.length})</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="general"><fieldset disabled={readOnly} className="ro-fieldset">{general}</fieldset></Tabs.Panel>
          <Tabs.Panel value="details"><fieldset disabled={readOnly} className="ro-fieldset">{details}</fieldset></Tabs.Panel>
          <Tabs.Panel value="relations"><fieldset disabled={readOnly} className="ro-fieldset">{rel}</fieldset></Tabs.Panel>
        </Tabs>
      )}
      {readOnly ? null : inline ? (
        <SaveBar dirty={dirty} busy={busy} invalid={!!codeError || !!nameError} onSave={save} onDiscard={reset} />
      ) : (
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={onCancel}>{t("Cancel")}</Button>
          <Button type="submit" loading={busy} disabled={!!codeError || !!nameError}>{existing ? t("Save") : t("Create")}</Button>
        </Group>
      )}
    </form>
  );
}
