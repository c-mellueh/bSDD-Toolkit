import { Button, Center, Code, Group, Stack, Text, Title } from "@mantine/core";
import { Component, type ErrorInfo, type ReactNode } from "react";
import { useRouteError } from "react-router-dom";
import i18n from "../i18n";

/** Shown instead of a part of the page that crashed. */
export function CrashMessage({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const t = i18n.t.bind(i18n);
  const message = error instanceof Error ? error.message : String(error);
  return (
    <Center h="100%" p="lg">
      <Stack align="center" gap="xs" maw={520}>
        <Title order={3}>{t("Something went wrong")}</Title>
        <Text size="sm" c="dimmed" ta="center">
          {t("This part of the page could not be displayed. Your dictionary is not affected – changes already saved are safe.")}
        </Text>
        <Code block style={{ maxWidth: "100%", whiteSpace: "pre-wrap" }}>{message}</Code>
        <Group mt="xs">
          {onRetry && <Button variant="default" onClick={onRetry}>{t("Try again")}</Button>}
          <Button onClick={() => window.location.reload()}>{t("Reload page")}</Button>
        </Group>
      </Stack>
    </Center>
  );
}

/** Catches render errors below it so the rest of the app (navigation, other pages) keeps working. */
export class ErrorBoundary extends Component<{ children: ReactNode; resetKey?: string }, { error: unknown }> {
  state = { error: null as unknown };

  static getDerivedStateFromError(error: unknown) {
    return { error };
  }

  componentDidCatch(error: unknown, info: ErrorInfo) {
    console.error("Render error", error, info.componentStack);
  }

  componentDidUpdate(prev: { resetKey?: string }) {
    // navigating elsewhere clears the error
    if (this.state.error && prev.resetKey !== this.props.resetKey) this.setState({ error: null });
  }

  render() {
    if (this.state.error) return <CrashMessage error={this.state.error} onRetry={() => this.setState({ error: null })} />;
    return this.props.children;
  }
}

/** errorElement of the router: errors outside any ErrorBoundary. */
export function RouteCrash() {
  return <CrashMessage error={useRouteError()} />;
}
