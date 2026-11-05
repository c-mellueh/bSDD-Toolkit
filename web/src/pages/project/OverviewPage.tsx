import { Accordion, Anchor, Avatar, Badge, Button, Card, CopyButton, Group, SimpleGrid, Stack, Text, TextInput, ThemeIcon, Title, Tooltip } from "@mantine/core";
import { IconAlertTriangle, IconBinaryTree2, IconCheck, IconCircleCheck, IconCopy, IconEye, IconFileExport, IconLink, IconList, IconListDetails, IconLock, IconLockOpen, IconPlus, IconStack2 } from "@tabler/icons-react";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { DictionaryForm } from "../../forms/DictionaryForm";
import { GOP, internalCode } from "../../model";
import { go, openClass, openProperty, type Section } from "../../state/nav";
import { useProject } from "../../state/project";
import { openUi } from "../../state/ui";

interface Check {
  key: string;
  label: string;
  items: { code: string; name: string; kind: "class" | "property" }[];
}

export function OverviewPage() {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const projectId = useProject((s) => s.projectId);
  const users = useProject((s) => s.users);
  const me = useProject((s) => s.me);
  const d = doc!.dictionary;

  const stats = useMemo(() => {
    const classes = d.Classes ?? [];
    const gops = classes.filter((c) => c.ClassType === GOP);
    const cps = classes.reduce((n, c) => n + (c.ClassProperties ?? []).length, 0);
    const rels = classes.reduce((n, c) => n + (c.ClassRelations ?? []).length, 0) + (d.Properties ?? []).reduce((n, p) => n + (p.PropertyRelations ?? []).length, 0);
    return { classes: classes.length - gops.length, gops: gops.length, props: (d.Properties ?? []).length, cps, rels };
  }, [d]);

  const checks = useMemo<Check[]>(() => {
    const classes = (d.Classes ?? []).filter((c) => c.ClassType !== GOP);
    const props = d.Properties ?? [];
    const used = new Set<string>();
    const dangling: Check["items"] = [];
    for (const c of d.Classes ?? [])
      for (const cp of c.ClassProperties ?? []) {
        const code = cp.PropertyCode ?? internalCode(d, cp.PropertyUri, "prop");
        if (code) used.add(code);
        if (cp.PropertyCode && !props.some((p) => p.Code === cp.PropertyCode)) dangling.push({ code: c.Code, name: `${c.Name} → ${cp.PropertyCode}`, kind: "class" });
      }
    const cls = (list: typeof classes) => list.map((c) => ({ code: c.Code, name: c.Name, kind: "class" as const }));
    const prp = (list: typeof props) => list.map((p) => ({ code: p.Code, name: p.Name, kind: "property" as const }));
    return [
      { key: "cdef", label: t("Classes without definition"), items: cls(classes.filter((c) => !c.Definition?.trim())) },
      { key: "cifc", label: t("Classes without IFC entity"), items: cls(classes.filter((c) => !(c.RelatedIfcEntityNamesList ?? []).length)) },
      { key: "cempty", label: t("Classes without properties"), items: cls(classes.filter((c) => !(c.ClassProperties ?? []).length)) },
      { key: "pdef", label: t("Properties without definition"), items: prp(props.filter((p) => !p.Definition?.trim())) },
      { key: "ptype", label: t("Properties without datatype"), items: prp(props.filter((p) => !p.DataType)) },
      { key: "punused", label: t("Unused properties"), items: prp(props.filter((p) => !used.has(p.Code))) },
      { key: "dangling", label: t("Class properties referencing missing properties"), items: dangling },
    ];
  }, [d, t]);

  const base = useProject((s) => s.base);
  const meta = useProject((s) => s.meta);
  const readOnly = base === "/v";
  const url = `${location.origin}${base}/${projectId}`;
  const stat = (label: string, value: number, icon: React.ReactNode, color: string, section: Section) => (
    <Card withBorder padding="md" radius="md" className="stat-card" onClick={() => go(section)}>
      <Group justify="space-between" wrap="nowrap">
        <div>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>{label}</Text>
          <Text fz={28} fw={700} lh={1.2}>{value.toLocaleString()}</Text>
        </div>
        <ThemeIcon size={44} radius="md" variant="light" color={color}>{icon}</ThemeIcon>
      </Group>
    </Card>
  );

  return (
    <div className="page">
      <div className="page-inner">
        <Group justify="space-between" align="flex-end" mb="lg" wrap="wrap">
          <div>
            <Text size="sm" c="dimmed">{d.OrganizationCode} / {d.DictionaryCode}</Text>
            <Title order={2}>{d.DictionaryName || d.DictionaryCode}</Title>
            <Group gap={6} mt={6}>
              <Badge variant="light">v{d.DictionaryVersion}</Badge>
              <Badge variant="light" color="gray">{d.LanguageIsoCode}</Badge>
              {d.Status && <Badge variant="light" color={d.Status === "Active" ? "green" : "yellow"}>{d.Status}</Badge>}
              {d.License && <Badge variant="outline" color="gray">{d.License}</Badge>}
            </Group>
          </div>
          <Group gap="xs">
            <Button data-edit variant="default" leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: null, classType: "Class" } })}>{t("New class")}</Button>
            <Button data-edit variant="default" leftSection={<IconPlus size={14} />} onClick={() => openUi({ propertyEditor: { onCreated: (c) => openProperty(c) } })}>{t("New property")}</Button>
            <Button leftSection={<IconFileExport size={14} />} onClick={() => go("export")}>{t("Export")}</Button>
          </Group>
        </Group>

        <SimpleGrid cols={{ base: 2, sm: 3, lg: 5 }} spacing="md" mb="lg">
          {stat(t("Classes"), stats.classes, <IconBinaryTree2 size={24} />, "orange", "classes")}
          {stat(t("Groups of properties"), stats.gops, <IconStack2 size={24} />, "violet", "groups")}
          {stat(t("Properties"), stats.props, <IconList size={24} />, "blue", "properties")}
          {stat(t("Class properties"), stats.cps, <IconListDetails size={24} />, "cyan", "classes")}
          {stat(t("Relations"), stats.rels, <IconLink size={24} />, "pink", "graph")}
        </SimpleGrid>

        <div className="overview-grid">
          <Card withBorder radius="md" padding="lg">
            <Title order={4} mb="md">{t("Dictionary data")}</Title>
            <DictionaryForm inline />
          </Card>

          <Stack gap="md">
            <Card withBorder radius="md" padding="lg">
              <Group justify="space-between" mb={4} wrap="nowrap">
                <Title order={4}>{t("Collaboration")}</Title>
                {readOnly ? (
                  <Badge variant="light" color="gray" leftSection={<IconEye size={12} />}>{t("Read-only")}</Badge>
                ) : (
                  <Badge variant="light" color={meta?.protected ? "green" : "gray"} leftSection={meta?.protected ? <IconLock size={12} /> : <IconLockOpen size={12} />}>
                    {meta?.protected ? t("Password protected") : t("No password")}
                  </Badge>
                )}
              </Group>
              <Text size="sm" c="dimmed" mb="sm">
                {readOnly
                  ? t("You opened a read-only link: you can browse, search and export, but not edit.")
                  : t("Everybody who has this link can view and edit the dictionary together with you in real time.")}
              </Text>
              <Group gap="xs" wrap="nowrap">
                <TextInput value={url} readOnly style={{ flex: 1 }} onFocus={(e) => e.currentTarget.select()} />
                <CopyButton value={url}>
                  {({ copied, copy }) => (
                    <Tooltip label={copied ? t("Copied") : t("Copy link")}>
                      <Button variant="light" color={copied ? "green" : undefined} onClick={copy} px="xs">{copied ? <IconCheck size={16} /> : <IconCopy size={16} />}</Button>
                    </Tooltip>
                  )}
                </CopyButton>
              </Group>
              {!readOnly && (
                <Button mt="sm" variant="light" size="xs" leftSection={<IconLock size={14} />} onClick={() => openUi({ share: true })}>{t("Password & read-only link…")}</Button>
              )}
              <Text size="xs" c="dimmed" mt="md" mb={6}>{t("Online now")}</Text>
              <Stack gap={6}>
                {users.map((u) => (
                  <Group key={u.id} gap="xs" wrap="nowrap">
                    <Avatar size={26} radius="xl" color={u.color} style={{ border: `2px solid ${u.color}` }}>{u.name.slice(0, 2).toUpperCase()}</Avatar>
                    <Text size="sm" truncate style={{ flex: 1 }}>{u.name}{u.id === me?.id ? ` (${t("you")})` : ""}</Text>
                    {u.role === "view" && <Badge size="xs" variant="light" color="gray">{t("viewer")}</Badge>}
                    {u.selection?.class && (
                      <Anchor size="xs" c="dimmed" onClick={() => openClass(u.selection!.class!)} truncate maw={140}>{u.selection.class}</Anchor>
                    )}
                  </Group>
                ))}
              </Stack>
            </Card>

            <Card withBorder radius="md" padding="lg">
              <Title order={4} mb="sm">{t("Checks")}</Title>
              <Accordion variant="separated" chevronPosition="right" multiple>
                {checks.map((c) => (
                  <Accordion.Item key={c.key} value={c.key}>
                    <Accordion.Control
                      disabled={!c.items.length}
                      icon={c.items.length ? <IconAlertTriangle size={16} color="var(--mantine-color-yellow-6)" /> : <IconCircleCheck size={16} color="var(--mantine-color-green-6)" />}
                    >
                      <Group justify="space-between" wrap="nowrap" pr="xs">
                        <Text size="sm">{c.label}</Text>
                        <Badge size="sm" variant="light" color={c.items.length ? "yellow" : "green"}>{c.items.length}</Badge>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Stack gap={2}>
                        {c.items.slice(0, 50).map((it, i) => (
                          <Anchor key={`${it.code}-${i}`} size="sm" onClick={() => (it.kind === "class" ? openClass(it.code) : openProperty(it.code))} truncate>
                            {it.name} <Text span size="xs" c="dimmed" className="mono">{it.code}</Text>
                          </Anchor>
                        ))}
                        {c.items.length > 50 && <Text size="xs" c="dimmed">{t("{{n}} more", { n: c.items.length - 50 })}</Text>}
                      </Stack>
                    </Accordion.Panel>
                  </Accordion.Item>
                ))}
              </Accordion>
            </Card>
          </Stack>
        </div>
      </div>
    </div>
  );
}
