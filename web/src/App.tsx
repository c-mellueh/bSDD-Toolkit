import { MantineProvider, createTheme, localStorageColorSchemeManager } from "@mantine/core";
import { DatesProvider } from "@mantine/dates";
import { ModalsProvider } from "@mantine/modals";
import { Notifications } from "@mantine/notifications";
import { Center, Loader } from "@mantine/core";
import { Suspense, lazy, useEffect, type ReactNode } from "react";
import { Outlet, Route, RouterProvider, createBrowserRouter, createRoutesFromElements } from "react-router-dom";
import { UnsavedGuard } from "./components/UnsavedGuard";
import { NotFound } from "./pages/NotFound";
import { RouteCrash } from "./components/ErrorBoundary";
import { Landing } from "./pages/Landing";
import { BsddCallback } from "./pages/BsddCallback";
import { ProjectLayout } from "./layout/ProjectLayout";
import { ClassesPage } from "./pages/project/ClassesPage";
import { OverviewPage } from "./pages/project/OverviewPage";
import { PropertiesPage } from "./pages/project/PropertiesPage";
import { useSettings } from "./state/settings";

// large, rarely first-visited parts load on demand (keeps the initial download small)
const GraphPage = lazy(() => import("./pages/GraphPage").then((m) => ({ default: m.GraphPage })));
const GraphRoute = lazy(() => import("./pages/project/GraphRoute").then((m) => ({ default: m.GraphRoute })));
const LoinPage = lazy(() => import("./pages/project/LoinPage").then((m) => ({ default: m.LoinPage })));
const ExportPage = lazy(() => import("./pages/project/ExportPage").then((m) => ({ default: m.ExportPage })));

function Lazy({ children }: { children: ReactNode }) {
  return <Suspense fallback={<Center h="100%" p="xl"><Loader size="sm" /></Center>}>{children}</Suspense>;
}

const theme = createTheme({
  primaryColor: "blue",
  defaultRadius: "md",
  fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
  components: {
    TextInput: { defaultProps: { size: "sm" } },
    Textarea: { defaultProps: { size: "sm" } },
    Select: { defaultProps: { size: "sm", clearButtonProps: { "aria-label": "Clear" } } },
    MultiSelect: { defaultProps: { size: "sm", clearButtonProps: { "aria-label": "Clear" } } },
    TagsInput: { defaultProps: { size: "sm", clearButtonProps: { "aria-label": "Clear" } } },
    NumberInput: { defaultProps: { size: "sm" } },
    Autocomplete: { defaultProps: { size: "sm" } },
    Checkbox: { defaultProps: { size: "sm" } },
    Switch: { defaultProps: { size: "sm" } },
    Button: { defaultProps: { size: "sm" } },
  },
});

/** Shell around every page: resets the title and guards unsaved edits. */
function Root() {
  return (
    <>
      <TitleReset />
      <UnsavedGuard />
      <Outlet />
    </>
  );
}

// data router: needed for useBlocker (warning before leaving a page with unsaved edits)
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<Root />} errorElement={<RouteCrash />}>
      <Route path="/" element={<Landing />} />
      <Route path="/auth/bsdd/callback" element={<BsddCallback />} />
      <Route path="/p/:projectId/window/graph" element={<Lazy><GraphPage /></Lazy>} />
      <Route path="/v/:projectId/window/graph" element={<Lazy><GraphPage base="/v" /></Lazy>} />
      {(["/p", "/v"] as const).map((base) => (
        <Route key={base} path={`${base}/:projectId`} element={<ProjectLayout base={base} />}>
          <Route index element={<OverviewPage />} />
          <Route path="classes/:code?" element={<ClassesPage key="classes" mode="main" />} />
          <Route path="groups/:code?" element={<ClassesPage key="groups" mode="gop" />} />
          <Route path="properties/:code?" element={<PropertiesPage />} />
          <Route path="loin" element={<Lazy><LoinPage /></Lazy>} />
          <Route path="graph" element={<Lazy><GraphRoute /></Lazy>} />
          <Route path="export" element={<Lazy><ExportPage /></Lazy>} />
        </Route>
      ))}
      <Route path="*" element={<NotFound />} />
    </Route>,
  ),
);

const colorSchemeManager = localStorageColorSchemeManager({ key: "bsdd-color-scheme" });

export function App() {
  const themeSetting = useSettings((s) => s.theme);
  const language = useSettings((s) => s.language);
  return (
    <MantineProvider theme={theme} colorSchemeManager={colorSchemeManager} defaultColorScheme="auto" forceColorScheme={themeSetting === "auto" ? undefined : themeSetting}>
      <DatesProvider settings={{ locale: language, firstDayOfWeek: 1 }}>
      <ModalsProvider>
        <Notifications position="bottom-right" />
        <RouterProvider router={router} />
      </ModalsProvider>
      </DatesProvider>
    </MantineProvider>
  );
}

function TitleReset() {
  useEffect(() => {
    document.title = "bSDD Toolkit";
  }, []);
  return null;
}
