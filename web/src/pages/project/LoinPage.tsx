import { Text, Title } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { LoinEditor } from "../../components/LoinEditor";

export function LoinPage() {
  const { t } = useTranslation();
  return (
    <div className="page fill">
      <div className="page-inner fill">
        <Title order={2} mb={2}>{t("Level of Information Need")}</Title>
        <Text c="dimmed" mb="md">{t("Define which classes and properties are required for which purpose and milestone (ISO 7817-3). Exports can be limited to these selections.")}</Text>
        <div style={{ flex: 1, minHeight: 0 }}>
          <LoinEditor inline />
        </div>
      </div>
    </div>
  );
}
