/** Route table + HTML document shell. Runs in Node (vite.config.ts plugin) at build/dev time; never imported by the client. */
import { esc, tr, type Ctx, type Lang, LANGS } from './i18n';
import { footer, topbar } from './components/shell';
import { archivePage, dataPage, methodPage, notFoundPage, qualityPage } from './pages/text';
import { cityPage } from './pages/city';
import { mapPage } from './pages/map';
import { rankingPage } from './pages/ranking';
import type { PageFn, PageOut, Site } from './pages/site';

const STATIC: Record<string, PageFn> = {
  '': rankingPage, mapa: mapPage, dane: dataPage, metodyka: methodPage, 'jakosc-danych': qualityPage, archiwum: archivePage,
};

/** Every route of the site, without language (PL and EN share them). */
export const routes = (site: Site): string[] => [...Object.keys(STATIC), ...site.cities.map((c) => `miasto/${c.slug}`)];

export function renderRoute(route: string, ctx: Ctx, site: Site): PageOut | null {
  if (route in STATIC) return STATIC[route](ctx, site);
  const m = /^miasto\/([\w-]+)$/.exec(route);
  return m && site.cities.some((c) => c.slug === m[1]) ? cityPage(ctx, site, m[1]) : null;
}

/** Tiny pre-paint script: stored theme, `idx-js` (hides reveal targets only when JS runs), and a safety net that
 *  un-hides everything if the app script never arrives. */
const BOOT = `(function(d){try{var s=localStorage.getItem('idx-theme');if(s==='light'||s==='dark')d.dataset.theme=s}catch(e){}d.classList.add('idx-js');setTimeout(function(){if(!window.__idx)d.classList.remove('idx-js')},6000)})(document.documentElement)`;

const FONTS = 'https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=IBM+Plex+Sans:wght@300;400;600&amp;display=swap';

export const HEAD_SLOT = '<!--idx:head-->';
export const SCRIPTS_SLOT = '<!--idx:scripts-->';

export function document(ctx: Ctx, page: PageOut): string {
  const tt = tr(ctx);
  const data = Object.entries({ page: page.page, lang: ctx.lang, base: ctx.base, ...page.data }).map(([k, v]) => ` data-${k}="${esc(v)}"`).join('');
  const title = `${page.title} · ${tt('site.name')}`;
  return `<!doctype html>
<html lang="${ctx.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<meta name="description" content="${esc(page.description)}">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website"><meta property="og:title" content="${title}"><meta property="og:description" content="${esc(page.description)}">
<link rel="icon" href="data:,">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="${FONTS}" rel="stylesheet">
<link rel="stylesheet" href="https://gisboost.github.io/assets/gisboost-1.css">
${HEAD_SLOT}
<script>${BOOT}</script>
</head>
<body>
<a class="idx-skip" href="#main">${tt('skip')}</a>
<div class="idx-frame idx-pv${page.frameClass ? ` ${page.frameClass}` : ''}"${data}>
${topbar(ctx, page.current, page.section)}
<main id="main" tabindex="-1">${page.main}</main>
${footer(ctx)}
</div>
${SCRIPTS_SLOT}
</body>
</html>
`;
}

export interface Emitted { file: string; html: string }
/** All pages of the site as [output file, html] pairs, both languages, plus 404.html. `inject` fills the head/script slots. */
export function renderSite(site: Site, base: string, inject: (html: string) => string): Emitted[] {
  const out: Emitted[] = [];
  for (const lang of LANGS) {
    const ctx: Ctx = { lang, base };
    for (const route of routes(site)) {
      const page = renderRoute(route, ctx, site);
      if (page) out.push({ file: `${lang === 'en' ? 'en/' : ''}${route ? `${route}/` : ''}index.html`, html: inject(document(ctx, page)) });
    }
  }
  const nf: Ctx = { lang: 'pl', base };
  out.push({ file: '404.html', html: inject(document(nf, notFoundPage(nf, site))) });
  return out;
}

/** Dev-server lookup: pathname (base already stripped) -> html, or null. */
export function renderPath(rest: string, site: Site, base: string, inject: (html: string) => string): string | null {
  const parts = rest.split('/').filter(Boolean);
  const lang: Lang = parts[0] === 'en' ? 'en' : 'pl';
  if (parts[0] === 'en') parts.shift();
  const ctx: Ctx = { lang, base }, route = parts.join('/');
  if (route === '404') return inject(document(ctx, notFoundPage(ctx, site)));
  const page = renderRoute(route, ctx, site);
  return page ? inject(document(ctx, page)) : null;
}

