/** Port of design/components/bundle.js (window.IDX): icons, number formatting, speed class, hourly chart.
 *  Deliberately without IDX.demo (placeholder network) and IDX.motion (replaced by src/motion.ts).
 *  Runs in Node (SSG) and in the browser, so the prerendered HTML and the client rendering come from one code path. */
import type { Lang } from '../i18n';

const P = {
  'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
  'arrow-up-right': '<path d="M7 17 17 7M8 7h9v9"/>',
  'download': '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
  'sliders': '<path d="M4 8h9M17 8h3M4 16h3M11 16h9"/><circle cx="15" cy="8" r="2"/><circle cx="9" cy="16" r="2"/>',
  'clock': '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
  'map': '<path d="M9 4 4 6v14l5-2 6 2 5-2V4l-5 2-6-2zM9 4v14M15 6v14"/>',
  'table': '<rect x="4" y="5" width="16" height="14" rx="1.5"/><path d="M4 10h16M10 5v14"/>',
  'info': '<circle cx="12" cy="12" r="8"/><path d="M12 11v5M12 8h.01"/>',
  'warning': '<path d="M12 4 21 20H3z"/><path d="M12 10v4M12 17h.01"/>',
  'check': '<path d="M5 12.5 9.5 17 19 7"/>',
  'close': '<path d="M6 6l12 12M18 6 6 18"/>',
  'chevron-down': '<path d="M6 9l6 6 6-6"/>',
  'external': '<path d="M14 5h5v5M19 5l-8 8M18 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4"/>',
  'search': '<circle cx="11" cy="11" r="6"/><path d="M16 16l4 4"/>',
  'layers': '<path d="M12 4l8 4-8 4-8-4zM4 12l8 4 8-4M4 16l8 4 8-4"/>',
  'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
} as const;
export type IconName = keyof typeof P;

export function icon(name: IconName, size = 20): string {
  return `<svg class="idx-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${P[name]}</svg>`;
}

const LOCALE: Record<Lang, string> = { pl: 'pl-PL', en: 'en-GB' };
/** Decimal comma in Polish, decimal point in English; a real minus sign (U+2212). */
export function fmt(n: number, d = 1, lang: Lang = 'pl'): string {
  return n.toLocaleString(LOCALE[lang], { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: false }).replace('-', '−');
}
/** Same, with the separator narrowed by .idx-comma so a mono figure does not fall apart. */
export function num(n: number, d = 1, lang: Lang = 'pl'): string {
  const sep = lang === 'pl' ? ',' : '.';
  return fmt(n, d, lang).replace(sep, `<span class="idx-comma">${sep}</span>`);
}
/** Signed difference: "+1,8" / "−1,8" (the sign carries the direction next to the amber/blue meaning). */
export function signed(n: number, d = 1, lang: Lang = 'pl'): string {
  return (n > 0 ? '+' : '') + fmt(n, d, lang);
}

/** Hero figure: digits revealed one by one (transform + opacity, see motion.css). */
export function digits(s: string): string {
  let out = '';
  for (let i = 0; i < s.length; i++) out += `<span class="idx-digit${s[i] === ',' || s[i] === '.' ? ' idx-digit--p' : ''}" aria-hidden="true" style="--i:${i}">${s[i]}</span>`;
  return `${out}<span class="idx-sr">${s}</span>`;
}

/* ---------- speed class: thresholds come from the tokens (--idx-speed-t1..t5), never typed here ---------- */
let thresholds: number[] = [8, 12, 16, 20, 26];
export const setThresholds = (t: number[]): void => { thresholds = t; };
/** Browser: read the thresholds from the computed tokens. */
export function readThresholds(): number[] {
  const cs = getComputedStyle(document.documentElement);
  const t = [1, 2, 3, 4, 5].map((i) => parseFloat(cs.getPropertyValue(`--idx-speed-t${i}`)));
  if (t.every(Number.isFinite)) thresholds = t;
  return thresholds;
}
export const getThresholds = (): number[] => thresholds;
export type SpeedClass = 1 | 2 | 3 | 4 | 5 | 6 | 'nd';
export function speedClass(kmh: number | null | undefined): SpeedClass {
  if (kmh == null || Number.isNaN(kmh)) return 'nd';
  for (let i = 0; i < thresholds.length; i++) if (kmh < thresholds[i]) return (i + 1) as SpeedClass;
  return 6;
}

