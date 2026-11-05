import { Badge, Button, Card, Group, SimpleGrid, Text, ThemeIcon, Title } from "@mantine/core";
import { IconBraces, IconBrandWindows, IconChecklist, IconDeviceFloppy, IconFileCode, IconFileSpreadsheet, IconListCheck, IconTable } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { downloadFile } from "../../api";
import { notifyError } from "../../notify";
import { useProject } from "../../state/project";
import { openUi, type ExportKind } from "../../state/ui";

export function ExportPage() {
  const { t } = useTranslation();
  const projectId = useProject((s) => s.projectId);
  const download = (path: string) => downloadFile(`/api/projects/${projectId}/${path}`, undefined, "GET").catch(notifyError);

  const formats: { kind: ExportKind; title: string; text: string; icon: React.ReactNode; color: string; tag: string }[] = [
    { kind: "excel", title: "Excel", text: t("Classes, properties and class properties as spreadsheet for reviews and bulk editing."), icon: <IconFileSpreadsheet size={26} />, color: "green", tag: ".xlsx" },
    { kind: "ids", title: "IDS", text: t("Information Delivery Specification to check IFC models against the dictionary."), icon: <IconChecklist size={26} />, color: "blue", tag: ".ids" },
    { kind: "iso23386", title: "ISO 23386", text: t("Data templates in the ISO 23386 / 12006-3 exchange format."), icon: <IconFileCode size={26} />, color: "indigo", tag: ".xml" },
    { kind: "iso7817", title: "ISO 7817-3", text: t("Level of Information Need specifications."), icon: <IconListCheck size={26} />, color: "teal", tag: ".xml" },
    { kind: "revit-psets", title: t("Revit property sets"), text: t("Property set definition file for the Revit IFC exporter."), icon: <IconBrandWindows size={26} />, color: "orange", tag: ".txt" },
    { kind: "revit-shared", title: t("Revit shared parameters"), text: t("Shared parameter file to create the parameters in Revit."), icon: <IconTable size={26} />, color: "red", tag: ".txt" },
  ];

  return (
    <div className="page">
      <div className="page-inner">
        <Title order={2} mb={4}>{t("Export")}</Title>
        <Text c="dimmed" mb="lg">{t("Download the dictionary or derived files. Exports can be limited to a Level of Information Need selection.")}</Text>

        <Title order={5} mb="sm">{t("Dictionary")}</Title>
        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" mb="xl">
          <ExportCard icon={<IconBraces size={26} />} color="gray" title="bSDD JSON" tag=".json" text={t("The dictionary in the official bSDD import format.")} action={t("Download")} onClick={() => download("dictionary.json")} />
          <ExportCard icon={<IconDeviceFloppy size={26} />} color="gray" title={t("Project file")} tag=".json" text={t("Dictionary plus editor data (LOIN, temporary property sets, export settings). Can be opened again on the start page.")} action={t("Download")} onClick={() => download("project.json")} />
        </SimpleGrid>

        <Title order={5} mb="sm">{t("Formats")}</Title>
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
          {formats.map((f) => (
            <ExportCard key={f.kind} icon={f.icon} color={f.color} title={f.title} tag={f.tag} text={f.text} action={t("Configure & export")} onClick={() => openUi({ exportKind: f.kind })} />
          ))}
        </SimpleGrid>
      </div>
    </div>
  );
}

function ExportCard(props: { icon: React.ReactNode; color: string; title: string; tag: string; text: string; action: string; onClick: () => void }) {
  return (
    <Card withBorder radius="md" padding="lg" style={{ display: "flex", flexDirection: "column" }}>
      <Group justify="space-between" mb="sm">
        <ThemeIcon size={46} radius="md" variant="light" color={props.color}>{props.icon}</ThemeIcon>
        <Badge variant="light" color="gray">{props.tag}</Badge>
      </Group>
      <Text fw={600}>{props.title}</Text>
      <Text size="sm" c="dimmed" mt={4} style={{ flex: 1 }}>{props.text}</Text>
      <Button variant="light" mt="md" onClick={props.onClick}>{props.action}</Button>
    </Card>
  );
}
