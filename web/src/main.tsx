import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "./styles.css";
import "./i18n";
import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
