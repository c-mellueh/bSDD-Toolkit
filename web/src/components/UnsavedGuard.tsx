import { Button, Group, Modal, Text } from "@mantine/core";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useBlocker } from "react-router-dom";
import i18n from "../i18n";
import { forgetUnsaved, hasUnsaved } from "../state/unsaved";
import { askConfirm } from "./dialogs";

/** Called when the user decided to stay: lets pages undo state that ran ahead of the URL. */
const stayHandlers = new Set<() => void>();
export function onNavigationCancelled(fn: () => void) {
  stayHandlers.add(fn);
  return () => {
    stayHandlers.delete(fn);
  };
}

/** Close an editor popup; asks first if it has unsaved changes. */
export async function closePopup(close: () => void) {
  if (hasUnsaved("popup")) {
    const t = i18n.t.bind(i18n);
    const ok = await askConfirm(t("Discard changes?"), t("Your changes have not been saved yet."), t("Discard"), true);
    if (!ok) return;
    forgetUnsaved("popup");
  }
  close();
}

/** Asks before a page with unsaved inline edits is left (links, tree clicks, back/forward). */
export function UnsavedGuard() {
  const { t } = useTranslation();
  const blocker = useBlocker(({ currentLocation, nextLocation }) => currentLocation.pathname !== nextLocation.pathname && hasUnsaved("page"));
  const blocked = blocker.state === "blocked";
  useEffect(() => {
    // nothing left to protect (e.g. saved meanwhile): let the navigation through
    if (blocked && !hasUnsaved("page")) blocker.proceed?.();
  }, [blocked, blocker]);
  const stay = () => {
    blocker.reset?.();
    stayHandlers.forEach((fn) => fn());
  };
  return (
    <Modal opened={blocked} onClose={stay} title={t("Discard changes?")} zIndex={500} centered>
      <Text size="sm">{t("This page has unsaved changes. If you leave it, they are lost.")}</Text>
      <Group justify="flex-end" mt="md">
        <Button variant="default" onClick={stay} data-autofocus>{t("Stay")}</Button>
        <Button
          color="red"
          onClick={() => {
            forgetUnsaved("page");
            blocker.proceed?.();
          }}
        >
          {t("Discard")}
        </Button>
      </Group>
    </Modal>
  );
}
