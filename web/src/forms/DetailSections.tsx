/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Building blocks of the "Details" tabs of classes and properties: fields grouped into themed
 * cards (identification, scope, lifecycle, …) instead of one long grid.
 */
import { Badge, Group, MultiSelect, Paper, Select, SimpleGrid, Stack, TagsInput, Text, TextInput, ThemeIcon, Tooltip } from "@mantine/core";
import { IconArrowsExchange, IconCalendarTime, IconFingerprint, IconWorld } from "@tabler/icons-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { DateField, OptionalNumber } from "../components/fields";

type Setter = (key: any, value: any) => void;

const filled = (v: unknown) => (Array.isArray(v) ? v.length > 0 : v !== null && v !== undefined && v !== "");

/** Card with icon, title, short explanation and "n/m filled" badge. */
export function DetailCard({ icon, color, title, hint, values, children }: {
  icon: ReactNode;
  color: string;
  title: string;
  hint?: string;
  /** field values of this card, for the "filled" counter */
  values: unknown[];
  children: ReactNode;
}) {
  const { t } = useTranslation();
  const n = values.filter(filled).length;
  return (
    <Paper withBorder radius="md" p="md" className="detail-card">
      <Group justify="space-between" wrap="nowrap" mb="sm" align="flex-start">
        <Group gap="sm" wrap="nowrap" style={{ minWidth: 0 }}>
          <ThemeIcon variant="light" color={color} size={32} radius="md">{icon}</ThemeIcon>
          <div style={{ minWidth: 0 }}>
            <Text fw={600} size="sm">{title}</Text>
            {hint && <Text size="xs" c="dimmed" lh={1.3}>{hint}</Text>}
          </div>
        </Group>
        <Tooltip label={t("{{n}} of {{total}} fields filled", { n, total: values.length })}>
          <Badge variant={n ? "light" : "outline"} color={n ? color : "gray"} size="sm" style={{ flex: "none" }}>{n}/{values.length}</Badge>
        </Tooltip>
      </Group>
      {children}
    </Paper>
  );
}

/** Label on the left, inputs on the right – for paired values (number + date, min + max …). */
export function DetailRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="detail-row">
      <Text size="sm" fw={500} className="detail-row-label">{label}</Text>
      <div className="detail-row-fields">{children}</div>
    </div>
  );
}

export function DetailGrid({ children }: { children: ReactNode }) {
  return <div className="detail-grid">{children}</div>;
}

interface CommonProps {
  form: any;
  set: Setter;
  countryData: (string | { value: string; label: string })[];
  languageData: (string | { value: string; label: string })[];
  /** input for the document reference (classes: free text, properties: list of documents) */
  documentReference: ReactNode;
}

