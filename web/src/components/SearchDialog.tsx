import { Checkbox, Group, Modal, ScrollArea, Table, TextInput } from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { rowScore } from "../fuzzy";
import { storageGet, storageSet } from "../state/settings";
import { useProject } from "../state/project";
import { useUi } from "../state/ui";

const THRESHOLD = 65;

export function SearchDialog() {
  const { t } = useTranslation();
  const search = useUi((s) => s.search);
  const close = () => useUi.getState().set({ search: null });
  const doc = useProject((s) => s.doc);
  const [query, setQuery] = useState("");
  const [strict, setStrict] = useState(() => storageGet("bsdd-search-strict", false));
  const [cursor, setCursor] = useState(0);
  const [debounced] = useDebouncedValue(query, 120);

  useEffect(() => {
    if (search) {
      setQuery("");
      setCursor(0);
    }
  }, [search]);

  const rows = useMemo(() => {
    if (!doc || !search) return [];
    if (search.kind === "class") return (doc.dictionary.Classes ?? []).map((c) => ({ code: c.Code, cells: [c.Code, c.Name, c.ClassType ?? "Class"] }));
    return (doc.dictionary.Properties ?? []).map((p) => ({ code: p.Code, cells: [p.Code, p.Name, p.DataType ?? ""] }));
  }, [doc, search]);

  const results = useMemo(() => {
    if (!debounced.trim()) return rows.slice(0, 200).map((r) => ({ ...r, score: 0 }));
    return rows
      .map((r) => ({ ...r, score: rowScore(debounced, r.cells, strict) }))
      .filter((r) => r.score > THRESHOLD)
      .sort((a, b) => b.score - a.score)
      .slice(0, 200);
  }, [rows, debounced, strict]);

  if (!search) return null;
  const pick = (code: string) => {
    close();
    search.onPick(code);
  };
  const headers = search.kind === "class" ? [t("Code"), t("Name"), t("Class type")] : [t("Code"), t("Name"), t("Datatype")];

  return (
    <Modal opened onClose={close} title={search.kind === "class" ? t("Search class") : t("Search property")} size="lg" zIndex={400}>
      <Group gap="xs" mb="xs">
        <TextInput
          style={{ flex: 1 }}
          placeholder={t("Search…")}
          value={query}
          onChange={(e) => { setQuery(e.currentTarget.value); setCursor(0); }}
          data-autofocus
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setCursor((c) => Math.min(c + 1, results.length - 1)); }
            else if (e.key === "ArrowUp") { e.preventDefault(); setCursor((c) => Math.max(c - 1, 0)); }
            else if (e.key === "Enter" && results[cursor]) pick(results[cursor].code);
          }}
        />
        <Checkbox label={t("Strict")} checked={strict} onChange={(e) => { setStrict(e.currentTarget.checked); storageSet("bsdd-search-strict", e.currentTarget.checked); }} />
      </Group>
      <ScrollArea h={400}>
        <Table highlightOnHover fz="sm" verticalSpacing={3}>
          <Table.Thead><Table.Tr>{headers.map((h) => <Table.Th key={h}>{h}</Table.Th>)}</Table.Tr></Table.Thead>
          <Table.Tbody>
            {results.map((r, i) => (
              <Table.Tr key={r.code} onClick={() => pick(r.code)} style={{ cursor: "pointer", background: i === cursor ? "var(--mantine-primary-color-light)" : undefined }}>
                {r.cells.map((c, j) => <Table.Td key={j}>{c}</Table.Td>)}
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </ScrollArea>
    </Modal>
  );
}
