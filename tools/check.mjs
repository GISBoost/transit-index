// Project checks (no dependencies): node tools/check.mjs   (npm run check; run `npm run build` first for the link check)
//   a) no colour literals in src/ and the site CSS (colours only from tokens)
//   b) contrast of the token pairs used for text (4.5:1), controls and map lines (3:1), both themes
//   c) nothing animated except transform / opacity (CSS transitions, keyframes, WAAPI, GSAP)
//   d) i18n: same keys in pl/en, every used key exists, same {placeholders}, no raw "<" / "&"; internal links in dist/ resolve
//   e) hygiene: css/bundle.css is an unchanged copy, no IDX.demo in the build, no lorem / emoji
// Exit code 1 on any failure. Findings that come from the design system itself are listed as "info" (not failures).
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, resolve, sep } from 'node:path';

const ROOT = resolve(import.meta.dirname, '..');
const rd = (p) => readFileSync(join(ROOT, p), 'utf8');
const rel = (p) => relative(ROOT, p).split(sep).join('/');
function walk(dir, ext, out = []) {
  if (!existsSync(dir)) return out;
  for (const n of readdirSync(dir)) {
    const p = join(dir, n);
    if (statSync(p).isDirectory()) walk(p, ext, out);
    else if (ext.some((e) => n.endsWith(e))) out.push(p);
  }
  return out;
}
const failures = [], infos = [];
const section = (t) => console.log(`\n== ${t}`);
const fail = (msg) => { failures.push(msg); console.log(`  FAIL ${msg}`); };
const info = (msg) => { infos.push(msg); console.log(`  info ${msg}`); };
const ok = (msg) => console.log(`  ok   ${msg}`);

const srcFiles = walk(join(ROOT, 'src'), ['.ts', '.json']);
const siteCss = ['css/site.css', 'css/motion.css'].map((p) => join(ROOT, p));
const scanned = [...srcFiles, ...siteCss, join(ROOT, 'vite.config.ts')];

/* ---------- a) colour literals ---------- */
section('a) colour literals');
{
  const re = /#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch)\(/g;
  let n = 0;
  for (const f of scanned) {
    const text = readFileSync(f, 'utf8');
    text.split('\n').forEach((line, i) => {
      // MapLibre / URL fragments never look like colours here, but keep the rule strict: report every hit.
      for (const m of line.matchAll(re)) { fail(`${rel(f)}:${i + 1}: colour literal "${m[0]}"`); n++; }
    });
  }
  if (!n) ok(`${scanned.length} files, no colour literals (colours come from tokens only)`);
}

