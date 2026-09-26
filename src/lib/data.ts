/** Browser loader: fetch + validate + cache. Any failure (network, HTTP, shape) rejects with an Error that the UI turns
 *  into the "Spróbuj ponownie" state; a rejected load is not cached, so a retry refetches. */
import { parseCities, parseManifest, parseRanking, parseSegments, type City, type Manifest, type Ranking, type SegCollection } from './schema';

const cache = new Map<string, Promise<unknown>>();

function get<T>(key: string, base: string, path: string, parse: (v: unknown) => T): Promise<T> {
  // dev only: ?offline makes every load fail, to look at the error states
  if (import.meta.env.DEV && new URLSearchParams(location.search).has('offline')) return Promise.reject(new Error('offline (dev flag)'));
  let p = cache.get(key) as Promise<T> | undefined;
  if (!p) {
    p = fetch(`${base}data/${path}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${path}: HTTP ${r.status}`))))
      .then(parse);
    p.catch(() => cache.delete(key));
    cache.set(key, p);
  }
  return p;
}

export const loadManifest = (base: string): Promise<Manifest> => get('manifest', base, 'manifest.json', parseManifest);
export const loadCities = (base: string): Promise<City[]> => get('cities', base, 'cities.json', parseCities);
export const loadRanking = async (base: string): Promise<Ranking> => {
  const cities = await loadCities(base);
  return get('ranking', base, 'ranking.json', (v) => parseRanking(v, cities));
};
export const loadSegments = (base: string, slug: string): Promise<SegCollection> =>
  get(`seg:${slug}`, base, `segments/${slug}.geojson`, (v) => parseSegments(v, `segments/${slug}`));
