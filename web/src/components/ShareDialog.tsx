import { ActionIcon, Alert, CopyButton, Group, Modal, Stack, Text, TextInput, Tooltip } from "@mantine/core";
import { IconCheck, IconCopy } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";

export function ShareDialog() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.share);
  const projectId = useProject((s) => s.projectId);
  if (!opened || !projectId) return null;
  const url = `${location.origin}/p/${projectId}`;
  const canCopy = typeof navigator !== "undefined" && !!navigator.clipboard && window.isSecureContext;
  return (
    <Modal opened onClose={() => useUi.getState().set({ share: false })} title={t("Share dictionary")}>
      <Stack>
        <Text size="sm">{t("Everybody who has this link can view and edit the dictionary together with you in real time.")}</Text>
        <Group gap="xs" wrap="nowrap">
          <TextInput value={url} readOnly style={{ flex: 1 }} onFocus={(e) => e.currentTarget.select()} />
          {canCopy && (
            <CopyButton value={url}>
              {({ copied, copy }) => (
                <Tooltip label={copied ? t("Copied") : t("Copy link")}>
                  <ActionIcon variant="light" onClick={copy} color={copied ? "green" : undefined}>{copied ? <IconCheck size={16} /> : <IconCopy size={16} />}</ActionIcon>
                </Tooltip>
              )}
            </CopyButton>
          )}
        </Group>
        <Alert color="yellow" variant="light">{t("Keep the link private: there is no other access protection.")}</Alert>
      </Stack>
    </Modal>
  );
}
