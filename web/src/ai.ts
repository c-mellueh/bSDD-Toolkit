/* eslint-disable @typescript-eslint/no-explicit-any */
import { AI_PROVIDERS, useSettings, type AiProvider } from "./state/settings";

function instructions(kind: "class" | "property", lang: "German" | "English", sentences: number) {
  if (lang === "German") {
    const what = kind === "class" ? "eine einzelne bSDD-Klasse" : "ein einzelnes bSDD-Merkmal (Property)";
    const def = kind === "class" ? "Klassendefinition" : "Merkmalsdefinition";
    const scope =
      kind === "class"
        ? "Die Definition umfasst baukonstruktive Ausführung, primären Zweck bzw. Funktion sowie typische Einsatzbereiche."
        : "Die Definition beschreibt, welche Eigenschaft erfasst wird, wie sie ermittelt wird und wofür sie verwendet wird.";
    return `Du bist ein erfahrener BIM-Manager und Fachexperte für Infrastruktur- und Ingenieurbauwerke. Du erhältst ${what} im JSON-Format gemäß der buildingSMART-Struktur. Deine Aufgabe ist es, eine fachlich korrekte, prägnante und technisch neutrale Definition in deutscher Sprache zu verfassen. Der Text besteht aus ${sentences} vollständigen Sätzen im normnahen Stil. ${scope} Falls fachlich sinnvoll, können einschlägige Normen wie DIN oder EN benannt werden, jedoch ohne nähere Erläuterung. Verzichte auf Aufzählungen, Wiederholung von JSON-Feldnamen, Beispielwerte sowie Einleitungssätze wie „Diese Klasse beschreibt …“. Gib ausschließlich die formulierte ${def} als zusammenhängenden Fließtext ohne Zusatzkommentare oder Hinweise zurück.`;
  }
  const what = kind === "class" ? "a single bSDD class" : "a single bSDD property";
  const scope =
    kind === "class"
      ? "The definition should include structural design, primary purpose or function, and typical areas of application."
      : "The definition should describe which characteristic is captured, how it is determined and what it is used for.";
  return `You are an experienced BIM manager and expert in infrastructure and civil engineering structures. You will receive ${what} in JSON format according to the buildingSMART structure. Your task is to write a technically correct, concise, and neutral definition in English. The text should consist of ${sentences} complete sentences in a style close to the standards. ${scope} Where technically appropriate, relevant standards such as DIN or EN may be mentioned, but without further explanation. Avoid bullet points, repetition of JSON field names, example values, and introductory sentences such as 'This class describes…'. Return only the formulated definition as a continuous text without additional comments or notes.`;
}

/** Grok / xAI is not allowed: refuse its keys and model names even if pasted into another provider. */
export function forbiddenAi(key: string, model: string): string | null {
  if (/^xai-/i.test(key.trim())) return "xAI (Grok) API keys are not supported.";
  if (/grok/i.test(model)) return "Grok models are not supported.";
  return null;
}

/**
 * Generate a definition with the user's own API key. The request goes directly from the browser
 * to the chosen provider (OpenAI, Anthropic or Google); the key is never sent to this server.
 */
export async function generateDefinition(kind: "class" | "property", data: Record<string, unknown>): Promise<string> {
  const s = useSettings.getState();
  const provider: AiProvider = s.aiProvider;
  const meta = AI_PROVIDERS.find((p) => p.value === provider);
  if (!meta) throw new Error("Unsupported AI provider");
  const key = (s.aiKeys[provider] ?? "").trim();
  const model = (s.aiModels[provider] ?? "").trim() || meta.defaultModel;
  if (!key) throw new Error(`Please enter your ${meta.label} API key in the settings first.`);
  const blocked = forbiddenAi(key, model);
  if (blocked) throw new Error(blocked);

  const header =
    s.aiLanguage === "German"
      ? `Hier ist ${kind === "class" ? "eine bSDD-Klasse" : "ein bSDD-Merkmal"} als JSON. Definiere ${kind === "class" ? "diese Klasse" : "dieses Merkmal"}:`
      : `Here is a bSDD ${kind} as JSON. Define this ${kind}:`;
  const system = instructions(kind, s.aiLanguage, s.aiSentences);
  const input = `${header}\n\n${JSON.stringify(data, null, 2)}`;

  const text =
    provider === "anthropic" ? await viaAnthropic(key, model, system, input)
    : provider === "gemini" ? await viaGemini(key, model, system, input)
    : await viaOpenAi(key, model, system, input);
  if (!text.trim()) throw new Error("The model returned no text");
  return text.trim();
}

