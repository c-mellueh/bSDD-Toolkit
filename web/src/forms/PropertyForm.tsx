/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Grid, Group, MultiSelect, Select, Tabs, TagsInput, TextInput, Textarea } from "@mantine/core";
import { Toggle } from "../components/Toggle";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { DATA_TYPES, PROPERTY_VALUE_KINDS, clean, slugify } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { useReadOnly } from "../state/readonly";
import type { AllowedValue, BsddProperty, PropertyRelation } from "../types";
import { SaveBar, changedKeys, mergeRemote, same, snap } from "./SaveBar";
import { AiTextarea, AllowedValuesEditor, DateField, OptionalNumber, RelationsEditor, useResources } from "../components/fields";

const DIMENSIONS = [
  "DimensionLength", "DimensionMass", "DimensionTime", "DimensionElectricCurrent", "DimensionThermodynamicTemperature",
  "DimensionAmountOfSubstance", "DimensionLuminousIntensity",
];
const EDITABLE = [
  "Code", "Name", "Definition", "Description", "DataType", "Units", "Example", "ActivationDateUtc", "ConnectedPropertyCodes",
  "CountriesOfUse", "CountryOfOrigin", "CreatorLanguageIsoCode", "DeActivationDateUtc", "DeprecationExplanation", "Dimension",
  ...DIMENSIONS, "DocumentReference", "DynamicParameterPropertyCodes", "IsDynamic", "MaxExclusive", "MaxInclusive", "MinExclusive",
  "MinInclusive", "MethodOfMeasurement", "OwnedUri", "Pattern", "PhysicalQuantity", "PropertyValueKind", "ReplacedObjectCodes",
  "ReplacingObjectCodes", "RevisionDateUtc", "RevisionNumber", "Status", "SubdivisionsOfUse", "TextFormat", "Uid", "VersionDateUtc",
  "VersionNumber", "VisualRepresentationUri", "AllowedValues",
];

export type PropertySection = "general" | "values" | "details" | "dimension" | "relations";

export interface PropertyFormProps {
  code?: string;
  section?: PropertySection;
  inline?: boolean;
  onDone?: (code: string, created: boolean) => void;
  onCancel?: () => void;
}

function initial(p: BsddProperty | undefined) {
  if (p) {
    const f: Record<string, any> = {};
    for (const k of EDITABLE) f[k] = p[k] ?? null;
    f.AllowedValues = p.AllowedValues ?? [];
    return { form: f, relations: p.PropertyRelations ?? [] };
  }
  return { form: { Code: "", Name: "", DataType: "String", AllowedValues: [] } as Record<string, any>, relations: [] as PropertyRelation[] };
}

