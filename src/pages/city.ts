import { esc, tr, url, type Ctx } from '../i18n';
import { icon, num, speedClass } from '../lib/idx';
import { speedOf } from '../lib/agg';
import type { City, SegCollection } from '../lib/schema';
import { cityName, lineBadge, quality, sectionHead } from '../components/common';
import { legend } from '../components/controls';
import { cityCard, cityHero, hourlyCard, kpiTiles, linesTable, methodNote, networkSvg, rule } from '../components/sections';
import type { PageOut, Site } from './site';

/** Slowest segments in the peak (P50), only ones with a value. */
export function slowest(fc: SegCollection, peak: number[], n = 5) {
  return fc.features
    .map((f) => ({ p: f.properties, v: speedOf(f.properties, 'p50', { hour: null, period: 'peak' }, peak) }))
    .filter((x): x is { p: typeof x.p; v: number } => x.v != null)
    .sort((a, b) => a.v - b.v)
    .slice(0, n);
}

function slowList(ctx: Ctx, c: City, fc: SegCollection, peak: number[]): string {
  const t = tr(ctx), rows = slowest(fc, peak);
  if (!rows.length) return `<div class="idx-rank"><div class="idx-rank__state idx-state"><span class="idx-state__icon">${icon('info')}</span><div><p class="idx-ui-strong" style="color: var(--ink)">${t('city.slow.none')}</p></div></div></div>`;
  const list = rows.map((r, i) => {
    const k = Math.min(r.v / 30, 1).toFixed(3);
    return `<a class="idx-rrow idx-rrow--seg" style="--i: ${i}" href="${url(ctx, 'mapa')}?miasto=${c.slug}&amp;odcinek=${esc(r.p.id)}"><span class="idx-conn${i === 0 ? ' idx-conn--first' : ''}${i === rows.length - 1 ? ' idx-conn--last' : ''}"><i class="idx-node idx-node--sm${i === 0 ? ' idx-node--solid' : ''}"></i></span>` +
      `<span class="idx-rrow__rank idx-board">${i + 1}</span><span class="idx-rrow__name">${lineBadge(r.p.route)}<span class="idx-ui-strong">${esc(r.p.stop_from)} → ${esc(r.p.stop_to)}</span></span>` +
      `<span class="idx-bar"><span class="idx-bar__fill idx-s${speedClass(r.v)}" style="--k: ${k}"></span></span>` +
      `<span class="idx-rrow__val idx-figure-md">${num(r.v, 1, ctx.lang)}<small>${t('unit.kmh')}</small></span></a>`;
  }).join('');
  return `<div class="idx-rank" style="align-self: start"><div>${list}</div><p class="idx-rank__foot idx-caption">${t('city.slow.foot')}</p></div>`;
}

/** Static SVG network: what you see before MapLibre loads and without JS. Peak P50, all modes. */
function miniMap(ctx: Ctx, c: City, fc: SegCollection, peak: number[]): string {
  const t = tr(ctx);
  const cls = fc.features.map((f) => speedClass(speedOf(f.properties, 'p50', { hour: null, period: 'peak' }, peak)));
  return `<div class="idx-map idx-map--mini" data-minimap data-city="${c.slug}"><div class="idx-map__fallback">${networkSvg(fc, cls, t('city.slow.map'))}</div><div class="idx-map__canvas" data-map-canvas></div><p class="idx-caption idx-map__attr" data-attr>${t('map.attr')}</p></div>`;
}

export function cityPage(ctx: Ctx, site: Site, slug: string): PageOut {
  const t = tr(ctx), c = site.cities.find((x) => x.slug === slug);
  if (!c) throw new Error(`unknown city ${slug}`);
  const fc = site.segments.get(slug);
  if (!fc) throw new Error(`missing segments for ${slug}`);
  const name = cityName(ctx, c), peak = site.manifest.peak_hours;
  const qText = t(`city.quality.${c.quality}`);
  const others = site.cities.filter((x) => x.slug !== slug).sort((a, b) => (a.kpi.rank ?? 99) - (b.kpi.rank ?? 99)).slice(0, 3);
  const section = (inner: string, cls = '') => `<section class="idx-wrap idx-section idx-fade ${cls}">${inner}</section>`;
  const main =
    cityHero(ctx, c) + rule() +
    section(kpiTiles(ctx, c), 'idx-section--md') +
    section(sectionHead(t('city.profile.eyebrow'), t('city.profile.h2')) + `<div class="idx-block">${hourlyCard(ctx, c)}</div><div class="idx-block">${methodNote(ctx, 'short')}</div>`) +
    section(sectionHead(t('city.slow.eyebrow'), t('city.slow.h2')) +
      `<div class="idx-split idx-block">${miniMap(ctx, c, fc, peak)}${slowList(ctx, c, fc, peak)}</div><div class="idx-block idx-legend-wrap">${legend(ctx)}<p style="margin-top: var(--idx-space-3)"><a class="idx-btn idx-btn--text" href="${url(ctx, 'mapa')}?miasto=${c.slug}">${t('city.slow.open')} ${icon('arrow-right', 18)}</a></p></div>`) +
    section(sectionHead(t('city.lines.eyebrow'), t('city.lines.h2')) + `<div class="idx-block">${linesTable(ctx, c)}</div>`) +
    section(`<div class="idx-split idx-split--text"><div><p class="idx-eyebrow">${t('city.quality.eyebrow')}</p><h2 class="idx-display-lg idx-sechead" data-lines>${t('city.quality.h2')}</h2><div style="margin-top: var(--idx-space-5)">${quality(ctx, c.quality)}</div><p class="idx-body idx-mute idx-copy">${qText}</p></div>${methodNote(ctx, 'full', 'mtd')}</div>`) +
    section(`<h2 class="idx-display-md idx-sechead" data-lines>${t('city.others.h2')}</h2><div class="idx-cardgrid idx-block" data-stagger>${others.map((o) => cityCard(ctx, o)).join('')}</div>`);
  return {
    title: t('title.city', { name }), description: t('desc.city', { name }), page: 'city', current: '', section: true, main,
    data: { city: c.slug },
  };
}
