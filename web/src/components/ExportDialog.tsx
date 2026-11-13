/* eslint-disable @typescript-eslint/no-explicit-any */
import { Alert, Badge, Button, Divider, Grid, Group, Modal, Radio, Select, Stack, TagsInput, Text, TextInput } from "@mantine/core";
import { Toggle } from "./Toggle";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { DayField } from "./fields";
import { api, downloadFile } from "../api";
import { notifyError, notifyOk } from "../notify";
import { useProject } from "../state/project";
import { storageGet, storageSet } from "../state/settings";
import { useUi, type ExportKind } from "../state/ui";
import { activeKeys } from "./LoinEditor";
import { LoinMatrix } from "./LoinMatrix";

const TITLES: Record<ExportKind, string> = {
  excel: "Export Excel",
  ids: "Export IDS",
  iso23386: "Export ISO 23386",
  iso7817: "Export ISO 7817-3 (LOIN)",
  "revit-psets": "Export Revit property sets",
  "revit-shared": "Export Revit shared parameters",
};

const IFC_TYPES = ["IFCLABEL", "IFCTEXT", "IFCBOOLEAN", "IFCINTEGER", "IFCREAL", "IFCDATETIME", "IFCDATE", "IFCIDENTIFIER"];

interface Candidate {
  pset: string;
  count: number;
  properties: string[];
}