export function PropertyForm({ code, section, inline, onDone, onCancel }: PropertyFormProps) {
  const { t } = useTranslation();
  const readOnly = useReadOnly();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const res = useResources();
  const existing = code ? idx.properties.get(code) : undefined;
  const [form, setForm] = useState<Record<string, any>>(() => initial(existing).form);
  const [relations, setRelations] = useState<PropertyRelation[]>(() => initial(existing).relations);
  const [base, setBase] = useState(() => initial(existing));
  const [busy, setBusy] = useState(false);
  const dirty = snap(form, relations) !== snap(base.form, base.relations);
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  const reset = () => {
    const i = initial(existing);
    setForm(i.form);
    setRelations(i.relations);
    setBase(i);
  };
  const lastCode = useRef(code);
  useEffect(() => {
    if (lastCode.current !== code || !dirtyRef.current) reset();
    else if (existing) {
      const next = initial(existing);
      setForm((f) => mergeRemote(f, base.form, next.form));
      setRelations((r) => (same(r, base.relations) ? next.relations : r));
      setBase(next);
    }
    lastCode.current = code;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, existing]);

  if (!doc) return null;
  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));
  const setName = (name: string) =>
    setForm((f) => {
      const next: Record<string, any> = { ...f, Name: name };
      if (!existing && (!f.Code || f.Code === slugify(f.Name ?? ""))) next.Code = slugify(name);
      return next;
    });

  const codeError = !form.Code?.trim() ? t("Code must not be empty") : form.Code !== code && idx.properties.has(form.Code) ? t("Code exists already") : false;
  const nameError = !form.Name?.trim() ? t("Name must not be empty") : false;

  const save = async () => {
    if (codeError || nameError) return;
    setBusy(true);
    const data: Record<string, any> = clean({ ...form });
    data.AllowedValues = form.AllowedValues ?? [];
    let ok: string | undefined;
    if (existing) {
      const baseData: Record<string, any> = clean({ ...base.form });
      baseData.AllowedValues = base.form.AllowedValues ?? [];
      const changed: Record<string, any> = {};
      for (const k of changedKeys(EDITABLE, data, baseData)) changed[k] = data[k];
      if (!same(relations, base.relations)) changed.PropertyRelations = relations;
      ok = Object.keys(changed).length ? await attempt(() => op<string>("prop.update", { code: existing.Code, data: changed })) : existing.Code;
    } else {
      ok = await attempt(() => op<string>("prop.create", { data: { ...data, PropertyRelations: relations } }));
    }
    setBusy(false);
    if (ok) {
      setBase({ form, relations });
      onDone?.(ok, !existing);
    }
  };

  const countryData = res.countries.map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` }));
  const languageData = [...new Set(res.languages.map((l) => l.IsoCode))];
  const unitData = [...new Set([...res.units.map((u) => u.Code), ...(form.Units ?? [])])];
  const propCodes = (doc.dictionary.Properties ?? []).map((p) => p.Code);

  const parts: Record<PropertySection, React.ReactNode> = {
    general: (
            <Grid>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Name")} value={form.Name ?? ""} onChange={(e) => setName(e.currentTarget.value)} error={nameError} data-autofocus={!inline || undefined} required /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => set("Code", e.currentTarget.value)} error={codeError} required /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Datatype")} data={DATA_TYPES} value={form.DataType ?? null} onChange={(v) => set("DataType", v)} clearable /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Value kind")} data={PROPERTY_VALUE_KINDS} value={form.PropertyValueKind ?? null} onChange={(v) => set("PropertyValueKind", v)} clearable /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Status")} data={["Preview", "Active", "Inactive"]} value={form.Status ?? null} onChange={(v) => set("Status", v)} clearable /></Grid.Col>
              <Grid.Col span={12}><MultiSelect label={t("Units")} data={unitData} value={form.Units ?? []} onChange={(v) => set("Units", v)} searchable clearable limit={100} /></Grid.Col>
              <Grid.Col span={12}>
                <AiTextarea label={t("Definition")} kind="property" value={form.Definition ?? ""} onChange={(v) => set("Definition", v)} context={() => ({ Name: form.Name, DataType: form.DataType, Units: form.Units ?? [] })} />
              </Grid.Col>
              <Grid.Col span={12}><Textarea label={t("Description")} value={form.Description ?? ""} onChange={(e) => set("Description", e.currentTarget.value)} autosize minRows={2} maxRows={6} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Example")} value={form.Example ?? ""} onChange={(e) => set("Example", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Method of measurement")} value={form.MethodOfMeasurement ?? ""} onChange={(e) => set("MethodOfMeasurement", e.currentTarget.value)} /></Grid.Col>
            </Grid>
    ),
    values: (
            <AllowedValuesEditor values={(form.AllowedValues ?? []) as AllowedValue[]} onChange={(v) => set("AllowedValues", v)} />
    ),
    details: (
            <Grid>
              <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Physical quantity")} value={form.PhysicalQuantity ?? ""} onChange={(e) => set("PhysicalQuantity", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Text format")} value={form.TextFormat ?? ""} onChange={(e) => set("TextFormat", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Pattern (regex)")} value={form.Pattern ?? ""} onChange={(e) => set("Pattern", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Min inclusive")} value={form.MinInclusive} onChange={(v) => set("MinInclusive", v)} /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Min exclusive")} value={form.MinExclusive} onChange={(v) => set("MinExclusive", v)} /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Max inclusive")} value={form.MaxInclusive} onChange={(v) => set("MaxInclusive", v)} /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><OptionalNumber label={t("Max exclusive")} value={form.MaxExclusive} onChange={(v) => set("MaxExclusive", v)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TagsInput label={t("Connected property codes")} data={propCodes} value={form.ConnectedPropertyCodes ?? []} onChange={(v) => set("ConnectedPropertyCodes", v)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><TagsInput label={t("Dynamic parameter property codes")} data={propCodes} value={form.DynamicParameterPropertyCodes ?? []} onChange={(v) => set("DynamicParameterPropertyCodes", v)} /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 2 }}><Toggle mt="lg" label={t("Is dynamic")} checked={!!form.IsDynamic} onChange={(e) => set("IsDynamic", e.currentTarget.checked)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><MultiSelect label={t("Countries of use")} data={countryData} value={form.CountriesOfUse ?? []} onChange={(v) => set("CountriesOfUse", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><Select label={t("Country of origin")} data={countryData} value={form.CountryOfOrigin ?? null} onChange={(v) => set("CountryOfOrigin", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={{ base: 6, sm: 3 }}><Select label={t("Creator language")} data={languageData} value={form.CreatorLanguageIsoCode ?? null} onChange={(v) => set("CreatorLanguageIsoCode", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Document reference")} data={[...new Map(res.referenceDocuments.filter((r) => r.Title).map((r) => [r.Title!, { value: r.Title!, label: `${r.Title} – ${r.Name}` }])).values()]} value={form.DocumentReference ?? null} onChange={(v) => set("DocumentReference", v)} searchable clearable limit={100} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label="UID" value={form.Uid ?? ""} onChange={(e) => set("Uid", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Owned URI")} value={form.OwnedUri ?? ""} onChange={(e) => set("OwnedUri", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TagsInput label={t("Subdivisions of use")} value={form.SubdivisionsOfUse ?? []} onChange={(v) => set("SubdivisionsOfUse", v)} /></Grid.Col>
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
    ),
    dimension: (
            <Grid>
              <Grid.Col span={12}><TextInput label={t("Dimension")} description={t("ISO 80000 dimension, e.g. '1 0 0 0 0 0 0'")} value={form.Dimension ?? ""} onChange={(e) => set("Dimension", e.currentTarget.value)} /></Grid.Col>
              {DIMENSIONS.map((k) => (
                <Grid.Col span={{ base: 6, sm: 3 }} key={k}><OptionalNumber label={t(k.replace("Dimension", ""))} value={form[k]} onChange={(v) => set(k, v)} integer /></Grid.Col>
              ))}
            </Grid>
    ),
    relations: (
            <RelationsEditor kind="property" relations={relations} onChange={(r) => setRelations(r as PropertyRelation[])} selfCode={code} />
    ),
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); if (!readOnly) void save(); }}>
      {section ? (
        <fieldset disabled={readOnly} className="ro-fieldset">{parts[section]}</fieldset>
      ) : (
        <Tabs defaultValue="general" keepMounted={false}>
          <Tabs.List mb="sm">
            <Tabs.Tab value="general">{t("General")}</Tabs.Tab>
            <Tabs.Tab value="values">{t("Allowed values")} ({(form.AllowedValues ?? []).length})</Tabs.Tab>
            <Tabs.Tab value="details">{t("Details")}</Tabs.Tab>
            <Tabs.Tab value="dimension">{t("Dimension")}</Tabs.Tab>
            <Tabs.Tab value="relations">{t("Relations")} ({relations.length})</Tabs.Tab>
          </Tabs.List>
          {(Object.keys(parts) as PropertySection[]).map((k) => <Tabs.Panel key={k} value={k}><fieldset disabled={readOnly} className="ro-fieldset">{parts[k]}</fieldset></Tabs.Panel>)}
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
