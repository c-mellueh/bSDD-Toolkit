/** Access tokens per link id (edit or read-only), kept in this browser only. */
const key = (ident: string) => `bsdd-token-${ident}`;

export function getToken(ident: string | null | undefined): string | null {
  if (!ident) return null;
  try {
    return localStorage.getItem(key(ident));
  } catch {
    return null;
  }
}

export function setToken(ident: string, token: string | null) {
  try {
    if (token) localStorage.setItem(key(ident), token);
    else localStorage.removeItem(key(ident));
  } catch {
    /* private mode: the password has to be entered again next time */
  }
}

/** Header carrying the token for requests to /api/projects/<ident>/... */
export function tokenHeaders(path: string): Record<string, string> {
  const m = /^\/api\/projects\/([^/?#]+)/.exec(path);
  const token = m ? getToken(m[1]) : null;
  return token ? { "X-Project-Token": token } : {};
}
