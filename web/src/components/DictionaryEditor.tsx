import { Modal } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { DictionaryForm } from "../forms/DictionaryForm";
import { useUi } from "../state/ui";
import { closePopup } from "./UnsavedGuard";

export function DictionaryEditor() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.dictionaryEditor);
  if (!opened) return null;
  const close = () => useUi.getState().set({ dictionaryEditor: false });
  return (
    <Modal opened onClose={() => closePopup(close)} title={t("Dictionary data")} size="lg">
      <DictionaryForm onCancel={() => closePopup(close)} onDone={close} />
    </Modal>
  );
}
