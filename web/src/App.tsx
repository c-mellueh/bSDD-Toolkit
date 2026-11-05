import { MantineProvider, createTheme, localStorageColorSchemeManager } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import { Notifications } from "@mantine/notifications";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Landing } from "./pages/Landing";
import { GraphPage } from "./pages/GraphPage";
import { ProjectLayout } from "./layout/ProjectLayout";
import { ClassesPage } from "./pages/project/ClassesPage";
import { ExportPage } from "./pages/project/ExportPage";
import { GraphRoute } from "./pages/project/GraphRoute";
import { LoinPage } from "./pages/project/LoinPage";
import { OverviewPage } from "./pages/project/OverviewPage";
import { PropertiesPage } from "./pages/project/PropertiesPage";
import { useSettings } from "./state/settings";

const theme = createTheme({
  primaryColor: "blue",
  defaultRadius: "md",
  fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
  components: {
    TextInput: { defaultProps: { size: "sm" } },
    Textarea: { defaultProps: { size: "sm" } },
    Select: { defaultProps: { size: "sm" } },
    MultiSelect: { defaultProps: { size: "sm" } },
    TagsInput: { defaultProps: { size: "sm" } },
    NumberInput: { defaultProps: { size: "sm" } },
    Autocomplete: { defaultProps: { size: "sm" } },
    Checkbox: { defaultProps: { size: "sm" } },
    Switch: { defaultProps: { size: "sm" } },
    Button: { defaultProps: { size: "sm" } },
  },
});

const colorSchemeManager = localStorageColorSchemeManager({ key: "bsdd-color-scheme" });

export function App() {
  const themeSetting = useSettings((s) => s.theme);
  return (
    <MantineProvider theme={theme} colorSchemeManager={colorSchemeManager} defaultColorScheme="auto" forceColorScheme={themeSetting === "auto" ? undefined : themeSetting}>
      <ModalsProvider>
        <Notifications position="bottom-right" />
        <BrowserRouter>
          <TitleReset />
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/p/:projectId/window/graph" element={<GraphPage />} />
            <Route path="/v/:projectId/window/graph" element={<GraphPage base="/v" />} />
            {(["/p", "/v"] as const).map((base) => (
            <Route key={base} path={`${base}/:projectId`} element={<ProjectLayout base={base} />}>
              <Route index element={<OverviewPage />} />
              <Route path="classes/:code?" element={<ClassesPage key="classes" mode="main" />} />
              <Route path="groups/:code?" element={<ClassesPage key="groups" mode="gop" />} />
              <Route path="properties/:code?" element={<PropertiesPage />} />
              <Route path="loin" element={<LoinPage />} />
              <Route path="graph" element={<GraphRoute />} />
              <Route path="export" element={<ExportPage />} />
            </Route>
            ))}
            <Route path="*" element={<Landing />} />
          </Routes>
        </BrowserRouter>
      </ModalsProvider>
    </MantineProvider>
  );
}

function TitleReset() {
  useEffect(() => {
    document.title = "bSDD Toolkit";
  }, []);
  return null;
}
