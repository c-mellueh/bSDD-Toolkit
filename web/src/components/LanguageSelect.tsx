import { SegmentedControl } from "@mantine/core";
import { useSettings } from "../state/settings";

export function LanguageSelect() {
  const language = useSettings((s) => s.language);
  const set = useSettings((s) => s.set);
  return (
    <SegmentedControl
      size="xs"
      value={language}
      onChange={(v) => set({ language: v as "en" | "de" })}
      data={[
        { value: "en", label: "EN" },
        { value: "de", label: "DE" },
      ]}
    />
  );
}
