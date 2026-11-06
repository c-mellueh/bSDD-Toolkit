import { Center, Loader, Stack, Text } from "@mantine/core";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { completeSignIn } from "../bsddAuth";
import { notifyError, notifyOk } from "../notify";

/** Return address of "Sign in with buildingSMART": redeems the code, then goes back. */
export function BsddCallback() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const done = useRef(false);
  useEffect(() => {
    if (done.current) return; // StrictMode runs effects twice; the code can be used only once
    done.current = true;
    completeSignIn(window.location.search)
      .then((back) => {
        notifyOk(t("Signed in with buildingSMART"));
        navigate(back, { replace: true });
      })
      .catch((e: Error & { back?: string }) => {
        notifyError(e, t("Sign-in with buildingSMART"));
        navigate(e.back ?? "/", { replace: true });
      });
  }, [navigate, t]);
  return (
    <Center h="100%">
      <Stack align="center" gap="xs">
        <Loader />
        <Text size="sm" c="dimmed">{t("Completing sign-in…")}</Text>
      </Stack>
    </Center>
  );
}