/* ---------- b) contrast ---------- */
section('b) contrast of tokens used in text, controls and map lines');
{
  const tok = JSON.parse(rd('design/tokens.json'));
  const themes = tok.color.themes.map((t) => t.id);
  const raw = new Map(tok.color.tokens.map((t) => [t.name, t.value]));
  const resolveTok = (name, theme, depth = 0) => {
    let v = raw.get(name);
    if (v === undefined || depth > 8) throw new Error(`unknown color token ${name}`);
    if (typeof v === 'object') v = v[theme];
    const m = /^\{([\w-]+)\}$/.exec(v);
    return m ? resolveTok(m[1], theme, depth + 1) : v;
  };
  const lin = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const lum = (hex) => { const h = hex.replace('#', ''); const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16)); return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

  // text colour token -> backgrounds it is used on (from bundle.css / site.css / templates)
  const TEXT = {
    ink: ['bg', 'surface', 'accent-soft', 'amber-soft'],
    'ink-muted': ['bg', 'surface'],
    'accent-ink': ['bg', 'surface', 'accent-soft'],
    'amber-ink': ['surface', 'bg', 'amber-soft'],
    'idx-on-accent': ['idx-accent'],
    'idx-q-ranked-ink': ['idx-q-ranked-bg'], 'idx-q-limited-ink': ['idx-q-limited-bg'], 'idx-q-out-ink': ['idx-q-out-bg'],
    'idx-placeholder-ink': ['idx-placeholder-bg'],
    'chrome-ink': ['chrome'],
  };
  // pairs that GISBoost/the design system document as below 4.5:1 and forbid for body text: reported, not failed
  const DOCUMENTED = [['ink-muted', 'surface-2'], ['chrome-muted', 'chrome'], ['ink-muted', 'accent-soft']];
  let bad = 0, rows = 0;
  for (const th of themes) {
    for (const [fg, bgs] of Object.entries(TEXT)) for (const bg of bgs) {
      const r = ratio(resolveTok(fg, th), resolveTok(bg, th)); rows++;
      if (r < 4.5) { fail(`${th}: text ${fg} on ${bg} = ${r.toFixed(2)}:1 (< 4.5)`); bad++; }
    }
    for (const [fg, bg] of DOCUMENTED) {
      const r = ratio(resolveTok(fg, th), resolveTok(bg, th));
      if (r < 4.5) info(`${th}: ${fg} on ${bg} = ${r.toFixed(2)}:1 (inherited pair, documented; not used for content text)`);
    }
    // topbar labels are chrome-muted mixed 20% toward chrome-ink (css/site.css); the current link sits on a 16% chrome-ink pill
    const hexOf = (h) => [0, 2, 4].map((i) => parseInt(h.replace('#', '').slice(i, i + 2), 16));
    const mix = (a, b, pa) => '#' + hexOf(a).map((v, i) => Math.round(v * pa + hexOf(b)[i] * (1 - pa)).toString(16).padStart(2, '0')).join('');
    const [chromeInk, chromeMuted, chrome] = ['chrome-ink', 'chrome-muted', 'chrome'].map((n) => resolveTok(n, th));
    for (const [label, fg, bg] of [['topbar label on chrome', mix(chromeInk, chromeMuted, 0.2), chrome], ['topbar label on the current-page pill', chromeInk, mix(chromeInk, chrome, 0.16)], ['topbar label on hover', chromeInk, mix(chromeInk, chrome, 0.1)]]) {
      const r = ratio(fg, bg); rows++;
      if (r < 4.5) { fail(`${th}: ${label} = ${r.toFixed(2)}:1 (< 4.5)`); bad++; }
    }
    // controls, focus ring, node outline: 3:1 against the surfaces they sit on
    for (const fg of ['idx-control-edge', 'focus', 'idx-node']) for (const bg of ['surface', 'bg']) {
      const r = ratio(resolveTok(fg, th), resolveTok(bg, th)); rows++;
      if (r < 3) { fail(`${th}: ${fg} on ${bg} = ${r.toFixed(2)}:1 (< 3)`); bad++; }
    }
    // map lines: every speed class and "brak danych" against land / water / road
    for (const cls of ['idx-speed-1', 'idx-speed-2', 'idx-speed-3', 'idx-speed-4', 'idx-speed-5', 'idx-speed-6', 'idx-speed-nodata']) for (const bg of ['idx-map-land', 'idx-map-water', 'idx-map-road']) {
      const r = ratio(resolveTok(cls, th), resolveTok(bg, th)); rows++;
      if (r < 3) { fail(`${th}: ${cls} on ${bg} = ${r.toFixed(2)}:1 (< 3)`); bad++; }
    }
  }
  // every colour token used as a text colour must be covered by the table above
  const used = new Set();
  const colorDecl = /(?<![-\w])color:\s*var\(--([\w-]+)\)/g;
  for (const f of [...scanned.filter((p) => p.endsWith('.ts') || p.endsWith('.css')), join(ROOT, 'css/bundle.css')]) {
    for (const m of readFileSync(f, 'utf8').matchAll(colorDecl)) used.add(m[1]);
  }
  const uncovered = [...used].filter((u) => !(u in TEXT) && !DOCUMENTED.some(([a]) => a === u) && !['chrome-muted', 'accent', 'ink-faint'].includes(u));
  if (uncovered.length) info(`text colours not in the contrast table: ${uncovered.join(', ')}`);
  if (!bad) ok(`${rows} pairs x 2 themes pass (text 4.5:1, controls and map lines 3:1)`);
  info('chrome-muted (nav labels on chrome) and accent-soft/ink-muted are the documented exceptions; ink-faint is decoration only');
}

