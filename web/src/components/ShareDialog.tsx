import { ActionIcon, Alert, Badge, Button, CopyButton, Divider, Group, Loader, Modal, PasswordInput, Stack, Switch, Text, TextInput, Title, Tooltip } from "@mantine/core";
import { IconCheck, IconCopy, IconEye, IconLock, IconLockOpen, IconPencil, IconRefresh } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import { attempt, notifyOk } from "../notify";
import { setToken } from "../state/access";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";
import { askConfirm } from "./dialogs";

interface AccessInfo {
  edit_protected: boolean;
  view_enabled: boolean;
  view_id: string | null;
  view_protected: boolean;
  token?: string;
}

function LinkField({ url }: { url: string }) {
  const { t } = useTranslation();
  const canCopy = typeof navigator !== "undefined" && !!navigator.clipboard && window.isSecureContext;
  return (
    <Group gap="xs" wrap="nowrap">
      <TextInput value={url} readOnly style={{ flex: 1 }} onFocus={(e) => e.currentTarget.select()} className="mono" />
      {canCopy && (
        <CopyButton value={url}>
          {({ copied, copy }) => (
            <Tooltip label={copied ? t("Copied") : t("Copy link")}>
              <ActionIcon variant="light" size="lg" onClick={copy} color={copied ? "green" : undefined} aria-label={t("Copy link")}>
                {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
              </ActionIcon>
            </Tooltip>
          )}
        </CopyButton>
      )}
    </Group>
  );
}

function PasswordControl({ protectedNow, onSet, onRemove, label }: { protectedNow: boolean; onSet: (pw: string) => Promise<void>; onRemove: () => Promise<void>; label: string }) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const tooShort = pw.length > 0 && pw.length < 4;
  const mismatch = pw2.length > 0 && pw !== pw2;
  const save = async () => {
    await onSet(pw);
    setPw("");
    setPw2("");
    setEditing(false);
  };
  return (
    <Stack gap={6}>
      <Group justify="space-between" wrap="nowrap">
        <Group gap={6}>
          {protectedNow ? <IconLock size={16} color="var(--mantine-color-green-7)" /> : <IconLockOpen size={16} color="var(--mantine-color-dimmed)" />}
          <Text size="sm">{label}</Text>
          <Badge size="sm" variant="light" color={protectedNow ? "green" : "gray"}>{protectedNow ? t("Password protected") : t("No password")}</Badge>
        </Group>
        {!editing && (
          <Group gap={4} wrap="nowrap">
            <Button size="compact-sm" variant="light" onClick={() => setEditing(true)}>{protectedNow ? t("Change") : t("Set password")}</Button>
            {protectedNow && <Button size="compact-sm" variant="subtle" color="red" onClick={() => void onRemove()}>{t("Remove")}</Button>}
          </Group>
        )}
      </Group>
      {editing && (
        <form onSubmit={(e) => { e.preventDefault(); if (!tooShort && !mismatch && pw && pw === pw2) void save(); }}>
          <Group gap="xs" align="flex-start" wrap="wrap">
            <PasswordInput placeholder={t("New password")} value={pw} onChange={(e) => setPw(e.currentTarget.value)} error={tooShort ? t("At least 4 characters") : undefined} style={{ flex: "1 1 160px" }} data-autofocus autoFocus />
            <PasswordInput placeholder={t("Repeat password")} value={pw2} onChange={(e) => setPw2(e.currentTarget.value)} error={mismatch ? t("Passwords do not match") : undefined} style={{ flex: "1 1 160px" }} />
            <Button type="submit" disabled={!pw || tooShort || pw !== pw2}>{t("Save")}</Button>
            <Button variant="default" onClick={() => { setEditing(false); setPw(""); setPw2(""); }}>{t("Cancel")}</Button>
          </Group>
        </form>
      )}
    </Stack>
  );
}

