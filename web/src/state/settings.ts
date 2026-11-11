import { create } from "zustand";

/** AI providers the helper may use. xAI / Grok is deliberately not supported. */
export type AiProvider = "openai" | "anthropic" | "gemini";

export const AI_PROVIDERS: { value: AiProvider; label: string; defaultModel: string; keyHint: string }[] = [
  { value: "openai", label: "OpenAI", defaultModel: "gpt-5-nano", keyHint: "sk-…" },
  { value: "anthropic", label: "Anthropic Claude", defaultModel: "claude-opus-5-5", keyHint: "sk-ant-…" },
  { value: "gemini", label: "Google Gemini", defaultModel: "gemini-3.5-flash-lite", keyHint: "AIza…" },
];

export interface Settings {
  language: "en" | "de";
  theme: "auto" | "light" | "dark";
  userName: string;
  pasteSeparator: string;
  aiProvider: AiProvider;
  /** API key per provider (stays in this browser) */
  aiKeys: Record<AiProvider, string>;
  /** model per provider */
  aiModels: Record<AiProvider, string>;
  aiLanguage: "German" | "English";
  aiSentences: number;
  allowUnknownUri: boolean;
  /** optional columns of the class trees */
  treeColumns: { code: boolean; status: boolean };
  /** prefix for the code of new predefined property sets (Groups of Properties), e.g. "Pset_" */
  gopPrefix: string;
  /** creating a property set in a class also creates a Group of Properties if none has that name */
  autoCreateGop: boolean;
}

const KEY = "bsdd-settings";

function load(): Settings {
  const defaults: Settings = {
    language: navigator.language?.toLowerCase().startsWith("de") ? "de" : "en",
    theme: "auto",
    userName: `Guest ${Math.floor(Math.random() * 900 + 100)}`,
    pasteSeparator: "\n",
    aiProvider: "openai",
    aiKeys: { openai: "", anthropic: "", gemini: "" },
    aiModels: { openai: "gpt-5-nano", anthropic: "claude-opus-5-5", gemini: "gemini-3.5-flash-lite" },
    aiLanguage: "English",
    aiSentences: 2,
    allowUnknownUri: true,
    treeColumns: { code: true, status: true },
    gopPrefix: "EPset_",
    autoCreateGop: false,
  };
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const stored = JSON.parse(raw);
      const merged: Settings = { ...defaults, ...stored, aiKeys: { ...defaults.aiKeys, ...stored.aiKeys }, aiModels: { ...defaults.aiModels, ...stored.aiModels } };
      // settings from before multi-provider support: a single OpenAI key and model
      if (typeof stored.aiKey === "string" && stored.aiKey && !stored.aiKeys) merged.aiKeys.openai = stored.aiKey;
      if (typeof stored.aiModel === "string" && stored.aiModel && !stored.aiModels) merged.aiModels.openai = stored.aiModel;
      delete (merged as unknown as Record<string, unknown>).aiKey;
      delete (merged as unknown as Record<string, unknown>).aiModel;
      if (!AI_PROVIDERS.some((p) => p.value === merged.aiProvider)) merged.aiProvider = "openai";
      return merged;
    }
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
