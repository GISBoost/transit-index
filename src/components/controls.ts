/** SegmentedControl, SpeedLegend, SegmentPopup. Behaviour lives in src/client/*. */
import { esc, tr, type Ctx } from '../i18n';
import { fmt, getThresholds, icon, num } from '../lib/idx';
import type { SpeedClass } from '../lib/idx';
import { lineBadge, loader, quality } from './common';

export interface SegOption { v: string; label: string }
/** radiogroup of buttons; `data-seg` names the group for the client. Only the checked option is in the tab order. */
export function seg(label: string, name: string, options: SegOption[], value: string | null, small = false): string {
  const opts = options.map((o, i) => {
    const on = o.v === value;
    return `<button type="button" role="radio" aria-checked="${on}" tabindex="${on || (value == null && i === 0) ? 0 : -1}" class="idx-seg__opt" data-v="${o.v}">${o.label}</button>`;
  }).join('');
  return `<div><span class="idx-cap idx-seg-label" id="seg-${name}">${label}</span><div class="idx-seg${small ? ' idx-seg--sm' : ''}" role="radiogroup" aria-labelledby="seg-${name}" data-seg="${name}">${opts}</div></div>`;
}

/** SpeedLegend: 6 classes as 44 px buttons (hover/focus dims the rest, click pins) + the dashed "brak danych" entry. */
export function legend(ctx: Ctx, opts: { interactive?: boolean; title?: boolean } = {}): string {
  const t = tr(ctx), th = getThresholds();
  const cls = [1, 2, 3, 4, 5, 6].map((n) =>
    opts.interactive
      ? `<button type="button" class="idx-legend__cls" data-cls="${n}" aria-pressed="false" aria-label="${t('legend.class', { n })}"><span class="idx-s${n}"></span></button>`
      : `<span class="idx-s${n}" style="display: block; height: 10px; border-radius: var(--idx-radius-xs)"></span>`).join('');
  const ticks = th.map((v, i) => `<span class="idx-label" style="--p: ${((i + 1) * 100 / 6).toFixed(2)}">${v}</span>`).join('');
  return `<div class="idx-legend" role="group" aria-label="${t('legend.aria')}"><div class="idx-legend__ramp">${cls}</div><div class="idx-legend__ticks">${ticks}</div><div class="idx-legend__nd"><i></i><span class="idx-caption">${opts.title === false ? t('legend.nodata') : t('legend.nodata.km')}</span></div></div>`;
}

/** Human range of a speed class in km/h, from the token thresholds ("12–16", "poniżej 8", "od 26"). */
export function classRange(ctx: Ctx, c: SpeedClass): string {
  const t = tr(ctx), th = getThresholds(), f = (v: number) => fmt(v, 0, ctx.lang);
  if (c === 'nd') return '';
  if (c === 1) return t('range.below', { n: f(th[0]) });
  if (c === 6) return t('range.from', { n: f(th[4]) });
  return `${f(th[c - 2])}–${f(th[c - 1])}`;
}

export interface PopupData {
  route: string | null; from: string; to: string; measured: number | null; plan: number | null;
  p15: number | null; p85: number | null; n: number | null; percLabel: string;
}
/** SegmentPopup body (window on desktop, bottom sheet on phones). */
export function popup(ctx: Ctx, d: PopupData | 'loading'): string {
  const t = tr(ctx);
  const close = `<button class="idx-btn idx-btn--text idx-pop__close" type="button" aria-label="${t('pop.close')}" data-pop-close style="min-width: var(--idx-tap); padding: 0">${icon('close')}</button>`;
  if (d === 'loading') return `${close}<p class="idx-cap" style="margin: 0">${t('pop.title')}</p><div class="idx-row">${loader(t('pop.loading'))}</div><span class="idx-skel" style="height: 14px; width: 70%"></span><span class="idx-skel" style="height: 40px"></span>`;
  const route = `<div class="idx-row" style="gap: var(--idx-space-2)">${lineBadge(d.route)}${d.route ? `<span class="idx-board">${t('pop.line', { n: esc(d.route) })}</span>` : ''}</div>`;
  const path = `<div class="idx-pop__route"><div class="idx-pop__stop"><span class="idx-conn idx-conn--first"><i class="idx-node idx-node--sm idx-node--solid"></i></span><span class="idx-ui-strong">${esc(d.from)}</span></div><div class="idx-pop__stop"><span class="idx-conn idx-conn--last"><i class="idx-node idx-node--sm"></i></span><span class="idx-ui-strong">${esc(d.to)}</span></div></div>`;
  const unit = (v: number | null) => (v == null ? '—' : `${num(v, 1, ctx.lang)}<span class="idx-ui idx-mute" style="font-family: var(--font-sans); font-weight: 400"> ${t('unit.kmh')}</span>`);
  if (d.measured == null) {
    return `${close}<p class="idx-cap" style="margin: 0">${t('pop.title')}</p>${route}${path}<div class="idx-pop__grid"><div style="grid-column: 1 / -1" class="idx-state">${icon('info')}<div><p class="idx-ui-strong" style="color: var(--ink)">${t('pop.nodata.title')}</p><p class="idx-ui">${t('pop.nodata.text')}</p></div></div></div>${quality(ctx, 'out', t('q.nodata'))}`;
  }
  const range = d.p15 != null && d.p85 != null ? `${fmt(d.p15, 1, ctx.lang)} – ${fmt(d.p85, 1, ctx.lang)} ${t('unit.kmh')}` : '—';
  return `${close}<p class="idx-cap" style="margin: 0">${t('pop.title')}</p>${route}${path}<div class="idx-pop__grid">` +
    `<div><p class="idx-cap" style="margin: 0">${t('pop.measured', { perc: d.percLabel })}</p><p class="idx-figure-md">${unit(d.measured)}</p></div>` +
    `<div><p class="idx-cap" style="margin: 0">${t('pop.plan')}</p><p class="idx-figure-md">${unit(d.plan)}</p></div>` +
    `<div style="grid-column: 1 / -1"><p class="idx-cap" style="margin: 0">${t('pop.range')}</p><p class="idx-board">${range} · n = ${d.n ?? 'XX'}</p></div></div>` +
    `<div class="idx-row" style="gap: var(--idx-space-3)">${quality(ctx, 'ranked', t('q.enough'))}<span class="idx-ph">${t('ph')}</span></div>`;
}