export function ExportDialog() {
  const { t } = useTranslation();
  const kind = useUi((s) => s.exportKind);
  const close = () => useUi.getState().set({ exportKind: null });
  const projectId = useProject((s) => s.projectId);
  const loin = useProject((s) => s.doc?.extras.loin);
  const language = useProject((s) => s.doc?.dictionary.LanguageIsoCode);
  const storeKey = `bsdd-export-${projectId}-${kind}`;
  const [scope, setScope] = useState<"all" | "loin">("all");
  const [specs, setSpecs] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [busy, setBusy] = useState(false);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  // default selection: the combinations ticked in the purpose × milestone matrix
  const filled = useMemo(() => activeKeys(loin), [loin]);

  useEffect(() => {
    if (!kind) return;
    const saved = storageGet<Record<string, any>>(storeKey, {});
    setScope(kind === "iso7817" ? "loin" : saved.scope ?? (filled.length ? "loin" : "all"));
    setSpecs(saved.specs?.filter((k: string) => filled.includes(k)) ?? filled);
    setSettings(saved.settings ?? {});
    if (kind === "ids") {
      api(`/api/projects/${projectId}/ids/candidates`, { method: "POST", json: {} })
        .then((r) => {
          setCandidates(r.candidates);
          setSettings((s) => ({
            settings: { ...r.default_settings, ...(s.settings ?? {}) },
            metadata: { ...r.default_metadata, ...(s.metadata ?? {}) },
          }));
        })
        .catch(notifyError);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kind]);

  if (!kind || !projectId) return null;

  const run = async () => {
    setBusy(true);
    try {
      const body = { specs: scope === "all" ? null : specs.filter((k) => filled.includes(k)), settings, lang: settings.lang ?? (language?.startsWith("de") ? "de" : "en") };
      storageSet(storeKey, { scope, specs, settings });
      const n = await downloadFile(`/api/projects/${projectId}/export/${kind}`, body);
      notifyOk(t("Export done ({{n}} items)", { n: n ?? 0 }));
      close();
    } catch (e) {
      notifyError(e);
    } finally {
      setBusy(false);
    }
  };

  const ids = settings.settings ?? {};
  const meta = settings.metadata ?? {};
  const setIds = (patch: Record<string, any>) => setSettings((s) => ({ ...s, settings: { ...(s.settings ?? {}), ...patch } }));
  const setMeta = (patch: Record<string, any>) => setSettings((s) => ({ ...s, metadata: { ...(s.metadata ?? {}), ...patch } }));
  const mainPset = candidates.find((c) => c.pset === ids.main_pset);

  return (
    // the dialog grows with the matrix (up to the window width) instead of having a fixed width
    <Modal opened onClose={close} title={t(TITLES[kind])} size="auto" styles={{ content: { minWidth: `min(${kind === "ids" ? 880 : 520}px, 95vw)`, maxWidth: "95vw" } }}>
      <Stack className="export-fit">
        {kind !== "iso7817" && (
          <Radio.Group value={scope} onChange={(v) => setScope(v as "all" | "loin")} label={t("Scope")}>
            <Group mt={4}>
              <Radio value="all" label={t("Whole dictionary")} />
              <Radio value="loin" label={t("Level of Information Need selection")} />
            </Group>
          </Radio.Group>
        )}
        {(scope === "loin" || kind === "iso7817") && (
          <>
            {filled.length === 0 && <Alert color="yellow">{t("No combination is ticked in the purpose × milestone matrix yet. Open Information need (LOIN) to set it up.")}</Alert>}
            {loin && (loin.purposes ?? []).length > 0 && (loin.milestones ?? []).length > 0 && (
              <>
                <Text size="sm" c="dimmed">{t("Choose the combinations to export. Hold the left mouse button and drag over cells to set them all to the same value.")}</Text>
                <LoinMatrix
                  loin={loin}
                  isOn={(k) => specs.includes(k)}
                  onChange={(keys, value) => setSpecs((cur) => (value ? [...new Set([...cur, ...keys])] : cur.filter((k) => !keys.includes(k))))}
                  unavailable={(k) => (filled.includes(k) ? undefined : t("Not ticked in the purpose × milestone matrix"))}
                  extra={(k) => {
                    const n = loin.specs?.[k]?.classes?.length ?? 0;
                    return <Badge size="sm" variant={n ? "light" : "outline"} color={n ? "blue" : "gray"}>{n ? t("{{n}} classes", { n }) : t("empty")}</Badge>;
                  }}
                />
                <Text size="xs" c="dimmed">{t("{{n}} of {{total}} combinations selected", { n: specs.filter((k) => filled.includes(k)).length, total: filled.length })}</Text>
              </>
            )}
          </>
        )}

        {kind === "excel" && (
          <Select label={t("Language of the headers")} data={[{ value: "en", label: "English" }, { value: "de", label: "Deutsch" }]} value={settings.lang ?? (language?.startsWith("de") ? "de" : "en")} onChange={(v) => setSettings({ ...settings, lang: v })} allowDeselect={false} w={200} />
        )}
        {kind === "revit-psets" && (
          <Select label={t("Datatype for strings")} data={["Text", "Label"]} value={settings.text_or_label ?? "Text"} onChange={(v) => setSettings({ ...settings, text_or_label: v })} allowDeselect={false} w={200} />
        )}
        {kind === "revit-shared" && (
          <TextInput label={t("Parameter group name")} value={settings.group_name ?? ""} placeholder={t("Dictionary code")} onChange={(e) => setSettings({ ...settings, group_name: e.currentTarget.value })} w={260} />
        )}
        {kind === "ids" && (
          <>
            <Divider label={t("Applicability")} />
            <Toggle label={t("Identify classes by bSDD classification reference")} checked={!!ids.classification} onChange={(e) => setIds({ classification: e.currentTarget.checked })} />
            {!ids.classification && (
              <Grid>
                <Grid.Col span={5}><Select label={t("Identifying property set")} data={candidates.map((c) => c.pset).filter(Boolean)} value={ids.main_pset || null} onChange={(v) => setIds({ main_pset: v ?? "", main_property: "" })} searchable /></Grid.Col>
                <Grid.Col span={5}><Select label={t("Identifying property")} data={mainPset?.properties ?? []} value={ids.main_property || null} onChange={(v) => setIds({ main_property: v ?? "" })} searchable /></Grid.Col>
                <Grid.Col span={2}><Select label={t("Datatype")} data={IFC_TYPES} value={ids.datatype ?? "IFCLABEL"} onChange={(v) => setIds({ datatype: v })} /></Grid.Col>
              </Grid>
            )}
            <Toggle label={t("Also allow the IFC type objects (e.g. IfcWallType)")} checked={!!ids.type_objects} onChange={(e) => setIds({ type_objects: e.currentTarget.checked })} />
            <Divider label={t("Datatype mapping")} />
            <Grid>
              {["string", "boolean", "integer", "real", "character", "time"].map((k) => (
                <Grid.Col span={2} key={k}>
                  <Select label={k} data={IFC_TYPES} value={ids.datatype_mapping?.[k] ?? null} onChange={(v) => setIds({ datatype_mapping: { ...(ids.datatype_mapping ?? {}), [k]: v } })} />
                </Grid.Col>
              ))}
            </Grid>
            <Divider label={t("Metadata")} />
            <Grid>
              {[["title", "Title"], ["description", "Description"], ["author", "Author (e-mail)"], ["copyright", "Copyright"], ["version", "Version"], ["purpose", "Purpose"], ["milestone", "Milestone"]].map(([k, label]) => (
                <Grid.Col span={k === "description" ? 12 : 6} key={k}>
                  <TextInput label={t(label)} value={meta[k] ?? ""} onChange={(e) => setMeta({ [k]: e.currentTarget.value })} />
                </Grid.Col>
              ))}
              <Grid.Col span={6}><DayField label={t("Date")} value={meta.date ?? ""} onChange={(v) => setMeta({ date: v ?? "" })} /></Grid.Col>
              <Grid.Col span={6}><TagsInput label={t("IFC versions")} data={["IFC2X3", "IFC4", "IFC4X3_ADD2"]} value={meta.ifc_versions ?? ["IFC4X3_ADD2"]} onChange={(v) => setMeta({ ifc_versions: v })} /></Grid.Col>
            </Grid>
          </>
        )}
        {kind === "iso7817" && <Text size="xs" c="dimmed">{t("Exports the selected purpose × milestone specifications as ISO 7817-3 XML.")}</Text>}
        <Group justify="flex-end">
          <Button variant="default" onClick={close}>{t("Cancel")}</Button>
          <Button onClick={run} loading={busy} disabled={(scope === "loin" || kind === "iso7817") && specs.length === 0}>{t("Export")}</Button>
        </Group>
      </Stack>
    </Modal>
  );
}
