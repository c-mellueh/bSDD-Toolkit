import { notifications } from "@mantine/notifications";
import i18n from "./i18n";

export function notifyError(e: unknown, title?: string) {
  const message = e instanceof Error ? e.message : String(e);
  notifications.show({ color: "red", title: title ?? i18n.t("Error"), message, autoClose: 7000 });
}

export function notifyOk(message: string, title?: string) {
  notifications.show({ color: "green", title, message, autoClose: 3000 });
}

/** Run an async action and report errors as a notification. Returns undefined on failure. */
export async function attempt<T>(fn: () => Promise<T>, okMessage?: string): Promise<T | undefined> {
  try {
    const result = await fn();
    if (okMessage) notifyOk(okMessage);
    return result;
  } catch (e) {
    notifyError(e);
    return undefined;
  }
}
