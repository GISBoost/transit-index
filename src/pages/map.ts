import { esc, tr } from '../i18n';
import { DEFAULT_CITY, MODE_KEYS, PERIOD_KEYS, speedOf } from '../lib/agg';
import { icon, speedClass } from '../lib/idx';
import { MODES, PERIODS } from '../lib/schema';
import { cityName, loader } from '../components/common';
import { legend, seg } from '../components/controls';
import { mapTable } from '../components/maptable';
import type { PageFn } from './site';

/** `/mapa/` : panel + MapLibre canvas (client) + table view. The table of the default view is prerendered, so it exists without JS. */
export const mapPage: PageFn = (ctx, site) => {
  const t = tr(ctx);
  const city = site.cities.find((c) => c.slug === DEFAULT_CITY) ?? site.cities[0];
  const fc = site.segments.get(city.slug);
  if (!fc) throw new Error(`missing segments for ${city.slug}`);
  const peak = site.manifest.peak_hours;
  const rows = fc.features.filter((f) => f.properties.mode === 'tram')
    .map((f) => { const v = speedOf(f.properties, 'p50', { hour: null, period: 'day' }, peak); return { id: f.properties.id, route: f.properties.route, from: f.properties.stop_from, to: f.properties.stop_to, v, cls: speedClass(v) }; })
    .sort((a, b) => (a.v ?? Infinity) - (b.v ?? Infinity));
  const options = site.cities.map((c) => `<option value="${c.slug}"${c.slug === city.slug ? ' selected' : ''}>${cityName(ctx, c)}</option>`).join('');
  const panel = `<aside class="idx-mapshell__panel idx-mapctl" aria-label="${t('map.aria.filters')}" data-panel>` +
    `<div class="idx-mapctl__head"><div><p class="idx-eyebrow" style="margin: 0" data-city-eyebrow>${cityName(ctx, city)}</p><h1 class="idx-display-md" style="margin: var(--idx-space-2) 0 0" data-lines>${t('map.h1')}</h1><p class="idx-caption idx-mute" style="margin: var(--idx-space-2) 0 0">${t('map.sub')} <span class="idx-ph">${t('ph')}</span></p></div>` +
    `<button class="idx-btn idx-btn--text idx-mapctl__close" type="button" aria-label="${t('map.filters.close')}" data-filters-close>${icon('close')}</button></div>` +
    `<div><label class="idx-cap idx-seg-label" for="map-city">${t('map.city')}</label><select id="map-city" class="idx-select" data-city-select>${options}</select></div>` +
    seg(t('seg.mode'), 'mode', MODES.map((m) => ({ v: m, label: t(MODE_KEYS[m]) })), 'tram') +
    seg(t('seg.period'), 'period', PERIODS.map((p) => ({ v: p, label: t(PERIOD_KEYS[p]) })), 'day') +
    `<div><label class="idx-cap idx-seg-label" for="map-hour">${t('map.hour')}: <span id="map-hour-v" class="idx-board" style="text-transform: none; letter-spacing: 0" data-hour-label>${t('map.hour.all')}</span></label><input id="map-hour" class="idx-range" type="range" min="0" max="23" value="8" aria-describedby="map-hour-ticks" data-hour><div class="idx-range__ticks idx-label" id="map-hour-ticks" aria-hidden="true"><span>0</span><span>6</span><span>12</span><span>18</span><span>23</span></div></div>` +
    seg(t('seg.perc'), 'perc', [{ v: 'p15', label: 'P15' }, { v: 'p50', label: 'P50' }, { v: 'p85', label: 'P85' }], 'p50', true) +
    `<p class="idx-caption idx-mute" style="margin-top: calc(var(--idx-space-3) * -1)">${t('map.perc.hint')}</p>` +
    legend(ctx, { interactive: true }) +
    `<button type="button" class="idx-btn idx-btn--secondary" aria-pressed="false" style="justify-self: start" data-table-toggle>${icon('table', 18)}<span data-table-label>${t('map.view.table')}</span></button></aside>`;
  const view = `<div class="idx-mapview">` +
    `<div class="idx-map idx-map--full" data-mapbox tabindex="0" role="application" aria-label="${t('map.aria')}"><div class="idx-map__canvas" data-map-canvas></div>` +
    `<div class="idx-map__over" data-over><div>${loader(t('state.loading'))}<p class="idx-ui idx-mute" style="margin-top: var(--idx-space-3)">${t('map.loading')}</p></div></div>` +
    `<button type="button" class="idx-btn idx-btn--secondary idx-map__filters" data-filters-open aria-label="${t('map.filters')}">${icon('sliders')}${t('map.filters')}</button>` +
    `<div class="idx-pop idx-map__pop" data-popup hidden role="dialog" aria-label="${t('pop.label')}" tabindex="-1"></div>` +
    `<p class="idx-caption idx-map__attr" data-attr>${t('map.attr')}</p></div>` +
    `<div class="idx-rank idx-mapview__table" data-table hidden>${mapTable(ctx, rows)}</div>` +
    `<noscript><style>[data-table]{display:block!important}[data-mapbox],[data-panel]{display:none!important}.idx-mapshell--page{display:block!important;height:auto!important}</style></noscript>` +
    `<p class="idx-sr" role="status" aria-live="polite" data-live></p></div>`;
  return {
    title: t('title.map'), description: t('desc.map'), page: 'map', current: 'mapa', frameClass: 'idx-pv--map',
    main: `<div class="idx-mapshell idx-mapshell--page" data-city="${esc(city.slug)}">${panel}${view}</div>`,
    data: { city: city.slug },
  };
};
