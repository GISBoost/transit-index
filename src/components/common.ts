/** Small markup builders for the design-system components. Markup is copied from design/components/<Name>/preview.html;
 *  every visible string comes from the i18n dictionary. */
import { esc, tr, type Ctx } from '../i18n';
import { icon } from '../lib/idx';
import type { City, Quality } from '../lib/schema';

/** dane zastępcze marker (.idx-ph) */
export const ph = (ctx: Ctx): string => `<span class="idx-ph">${tr(ctx)('ph')}</span>`;

/** QualityBadge: word + node shape + colour, never colour alone. */
export const quality = (ctx: Ctx, q: Quality, label?: string): string =>
  `<span class="idx-q idx-q--${q}"><i class="idx-node idx-node--sm"></i>${label ?? tr(ctx)(`q.${q}`)}</span>`;

/** LineBadge: only real route numbers; unknown = dashed XX. */
export const lineBadge = (route: string | null): string =>
  route ? `<span class="idx-badge">${esc(route)}</span>` : '<span class="idx-badge idx-badge--ph">XX</span>';

export const cityName = (ctx: Ctx, c: City): string => esc(ctx.lang === 'en' ? c.name_en : c.name);
export const cityRegion = (ctx: Ctx, c: City): string =>
  tr(ctx)('region', { region: esc(ctx.lang === 'en' ? c.region_en : c.region) });

/** Eyebrow + display heading pair used by every section (the heading enters line by line, see motion.ts). */
export const sectionHead = (eyebrow: string, title: string, level: 'h2' | 'h3' = 'h2', id = ''): string =>
  `<p class="idx-eyebrow">${eyebrow}</p><${level} class="idx-display-lg idx-sechead" data-lines${id ? ` id="${id}"` : ''}>${title}</${level}>`;

/** Loader: line with four nodes, lights up in turn. Static line + one solid node under reduced motion. */
export const loader = (label: string, small = false): string =>
  `<span class="idx-loader${small ? ' idx-loader--sm' : ''}" role="status" aria-label="${label}"><i class="idx-node"></i><i class="idx-node"></i><i class="idx-node"></i><i class="idx-node"></i></span>`;

/** Error / empty state block: icon + word, never colour alone (errors have no colour of their own). */
export const state = (kind: 'info' | 'error', title: string, text: string, action = ''): string =>
  `<div class="idx-state${kind === 'error' ? ' idx-state--error' : ''}">${icon(kind === 'error' ? 'warning' : 'info')}<div><p class="idx-ui-strong"${kind === 'info' ? ' style="color:var(--ink)"' : ''}>${title}</p><p class="idx-ui${kind === 'error' ? ' idx-mute' : ''}">${text}</p>${action}</div></div>`;

export const retryButton = (ctx: Ctx, attr = 'data-retry'): string =>
  `<button class="idx-btn idx-btn--secondary" type="button" ${attr}>${tr(ctx)('state.retry')}</button>`;

/** Number-or-XX helper: unknown sample sizes are XX until the method fixes the thresholds. */
export const orXX = (v: number | null): string => (v == null ? 'XX' : String(v));
