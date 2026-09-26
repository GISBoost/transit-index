/** Data components: ranking, hero + KPI, city card, download card, method note, tables, network schematic. */
import { esc, tr, url, type Ctx } from '../i18n';
import { digits, fmt, hourlyChart, icon, num, signed, speedClass } from '../lib/idx';
import { KMH_AXIS_MAX, PERIOD_KEYS, MODE_KEYS, bounds, type RankItem } from '../lib/agg';
import { MODES, PERIODS, type City, type DataFile, type Mode, type Period, type SegCollection } from '../lib/schema';
import { cityName, cityRegion, lineBadge, loader, orXX, ph, quality } from './common';
import { seg } from './controls';

/* ---------- section scaffolding ---------- */
export const rule = (): string => '<div class="idx-wrap"><div class="idx-rule" aria-hidden="true"><i class="idx-node idx-node--solid"></i><i class="idx-node"></i></div></div>';

export const hero = (eyebrow: string, title: string, lead = '', extra = ''): string =>
  `<section class="idx-wrap idx-hero" aria-labelledby="h1"><p class="idx-eyebrow">${eyebrow}</p><h1 class="idx-display-xl idx-hero__title" id="h1" data-lines>${title}</h1>${lead ? `<p class="idx-lead idx-read">${lead}</p>` : ''}${extra}</section>`;

/** Two definitions with nodes: solid = measured, hollow = planned. Always in full wording on first use. */
export function definitions(ctx: Ctx): string {
  const t = tr(ctx);
  return `<dl class="idx-hero__defs"><div class="idx-method__item"><i class="idx-node idx-node--solid"></i><div><dt class="idx-body-strong">${t('measured.full.cap')}</dt><dd class="idx-ui idx-mute">${t('def.measured')}</dd></div></div>` +
    `<div class="idx-method__item"><i class="idx-node"></i><div><dt class="idx-body-strong">${t('plan.cap')}</dt><dd class="idx-ui idx-mute">${t('def.plan')}</dd></div></div></dl>`;
}

/* ---------- ranking ---------- */
export function rankRow(ctx: Ctx, it: RankItem, name: string, i: number, n: number): string {
  const t = tr(ctx), out = it.kmh == null;
  const conn = `idx-conn${i === 0 ? ' idx-conn--first' : ''}${i === n - 1 ? ' idx-conn--last' : ''}`;
  const k = out ? 0 : Math.min((it.kmh as number) / KMH_AXIS_MAX, 1);
  const bar = out
    ? `<span class="idx-bar idx-bar--nd idx-hatch" aria-label="${t('legend.nodata')}"></span>`
    : `<span class="idx-bar"><span class="idx-bar__fill idx-s${speedClass(it.kmh)}" style="--k: ${k.toFixed(3)}"></span></span>`;
  return `<a class="idx-rrow${out ? ' idx-rrow--out' : ''}" href="${url(ctx, `miasto/${it.slug}`)}" data-key="${it.slug}" style="--i: ${i}">` +
    `<span class="${conn}"><i class="idx-node idx-node--sm${i === 0 ? ' idx-node--solid' : ''}"></i></span>` +
    `<span class="idx-rrow__rank idx-board">${out ? '–' : it.pos}</span>` +
    `<span class="idx-rrow__name"><span class="idx-rrow__city">${name}</span>${quality(ctx, it.quality)}</span>${bar}` +
    `<span class="idx-rrow__val idx-figure-md">${out ? '—' : num(it.kmh as number, 1, ctx.lang)}<small>${t('unit.kmh')}</small></span></a>`;
}

export const rankRows = (ctx: Ctx, items: RankItem[], cities: City[]): string => {
  const byName = new Map(cities.map((c) => [c.slug, cityName(ctx, c)]));
  return items.map((it, i) => rankRow(ctx, it, byName.get(it.slug) ?? esc(it.slug), i, items.length)).join('');
};

