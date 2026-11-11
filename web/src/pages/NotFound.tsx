import { Button, Center, Stack, Text, Title } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

export function NotFound() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  return (
    <Center h="100%" p="md">
      <Stack align="center" gap="xs">
        <Title order={2}>{t("Page not found")}</Title>
        <Text c="dimmed" size="sm" className="mono">{window.location.pathname}</Text>
        <Text c="dimmed" size="sm">{t("This address does not exist in the bSDD Toolkit.")}</Text>
        <Button mt="sm" onClick={() => navigate("/")}>{t("Back to start page")}</Button>
      </Stack>
    </Center>
  );
}