/* ---------- hourly chart: planned (dashed) vs measured (solid), 24 h, axis from 0, hatched where sample too small ---------- */
/** Chart geometry per container width: the same chart, drawn at the size it is shown (text stays 12 px, never scaled down). */
export type ChartSize = 'sm' | 'md' | 'lg';
const GEOM: Record<ChartSize, { W: number; H: number; L: number; R: number; T: number; B: number; tick: number }> = {
  sm: { W: 354, H: 280, L: 32, R: 84, T: 24, B: 32, tick: 6 },
  md: { W: 720, H: 320, L: 44, R: 104, T: 28, B: 36, tick: 3 },
  lg: { W: 1072, H: 320, L: 44, R: 104, T: 28, B: 36, tick: 3 },
};
export interface HourlyOpts {
  plan: (number | null)[]; meas: (number | null)[]; ymax?: number; size?: ChartSize;
  labels: { title: string; desc: string; nodata: string; plan: string; meas: string };
}
let uid = 0;
export function hourlyChart(o: HourlyOpts): string {
  const { W, H, L, R, T, B, tick } = GEOM[o.size ?? 'md'];
  const plan = o.plan, meas = o.meas;
  const ymax = o.ymax || 30, iw = W - L - R, ih = H - T - B, id = `idxh${++uid}`;
  const x = (h: number) => L + (h + 0.5) * iw / 24;
  const y = (v: number) => T + ih - v / ymax * ih;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}t ${id}d"><title id="${id}t">${o.labels.title}</title><desc id="${id}d">${o.labels.desc}</desc>`;
  s += `<defs><pattern id="${id}p" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="c-hatch" x1="0" y1="0" x2="0" y2="7"/></pattern></defs>`;
  for (let g = 0; g <= ymax; g += 10) {
    s += `<line class="c-grid" x1="${L}" x2="${W - R}" y1="${y(g)}" y2="${y(g)}"/><text class="c-axis" x="${L - 8}" y="${y(g) + 4}" text-anchor="end">${g}</text>`;
  }
  s += `<text class="c-axis" x="${L}" y="${T - 12}">km/h</text>`;
  for (let h = 0; h < 24; h += tick) s += `<text class="c-axis" x="${x(h)}" y="${H - 10}" text-anchor="middle">${h}:00</text>`;
  const runs: [number, number][] = [];
  let st: number | null = null;
  for (let i = 0; i < 24; i++) { if (meas[i] == null) { if (st == null) st = i; } else if (st != null) { runs.push([st, i - 1]); st = null; } }
  if (st != null) runs.push([st, 23]);
  for (const r of runs) {
    const x0 = x(r[0]) - iw / 48, x1 = x(r[1]) + iw / 48;
    s += `<rect x="${x0}" y="${T}" width="${x1 - x0}" height="${ih}" fill="url(#${id}p)"/><rect class="c-hatch-frame" x="${x0}" y="${T}" width="${x1 - x0}" height="${ih}"/>`;
    if (x1 - x0 > 60) s += `<text class="c-nodata-t" x="${(x0 + x1) / 2}" y="${T + 16}" text-anchor="middle">${o.labels.nodata}</text>`;
  }
  const path = (a: (number | null)[]) => { let d = '', pen = false; a.forEach((v, k) => { if (v == null) { pen = false; return; } d += `${pen ? 'L' : 'M'}${x(k).toFixed(1)} ${y(v).toFixed(1)}`; pen = true; }); return d; };
  const last = (a: (number | null)[]) => { let i = 23; while (i > 0 && a[i] == null) i--; return i; };
  s += `<path class="c-plan" d="${path(plan)}"/><path class="c-meas" d="${path(meas)}"/>`;
  const lastM = last(meas), lastV = meas[lastM] ?? 0;
  let yp = y(plan[last(plan)] ?? 0), ym = y(lastV);
  if (Math.abs(yp - ym) < 18) { if (yp < ym) { yp -= 9; ym += 9; } else { yp += 9; ym -= 9; } }
  s += `<circle class="c-dot" cx="${x(lastM)}" cy="${y(lastV)}" r="4"/>`;
  s += `<text class="c-lab-plan" x="${W - R + 10}" y="${yp + 4}">${o.labels.plan}</text><text class="c-lab-meas" x="${W - R + 10}" y="${ym + 4}">${o.labels.meas}</text>`;
  return `${s}</svg>`;
}
