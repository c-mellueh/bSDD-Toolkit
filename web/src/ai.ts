/* eslint-disable @typescript-eslint/no-explicit-any */
import { useSettings } from "./state/settings";

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

/** Generate a definition with the user's own OpenAI key (called directly from the browser). */
export async function generateDefinition(kind: "class" | "property", data: Record<string, unknown>): Promise<string> {
  const s = useSettings.getState();
  if (!s.aiKey) throw new Error("Please enter your OpenAI API key in the settings first.");
  const header =
    s.aiLanguage === "German"
      ? `Hier ist ${kind === "class" ? "eine bSDD-Klasse" : "ein bSDD-Merkmal"} als JSON. Definiere ${kind === "class" ? "diese Klasse" : "dieses Merkmal"}:`
      : `Here is a bSDD ${kind} as JSON. Define this ${kind}:`;
  const body: Record<string, unknown> = {
    model: s.aiModel || "gpt-5-nano",
    instructions: instructions(kind, s.aiLanguage, s.aiSentences),
    input: `${header}\n\n${JSON.stringify(data, null, 2)}`,
    max_output_tokens: 1024,
    store: false,
  };
  if ((s.aiModel || "gpt-5").startsWith("gpt-5")) {
    body.reasoning = { effort: "minimal" };
    body.text = { verbosity: "low" };
  }
  const res = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${s.aiKey}` },
    body: JSON.stringify(body),
  });
  const json: any = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json?.error?.message ?? `OpenAI request failed (${res.status})`);
  const parts: string[] = [];
  for (const item of json.output ?? []) for (const c of item.content ?? []) if (c.type === "output_text" && c.text) parts.push(c.text);
  const text = (parts.join("\n") || json.output_text || "").trim();
  if (!text) throw new Error("The model returned no text");
  return text;
}