export const rankSkeleton = (ctx: Ctx, n = 4): string =>
  `<div aria-busy="true"><div class="idx-rank__loading">${loader(tr(ctx)('rank.loading'))}</div>` +
  Array.from({ length: n }, (_, i) => `<div class="idx-rrow" aria-hidden="true"><span class="idx-conn${i === 0 ? ' idx-conn--first' : ''}${i === n - 1 ? ' idx-conn--last' : ''}"><i class="idx-node idx-node--sm"></i></span><span class="idx-skel" style="height: 12px; width: 24px; grid-area: rank"></span><span class="idx-skel" style="height: 16px; width: 60%; grid-area: name"></span><span class="idx-skel" style="height: 6px; grid-area: bar"></span><span class="idx-skel" style="height: 20px; width: 64px; justify-self: end; grid-area: val"></span></div>`).join('') + '</div>';

export const rankEmpty = (ctx: Ctx): string => {
  const t = tr(ctx);
  return `<div class="idx-rank__state idx-state"><span class="idx-state__icon">${icon('info')}</span><div><p class="idx-ui-strong" style="color: var(--ink)">${t('rank.empty.title')}</p><p class="idx-ui">${t('rank.empty.text')}</p></div></div>`;
};
export const rankError = (ctx: Ctx): string => {
  const t = tr(ctx);
  return `<div class="idx-rank__state idx-state idx-state--error" role="alert"><span class="idx-state__icon">${icon('warning')}</span><div><p class="idx-ui-strong">${t('rank.err.title')}</p><p class="idx-ui idx-mute" style="margin: var(--idx-space-1) 0 var(--idx-space-4)">${t('rank.err.text')}</p><button class="idx-btn idx-btn--secondary" type="button" data-retry>${t('state.retry')}</button></div></div>`;
};

export function rankCard(ctx: Ctx, mode: Mode, period: Period, body: string): string {
  const t = tr(ctx);
  const head = seg(t('seg.mode'), 'mode', MODES.map((m) => ({ v: m, label: t(MODE_KEYS[m]) })), mode) +
    seg(t('seg.period'), 'period', PERIODS.map((p) => ({ v: p, label: t(PERIOD_KEYS[p]) })), period);
  return `<div class="idx-rank" data-ranking><div class="idx-rank__head">${head}</div><div data-rank-body>${body}</div>` +
    `<p class="idx-rank__foot idx-caption">${t('rank.foot')} <a href="${url(ctx, 'metodyka')}">${t('mn.link')}</a></p></div>` +
    `<p class="idx-sr" role="status" aria-live="polite" data-live></p>`;
}

/* ---------- city hero + KPI ---------- */
export function cityHero(ctx: Ctx, c: City): string {
  const t = tr(ctx), k = c.kpi, name = cityName(ctx, c);
  const title = ctx.lang === 'pl'
    ? (c.name_loc ? t('city.h1', { loc: esc(c.name_loc) }) : t('city.h1.plain', { name }))
    : t('city.h1', { loc: name });
  const has = k.measured != null;
  const fig = has
    ? `<span class="idx-figure-xl" role="text">${digits(fmt(k.measured as number, 1, ctx.lang))}</span><span class="idx-hero__unit">${t('unit.kmh')}</span>`
    : `<span class="idx-figure-xl idx-mute" aria-label="${t('nodata.value')}">—</span><span class="idx-hero__unit">${t('unit.kmh')}</span>`;
  const badge = c.quality === 'out'
    ? `${quality(ctx, 'out')}<span class="idx-caption idx-mute">${t('nodata.n')}</span>`
    : quality(ctx, c.quality, k.rank != null ? `${t(`q.${c.quality}`)} · ${t('city.rank', { n: k.rank })}` : undefined);
  return `<section class="idx-wrap idx-hero idx-cityhero" aria-labelledby="h1">` +
    `<p class="idx-eyebrow idx-cityhero__eyebrow">${t('city.eyebrow', { name })}</p>` +
    `<h1 class="idx-display-xl idx-hero__title idx-cityhero__title" id="h1" data-lines>${title}</h1>` +
    `<div class="idx-cityhero__fig"><div class="idx-cityhero__num">${fig}</div><div class="idx-row">${badge}${ph(ctx)}</div></div>` +
    `<p class="idx-lead idx-cityhero__lead">${t('lead.recon')}</p>` +
    `<div class="idx-cityhero__defs">${definitions(ctx)}</div></section>`;
}

