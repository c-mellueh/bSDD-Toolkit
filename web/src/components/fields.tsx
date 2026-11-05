/* eslint-disable @typescript-eslint/no-explicit-any */
import { ActionIcon, Group, Loader, NumberInput, TextInput, Textarea, Tooltip } from "@mantine/core";
import { IconSparkles } from "@tabler/icons-react";
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

export { AllowedValuesEditor } from "./AllowedValuesEditor";

export { RelationsEditor } from "./RelationsEditor";
