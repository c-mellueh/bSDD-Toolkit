/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Grid, Group, Modal, MultiSelect, Select, Tabs, TagsInput, TextInput, Textarea } from "@mantine/core";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { CLASS_STATUSES, CLASS_TYPES, clean, slugify } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { useUi } from "../state/ui";
import type { BsddClass, ClassRelation } from "../types";
import { AiTextarea, DateField, OptionalNumber, RelationsEditor, useResources } from "./fields";

const EDITABLE = [
  "Code", "Name", "ClassType", "Definition", "Description", "ParentClassCode", "RelatedIfcEntityNamesList", "Synonyms", "Status",
  "ReferenceCode", "CountriesOfUse", "CountryOfOrigin", "CreatorLanguageIsoCode", "DocumentReference", "OwnedUri",
  "ReplacedObjectCodes", "ReplacingObjectCodes", "SubdivisionsOfUse", "Uid", "RevisionNumber", "VersionNumber",
  "RevisionDateUtc", "VersionDateUtc", "ActivationDateUtc", "DeActivationDateUtc", "DeprecationExplanation", "VisualRepresentationUri",
];

export function ClassEditor() {
  const { t } = useTranslation();
  const target = useUi((s) => s.classEditor);
  const close = () => useUi.getState().set({ classEditor: null });
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const setActiveClass = useProject((s) => s.setActiveClass);
  const res = useResources();
  const [form, setForm] = useState<Record<string, any>>({});
  const [relations, setRelations] = useState<ClassRelation[]>([]);
  const [busy, setBusy] = useState(false);
  const existing = target?.code ? idx.classes.get(target.code) : undefined;

  useEffect(() => {
    if (!target) return;
    if (target.code) {
      const c = idx.classes.get(target.code);
      if (!c) return close();
      const f: Record<string, any> = {};
      for (const k of EDITABLE) f[k] = c[k] ?? null;
      setForm(f);
      setRelations(c.ClassRelations ?? []);
    } else {
      setForm({ Code: "", Name: "", ClassType: target.classType ?? "Class", ParentClassCode: target.parentCode ?? null, Status: "Preview" });
      setRelations([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  const ifcOptions = useMemo(() => res.ifcClasses.map((c) => c.code), [res.ifcClasses]);
  const parentOptions = useMemo(
    () => (doc?.dictionary.Classes ?? []).filter((c) => c.Code !== target?.code).map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` })),
    [doc, target],
  );

  if (!target || !doc) return null;

  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));
  const setName = (name: string) =>
    setForm((f) => {
      const next: Record<string, any> = { ...f, Name: name };
      if (!f.Code || f.Code === slugify(f.Name ?? "")) next.Code = slugify(name);
      return next;
    });

  const codeTaken = form.Code && form.Code !== target.code && idx.classes.has(form.Code);
  const codeError = !form.Code?.trim() ? t("Code must not be empty") : codeTaken ? t("Code exists already") : false;
  const nameError = !form.Name?.trim() ? t("Name must not be empty") : false;

  const save = async () => {
    if (codeError || nameError) return;
    setBusy(true);
    const data: Record<string, any> = clean({ ...form });
    let ok: string | undefined;
    if (existing) {
      const changed: Record<string, any> = {};
      for (const k of EDITABLE) if (JSON.stringify(data[k] ?? null) !== JSON.stringify(existing[k] ?? null)) changed[k] = data[k];
      if (JSON.stringify(relations) !== JSON.stringify(existing.ClassRelations ?? [])) changed.ClassRelations = relations;
      ok = Object.keys(changed).length ? await attempt(() => op<string>("class.update", { code: existing.Code, data: changed })) : existing.Code;
    } else {
      ok = await attempt(() => op<string>("class.create", { data: { ...data, ClassRelations: relations }, parent_code: data.ParentClassCode ?? null }));
    }
    setBusy(false);
    if (ok) {
      setActiveClass(ok);
      close();
    }
  };

  const countryData = res.countries.map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` }));
  const languageData = [...new Set(res.languages.map((l) => l.IsoCode))].map((c) => ({ value: c, label: `${res.languages.find((l) => l.IsoCode === c)?.Name} (${c})` }));

  return (
    <Modal opened onClose={close} title={existing ? t("Edit class: {{name}}", { name: existing.Name }) : t("New class")} size="xl">
      <form onSubmit={(e) => { e.preventDefault(); void save(); }}>
        <Tabs defaultValue="general" keepMounted={false}>
          <Tabs.List mb="sm">
            <Tabs.Tab value="general">{t("General")}</Tabs.Tab>
            <Tabs.Tab value="details">{t("Details")}</Tabs.Tab>
            <Tabs.Tab value="relations">{t("Relations")} ({relations.length})</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="general">
            <Grid>
              <Grid.Col span={6}><TextInput label={t("Name")} value={form.Name ?? ""} onChange={(e) => setName(e.currentTarget.value)} error={nameError} data-autofocus required /></Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Code")} value={form.Code ?? ""} onChange={(e) => set("Code", e.currentTarget.value)} error={codeError} required /></Grid.Col>
              <Grid.Col span={4}><Select label={t("Class type")} data={CLASS_TYPES} value={form.ClassType ?? "Class"} onChange={(v) => set("ClassType", v)} allowDeselect={false} /></Grid.Col>
              <Grid.Col span={4}><Select label={t("Status")} data={CLASS_STATUSES} value={form.Status ?? null} onChange={(v) => set("Status", v)} clearable /></Grid.Col>
              <Grid.Col span={4}><Select label={t("Parent class")} data={parentOptions} value={form.ParentClassCode ?? null} onChange={(v) => set("ParentClassCode", v)} searchable clearable limit={100} /></Grid.Col>
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
          </Tabs.Panel>
          <Tabs.Panel value="details">
            <Grid>
              <Grid.Col span={4}><TextInput label={t("Reference code")} value={form.ReferenceCode ?? ""} onChange={(e) => set("ReferenceCode", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={4}><TextInput label="UID" value={form.Uid ?? ""} onChange={(e) => set("Uid", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={4}><TextInput label={t("Document reference")} value={form.DocumentReference ?? ""} onChange={(e) => set("DocumentReference", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={6}><MultiSelect label={t("Countries of use")} data={countryData} value={form.CountriesOfUse ?? []} onChange={(v) => set("CountriesOfUse", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={6}><Select label={t("Country of origin")} data={countryData} value={form.CountryOfOrigin ?? null} onChange={(v) => set("CountryOfOrigin", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={6}><Select label={t("Creator language")} data={languageData} value={form.CreatorLanguageIsoCode ?? null} onChange={(v) => set("CreatorLanguageIsoCode", v)} searchable clearable /></Grid.Col>
              <Grid.Col span={6}><TagsInput label={t("Subdivisions of use")} value={form.SubdivisionsOfUse ?? []} onChange={(v) => set("SubdivisionsOfUse", v)} /></Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Owned URI")} value={form.OwnedUri ?? ""} onChange={(e) => set("OwnedUri", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Visual representation URI")} value={form.VisualRepresentationUri ?? ""} onChange={(e) => set("VisualRepresentationUri", e.currentTarget.value)} /></Grid.Col>
              <Grid.Col span={6}><TagsInput label={t("Replaced object codes")} value={form.ReplacedObjectCodes ?? []} onChange={(v) => set("ReplacedObjectCodes", v)} /></Grid.Col>
              <Grid.Col span={6}><TagsInput label={t("Replacing object codes")} value={form.ReplacingObjectCodes ?? []} onChange={(v) => set("ReplacingObjectCodes", v)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Version number")} value={form.VersionNumber} onChange={(v) => set("VersionNumber", v)} integer /></Grid.Col>
              <Grid.Col span={3}><DateField label={t("Version date")} value={form.VersionDateUtc} onChange={(v) => set("VersionDateUtc", v)} /></Grid.Col>
              <Grid.Col span={3}><OptionalNumber label={t("Revision number")} value={form.RevisionNumber} onChange={(v) => set("RevisionNumber", v)} integer /></Grid.Col>
              <Grid.Col span={3}><DateField label={t("Revision date")} value={form.RevisionDateUtc} onChange={(v) => set("RevisionDateUtc", v)} /></Grid.Col>
              <Grid.Col span={3}><DateField label={t("Activation date")} value={form.ActivationDateUtc} onChange={(v) => set("ActivationDateUtc", v)} /></Grid.Col>
              <Grid.Col span={3}><DateField label={t("Deactivation date")} value={form.DeActivationDateUtc} onChange={(v) => set("DeActivationDateUtc", v)} /></Grid.Col>
              <Grid.Col span={6}><TextInput label={t("Deprecation explanation")} value={form.DeprecationExplanation ?? ""} onChange={(e) => set("DeprecationExplanation", e.currentTarget.value)} /></Grid.Col>
            </Grid>
          </Tabs.Panel>
          <Tabs.Panel value="relations">
            <RelationsEditor kind="class" relations={relations} onChange={(r) => setRelations(r as ClassRelation[])} selfCode={target.code} />
          </Tabs.Panel>
        </Tabs>
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={close}>{t("Cancel")}</Button>
          <Button type="submit" loading={busy} disabled={!!codeError || !!nameError}>{existing ? t("Save") : t("Create")}</Button>
        </Group>
      </form>
    </Modal>
  );
}

export type { BsddClass };
