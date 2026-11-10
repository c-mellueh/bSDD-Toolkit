/* eslint-disable @typescript-eslint/no-explicit-any */
import { ActionIcon, Group, Loader, NumberInput, Textarea, Tooltip, type MantineSize } from "@mantine/core";
import { IconSparkles } from "@tabler/icons-react";
import { DateInput, DateTimePicker } from "@mantine/dates";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { generateDefinition } from "../ai";
import { cached } from "../api";
import { notifyError } from "../notify";
import { useSettings } from "../state/settings";

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

/** ISO date-time string (UTC) <-> localized date-time picker. */
export function DateField({ label, value, onChange }: { label: string; value?: string | null; onChange: (v: string | null) => void }) {
  const lang = useSettings((st) => st.language);
  // bSDD stores UTC timestamps; they are shown as they are (no time zone shift)
  const local = value ? dayjs(value.replace("Z", "").slice(0, 19)).toDate() : null;
  return (
    <DateTimePicker
      label={label}
      value={local && !isNaN(local.getTime()) ? local : null}
      valueFormat={lang === "de" ? "DD.MM.YYYY HH:mm" : "YYYY-MM-DD HH:mm"}
      clearable
      onChange={(d) => onChange(d ? dayjs(d).format("YYYY-MM-DDTHH:mm:ss") + "Z" : null)}
    />
  );
}

/** Plain date "YYYY-MM-DD" <-> localized date picker. */
export function DayField({ value, onChange, ...rest }: { value?: string | null; onChange: (v: string | null) => void; label?: string; size?: MantineSize; w?: number }) {
  const lang = useSettings((st) => st.language);
  const d = value ? dayjs(value.slice(0, 10)).toDate() : null;
  return (
    <DateInput
      {...rest}
      value={d && !isNaN(d.getTime()) ? d : null}
      valueFormat={lang === "de" ? "DD.MM.YYYY" : "YYYY-MM-DD"}
      clearable
      onChange={(x) => onChange(x ? dayjs(x).format("YYYY-MM-DD") : null)}
    />
  );
}

export function OptionalNumber({ label, value, onChange, integer, hideControls }: { label: string; value?: number | null; onChange: (v: number | null) => void; integer?: boolean; hideControls?: boolean }) {
  return (
    <NumberInput
      label={label}
      hideControls={hideControls}
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
  const hasKey = useSettings((s) => !!s.aiKeys[s.aiProvider]?.trim());
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
          <Tooltip label={hasKey ? t("Generate definition with AI") : t("Enter an API key (OpenAI, Claude or Gemini) in the settings to use the AI helper")}>
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

export { AllowedValuesEditor } from "./AllowedValuesEditor";

export { RelationsEditor } from "./RelationsEditor";