async function viaOpenAi(key: string, model: string, system: string, input: string): Promise<string> {
  const body: Record<string, unknown> = { model, instructions: system, input, max_output_tokens: 1024, store: false };
  if (model.startsWith("gpt-5")) {
    body.reasoning = { effort: "minimal" };
    body.text = { verbosity: "low" };
  }
  let res: Response;
  try {
    res = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
      body: JSON.stringify(body),
    });
  } catch {
    // OpenAI answers an invalid key without CORS headers, so the browser only sees a network error
    throw new Error("Could not reach OpenAI. Check that the API key is correct and that you are online.");
  }
  const json: any = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json?.error?.message ?? `OpenAI request failed (${res.status})`);
  const parts: string[] = [];
  for (const item of json.output ?? []) for (const c of item.content ?? []) if (c.type === "output_text" && c.text) parts.push(c.text);
  return parts.join("\n") || json.output_text || "";
}

async function viaAnthropic(key: string, model: string, system: string, input: string): Promise<string> {
  // loaded on first use only (keeps the app download small)
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  // the key belongs to the person using this browser and is sent only to Anthropic
  const client = new Anthropic({ apiKey: key, dangerouslyAllowBrowser: true });
  try {
    const response = await client.beta.messages.create({
      model,
      max_tokens: 16000,
      system,
      messages: [{ role: "user", content: input }],
      // a short definition needs little deliberation
      output_config: { effort: "low" },
      // if a safety classifier declines, let the API retry on its recommended fallback model
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
    });
    if (response.stop_reason === "refusal") throw new Error("Claude declined to write this definition.");
    return response.content.map((b) => (b.type === "text" ? b.text : "")).join("");
  } catch (error) {
    if (error instanceof Anthropic.AuthenticationError) throw new Error("The Anthropic API key is invalid.");
    if (error instanceof Anthropic.RateLimitError) throw new Error("Anthropic rate limit reached. Please try again later.");
    if (error instanceof Anthropic.APIError) throw new Error(`Anthropic request failed (${error.status}): ${error.message}`);
    throw error;
  }
}

async function viaGemini(key: string, model: string, system: string, input: string): Promise<string> {
  const { GoogleGenAI } = await import("@google/genai");
  const ai = new GoogleGenAI({ apiKey: key });
  try {
    const interaction = await ai.interactions.create({
      model,
      input,
      system_instruction: system,
      generation_config: { max_output_tokens: 2048, thinking_level: "low" },
    });
    return interaction.output_text ?? "";
  } catch (error: any) {
    // the SDK does not always pass the server's message on - explain by status code
    const status = Number(error?.status ?? error?.statusCode ?? error?.httpMeta?.response?.status ?? /^(\d{3}) /.exec(String(error?.message))?.[1]);
    const detail = error?.error?.message ?? error?.error?.error?.message;
    if (status === 400 || status === 401 || status === 403) throw new Error(detail ?? "The Gemini API key is invalid or not allowed to use this model.");
    if (status === 404) throw new Error(`Gemini model "${model}" was not found.`);
    if (status === 429) throw new Error("Gemini rate limit or quota reached. Please try again later.");
    if (status) throw new Error(`Gemini request failed (${status})${detail ? `: ${detail}` : ""}`);
    throw new Error("Could not reach Google Gemini. Check your network connection.");
  }
}
