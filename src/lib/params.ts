/** URL state (shareable links): ranking `?rodzaj=&pora=`, map `?miasto=&rodzaj=&pora=&h=&perc=&klasa=&widok=&odcinek=`.
 *  Polish words in the URL, internal codes in the code. Unknown values fall back to the default, never throw. */
import type { Mode, Period } from './schema';
import type { Perc } from './agg';

const MODE_URL: Record<Mode, string> = { tram: 'tramwaje', bus: 'autobusy' };
const PERIOD_URL: Record<Period, string> = { day: 'dzien', peak: 'szczyt', off: 'poza' };
const inv = <K extends string>(m: Record<K, string>): Record<string, K> => Object.fromEntries(Object.entries(m).map(([k, v]) => [v, k])) as Record<string, K>;
const URL_MODE = inv(MODE_URL), URL_PERIOD = inv(PERIOD_URL);

export interface RankState { mode: Mode; period: Period }
export interface MapState {
  city: string | null; mode: Mode; period: Period; hour: number | null; perc: Perc;
  cls: number | null; table: boolean; segment: string | null;
}

export function readRank(q: URLSearchParams): RankState {
  return { mode: URL_MODE[q.get('rodzaj') ?? ''] ?? 'tram', period: URL_PERIOD[q.get('pora') ?? ''] ?? 'day' };
}
export function writeRank(s: RankState): string {
  const q = new URLSearchParams();
  if (s.mode !== 'tram') q.set('rodzaj', MODE_URL[s.mode]);
  if (s.period !== 'day') q.set('pora', PERIOD_URL[s.period]);
  return q.toString();
}

export function readMap(q: URLSearchParams): MapState {
  const h = q.get('h'), perc = q.get('perc'), cls = Number(q.get('klasa'));
  return {
    city: q.get('miasto'), mode: URL_MODE[q.get('rodzaj') ?? ''] ?? 'tram', period: URL_PERIOD[q.get('pora') ?? ''] ?? 'day',
    hour: h != null && /^\d+$/.test(h) && Number(h) < 24 ? Number(h) : null,
    perc: perc === 'p15' || perc === 'p85' ? perc : 'p50', cls: cls >= 1 && cls <= 6 ? cls : null,
    table: q.get('widok') === 'tabela', segment: q.get('odcinek'),
  };
}
export function writeMap(s: MapState, defaultCity: string): string {
  const q = new URLSearchParams();
  if (s.city && s.city !== defaultCity) q.set('miasto', s.city);
  if (s.mode !== 'tram') q.set('rodzaj', MODE_URL[s.mode]);
  if (s.period !== 'day') q.set('pora', PERIOD_URL[s.period]);
  if (s.hour != null) q.set('h', String(s.hour));
  if (s.perc !== 'p50') q.set('perc', s.perc);
  if (s.cls != null) q.set('klasa', String(s.cls));
  if (s.table) q.set('widok', 'tabela');
  if (s.segment) q.set('odcinek', s.segment);
  return q.toString();
}
