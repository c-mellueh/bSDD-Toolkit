import { create } from "zustand";

export interface Settings {
  language: "en" | "de";
  theme: "auto" | "light" | "dark";
  userName: string;
  pasteSeparator: string;
  aiKey: string;
  aiModel: string;
  aiLanguage: "German" | "English";
  aiSentences: number;
  allowUnknownUri: boolean;
  /** optional columns of the class trees */
  treeColumns: { code: boolean; status: boolean };
}

const KEY = "bsdd-settings";

function load(): Settings {
  const defaults: Settings = {
    language: navigator.language?.toLowerCase().startsWith("de") ? "de" : "en",
    theme: "auto",
    userName: `Guest ${Math.floor(Math.random() * 900 + 100)}`,
    pasteSeparator: "\n",
    aiKey: "",
    aiModel: "gpt-5-nano",
    aiLanguage: "English",
    aiSentences: 2,
    allowUnknownUri: true,
    treeColumns: { code: true, status: true },
  };
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...defaults, ...JSON.parse(raw) };
  } catch {
    /* storage unavailable */
  }
  return defaults;
}

interface SettingsState extends Settings {
  set: (patch: Partial<Settings>) => void;
}

export const useSettings = create<SettingsState>((set, get) => ({
  ...load(),
  set: (patch) => {
    set(patch);
    try {
      const { set: _ignored, ...rest } = { ...get(), ...patch };
      void _ignored;
      localStorage.setItem(KEY, JSON.stringify(rest));
    } catch {
      /* ignore */
    }
  },
}));

export function storageGet<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function storageSet(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* ignore */
  }
}

export interface RecentProject {
  id: string;
  name: string;
  opened: number;
  /** "/v" for read-only links */
  base?: "/p" | "/v";
}

export function rememberProject(id: string, name: string, base: "/p" | "/v" = "/p") {
  const list = storageGet<RecentProject[]>("bsdd-recent", []).filter((p) => p.id !== id);
  list.unshift({ id, name, opened: Date.now(), base });
  storageSet("bsdd-recent", list.slice(0, 30));
}

export function forgetProject(id: string) {
  storageSet(
    "bsdd-recent",
    storageGet<RecentProject[]>("bsdd-recent", []).filter((p) => p.id !== id),
  );
}

export function clientId(): string {
  try {
    let id = sessionStorage.getItem("bsdd-client-id");
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
      sessionStorage.setItem("bsdd-client-id", id);
    }
    return id;
  } catch {
    return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }
}

/** Two-letter avatar label that tells users apart ("Christoph Mellüh" → "CM", "Guest 245" → "45"). */
export function initials(name: string): string {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return "?";
  const num = words.find((w) => /^\d+$/.test(w));
  if (num) return num.slice(-2);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}
