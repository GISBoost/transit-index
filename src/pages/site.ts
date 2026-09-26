/** What the prerender knows about the world: validated data + page renderer contract. */
import type { City, Manifest, Ranking, SegCollection } from '../lib/schema';
import type { Ctx } from '../i18n';

export interface Site {
  cities: City[];
  ranking: Ranking;
  manifest: Manifest;
  segments: Map<string, SegCollection>;
}

export interface PageOut {
  /** browser tab title (without the site suffix) */
  title: string;
  description: string;
  /** value of data-page: selects the client module */
  page: string;
  /** nav route highlighted in the topbar; `section` = the page belongs to that section (city pages) */
  current: string | null;
  section?: boolean;
  /** everything inside <main> */
  main: string;
  /** extra class on the root frame, e.g. the map page */
  frameClass?: string;
  /** extra data-* attributes on the root frame */
  data?: Record<string, string>;
}

export type PageFn = (ctx: Ctx, site: Site) => PageOut;
