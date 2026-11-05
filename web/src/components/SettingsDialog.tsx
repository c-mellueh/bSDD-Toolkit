import { Button, Divider, Group, Modal, NumberInput, PasswordInput, Select, Stack, Switch, Text, TextInput } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { renameMe } from "../state/project";
import { forbiddenAi } from "../ai";
import { AI_PROVIDERS, useSettings, type AiProvider } from "../state/settings";
import { useUi } from "../state/ui";

export function SettingsDialog() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.settings);
  const s = useSettings();
  if (!opened) return null;
  const provider = AI_PROVIDERS.find((p) => p.value === s.aiProvider) ?? AI_PROVIDERS[0];
  const blocked = forbiddenAi(s.aiKeys[s.aiProvider] ?? "", s.aiModels[s.aiProvider] ?? "");
  return (
    <Modal opened onClose={() => useUi.getState().set({ settings: false })} title={t("Settings")} size="md">
      <Stack>
        <Text size="xs" c="dimmed">{t("Settings are stored in this browser only.")}</Text>
        <TextInput label={t("Your name (shown to collaborators)")} value={s.userName} onChange={(e) => s.set({ userName: e.currentTarget.value })} onBlur={() => renameMe(s.userName)} />
        <Group grow>
          <Select label={t("Language")} data={[{ value: "en", label: "English" }, { value: "de", label: "Deutsch" }]} value={s.language} onChange={(v) => v && s.set({ language: v as "en" | "de" })} allowDeselect={false} />
          <Select label={t("Theme")} data={[{ value: "auto", label: t("Auto") }, { value: "light", label: t("Light") }, { value: "dark", label: t("Dark") }]} value={s.theme} onChange={(v) => v && s.set({ theme: v as "auto" | "light" | "dark" })} allowDeselect={false} />
        </Group>
        <TextInput label={t("Separator for pasting allowed values")} description={t("Use \\n for line breaks")} value={s.pasteSeparator === "\n" ? "\\n" : s.pasteSeparator} onChange={(e) => s.set({ pasteSeparator: e.currentTarget.value === "\\n" ? "\n" : e.currentTarget.value })} />
        <Switch label={t("Allow relations to unknown URIs")} checked={s.allowUnknownUri} onChange={(e) => s.set({ allowUnknownUri: e.currentTarget.checked })} />
        <Divider label={t("AI helper")} />
        <Select
          label={t("AI provider")}
          data={AI_PROVIDERS.map((p) => ({ value: p.value, label: p.label }))}
          value={s.aiProvider}
          onChange={(v) => v && s.set({ aiProvider: v as AiProvider })}
          allowDeselect={false}
        />
        <PasswordInput
          label={t("{{provider}} API key", { provider: provider.label })}
          description={t("Used directly from your browser, never sent to this server.")}
          placeholder={provider.keyHint}
          value={s.aiKeys[s.aiProvider] ?? ""}
          onChange={(e) => s.set({ aiKeys: { ...s.aiKeys, [s.aiProvider]: e.currentTarget.value } })}
          error={blocked ? t(blocked) : undefined}
        />
        <Group grow>
          <TextInput
            label={t("Model")}
            placeholder={provider.defaultModel}
            value={s.aiModels[s.aiProvider] ?? ""}
            onChange={(e) => s.set({ aiModels: { ...s.aiModels, [s.aiProvider]: e.currentTarget.value } })}
          />
          <Select label={t("Output language")} data={[{ value: "English", label: "English" }, { value: "German", label: "Deutsch" }]} value={s.aiLanguage} onChange={(v) => v && s.set({ aiLanguage: v as "English" | "German" })} allowDeselect={false} />
          <NumberInput label={t("Sentences")} min={1} max={10} value={s.aiSentences} onChange={(v) => s.set({ aiSentences: Number(v) || 2 })} />
        </Group>
        <Group justify="flex-end"><Button onClick={() => useUi.getState().set({ settings: false })}>{t("Close")}</Button></Group>
      </Stack>
    </Modal>
  );
}
