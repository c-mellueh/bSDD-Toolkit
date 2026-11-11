/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Grid, Group, Select, Tabs, TagsInput, TextInput, Textarea } from "@mantine/core";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { AiTextarea, RelationsEditor, useResources } from "../components/fields";
import { CLASS_STATUSES, CLASS_TYPES, GOP, clean, slugify } from "../model";
import { useSettings } from "../state/settings";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { useReadOnly } from "../state/readonly";
import type { BsddClass, ClassRelation } from "../types";
import { SaveBar, changedKeys, mergeRemote, same, snap } from "./SaveBar";
import { CommonDetailCards, DetailGrid } from "./DetailSections";
import { useUnsaved } from "../state/unsaved";

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
  const releaseUnsaved = useUnsaved(dirty && !readOnly, inline ? "page" : "popup");
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
      // new Groups of Properties get the prefix from the settings (e.g. "Pset_Fire-Safety")
      const codeFor = (n: string) => (n && f.ClassType === GOP ? useSettings.getState().gopPrefix : "") + slugify(n);
      if (!existing && (!f.Code || f.Code === codeFor(f.Name ?? "") || f.Code === slugify(f.Name ?? ""))) next.Code = codeFor(name);
      return next;
    });

  const codeTaken = form.Code && form.Code !== code && idx.classes.has(form.Code);
  // "empty" errors only after the user touched the field (not right when a new form opens)
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const touch = (k: string) => setTouched((s) => (s[k] ? s : { ...s, [k]: true }));
  const codeEmpty = !form.Code?.trim();
  const nameEmpty = !form.Name?.trim();
  const codeError = codeEmpty ? (touched.Code || touched.Name) && t("Code must not be empty") : codeTaken ? t("Code exists already") : false;
  const nameError = nameEmpty ? touched.Name && t("Name must not be empty") : false;
  const invalid = !!codeError || !!nameError || codeEmpty || nameEmpty;

  const save = async () => {
    if (invalid) {
      setTouched({ Name: true, Code: true });
      return;
    }
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
      releaseUnsaved();
      onDone?.(ok);
    }
  };

  const countryData = res.countries.map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` }));
  const languageData = [...new Set(res.languages.map((l) => l.IsoCode))].map((c) => ({ value: c, label: `${res.languages.find((l) => l.IsoCode === c)?.Name} (${c})` }));

  const general = (
    <Grid>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Name")} value={form.Name ?? ""} onChange={(e) => setName(e.currentTarget.value)} onBlur={() => touch("Name")} error={nameError || undefined} data-autofocus={!inline || undefined} required /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => { touch("Code"); set("Code", e.currentTarget.value); }} onBlur={() => touch("Code")} error={codeError || undefined} required /></Grid.Col>
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
    <DetailGrid>
      <CommonDetailCards
        form={form}
        set={set}
        countryData={countryData}
        languageData={languageData}
        documentReference={<TextInput label={t("Document reference")} value={form.DocumentReference ?? ""} onChange={(e) => set("DocumentReference", e.currentTarget.value)} />}
      />
    </DetailGrid>
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
        <SaveBar dirty={dirty} busy={busy} invalid={invalid} onSave={save} onDiscard={reset} />
      ) : (
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={onCancel}>{t("Cancel")}</Button>
          <Button type="submit" loading={busy} disabled={invalid}>{existing ? t("Save") : t("Create")}</Button>
        </Group>
      )}
    </form>
  );
}
