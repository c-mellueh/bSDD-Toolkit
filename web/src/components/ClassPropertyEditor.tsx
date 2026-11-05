/* eslint-disable @typescript-eslint/no-explicit-any */
import { ActionIcon, Autocomplete, Button, Checkbox, Grid, Group, Modal, SegmentedControl, Select, Tabs, Text, TextInput, Textarea, Tooltip } from "@mantine/core";
import { IconEdit, IconExternalLink, IconPlus } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { GOP, clean, codeFromUri, internalCode, isUri, psetsOfClass, uniqueCode } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { openUi, useUi } from "../state/ui";
import type { AllowedValue } from "../types";
import { AllowedValuesEditor, OptionalNumber, useResources } from "./fields";

const EDITABLE = [
  "Code", "PropertyCode", "PropertyUri", "Description", "PropertySet", "Unit", "PredefinedValue", "IsRequired", "IsWritable",
  "MaxExclusive", "MaxInclusive", "MinExclusive", "MinInclusive", "Pattern", "OwnedUri", "PropertyType", "SortNumber", "Symbol", "AllowedValues",
];

export function ClassPropertyEditor() {
  const { t } = useTranslation();
  const target = useUi((s) => s.cpEditor);
  const close = () => useUi.getState().set({ cpEditor: null });
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const res = useResources();
  const [form, setForm] = useState<Record<string, any>>({});
  const [refMode, setRefMode] = useState<"code" | "uri">("code");
  const [busy, setBusy] = useState(false);
  const cls = target ? idx.classes.get(target.classCode) : undefined;
  const existing = target?.code ? cls?.ClassProperties?.find((cp) => cp.Code === target.code) : undefined;

  useEffect(() => {
    if (!target || !cls) return;
    if (existing) {
      const f: Record<string, any> = {};
      for (const k of EDITABLE) f[k] = (existing as any)[k] ?? null;
      f.AllowedValues = existing.AllowedValues ?? [];
      setForm(f);
      setRefMode(existing.PropertyUri ? "uri" : "code");
    } else {
      setForm({ Code: "", PropertyCode: "", PropertySet: cls.ClassType === GOP ? cls.Name : target.pset ?? "", IsRequired: true, AllowedValues: [] });
      setRefMode("code");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  const propOptions = useMemo(() => (doc?.dictionary.Properties ?? []).map((p) => ({ value: p.Code, label: `${p.Name} (${p.Code})` })), [doc]);
  if (!target || !cls || !doc) return null;
  const d = doc.dictionary;

  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));
  const prop =
    refMode === "code" ? idx.properties.get(form.PropertyCode ?? "") : form.PropertyUri ? idx.properties.get(internalCode(d, form.PropertyUri, "prop") ?? "") : undefined;
  const siblingCodes = (cls.ClassProperties ?? []).map((c) => c.Code).filter((c) => c !== existing?.Code);

  const chooseProperty = (code: string) =>
    setForm((f) => {
      const next: Record<string, any> = { ...f, PropertyCode: code };
      const p = idx.properties.get(code);
      if (!f.Code || f.Code === f.PropertyCode || siblingCodes.includes(f.Code)) next.Code = uniqueCode(code, siblingCodes);
      if (p?.Units?.length && !f.Unit) next.Unit = p.Units[0];
      return next;
    });

  const refError =
    refMode === "code"
      ? !form.PropertyCode
        ? t("Select a property")
        : !idx.properties.has(form.PropertyCode)
          ? t("Property does not exist")
          : false
      : !isUri(form.PropertyUri)
        ? t("Enter a valid URI")
        : false;
  const codeError = !form.Code?.trim() ? t("Code must not be empty") : siblingCodes.includes(form.Code) ? t("Code exists already in this class") : false;

  const units = prop?.Units?.length ? prop.Units : res.units.map((u) => u.Code);

  const save = async () => {
    if (refError || codeError) return;
    setBusy(true);
    const data: Record<string, any> = clean({ ...form });
    if (refMode === "code") data.PropertyUri = null;
    else data.PropertyCode = null;
    data.AllowedValues = form.AllowedValues ?? [];
    let ok: string | undefined;
    if (existing) {
      const changed: Record<string, any> = {};
      for (const k of EDITABLE) if (JSON.stringify(data[k] ?? null) !== JSON.stringify((existing as any)[k] ?? (k === "AllowedValues" ? [] : null))) changed[k] = data[k];
      if (changed.PropertyCode !== undefined || changed.PropertyUri !== undefined) {
        changed.PropertyCode = data.PropertyCode;
        changed.PropertyUri = data.PropertyUri;
      }
      ok = Object.keys(changed).length ? await attempt(() => op<string>("cp.update", { class_code: cls.Code, code: existing.Code, data: changed })) : existing.Code;
    } else {
      ok = await attempt(() => op<string>("cp.create", { class_code: cls.Code, data }));
    }
    setBusy(false);
    if (ok) close();
  };

  const createProperty = () =>
    openUi({
      propertyEditor: {
        onCreated: (code) => {
          setRefMode("code");
          chooseProperty(code);
        },
      },
    });

  return (
    <Modal opened onClose={close} title={existing ? t("Edit class property: {{code}}", { code: existing.Code }) : t("New class property in {{cls}}", { cls: cls.Name })} size="xl">
      <form onSubmit={(e) => { e.preventDefault(); void save(); }}>
        <Tabs defaultValue="general" keepMounted={false}>
          <Tabs.List mb="sm">
            <Tabs.Tab value="general">{t("General")}</Tabs.Tab>
            <Tabs.Tab value="values">{t("Allowed values")} ({(form.AllowedValues ?? []).length})</Tabs.Tab>
            <Tabs.Tab value="constraints">{t("Constraints")}</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="general">
            <Grid>
              <Grid.Col span={12}>
                <Group gap="xs" align="flex-end" wrap="nowrap">
                  <SegmentedControl size="xs" value={refMode} onChange={(v) => setRefMode(v as "code" | "uri")} data={[{ value: "code", label: t("Dictionary property") }, { value: "uri", label: t("External URI") }]} />
                  {refMode === "code" ? (
                    <Select
                      label={t("Property")}
                      data={propOptions}
                      value={form.PropertyCode || null}
                      onChange={(v) => v && chooseProperty(v)}
                      searchable
                      limit={100}
                      style={{ flex: 1 }}
                      error={refError}
                      data-autofocus
                    />
                  ) : (
                    <TextInput label={t("Property URI")} value={form.PropertyUri ?? ""} onChange={(e) => {
                      const v = e.currentTarget.value;
                      setForm((f) => ({ ...f, PropertyUri: v, Code: f.Code || (isUri(v) ? uniqueCode(codeFromUri(v), siblingCodes) : f.Code) }));
                    }} style={{ flex: 1 }} error={refError} />
                  )}
                  {refMode === "code" && prop && (
                    <Tooltip label={t("Edit property")}><ActionIcon variant="light" mb={2} onClick={() => openUi({ propertyEditor: { code: prop.Code } })}><IconEdit size={16} /></ActionIcon></Tooltip>
                  )}
                  {refMode === "code" && (
                    <Tooltip label={t("Create new property")}><ActionIcon variant="light" mb={2} onClick={createProperty}><IconPlus size={16} /></ActionIcon></Tooltip>
                  )}
                  {refMode === "uri" && isUri(form.PropertyUri) && (
                    <Tooltip label={t("Open in browser")}><ActionIcon variant="light" mb={2} component="a" href={form.PropertyUri} target="_blank"><IconExternalLink size={16} /></ActionIcon></Tooltip>
                  )}
                </Group>
              </Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => set("Code", e.currentTarget.value)} error={codeError} required /></Grid.Col>
              <Grid.Col span={6}>
                <Autocomplete label={t("Property set")} data={psetsOfClass(doc, cls).filter(Boolean)} value={form.PropertySet ?? ""} onChange={(v) => set("PropertySet", v)} disabled={cls.ClassType === GOP} />
              </Grid.Col>
              <Grid.Col span={12}>
                <Textarea label={t("Description")} value={form.Description ?? ""} onChange={(e) => set("Description", e.currentTarget.value)} placeholder={prop?.Description || prop?.Definition || ""} autosize minRows={2} maxRows={6} />
              </Grid.Col>
              <Grid.Col span={4}><Select label={t("Unit")} data={[...new Set(units)]} value={form.Unit ?? null} onChange={(v) => set("Unit", v)} searchable clearable limit={100} /></Grid.Col>
              <Grid.Col span={4}><TextInput label={t("Predefined value")} value={form.PredefinedValue ?? ""} onChange={(e) => set("PredefinedValue", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={4}><Select label={t("Property type")} data={["Property", "Dependency"]} value={form.PropertyType ?? null} onChange={(v) => set("PropertyType", v)} clearable /></Grid.Col>
              <Grid.Col span={4}><Checkbox mt="md" label={t("Is required")} checked={!!form.IsRequired} onChange={(e) => set("IsRequired", e.currentTarget.checked)} /></Grid.Col>
              <Grid.Col span={4}><Checkbox mt="md" label={t("Is writable")} checked={!!form.IsWritable} onChange={(e) => set("IsWritable", e.currentTarget.checked)} /></Grid.Col>
              {prop && (
                <Grid.Col span={12}>
                  <Text size="xs" c="dimmed">
                    {t("Property")}: {prop.Name} · {t("Datatype")}: {prop.DataType ?? "-"} · {t("Units")}: {(prop.Units ?? []).join(", ") || "-"}
                  </Text>
                </Grid.Col>
              )}
            </Grid>
          </Tabs.Panel>
          <Tabs.Panel value="values">
            <AllowedValuesEditor values={(form.AllowedValues ?? []) as AllowedValue[]} onChange={(v) => set("AllowedValues", v)} inherited={prop?.AllowedValues} />
          </Tabs.Panel>
          <Tabs.Panel value="constraints">
            <Grid>
              <Grid.Col span={3}><OptionalNumber label={t("Min inclusive")} value={form.MinInclusive} onChange={(v) => set("MinInclusive", v)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Min exclusive")} value={form.MinExclusive} onChange={(v) => set("MinExclusive", v)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Max inclusive")} value={form.MaxInclusive} onChange={(v) => set("MaxInclusive", v)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Max exclusive")} value={form.MaxExclusive} onChange={(v) => set("MaxExclusive", v)} /></Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Pattern (regex)")} value={form.Pattern ?? ""} onChange={(e) => set("Pattern", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={3}><TextInput label={t("Symbol")} value={form.Symbol ?? ""} onChange={(e) => set("Symbol", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Sort number")} value={form.SortNumber} onChange={(v) => set("SortNumber", v)} integer /></Grid.Col>
              <Grid.Col span={12}><TextInput label={t("Owned URI")} value={form.OwnedUri ?? ""} onChange={(e) => set("OwnedUri", e.currentTarget.value)} /></Grid.Col>
            </Grid>
          </Tabs.Panel>
        </Tabs>
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={close}>{t("Cancel")}</Button>
          <Button type="submit" loading={busy} disabled={!!refError || !!codeError}>{existing ? t("Save") : t("Create")}</Button>
        </Group>
      </form>
    </Modal>
  );
}