export function ShareDialog() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.share);
  const projectId = useProject((s) => s.projectId);
  const role = useProject((s) => s.role);
  const base = useProject((s) => s.base);
  const [info, setInfo] = useState<AccessInfo | null>(null);

  useEffect(() => {
    if (!opened || !projectId || role !== "edit") return;
    setInfo(null);
    api<AccessInfo>(`/api/projects/${projectId}/access`).then(setInfo).catch(() => setInfo(null));
  }, [opened, projectId, role]);

  if (!opened || !projectId) return null;
  const close = () => useUi.getState().set({ share: false });

  const change = async (body: Record<string, unknown>, message?: string) => {
    const res = await attempt(() => api<AccessInfo>(`/api/projects/${projectId}/access`, { method: "POST", json: body }));
    if (!res) return;
    if (res.token) setToken(projectId, res.token); // keep access after the change
    setInfo(res);
    if (message) notifyOk(message);
  };

  if (role === "view") {
    return (
      <Modal opened onClose={close} title={t("Share dictionary")}>
        <Stack>
          <Text size="sm">{t("You opened a read-only link. You can pass it on; whoever opens it can only view the dictionary.")}</Text>
          <LinkField url={`${location.origin}${base}/${projectId}`} />
        </Stack>
      </Modal>
    );
  }

  return (
    <Modal opened onClose={close} title={t("Share dictionary")} size="lg">
      {!info ? (
        <Group justify="center" p="lg"><Loader size="sm" /></Group>
      ) : (
        <Stack gap="lg">
          <Stack gap="xs">
            <Group gap={8}><IconPencil size={18} /><Title order={5}>{t("Edit link")}</Title></Group>
            <Text size="sm" c="dimmed">{t("Everybody who has this link can view and edit the dictionary together with you in real time.")}</Text>
            <LinkField url={`${location.origin}/p/${projectId}`} />
            <PasswordControl
              label={t("Access")}
              protectedNow={info.edit_protected}
              onSet={(pw) => change({ edit_password: pw }, t("Password set. Everybody else has to enter it now."))}
              onRemove={async () => {
                if (await askConfirm(t("Remove password"), t("Everybody with the link can then open and edit the dictionary without a password."), t("Remove"), true))
                  await change({ remove: ["edit_password"] }, t("Password removed"));
              }}
            />
          </Stack>

          <Divider />

          <Stack gap="xs">
            <Group justify="space-between" wrap="nowrap">
              <Group gap={8}><IconEye size={18} /><Title order={5}>{t("Read-only link")}</Title></Group>
              <Switch
                checked={info.view_enabled}
                onChange={async (e) => {
                  const on = e.currentTarget.checked;
                  if (!on && !(await askConfirm(t("Disable read-only link"), t("The read-only link stops working for everybody."), t("Disable"), true))) return;
                  await change({ view_enabled: on });
                }}
                label={info.view_enabled ? t("Enabled") : t("Disabled")}
              />
            </Group>
            <Text size="sm" c="dimmed">{t("A separate link that only allows viewing, searching and exporting. It does not reveal the edit link.")}</Text>
            {info.view_enabled && info.view_id && (
              <>
                <Group gap="xs" wrap="nowrap" align="center">
                  <div style={{ flex: 1 }}><LinkField url={`${location.origin}/v/${info.view_id}`} /></div>
                  <Tooltip label={t("Create a new read-only link (the old one stops working)")}>
                    <ActionIcon
                      variant="default"
                      size="lg"
                      aria-label={t("New link")}
                      onClick={async () => {
                        if (await askConfirm(t("New read-only link"), t("The current read-only link stops working. Continue?"), t("New link")))
                          await change({ regenerate_view: true }, t("New read-only link created"));
                      }}
                    >
                      <IconRefresh size={16} />
                    </ActionIcon>
                  </Tooltip>
                </Group>
                <PasswordControl
                  label={t("Read-only access")}
                  protectedNow={info.view_protected}
                  onSet={(pw) => change({ view_password: pw }, t("Password for the read-only link set"))}
                  onRemove={() => change({ remove: ["view_password"] }, t("Password removed"))}
                />
                {!info.view_protected && info.edit_protected && (
                  <Text size="xs" c="dimmed">{t("Without its own password, anybody with the read-only link can view the dictionary.")}</Text>
                )}
              </>
            )}
          </Stack>

          <Alert color="yellow" variant="light">
            {t("Changing the edit password signs out everybody else. Changing the read-only link or its password only affects viewers.")}
          </Alert>
        </Stack>
      )}
    </Modal>
  );
}
