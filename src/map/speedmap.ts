/** MapLibre speed map: style built from the idx-map-* / idx-speed-* tokens (both themes), segments coloured by a `step`
 *  expression over the token thresholds, "brak danych" dashed. Loaded lazily (dynamic import) only on pages with a map.
 *  Motion here is opacity only: the segments come in as a wave from the centre, a change of view fades through. */
import { Map as MlMap, Marker, setWorkerUrl, type GeoJSONSource, type LayerSpecification, type StyleSpecification } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { getThresholds } from '../lib/idx';
import { speedOf, type Perc, type Sel } from '../lib/agg';
import type { City, Mode, SegCollection, SegFeature } from '../lib/schema';
import { ease, ms, reduced } from '../motion';

/** mode null = both modes (city mini-map) */
export interface ViewState { mode: Mode | null; perc: Perc; sel: Sel }
export interface SpeedMapOpts {
  interactive: boolean; peak: number[];
  /** called when a segment is picked with the pointer (null = empty click) */
  onPick?: (id: string | null) => void;
}
export interface SpeedMap {
  ready: Promise<void>;
  hasTiles: boolean;
  setCity(fc: SegCollection, city: City): void;
  update(view: ViewState, fade?: boolean): void;
  /** hover / focus on a legend class: dim the others (null = all) */
  dim(cls: number | null): void;
  /** click on a legend class: keep only that class (null = all) */
  pin(cls: number | null): void;
  select(id: string | null, recenter?: boolean): void;
  /** screen position of a segment's midpoint, relative to the map container (null if unknown) */
  pixelOf(id: string): [number, number] | null;
  /** speed of the currently shown view, by segment id (for the table view and the popup) */
  current(): Map<string, number | null>;
  destroy(): void;
}

const css = (name: string): string => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const TILES = import.meta.env.VITE_TILES_URL as string | undefined;
const GLYPHS = import.meta.env.VITE_GLYPHS_URL as string | undefined;
const FONT = (import.meta.env.VITE_GLYPHS_FONT as string | undefined) || 'Noto Sans Regular';
const RINGS = 5;
// MapLibre 6 looks for its worker next to its entry chunk; once bundled that file is gone. vite.config.ts serves/emits the
// worker (+ its shared chunk) as plain static files under vendor/maplibre/, and we point MapLibre there.
setWorkerUrl(`${import.meta.env.BASE_URL}vendor/maplibre/maplibre-gl-worker.mjs`);
interface DrawFC { type: 'FeatureCollection'; features: { type: 'Feature'; geometry: SegFeature['geometry']; properties: Record<string, unknown> }[] }

/** ['step', input, v0, t1, v1, ..., t5, v5] over the token thresholds */
const step = (input: unknown, values: (string | number)[]): unknown[] => {
  const out: unknown[] = ['step', input, values[0]];
  getThresholds().forEach((t, i) => out.push(t, values[i + 1]));
  return out;
};

