import { Button, Center, Paper, PasswordInput, Stack, Text, ThemeIcon, Title } from "@mantine/core";
import { IconLock } from "@tabler/icons-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { ApiError, api } from "../api";
import { setToken } from "../state/access";
import { reconnect, useProject } from "../state/project";

/** Shown when the link is protected: exchanges the password for an access token. */
export function PasswordScreen() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const projectId = useProject((s) => s.projectId);
  const locked = useProject((s) => s.locked);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!projectId || !password) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api<{ token: string }>(`/api/projects/${projectId}/auth`, { method: "POST", json: { password } });
      setToken(projectId, res.token);
      reconnect();
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) setError(t("Too many attempts. Please wait a few minutes."));
      else if (e instanceof ApiError && e.status === 401) setError(t("Wrong password"));
      else setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Center h="100%" p="md" style={{ background: "var(--app-page-bg)" }}>
      <Paper withBorder radius="lg" p="xl" w={400} maw="100%" shadow="sm">
        <form onSubmit={(e) => { e.preventDefault(); void submit(); }}>
          <Stack gap="md" align="stretch">
            <Center><ThemeIcon size={56} radius="xl" variant="light"><IconLock size={28} /></ThemeIcon></Center>
            <div style={{ textAlign: "center" }}>
              <Title order={3}>{t("Protected dictionary")}</Title>
              <Text size="sm" c="dimmed" mt={4}>
                {locked === "view" ? t("This read-only link is protected. Enter the password to view the dictionary.") : t("This dictionary is protected. Enter the password to view and edit it.")}
              </Text>
            </div>
            <PasswordInput label={t("Password")} value={password} onChange={(e) => setPassword(e.currentTarget.value)} error={error} data-autofocus autoFocus />
            <Button type="submit" loading={busy} disabled={!password}>{t("Open")}</Button>
            <Button variant="subtle" color="gray" onClick={() => navigate("/")}>{t("Back to start page")}</Button>
          </Stack>
        </form>
      </Paper>
    </Center>
  );
}
