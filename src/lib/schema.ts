/** Data schema + validators. Shared by the SSG (Node) and the browser loader; no dependencies.
 *  Every field that can be unknown is `| null`; the UI renders null as "XX" / "za mało danych". */

export class DataError extends Error {}

export type Quality = 'ranked' | 'limited' | 'out';
export type Mode = 'tram' | 'bus';
export type Period = 'day' | 'peak' | 'off';
export const MODES: Mode[] = ['tram', 'bus'];
export const PERIODS: Period[] = ['day', 'peak', 'off'];

export interface Line { route: string | null; measured: number | null; plan: number | null; n: number | null }
export interface City {
  slug: string; name: string; name_en: string; name_loc: string | null; region: string; region_en: string;
  center: [number, number]; zoom: number; quality: Quality; coverage: number | null;
  kpi: { measured: number | null; plan: number | null; n: number | null; rank: number | null };
  hourly: { plan: (number | null)[]; meas: (number | null)[] };
  lines: Line[];
}
export interface RankRow { slug: string; kmh: number | null }
export type Ranking = Record<Mode, Record<Period, RankRow[]>>;
export interface SegProps {
  id: string; route: string | null; mode: Mode; stop_from: string; stop_to: string; plan_kmh: number | null;
  kmh_p15: (number | null)[]; kmh_p50: (number | null)[]; kmh_p85: (number | null)[]; n: number | null;
}
export interface SegFeature { type: 'Feature'; geometry: { type: 'LineString'; coordinates: [number, number][] }; properties: SegProps }
export interface SegCollection { type: 'FeatureCollection'; features: SegFeature[] }
export interface DataFile { id: string; name: string; format: string; encoding: string; license: string | null; size_mb: number | null; url: string | null }
export interface Manifest {
  placeholder: boolean; edition: string; generated: string | null; peak_hours: number[];
  thresholds: { sample_min: number | null; coverage_min: number | null };
  files: DataFile[]; editions: { edition: string; current: boolean; published: string | null }[];
}

const fail = (p: string, m: string): never => { throw new DataError(`${p}: ${m}`); };
type R = Record<string, unknown>;
const obj = (v: unknown, p: string): R => (typeof v === 'object' && v !== null && !Array.isArray(v) ? (v as R) : fail(p, 'expected object'));
const arr = <T>(v: unknown, p: string, f: (x: unknown, p: string) => T): T[] => (Array.isArray(v) ? v.map((x, i) => f(x, `${p}[${i}]`)) : fail(p, 'expected array'));
const str = (v: unknown, p: string): string => (typeof v === 'string' ? v : fail(p, 'expected string'));
const num = (v: unknown, p: string): number => (typeof v === 'number' && Number.isFinite(v) ? v : fail(p, 'expected number'));
const bool = (v: unknown, p: string): boolean => (typeof v === 'boolean' ? v : fail(p, 'expected boolean'));
const nul = <T>(f: (x: unknown, p: string) => T) => (v: unknown, p: string): T | null => (v === null ? null : f(v, p));
const oneOf = <T extends string>(v: unknown, p: string, set: readonly T[]): T => (set.includes(v as T) ? (v as T) : fail(p, `expected one of ${set.join(', ')}`));
const hours = (v: unknown, p: string): (number | null)[] => {
  const a = arr(v, p, nul(num));
  return a.length === 24 ? a : fail(p, `expected 24 hourly values, got ${a.length}`);
};

export function parseCities(v: unknown): City[] {
  const cities = arr(v, 'cities', (c, p): City => {
    const o = obj(c, p), k = obj(o.kpi, `${p}.kpi`), h = obj(o.hourly, `${p}.hourly`), ce = arr(o.center, `${p}.center`, num);
    if (ce.length !== 2) fail(`${p}.center`, 'expected [lon, lat]');
    return {
      slug: str(o.slug, `${p}.slug`), name: str(o.name, `${p}.name`), name_en: str(o.name_en, `${p}.name_en`), name_loc: nul(str)(o.name_loc, `${p}.name_loc`),
      region: str(o.region, `${p}.region`), region_en: str(o.region_en, `${p}.region_en`),
      center: [ce[0], ce[1]], zoom: num(o.zoom, `${p}.zoom`), quality: oneOf(o.quality, `${p}.quality`, ['ranked', 'limited', 'out']),
      coverage: nul(num)(o.coverage, `${p}.coverage`),
      kpi: { measured: nul(num)(k.measured, `${p}.kpi.measured`), plan: nul(num)(k.plan, `${p}.kpi.plan`), n: nul(num)(k.n, `${p}.kpi.n`), rank: nul(num)(k.rank, `${p}.kpi.rank`) },
      hourly: { plan: hours(h.plan, `${p}.hourly.plan`), meas: hours(h.meas, `${p}.hourly.meas`) },
      lines: arr(o.lines, `${p}.lines`, (l, q): Line => {
        const lo = obj(l, q);
        return { route: nul(str)(lo.route, `${q}.route`), measured: nul(num)(lo.measured, `${q}.measured`), plan: nul(num)(lo.plan, `${q}.plan`), n: nul(num)(lo.n, `${q}.n`) };
      }),
    };
  });
  const seen = new Set<string>();
  for (const c of cities) { if (seen.has(c.slug)) fail('cities', `duplicate slug ${c.slug}`); seen.add(c.slug); }
  return cities;
}