function baseLayers(): { sources: StyleSpecification['sources']; layers: LayerSpecification[] } {
  const land = css('--idx-map-land'), water = css('--idx-map-water'), road = css('--idx-map-road'), boundary = css('--idx-map-boundary'), label = css('--idx-map-label');
  const layers: LayerSpecification[] = [{ id: 'land', type: 'background', paint: { 'background-color': land } }];
  const sources: StyleSpecification['sources'] = {};
  if (TILES) {
    sources.base = /\.json(\?|$)/.test(TILES) ? { type: 'vector', url: TILES } : { type: 'vector', tiles: [TILES], maxzoom: 14 };
    layers.push(
      { id: 'water', type: 'fill', source: 'base', 'source-layer': 'water', paint: { 'fill-color': water } },
      { id: 'waterway', type: 'line', source: 'base', 'source-layer': 'waterway', paint: { 'line-color': water, 'line-width': 1.2 } },
      { id: 'road', type: 'line', source: 'base', 'source-layer': 'transportation', minzoom: 10, layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': road, 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.4, 15, 1.4] } },
      { id: 'boundary', type: 'line', source: 'base', 'source-layer': 'boundary', filter: ['<=', ['get', 'admin_level'], 8], paint: { 'line-color': boundary, 'line-width': 1, 'line-dasharray': [2, 3] } },
    );
    if (GLYPHS) {
      layers.push({ id: 'place', type: 'symbol', source: 'base', 'source-layer': 'place', layout: { 'text-field': ['get', 'name'], 'text-font': [FONT], 'text-size': 12 }, paint: { 'text-color': label, 'text-halo-color': land, 'text-halo-width': 1.2 } });
    }
  }
  return { sources, layers };
}

export function createSpeedMap(container: HTMLElement, opts: SpeedMapOpts): SpeedMap {
  // dev only: exercise the no-WebGL fallback (table view) without a browser that lacks WebGL
  if (import.meta.env.DEV && new URLSearchParams(location.search).has('nogl')) throw new Error('WebGL disabled by ?nogl');
  let fc: SegCollection = { type: 'FeatureCollection', features: [] };
  let city: City | null = null;
  let view: ViewState | null = null;
  let hoverCls: number | null = null, pinCls: number | null = null;
  let waveDone = false, destroyed = false;
  const speeds = new globalThis.Map<string, number | null>();
  const rings = new globalThis.Map<string, number>();
  let marker: Marker | null = null;

  const focusCls = (): number | null => hoverCls ?? pinCls;
  const opacityFor = (): unknown => {
    const c = focusCls();
    return c == null ? 1 : ['case', ['==', step(['get', 'v'], [1, 2, 3, 4, 5, 6]), c], 1, 0.2];
  };
  const ndOpacity = (): number => (focusCls() == null ? 1 : 0.2);

  function segLayers(): LayerSpecification[] {
    const colors = [1, 2, 3, 4, 5, 6].map((i) => css(`--idx-speed-${i}`));
    const width = ['interpolate', ['linear'], ['zoom'], 8, 1.6, 12, 3, 15, 4.5] as unknown as number;
    const out: LayerSpecification[] = [];
    for (let k = 0; k < RINGS; k++) {
      out.push({
        id: `seg-r${k}`, type: 'line', source: 'seg', filter: ['all', ['has', 'v'], ['==', ['get', 'ring'], k]],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: { 'line-color': step(['get', 'v'], colors) as never, 'line-width': width, 'line-opacity': (waveDone ? opacityFor() : 0) as never, 'line-opacity-transition': { duration: reduced() ? 0 : 500, delay: waveDone ? 0 : k * 90 } },
      });
    }
    out.push({
      id: 'seg-nd', type: 'line', source: 'seg', filter: ['!', ['has', 'v']],
      layout: { 'line-cap': 'butt', 'line-join': 'round' },
      paint: { 'line-color': css('--idx-speed-nodata'), 'line-width': 3, 'line-dasharray': [2, 1.6], 'line-opacity': waveDone ? ndOpacity() : 0, 'line-opacity-transition': { duration: reduced() ? 0 : 500, delay: waveDone ? 0 : RINGS * 90 } },
    });
    return out;
  }

  function data(): DrawFC {
    speeds.clear();
    const features: DrawFC['features'] = [];
    if (view) {
      for (const f of fc.features) {
        if (view.mode && f.properties.mode !== view.mode) continue;
        const v = speedOf(f.properties, view.perc, view.sel, opts.peak);
        speeds.set(f.properties.id, v);
        features.push({ type: 'Feature', geometry: f.geometry, properties: { id: f.properties.id, ring: rings.get(f.properties.id) ?? 0, ...(v != null ? { v } : {}) } });
      }
    }
    return { type: 'FeatureCollection', features };
  }

  const style = (): StyleSpecification => {
    const b = baseLayers();
    return { version: 8, ...(GLYPHS ? { glyphs: GLYPHS } : {}), sources: { ...b.sources, seg: { type: 'geojson', data: data() } }, layers: [...b.layers, ...segLayers()] };
  };

  const map = new MlMap({
    container, style: style(), center: [19.45, 51.76], zoom: 10, minZoom: 6, maxZoom: 17, attributionControl: false,
    interactive: opts.interactive, keyboard: false, dragRotate: false, pitchWithRotate: false, fadeDuration: 0,
  });
  if (import.meta.env.DEV) (globalThis as { __idxMap?: MlMap }).__idxMap = map; // dev only: lets tests inspect the map
  if (opts.interactive) map.touchZoomRotate.disableRotation();
  const canvasNotice = (): void => { container.querySelector('canvas')?.setAttribute('aria-hidden', 'true'); };

  const ready = new Promise<void>((res, rej) => {
    map.once('load', () => { canvasNotice(); res(); });
    map.once('error', (e) => { if (!map.loaded()) rej(e.error); });
  });

  const layerIds = (): string[] => [...Array.from({ length: RINGS }, (_, k) => `seg-r${k}`), 'seg-nd'];
  const setOpacity = (dur: number): void => {
    if (destroyed || !map.getStyle()) return;
    layerIds().forEach((id) => {
      if (!map.getLayer(id)) return;
      map.setPaintProperty(id, 'line-opacity-transition', { duration: reduced() ? 0 : dur, delay: 0 });
      map.setPaintProperty(id, 'line-opacity', (id === 'seg-nd' ? ndOpacity() : opacityFor()) as never);
    });
  };
  const pushData = (): void => { (map.getSource('seg') as GeoJSONSource | undefined)?.setData(data()); };

  /** wave from the centre: the ring layers carry staggered opacity transitions */
  function wave(): void {
    if (waveDone) return;
    waveDone = true;
    if (reduced()) { setOpacity(0); return; }
    layerIds().forEach((id, k) => {
      map.setPaintProperty(id, 'line-opacity-transition', { duration: 500, delay: k * 90 });
      map.setPaintProperty(id, 'line-opacity', (id === 'seg-nd' ? ndOpacity() : opacityFor()) as never);
    });
  }

  function midOf(f: SegFeature): [number, number] {
    const c = f.geometry.coordinates, a = c[Math.floor((c.length - 1) / 2)], b = c[Math.ceil((c.length - 1) / 2)];
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  }

  function computeRings(): void {
    rings.clear();
    if (!city) return;
    const [cx, cy] = city.center, k = Math.cos(cy * Math.PI / 180);
    const d = fc.features.map((f) => { const m = midOf(f); return [f.properties.id, Math.hypot((m[0] - cx) * k, m[1] - cy)] as const; });
    const max = Math.max(...d.map((x) => x[1]), 1e-9);
    d.forEach(([id, dist]) => rings.set(id, Math.min(RINGS - 1, Math.floor(dist / max * RINGS))));
  }

  const ringEl = document.createElement('div');
  ringEl.className = 'idx-ring'; ringEl.setAttribute('aria-hidden', 'true'); ringEl.innerHTML = '<i></i>';

  const api: SpeedMap = {
    ready, hasTiles: Boolean(TILES),
    setCity(nextFc, nextCity) {
      fc = nextFc; city = nextCity; computeRings();
      api.select(null);
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const f of fc.features) for (const [x, y] of f.geometry.coordinates) { minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
      if (Number.isFinite(minX)) map.fitBounds([[minX, minY], [maxX, maxY]], { padding: 36, maxZoom: 14, duration: 0 });
      else map.jumpTo({ center: city.center, zoom: city.zoom });
      pushData();
    },
    update(v, fade = false) {
      view = v;
      if (!waveDone || !fade || reduced()) { pushData(); return; }
      setOpacity(ms('--idx-dur-fast'));
      window.setTimeout(() => { if (destroyed) return; pushData(); window.setTimeout(() => setOpacity(ms('--idx-dur-base')), 90); }, ms('--idx-dur-fast') + 10);
    },
    dim(c) { hoverCls = c; setOpacity(ms('--idx-dur-fast')); },
    pin(c) { pinCls = c; setOpacity(ms('--idx-dur-fast')); },
    select(id, recenter = false) {
      marker?.remove();
      if (!id) return;
      const f = fc.features.find((x) => x.properties.id === id);
      if (!f) return;
      const at = midOf(f);
      marker = new Marker({ element: ringEl, anchor: 'center' }).setLngLat(at).addTo(map);
      const inner = ringEl.firstElementChild as HTMLElement;
      if (!reduced()) inner.animate([{ transform: 'scale(0.6)', opacity: 0 }, { transform: 'scale(1)', opacity: 1 }], { duration: ms('--idx-dur-base'), easing: ease('--idx-ease-out') });
      if (recenter && !map.getBounds().contains(at)) map.easeTo({ center: at, duration: reduced() ? 0 : 300 });
    },
    pixelOf(id) {
      const f = fc.features.find((x) => x.properties.id === id);
      if (!f) return null;
      const p = map.project(midOf(f));
      return [p.x, p.y];
    },
    current: () => speeds,
    destroy() { destroyed = true; document.removeEventListener('idx:theme', onTheme); map.remove(); },
  };

  // theme: the tokens changed under us, rebuild the style from them (sources and data are part of the style, so they survive)
  const onTheme = (): void => { if (!destroyed && map.getStyle()) map.setStyle(style(), { diff: true }); };
  document.addEventListener('idx:theme', onTheme);

  if (opts.interactive) {
    const hit = (e: { point: { x: number; y: number } }): string | null => {
      const r = 9, feats = map.queryRenderedFeatures([[e.point.x - r, e.point.y - r], [e.point.x + r, e.point.y + r]], { layers: layerIds().filter((id) => map.getLayer(id)) });
      return (feats[0]?.properties?.id as string | undefined) ?? null;
    };
    map.on('click', (e) => opts.onPick?.(hit(e)));
    map.on('mousemove', (e) => { map.getCanvas().style.cursor = hit(e) ? 'pointer' : ''; });
  }
  new ResizeObserver(() => { if (!destroyed) map.resize(); }).observe(container);
  ready.then(() => { if (!destroyed) { pushData(); wave(); } }).catch(() => undefined);
  return api;
}
