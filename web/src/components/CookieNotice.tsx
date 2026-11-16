/**
 * Cookie notice. The app sets no cookies and does no tracking: everything it keeps in the browser
 * (local/session storage) is needed for it to work, so there is nothing to consent to – the
 * banner only informs and is shown until it is acknowledged once per browser.
 */
import { Anchor, Button, Collapse, Group, List, Paper, Text } from "@mantine/core";
import { IconCookie } from "@tabler/icons-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { PRIVACY_PATH } from "../pages/Legal";
import { storageGet, storageSet } from "../state/settings";

export const COOKIE_NOTICE_KEY = "bsdd-cookie-notice";

export function CookieNotice() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(() => !storageGet(COOKIE_NOTICE_KEY, false));
  const [details, setDetails] = useState(false);
  if (!open) return null;
  const close = () => {
    storageSet(COOKIE_NOTICE_KEY, true);
    setOpen(false);
  };
  return (
    <Paper
      role="region"
      aria-label={t("Cookie notice")}
      className="cookie-notice"
      shadow="lg"
      withBorder
      p="md"
    >
      <Group gap="sm" wrap="nowrap" align="flex-start">
        <IconCookie size={22} style={{ flex: "none", marginTop: 2 }} />
        <div style={{ minWidth: 0, flex: 1 }}>
          <Text size="sm">
            {t("This app uses no cookies and no tracking. It only stores what it needs to work (settings, recent dictionaries, access keys) in your browser.")}{" "}
            <Anchor component="button" type="button" size="sm" onClick={() => setDetails((d) => !d)} aria-expanded={details}>
              {details ? t("Less") : t("Details")}
            </Anchor>
          </Text>
          <Collapse in={details}>
            <List size="xs" mt="xs" spacing={4} c="dimmed">
              <List.Item>{t("Local storage of this browser: settings (theme, language, layout), recent dictionaries, access keys of shared dictionaries, export selections, your OpenAI key if you enter one, and the in-app clipboard. It stays on this device and can be deleted in the browser settings.")}</List.Item>
              <List.Item>{t("Session storage (cleared when the tab is closed): an ID of this tab for live collaboration and, after signing in to buildingSMART, the sign-in for downloading.")}</List.Item>
              <List.Item>{t("The Python shell loads its runtime from cdn.jsdelivr.net when you open it. The AI helper sends your text directly from the browser to OpenAI with your own key.")}</List.Item>
            </List>
            <Anchor component={Link} to={PRIVACY_PATH} size="xs" mt={6} display="inline-block">
              {t("Privacy policy")}
            </Anchor>
          </Collapse>
        </div>
        <Button size="xs" onClick={close} style={{ flex: "none" }}>
          {t("OK")}
        </Button>
      </Group>
    </Paper>
  );
}