export function parseRanking(v: unknown, cities: City[]): Ranking {
  const o = obj(v, 'ranking'), slugs = new Set(cities.map((c) => c.slug));
  const out = {} as Ranking;
  for (const m of MODES) {
    const mo = obj(o[m], `ranking.${m}`);
    out[m] = {} as Ranking[Mode];
    for (const per of PERIODS) {
      out[m][per] = arr(mo[per], `ranking.${m}.${per}`, (r, p): RankRow => {
        const ro = obj(r, p), slug = str(ro.slug, `${p}.slug`);
        if (!slugs.has(slug)) fail(`${p}.slug`, `unknown city ${slug}`);
        return { slug, kmh: nul(num)(ro.kmh, `${p}.kmh`) };
      });
    }
  }
  return out;
}

export function parseSegments(v: unknown, name = 'segments'): SegCollection {
  const o = obj(v, name);
  if (o.type !== 'FeatureCollection') fail(name, 'expected FeatureCollection');
  return {
    type: 'FeatureCollection',
    features: arr(o.features, `${name}.features`, (f, p): SegFeature => {
      const fo = obj(f, p), g = obj(fo.geometry, `${p}.geometry`), pr = obj(fo.properties, `${p}.properties`);
      if (g.type !== 'LineString') fail(`${p}.geometry.type`, 'expected LineString');
      const coords = arr(g.coordinates, `${p}.geometry.coordinates`, (c, q) => { const a = arr(c, q, num); return a.length === 2 ? ([a[0], a[1]] as [number, number]) : fail(q, 'expected [lon, lat]'); });
      if (coords.length < 2) fail(`${p}.geometry.coordinates`, 'expected at least 2 points');
      const q = `${p}.properties`;
      return {
        type: 'Feature', geometry: { type: 'LineString', coordinates: coords },
        properties: {
          id: str(pr.id, `${q}.id`), route: nul(str)(pr.route, `${q}.route`), mode: oneOf(pr.mode, `${q}.mode`, MODES),
          stop_from: str(pr.stop_from, `${q}.stop_from`), stop_to: str(pr.stop_to, `${q}.stop_to`), plan_kmh: nul(num)(pr.plan_kmh, `${q}.plan_kmh`),
          kmh_p15: hours(pr.kmh_p15, `${q}.kmh_p15`), kmh_p50: hours(pr.kmh_p50, `${q}.kmh_p50`), kmh_p85: hours(pr.kmh_p85, `${q}.kmh_p85`), n: nul(num)(pr.n, `${q}.n`),
        },
      };
    }),
  };
}

export function parseManifest(v: unknown): Manifest {
  const o = obj(v, 'manifest'), t = obj(o.thresholds, 'manifest.thresholds');
  return {
    placeholder: bool(o.placeholder, 'manifest.placeholder'), edition: str(o.edition, 'manifest.edition'), generated: nul(str)(o.generated, 'manifest.generated'),
    peak_hours: arr(o.peak_hours, 'manifest.peak_hours', num),
    thresholds: { sample_min: nul(num)(t.sample_min, 'manifest.thresholds.sample_min'), coverage_min: nul(num)(t.coverage_min, 'manifest.thresholds.coverage_min') },
    files: arr(o.files, 'manifest.files', (f, p): DataFile => {
      const fo = obj(f, p);
      return { id: str(fo.id, `${p}.id`), name: str(fo.name, `${p}.name`), format: str(fo.format, `${p}.format`), encoding: str(fo.encoding, `${p}.encoding`), license: nul(str)(fo.license, `${p}.license`), size_mb: nul(num)(fo.size_mb, `${p}.size_mb`), url: nul(str)(fo.url, `${p}.url`) };
    }),
    editions: arr(o.editions, 'manifest.editions', (e, p) => {
      const eo = obj(e, p);
      return { edition: str(eo.edition, `${p}.edition`), current: bool(eo.current, `${p}.current`), published: nul(str)(eo.published, `${p}.published`) };
    }),
  };
}
