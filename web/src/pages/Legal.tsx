/**
 * Imprint and privacy policy. The operator details come from the server settings
 * (OPERATOR_NAME, OPERATOR_ADDRESS, ... – see README); the text describes what this app does with
 * data. Long legal text is written per language here instead of in the translation file.
 */
import { Alert, Anchor, Button, Center, Container, Group, List, Loader, Stack, Text, Title } from "@mantine/core";
import { IconArrowLeft, IconInfoCircle } from "@tabler/icons-react";
import { useEffect, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

export interface LegalConfig {
  name: string;
  address: string;
  email: string;
  phone: string;
  imprint_extra: string;
  privacy_extra: string;
  project_ttl_days: number;
  max_snapshots: number;
  bsdd_login: boolean;
  offline: boolean;
}

export const IMPRINT_PATH = "/imprint";
export const PRIVACY_PATH = "/privacy";
const SOURCE_URL = "https://github.com/c-mellueh/bSDD-Toolkit";

let legalPromise: Promise<LegalConfig | null> | null = null;
function loadLegal(): Promise<LegalConfig | null> {
  legalPromise ??= api<{ legal?: LegalConfig }>("/api/config")
    .then((r) => r.legal ?? null)
    .catch(() => {
      legalPromise = null; // try again next time
      return null;
    });
  return legalPromise;
}

function useLegal() {
  const [cfg, setCfg] = useState<LegalConfig | null | undefined>(undefined);
  useEffect(() => {
    let alive = true;
    loadLegal().then((c) => alive && setCfg(c));
    return () => {
      alive = false;
    };
  }, []);
  return cfg;
}

/** "Imprint · Privacy policy" – small links for footers. */
export function LegalLinks({ size = "xs" }: { size?: "xs" | "sm" }) {
  const { t } = useTranslation();
  return (
    <Group gap={6} wrap="nowrap">
      <Anchor component={Link} to={IMPRINT_PATH} size={size} c="dimmed">{t("Imprint")}</Anchor>
      <Text size={size} c="dimmed">·</Text>
      <Anchor component={Link} to={PRIVACY_PATH} size={size} c="dimmed">{t("Privacy policy")}</Anchor>
    </Group>
  );
}

function Page({ title, children }: { title: string; children: ReactNode }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  useEffect(() => {
    document.title = `${title} – bSDD Toolkit`;
    return () => {
      document.title = "bSDD Toolkit";
    };
  }, [title]);
  return (
    <div style={{ height: "100%", overflow: "auto" }}>
      <Container size="sm" py="xl" className="legal-page">
        <Button
          variant="subtle"
          size="xs"
          leftSection={<IconArrowLeft size={14} />}
          mb="md"
          onClick={() => (window.history.length > 1 ? navigate(-1) : navigate("/"))}
        >
          {t("Back")}
        </Button>
        <Title order={2} mb="lg">{title}</Title>
        <Stack gap="lg">{children}</Stack>
        <Group justify="space-between" mt="xl">
          <LegalLinks size="sm" />
          <Anchor component={Link} to="/" size="sm">{t("Start page")}</Anchor>
        </Group>
      </Container>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <Title order={4} mb={6}>{title}</Title>
      <Stack gap={6}>{children}</Stack>
    </section>
  );
}

const P = ({ children }: { children: ReactNode }) => <Text size="sm">{children}</Text>;

/** Name, address and contact – or a note that the operator has not entered them. */
function Operator({ cfg, de }: { cfg: LegalConfig | null; de: boolean }) {
  if (!cfg?.name) {
    return (
      <Alert color="yellow" icon={<IconInfoCircle size={18} />}>
        {de
          ? "Der Betreiber dieser Installation hat seine Angaben noch nicht hinterlegt."
          : "The operator of this installation has not entered their details yet."}
        <Text size="xs" c="dimmed" mt={4}>
          {de ? "Für Betreiber: " : "For operators: "}
          <code>OPERATOR_NAME</code>, <code>OPERATOR_ADDRESS</code>, <code>OPERATOR_EMAIL</code>, <code>OPERATOR_PHONE</code>
        </Text>
      </Alert>
    );
  }
  return (
    <div className="legal-operator">
      <Text size="sm" fw={600}>{cfg.name}</Text>
      {cfg.address && <Text size="sm" style={{ whiteSpace: "pre-line" }}>{cfg.address}</Text>}
      {(cfg.email || cfg.phone) && (
        <Text size="sm" mt={6}>
          {cfg.email && (
            <>
              {de ? "E-Mail: " : "Email: "}
              <Anchor href={`mailto:${cfg.email}`} size="sm">{cfg.email}</Anchor>
              {cfg.phone && <br />}
            </>
          )}
          {cfg.phone && <>{de ? "Telefon: " : "Phone: "}{cfg.phone}</>}
        </Text>
      )}
    </div>
  );
}

function Extra({ text }: { text: string }) {
  return text ? <Text size="sm" style={{ whiteSpace: "pre-line" }}>{text}</Text> : null;
}

function useDe() {
  const { i18n } = useTranslation();
  return (i18n.resolvedLanguage ?? i18n.language ?? "en").startsWith("de");
}

function Loading() {
  return <Center h="100%" p="xl"><Loader size="sm" /></Center>;
}

export function ImprintPage() {
  const { t } = useTranslation();
  const de = useDe();
  const cfg = useLegal();
  if (cfg === undefined) return <Loading />;
  return (
    <Page title={t("Imprint")}>
      <Section title={de ? "Angaben gemäß § 5 DDG" : "Information according to § 5 DDG (German Digital Services Act)"}>
        <Operator cfg={cfg} de={de} />
        {cfg && <Extra text={cfg.imprint_extra} />}
      </Section>
      <Section title={de ? "Inhalte der Wörterbücher" : "Content of the dictionaries"}>
        <P>
          {de
            ? "Die Wörterbücher in dieser Anwendung werden von ihren Nutzerinnen und Nutzern erstellt und bearbeitet. Für deren Inhalte sind die jeweiligen Ersteller verantwortlich. Werden uns Rechtsverletzungen bekannt, entfernen wir die betroffenen Inhalte umgehend."
            : "The dictionaries in this application are created and edited by its users, who are responsible for their content. If we become aware of any infringement, we will remove the content concerned without delay."}
        </P>
      </Section>
      <Section title={de ? "Software" : "Software"}>
        <P>
          {de ? "Der bSDD Toolkit ist Open Source: " : "bSDD Toolkit is open source: "}
          <Anchor href={SOURCE_URL} target="_blank" rel="noreferrer" size="sm">{SOURCE_URL.replace("https://", "")}</Anchor>
        </P>
      </Section>
    </Page>
  );
}

export function PrivacyPage() {
  const { t } = useTranslation();
  const de = useDe();
  const cfg = useLegal();
  if (cfg === undefined) return <Loading />;
  const ttl = cfg?.project_ttl_days ?? 0;
  const snapshots = cfg?.max_snapshots ?? 20;
  return (
    <Page title={t("Privacy policy")}>
      <Section title={de ? "Verantwortlicher" : "Controller"}>
        <Operator cfg={cfg} de={de} />
      </Section>

      <Section title={de ? "Überblick" : "Overview"}>
        <P>
          {de
            ? "Diese Anwendung setzt keine Cookies, verwendet keine Analyse- oder Tracking-Dienste, zeigt keine Werbung und benötigt kein Benutzerkonto."
            : "This application sets no cookies, uses no analytics or tracking services, shows no advertising and needs no user account."}
        </P>
      </Section>

      <Section title={de ? "Server-Protokolle" : "Server logs"}>
        <P>
          {de
            ? "Bei jedem Aufruf verarbeitet der Server Ihre IP-Adresse, Zeitpunkt, aufgerufene Adresse und Statuscode der Antwort und schreibt sie in sein Protokoll. Das ist für den Betrieb und die Sicherheit der Anwendung nötig (Art. 6 Abs. 1 lit. f DSGVO). Die Protokolle werden nicht ausgewertet, um Nutzer zu verfolgen, und nur so lange aufbewahrt, wie es für diese Zwecke erforderlich ist."
            : "With every request the server processes your IP address, the time, the requested address and the status code of the response and writes them to its log. This is necessary to run and secure the application (Art. 6(1)(f) GDPR). The logs are not analysed to track users and are kept only as long as necessary for these purposes."}
        </P>
      </Section>

      <Section title={de ? "Wörterbücher" : "Dictionaries"}>
        <P>
          {de
            ? "Wörterbücher, die Sie anlegen, hochladen oder herunterladen, werden mit ihrem Inhalt auf dem Server gespeichert, damit Sie und andere über den Link daran arbeiten können (Art. 6 Abs. 1 lit. b und f DSGVO). Jede Person mit dem Link kann das Wörterbuch öffnen; optional können Sie es mit einem Passwort schützen, das nur als gesalzener Hash gespeichert wird."
            : "Dictionaries you create, upload or download are stored with their content on the server so that you and others can work on them via their link (Art. 6(1)(b) and (f) GDPR). Anybody with the link can open the dictionary; you can optionally protect it with a password, which is only stored as a salted hash."}
        </P>
        <P>
          {de
            ? `Zusätzlich werden bis zu ${snapshots} ältere Stände als Versionsverlauf aufbewahrt. Über „Löschen“ in der Anwendung wird ein Wörterbuch mit allen Ständen entfernt.`
            : `In addition, up to ${snapshots} earlier states are kept as version history. "Delete" in the application removes a dictionary with all its states.`}{" "}
          {ttl > 0
            ? de
              ? `Wörterbücher, die ${ttl} Tage lang nicht geöffnet wurden, werden automatisch gelöscht.`
              : `Dictionaries that were not opened for ${ttl} days are deleted automatically.`
            : de
              ? "Wörterbücher werden nicht automatisch gelöscht."
              : "Dictionaries are not deleted automatically."}
        </P>
        <P>
          {de
            ? "Bitte legen Sie in Wörterbüchern keine personenbezogenen Daten ab, die dort nicht hingehören."
            : "Please do not put personal data in dictionaries that does not belong there."}
        </P>
      </Section>

      <Section title={de ? "Gemeinsame Bearbeitung" : "Working together"}>
        <P>
          {de
            ? "Solange ein Wörterbuch geöffnet ist, werden der von Ihnen gewählte Anzeigename, eine zufällige Kennung Ihres Tabs und das gerade gewählte Element (z. B. eine Klasse) an den Server übertragen und den anderen Personen angezeigt, die dasselbe Wörterbuch geöffnet haben. Diese Angaben liegen nur im Arbeitsspeicher des Servers und werden nicht gespeichert."
            : "While a dictionary is open, the display name you choose, a random ID of your tab and the item you have selected (e.g. a class) are sent to the server and shown to the other people who have the same dictionary open. These details are only held in the server's memory and are not stored."}
        </P>
      </Section>

      <Section title={de ? "Speicher im Browser" : "Storage in your browser"}>
        <P>
          {de
            ? "Die Anwendung speichert in Ihrem Browser nur, was sie zum Funktionieren braucht (§ 25 Abs. 2 Nr. 2 TDDDG):"
            : "The application stores only what it needs to work in your browser (§ 25(2) no. 2 TDDDG, German Telecommunications Digital Services Data Protection Act):"}
        </P>
        <List size="sm" spacing={4}>
          <List.Item>
            {de
              ? "Lokaler Speicher: Einstellungen (Design, Sprache, Layout), zuletzt geöffnete Wörterbücher, Zugangsschlüssel geteilter Wörterbücher, Export-Auswahlen, Ihr OpenAI-Schlüssel, falls Sie ihn eingeben, und die Zwischenablage der Anwendung. Er bleibt auf Ihrem Gerät und kann in den Browser-Einstellungen gelöscht werden."
              : "Local storage: settings (theme, language, layout), recently opened dictionaries, access keys of shared dictionaries, export selections, your OpenAI key if you enter one, and the in-app clipboard. It stays on your device and can be deleted in the browser settings."}
          </List.Item>
          <List.Item>
            {de
              ? "Sitzungsspeicher (wird beim Schließen des Tabs gelöscht): die Kennung des Tabs und, nach der Anmeldung bei buildingSMART, die Anmeldung für den Download."
              : "Session storage (cleared when the tab is closed): the ID of the tab and, after signing in to buildingSMART, the sign-in for downloading."}
          </List.Item>
        </List>
      </Section>

      <Section title={de ? "Externe Dienste" : "External services"}>
        <List size="sm" spacing={6}>
          {!cfg?.offline && (
            <List.Item>
              <b>buildingSMART Data Dictionary</b> –{" "}
              {de
                ? "Beim Download von Wörterbüchern und beim Auflösen externer Klassen und Merkmale fragt der Server die bSDD-Schnittstelle von buildingSMART International ab. Dabei wird Ihre IP-Adresse nicht übermittelt."
                : "When downloading dictionaries and resolving external classes and properties, the server queries the bSDD interface of buildingSMART International. Your IP address is not passed on."}
            </List.Item>
          )}
          {cfg?.bsdd_login && (
            <List.Item>
              <b>{de ? "Anmeldung bei buildingSMART" : "Sign in with buildingSMART"}</b> –{" "}
              {de
                ? "Wenn Sie sich für den vollständigen Download anmelden, geschieht das auf der Seite von buildingSMART; dort gilt deren Datenschutzerklärung. Das Zugangstoken bleibt in Ihrem Tab und wird nur für den Download an diesen Server geschickt, der es an buildingSMART weiterreicht und nicht speichert."
                : "If you sign in for the complete download, you do so on buildingSMART's page, where their privacy policy applies. The access token stays in your tab and is sent to this server only for the download, which passes it on to buildingSMART and does not store it."}
            </List.Item>
          )}
          <List.Item>
            <b>jsDelivr</b> –{" "}
            {de
              ? "Wenn Sie die Python-Shell öffnen, lädt Ihr Browser deren Laufzeitumgebung (Pyodide) vom Content-Delivery-Netzwerk cdn.jsdelivr.net. Dabei wird Ihre IP-Adresse an jsDelivr übertragen (Art. 6 Abs. 1 lit. f DSGVO). Ohne die Shell findet kein Aufruf statt."
              : "When you open the Python shell, your browser loads its runtime (Pyodide) from the content delivery network cdn.jsdelivr.net, which receives your IP address (Art. 6(1)(f) GDPR). Without the shell, no request is made."}
          </List.Item>
          <List.Item>
            <b>OpenAI</b> –{" "}
            {de
              ? "Nur wenn Sie den KI-Assistenten mit Ihrem eigenen API-Schlüssel nutzen, sendet Ihr Browser den jeweiligen Text direkt an OpenAI (USA); dort gelten die Bedingungen von OpenAI. Der Server dieser Anwendung ist daran nicht beteiligt."
              : "Only if you use the AI helper with your own API key does your browser send the text in question directly to OpenAI (USA), whose terms apply. This application's server is not involved."}
          </List.Item>
        </List>
        {cfg && <Extra text={cfg.privacy_extra} />}
      </Section>

      <Section title={de ? "Ihre Rechte" : "Your rights"}>
        <P>
          {de
            ? "Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung, auf Datenübertragbarkeit sowie auf Widerspruch gegen die Verarbeitung (Art. 15–21 DSGVO). Wenden Sie sich dazu an den oben genannten Verantwortlichen. Da es keine Benutzerkonten gibt, nennen Sie bitte den Link des betroffenen Wörterbuchs. Außerdem können Sie sich bei einer Datenschutz-Aufsichtsbehörde beschweren."
            : "You have the right of access, rectification, erasure and restriction of processing, the right to data portability and the right to object to processing (Art. 15–21 GDPR). Please contact the controller named above; as there are no user accounts, please include the link of the dictionary concerned. You can also lodge a complaint with a data protection supervisory authority."}
        </P>
      </Section>
    </Page>
  );
}
