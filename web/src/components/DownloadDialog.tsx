import { Alert, Button, Group, Modal, Progress, Select, Stack, Text, TextInput } from "@mantine/core";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { rememberProject } from "../state/settings";

interface Job {
  id: string;
  status: string;
  message: string;
  classes_done: number;
  classes_total: number;
  properties_done: number;
  properties_total: number;
  project_id: string | null;
  error: string | null;
}

interface RemoteDictionary {
  uri: string;
  name: string;
  version: string;
  organization: string;
  status: string;
}

export function DownloadDialog({ opened, onClose }: { opened: boolean; onClose: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [uri, setUri] = useState("");
  const [list, setList] = useState<RemoteDictionary[] | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const timer = useRef<number>();

  useEffect(() => {
    if (!opened || list) return;
    api<{ dictionaries: RemoteDictionary[] }>("/api/bsdd/dictionaries")
      .then((r) => setList(r.dictionaries))
      .catch((e) => setListError(e.message));
  }, [opened, list]);

  useEffect(() => () => window.clearInterval(timer.current), []);

  const start = async () => {
    try {
      const j = await api<Job>("/api/download", { method: "POST", json: { uri } });
      setJob(j);
      timer.current = window.setInterval(async () => {
        const s = await api<Job>(`/api/download/${j.id}`);
        setJob(s);
        if (s.status !== "running") {
          window.clearInterval(timer.current);
          if (s.status === "done" && s.project_id) {
            const item = list?.find((d) => d.uri === uri);
            rememberProject(s.project_id, item?.name ?? uri);
            navigate(`/p/${s.project_id}`);
          }
        }
      }, 800);
    } catch (e) {
      setJob({ id: "", status: "error", message: "", classes_done: 0, classes_total: 0, properties_done: 0, properties_total: 0, project_id: null, error: (e as Error).message });
    }
  };

  const cancel = async () => {
    if (job?.id) await api(`/api/download/${job.id}`, { method: "DELETE" }).catch(() => undefined);
    window.clearInterval(timer.current);
    setJob(null);
  };

  const running = job?.status === "running";
  const pct = (a: number, b: number) => (b ? Math.round((a / b) * 100) : 0);

  return (
    <Modal opened={opened} onClose={running ? () => undefined : onClose} title={t("Download dictionary from bSDD")} size="lg">
      <Stack>
        <Select
          label={t("Published dictionaries")}
          placeholder={list ? t("Search…") : listError ? t("Could not load list") : t("Loading…")}
          searchable
          clearable
          disabled={running || !list}
          data={(list ?? []).map((d) => ({ value: d.uri, label: `${d.name} ${d.version} — ${d.organization ?? ""}` }))}
          value={list?.some((d) => d.uri === uri) ? uri : null}
          onChange={(v) => setUri(v ?? "")}
          limit={200}
        />
        <TextInput label={t("Dictionary URI")} value={uri} onChange={(e) => setUri(e.currentTarget.value)} disabled={running} placeholder="https://identifier.buildingsmart.org/uri/…" />
        {listError && <Text size="xs" c="dimmed">{listError}</Text>}
        {job && (
          <Stack gap={4}>
            <Text size="sm">{t(job.message)}</Text>
            <Text size="xs">{t("Classes")} {job.classes_done}/{job.classes_total}</Text>
            <Progress value={pct(job.classes_done, job.classes_total)} animated={running} />
            <Text size="xs">{t("Properties")} {job.properties_done}/{job.properties_total}</Text>
            <Progress value={pct(job.properties_done, job.properties_total)} animated={running} />
            {job.error && <Alert color="red">{job.error}</Alert>}
          </Stack>
        )}
        <Group justify="flex-end">
          {running ? (
            <Button color="red" variant="light" onClick={cancel}>{t("Cancel")}</Button>
          ) : (
            <>
              <Button variant="default" onClick={onClose}>{t("Close")}</Button>
              <Button onClick={start} disabled={!uri}>{t("Download")}</Button>
            </>
          )}
        </Group>
      </Stack>
    </Modal>
  );
}
