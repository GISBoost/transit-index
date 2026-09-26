import pl from './pl.json';
import en from './en.json';

export type Lang = 'pl' | 'en';
export const LANGS: Lang[] = ['pl', 'en'];
export interface Ctx { lang: Lang; base: string }

const DICT: Record<Lang, Record<string, string>> = { pl, en };

/** Dictionary lookup. A missing key throws: the build (and tools/check.mjs) fails instead of shipping a hole.
 *  Values are HTML: a literal `<` or `&` is written as `&lt;` / `&amp;` (tools/check.mjs enforces it). */
export function t(lang: Lang, key: string, vars?: Record<string, string | number>): string {
  const s = DICT[lang][key];
  if (s === undefined) throw new Error(`missing i18n key "${key}" for ${lang}`);
  const out = vars ? s.replace(/\{(\w+)\}/g, (_, k: string) => String(vars[k] ?? '')) : s;
  // Polish typography: a one-letter word (w, z, i, o, u, a) never ends a line
  return lang === 'pl' ? out.replace(/(^|\s)([aiouwzAIOUWZ])\s+(?=\S)/g, '$1$2\u00a0') : out;
}
export const tr = (ctx: Ctx) => (key: string, vars?: Record<string, string | number>): string => t(ctx.lang, key, vars);

/** Public URL of a route ("", "mapa", "miasto/lodz") in a language; PL is the root, EN lives under /en/. */
export function url(ctx: Ctx, route: string, lang: Lang = ctx.lang): string {
  return `${ctx.base}${lang === 'en' ? 'en/' : ''}${route ? `${route}/` : ''}`;
}

/** Split a pathname (already without the base) into language + route. */
export function parsePath(rest: string): { lang: Lang; route: string } {
  const parts = rest.split('/').filter(Boolean);
  const lang: Lang = parts[0] === 'en' ? 'en' : 'pl';
  if (parts[0] === 'en') parts.shift();
  return { lang, route: parts.join('/') };
}

const ESC: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
/** Escape data-derived strings (city names, stop names, file names) before they go into markup. */
export const esc = (s: string): string => s.replace(/[&<>"']/g, (c) => ESC[c]);
