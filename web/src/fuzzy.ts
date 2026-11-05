/** Fuzzy matching like thefuzz (ratio / partial_ratio) used by the desktop search dialog. */
const UMLAUTS: Record<string, string> = { ä: "ae", ö: "oe", ü: "ue", ß: "ss" };

export function normalize(s: string): string {
  return s.toLowerCase().replace(/[äöüß]/g, (c) => UMLAUTS[c]);
}

function levenshtein(a: string, b: string): number {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    prev = cur;
  }
  return prev[b.length];
}

/** 0..100, similar to fuzz.ratio */
export function ratio(a: string, b: string): number {
  const total = a.length + b.length;
  if (!total) return 100;
  return Math.round(100 * (1 - levenshtein(a, b) / total) * 1) ;
}

/** 0..100, best ratio of the shorter string against substrings of the longer one */
export function partialRatio(a: string, b: string): number {
  const [s, l] = a.length <= b.length ? [a, b] : [b, a];
  if (!s.length) return 0;
  if (l.includes(s)) return 100;
  let best = 0;
  for (let i = 0; i <= l.length - s.length; i++) {
    best = Math.max(best, ratio(s, l.slice(i, i + s.length)));
    if (best === 100) break;
  }
  return best;
}

export function rowScore(query: string, cells: string[], strict: boolean): number {
  const q = normalize(query);
  let best = 0;
  cells.forEach((cell, i) => {
    const c = normalize(cell ?? "");
    let score: number;
    if (c === q) score = 1000;
    else score = (strict ? ratio(q, c) : partialRatio(q, c)) - 0.1 * i;
    best = Math.max(best, score);
  });
  return best;
}