export function kpiTile(ctx: Ctx, label: string, value: number | null, note: string, tone: 'slow' | 'fast' | null = null, signedValue = false): string {
  const t = tr(ctx);
  const fig = value == null
    ? `<span class="idx-figure-lg idx-mute">—</span>`
    : `<span class="idx-figure-lg">${signedValue && value > 0 ? '+' : ''}${num(value, 1, ctx.lang)}</span><span class="idx-kpi__unit idx-ui">${t('unit.kmh')}</span>`;
  const noteHtml = tone
    ? `<span class="idx-delta" style="color: var(${tone === 'slow' ? '--amber-ink' : '--accent-ink'})"><span style="display: inline-flex; transform: rotate(${tone === 'slow' ? 45 : -45}deg)">${icon('arrow-right', 16)}</span>${note}</span>`
    : note;
  return `<article class="idx-card idx-kpi"><p class="idx-cap" style="margin: 0">${label}</p><p class="idx-kpi__fig">${fig}</p><p class="idx-kpi__note idx-caption">${noteHtml}</p></article>`;
}

export function kpiTiles(ctx: Ctx, c: City): string {
  const t = tr(ctx), { measured: m, plan: p, n } = c.kpi;
  const diff = m != null && p != null ? m - p : null;
  const dNote = diff == null ? t('nodata.short.cap') : Math.abs(diff) < 0.05 ? t('kpi.diff.same') : t(diff < 0 ? 'kpi.diff.slower' : 'kpi.diff.faster');
  return `<div class="idx-cardgrid" data-stagger>` +
    kpiTile(ctx, t('measured.cap'), m, m == null ? t('nodata.n') : t('kpi.measured.note', { n: orXX(n) })) +
    kpiTile(ctx, t('plan.cap'), p, t('kpi.plan.note')) +
    kpiTile(ctx, t('kpi.diff'), diff, dNote, diff == null || Math.abs(diff) < 0.05 ? null : diff < 0 ? 'slow' : 'fast', true) + `</div>`;
}

/* ---------- hourly profile card (chart + table version) ---------- */
export function hourlyCard(ctx: Ctx, c: City): string {
  const t = tr(ctx), h = c.hourly;
  const empty = h.meas.every((v) => v == null);
  const cap = `<figcaption class="idx-display-sm idx-chart__cap">${t('chart.title')}<span class="idx-chart__sub">${t('chart.sub')} · ${t('ph')}</span></figcaption>`;
  if (empty) return `<figure class="idx-card idx-chart">${cap}<div class="idx-hatch idx-chart__none"><span class="idx-ui idx-mute">${t('chart.empty')}</span></div></figure>`;
  const ymax = Math.max(30, Math.ceil(Math.max(...h.plan.concat(h.meas).filter((v): v is number => v != null)) / 10) * 10);
  const labels = { title: t('chart.svg.title'), desc: t('chart.svg.desc'), nodata: t('nodata.short'), plan: t('plan'), meas: t('measured') };
  // one chart per container width (see .idx-chart__v in site.css); only the visible one is exposed and animated
  const svg = (['sm', 'md', 'lg'] as const).map((size) => `<div class="idx-chart__v idx-chart__v--${size}">${hourlyChart({ plan: h.plan, meas: h.meas, ymax, size, labels })}</div>`).join('');
  const rows = h.plan.map((p, i) => `<tr><td class="is-num">${i}:00</td><td class="is-num">${p == null ? '—' : fmt(p, 1, ctx.lang)}</td><td class="is-num">${h.meas[i] == null ? t('nodata.short') : fmt(h.meas[i] as number, 1, ctx.lang)}</td></tr>`).join('');
  return `<figure class="idx-card idx-chart" data-chart>${cap}${svg}<p class="idx-caption idx-mute idx-chart__foot">${t('chart.foot')}</p>` +
    `<details class="idx-details"><summary class="idx-ui-strong">${icon('table', 18)}${t('chart.table')}</summary><div class="idx-table-scroll"><table class="idx-table"><caption class="idx-sr">${t('chart.svg.title')}</caption><thead><tr><th scope="col">${t('col.hour')}</th><th scope="col" class="is-num">${t('col.plan')}</th><th scope="col" class="is-num">${t('col.measured')}</th></tr></thead><tbody>${rows}</tbody></table></div></details></figure>`;
}

