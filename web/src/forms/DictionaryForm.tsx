/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Checkbox, Grid, Group, Select, TextInput, Textarea } from "@mantine/core";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { DateField, useResources } from "../components/fields";
import { clean } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { SaveBar, changedKeys, mergeRemote, snap } from "./SaveBar";

const FIELDS = [
  "OrganizationCode", "DictionaryCode", "DictionaryName", "DictionaryVersion", "LanguageIsoCode", "LanguageOnly", "UseOwnUri", "DictionaryUri",
  "License", "LicenseUrl", "ChangeRequestEmailAddress", "ModelVersion", "MoreInfoUrl", "QualityAssuranceProcedure", "QualityAssuranceProcedureUrl",
  "ReleaseDate", "Status",
];

export function DictionaryForm({ inline, onDone, onCancel }: { inline?: boolean; onDone?: () => void; onCancel?: () => void }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const res = useResources();
  const d = doc?.dictionary;
  const fromDoc = () => {
    const f: Record<string, any> = {};
    for (const k of FIELDS) f[k] = d?.[k] ?? null;
    return f;
  };
  const [form, setForm] = useState<Record<string, any>>(fromDoc);
  const [base, setBase] = useState<Record<string, any>>(fromDoc);
  const [busy, setBusy] = useState(false);
  const dirty = snap(form) !== snap(base);
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  const reset = () => {
    const f = fromDoc();
    setForm(f);
    setBase(f);
  };
  // follow remote changes while the form is clean
  const header = snap(...FIELDS.map((k) => d?.[k] ?? null));
  useEffect(() => {
    if (!dirtyRef.current) reset();
    else {
      const next = fromDoc();
      setForm((f) => mergeRemote(f, base, next));
      setBase(next);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [header]);

  if (!doc) return null;
  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));
  const errors: Record<string, string | false> = {
    OrganizationCode: !form.OrganizationCode?.trim() && t("Required"),
    DictionaryCode: !form.DictionaryCode?.trim() && t("Required"),
    DictionaryName: !form.DictionaryName?.trim() && t("Required"),
    LanguageIsoCode: !form.LanguageIsoCode && t("Required"),
    DictionaryVersion: !/^(0|[1-9]\d*)(\.(0|[1-9]\d*)){0,2}$/.test(form.DictionaryVersion ?? "") && t("Format: 1, 1.0 or 1.0.0"),
    DictionaryUri: form.UseOwnUri && !form.DictionaryUri?.trim() ? t("Required when using own URIs") : false,
  };
  const invalid = Object.values(errors).some(Boolean);

  const save = async () => {
    if (invalid) return;
    const data = clean({ ...form });
    const changed: Record<string, any> = {};
    for (const k of changedKeys(FIELDS, data, clean({ ...base }))) changed[k] = data[k];
    if (!Object.keys(changed).length) {
      setBase(form);
      return onDone?.();
    }
    setBusy(true);
    const ok = await attempt(() => op("dict.update", { data: changed }).then(() => true));
    setBusy(false);
    if (ok) {
      setBase(form);
      onDone?.();
    }
  };

  const languages = [...new Set(res.languages.map((l) => l.IsoCode))];

  return (
    <form onSubmit={(e) => { e.preventDefault(); void save(); }}>
        <Grid>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Organization code")} value={form.OrganizationCode ?? ""} onChange={(e) => set("OrganizationCode", e.currentTarget.value)} error={errors.OrganizationCode} required /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Dictionary code")} value={form.DictionaryCode ?? ""} onChange={(e) => set("DictionaryCode", e.currentTarget.value)} error={errors.DictionaryCode} required /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 8 }}><TextInput label={t("Dictionary name")} value={form.DictionaryName ?? ""} onChange={(e) => set("DictionaryName", e.currentTarget.value)} error={errors.DictionaryName} required /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Version")} value={form.DictionaryVersion ?? ""} onChange={(e) => set("DictionaryVersion", e.currentTarget.value)} error={errors.DictionaryVersion} required /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Language")} data={languages.length ? languages : [form.LanguageIsoCode ?? "en-GB"]} value={form.LanguageIsoCode ?? null} onChange={(v) => set("LanguageIsoCode", v)} searchable error={errors.LanguageIsoCode} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 4 }}><Select label={t("Status")} data={["Preview", "Active", "Inactive"]} value={form.Status ?? null} onChange={(v) => set("Status", v)} clearable /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 4 }}><TextInput label={t("Model version")} value={form.ModelVersion ?? ""} onChange={(e) => set("ModelVersion", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><Checkbox label={t("Language only")} checked={!!form.LanguageOnly} onChange={(e) => set("LanguageOnly", e.currentTarget.checked)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><Checkbox label={t("Use own URI")} checked={!!form.UseOwnUri} onChange={(e) => set("UseOwnUri", e.currentTarget.checked)} /></Grid.Col>
          {form.UseOwnUri && <Grid.Col span={12}><TextInput label={t("Dictionary URI")} value={form.DictionaryUri ?? ""} onChange={(e) => set("DictionaryUri", e.currentTarget.value)} error={errors.DictionaryUri} /></Grid.Col>}
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("License")} value={form.License ?? ""} onChange={(e) => set("License", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("License URL")} value={form.LicenseUrl ?? ""} onChange={(e) => set("LicenseUrl", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Change request e-mail")} value={form.ChangeRequestEmailAddress ?? ""} onChange={(e) => set("ChangeRequestEmailAddress", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("More info URL")} value={form.MoreInfoUrl ?? ""} onChange={(e) => set("MoreInfoUrl", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={12}><Textarea label={t("Quality assurance procedure")} value={form.QualityAssuranceProcedure ?? ""} onChange={(e) => set("QualityAssuranceProcedure", e.currentTarget.value)} autosize minRows={2} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><TextInput label={t("Quality assurance procedure URL")} value={form.QualityAssuranceProcedureUrl ?? ""} onChange={(e) => set("QualityAssuranceProcedureUrl", e.currentTarget.value)} /></Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}><DateField label={t("Release date")} value={form.ReleaseDate} onChange={(v) => set("ReleaseDate", v)} /></Grid.Col>
        </Grid>
      {inline ? (
        <SaveBar dirty={dirty} busy={busy} invalid={invalid} onSave={save} onDiscard={reset} />
      ) : (
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={onCancel}>{t("Cancel")}</Button>
          <Button type="submit" loading={busy} disabled={invalid}>{t("Save")}</Button>
        </Group>
      )}
    </form>
  );
}
