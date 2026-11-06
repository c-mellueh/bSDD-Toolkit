/**
 * "Sign in with buildingSMART" (OAuth 2.0 authorization code flow with PKCE, single-page app).
 *
 * Only active when the server is configured with BSDD_CLIENT_ID. The access token stays in this
 * browser tab (sessionStorage) and is sent to this server only for a full dictionary download,
 * which forwards it to buildingSMART without storing it.
 */
import { api } from "./api";

export interface BsddLoginConfig {
  client_id: string;
  authority: string;
  scope: string;
  /** configured return address (PUBLIC_URL); null = derive from the current address */
  redirect_uri: string | null;
}

interface StoredToken {
  access_token: string;
  expires_at: number;
  name?: string;
}

const TOKEN_KEY = "bsdd-auth-token";
const FLOW_KEY = "bsdd-auth-flow";
/** set before leaving for the sign-in page: reopen the download dialog when back */
export const REOPEN_KEY = "bsdd-auth-reopen";
export const CALLBACK_PATH = "/auth/bsdd/callback";

let configPromise: Promise<BsddLoginConfig | null> | null = null;

export function loginConfig(): Promise<BsddLoginConfig | null> {
  configPromise ??= api<{ bsdd_login: BsddLoginConfig | null }>("/api/config")
    .then((r) => r.bsdd_login ?? null)
    .catch(() => null);
  return configPromise;
}

const redirectUri = (cfg: BsddLoginConfig) => cfg.redirect_uri || `${window.location.origin}${CALLBACK_PATH}`;
const scopes = (cfg: BsddLoginConfig) => `openid offline_access ${cfg.scope}`;

function storage(): Storage | null {
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

function b64url(bytes: Uint8Array): string {
  let s = "";
  bytes.forEach((b) => (s += String.fromCharCode(b)));
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function randomString(n = 32): string {
  return b64url(crypto.getRandomValues(new Uint8Array(n)));
}

async function challenge(verifier: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  return b64url(new Uint8Array(digest));
}

/** Leave for the buildingSMART sign-in page; afterwards the user comes back to ``returnTo``. */
export async function signIn(returnTo: string = window.location.pathname + window.location.search): Promise<void> {
  const cfg = await loginConfig();
  if (!cfg) throw new Error("Sign-in with buildingSMART is not configured on this server");
  const verifier = randomString(48);
  const state = randomString(16);
  storage()?.setItem(FLOW_KEY, JSON.stringify({ verifier, state, returnTo }));
  storage()?.setItem(REOPEN_KEY, "1");
  const params = new URLSearchParams({
    client_id: cfg.client_id,
    response_type: "code",
    redirect_uri: redirectUri(cfg),
    response_mode: "query",
    scope: scopes(cfg),
    state,
    code_challenge: await challenge(verifier),
    code_challenge_method: "S256",
  });
  window.location.assign(`${cfg.authority}/oauth2/v2.0/authorize?${params}`);
}

function nameFromIdToken(idToken?: string): string | undefined {
  try {
    const part = idToken?.split(".")[1];
    if (!part) return undefined;
    const claims = JSON.parse(decodeURIComponent(escape(atob(part.replace(/-/g, "+").replace(/_/g, "/")))));
    return claims.name || claims.email || (Array.isArray(claims.emails) ? claims.emails[0] : undefined);
  } catch {
    return undefined;
  }
}

/** Handle the return from the sign-in page. Returns the path to go back to. */
export async function completeSignIn(search: string): Promise<string> {
  const query = new URLSearchParams(search);
  const flow = JSON.parse(storage()?.getItem(FLOW_KEY) ?? "null") as { verifier: string; state: string; returnTo: string } | null;
  storage()?.removeItem(FLOW_KEY);
  const back = flow?.returnTo || "/";
  if (query.get("error")) throw Object.assign(new Error(query.get("error_description") || query.get("error") || "Sign-in failed"), { back });
  if (!flow || query.get("state") !== flow.state) throw Object.assign(new Error("The sign-in could not be verified. Please try again."), { back });
  const code = query.get("code");
  if (!code) throw Object.assign(new Error("The sign-in returned no code"), { back });
  const cfg = await loginConfig();
  if (!cfg) throw Object.assign(new Error("Sign-in with buildingSMART is not configured on this server"), { back });
  const res = await fetch(`${cfg.authority}/oauth2/v2.0/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: cfg.client_id,
      code,
      redirect_uri: redirectUri(cfg),
      code_verifier: flow.verifier,
      scope: scopes(cfg),
    }),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || !json.access_token) throw Object.assign(new Error(json.error_description || json.error || `Sign-in failed (${res.status})`), { back });
  const token: StoredToken = {
    access_token: json.access_token,
    expires_at: Date.now() + Math.max(60, Number(json.expires_in) || 3600) * 1000 - 60_000,
    name: nameFromIdToken(json.id_token),
  };
  storage()?.setItem(TOKEN_KEY, JSON.stringify(token));
  return back;
}

/** Current sign-in, or null when not signed in / expired. */
export function currentSignIn(): StoredToken | null {
  try {
    const t = JSON.parse(storage()?.getItem(TOKEN_KEY) ?? "null") as StoredToken | null;
    if (!t || t.expires_at < Date.now()) return null;
    return t;
  } catch {
    return null;
  }
}

export function signOut(): void {
  storage()?.removeItem(TOKEN_KEY);
}

/** Reopen the download dialog after coming back from the sign-in (consumes the flag). */
export function takeReopenFlag(): boolean {
  const s = storage();
  if (!s?.getItem(REOPEN_KEY) || s.getItem(FLOW_KEY)) return false;
  s.removeItem(REOPEN_KEY);
  return true;
}
