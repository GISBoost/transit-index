/** Pure helpers shared by the prerender and the client: hourly aggregation, ranking order, network geometry. */
import type { City, Mode, Period, Quality, RankRow, SegCollection, SegProps } from './schema';

export type Perc = 'p15' | 'p50' | 'p85';
export const PERCS: Perc[] = ['p15', 'p50', 'p85'];
export const KMH_AXIS_MAX = 30; // ranking bars run 0..30 km/h
export const DEFAULT_CITY = 'lodz';

export interface Sel { hour: number | null; period: Period }

/** Hours that belong to a period. peak comes from the manifest, off is the complement. */
export function periodHours(period: Period, peak: number[]): number[] {
  const all = Array.from({ length: 24 }, (_, h) => h);
  return period === 'day' ? all : period === 'peak' ? peak : all.filter((h) => !peak.includes(h));
}

const median = (a: number[]): number => {
  const s = [...a].sort((x, y) => x - y), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

/** Speed of a segment for a percentile and a selection. A single hour reads that hour; a period is the median of its
 *  non-null hourly values (an approximation: replace with pipeline-made aggregates when the real data arrives). */
export function speedOf(p: SegProps, perc: Perc, sel: Sel, peak: number[]): number | null {
  const arr = p[`kmh_${perc}`];
  if (sel.hour != null) return arr[sel.hour] ?? null;
  const v = periodHours(sel.period, peak).map((h) => arr[h]).filter((x): x is number => x != null);
  return v.length ? median(v) : null;
}

export interface RankItem { slug: string; kmh: number | null; quality: Quality; pos: number | null }
/** Fastest first; cities without a value or "out" of the ranking come last, in data order, without a position. */
export function sortRanking(rows: RankRow[], cities: City[]): RankItem[] {
  const q = new Map(cities.map((c) => [c.slug, c.quality]));
  const ranked = (r: RankRow) => r.kmh != null && q.get(r.slug) !== 'out';
  return [
    ...rows.filter(ranked).sort((a, b) => (b.kmh as number) - (a.kmh as number))
      .map((r, i): RankItem => ({ slug: r.slug, kmh: r.kmh, quality: q.get(r.slug) ?? 'ranked', pos: i + 1 })),
    ...rows.filter((r) => !ranked(r)).map((r): RankItem => ({ slug: r.slug, kmh: null, quality: 'out', pos: null })),
  ];
}

export const MODE_KEYS: Record<Mode, string> = { tram: 'mode.tram', bus: 'mode.bus' };
export const PERIOD_KEYS: Record<Period, string> = { day: 'period.day', peak: 'period.peak', off: 'period.off' };

export interface Bounds { minX: number; maxX: number; minY: number; maxY: number }
export function bounds(fc: SegCollection): Bounds {
  const b = { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
  for (const f of fc.features) for (const [x, y] of f.geometry.coordinates) {
    b.minX = Math.min(b.minX, x); b.maxX = Math.max(b.maxX, x); b.minY = Math.min(b.minY, y); b.maxY = Math.max(b.maxY, y);
  }
  return b;
}
export const midpoint = (c: [number, number][]): [number, number] => {
  const a = c[Math.floor((c.length - 1) / 2)], b = c[Math.ceil((c.length - 1) / 2)];
  return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
};
