/** /mapa/ : filters -> MapLibre layer + table view, popup / bottom sheet, keyboard on the map, state in the URL. */
import { esc, tr, type Ctx } from '../i18n';
import { loadCities, loadManifest, loadSegments } from '../lib/data';
import { icon, readThresholds, speedClass } from '../lib/idx';
import { DEFAULT_CITY, speedOf, type Perc } from '../lib/agg';
import { readMap, writeMap, type MapState } from '../lib/params';
import type { City, Manifest, SegCollection } from '../lib/schema';
import { loader } from '../components/common';
import { popup, type PopupData } from '../components/controls';
import { classLabel, mapTable, type TableRow } from '../components/maptable';
import { enter, reduced } from '../motion';
import type { SpeedMap } from '../map/speedmap';
import { bindSeg } from './controls';

export function initMap(ctx: Ctx): void {
  const $ = <T extends HTMLElement>(sel: string): T => document.querySelector<T>(sel) as T;
  const shell = $('.idx-mapshell--page'), panel = $('[data-panel]'), box = $('[data-mapbox]'), canvas = $('[data-map-canvas]');
  const over = $('[data-over]'), pop = $('[data-popup]'), tableEl = $('[data-table]'), live = $('[data-live]');
  const hourIn = $<HTMLInputElement>('[data-hour]'), hourLabel = $('[data-hour-label]'), tableBtn = $<HTMLButtonElement>('[data-table-toggle]');
  const citySel = $<HTMLSelectElement>('[data-city-select]');
  const t = tr(ctx);
  readThresholds();

  const q = readMap(new URLSearchParams(location.search));
  const defaultCity = shell.dataset.city ?? DEFAULT_CITY;
  let state: MapState = { ...q, city: q.city ?? defaultCity };
  let cities: City[] = [], manifest: Manifest | null = null, fc: SegCollection | null = null, city: City | null = null;
  let map: SpeedMap | null = null, order: string[] = [], cur = -1, hoverCls: number | null = null, token = 0;
  let selectedId: string | null = null;

  const mobile = matchMedia('(max-width: 1023px)');
  const say = (s: string): void => { live.textContent = ''; window.setTimeout(() => { live.textContent = s; }, 30); };
  const sync = (): void => {
    const s = writeMap(state, defaultCity);
    history.replaceState(null, '', `${location.pathname}${s ? `?${s}` : ''}${location.hash}`);
  };
  const view = () => ({ mode: state.mode, perc: state.perc, sel: { hour: state.hour, period: state.period } });
  const peak = (): number[] => manifest?.peak_hours ?? [];

  /* ---------- controls ---------- */
  const segs = new Map<string, ReturnType<typeof bindSeg>>();
  panel.querySelectorAll<HTMLElement>('[data-seg]').forEach((g) => {
    const name = g.dataset.seg as string;
    segs.set(name, bindSeg(g, (v) => {
      if (name === 'mode') state.mode = v as MapState['mode'];
      else if (name === 'period') { state.period = v as MapState['period']; state.hour = null; }
      else state.perc = v as Perc;
      applyView(true);
    }));
  });
  const showHour = (): void => {
    hourLabel.textContent = state.hour == null ? t('map.hour.all') : `${state.hour}:00–${state.hour + 1}:00`;
    if (state.hour != null) segs.get('period')?.clear(); else segs.get('period')?.set(state.period);
  };
  hourIn.addEventListener('input', () => { state.hour = Number(hourIn.value); showHour(); applyView(false); });
  citySel.addEventListener('change', () => { state.city = citySel.value; state.segment = null; closePopup(false); void loadCity(); });

  const legendBtns = [...panel.querySelectorAll<HTMLButtonElement>('.idx-legend__cls')];
  const refreshLegend = (): void => {
    const f = hoverCls ?? state.cls;
    legendBtns.forEach((b) => { b.classList.toggle('is-dim', f != null && Number(b.dataset.cls) !== f); b.setAttribute('aria-pressed', String(state.cls === Number(b.dataset.cls))); });
  };
  legendBtns.forEach((b) => {
    const n = Number(b.dataset.cls);
    ['pointerenter', 'focus'].forEach((ev) => b.addEventListener(ev, () => { hoverCls = n; map?.dim(n); refreshLegend(); }));
    ['pointerleave', 'blur'].forEach((ev) => b.addEventListener(ev, () => { hoverCls = null; map?.dim(null); refreshLegend(); }));
    b.addEventListener('click', () => {
      state.cls = state.cls === n ? null : n;
      map?.pin(state.cls); refreshLegend(); renderTable(); sync();
      say(state.cls == null ? '' : t('map.pinned', { n: state.cls }));
    });
  });

  /* ---------- table view (always available; independent of the map) ---------- */
  function rows(): TableRow[] {
    if (!fc) return [];
    return fc.features.filter((f) => f.properties.mode === state.mode).map((f) => {
      const v = speedOf(f.properties, state.perc, { hour: state.hour, period: state.period }, peak());
      return { id: f.properties.id, route: f.properties.route, from: f.properties.stop_from, to: f.properties.stop_to, v, cls: speedClass(v) };
    });
  }
  function renderTable(): void {
    const all = rows();
    order = all.map((r) => r.id);
    const shown = all.filter((r) => state.cls == null || r.cls === state.cls).sort((a, b) => (a.v ?? Infinity) - (b.v ?? Infinity));
    tableEl.innerHTML = mapTable(ctx, shown);
    tableEl.querySelectorAll<HTMLElement>('tbody tr').forEach((tr2) => { tr2.tabIndex = -1; });
  }
  tableBtn.addEventListener('click', () => { setTable(!state.table); sync(); });
  function setTable(on: boolean): void {
    state.table = on;
    box.hidden = on; tableEl.hidden = !on;
    tableBtn.setAttribute('aria-pressed', String(on));
    const label = tableBtn.querySelector<HTMLElement>('[data-table-label]');
    if (label) label.textContent = on ? t('map.view.map') : t('map.view.table');
    const ico = tableBtn.querySelector('svg');
    if (ico) ico.outerHTML = icon(on ? 'map' : 'table', 18);
    if (!on) window.setTimeout(() => window.dispatchEvent(new Event('resize')), 0);
  }

  /* ---------- popup / bottom sheet ---------- */
  function popupData(id: string): PopupData | null {
    const f = fc?.features.find((x) => x.properties.id === id);
    if (!f) return null;
    const p = f.properties, sel = { hour: state.hour, period: state.period };
    return {
      route: p.route, from: p.stop_from, to: p.stop_to, measured: speedOf(p, state.perc, sel, peak()), plan: p.plan_kmh,
      p15: speedOf(p, 'p15', sel, peak()), p85: speedOf(p, 'p85', sel, peak()), n: p.n, percLabel: state.perc.toUpperCase(),
    };
  }
  function openPopup(id: string, focus = true): void {
    const d = popupData(id);
    if (!d) return;
    selectedId = id; state.segment = id;
    pop.innerHTML = popup(ctx, d);
    // desktop window: on the side of the map away from the segment, so the segment stays visible
    const px = map?.pixelOf(id);
    pop.classList.toggle('is-left', !!px && px[0] > box.clientWidth / 2);
    pop.hidden = false;
    enter(pop, mobile.matches ? 40 : 8);
    if (focus) pop.focus();
    sync();
  }
  function closePopup(refocus = true): void {
    pop.hidden = true; selectedId = null; state.segment = null;
    map?.select(null);
    sync();
    if (refocus) box.focus();
  }
  pop.addEventListener('click', (e) => { if ((e.target as HTMLElement).closest('[data-pop-close]')) closePopup(); });

  function pick(id: string, recenter: boolean, open: boolean): void {
    cur = order.indexOf(id);
    map?.select(id, recenter);
    if (open) openPopup(id, false); else if (selectedId) openPopup(id, false);
    const f = fc?.features.find((x) => x.properties.id === id);
    if (f) {
      const v = speedOf(f.properties, state.perc, { hour: state.hour, period: state.period }, peak());
      say(t('map.live', { i: cur + 1, n: order.length, from: f.properties.stop_from, to: f.properties.stop_to, cls: classLabel(ctx, speedClass(v)) }));
    }
  }

  box.addEventListener('keydown', (e) => {
    if (!order.length) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      const d = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : -1;
      cur = cur < 0 ? (d > 0 ? 0 : order.length - 1) : (cur + d + order.length) % order.length;
      pick(order[cur], true, false);
    } else if (e.key === 'Enter' && cur >= 0) { e.preventDefault(); openPopup(order[cur]); }
    else if (e.key === 'Escape' && !pop.hidden) { e.preventDefault(); closePopup(); }
  });
  pop.addEventListener('keydown', (e) => { if (e.key === 'Escape') { e.preventDefault(); closePopup(); } });

  /* ---------- filters drawer (phones) ---------- */
  const setDrawer = (open: boolean): void => {
    panel.classList.toggle('is-open', open);
    panel.inert = mobile.matches && !open;
    if (mobile.matches) { if (open) (panel.querySelector('[data-filters-close]') as HTMLElement).focus(); }
  };
  $('[data-filters-open]').addEventListener('click', () => { closePopup(false); setDrawer(true); });
  $('[data-filters-close]').addEventListener('click', () => { setDrawer(false); ($('[data-filters-open]')).focus(); });
  panel.addEventListener('keydown', (e) => { if (e.key === 'Escape' && mobile.matches) { setDrawer(false); ($('[data-filters-open]')).focus(); } });
  mobile.addEventListener('change', () => setDrawer(false));
  setDrawer(false);

  /* ---------- overlay states on the map ---------- */
  const overlay = (kind: 'load' | 'none' | 'err' | null): void => {
    if (!kind) { over.hidden = true; return; }
    over.hidden = false;
    over.classList.toggle('idx-map__over--soft', kind === 'none');
    over.innerHTML = kind === 'load'
      ? `<div>${loader(t('state.loading'))}<p class="idx-ui idx-mute" style="margin-top: var(--idx-space-3)">${t('map.loading')}</p></div>`
      : kind === 'none'
        ? `<div class="idx-state" style="max-width: 34ch; text-align: left; background: var(--surface); padding: var(--idx-space-4); border-radius: var(--idx-radius-md)">${icon('info')}<div><p class="idx-ui-strong" style="color: var(--ink)">${t('map.none.title')}</p><p class="idx-ui">${t('map.none.text')}</p></div></div>`
        : `<div class="idx-state idx-state--error" style="max-width: 34ch; text-align: left">${icon('warning')}<div><p class="idx-ui-strong">${esc(t('map.err.title'))}</p><button class="idx-btn idx-btn--secondary" type="button" style="margin-top: var(--idx-space-3)" data-retry>${t('state.retry')}</button></div></div>`;
  };
  over.addEventListener('click', (e) => { if ((e.target as HTMLElement).closest('[data-retry]')) { overlay('load'); void boot(); } });

  /* ---------- data + map ---------- */
  function applyView(fade: boolean): void {
    renderTable(); sync();
    if (!map) return;
    map.update(view(), fade);
    const any = rows().some((r) => r.v != null);
    overlay(any ? null : 'none');
    if (selectedId) openPopup(selectedId, false);
  }

  async function loadCity(): Promise<void> {
    const my = ++token;
    overlay('load');
    try {
      const slug = state.city as string;
      city = cities.find((c) => c.slug === slug) ?? cities[0];
      state.city = city.slug; citySel.value = city.slug;
      $('[data-city-eyebrow]').textContent = citySel.selectedOptions[0]?.textContent ?? city.name;
      fc = await loadSegments(ctx.base, city.slug);
      if (my !== token) return;
      renderTable();
      if (map) { map.setCity(fc, city); map.update(view(), false); overlay(rows().some((r) => r.v != null) ? null : 'none'); }
      sync();
    } catch { overlay('err'); }
  }

  async function boot(): Promise<void> {
    try {
      [cities, manifest] = await Promise.all([loadCities(ctx.base), loadManifest(ctx.base)]);
      await loadCity();
      if (!map) {
        const { createSpeedMap } = await import('../map/speedmap');
        map = createSpeedMap(canvas, { interactive: true, peak: peak(), onPick: (id) => { if (id) pick(id, false, true); else if (!pop.hidden) closePopup(false); } });
        await map.ready;
        if (!map.hasTiles) {
          const n = document.createElement('p');
          n.className = 'idx-caption idx-map__notice'; n.textContent = t('map.notiles');
          box.append(n);
        }
        if (fc && city) { map.setCity(fc, city); map.update(view(), false); }
        map.pin(state.cls);
        overlay(rows().some((r) => r.v != null) ? null : 'none');
      }
      if (state.segment && order.includes(state.segment)) pick(state.segment, true, true);
    } catch {
      // no WebGL / tiles failed: the table view is the equivalent, so fall back to it
      overlay('err'); setTable(true);
    }
  }

  // initial state -> controls
  segs.get('mode')?.set(state.mode); segs.get('period')?.set(state.period); segs.get('perc')?.set(state.perc);
  if (state.hour != null) hourIn.value = String(state.hour);
  showHour(); refreshLegend(); setTable(state.table);
  void boot();
  void reduced;
}
