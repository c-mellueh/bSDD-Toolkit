/* eslint-disable @typescript-eslint/no-explicit-any */
import { Badge, Button, Grid, Group, MultiSelect, Select, SimpleGrid, Stack, Tabs, TagsInput, Text, TextInput, Textarea, Tooltip } from "@mantine/core";
import { Toggle } from "../components/Toggle";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { DATA_TYPES, PROPERTY_VALUE_KINDS, clean, slugify } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { useReadOnly } from "../state/readonly";
import type { AllowedValue, BsddProperty, PropertyRelation } from "../types";
import { SaveBar, changedKeys, mergeRemote, same, snap } from "./SaveBar";
import { CommonDetailCards, DetailCard, DetailGrid, DetailRow, rangePreview } from "./DetailSections";
import { IconAtom2, IconLink, IconRuler2 } from "@tabler/icons-react";
import { AiTextarea, AllowedValuesEditor, OptionalNumber, RelationsEditor, useResources } from "../components/fields";

const DIMENSIONS = [
  "DimensionLength", "DimensionMass", "DimensionTime", "DimensionElectricCurrent", "DimensionThermodynamicTemperature",
  "DimensionAmountOfSubstance", "DimensionLuminousIntensity",
] as const;
/** ISO 80000 symbols of the base quantities */
const DIMENSION_SYMBOL: Record<(typeof DIMENSIONS)[number], string> = {
  DimensionLength: "L", DimensionMass: "M", DimensionTime: "T", DimensionElectricCurrent: "I",
  DimensionThermodynamicTemperature: "Θ", DimensionAmountOfSubstance: "N", DimensionLuminousIntensity: "J",
};
const EDITABLE = [
  "Code", "Name", "Definition", "Description", "DataType", "Units", "Example", "ActivationDateUtc", "ConnectedPropertyCodes",
  "CountriesOfUse", "CountryOfOrigin", "CreatorLanguageIsoCode", "DeActivationDateUtc", "DeprecationExplanation", "Dimension",
  ...DIMENSIONS, "DocumentReference", "DynamicParameterPropertyCodes", "IsDynamic", "MaxExclusive", "MaxInclusive", "MinExclusive",
  "MinInclusive", "MethodOfMeasurement", "OwnedUri", "Pattern", "PhysicalQuantity", "PropertyValueKind", "ReplacedObjectCodes",
  "ReplacingObjectCodes", "RevisionDateUtc", "RevisionNumber", "Status", "SubdivisionsOfUse", "TextFormat", "Uid", "VersionDateUtc",
  "VersionNumber", "VisualRepresentationUri", "AllowedValues",
];