/* ---------- lines table ---------- */
export function linesTable(ctx: Ctx, c: City): string {
  const t = tr(ctx);
  if (!c.lines.length) return `<div class="idx-rank"><div class="idx-rank__state idx-state"><span class="idx-state__icon">${icon('info')}</span><div><p class="idx-ui-strong" style="color: var(--ink)">${t('city.lines.none')}</p></div></div></div>`;
  const rows = c.lines.map((l) => {
    const d = l.measured != null && l.plan != null ? l.measured - l.plan : null;
    return `<tr><td>${lineBadge(l.route)}${l.route ? `<span class="idx-sr"> ${t('pop.line', { n: esc(l.route) })}</span>` : ''}</td>` +
      `<td class="is-num">${l.measured == null ? `<span class="idx-mute">${t('nodata.short')}</span>` : fmt(l.measured, 1, ctx.lang)}</td>` +
      `<td class="is-num">${l.plan == null ? '—' : fmt(l.plan, 1, ctx.lang)}</td>` +
      `<td class="is-num">${d == null ? '<span class="idx-mute">—</span>' : signed(d, 1, ctx.lang)}</td><td class="is-num">${orXX(l.n)}</td></tr>`;
  }).join('');
  return `<div class="idx-rank"><div class="idx-table-scroll"><table class="idx-table"><caption>${t('city.lines.caption')}</caption><thead><tr><th scope="col">${t('col.line')}</th><th scope="col" class="is-num">${t('col.measured.kmh')}</th><th scope="col" class="is-num">${t('col.plan.kmh')}</th><th scope="col" class="is-num">${t('kpi.diff')}</th><th scope="col" class="is-num">n</th></tr></thead><tbody>${rows}</tbody></table></div></div>`;
}

/* ---------- cards ---------- */
export function cityCard(ctx: Ctx, c: City): string {
  const t = tr(ctx), v = c.kpi.measured;
  return `<article class="idx-card idx-city"><div class="idx-city__top"><div><h3 class="idx-display-sm"><a class="idx-stretch" href="${url(ctx, `miasto/${c.slug}`)}">${cityName(ctx, c)}</a></h3><p class="idx-caption idx-mute">${cityRegion(ctx, c)}</p></div>${quality(ctx, c.quality)}</div>` +
    `<p class="idx-kpi__fig"><span class="idx-figure-lg">${v == null ? '—' : num(v, 1, ctx.lang)}</span><span class="idx-kpi__unit idx-ui">${t('unit.kmh')}</span></p>` +
    `<div class="idx-city__foot"><span class="idx-caption idx-mute">${t('city.card.foot', { n: orXX(c.kpi.n) })}</span><span class="idx-ui-strong" style="color: var(--accent-ink); display: inline-flex; gap: var(--idx-space-1); align-items: center">${t('city.card.see')} ${icon('arrow-right', 18)}</span></div></article>`;
}

export function downloadCard(ctx: Ctx, f: DataFile, edition: string): string {
  const t = tr(ctx), ok = f.url != null;
  const btn = ok
    ? `<a class="idx-btn idx-btn--primary" href="${esc(f.url as string)}" download>${icon('download', 18)}${t('dl.button')}</a>`
    : `<button class="idx-btn idx-btn--primary" type="button" disabled>${t('dl.na')}</button>`;
  return `<article class="idx-card idx-dl"><div><p class="idx-cap" style="margin: 0 0 var(--idx-space-2)">${t('dl.edition', { e: esc(edition) })}</p><h2 class="idx-display-sm">${t(`dl.title.${f.id}`)}</h2><p class="idx-ui idx-mute" style="margin-top: var(--idx-space-2)">${t(`dl.desc.${f.id}`)}</p></div>` +
    `<p class="idx-dl__name">${esc(f.name)}</p><div class="idx-dl__tags"><span class="idx-tag">${esc(f.format)}</span><span class="idx-tag">${esc(f.encoding)}</span><span class="idx-tag">${t('dl.license', { l: esc(f.license ?? 'XX') })}</span></div>` +
    `${ok ? '' : `<p class="idx-caption idx-mute">${t('dl.na.reason')}</p>`}<div class="idx-dl__foot">${btn}<span class="idx-label idx-mute">${f.size_mb == null ? 'XX MB' : `${fmt(f.size_mb, 1, ctx.lang)} MB`}</span></div></article>`;
}

