/** Vite MPA with a tiny prerender plugin: every page (PL + EN, one per city) is rendered to static HTML from the templates in
 *  src/pages + the JSON in public/data, so the content exists without JS; src/main.ts then enhances it.
 *  Dev: pages are rendered per request (edits to templates show on refresh). Build: HTML is emitted next to the hashed assets. */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig, type Plugin, type ViteDevServer } from 'vite';
import { parseCities, parseManifest, parseRanking, parseSegments } from './src/lib/schema';
import type { Site } from './src/pages/site';
import * as buildRender from './src/render';
import * as buildIdx from './src/lib/idx';

const ROOT = process.cwd();
const HEAD_SLOT = '<!--idx:head-->', SCRIPTS_SLOT = '<!--idx:scripts-->';

function loadSite(): Site {
  const json = (p: string): unknown => JSON.parse(readFileSync(resolve(ROOT, 'public/data', p), 'utf8'));
  const cities = parseCities(json('cities.json'));
  return {
    cities,
    ranking: parseRanking(json('ranking.json'), cities),
    manifest: parseManifest(json('manifest.json')),
    segments: new Map(cities.map((c) => [c.slug, parseSegments(json(`segments/${c.slug}.geojson`), c.slug)])),
  };
}

/** Speed class thresholds come from design/tokens.json (idx-speed-t1..t5), the same tokens the CSS exposes. */
function thresholds(): number[] {
  const tok = JSON.parse(readFileSync(resolve(ROOT, 'design/tokens.json'), 'utf8')) as { threshold: { tokens: { name: string; value: string }[] } };
  return [1, 2, 3, 4, 5].map((i) => Number(tok.threshold.tokens.find((t) => t.name === `idx-speed-t${i}`)?.value));
}

function prerender(): Plugin {
  let base = '/';
  let dev: ViteDevServer | undefined;
  return {
    name: 'idx-prerender',
    configResolved(c) { base = c.base; },
    configureServer(server) {
      dev = server;
      server.middlewares.use(async (req, res, next) => {
        const path = decodeURIComponent(new URL(req.url ?? '/', 'http://localhost').pathname);
        if (/\.\w+$/.test(path)) return next();
        try {
          const R = (await server.ssrLoadModule('/src/render.ts')) as typeof buildRender;
          const I = (await server.ssrLoadModule('/src/lib/idx.ts')) as typeof buildIdx;
          I.setThresholds(thresholds());
          const html = R.renderPath(path.replace(/^\//, ''), loadSite(), '/', (h) => h.replace(HEAD_SLOT, '').replace(SCRIPTS_SLOT, '<script type="module" src="/src/main.ts"></script>'));
          if (html == null) return next();
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          res.end(await server.transformIndexHtml(req.url ?? '/', html));
        } catch (e) {
          server.ssrFixStacktrace(e as Error);
          next(e);
        }
      });
    },
    generateBundle(_, bundle) {
      if (dev) return;
      const entry = Object.values(bundle).find((b) => b.type === 'chunk' && b.isEntry);
      if (!entry || entry.type !== 'chunk') throw new Error('idx-prerender: no entry chunk');
      const css = [...(entry.viteMetadata?.importedCss ?? [])];
      const head = css.map((f) => `<link rel="stylesheet" href="${base}${f}">`).join('\n') + entry.imports.map((f) => `\n<link rel="modulepreload" href="${base}${f}">`).join('');
      const scripts = `<script type="module" src="${base}${entry.fileName}"></script>`;
      buildIdx.setThresholds(thresholds());
      for (const p of buildRender.renderSite(loadSite(), base, (h) => h.replace(HEAD_SLOT, head).replace(SCRIPTS_SLOT, scripts))) {
        this.emitFile({ type: 'asset', fileName: p.file, source: p.html });
      }
    },
  };
}

/** MapLibre 6 runs its worker as an ES module that imports a shared chunk by relative path. Serve both files untouched
 *  (dev) and emit them next to the site (build); src/map/speedmap.ts points setWorkerUrl at vendor/maplibre/. */
function maplibreWorker(): Plugin {
  const dir = resolve(ROOT, 'node_modules/maplibre-gl/dist');
  const files = ['maplibre-gl-worker.mjs', 'maplibre-gl-shared.mjs'];
  return {
    name: 'idx-maplibre-worker',
    configureServer(server) {
      server.middlewares.use('/vendor/maplibre', (req, res, next) => {
        const f = (req.url ?? '').replace(/^\//, '').split('?')[0];
        if (!files.includes(f)) return next();
        res.setHeader('Content-Type', 'text/javascript');
        res.end(readFileSync(resolve(dir, f)));
      });
    },
    generateBundle() {
      for (const f of files) this.emitFile({ type: 'asset', fileName: `vendor/maplibre/${f}`, source: readFileSync(resolve(dir, f)) });
    },
  };
}

export default defineConfig(({ command, isPreview }) => ({
  base: command === 'build' || isPreview ? `/${(process.env.BASE ?? '/transit-index/').replace(/^\/+|\/+$/g, '')}/`.replace(/^\/\/$/, '/') : '/',
  plugins: [prerender(), maplibreWorker()],
  build: { rollupOptions: { input: { main: resolve(ROOT, 'src/main.ts') } }, target: 'es2022', chunkSizeWarningLimit: 1200 },
  appType: isPreview ? 'mpa' : 'custom',
}));