export type PropertySection = "general" | "values" | "details" | "relations";

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

  // "empty" errors only after the user touched the field (not right when a new form opens)
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const touch = (k: string) => setTouched((s) => (s[k] ? s : { ...s, [k]: true }));
  const codeEmpty = !form.Code?.trim();
  const nameEmpty = !form.Name?.trim();
  const codeError = codeEmpty ? (touched.Code || touched.Name) && t("Code must not be empty") : form.Code !== code && idx.properties.has(form.Code) ? t("Code exists already") : false;
  const nameError = nameEmpty ? touched.Name && t("Name must not be empty") : false;
  const invalid = !!codeError || !!nameError || codeEmpty || nameEmpty;

  const save = async () => {
    if (invalid) {
      setTouched({ Name: true, Code: true });
      return;
    }
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
  const languageData = [...new Set(res.languages.map((l) => l.IsoCode))].map((c) => ({ value: c, label: `${res.languages.find((l) => l.IsoCode === c)?.Name} (${c})` }));
  const unitData = [...new Set([...res.units.map((u) => u.Code), ...(form.Units ?? [])])];
  const propCodes = (doc.dictionary.Properties ?? []).map((p) => p.Code);

  const parts: Record<PropertySection, React.ReactNode> = {
    general: (
            <Grid>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Name")} value={form.Name ?? ""} onChange={(e) => setName(e.currentTarget.value)} onBlur={() => touch("Name")} error={nameError || undefined} data-autofocus={!inline || undefined} required /></Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => { touch("Code"); set("Code", e.currentTarget.value); }} onBlur={() => touch("Code")} error={codeError || undefined} required /></Grid.Col>
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
            <DetailGrid>
              <DetailCard
                icon={<IconRuler2 size={18} />}
                color="indigo"
                title={t("Value constraints")}
                hint={t("Which values are valid for this property")}
                values={[form.PhysicalQuantity, form.TextFormat, form.Pattern, form.MinInclusive, form.MinExclusive, form.MaxInclusive, form.MaxExclusive]}
              >
                <Stack gap="xs">
                  <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="xs">
                    <TextInput label={t("Physical quantity")} placeholder={t("e.g. length")} value={form.PhysicalQuantity ?? ""} onChange={(e) => set("PhysicalQuantity", e.currentTarget.value)} />
                    <TextInput label={t("Text format")} placeholder="UTF-8" value={form.TextFormat ?? ""} onChange={(e) => set("TextFormat", e.currentTarget.value)} />
                  </SimpleGrid>
                  <TextInput label={t("Pattern (regex)")} classNames={{ input: "mono" }} placeholder="^[A-Z]{2}[0-9]+$" value={form.Pattern ?? ""} onChange={(e) => set("Pattern", e.currentTarget.value)} />
                  <DetailRow label={t("Minimum")}>
                    <OptionalNumber label={t("inclusive (≥)")} value={form.MinInclusive} onChange={(v) => set("MinInclusive", v)} />
                    <OptionalNumber label={t("exclusive (>)")} value={form.MinExclusive} onChange={(v) => set("MinExclusive", v)} />
                  </DetailRow>
                  <DetailRow label={t("Maximum")}>
                    <OptionalNumber label={t("inclusive (≤)")} value={form.MaxInclusive} onChange={(v) => set("MaxInclusive", v)} />
                    <OptionalNumber label={t("exclusive (<)")} value={form.MaxExclusive} onChange={(v) => set("MaxExclusive", v)} />
                  </DetailRow>
                  {rangePreview(form) && (
                    <Group gap={6}>
                      <Text size="xs" c="dimmed">{t("Allowed range")}:</Text>
                      <Badge variant="light" color="indigo" className="mono" tt="none">{rangePreview(form)}</Badge>
                    </Group>
                  )}
                </Stack>
              </DetailCard>

              <DetailCard
                icon={<IconLink size={18} />}
                color="cyan"
                title={t("Linked properties")}
                hint={t("Properties that belong together or that this property depends on")}
                values={[form.ConnectedPropertyCodes, form.IsDynamic || undefined, form.DynamicParameterPropertyCodes]}
              >
                <Stack gap="xs">
                  <TagsInput label={t("Connected property codes")} data={propCodes} value={form.ConnectedPropertyCodes ?? []} onChange={(v) => set("ConnectedPropertyCodes", v)} />
                  <Toggle label={t("Is dynamic")} description={t("The value is calculated from other properties")} checked={!!form.IsDynamic} onChange={(e) => set("IsDynamic", e.currentTarget.checked)} />
                  {(form.IsDynamic || (form.DynamicParameterPropertyCodes ?? []).length > 0) && (
                    <TagsInput label={t("Dynamic parameter property codes")} data={propCodes} value={form.DynamicParameterPropertyCodes ?? []} onChange={(v) => set("DynamicParameterPropertyCodes", v)} />
                  )}
                </Stack>
              </DetailCard>

              <DetailCard
                icon={<IconAtom2 size={18} />}
                color="pink"
                title={t("Dimension")}
                hint={t("ISO 80000 dimension: exponents of the base quantities")}
                values={[form.Dimension, ...DIMENSIONS.map((k) => form[k])]}
              >
                <Stack gap="xs">
                  <TextInput label={t("Dimension")} classNames={{ input: "mono" }} placeholder="1 0 0 0 0 0 0" value={form.Dimension ?? ""} onChange={(e) => set("Dimension", e.currentTarget.value)} />
                  <div className="dimension-grid">
                    {DIMENSIONS.map((k) => (
                      <Tooltip key={k} label={t(k.replace("Dimension", ""))}>
                        <div>
                          <OptionalNumber label={DIMENSION_SYMBOL[k]} value={form[k]} onChange={(v) => set(k, v)} integer hideControls />
                        </div>
                      </Tooltip>
                    ))}
                  </div>
                </Stack>
              </DetailCard>

              <CommonDetailCards
                form={form}
                set={set}
                countryData={countryData}
                languageData={languageData}
                documentReference={<Select label={t("Document reference")} data={[...new Map(res.referenceDocuments.filter((r) => r.Title).map((r) => [r.Title!, { value: r.Title!, label: `${r.Title} – ${r.Name}` }])).values()]} value={form.DocumentReference ?? null} onChange={(v) => set("DocumentReference", v)} searchable clearable limit={100} />}
              />
            </DetailGrid>
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
            <Tabs.Tab value="relations">{t("Relations")} ({relations.length})</Tabs.Tab>
          </Tabs.List>
          {(Object.keys(parts) as PropertySection[]).map((k) => <Tabs.Panel key={k} value={k}><fieldset disabled={readOnly} className="ro-fieldset">{parts[k]}</fieldset></Tabs.Panel>)}
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
