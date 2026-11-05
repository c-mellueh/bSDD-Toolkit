import { ActionIcon, Badge, Button, Group, Switch, Text, Textarea, Tooltip } from "@mantine/core";
import { IconCloudUpload, IconRefresh, IconTrash, IconX } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { storageGet, storageSet } from "../state/settings";
import { useUi } from "../state/ui";

interface Line {
  kind: "in" | "out" | "err" | "result" | "info";
  text: string;
}

const HELP = `Python ${"runs in your browser"} (Pyodide). Available names:
  d           the dictionary (BsddDictionary, a local copy)
  cl_utils    bsdd_json.utils.class_utils
  prop_utils  bsdd_json.utils.property_utils
  dict_utils  bsdd_json.utils.dictionary_utils
  BsddClass, BsddProperty, BsddClassProperty, ...
Examples:  len(d.Classes)   [c.Name for c in cl_utils.get_root_classes(d)]
With "Live" on, every change to 'd' is sent to the shared dictionary after each command
(only the changed values; nothing is overwritten if someone else changed the same data).`;

export function ShellPanel() {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const [lines, setLines] = useState<Line[]>([{ kind: "info", text: HELP }]);
  const [code, setCode] = useState("");
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(true);
  const [history, setHistory] = useState<string[]>([]);
  const [hPos, setHPos] = useState(-1);
  const worker = useRef<Worker | null>(null);
  const out = useRef<HTMLDivElement | null>(null);
  const [live, setLiveState] = useState<boolean>(() => storageGet("bsdd-shell-live", true));
  const [stale, setStale] = useState(false);
  const [pending, setPending] = useState(false);
  const syncing = useRef(false);
  const setLive = (v: boolean) => {
    setLiveState(v);
    storageSet("bsdd-shell-live", v);
  };

  const push = (l: Line) => setLines((ls) => [...ls.slice(-500), l]);

  useEffect(() => {
    const w = new Worker(new URL("../shell.worker.ts", import.meta.url), { type: "module" });
    worker.current = w;
    w.onmessage = (ev) => {
      const m = ev.data;
      if (m.type === "status") push({ kind: "info", text: m.text });
      else if (m.type === "ready") { setReady(true); setBusy(false); push({ kind: "info", text: "Ready." }); }
      else if (m.type === "out") push({ kind: "out", text: m.text });
      else if (m.type === "err") push({ kind: "err", text: m.text });
      else if (m.type === "result") push({ kind: "result", text: m.text });
      else if (m.type === "done") setBusy(false);
      else if (m.type === "changes") void send(m.payload);
      else if (m.type === "nochanges") push({ kind: "info", text: t("No changes to sync.") });
    };
    w.onerror = (e) => { push({ kind: "err", text: String(e.message || "Shell could not be started (is the Pyodide CDN reachable?)") }); setBusy(false); };
    w.postMessage({ type: "init", dictionary: JSON.stringify(useProject.getState().doc?.dictionary ?? {}), zipUrl: "/api/shell/bsdd_json.zip" });
    return () => w.terminate();
  }, []);

  // the shared dictionary changed outside the shell → 'd' is outdated
  useEffect(
    () =>
      useProject.subscribe((st, prev) => {
        if (st.doc !== prev.doc && prev.doc && !syncing.current) setStale(true);
      }),
    [],
  );

  const send = async (payload: string) => {
    syncing.current = true;
    const n = await attempt(() => op<number>("dict.patch", JSON.parse(payload)));
    syncing.current = false;
    setPending(false);
    if (n !== undefined) push({ kind: "info", text: t("✓ {{n}} changes synced to the shared dictionary", { n }) });
    else push({ kind: "err", text: t("The changes were not applied. Reload the dictionary (↻) and run your code again.") });
  };

  useEffect(() => {
    out.current?.scrollTo({ top: out.current.scrollHeight });
  }, [lines]);

  const run = () => {
    if (!code.trim() || !ready || busy) return;
    push({ kind: "in", text: code });
    setHistory((h) => [...h, code]);
    setHPos(-1);
    setBusy(true);
    worker.current?.postMessage({ type: "run", code, sync: live });
    if (!live) setPending(true);
    setCode("");
  };

  const reload = () => {
    if (!doc) return;
    setBusy(true);
    worker.current?.postMessage({ type: "load", dictionary: JSON.stringify(doc.dictionary) });
    setStale(false);
    setPending(false);
  };

  const syncNow = () => worker.current?.postMessage({ type: "sync" });

  const color = (k: Line["kind"]) => (k === "err" ? "var(--mantine-color-red-6)" : k === "in" ? "var(--mantine-color-blue-6)" : k === "info" ? "var(--mantine-color-dimmed)" : undefined);

  return (
    <div style={{ height: 300, flex: "none", borderTop: "2px solid var(--mantine-color-default-border)", display: "flex", flexDirection: "column" }}>
      <Group gap={4} px="xs" py={2} style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <Text size="xs" fw={600} style={{ flex: 1 }}>{t("Python shell (runs in your browser)")}</Text>
        {stale && (
          <Tooltip multiline w={300} label={t("The dictionary was changed outside the shell. Reload 'd' to see these changes (variables like 'cl = d.Classes[0]' then have to be fetched again).")}>
            <Badge color="yellow" variant="light" style={{ cursor: "pointer" }} onClick={reload}>{t("Changed elsewhere – reload")}</Badge>
          </Tooltip>
        )}
        <Tooltip label={t("Reload dictionary from server")}><ActionIcon size="sm" variant={stale ? "light" : "subtle"} color={stale ? "yellow" : undefined} onClick={reload} disabled={!ready || busy}><IconRefresh size={14} /></ActionIcon></Tooltip>
        <Tooltip label={t("Send every change to the shared dictionary after each command")}>
          <Switch size="xs" label={t("Live")} checked={live} onChange={(e) => setLive(e.currentTarget.checked)} />
        </Tooltip>
        {!live && (
          <Button size="compact-xs" variant={pending ? "filled" : "light"} leftSection={<IconCloudUpload size={12} />} onClick={syncNow} disabled={!ready || busy}>{t("Apply to shared dictionary")}</Button>
        )}
        <Tooltip label={t("Clear")}><ActionIcon size="sm" variant="subtle" onClick={() => setLines([])}><IconTrash size={14} /></ActionIcon></Tooltip>
        <Tooltip label={t("Close")}><ActionIcon size="sm" variant="subtle" onClick={() => useUi.getState().set({ shell: false })}><IconX size={14} /></ActionIcon></Tooltip>
      </Group>
      <div ref={out} className="shell-output" style={{ flex: 1, overflow: "auto", padding: "4px 8px" }}>
        {lines.map((l, i) => (
          <div key={i} style={{ color: color(l.kind) }}>{l.kind === "in" ? l.text.split("\n").map((x, j) => `${j ? "... " : ">>> "}${x}`).join("\n") : l.text}</div>
        ))}
      </div>
      <Textarea
        className="mono"
        styles={{ input: { fontFamily: "ui-monospace, monospace", fontSize: 12 } }}
        placeholder={ready ? t("Python code – Enter to run, Shift+Enter for a new line") : t("Starting…")}
        value={code}
        onChange={(e) => setCode(e.currentTarget.value)}
        autosize
        minRows={1}
        maxRows={6}
        disabled={!ready}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); run(); }
          else if (e.key === "ArrowUp" && !code.includes("\n") && history.length) {
            e.preventDefault();
            const p = hPos < 0 ? history.length - 1 : Math.max(0, hPos - 1);
            setHPos(p); setCode(history[p]);
          } else if (e.key === "ArrowDown" && hPos >= 0) {
            e.preventDefault();
            const p = hPos + 1;
            if (p >= history.length) { setHPos(-1); setCode(""); } else { setHPos(p); setCode(history[p]); }
          }
        }}
      />
    </div>
  );
}