/** MethodNote: full, or the short variant under a chart. */
export function methodNote(ctx: Ctx, variant: 'full' | 'short' = 'full', id = 'mt'): string {
  const t = tr(ctx);
  if (variant === 'short') return `<aside class="idx-method"><p class="idx-caption"><span class="idx-ui-strong" style="color: var(--ink)">${t('measured.cap')}</span> ${t('mn.short.a')} <span class="idx-ui-strong" style="color: var(--ink)">${t('plan.cap')}</span> ${t('mn.short.b')} <a href="${url(ctx, 'metodyka')}">${t('nav.method')}</a></p></aside>`;
  const item = (warn: boolean, title: string, text: string) => `<div class="idx-method__item"><i class="idx-node idx-node--sm ${warn ? 'idx-node--warn' : 'idx-node--solid'}"></i><div><dt class="idx-body-strong">${title}</dt><dd class="idx-ui">${text}</dd></div></div>`;
  return `<aside class="idx-method" aria-labelledby="${id}"><p class="idx-cap" style="margin: 0">${t('mn.eyebrow')}</p><h2 id="${id}" class="idx-display-sm" style="margin-top: var(--idx-space-2)">${t('mn.h')}</h2><p class="idx-body" style="margin-top: var(--idx-space-3)">${t('mn.p')}</p>` +
    `<dl class="idx-method__list">${item(false, t('mn.i1.t'), t('mn.i1.d'))}${item(true, t('mn.i2.t'), t('mn.i2.d'))}${item(true, t('mn.i2.t'), t('mn.i3.d'))}</dl>` +
    `<p class="idx-caption idx-mute" style="margin-top: var(--idx-space-4)"><a href="${url(ctx, 'metodyka')}">${t('mn.link')} ${icon('arrow-right', 16)}</a></p></aside>`;
}

/* ---------- network schematic (SVG): map fallback, no-JS view and the scrollytelling stage ---------- */
export function networkSvg(fc: SegCollection, classes: (number | 'nd')[], label: string): string {
  const W = 640, H = 400, pad = 28, b = bounds(fc);
  const kx = Math.cos(((b.minY + b.maxY) / 2) * Math.PI / 180);
  const dx = (b.maxX - b.minX) * kx, dy = b.maxY - b.minY, sc = Math.min((W - 2 * pad) / dx, (H - 2 * pad) / dy);
  const px = (lon: number) => ((W - dx * sc) / 2 + (lon - b.minX) * kx * sc).toFixed(1);
  const py = (lat: number) => ((H - dy * sc) / 2 + (b.maxY - lat) * sc).toFixed(1);
  const stops = new Set<string>();
  let paths = '';
  fc.features.forEach((f, i) => {
    const c = classes[i];
    paths += `<path class="m-seg ${c === 'nd' ? 'nd' : `k${c}`}" data-cls="${c}" d="${f.geometry.coordinates.map(([x, y], j) => `${j ? 'L' : 'M'}${px(x)} ${py(y)}`).join('')}"/>`;
    for (const [x, y] of f.geometry.coordinates) stops.add(`${px(x)} ${py(y)}`);
  });
  const dots = [...stops].filter((_, i) => i % 2 === 0).map((s) => { const [x, y] = s.split(' '); return `<circle class="m-stop" cx="${x}" cy="${y}" r="2.6"/>`; }).join('');
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${label}" preserveAspectRatio="xMidYMid slice"><rect class="m-land" width="${W}" height="${H}"/>${paths}${dots}</svg>`;
}