/** The cards classes and properties share. */
export function CommonDetailCards({ form, set, countryData, languageData, documentReference }: CommonProps) {
  const { t } = useTranslation();
  return (
    <>
      <DetailCard
        icon={<IconFingerprint size={18} />}
        color="blue"
        title={t("Identification")}
        hint={t("References that identify this item outside the dictionary")}
        values={[form.ReferenceCode, form.Uid, form.OwnedUri, form.DocumentReference, form.VisualRepresentationUri]}
      >
        <Stack gap="xs">
          <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="xs">
            <TextInput label={t("Reference code")} value={form.ReferenceCode ?? ""} onChange={(e) => set("ReferenceCode", e.currentTarget.value)} />
            <TextInput label="UID" value={form.Uid ?? ""} onChange={(e) => set("Uid", e.currentTarget.value)} />
          </SimpleGrid>
          {documentReference}
          <TextInput label={t("Owned URI")} description={t("Only if the dictionary uses its own URIs")} value={form.OwnedUri ?? ""} onChange={(e) => set("OwnedUri", e.currentTarget.value)} />
          <TextInput label={t("Visual representation URI")} placeholder="https://…" value={form.VisualRepresentationUri ?? ""} onChange={(e) => set("VisualRepresentationUri", e.currentTarget.value)} />
        </Stack>
      </DetailCard>

      <DetailCard
        icon={<IconWorld size={18} />}
        color="teal"
        title={t("Scope of use")}
        hint={t("Where this item applies and in which language it was written")}
        values={[form.CountriesOfUse, form.CountryOfOrigin, form.SubdivisionsOfUse, form.CreatorLanguageIsoCode]}
      >
        <Stack gap="xs">
          <MultiSelect label={t("Countries of use")} data={countryData} value={form.CountriesOfUse ?? []} onChange={(v) => set("CountriesOfUse", v)} searchable clearable />
          <TagsInput label={t("Subdivisions of use")} description={t("Regions, e.g. US-MT")} value={form.SubdivisionsOfUse ?? []} onChange={(v) => set("SubdivisionsOfUse", v)} />
          <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="xs">
            <Select label={t("Country of origin")} data={countryData} value={form.CountryOfOrigin ?? null} onChange={(v) => set("CountryOfOrigin", v)} searchable clearable />
            <Select label={t("Creator language")} data={languageData} value={form.CreatorLanguageIsoCode ?? null} onChange={(v) => set("CreatorLanguageIsoCode", v)} searchable clearable />
          </SimpleGrid>
        </Stack>
      </DetailCard>

      <DetailCard
        icon={<IconCalendarTime size={18} />}
        color="grape"
        title={t("Version & lifecycle")}
        hint={t("Versioning and the period in which this item is valid")}
        values={[form.VersionNumber, form.VersionDateUtc, form.RevisionNumber, form.RevisionDateUtc, form.ActivationDateUtc, form.DeActivationDateUtc, form.DeprecationExplanation]}
      >
        <Stack gap="xs">
          <DetailRow label={t("Version")}>
            <OptionalNumber label={t("Number")} value={form.VersionNumber} onChange={(v) => set("VersionNumber", v)} integer />
            <DateField label={t("Date")} value={form.VersionDateUtc} onChange={(v) => set("VersionDateUtc", v)} />
          </DetailRow>
          <DetailRow label={t("Revision")}>
            <OptionalNumber label={t("Number")} value={form.RevisionNumber} onChange={(v) => set("RevisionNumber", v)} integer />
            <DateField label={t("Date")} value={form.RevisionDateUtc} onChange={(v) => set("RevisionDateUtc", v)} />
          </DetailRow>
          <DetailRow label={t("Valid")}>
            <DateField label={t("From (activation)")} value={form.ActivationDateUtc} onChange={(v) => set("ActivationDateUtc", v)} />
            <DateField label={t("Until (deactivation)")} value={form.DeActivationDateUtc} onChange={(v) => set("DeActivationDateUtc", v)} />
          </DetailRow>
          <TextInput label={t("Deprecation explanation")} placeholder={form.DeActivationDateUtc ? t("Why is it no longer valid?") : undefined} value={form.DeprecationExplanation ?? ""} onChange={(e) => set("DeprecationExplanation", e.currentTarget.value)} />
        </Stack>
      </DetailCard>

      <DetailCard
        icon={<IconArrowsExchange size={18} />}
        color="orange"
        title={t("Replacement")}
        hint={t("Codes of items this one replaces or is replaced by")}
        values={[form.ReplacedObjectCodes, form.ReplacingObjectCodes]}
      >
        <Stack gap="xs">
          <TagsInput label={t("Replaces")} description={t("Replaced object codes")} value={form.ReplacedObjectCodes ?? []} onChange={(v) => set("ReplacedObjectCodes", v)} />
          <TagsInput label={t("Replaced by")} description={t("Replacing object codes")} value={form.ReplacingObjectCodes ?? []} onChange={(v) => set("ReplacingObjectCodes", v)} />
        </Stack>
      </DetailCard>
    </>
  );
}

/** "0 ≤ x < 100" from the four bound fields (empty when no bound is set). */
export function rangePreview(form: any): string {
  const parts: string[] = [];
  const lo = form.MinInclusive ?? form.MinExclusive;
  const hi = form.MaxInclusive ?? form.MaxExclusive;
  if (lo === null || lo === undefined) {
    if (hi === null || hi === undefined) return "";
  } else parts.push(`${lo} ${form.MinInclusive !== null && form.MinInclusive !== undefined ? "≤" : "<"}`);
  parts.push("x");
  if (hi !== null && hi !== undefined) parts.push(`${form.MaxInclusive !== null && form.MaxInclusive !== undefined ? "≤" : "<"} ${hi}`);
  return parts.join(" ");
}