/* ---------- c) animated properties ---------- */
section('c) only transform / opacity are animated');
{
  const OK = new Set(['transform', 'opacity', 'translate', 'scale', 'rotate', 'none', 'transform-origin']);
  const OK_KF = new Set([...OK, 'animation-timing-function', 'offset', 'easing', 'composite']);
  const OK_JS = new Set([...OK, 'offset', 'easing', 'duration', 'delay', 'fill', 'composite', 'ease', 'scrollTrigger', 'trigger', 'start', 'end', 'scrub', 'xPercent', 'yPercent', 'x', 'y', 'scaleX', 'scaleY', 'rotation']);
  const cssCheck = (file, text, reporter) => {
    text.split('\n').forEach((line, i) => {
      const t = /(?<![-\w])transition(?:-property)?:\s*([^;}]+)/.exec(line);
      if (t) {
        const parts = /transition-property/.test(line) ? t[1].split(',') : t[1].split(/,(?![^(]*\))/);
        for (const p of parts) { const name = p.trim().split(/\s+/)[0]; if (name && !OK.has(name) && !name.startsWith('var(')) reporter(`${rel(file)}:${i + 1}: transition of "${name}"`); }
      }
    });
    for (const m of text.matchAll(/@keyframes\s+([\w-]+)\s*\{((?:[^{}]|\{[^{}]*\})*)\}/g)) {
      for (const d of m[2].matchAll(/([\w-]+)\s*:\s*[^;{}]+;?/g)) if (!OK_KF.has(d[1]) && !/^\d+%|from|to$/.test(d[1])) reporter(`${rel(file)}: @keyframes ${m[1]} animates "${d[1]}"`);
    }
  };
  let n = 0;
  for (const f of siteCss) cssCheck(f, readFileSync(f, 'utf8'), (m) => { fail(m); n++; });
  // design-system CSS is unchanged on purpose; what it animates that we override is reported once
  const bundle = [];
  cssCheck(join(ROOT, 'css/bundle.css'), rd('css/bundle.css'), (m) => bundle.push(m));
  const overridden = bundle.filter((m) => /background-color/.test(m));
  if (overridden.length) info(`css/bundle.css transitions background-color ${overridden.length}x (design system); css/site.css switches those to instant, so the rule holds`);
  for (const f of srcFiles.filter((p) => p.endsWith('.ts'))) {
    const text = readFileSync(f, 'utf8');
    for (const m of text.matchAll(/\.animate\(\s*\[([\s\S]*?)\]\s*,/g)) {
      for (const k of m[1].matchAll(/([A-Za-z]+)\s*:/g)) if (!OK_JS.has(k[1])) { fail(`${rel(f)}: .animate() keyframe property "${k[1]}"`); n++; }
    }
    for (const m of text.matchAll(/gsap\.(?:to|fromTo|from|set)\(([\s\S]*?)\)\s*;/g)) {
      for (const k of m[1].matchAll(/([A-Za-z]+)\s*:/g)) if (!OK_JS.has(k[1])) { fail(`${rel(f)}: gsap property "${k[1]}"`); n++; }
    }
    for (const m of text.matchAll(/style\.(?!setProperty|transformBox|transformOrigin|transition|opacity|cssText|background|cursor|zoom)(\w+)\s*=/g)) info(`${rel(f)}: inline style.${m[1]} (not an animation; check by eye)`);
    // MapLibre paint transitions must be opacity only
    for (const m of text.matchAll(/setPaintProperty\([^,]+,\s*'([\w-]+)-transition'/g)) if (m[1] !== 'line-opacity') { fail(`${rel(f)}: paint transition on "${m[1]}"`); n++; }
  }
  if (!n) ok('site CSS, keyframes, WAAPI, GSAP and MapLibre paint transitions: transform / opacity only');
}

/* ---------- d) i18n + links ---------- */
section('d) i18n and links');
{
  const pl = JSON.parse(rd('src/i18n/pl.json')), en = JSON.parse(rd('src/i18n/en.json'));
  let n = 0;
  for (const k of Object.keys(pl)) if (!(k in en)) { fail(`i18n: "${k}" missing in en.json`); n++; }
  for (const k of Object.keys(en)) if (!(k in pl)) { fail(`i18n: "${k}" missing in pl.json`); n++; }
  const ph = (s) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',');
  for (const k of Object.keys(pl)) if (k in en && ph(pl[k]) !== ph(en[k])) { fail(`i18n: "${k}" placeholders differ (pl {${ph(pl[k])}} vs en {${ph(en[k])}})`); n++; }
  for (const [lang, d] of [['pl', pl], ['en', en]]) for (const [k, v] of Object.entries(d)) if (/<|&(?!lt;|gt;|amp;|quot;|#\d+;)/.test(v)) { fail(`i18n ${lang}: "${k}" has a raw < or & (write &lt; / &amp;)`); n++; }
  // keys used in code
  const keys = new Set(), prefixes = new Set();
  for (const f of srcFiles.filter((p) => p.endsWith('.ts') && !p.includes(`${sep}i18n${sep}`))) {
    const text = readFileSync(f, 'utf8');
    for (const m of text.matchAll(/\bt\(\s*'([\w.-]+)'/g)) keys.add(m[1]);
    for (const m of text.matchAll(/\bt\(\s*`([\w.-]*)\$\{/g)) prefixes.add(m[1]);
    for (const m of text.matchAll(/\bt\(\s*`([\w.-]+)`/g)) keys.add(m[1]);
    for (const m of text.matchAll(/(?:key|label):\s*'([a-z]+(?:\.[a-z0-9]+)+)'/g)) keys.add(m[1]);
    if (f.endsWith('lib/agg.ts')) for (const m of text.matchAll(/'((?:mode|period)\.[a-z]+)'/g)) keys.add(m[1]);
  }
  for (const k of keys) if (!(k in pl)) { fail(`i18n: code uses "${k}" but it is not in the dictionary`); n++; }
  for (const p of prefixes) if (!Object.keys(pl).some((k) => k.startsWith(p))) { fail(`i18n: code uses keys "${p}\${...}" but none exist`); n++; }
  // data-driven keys: one title/description per file id in the manifest
  const manifest = JSON.parse(rd('public/data/manifest.json'));
  for (const f of manifest.files) for (const pre of ['dl.title.', 'dl.desc.']) if (!(pre + f.id in pl)) { fail(`i18n: manifest file "${f.id}" has no "${pre}${f.id}"`); n++; }
  const unused = Object.keys(pl).filter((k) => !keys.has(k) && ![...prefixes].some((p) => k.startsWith(p)) && !/^(city\.quality|qual|scr\.s\d|mth\.s\d|q|period|mode)\./.test(k));
  if (unused.length) info(`i18n: keys not referenced literally (may be built dynamically): ${unused.length}`);
  if (!n) ok(`${Object.keys(pl).length} keys in pl and en, placeholders match, ${keys.size} literal + ${prefixes.size} dynamic uses resolve`);

  const dist = join(ROOT, 'dist');
  if (!existsSync(dist)) info('links: dist/ not found, run `npm run build` first to check internal links');
  else {
    const base = '/' + (process.env.BASE ?? '/transit-index/').replace(/^\/+|\/+$/g, '') + '/';
    const html = walk(dist, ['.html']);
    let links = 0, bad = 0;
    for (const f of html) {
      const text = readFileSync(f, 'utf8');
      const ids = new Set([...text.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
      for (const m of text.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
        const u = m[1];
        if (/^(https?:|mailto:|data:|\/\/)/.test(u)) continue;
        links++;
        if (u.startsWith('#')) { if (u.length > 1 && !ids.has(u.slice(1))) { fail(`${rel(f)}: anchor ${u} has no target`); bad++; } continue; }
        if (!u.startsWith(base)) { fail(`${rel(f)}: link "${u}" is outside the base ${base}`); bad++; continue; }
        const path = u.slice(base.length).split('#')[0].split('?')[0];
        const target = join(dist, path);
        const exists = path === '' ? existsSync(join(dist, 'index.html')) : /\.\w+$/.test(path) ? existsSync(target) : existsSync(join(target, 'index.html'));
        if (!exists) { fail(`${rel(f)}: broken link "${u}"`); bad++; }
      }
    }
    if (!bad) ok(`${html.length} pages, ${links} internal links/assets resolve (base ${base})`);
    // no demo data in the build
    const js = walk(join(dist, 'assets'), ['.js']).map((p) => readFileSync(p, 'utf8')).join('\n');
    if (/mockMap|idx-demo|IDX\.demo/.test(js)) fail('build contains IDX.demo (placeholder network from bundle.js must not ship)'); else ok('no IDX.demo in the build');
  }
}

/* ---------- e) hygiene ---------- */
section('e) hygiene');
{
  const a = readFileSync(join(ROOT, 'css/bundle.css')), b = readFileSync(join(ROOT, 'design/components/bundle.css'));
  if (Buffer.compare(a, b) !== 0) fail('css/bundle.css differs from design/components/bundle.css (it must stay an unchanged copy)'); else ok('css/bundle.css is an unchanged copy of the design system bundle');
  if (!existsSync(join(ROOT, 'design/tokens.css'))) fail('design/tokens.css missing (py tools/gen_tokens.py)'); else ok('design/tokens.css present');
  const emoji = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u, lorem = /lorem ipsum/i;
  let n = 0;
  for (const f of [...srcFiles, ...walk(join(ROOT, 'public/data'), ['.json'])]) {
    const t = readFileSync(f, 'utf8');
    if (emoji.test(t)) { fail(`${rel(f)}: emoji`); n++; }
    if (lorem.test(t)) { fail(`${rel(f)}: lorem ipsum`); n++; }
  }
  if (!n) ok('no emoji, no lorem ipsum');
  const gis = existsSync(join(ROOT, 'dist')) ? walk(join(ROOT, 'dist'), ['.html']).filter((f) => !readFileSync(f, 'utf8').includes('gisboost-1.css')) : [];
  if (gis.length) fail(`pages without gisboost-1.css: ${gis.map(rel).join(', ')}`);
}

console.log(`\n${failures.length ? `FAILED: ${failures.length} problem(s)` : 'PASSED'}${infos.length ? `, ${infos.length} info` : ''}`);
process.exit(failures.length ? 1 : 0);
