/* eslint-disable @typescript-eslint/no-explicit-any */
import { ActionIcon, Autocomplete, Group, Loader, NumberInput, Select, Table, Text, TextInput, Textarea, Tooltip } from "@mantine/core";
import { IconPlus, IconSparkles, IconTrash } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { generateDefinition } from "../ai";
import { cached } from "../api";
import { parseValuesText } from "../clipboard";
import { CLASS_RELATION_TYPES, PROPERTY_RELATION_TYPES, isUri, slugify, uniqueCode } from "../model";
import { notifyError } from "../notify";
import { useProject } from "../state/project";
import { useSettings } from "../state/settings";
import type { AllowedValue, ClassRelation, PropertyRelation } from "../types";

export interface Resources {
  units: { Code: string; Name: string }[];
  countries: { Code: string; Name: string }[];
  languages: { IsoCode: string; Name: string }[];
  referenceDocuments: { Name: string; Title?: string }[];
  ifcClasses: { code: string; name: string; parentClassCode?: string }[];
}

const EMPTY: Resources = { units: [], countries: [], languages: [], referenceDocuments: [], ifcClasses: [] };

export function useResources(): Resources {
  const [res, setRes] = useState<Resources>(EMPTY);
  useEffect(() => {
    let alive = true;
    Promise.all([
      cached("/api/resources/units"),
      cached("/api/resources/countries"),
      cached("/api/resources/languages"),
      cached("/api/resources/reference-documents"),
      cached("/api/ifc/classes"),
    ])
      .then(([units, countries, languages, referenceDocuments, ifcClasses]) => {
        if (alive) setRes({ units, countries, languages, referenceDocuments, ifcClasses });
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);
  return res;
}

/** ISO date string <-> datetime-local input. */
export function DateField({ label, value, onChange }: { label: string; value?: string | null; onChange: (v: string | null) => void }) {
  const local = value ? value.replace("Z", "").slice(0, 16) : "";
  return (
    <TextInput
      label={label}
      type="datetime-local"
      value={local}
      onChange={(e) => onChange(e.currentTarget.value ? new Date(e.currentTarget.value + "Z").toISOString().replace(".000Z", "Z") : null)}
    />
  );
}

export function OptionalNumber({ label, value, onChange, integer }: { label: string; value?: number | null; onChange: (v: number | null) => void; integer?: boolean }) {
  return (
    <NumberInput
      label={label}
      value={value ?? ""}
      allowDecimal={!integer}
      onChange={(v) => onChange(v === "" || v === undefined ? null : Number(v))}
    />
  );
}

export function AiTextarea(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  kind: "class" | "property";
  context: () => Record<string, unknown>;
  placeholder?: string;
  error?: string | false;
}) {
  const { t } = useTranslation();
  const hasKey = useSettings((s) => !!s.aiKey);
  const [busy, setBusy] = useState(false);
  const generate = async () => {
    setBusy(true);
    try {
      props.onChange(await generateDefinition(props.kind, props.context()));
    } catch (e) {
      notifyError(e, t("AI helper"));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Textarea
      label={
        <Group gap={4} component="span">
          {props.label}
          <Tooltip label={hasKey ? t("Generate definition with AI") : t("Enter your OpenAI API key in the settings to use the AI helper")}>
            <ActionIcon size="xs" variant="subtle" onClick={generate} disabled={!hasKey || busy} component="span">
              {busy ? <Loader size={10} /> : <IconSparkles size={12} />}
            </ActionIcon>
          </Tooltip>
        </Group>
      }
      value={props.value}
      onChange={(e) => props.onChange(e.currentTarget.value)}
      autosize
      minRows={3}
      maxRows={10}
      placeholder={props.placeholder}
      error={props.error}
    />
  );
}

// ------------------------------------------------------------------ allowed values

export function AllowedValuesEditor({ values, onChange, inherited }: { values: AllowedValue[]; onChange: (v: AllowedValue[]) => void; inherited?: AllowedValue[] }) {
  const { t } = useTranslation();
  const separator = useSettings((s) => s.pasteSeparator);
  const showInherited = values.length === 0 && (inherited?.length ?? 0) > 0;
  const update = (i: number, patch: Partial<AllowedValue>) => {
    const next = values.slice();
    const old = next[i];
    const item = { ...old, ...patch };
    if (patch.Value !== undefined && (old.Code === slugify(old.Value) || !old.Code)) {
      item.Code = uniqueCode(slugify(patch.Value) || "value", values.filter((_, j) => j !== i).map((v) => v.Code));
    }
    next[i] = item;
    onChange(next);
  };
  const add = () => onChange([...values, { Code: uniqueCode("new-value", values.map((v) => v.Code)), Value: "new value" }]);
  const onPaste = (e: React.ClipboardEvent) => {
    const target = e.target as HTMLElement;
    const text = e.clipboardData.getData("text/plain");
    if (!text || (target.tagName === "INPUT" && !text.includes("\n") && !text.includes(";") && !text.includes("\t"))) return;
    e.preventDefault();
    const rows = parseValuesText(text, separator);
    const existing = new Set(values.map((v) => v.Code.toLowerCase()));
    const next = values.slice();
    for (const cols of rows) {
      const value = cols[0];
      if (!value) continue;
      const code = cols[1] || slugify(value) || "value";
      if (existing.has(code.toLowerCase())) continue;
      existing.add(code.toLowerCase());
      next.push({ Value: value, Code: code, Description: cols[2] || undefined, SortNumber: cols[3] ? Number(cols[3]) : undefined, OwnedUri: cols[4] || undefined });
    }
    onChange(next);
  };
  return (
    <div onPaste={onPaste}>
      <Group justify="space-between" mb={4}>
        <Text size="xs" c="dimmed">{t("Paste lists (one value per line, or CSV with ';': Value;Code;Description;SortNumber;OwnedUri)")}</Text>
        <ActionIcon variant="light" size="sm" onClick={add}><IconPlus size={14} /></ActionIcon>
      </Group>
      <Table withTableBorder withColumnBorders striped fz="xs" verticalSpacing={2}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>{t("Value")}</Table.Th>
            <Table.Th>{t("Code")}</Table.Th>
            <Table.Th>{t("Description")}</Table.Th>
            <Table.Th w={70}>{t("Sort")}</Table.Th>
            <Table.Th>{t("Owned URI")}</Table.Th>
            <Table.Th w={30} />
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {showInherited &&
            inherited!.map((v, i) => (
              <Table.Tr key={`inh-${i}`} style={{ opacity: 0.55, fontStyle: "italic" }}>
                <Table.Td>{v.Value}</Table.Td>
                <Table.Td>{v.Code}</Table.Td>
                <Table.Td>{v.Description}</Table.Td>
                <Table.Td>{v.SortNumber}</Table.Td>
                <Table.Td>{v.OwnedUri}</Table.Td>
                <Table.Td />
              </Table.Tr>
            ))}
          {values.map((v, i) => (
            <Table.Tr key={i}>
              <Table.Td><CellInput value={v.Value} onChange={(x) => update(i, { Value: x })} /></Table.Td>
              <Table.Td><CellInput value={v.Code} onChange={(x) => update(i, { Code: x })} /></Table.Td>
              <Table.Td><CellInput value={v.Description ?? ""} onChange={(x) => update(i, { Description: x || undefined })} /></Table.Td>
              <Table.Td><CellInput value={v.SortNumber?.toString() ?? ""} onChange={(x) => update(i, { SortNumber: x === "" || isNaN(Number(x)) ? undefined : Number(x) })} /></Table.Td>
              <Table.Td><CellInput value={v.OwnedUri ?? ""} onChange={(x) => update(i, { OwnedUri: x || undefined })} /></Table.Td>
              <Table.Td>
                <ActionIcon size="xs" variant="subtle" color="red" onClick={() => onChange(values.filter((_, j) => j !== i))}><IconTrash size={12} /></ActionIcon>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      {showInherited && <Text size="xs" c="dimmed" mt={4}>{t("Grey values are inherited from the property. Add values to override them.")}</Text>}
    </div>
  );
}

function CellInput({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return <input className="cell-edit" style={{ width: "100%", border: "none", background: "transparent", font: "inherit", color: "inherit" }} value={value} onChange={(e) => onChange(e.currentTarget.value)} />;
}

// ------------------------------------------------------------------ relations

type AnyRelation = ClassRelation | PropertyRelation;

export function RelationsEditor({ kind, relations, onChange, selfCode }: { kind: "class" | "property"; relations: AnyRelation[]; onChange: (r: AnyRelation[]) => void; selfCode?: string }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const allowUnknown = useSettings((s) => s.allowUnknownUri);
  const [type, setType] = useState<string>(kind === "class" ? "IsSimilarTo" : "IsSimilarTo");
  const [target, setTarget] = useState("");
  const [fraction, setFraction] = useState<number | null>(null);
  const [owned, setOwned] = useState("");
  const d = doc?.dictionary;
  const useOwnUri = !!d?.UseOwnUri;

  const options = useMemo(() => {
    if (!d) return [];
    if (kind === "class") {
      return (d.Classes ?? [])
        .filter((c) => c.Code !== selfCode && (type !== "HasMaterial" || c.ClassType === "Material"))
        .map((c) => ({ value: c.Code, label: `${c.Code} — ${c.Name}` }));
    }
    return (d.Properties ?? []).filter((p) => p.Code !== selfCode).map((p) => ({ value: p.Code, label: `${p.Code} — ${p.Name}` }));
  }, [d, kind, type, selfCode]);

  const uriKey = kind === "class" ? "RelatedClassUri" : "RelatedPropertyUri";
  const nameKey = kind === "class" ? "RelatedClassName" : "RelatedPropertyName";
  const codes = new Set(options.map((o) => o.value));
  const targetValid = !!target && (codes.has(target) || (isUri(target) && allowUnknown) || (isUri(target) && !allowUnknown && target.includes("/uri/")));

  const add = () => {
    if (!targetValid) return;
    const rel: any = { RelationType: type, [uriKey]: target };
    if (kind === "class" && type === "HasMaterial" && fraction !== null) rel.Fraction = fraction;
    if (useOwnUri && owned) rel.OwnedUri = owned;
    onChange([...relations, rel]);
    setTarget("");
    setFraction(null);
    setOwned("");
  };

  const label = (r: any) => {
    const uri: string = r[uriKey] ?? "";
    return r[nameKey] || (isUri(uri) ? uri.split("/").pop() : uri);
  };

  return (
    <div>
      <Table withTableBorder striped fz="xs" verticalSpacing={2} mb="xs">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>{t("Relation")}</Table.Th>
            <Table.Th>{t("Target")}</Table.Th>
            <Table.Th>{t("URI / Code")}</Table.Th>
            {kind === "class" && <Table.Th w={70}>{t("Fraction")}</Table.Th>}
            {useOwnUri && <Table.Th>{t("Owned URI")}</Table.Th>}
            <Table.Th w={30} />
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {relations.length === 0 && (
            <Table.Tr><Table.Td colSpan={6}><Text size="xs" c="dimmed">{t("No relations")}</Text></Table.Td></Table.Tr>
          )}
          {relations.map((r: any, i) => (
            <Table.Tr key={i}>
              <Table.Td>{r.RelationType}</Table.Td>
              <Table.Td>{label(r)}</Table.Td>
              <Table.Td style={{ maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis" }} title={r[uriKey]}>{r[uriKey]}</Table.Td>
              {kind === "class" && <Table.Td>{r.Fraction ?? ""}</Table.Td>}
              {useOwnUri && <Table.Td>{r.OwnedUri ?? ""}</Table.Td>}
              <Table.Td>
                <ActionIcon size="xs" variant="subtle" color="red" onClick={() => onChange(relations.filter((_, j) => j !== i))}><IconTrash size={12} /></ActionIcon>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      <Group gap="xs" align="flex-end" wrap="nowrap">
        <Select label={t("Relation")} data={kind === "class" ? CLASS_RELATION_TYPES : PROPERTY_RELATION_TYPES} value={type} onChange={(v) => setType(v ?? type)} w={150} allowDeselect={false} />
        <Autocomplete
          label={t("Target (code or URI)")}
          data={options}
          value={target}
          onChange={setTarget}
          style={{ flex: 1 }}
          limit={50}
          error={target && !targetValid ? t("Unknown code") : undefined}
          onKeyDown={(e) => e.key === "Enter" && add()}
        />
        {kind === "class" && type === "HasMaterial" && <NumberInput label={t("Fraction")} value={fraction ?? ""} onChange={(v) => setFraction(v === "" ? null : Number(v))} w={90} min={0} max={1} step={0.1} decimalScale={4} />}
        {useOwnUri && <TextInput label={t("Owned URI")} value={owned} onChange={(e) => setOwned(e.currentTarget.value)} w={180} />}
        <ActionIcon variant="light" onClick={add} disabled={!targetValid} mb={2}><IconPlus size={16} /></ActionIcon>
      </Group>
    </div>
  );
}
