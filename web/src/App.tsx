import { MantineProvider, createTheme, localStorageColorSchemeManager } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import { Notifications } from "@mantine/notifications";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Landing } from "./pages/Landing";
import { ProjectPage } from "./pages/ProjectPage";
import { useSettings } from "./state/settings";

const theme = createTheme({
  primaryColor: "blue",
  defaultRadius: "sm",
  fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
  components: {
    TextInput: { defaultProps: { size: "xs" } },
    Textarea: { defaultProps: { size: "xs" } },
    Select: { defaultProps: { size: "xs" } },
    MultiSelect: { defaultProps: { size: "xs" } },
    TagsInput: { defaultProps: { size: "xs" } },
    NumberInput: { defaultProps: { size: "xs" } },
    Autocomplete: { defaultProps: { size: "xs" } },
    Checkbox: { defaultProps: { size: "xs" } },
    Switch: { defaultProps: { size: "xs" } },
    Button: { defaultProps: { size: "xs" } },
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
            <Route path="/p/:projectId" element={<ProjectPage />} />
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
