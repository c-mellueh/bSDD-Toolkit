import { Stack, Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { ApiError, api, readFileText } from "../api";
import { notifyError } from "../notify";
import { rememberProject } from "../state/settings";

/**
 * Create a project from a JSON file: a plain bSDD JSON (e.g. downloaded from the bSDD website)
 * or a project file (dictionary + editor data). Offers to drop invalid parts if needed.
 */
export function useDictionaryUpload(onOpened?: () => void) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);

  const upload = async (file: File | null, sloppy = false, text?: string): Promise<void> => {
    if (!file) return;
    setBusy(true);
    try {
      const content = text ?? (await readFileText(file));
      let data: Record<string, unknown>;
      try {
        data = JSON.parse(content);
      } catch {
        throw new Error(t("The file is not valid JSON"));
      }
      // project export (dictionary + editor data) or plain bSDD JSON
      const body = "dictionary" in data && "extras" in data ? { dictionary: data.dictionary, extras: data.extras, sloppy } : { dictionary: data, sloppy };
      const res = await api<{ id: string; meta: { name: string } }>("/api/projects", { method: "POST", json: body });
      rememberProject(res.id, res.meta.name ?? file.name);
      onOpened?.();
      navigate(`/p/${res.id}`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 422 && e.body?.can_sloppy) {
        modals.openConfirmModal({
          title: t("The file contains invalid data"),
          children: (
            <Stack gap="xs">
              <Text size="sm">{e.message}</Text>
              <Text size="sm">{t("Do you want to load it anyway? Invalid parts will be removed.")}</Text>
            </Stack>
          ),
          labels: { confirm: t("Load anyway"), cancel: t("Cancel") },
          onConfirm: () => upload(file, true, text),
        });
      } else notifyError(e);
    } finally {
      setBusy(false);
    }
  };
  return { upload, busy };
}
